"""Small synthetic fixtures for preparation; never train or fetch datasets."""
import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image
import yaml

from model.acquire_dataset import file_manifest, sha256
from model.audit_dataset import EXPECTED_NAMES, validate_row
from model.prepare_dataset import corrected_row, prepare, transform_label, verify_prepared
from model.review_dataset import features, scene_candidates, select_sample


class CorrectionTests(unittest.TestCase):
    def test_exact_clipping_and_unchanged_values(self):
        source,coordinates,changed=corrected_row('5 .402330 .574780 .288170 .850450')
        self.assertEqual((source,changed),(5,True))
        self.assertEqual(coordinates,['0.40233','0.5747775','0.28817','0.850445'])
        self.assertIsNone(validate_row('5 '+' '.join(coordinates),12)[1])
        self.assertEqual(corrected_row('0 .5 .5 .20 .20'),(0,['.5','.5','.20','.20'],False))

    def test_each_boundary_is_clipped_only_in_derived_result(self):
        for line in ['5 .049995 .5 .1 .2','5 .950005 .5 .1 .2',
                     '5 .5 .049995 .2 .1','5 .5 .950005 .2 .1']:
            with self.subTest(line=line):
                source,coordinates,changed=corrected_row(line)
                self.assertTrue(changed)
                self.assertIsNone(validate_row(f'{source} '+' '.join(coordinates),12)[1])

    def test_reject_gross_invalid_or_malformed(self):
        for line in ['5 .99 .5 .1 .1','5 nan .5 .1 .1','99 .5 .5 .1 .1',
                     '5 .5 .5 -1 .1','5 .5 .5 .2','5 .5 .5 1.2 .2']:
            with self.subTest(line=line):
                with self.assertRaises(ValueError): corrected_row(line)

    def test_all_source_ids_remap_and_dropped_flags_are_logged(self):
        text='\n'.join(f'{i} .5 .5 .2 .2' for i in range(12))
        derived,actions=transform_label(text)
        self.assertEqual([int(row.split()[0]) for row in derived.splitlines()],[1,2,0,3,4])
        self.assertEqual(sum(a['action']=='drop_out_of_scope' for a in actions),7)
        empty,actions=transform_label('10 .049995 .5 .1 .2')
        self.assertEqual(empty,'')
        self.assertTrue(actions[0]['boundary_flag'])
        self.assertEqual(actions[0]['action'],'drop_out_of_scope')


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base=Path(self.temporary.name)
        self.root=self.base/'original'/'construction-ppe'
        for split in ('train','val'):
            (self.root/'images'/split).mkdir(parents=True)
            (self.root/'labels'/split).mkdir(parents=True)
            Image.new('RGB',(16,16),'red').save(self.root/'images'/split/'one.png')
            (self.root/'labels'/split/'one.txt').write_text('5 .402330 .574780 .288170 .850450\n0 .5 .5 .1 .1\n10 .5 .5 .1 .1\n')
        (self.root/'data.yaml').write_text(yaml.safe_dump({'train':'images/train','val':'images/val','names':dict(enumerate(EXPECTED_NAMES))}))
        (self.root/'LICENSE.txt').write_text('Synthetic license fixture')
        (self.root/'README.md').write_text('Synthetic fixture, no real images')
        self.baseline=self.base/'baseline.json'
        self.baseline.write_text(json.dumps(file_manifest(self.root.parent)))
        self.review=self.base/'review.json'
        image=self.root/'images/train/one.png'
        self.review.write_text(json.dumps({'status':'reviewed_sample_not_full_clearance',
                                          'sample':[{'path':'images/train/one.png','sha256':sha256(image),'notes':'Synthetic test fixture only'}]}))
        self.output=self.base/'derived'

    def test_end_to_end_counts_copies_manifests_and_no_split_changes(self):
        before=file_manifest(self.root)
        summary=prepare(self.root,self.output,self.baseline,self.review)
        self.assertEqual(summary['retained_rows'],4)
        self.assertEqual(summary['dropped_rows'],2)
        self.assertEqual(summary['retained_corrections'],2)
        self.assertFalse(summary['training_ready'])
        self.assertEqual(summary['split_changes'],0)
        self.assertTrue(summary['originals_unchanged'])
        self.assertEqual(before,file_manifest(self.root))
        self.assertEqual(summary['class_counts'],{'0':2,'1':2,'2':0,'3':0,'4':0})
        records=[json.loads(line) for line in (self.output/'transformation.jsonl').read_text().splitlines()]
        self.assertEqual(len(records),2)
        for row in records:
            self.assertEqual(row['source_image_sha256'],row['derived_image_sha256'])
            self.assertEqual(row['source_split'],row['derived_split'])
        # Editing a derivative cannot mutate originals through a shared inode.
        (self.output/'images/train/one.png').write_bytes(b'changed')
        self.assertEqual(before,file_manifest(self.root))

    def test_background_images_are_retained(self):
        (self.root/'labels/val/one.txt').write_text('10 .5 .5 .2 .2\n')
        self.baseline.write_text(json.dumps(file_manifest(self.root.parent)))
        summary=prepare(self.root,self.output,self.baseline,self.review)
        self.assertEqual(summary['splits']['val']['background_images'],1)
        self.assertEqual((self.output/'labels/val/one.txt').read_text(),'')
        self.assertTrue((self.output/'images/val/one.png').is_file())

    def test_changed_original_or_review_hash_fails_before_output(self):
        (self.root/'labels/val/one.txt').write_text('changed')
        with self.assertRaises(ValueError): prepare(self.root,self.output,self.baseline,self.review)
        self.assertFalse(self.output.exists())
        self.baseline.write_text(json.dumps(file_manifest(self.root.parent)))
        review=json.loads(self.review.read_text());review['sample'][0]['sha256']='wrong'
        self.review.write_text(json.dumps(review))
        with self.assertRaises(ValueError): prepare(self.root,self.output,self.baseline,self.review)
        self.assertFalse(self.output.exists())

    def test_invalid_row_leaves_no_published_output_and_existing_data_survives(self):
        (self.root/'labels/val/one.txt').write_text('5 .99 .5 .2 .2')
        self.baseline.write_text(json.dumps(file_manifest(self.root.parent)))
        with self.assertRaises(ValueError): prepare(self.root,self.output,self.baseline,self.review)
        self.assertFalse(self.output.exists())
        self.output.mkdir(); (self.output/'keep').write_text('keep')
        with self.assertRaises(FileExistsError): prepare(self.root,self.output,self.baseline,self.review)
        self.assertEqual((self.output/'keep').read_text(),'keep')

    def test_nested_output_and_missing_pairing_rejected(self):
        with self.assertRaises(ValueError): prepare(self.root,self.root/'derived',self.baseline,self.review)
        (self.root/'labels/val/one.txt').unlink()
        self.baseline.write_text(json.dumps(file_manifest(self.root.parent)))
        with self.assertRaises(ValueError): prepare(self.root,self.output,self.baseline,self.review)
        self.assertFalse(self.output.exists())

    def test_mapping_schema_change_rejected(self):
        config=yaml.safe_load((self.root/'data.yaml').read_text());config['names'][5]='head'
        (self.root/'data.yaml').write_text(yaml.safe_dump(config))
        self.baseline.write_text(json.dumps(file_manifest(self.root.parent)))
        with self.assertRaises(ValueError): prepare(self.root,self.output,self.baseline,self.review)

    def test_repeatable_manifest_and_labels_across_runs(self):
        one=prepare(self.root,self.output,self.baseline,self.review)
        two=prepare(self.root,self.base/'derived-again',self.baseline,self.review)
        self.assertEqual(one['transformation_manifest_sha256'],two['transformation_manifest_sha256'])
        self.assertEqual((self.output/'labels/train/one.txt').read_bytes(),(self.base/'derived-again/labels/train/one.txt').read_bytes())

    def test_independent_verification_rejects_tampering(self):
        prepare(self.root,self.output,self.baseline,self.review)
        result=verify_prepared(self.output)
        self.assertEqual(result['verified_images'],2)
        self.assertEqual(result['verified_annotations'],4)
        (self.output/'labels/train/one.txt').write_text('0 .5 .5 .2 .2\n')
        with self.assertRaises(ValueError): verify_prepared(self.output)


class SceneSearchTests(unittest.TestCase):
    def test_stratified_sample_is_deterministic_and_unique(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);records=[]
            for split in ('train','val'):
                (root/'images'/split).mkdir(parents=True)
                (root/'labels'/split).mkdir(parents=True)
                for source in (5,0,2,6,11):
                    for family in ('source-','ultralytics-ppe-nov2026-'):
                        name=f'{family}{source}.png'
                        Image.new('RGB',(16,16),'blue').save(root/'images'/split/name)
                        (root/'labels'/split/Path(name).with_suffix('.txt')).write_text(f'{source} .5 .5 .2 .2\n')
                        records.append({'path':f'images/{split}/{name}'})
            one=select_sample(root,records)
            self.assertEqual(len(one),20)
            self.assertEqual(len({s['path'] for s in one}),20)
            self.assertEqual(one,select_sample(root,list(reversed(records))))

    def test_similar_borders_can_flag_different_foreground_and_aspect_filter(self):
        image=Image.new('RGB',(64,64),'blue')
        left=dict(path='images/train/a.jpg',**features(image))
        right=dict(left,path='images/val/b.jpg',whole=left['whole'] ^ ((1<<20)-1))
        pairs=scene_candidates([left,right])
        self.assertEqual(len(pairs),1)
        self.assertTrue(pairs[0]['cross_split'])
        right['aspect']=2
        self.assertEqual(scene_candidates([left,right]),[])

    def test_different_scenes_not_forced_into_groups(self):
        left=dict(path='images/train/a.jpg',whole=0,border=0,colors=[0]*12,aspect=1)
        right=dict(path='images/val/b.jpg',whole=(1<<64)-1,border=(1<<256)-1,colors=[255]*12,aspect=1)
        self.assertEqual(scene_candidates([left,right]),[])


if __name__=='__main__': unittest.main()
