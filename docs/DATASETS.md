# Dataset candidates and constraints

Phase 1 identifies candidates only. No images, annotations, weights, or training dependencies have been downloaded, audited, prepared, or used for training. Links are starting points, not verified license or compatibility approvals.

| Candidate | Potential use | Required checks in Phase 2 |
| --- | --- | --- |
| [Safety Helmet Wearing Dataset (SHWD)](https://github.com/njvisionpower/Safety-Helmet-Wearing-Dataset) | Helmet/head-related examples for the hard-hat portion of the task. | Verify current availability, license and upstream image rights; inspect class definitions and negative labels. Head labels cannot automatically substitute for full-worker boxes; vest coverage is not established. |
| [SH17 dataset](https://github.com/ahmadmughees/SH17dataset) | Industrial worker/PPE examples and potential hard-hat/vest coverage. | Verify source, license, exact class mapping, construction relevance, annotation completeness, and whether worker/PPE association is possible. Industrial imagery may differ from smartphone construction scenes. |
| [Ultralytics Construction-PPE dataset documentation](https://docs.ultralytics.com/datasets/detect/construction-ppe/) | Candidate construction PPE data and YOLO-format reference. | Verify provenance, access, dataset-specific rights, class definitions, and split quality independently of Ultralytics software licensing. |
| Consented independent smartphone photographs and short clips | Held-out target-domain evaluation and temporal duplicate tests. | Site permission, consent/privacy handling, annotation protocol, no split leakage, and secure storage outside Git. Do not collect private site material without authorization. |

## Selection checklist

1. Record source/version, download date, license, upstream provenance, redistribution terms, and image hashes in a non-sensitive manifest.
2. Inspect worker, hard-hat, and high-visibility vest labels, including occlusion and ambiguous cases. Do not infer negative PPE labels simply from missing annotations.
3. Audit annotation quality and define a common taxonomy, visibility rules, and PPE-to-worker association labels. Retain uncertain/unassessable cases.
4. Check class and scene balance, small/distant workers, lighting, occlusion, camera angles, and target-domain coverage.
5. Remove exact/near duplicates and split by site/source/scene before training, keeping adjacent video frames and the same scene out of different splits.
6. Freeze an untouched test set and independently collected smartphone evaluation set. Use validation data for thresholds and model selection, not the test set.
7. Document dataset and software licensing separately, including Ultralytics model/export/distribution terms. Stop acquisition if rights or access cannot be established.

PPE association, temporal event labels, and assessability may need additional annotations; object boxes alone do not validate missing-PPE concerns or duplicate handling. Dataset selection and preparation belong to Phase 2 after approval.
