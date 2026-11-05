"""Generate deterministic scene-search and annotation-review diagnostics, not labels.

All outputs belong in an ignored workspace outside originals. Candidate similarity
is not a scene-ID detector or a substitute for documented visual adjudication.
"""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

try:
    from .acquire_dataset import sha256
    from .audit_dataset import difference_hash, TARGETS
except ImportError:
    from acquire_dataset import sha256
    from audit_dataset import difference_hash, TARGETS


COLORS = {5: '#00ffff', 0: '#ffff00', 2: '#00ff00', 6: '#ff6060', 11: '#ff80ff'}
NAMES = {source: name for source, name in TARGETS}


def rows_for(root, relative):
    label = root / 'labels' / Path(relative).relative_to('images').with_suffix('.txt')
    return [tuple(map(float, line.split())) for line in label.read_text().splitlines() if line.strip()]


def features(image):
    width, height = image.size
    # Border crops reduce, but do not eliminate, changes caused by foreground people.
    crops = [(0, 0, width, height // 4), (0, 0, width // 4, height),
             (width * 3 // 4, 0, width, height), (0, height * 3 // 4, width, height)]
    border = 0
    for crop in crops:
        border = (border << 64) | difference_hash(image.crop(crop))
    colors = tuple(v for pixel in image.convert('RGB').resize((2, 2)).get_flattened_data() for v in pixel)
    return {'whole': difference_hash(image), 'border': border, 'colors': colors,
            'aspect': width / height}


def scene_candidates(records):
    """Broad search: whole dHash <=12 OR border distance <=32 + color MAE <=25."""
    pairs = []
    for i, left in enumerate(records):
        for right in records[i+1:]:
            if abs(left['aspect']-right['aspect']) / max(left['aspect'], right['aspect']) > .10:
                continue
            whole = (left['whole'] ^ right['whole']).bit_count()
            border = (left['border'] ^ right['border']).bit_count()
            color = sum(abs(a-b) for a,b in zip(left['colors'], right['colors'])) / 12
            if whole <= 12 or (border <= 32 and color <= 25):
                pairs.append({'left':left['path'], 'right':right['path'], 'whole_distance':whole,
                              'border_distance':border, 'color_mae':round(color, 3),
                              'cross_split':Path(left['path']).parts[1] != Path(right['path']).parts[1]})
    return sorted(pairs, key=lambda p:(p['border_distance'],p['whole_distance'],p['left'],p['right']))


def select_sample(root, records):
    """One unique image for each class x split x filename family: 20 strata.

    Select a lower-quartile target-box area in source-* and median in the other
    family. These are filename strata, never verified real/generated categories.
    """
    sample, used = [], set()
    for source, name in TARGETS:
        for split in ('train','val'):
            for family in ('source-', 'ultralytics-ppe-nov2026-'):
                candidates = []
                for record in records:
                    path = record['path']
                    if Path(path).parts[1] != split or not Path(path).name.startswith(family) or path in used:
                        continue
                    matching = [r for r in rows_for(root,path) if int(r[0]) == source]
                    if matching:
                        smallest = min(r[3]*r[4] for r in matching)
                        candidates.append((smallest,path))
                candidates.sort()
                if not candidates:
                    raise ValueError(f'Empty review stratum: {source}/{split}/{family}')
                area,path = candidates[int((len(candidates)-1) * (.25 if family=='source-' else .5))]
                used.add(path)
                sample.append({'sample_id':f'S{len(sample)+1:02}', 'path':path, 'stratum_class':name,
                               'source_class':source,'split':split,'filename_family':family,
                               'smallest_target_area':area, 'sha256':sha256(root/path)})
    return sample


def annotation_panel(root, item, width=720, height=540, focus=False):
    """Diagnostic overlay on a resized copy; originals remain byte-identical."""
    with Image.open(root/item['path']) as opened:
        image = opened.convert('RGB')  # Raw YOLO coordinates refer to stored pixels.
    original_width, original_height = image.size
    crop_left,crop_top,crop_right,crop_bottom=0,0,original_width,original_height
    if focus:
        rows=rows_for(root,item['path'])
        target=min((r for r in rows if int(r[0])==item['source_class']),key=lambda r:r[3]*r[4])
        _,x,y,w,h=target
        # Include a containing person when present, preserving ownership/visibility context.
        people=[r for r in rows if int(r[0])==5 and abs(x-r[1])<=r[3]/2 and abs(y-r[2])<=r[4]/2]
        if people:
            target=min(people,key=lambda r:r[3]*r[4])
            _,x,y,w,h=target
        crop_left=max(0,int((x-w*.75)*original_width))
        crop_top=max(0,int((y-h*.75)*original_height))
        crop_right=min(original_width,int((x+w*.75)*original_width)+1)
        crop_bottom=min(original_height,int((y+h*.75)*original_height)+1)
        image=image.crop((crop_left,crop_top,crop_right,crop_bottom))
    if focus:
        scale=min(width/image.width,(height-65)/image.height)
        image=image.resize((max(1,int(image.width*scale)),max(1,int(image.height*scale))),Image.Resampling.NEAREST)
    else:
        image.thumbnail((width,height-65))
    panel = Image.new('RGB',(width,height),'#181818')
    panel.paste(image,(0,65))
    draw = ImageDraw.Draw(panel)
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14) if Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf').exists() else ImageFont.load_default()
    draw.text((5,2),f"{item['sample_id']} {item.get('stratum_class','scene search')} {item['path'].split('/')[1]}",fill='white',font=font)
    draw.text((5,23),Path(item['path']).name,fill='white',font=font)
    draw.text((5,44),'P=person H=helmet V=vest NH=visible no helmet NV=visible no vest',fill='white',font=font)
    for row in rows_for(root,item['path']):
        source,x,y,w,h=row; source=int(source)
        if source not in COLORS: continue
        scale_x=image.width/(crop_right-crop_left); scale_y=image.height/(crop_bottom-crop_top)
        left=max(0,((x-w/2)*original_width-crop_left)*scale_x)
        top=max(0,((y-h/2)*original_height-crop_top)*scale_y)+65
        right=min(image.width,((x+w/2)*original_width-crop_left)*scale_x)
        bottom=min(image.height,((y+h/2)*original_height-crop_top)*scale_y)+65
        if left>=right or top>=bottom: continue
        draw.rectangle((left,top,right,bottom),outline=COLORS[source],width=2)
        draw.text((left,max(65,top-16)),{5:'P',0:'H',2:'V',6:'NH',11:'NV'}[source],fill=COLORS[source],font=font)
    return panel


def write_pages(root, items, output, prefix, focus=False):
    for start in range(0,len(items),4):
        page=Image.new('RGB',(1440,1080),'#181818')
        for i,item in enumerate(items[start:start+4]):
            page.paste(annotation_panel(root,item,focus=focus),((i%2)*720,(i//2)*540))
        page.save(output/f'{prefix}-{start//4+1:02}.png')


def run(root, output):
    root,output=Path(root).resolve(),Path(output).resolve()
    if root==output or root in output.parents:
        raise ValueError('Diagnostics must be outside originals')
    output.mkdir(parents=True,exist_ok=True)
    inventory = {p.relative_to(root).as_posix(): sha256(p) for p in sorted((root/'images').rglob('*.jpg'))}
    cache=output/'scene_features.json'
    if cache.exists():
        cached=json.loads(cache.read_text())
        if cached['inventory'] != inventory:
            raise ValueError('Feature cache does not match source images')
        records=cached['records']
    else:
        records=[]
        for relative in inventory:
            with Image.open(root/relative) as opened:
                record=features(opened.convert('RGB'))
            records.append(dict(path=relative,**record))
        cache.write_text(json.dumps({'inventory':inventory,'records':records},indent=2)+'\n')
    pairs=scene_candidates(records)
    (output/'scene_candidates.json').write_text(json.dumps(pairs,indent=2)+'\n')
    sample=select_sample(root,records)
    (output/'review_sample.json').write_text(json.dumps(sample,indent=2)+'\n')
    write_pages(root,sample,output,'sample')
    write_pages(root,[s for s in sample if s['filename_family']=='source-'],output,'focus',focus=True)
    # Top-ranked candidate endpoints are a visual triage queue, not adjudicated groups.
    endpoints=sorted({p[side] for p in pairs[:30] for side in ('left','right')})
    queue=[{'sample_id':f'Q{i+1:02}','path':path} for i,path in enumerate(endpoints)]
    (output/'scene_review_queue.json').write_text(json.dumps(queue,indent=2)+'\n')
    write_pages(root,queue,output,'scenes')
    # Retrieve additional neighbors of the audited gate scene, beyond pair thresholds.
    seed_paths={'images/train/source-3978abe9cfed5d8a5faa5a98dfe4b00a.jpg',
                'images/train/source-efc23273c04e007083114c0f217335f0.jpg',
                'images/val/source-9e10b0409f922546c35b276eb5a5756e.jpg'}
    seeds=[r for r in records if r['path'] in seed_paths]
    neighbors=[]
    for record in records:
        if record['path'] in endpoints: continue
        if not seeds: break
        score=min((record['whole']^seed['whole']).bit_count()/64+
                  (record['border']^seed['border']).bit_count()/256 for seed in seeds)
        neighbors.append((score,record['path']))
    neighbors=sorted(neighbors)[:12]
    neighbor_queue=[{'sample_id':f'N{i+1:02}','path':path,'retrieval_score':score}
                    for i,(score,path) in enumerate(neighbors)]
    (output/'seed_neighbors.json').write_text(json.dumps(neighbor_queue,indent=2)+'\n')
    write_pages(root,neighbor_queue,output,'neighbors')
    summary={'images_searched':len(records),'candidate_pairs':len(pairs),
             'cross_split_candidates':sum(p['cross_split'] for p in pairs),
             'stratified_images':len(sample),'scene_queue_images':len(queue),
             'additional_gate_neighbors':len(neighbor_queue),
             'method':'whole dHash<=12 OR border dHash<=32/256 plus color MAE<=25; aspect difference<=10%'}
    (output/'search_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    run(args.root,args.output)
