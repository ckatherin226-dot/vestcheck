"""Synthetic fixtures only: no source dataset images or model dependencies."""
import json
from pathlib import Path
import shutil
import stat
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from PIL import Image, PngImagePlugin
import yaml

from model.acquire_dataset import acquire, extract_originals, sha256
from model.audit_dataset import (EXPECTED_NAMES, audit, box_iou, inspect_image,
                                 boundary_overhang, markdown_report, near_duplicate_pairs, validate_row)


class LabelValidationTests(unittest.TestCase):
    def test_valid_edge_and_scientific_notation(self):
        for line in ('0 .5 .5 1 1', '11 5e-1 .5 .1 .2', '5 .1 .1 .2 .2'):
            with self.subTest(line=line):
                self.assertIsNone(validate_row(line, 12)[1])

    def test_invalid_rows(self):
        cases = {
            '0 .5 .5 .1': 'malformed_row',
            '0 .5 .5 .1 .1 extra': 'malformed_row',
            '12 .5 .5 .1 .1': 'invalid_class',
            '-1 .5 .5 .1 .1': 'invalid_class',
            '1.0 .5 .5 .1 .1': 'invalid_class',
            '0 nan .5 .1 .1': 'invalid_bbox',
            '0 .5 .5 inf .1': 'invalid_bbox',
            '0 .5 .5 0 .1': 'invalid_bbox',
            '0 .5 .5 -.1 .1': 'invalid_bbox',
            '0 .99 .5 .1 .1': 'invalid_bbox',
            '0 .5 .5 1.1 .1': 'invalid_bbox',
            '0 text .5 .1 .1': 'malformed_row',
        }
        for line, expected in cases.items():
            with self.subTest(line=line):
                self.assertEqual(validate_row(line, 12)[1], expected)

    def test_iou(self):
        self.assertAlmostEqual(box_iou((0,.5,.5,.2,.2), (6,.5,.5,.2,.2)), 1)
        self.assertEqual(box_iou((0,.1,.1,.1,.1), (6,.9,.9,.1,.1)), 0)

    def test_small_boundary_excursion_is_not_silently_accepted(self):
        line = '5 .402330 .574780 .288170 .850450'
        self.assertEqual(validate_row(line, 12)[1], 'invalid_bbox')
        self.assertAlmostEqual(boundary_overhang(line), .000005)
        self.assertIsNone(boundary_overhang('5 nan .5 .2 .2'))


class DatasetTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        for kind in ('images', 'labels'):
            for split in ('train', 'val'):
                (self.root / kind / split).mkdir(parents=True)
        self.config = self.root / 'data.yaml'
        self.config.write_text(yaml.safe_dump({'train':'images/train', 'val':'images/val',
                                               'names': dict(enumerate(EXPECTED_NAMES))}))

    def image(self, split, name, label='5 .5 .5 .4 .4\n', color='red'):
        path = self.root / 'images' / split / name
        Image.new('RGB', (24, 24), color).save(path)
        if label is not None:
            (self.root / 'labels' / split / Path(name).with_suffix('.txt')).write_text(label)
        return path

    def test_clean_counts_mapping_and_no_mutation(self):
        self.image('train', 'one.png', '5 .5 .5 .4 .4\n0 .5 .2 .1 .1\n')
        self.image('val', 'two.png', '', color='blue')
        report = audit(self.root, self.config)
        self.assertEqual(report['totals']['images'], 2)
        self.assertEqual(report['totals']['valid_annotations'], 2)
        self.assertEqual(report['totals']['empty_label_files'], 1)
        self.assertEqual(report['totals']['class_counts']['5'], 1)
        self.assertTrue(report['mapping_matches'])
        self.assertEqual(report['proposed_mapping'][0]['source_id'], 5)
        self.assertTrue(report['original_files_unchanged_during_audit'])
        self.assertIn('| 0: helmet | 1 | 0 | 1 |', markdown_report(report))

    def test_missing_orphan_corrupt_and_invalid(self):
        self.image('train','missing.png',None)
        self.image('train','bad.png','0 .99 .5 .1 .1\n99 .5 .5 .1 .1\n')
        (self.root/'images/val/corrupt.jpg').write_bytes(b'not an image')
        (self.root/'labels/val/corrupt.txt').write_text('')
        (self.root/'labels/val/orphan.txt').write_text('5 .5 .5 .2 .2\n')
        report = audit(self.root, self.config)
        for key in ('missing_labels','orphan_labels','corrupt_images','invalid_bbox'):
            self.assertEqual(report['totals'][key], 1, key)
        self.assertEqual(report['totals']['invalid_rows'], 2)
        self.assertEqual(report['totals']['valid_annotations'], 0)  # orphan not counted

    def test_duplicate_rows_and_opposing_labels(self):
        self.image('train','one.png','0 .5 .5 .2 .2\n0 .5 .5 .2 .2\n6 .5 .5 .2 .2\n')
        report = audit(self.root, self.config)
        self.assertEqual(len(report['duplicate_annotation_rows']),1)
        self.assertEqual(len(report['positive_negative_overlap_candidates']),2)
        self.assertEqual(report['totals']['valid_annotations'],3)

    def test_file_and_decoded_duplicates_across_splits(self):
        first = self.image('train','one.png')
        other = self.image('val','two.png')
        shutil.copyfile(first, other)
        metadata = PngImagePlugin.PngInfo(); metadata.add_text('note','different encoding')
        third = self.image('val','three.png')
        Image.new('RGB',(24,24),'red').save(third, pnginfo=metadata)
        self.assertNotEqual(sha256(first),sha256(third))
        report = audit(self.root,self.config)
        self.assertEqual(len(report['exact_file_groups']),1)
        self.assertEqual(len(report['exact_pixel_groups'][0]),3)
        self.assertEqual(report['cross_split_file_groups'],1)
        self.assertEqual(report['cross_split_pixel_groups'],1)
        self.assertEqual(report['near_duplicate_pairs'],[])

    def test_near_hash_is_heuristic_and_aspect_filtered(self):
        first = self.image('train','one.png',color='red')
        second = self.image('val','two.png',color='blue')
        records=[]
        for path, split in [(first,'train'),(second,'val')]:
            records.append(dict(path=str(path),split=split,sha256=sha256(path),**inspect_image(path)))
        self.assertEqual(len(near_duplicate_pairs(records,0)),1)  # flat colors collide
        records[1]['width']=100
        self.assertEqual(near_duplicate_pairs(records,4),[])

    def test_mapping_mismatch_and_unsupported_layout(self):
        self.config.write_text('train: images/train\nval: images/val\nnames: [different]\n')
        report=audit(self.root,self.config)
        self.assertFalse(report['mapping_matches'])
        self.assertEqual(report['proposed_mapping'],[])
        self.config.write_text('train: elsewhere\nval: images/val\nnames: [different]\n')
        with self.assertRaises(ValueError): audit(self.root,self.config)

    def test_ambiguous_stems_and_unreadable_label(self):
        self.image('train','one.png')
        self.image('train','one.jpg')
        self.image('val','two.png')
        (self.root/'labels/val/two.txt').write_bytes(b'\xff')
        report=audit(self.root,self.config)
        self.assertEqual(report['totals']['ambiguous_image_stems'],1)
        self.assertEqual(report['totals']['unreadable_labels'],1)
        self.assertEqual(report['totals']['valid_annotations'],0)

    def test_missing_directory_fails_instead_of_zero_image_success(self):
        (self.root/'images/val').rmdir()
        with self.assertRaises(ValueError): audit(self.root,self.config)

    def test_manifest_hash_annotation_and_dimension_checks(self):
        image = self.image('train','one.png')
        row = dict(file='one.png', split='train', sha256=sha256(image),
                   annotations=1, width=24, height=24)
        manifest = self.root/'manifest.jsonl'
        manifest.write_text(json.dumps(row)+'\n')
        result=audit(self.root,self.config)['publisher_manifest']
        self.assertEqual(result['rows'],1)
        self.assertEqual(result['hash_mismatches'],0)
        self.assertEqual(result['annotation_count_mismatches'],0)
        row.update(sha256='wrong',annotations=2,width=25)
        manifest.write_text(json.dumps(row)+'\n')
        result=audit(self.root,self.config)['publisher_manifest']
        for key in ('hash_mismatches','annotation_count_mismatches','dimension_mismatches'):
            self.assertEqual(result[key],1,key)

    def test_source_counts_include_flagged_rows_but_valid_counts_do_not(self):
        self.image('train','one.png','05 .5 .5 .2 .2\n5 .99 .5 .1 .1\n')
        report=audit(self.root,self.config)
        self.assertEqual(report['totals']['source_class_counts']['5'],2)
        self.assertEqual(report['totals']['class_counts']['5'],1)
        self.assertEqual(report['bbox_boundary_analysis']['other_invalid_bbox_rows'],1)


class AcquisitionTests(unittest.TestCase):
    def test_changed_official_archive_url_blocks_download(self):
        repo=Path(__file__).resolve().parents[1]
        (repo/'model/data').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=repo/'model/data') as temporary:
            workspace=Path(temporary)/'new'
            def fake_download(url, path):
                content = 'download: https://example.com/changed.zip\n' if path.suffix=='.yaml' else 'Images and annotations CC BY 4.0'
                path.write_text(content)
            with patch('model.acquire_dataset.download',side_effect=fake_download) as network:
                with self.assertRaises(ValueError): acquire(workspace)
                self.assertEqual(network.call_count,2)
            metadata=json.loads((workspace/'acquisition.json').read_text())
            self.assertEqual(metadata['status'],'blocked_or_failed')
            self.assertFalse((workspace/'original').exists())

    def test_safe_extraction_and_manifest_hash(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary); archive=root/'archive.zip'
            with zipfile.ZipFile(archive,'w') as zipped: zipped.writestr('dataset/data.yaml','names: []')
            extract_originals(archive,root/'original')
            self.assertEqual((root/'original/dataset/data.yaml').read_text(),'names: []')
            with self.assertRaises(FileExistsError): extract_originals(archive,root/'original')

    def test_reject_zip_traversal_and_symlink(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            for name in ('../escape','/absolute','folder/../../escape','bad\\path','C:/drive'):
                with self.subTest(name=name):
                    archive=root/'bad.zip'
                    with zipfile.ZipFile(archive,'w') as zipped: zipped.writestr(name,'bad')
                    with self.assertRaises(ValueError): extract_originals(archive,root/'original')
                    self.assertFalse((root/'original').exists())
            info=zipfile.ZipInfo('link'); info.create_system=3; info.external_attr=(stat.S_IFLNK | 0o777)<<16
            with zipfile.ZipFile(root/'link.zip','w') as zipped: zipped.writestr(info,'../../target')
            with self.assertRaises(ValueError): extract_originals(root/'link.zip',root/'original')

    def test_existing_workspace_not_overwritten(self):
        repo=Path(__file__).resolve().parents[1]
        (repo/'model/data').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=repo/'model/data') as temporary:
            workspace=Path(temporary); marker=workspace/'acquisition.json'; marker.write_text('keep')
            with self.assertRaises(FileExistsError): acquire(workspace)
            self.assertEqual(marker.read_text(),'keep')


if __name__ == '__main__':
    unittest.main()
