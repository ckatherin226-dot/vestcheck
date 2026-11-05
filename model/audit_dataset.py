"""Read-only YOLO dataset audit; writes JSON and Markdown outside the dataset.

Requires images/train, images/val, labels/train and labels/val. No corrections,
remapping, split changes or model execution are performed. Detailed local reports
may contain source filenames; review before publishing, especially for private data.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageOps
import yaml

try:  # Support both `python model/audit_dataset.py` and unit-test imports.
    from .acquire_dataset import sha256
except ImportError:
    from acquire_dataset import sha256

EXPECTED_NAMES = ['helmet', 'gloves', 'vest', 'boots', 'goggles', 'Person',
                  'no_helmet', 'no_goggle', 'no_gloves', 'no_boots', 'forklift', 'no_vest']
TARGETS = [(5, 'worker'), (0, 'hard_hat'), (2, 'safety_vest'),
           (6, 'visible_missing_hard_hat'), (11, 'visible_missing_safety_vest')]
IMAGE_SUFFIXES = {'.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tif', '.tiff',
                  '.avif', '.heic', '.heif', '.dng'}


def validate_row(line, class_count):
    """Return (parsed box, error category) for one nonempty YOLO detection row."""
    fields = line.split()
    if len(fields) != 5:
        return None, 'malformed_row'
    try:
        if not fields[0].isascii() or not fields[0].isdigit():
            return None, 'invalid_class'
        class_id = int(fields[0])
        if not 0 <= class_id < class_count:
            return None, 'invalid_class'
        x, y, width, height = map(float, fields[1:])
    except ValueError:
        return None, 'malformed_row'
    if (not all(math.isfinite(v) for v in (x, y, width, height))
            or not (0 <= x <= 1 and 0 <= y <= 1 and 0 < width <= 1 and 0 < height <= 1)
            or x - width / 2 < -1e-6 or x + width / 2 > 1 + 1e-6
            or y - height / 2 < -1e-6 or y + height / 2 > 1 + 1e-6):
        return None, 'invalid_bbox'
    return (class_id, x, y, width, height), None


def boundary_overhang(line):
    """Measure small corner excursions separately from malformed/invalid boxes."""
    fields = line.split()
    if len(fields) != 5:
        return None
    try:
        x, y, width, height = map(float, fields[1:])
    except ValueError:
        return None
    if not (all(math.isfinite(v) for v in (x, y, width, height))
            and 0 <= x <= 1 and 0 <= y <= 1 and 0 < width <= 1 and 0 < height <= 1):
        return None
    return max(0, width / 2 - x, x + width / 2 - 1,
               height / 2 - y, y + height / 2 - 1)


def difference_hash(image):
    """64-bit horizontal dHash. Similar hashes flag review, not proven duplicates."""
    pixels = list(image.convert('L').resize((9, 8), Image.Resampling.LANCZOS).get_flattened_data())
    value = 0
    for row in range(8):
        for column in range(8):
            value = (value << 1) | (pixels[row * 9 + column] > pixels[row * 9 + column + 1])
    return value


def inspect_image(path):
    """Fully decode images (not just headers), then hash orientation-normalized RGB."""
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        image.load()
        rgb = ImageOps.exif_transpose(image).convert('RGB')
        digest = hashlib.sha256()
        digest.update(f'{rgb.width}x{rgb.height}:RGB:'.encode())
        digest.update(rgb.tobytes())
        return {'width': rgb.width, 'height': rgb.height,
                'pixel_sha256': digest.hexdigest(), 'dhash': difference_hash(rgb)}


def duplicate_groups(records, key):
    groups = defaultdict(list)
    for record in records:
        if key in record:
            groups[record[key]].append(record['path'])
    return [paths for paths in groups.values() if len(paths) > 1]


def cross_split_group(group):
    return len({Path(path).parts[1] for path in group}) > 1


def near_duplicate_pairs(records, threshold=4):
    """Compare all decoded images; exclude proven encoded/pixel duplicates."""
    pairs = []
    decoded = [record for record in records if 'dhash' in record]
    for index, left in enumerate(decoded):
        for right in decoded[index + 1:]:
            if left['sha256'] == right['sha256'] or left['pixel_sha256'] == right['pixel_sha256']:
                continue
            ratio_a = left['width'] / left['height']
            ratio_b = right['width'] / right['height']
            if abs(ratio_a - ratio_b) / max(ratio_a, ratio_b) > 0.05:
                continue
            distance = (left['dhash'] ^ right['dhash']).bit_count()
            if distance <= threshold:
                pairs.append({'left': left['path'], 'right': right['path'],
                              'distance': distance, 'cross_split': left['split'] != right['split']})
    return pairs


def box_iou(left, right):
    def edges(box):
        _, x, y, w, h = box
        return x - w / 2, y - h / 2, x + w / 2, y + h / 2
    a, b = edges(left), edges(right)
    area = max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[1], b[1]))
    union = left[3] * left[4] + right[3] * right[4] - area
    return area / union if union else 0


def load_config(path):
    config = yaml.safe_load(Path(path).read_text())
    names = config['names']
    if isinstance(names, dict):
        if set(names) != set(range(len(names))):
            raise ValueError('Class IDs must be contiguous zero-based integers')
        names = [names[i] for i in range(len(names))]
    if not isinstance(names, list) or not names or not all(isinstance(n, str) for n in names):
        raise ValueError('Invalid names in YAML')
    return config, names


def inspect_manifest(root, records, annotation_counts):
    """Cross-check optional publisher JSONL metadata; do not infer image origin."""
    path = root / 'manifest.jsonl'
    if not path.is_file():
        return {'present': False}
    images = {r['path']: r for r in records}
    result = {'present': True, 'rows': 0, 'field_counts': Counter(),
              'duplicate_entries': 0, 'missing_images': 0, 'hash_mismatches': 0,
              'annotation_count_mismatches': 0, 'dimension_mismatches': 0,
              'invalid_rows': 0}
    seen = set()
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        result['rows'] += 1
        try:
            row = json.loads(line)
            key = f"images/{row['split']}/{row['file']}"
            result['field_counts'].update(row.keys())
            if key in seen:
                result['duplicate_entries'] += 1
            seen.add(key)
            record = images.get(key)
            if record is None:
                result['missing_images'] += 1
                continue
            result['hash_mismatches'] += int(row['sha256'] != record['sha256'])
            result['annotation_count_mismatches'] += int(row['annotations'] != annotation_counts.get(key))
            if 'width' in row and 'height' in row:
                result['dimension_mismatches'] += int(
                    (row['width'], row['height']) != (record.get('width'), record.get('height')))
        except (ValueError, KeyError, TypeError, AttributeError):
            result['invalid_rows'] += 1
    result['images_not_in_manifest'] = len(set(images) - seen)
    result['field_counts'] = dict(result['field_counts'])
    return result


def audit(root, config_path, near_threshold=4):
    root = Path(root).resolve()
    config, names = load_config(config_path)
    mapping_matches = names == EXPECTED_NAMES
    # Refuse silent partial audits: this tool deliberately supports the documented layout.
    for split in ('train', 'val'):
        for kind in ('images', 'labels'):
            if not (root / kind / split).is_dir():
                raise ValueError(f'Missing required directory: {kind}/{split}')
        if config.get(split) != f'images/{split}':
            raise ValueError(f'Unsupported configured {split} path; review layout explicitly')
    files_before = {p.relative_to(root).as_posix(): sha256(p)
                    for p in sorted(root.rglob('*')) if p.is_file()}
    issues, records, split_counts = [], [], {}
    conflict_pairs, repeated_rows, overhangs = [], [], []
    annotation_counts = {}
    for split in ('train', 'val'):
        image_dir, label_dir = root / 'images' / split, root / 'labels' / split
        images = sorted(p for p in image_dir.rglob('*') if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES)
        labels = sorted(label_dir.rglob('*.txt'))
        by_stem = defaultdict(list)
        for image in images:
            by_stem[image.relative_to(image_dir).with_suffix('').as_posix()].append(image)
        counts = {'images': len(images), 'label_files': len(labels), 'nonempty_rows': 0,
                  'valid_annotations': 0, 'invalid_rows': 0, 'invalid_bbox': 0,
                  'empty_label_files': 0, 'missing_labels': 0, 'orphan_labels': 0,
                  'corrupt_images': 0, 'unreadable_labels': 0,
                  'ambiguous_image_stems': sum(len(v) > 1 for v in by_stem.values()),
                  'class_counts': {str(i): 0 for i in range(len(names))},
                  'source_class_counts': {str(i): 0 for i in range(len(names))}}
        paired_labels = set()
        for image in images:
            relative = image.relative_to(root).as_posix()
            record = {'path': relative, 'split': split, 'sha256': files_before[relative]}
            try:
                record.update(inspect_image(image))
            except (OSError, ValueError, Image.DecompressionBombError):
                counts['corrupt_images'] += 1
                issues.append({'file': relative, 'error': 'corrupt_or_unsupported_image'})
            records.append(record)
            key = image.relative_to(image_dir).with_suffix('').as_posix()
            label = label_dir / (key + '.txt')
            if not label.is_file():
                counts['missing_labels'] += 1
                issues.append({'file': relative, 'error': 'missing_label_background_or_missing_annotation'})
            elif len(by_stem[key]) > 1:
                issues.append({'file': relative, 'error': 'ambiguous_image_stem'})
            else:
                paired_labels.add(label)
        for label in labels:
            relative = label.relative_to(root).as_posix()
            key = label.relative_to(label_dir).with_suffix('').as_posix()
            if key not in by_stem:
                counts['orphan_labels'] += 1
                issues.append({'file': relative, 'error': 'orphan_label'})
            try:
                lines = [line for line in label.read_text().splitlines() if line.strip()]
            except (UnicodeError, OSError):
                counts['unreadable_labels'] += 1
                issues.append({'file': relative, 'error': 'unreadable_label'})
                continue
            if not lines:
                counts['empty_label_files'] += 1
            if label in paired_labels:
                annotation_counts[f'images/{split}/{by_stem[key][0].relative_to(image_dir).as_posix()}'] = len(lines)
            seen, boxes = set(), []
            for number, line in enumerate(lines, 1):
                counts['nonempty_rows'] += 1
                fields = line.split()
                if (label in paired_labels and fields[0].isascii() and fields[0].isdigit()
                        and 0 <= int(fields[0]) < len(names)):
                    counts['source_class_counts'][str(int(fields[0]))] += 1
                box, error = validate_row(line, len(names))
                if error:
                    counts['invalid_rows'] += 1
                    counts['invalid_bbox'] += int(error == 'invalid_bbox')
                    issues.append({'file': relative, 'nonempty_row': number, 'error': error})
                    if error == 'invalid_bbox':
                        overhangs.append(boundary_overhang(line))
                    continue
                if label in paired_labels:
                    counts['valid_annotations'] += 1
                    counts['class_counts'][str(box[0])] += 1
                if box in seen:
                    repeated_rows.append({'file': relative, 'nonempty_row': number})
                seen.add(box)
                boxes.append(box)
            if mapping_matches:
                for index, left in enumerate(boxes):
                    for right in boxes[index + 1:]:
                        if {left[0], right[0]} in ({0, 6}, {2, 11}) and box_iou(left, right) >= 0.5:
                            conflict_pairs.append({'file': relative, 'classes': [left[0], right[0]],
                                                   'iou': round(box_iou(left, right), 4)})
        split_counts[split] = counts
    encoded = duplicate_groups(records, 'sha256')
    pixels = duplicate_groups(records, 'pixel_sha256')
    near = near_duplicate_pairs(records, near_threshold)
    totals = {key: sum(split_counts[s][key] for s in split_counts)
              for key in split_counts['train'] if not isinstance(split_counts['train'][key], dict)}
    for key in ('class_counts', 'source_class_counts'):
        totals[key] = {str(i): sum(split_counts[s][key][str(i)] for s in split_counts)
                       for i in range(len(names))}
    unchanged = files_before == {p.relative_to(root).as_posix(): sha256(p)
                                 for p in sorted(root.rglob('*')) if p.is_file()}
    return {'schema_version': 1, 'audited_at_utc': datetime.now(timezone.utc).isoformat(),
            'pillow_version': Image.__version__, 'configuration_sha256': sha256(config_path),
            'source_names': names, 'mapping_matches': mapping_matches,
            'proposed_mapping': [{'target_id': i, 'target': name, 'source_id': source}
                                 for i, (source, name) in enumerate(TARGETS)] if mapping_matches else [],
            'splits': split_counts, 'totals': totals, 'issues': issues,
            'exact_file_groups': encoded, 'exact_pixel_groups': pixels,
            'cross_split_file_groups': sum(cross_split_group(g) for g in encoded),
            'cross_split_pixel_groups': sum(cross_split_group(g) for g in pixels),
            'near_duplicate_method': {'algorithm': '64-bit horizontal dHash',
                                      'max_hamming_distance': near_threshold,
                                      'max_relative_aspect_difference': 0.05,
                                      'excludes_exact_file_or_pixel_pairs': True},
            'near_duplicate_pairs': near,
            'cross_split_near_pairs': sum(p['cross_split'] for p in near),
            'duplicate_annotation_rows': repeated_rows, 'positive_negative_overlap_candidates': conflict_pairs,
            'bbox_boundary_analysis': {
                'strict_corner_tolerance': 1e-6,
                'rounding_candidate_threshold': 1e-5,
                'rounding_candidate_rows': sum(v is not None and v <= 1e-5 for v in overhangs),
                'other_invalid_bbox_rows': sum(v is None or v > 1e-5 for v in overhangs),
                'maximum_measurable_overhang': max((v for v in overhangs if v is not None), default=0)},
            'publisher_manifest': inspect_manifest(root, records, annotation_counts),
            'original_files_unchanged_during_audit': unchanged,
            'inspected_files': len(files_before),
            'metadata_files': [p for p in files_before if not p.startswith(('images/', 'labels/'))],
            'unknown_image_directory_files': [p.relative_to(root).as_posix() for p in (root / 'images').rglob('*')
                                             if p.is_file() and p.suffix.lower() not in IMAGE_SUFFIXES],
            'limits': ['Missing or empty labels may represent intended background, not proven missing annotations.',
                       'Class counts include valid paired rows, including repeated rows; orphan/ambiguous rows excluded.',
                       'Hashes cannot establish scene-disjoint splits; dHash can miss crop/rotation changes or flag unrelated images.',
                       'Positive/negative IoU candidates are not proven contradictions or PPE ownership links.',
                       'Automated geometry checks do not establish annotation completeness, correctness, or real/generated provenance.']}


def markdown_report(report):
    lines = ['# Automated dataset audit', '', f"Run: {report['audited_at_utc']}", '',
             f"Mapping matches expected classes: {report['mapping_matches']}", '',
             '| Metric | Train | Validation | Total |', '| --- | ---: | ---: | ---: |']
    for key, value in report['totals'].items():
        if not isinstance(value, dict):
            lines.append(f"| {key} | {report['splits']['train'][key]} | {report['splits']['val'][key]} | {value} |")
    lines += ['', '| Class | Train | Validation | Total |', '| --- | ---: | ---: | ---: |']
    for i, name in enumerate(report['source_names']):
        lines.append(f"| {i}: {name} | {report['splits']['train']['class_counts'][str(i)]} | "
                     f"{report['splits']['val']['class_counts'][str(i)]} | {report['totals']['class_counts'][str(i)]} |")
    lines += ['', 'The table above counts geometrically valid paired rows only.', '',
              '| Source class (all paired rows) | Train | Validation | Total |',
              '| --- | ---: | ---: | ---: |']
    for i, name in enumerate(report['source_names']):
        key = str(i)
        lines.append(f"| {i}: {name} | {report['splits']['train']['source_class_counts'][key]} | "
                     f"{report['splits']['val']['source_class_counts'][key]} | {report['totals']['source_class_counts'][key]} |")
    for name in ('exact_file_groups', 'exact_pixel_groups', 'cross_split_file_groups',
                 'cross_split_pixel_groups', 'near_duplicate_pairs', 'cross_split_near_pairs',
                 'duplicate_annotation_rows', 'positive_negative_overlap_candidates'):
        value = report[name]
        lines.append(f"\n{name}: {len(value) if isinstance(value, list) else value}")
    lines += ['', '## Limits', ''] + ['- ' + line for line in report['limits']]
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--near-threshold', type=int, default=4, choices=range(65))
    args = parser.parse_args()
    root, output = args.root.resolve(), args.output.resolve()
    if output == root or root in output.parents:
        parser.error('Output must be outside the original dataset')
    report = audit(root, args.config, args.near_threshold)
    output.mkdir(parents=True, exist_ok=True)
    (output / 'audit.json').write_text(json.dumps(report, indent=2) + '\n')
    (output / 'audit.md').write_text(markdown_report(report))
    print(markdown_report(report))
    # A nonzero quality gate leaves the detailed report available for human review.
    errors = report['totals']
    if (not report['mapping_matches'] or not report['original_files_unchanged_during_audit']
            or any(errors[k] for k in ('invalid_rows', 'corrupt_images', 'unreadable_labels',
                                      'orphan_labels', 'ambiguous_image_stems'))):
        raise SystemExit(2)


if __name__ == '__main__':
    main()
