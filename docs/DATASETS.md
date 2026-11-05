# Dataset research — Phase 2.1

Research date: **2026-11-05**. Scope: dataset research and selection only. Read alongside [architecture](ARCHITECTURE.md), [evaluation](EVALUATION.md), and the [selection recommendation and preparation proposal](DATASET_SELECTION.md).

**Evidence convention:** “verified publication” means the statement was read in the cited primary-source documentation/configuration at a fixed Git revision. It does not mean the underlying dataset was independently counted, visually audited, or licensed for every intended downstream use. “Derived” denotes our calculation or interpretation; “unconfirmed” denotes information the inspected sources do not establish. No dataset archive, photographs, labels corpus, model weights, or training dependencies were downloaded. Only documentation, configuration, license text, and a published class-distribution chart were inspected.

The rendered Ultralytics documentation site was blocked by the environment's network policy. Its official Markdown source and YAML were retrieved from the Ultralytics GitHub repository instead and verified at the pinned revision below. The SH17 paper, Kaggle package, upstream Pexels terms, and dataset archives were not independently inspected; references to their contents are limited to what the repository publishes.

## Primary-source register

All sources below were retrieved on 2026-11-05. GitHub revision links preserve the researched version rather than relying on changing branch tips.

| ID | Primary source | Evidence used |
| --- | --- | --- |
| C1 | [Construction-PPE documentation source](https://github.com/ultralytics/ultralytics/blob/87ea3adb378621a2a260acd3296f4f84dd555197/docs/en/datasets/detect/construction-ppe.md) | Counts, provenance, class meanings, split, annotation method, dataset license and attribution. Published page: [Construction-PPE](https://docs.ultralytics.com/datasets/detect/construction-ppe/). |
| C2 | [Construction-PPE YAML](https://github.com/ultralytics/ultralytics/blob/87ea3adb378621a2a260acd3296f4f84dd555197/ultralytics/cfg/datasets/construction-ppe.yaml) | Exact zero-based class IDs, train/validation paths, declared counts, archive location; no test entry. |
| F1 | [Ultralytics detection format](https://github.com/ultralytics/ultralytics/blob/87ea3adb378621a2a260acd3296f4f84dd555197/docs/en/datasets/detect/index.md) | YOLO label text structure and normalized coordinates. |
| H1 | [SHWD README](https://github.com/njvisionpower/Safety-Helmet-Wearing-Dataset/blob/c952631dfc352e0defdd54b4785a9be6576451ad/README.md) | Image/instance counts, Google/Baidu and SCUT-HEAD provenance, two class meanings, Pascal VOC layout, split-name examples. |
| H2 | [SHWD repository LICENSE](https://github.com/njvisionpower/Safety-Helmet-Wearing-Dataset/blob/c952631dfc352e0defdd54b4785a9be6576451ad/LICENSE) | MIT grant for software and associated documentation; not a demonstrated rights audit of all source images. |
| S1 | [SH17 README](https://github.com/ahmadmughees/SH17dataset/blob/2f832c289f9deea063367045ed8230b26e3e7ea9/README.md) | Counts, industrial/Pexels provenance, classes, image sizes, benchmark evaluation size, CC BY-NC-SA 4.0 and responsible-use statements. |
| S2 | [SH17 YAML](https://github.com/ahmadmughees/SH17dataset/blob/2f832c289f9deea063367045ed8230b26e3e7ea9/sh17.yaml) | Actual class ID order; placeholder file paths and stale-looking 128-image comments. |
| S3 | [SH17 published class-distribution chart](https://github.com/ahmadmughees/SH17dataset/blob/2f832c289f9deea063367045ed8230b26e3e7ea9/extras/readme/data_distribution.svg) | Rounded instance shares, including helmet and vest scarcity. |
| U1 | [Ultralytics software LICENSE](https://github.com/ultralytics/ultralytics/blob/87ea3adb378621a2a260acd3296f4f84dd555197/LICENSE) | GNU AGPL version 3 text. |
| U2 | [Ultralytics README licensing section](https://github.com/ultralytics/ultralytics/blob/87ea3adb378621a2a260acd3296f4f84dd555197/README.md#-license) | AGPL-3.0 and Enterprise licensing options; software/model terms are separate from dataset terms. |

## Ultralytics Construction-PPE

### Verified publication findings (C1, C2, F1)

- **1,000 images**, **14,863 bounding boxes**, **12 classes**; created/open-sourced by the Ultralytics team in **November 2026**. Do not substitute figures from an older mirror or release without identifying that version.
- **800 training / 200 validation images (80/20)**. No separate test split is published in the inspected documentation/configuration. Paths are `images/train` and `images/val` relative to `construction-ppe`.
- Human-collected **and generated images**; expert human annotation and AI auto-annotation. The sources do not quantify the real/generated proportions or per-image annotation method.
- Construction sites, workshops, warehouses, loading areas, and maintenance settings; portrait, landscape, and square compositions with varied resolutions. No numerical resolution distribution or smartphone-camera provenance breakdown is given.
- Bounding boxes in **Ultralytics YOLO detection format**: one text label file per labeled image, one row per object, `class x_center y_center width height`, with zero-based classes and coordinates normalized to 0–1. These are boxes, not segmentation masks, worker identities, or temporal tracks.
- The publisher explicitly states **images and annotations are CC BY 4.0**. This differs from the AGPL header on the software configuration file; see licensing below.

| Source ID | Exact class | Published target |
| --- | --- | --- |
| 0 | `helmet` | Protective helmet or hard hat |
| 1 | `gloves` | Work gloves |
| 2 | `vest` | High-visibility safety vest, jacket, or shirt |
| 3 | `boots` | Protective work boots or work shoes |
| 4 | `goggles` | Protective eyewear |
| 5 | `Person` | Person |
| 6 | `no_helmet` | Visible head without a helmet |
| 7 | `no_goggle` | Visible eye region without protective eyewear |
| 8 | `no_gloves` | Visible hand without a glove |
| 9 | `no_boots` | Visible foot or footwear without protective work footwear |
| 10 | `forklift` | Forklift |
| 11 | `no_vest` | Visible torso without high-visibility safety clothing |

**Important semantics:** missing-equipment labels refer to visible body regions. An occluded/out-of-frame region does not establish missing PPE. `Person` is not an occupation classifier; `vest` includes jackets/shirts and is broader than a literal vest. Missing-equipment boxes are not necessarily full-person boxes or paired to person IDs.

### Limitations and unconfirmed information

The direct five-target coverage is the strongest match for VestCheck, but 1,000 images alone do not establish adequate generalization. Generated imagery may introduce shortcuts or unrealistic textures; the proportion, generator, and real-only evaluation coverage are unknown. Human plus AI annotation is a published process claim, not evidence of measured annotation accuracy.

Per-class train/validation counts, negative-label frequency, inter-annotator agreement, label exhaustiveness, head/torso visibility rules beyond the published descriptions, site-disjoint splitting, exact/near duplicates, and cross-dataset overlap have **not been verified**. No duplicate rate or class-balance result is claimed. No identity/association, correct-fit certification, or temporal event annotations are documented. The archive's embedded license, manifest, and stated counts must be checked in an approved Step 2.2 audit.

## Safety Helmet Wearing Dataset (SHWD)

### Verified publication findings (H1, H2)

- **7,581 images** with **9,044 helmet-wearing positive objects** and **111,514 normal-head negative objects**: **120,558 total objects** is a derived sum.
- Classes are `hat` (helmet-wearing positive object) and `person` (**normal/bare head**, not a full-person or worker box). It does not provide vest/no-vest classes or the full worker target.
- Images for positives were obtained from Google/Baidu; some negative objects come from SCUT-HEAD. Manual LabelImg annotations are published in **Pascal VOC** layout (`Annotations`, `ImageSets`, `JPEGImages`), requiring audited conversion before YOLO use.
- Examples reference `trainval` and `test` splits. Exact split image counts and a separate validation partition were not established from the README; no 80/20 ratio is assumed.
- A repository **MIT LICENSE** exists. It does not by itself demonstrate permission from all Google/Baidu image owners or resolve SCUT-HEAD's upstream conditions.

### Suitability and limitations

The published instance ratio is approximately **12.3 bare-head objects per helmet-wearing object** (derived from 111,514 / 9,044). That is an object-level imbalance, not an image-level rate. Crowded head scenes and web/SCUT-HEAD provenance can differ materially from a supervisor's moving phone camera. Full-worker detection, PPE ownership, vest concerns, temporal labels, and correct helmet fit are not supplied by the two-class taxonomy.

Potential role: a later, license-cleared helmet/head auxiliary source. Do not map `person` to VestCheck's worker class or merge head boxes directly with helmet-object boxes without defining a consistent box policy. Annotation completeness, duplicates, source overlap, and actual smartphone performance remain unaudited. It is not the primary recommendation.

## SH17

### Verified publication findings (S1, S2, S3)

- **8,099 annotated images**, **75,994 object instances**, **17 classes** from industrial/manufacturing environments. The README describes images sourced via Pexels, with sizes from **1920×1002 to 8192×5462** and **9.38 instances/image** on average.
- The project uses YOLO-format labels and publishes a class YAML. The README's displayed class list is **not the class ID order**; use S2 for IDs.
- S2 zero-based IDs: `0 person`, `1 ear`, `2 ear-mufs`, `3 face`, `4 face-guard`, `5 face-mask`, `6 foot`, `7 tool`, `8 glasses`, `9 gloves`, `10 helmet`, `11 hands`, `12 head`, `13 medical-suit`, `14 shoes`, `15 safety-suit`, `16 safety-vest`.
- The README's model table evaluates **1,620 images / 15,358 instances**, and it discusses `train_files.txt` / `test_files.txt` while calling evaluation a validation set. **6,479 remaining images** is only a derived 8,099 − 1,620 calculation, not an audited train count. S2 has placeholder paths and comments saying 128 images, so it is not evidence of actual split sizes. Inspect the released manifests before declaring an 80/20 split or an untouched test set.
- The published distribution chart gives approximately **18.2% person**, **15.8% head**, **1.2% helmet**, and **0.7% safety-vest** of instances. Hands dominate at **20.9%**. These are rounded publisher-chart values, not independently counted per-split annotations.
- The README reports **39,764 annotations smaller than 1%** of image area and **59,025 smaller than 5%**, across all classes. Do not assume those are helmet/vest-specific statistics.
- Dataset license is declared **CC BY-NC-SA 4.0**, with a request to cite Hafiz Mughees Ahmad and Afshin Rahimi, *SH17: A dataset for human safety and personal protective equipment detection in manufacturing industry*, 2024, [DOI](https://doi.org/10.1016/j.jnlssr.2024.09.002). The README also instructs users to follow Pexels terms; those upstream terms were not independently verified here.

### Suitability and limitations

SH17 supplies person, helmet and vest boxes, but **no explicit no-helmet/no-vest classes**. A `head` label does not mean “bare head”; missing equipment cannot be inferred from absent annotations. Full worker/PPE ownership, correct wearing, assessability, and temporal event labels remain unverified.

More images and a YOLO format are useful, but helmet/vest rarity, stock-photo/manufacturing bias, and downscaling of small objects are material concerns. A large source image does not guarantee usable hard-hat pixels after mobile-model resizing. Published small-model benchmarks demonstrate a research baseline, not smartphone latency, recall, or safe field performance. Noncommercial/share-alike restrictions make it a poor default for an application with an unresolved future commercial path. Do not silently combine it with Construction-PPE and call the combined dataset CC BY 4.0.

## Cross-candidate quality and bias assessment

| Issue | Verified evidence | Unknown / future audit |
| --- | --- | --- |
| Class imbalance | SHWD head/helmet counts; SH17 rounded chart shares. | Construction-PPE class counts; all per-split distributions and per-image negative coverage. |
| Annotation quality | Construction-PPE declares human and AI annotation; SHWD declares manual LabelImg; all describe boxes. | Missing labels, box consistency, PPE-to-person links, reviewer agreement, correct-wearing criteria. |
| Duplicates/leakage | No duplicate audit results were found in the inspected sources. | Exact hashes, perceptual clusters, same-site/sequence leakage, and overlap across candidates. Do not claim duplicate-free data. |
| Domain bias | Construction-PPE mixes real/generated industrial scenes; SHWD web/SCUT-HEAD; SH17 Pexels industrial/manufacturing imagery. | Real-phone motion blur, local sites/clothing, geographic/demographic coverage, weather and lighting representation. |
| Phone suitability | All have box annotations potentially usable by lightweight detectors after any required conversion. | Measured recall on small workers, export parity, latency/FPS, thermals and battery; dataset size/format cannot establish real-time readiness. |

## Dataset licensing versus software licensing

- **Construction-PPE data:** C1 explicitly licenses images/annotations under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The publisher states sharing/adaptation including commercial use with attribution. Preserve creator credit, dataset/source and license links, and notices; indicate filtering, remapping, annotation corrections or other changes. Suggested publisher credit: “Ultralytics Construction-PPE Dataset, Ultralytics team, November 2026, CC BY 4.0.” Verify the actual release's notices in Step 2.2. Attribution is not a worker consent/model release or a guarantee of upstream rights.
- **SHWD data:** H2's MIT notice is verified for the repository's software/documentation. The inspected sources do not establish blanket rights for externally sourced photographs. Preserve the notice for covered code, investigate upstream rights separately, and do not label the entire image corpus “commercially cleared.”
- **SH17 data:** S1 declares [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) and additional Pexels-source considerations. Preserve attribution/citation, license link and change notices; resolve noncommercial use and share-alike obligations for any planned use or adapted-data release. Free access or a public portfolio does not automatically resolve all permissions. Obtain appropriate permission before incompatible/commercial use; do not infer a definitive trained-weight license from the dataset declaration alone.
- **Ultralytics software and model artifacts:** U1 verifies **AGPL-3.0** for the software; U2 advertises **Enterprise** terms as an alternative to its open-source requirements. CC BY 4.0 data does not relicense training/export software, pretrained weights, plugins, or the mobile app. Assess exact software, pretrained/fine-tuned weights, exporters and distribution/hosting use separately. AGPL permits commercial use subject to its conditions; it is not merely a “noncommercial” license. Source/distribution obligations and modified network-service requirements can matter; exporting to Core ML/TFLite does not automatically remove obligations. Resolve whether the intended app release can meet applicable terms or needs a separate agreement before distributing artifacts. No blanket legal clearance is claimed by this research.

**Recommendation:** select Construction-PPE as the **conditional primary training candidate**, subject to release/license and annotation audits. The [selection document](DATASET_SELECTION.md) gives the comparison, exact proposed class mapping, independent smartphone test strategy, and Step 2.2 approval gates. Research completion does not authorize dataset preparation or training.
