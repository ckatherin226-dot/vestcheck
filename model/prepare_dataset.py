"""Build an immutable-source, five-class staging dataset; do not train or resplit.

Tiny out-of-frame corners (at most 1e-5 normalized units) are clipped in retained
labels only. Larger/malformed errors fail closed. Publisher membership is retained
and explicitly marked NOT training-ready pending scene/annotation review.
"""
import argparse
from collections import Counter
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

import yaml

try:
    from .acquire_dataset import file_manifest, sha256
    from .audit_dataset import EXPECTED_NAMES, IMAGE_SUFFIXES, TARGETS, load_config, validate_row
except ImportError:
    from acquire_dataset import file_manifest, sha256
    from audit_dataset import EXPECTED_NAMES, IMAGE_SUFFIXES, TARGETS, load_config, validate_row

MAPPING = {source: target for target, (source, _) in enumerate(TARGETS)}
MAX_EXCURSION = Decimal('0.00001')


def corrected_row(line):
    """Return source class, coordinates, and whether exact-decimal clipping occurred.

    The intersection with the image rectangle is the minimal edge correction.
    Valid unchanged source coordinate strings are preserved verbatim.
    """
    fields = line.split()
    _, error = validate_row(line, len(EXPECTED_NAMES))
    if error and error != 'invalid_bbox':
        raise ValueError(f'Untransformable annotation: {error}')
    try:
        source = int(fields[0])
        x, y, w, h = map(Decimal, fields[1:])
    except (InvalidOperation, ValueError):
        raise ValueError('Invalid numeric annotation') from None
    if (not all(v.is_finite() for v in (x,y,w,h))
            or not (0 <= x <= 1 and 0 <= y <= 1 and 0 < w <= 1 and 0 < h <= 1)):
        raise ValueError('Invalid normalized center or dimensions')
    left, top, right, bottom = x-w/2, y-h/2, x+w/2, y+h/2
    excursion = max(Decimal(0), -left, -top, right-1, bottom-1)
    if excursion > MAX_EXCURSION:
        raise ValueError('Boundary excursion exceeds reviewed rounding policy')
    if not excursion:
        return source, fields[1:], False
    left, top, right, bottom = max(Decimal(0),left), max(Decimal(0),top), min(Decimal(1),right), min(Decimal(1),bottom)
    values = [(left+right)/2, (top+bottom)/2, right-left, bottom-top]
    tokens = [format(v,'.12f').rstrip('0').rstrip('.') or '0' for v in values]
    if validate_row(f"{source} {' '.join(tokens)}",len(EXPECTED_NAMES))[1]:
        raise ValueError('Corrected box is not valid; no output accepted')
    return source, tokens, True


def transform_label(text):
    """Keep all target rows, retain legitimate empty outputs, and log each action."""
    output, actions = [], []
    for number, line in enumerate(text.splitlines(),1):
        if not line.strip():
            continue
        source, coordinates, clipped = corrected_row(line)
        action = {'source_line':number, 'source_class':source, 'source_row':line,
                  'boundary_flag':clipped}
        if source not in MAPPING:
            action['action']='drop_out_of_scope'
        else:
            target=MAPPING[source]
            result=f"{target} {' '.join(coordinates)}"
            output.append(result)
            action.update(action='clip_and_remap' if clipped else 'remap_only',
                          target_class=target,derived_row=result)
        actions.append(action)
    return '\n'.join(output)+ ('\n' if output else ''), actions


def verify_originals(root, baseline):
    """The acquisition baseline is relative to original/, including dataset prefix."""
    expected=json.loads(Path(baseline).read_text())
    if any(p.is_symlink() for p in root.rglob('*')):
        raise ValueError('Symlinks are not allowed in source data')
    observed={root.name+'/'+name:digest for name,digest in file_manifest(root).items()}
    if expected != observed:
        raise ValueError('Original dataset differs from acquisition baseline')
    return observed


def check_output_location(root, output):
    root,output=Path(root).resolve(),Path(output).resolve()
    if root==output or root in output.parents or output in root.parents:
        raise ValueError('Derived output must be separate from originals')
    if output.exists():
        raise FileExistsError('Refusing to overwrite existing derived output')
    repo=Path(__file__).resolve().parents[1]
    if output.is_relative_to(repo):
        relative=output.relative_to(repo)
        if subprocess.run(['git','-C',str(repo),'check-ignore','-q',str(relative)]).returncode:
            raise ValueError('Derived output inside the checkout must be Git-ignored')
    return root,output


def verify_prepared(output):
    """Independently reread every derived label and verify image/label hashes."""
    output=Path(output).resolve()
    summary=json.loads((output/'preparation.json').read_text())
    manifest=output/'transformation.jsonl'
    if sha256(manifest) != summary['transformation_manifest_sha256']:
        raise ValueError('Transformation manifest changed')
    config,names=load_config(output/'data.staging.yaml')
    if names != [name for _,name in TARGETS] or any(config.get(s)!=f'images/{s}' for s in ('train','val')):
        raise ValueError('Derived YAML schema changed')
    counts={split:Counter() for split in ('train','val')}
    membership={split:0 for split in counts}
    seen=set()
    for line in manifest.read_text().splitlines():
        row=json.loads(line)
        split=row['derived_split']
        if split not in counts or row['source_split'] != split:
            raise ValueError('Unexpected split change')
        for key in ('image','label'):
            relative=Path(row['derived_'+key])
            path=(output/relative).resolve()
            if (relative.is_absolute() or '..' in relative.parts or not path.is_relative_to(output)
                    or relative.as_posix() in seen):
                raise ValueError('Invalid or repeated derived path')
            seen.add(relative.as_posix())
            if sha256(path) != row['derived_'+key+'_sha256']:
                raise ValueError('Derived content hash mismatch')
        if row['source_image_sha256'] != row['derived_image_sha256']:
            raise ValueError('Images must remain byte-identical')
        membership[split]+=1
        for annotation in (output/row['derived_label']).read_text().splitlines():
            box,error=validate_row(annotation,5)
            if error: raise ValueError('Invalid derived row during independent verification')
            counts[split][str(box[0])]+=1
    inventory={p.relative_to(output).as_posix() for kind in ('images','labels')
               for p in (output/kind).rglob('*') if p.is_file()}
    if inventory != seen:
        raise ValueError('Derived inventory differs from transformation manifest')
    for split in counts:
        expected=summary['splits'][split]
        if (membership[split] != expected['images'] or sum(counts[split].values()) != expected['annotations']
                or {str(i):counts[split][str(i)] for i in range(5)} != expected['class_counts']):
            raise ValueError('Derived class counts differ from recorded summary')
    return {'verified_images':sum(membership.values()),
            'verified_annotations':sum(sum(c.values()) for c in counts.values()),
            'invalid_rows':0,'image_and_label_hashes_match':True,
            'training_ready':summary['training_ready']}


def prepare(root, output, baseline, review_record):
    root,output=check_output_location(root,output)
    before=verify_originals(root,baseline)
    config,names=load_config(root/'data.yaml')
    if names != EXPECTED_NAMES or any(config.get(s) != f'images/{s}' for s in ('train','val')):
        raise ValueError('Source schema/layout changed; review mapping before preparation')
    review=json.loads(Path(review_record).read_text())
    if review.get('status') != 'reviewed_sample_not_full_clearance' or not review.get('sample'):
        raise ValueError('A documented visual review record is required')
    # Review references are evidence, not an instruction to move any source images.
    for item in review.get('sample',[]):
        path=Path(item['path'])
        if (not item.get('notes') or path.is_absolute() or '..' in path.parts
                or sha256(root/path) != item['sha256']):
            raise ValueError('Review sample does not match original content')
    output.parent.mkdir(parents=True,exist_ok=True)
    summary={'schema_version':1,'split_policy':'preserve-publisher-staging',
             'training_ready':False,'readiness_reason':'Known scene overlap and unresolved semantic/provenance review',
             'original_baseline_sha256':sha256(baseline),'review_record_sha256':sha256(review_record),
             'source_yaml_sha256':sha256(root/'data.yaml'),
             'mapping':{str(source):target for source,target in MAPPING.items()},
             'maximum_allowed_boundary_excursion':str(MAX_EXCURSION),
             'splits':{},'retained_corrections':0,'dropped_boundary_flags':0,
             'source_rows':0,'retained_rows':0,'dropped_rows':0,'split_changes':0}
    manifest=[]
    with tempfile.TemporaryDirectory(prefix='preparation-',dir=output.parent) as temporary:
        staging=Path(temporary)
        for split in ('train','val'):
            images=sorted(p for p in (root/'images'/split).rglob('*') if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES)
            labels=set((root/'labels'/split).rglob('*.txt'))
            expected_labels=set()
            counts=Counter(); stems=set(); backgrounds=0
            if not images:
                raise ValueError(f'No source images in {split}')
            for image in images:
                relative=image.relative_to(root/'images'/split)
                if relative.with_suffix('') in stems:
                    raise ValueError('Ambiguous source image stem')
                stems.add(relative.with_suffix(''))
                label=root/'labels'/split/relative.with_suffix('.txt')
                expected_labels.add(label)
                if not label.is_file():
                    raise ValueError('Missing source label requires explicit background review')
                text,actions=transform_label(label.read_text())
                image_out=staging/'images'/split/relative
                label_out=staging/'labels'/split/relative.with_suffix('.txt')
                image_out.parent.mkdir(parents=True,exist_ok=True)
                label_out.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(image,image_out)  # Independent copy, not a source-aliasing hard link.
                label_out.write_text(text)
                if sha256(image) != sha256(image_out):
                    raise ValueError('Image copy differs from original')
                for line in text.splitlines():
                    box,error=validate_row(line,len(TARGETS))
                    if error: raise ValueError('Invalid derived annotation')
                    counts[str(box[0])]+=1
                backgrounds += not bool(text)
                for action in actions:
                    summary['source_rows']+=1
                    dropped=action['action']=='drop_out_of_scope'
                    summary['dropped_rows']+=dropped
                    summary['retained_rows']+=not dropped
                    summary['dropped_boundary_flags']+=dropped and action['boundary_flag']
                    summary['retained_corrections']+=(not dropped) and action['boundary_flag']
                manifest.append({'source_image':image.relative_to(root).as_posix(),
                                 'source_label':label.relative_to(root).as_posix(),
                                 'derived_image':image_out.relative_to(staging).as_posix(),
                                 'derived_label':label_out.relative_to(staging).as_posix(),
                                 'source_split':split,'derived_split':split,
                                 'split_rationale':'Publisher staging membership retained; not cleared for independent validation',
                                 'source_image_sha256':sha256(image),'derived_image_sha256':sha256(image_out),
                                 'source_label_sha256':sha256(label),'derived_label_sha256':sha256(label_out),
                                 'row_actions':actions})
            if labels != expected_labels:
                raise ValueError('Orphan/extra source labels require review')
            summary['splits'][split]={'images':len(images),'class_counts':{str(i):counts[str(i)] for i in range(5)},
                                     'annotations':sum(counts.values()),'background_images':backgrounds}
        summary['class_counts']={str(i):sum(s['class_counts'][str(i)] for s in summary['splits'].values()) for i in range(5)}
        # Keep attribution/license with all local derivatives, without publishing the dataset.
        for name in ('LICENSE.txt','README.md'):
            shutil.copyfile(root/name,staging/('SOURCE_'+name))
        (staging/'TRANSFORMATION_NOTICE.md').write_text(
            '# VestCheck five-class staging derivative\n\n'
            'Ultralytics Construction-PPE Dataset, Ultralytics team, November 2026, CC BY 4.0.\n'
            'Source: https://docs.ultralytics.com/datasets/detect/construction-ppe/\n'
            'License: https://creativecommons.org/licenses/by/4.0/\n\n'
            'Adapted by selecting/remapping source classes 5,0,2,6,11 and minimally clipping tiny '\
            'boundary excursions in retained boxes. Images and publisher split membership unchanged.\n'
            'NOT TRAINING-READY: known scene overlap, limited semantic review and unresolved per-image provenance.\n')
        yaml_data={'path':str(output),'train':'images/train','val':'images/val',
                   'names':{i:name for i,(_,name) in enumerate(TARGETS)}}
        (staging/'data.staging.yaml').write_text('# Staging only; review split/annotation gates before training.\n'+yaml.safe_dump(yaml_data,sort_keys=False))
        manifest_path=staging/'transformation.jsonl'
        manifest_path.write_text(''.join(json.dumps(row,sort_keys=True)+'\n' for row in manifest))
        summary['transformation_manifest_sha256']=sha256(manifest_path)
        summary['originals_unchanged']=before==verify_originals(root,baseline)
        (staging/'preparation.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
        verify_prepared(staging)
        staging.rename(output)  # Publish only a complete, verified preparation.
    return summary


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--root',type=Path)
    mode.add_argument('--verify',type=Path,help='Verify an existing derivative without modifying it')
    parser.add_argument('--output',type=Path)
    parser.add_argument('--baseline',type=Path)
    parser.add_argument('--review-record',type=Path)
    args=parser.parse_args()
    if args.verify:
        print(json.dumps(verify_prepared(args.verify),indent=2))
    else:
        if not all((args.output,args.baseline,args.review_record)):
            parser.error('--root requires --output, --baseline and --review-record')
        print(json.dumps(prepare(args.root,args.output,args.baseline,args.review_record),indent=2))
