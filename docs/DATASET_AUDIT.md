# Construction-PPE acquisition and quality audit — Phase 2.2A

Audit date: **2026-11-05**. Status: **downloaded and inspected; human review required before transformation or split changes**. Counts below are from the actual archive, not copied from publisher estimates. No training, complete class conversion, split changes, final test split, camera development, inference or RAG was performed.

## Acquisition, version and rights

- Official configuration: [pinned Ultralytics YAML](https://github.com/ultralytics/ultralytics/blob/1bbe9baf26965b46009401db8895d565d73d19ea/ultralytics/cfg/datasets/construction-ppe.yaml).
- Official provenance/license description: [pinned documentation source](https://github.com/ultralytics/ultralytics/blob/1bbe9baf26965b46009401db8895d565d73d19ea/docs/en/datasets/detect/construction-ppe.md). The official GitHub Markdown was used because the rendered documentation host is not in the environment allowlist.
- Verified archive URL from that configuration: `https://github.com/ultralytics/assets/releases/download/v0.0.0/construction-ppe.zip`.
- Version description: **Ultralytics Construction-PPE, November 2026**, as declared by the downloaded README. The `v0.0.0` asset URL is mutable; the SHA-256 below identifies the exact downloaded bytes.
- Download completed **2026-11-05 at 18:45:58 UTC (1:45:58 PM America/New_York)**. Archive size: **647,666,037 bytes**.
- Archive SHA-256: `e5817aa9c73f33e525d76ca6bc6af4e4eac9dcea9bcfef1cfd1a71c09fbc1232`.
- Downloaded README explicitly licenses **images and annotations under CC BY 4.0**; embedded `LICENSE.txt` contains the Creative Commons Attribution 4.0 International license. This confirms release notices, not independent upstream rights or subject consent. Credit: **Ultralytics Construction-PPE Dataset, Ultralytics team, November 2026, CC BY 4.0**; retain dataset/license links and indicate future adaptations. No adapted dataset is distributed in this branch.
- Ultralytics software/model/export licensing remains a separate issue: dataset CC BY 4.0 does not replace applicable AGPL/Enterprise or pretrained-weight terms. See [dataset/software license analysis](DATASETS.md).

HTTPS verification and ZIP CRC checks were retained. No publisher-signed archive checksum was available in the inspected configuration; the recorded checksum is our observed content identifier, not a signature or independent publisher attestation. The acquisition tool now refuses an archive whose digest differs from this audited release.

## Preservation and evidence locations

Original ZIP, source documents, acquisition metadata, and extracted originals are in the **Git-ignored** `model/data/audit-2026-11-05/` workspace. Original files are under `original/construction-ppe/`. The original split and labels were not modified. All **2,004 extracted file hashes** still match the acquisition baseline; the audit also compared full original file hashes before and after its read-only run.

Only the two aggregate audit/preparation documents, source tools, tests, requirements and usage guidance are committed. No raw images, source label corpus, archive, generated image montage or detailed per-file report is committed.

Local evidence:

- `acquisition.json`: source URLs/revision, UTC timestamps, byte length, configuration/documentation/archive hashes, acquisition outcome.
- `original-manifest.json`: acquisition baseline content hashes for every extracted file.
- `results/audit.json` and `results/audit.md`: automated counts, local per-file issues, duplicate pairs, mapping checks and limitations. The final automated run was **2026-11-05T18:51:23.813729+00:00**. Manual review and baseline comparison described below followed that run.

Embedded metadata SHA-256 values:

| File | SHA-256 |
| --- | --- |
| data.yaml | `d099873f1abf4b9862870b0b1305d01cd203914b1afb2c8bb217563af52488c3` |
| LICENSE.txt | `9ba9550ad48438d0836ddab3da480b3b69ffa0aac7b7878b5a0039e7ab429411` |
| manifest.jsonl | `1d9dd88a8699c236c993a4291cb29f8918228ce61af5b0651e0ac3864cbd3474` |

## Verified inventory

| Metric | Training | Validation | Total |
| --- | ---: | ---: | ---: |
| Fully decoded images | 800 | 200 | 1,000 |
| Label text files | 800 | 200 | 1,000 |
| Nonempty annotation rows | 11,902 | 2,961 | 14,863 |
| Rows passing strict syntax/class/geometry checks | 11,825 | 2,944 | 14,769 |
| Strict box-boundary flags | 77 | 17 | 94 |
| Missing label files | 0 | 0 | 0 |
| Orphan labels / missing paired images | 0 | 0 | 0 |
| Corrupt or unsupported images | 0 | 0 | 0 |
| Unreadable labels | 0 | 0 | 0 |
| Empty label files | 0 | 0 | 0 |
| Ambiguous image stems | 0 | 0 | 0 |

There were no malformed annotation rows, unknown class IDs, non-finite coordinates, zero/negative box sizes, or duplicate annotation rows. All 94 rejected rows were corner-boundary excursions, explained below. The archive contains four metadata files: `README.md`, `LICENSE.txt`, `data.yaml`, `manifest.jsonl`; there were no unrecognized files in the image directories. No test split was supplied or created.

The publisher manifest has **1,000 entries**. Every image is represented once; file SHA-256 and annotation-row counts match all entries. Width/height fields are supplied for **707 entries** and match the decoded images for those entries. No missing images, extra images, duplicate manifest entries, malformed manifest rows, hash mismatches, annotation-count mismatches or supplied-dimension mismatches were observed.

## Actual class distribution

**Source rows** count all paired annotations with recognized class IDs, including the 94 strict boundary flags; these sum to 14,863. The last column excludes the flags and sums to 14,769. No rows were deleted or rewritten. Counts are object instances, not independent scenes or worker-level rates.

| Source class | Train source rows | Validation source rows | Total source rows | Strictly valid rows |
| --- | ---: | ---: | ---: | ---: |
| 0: helmet | 1282 | 294 | 1576 | 1573 |
| 1: gloves | 1548 | 381 | 1929 | 1927 |
| 2: vest | 1476 | 340 | 1816 | 1812 |
| 3: boots | 2003 | 481 | 2484 | 2474 |
| 4: goggles | 612 | 139 | 751 | 750 |
| 5: Person | 1962 | 481 | 2443 | 2383 |
| 6: no_helmet | 634 | 179 | 813 | 812 |
| 7: no_goggle | 265 | 82 | 347 | 347 |
| 8: no_gloves | 839 | 203 | 1042 | 1042 |
| 9: no_boots | 569 | 178 | 747 | 746 |
| 10: forklift | 275 | 73 | 348 | 337 |
| 11: no_vest | 437 | 130 | 567 | 566 |

The five proposed targets account for **7,215 source rows** (**7,146 strictly valid rows**). `no_vest` has 567 source rows versus 1,816 vest and 2,443 person rows; `no_helmet` has 813 versus 1,576 helmet rows. These counts reveal unequal label support, but cannot be interpreted as per-worker PPE prevalence without ownership/visibility annotations. No resampling or class balancing has been performed.

## Box validity and annotation quality

The audit requires exactly five fields, a known integer class, finite center/dimensions in the normalized range, positive width/height and in-frame corners with a `1e-6` numerical tolerance. It found **94 rows in 87 label files** whose corner extends approximately **0.000005** beyond an image edge; the maximum measured excursion was `5.000000000032756e-06`. All are within the separately reported `1e-5` rounding-candidate band. **Zero other invalid-box rows** were found. These are consistent with coordinate rounding; that explanation is an interpretation, not confirmed authoring history. They are not evidence that 94 objects are badly localized.

The strict CLI intentionally exits **2** and writes the report rather than silently clipping coordinates or declaring a clean quality pass. A future tolerance/clipping decision must be reviewed, documented and applied only to a derived copy, if approved.

No opposing helmet/no-helmet or vest/no-vest boxes reached the audit's IoU ≥0.5 conflict-screen threshold. This does **not** establish absence of semantic conflicts: positive and negative regions have different extents, and there are no verified worker-to-PPE association IDs or assessability fields. The README's statement that annotations were reviewed/corrected is a publisher claim; this automated audit cannot certify annotation completeness.

## Exact duplicates, near-duplicates and scene overlap

- **0 exact file SHA-256 duplicate groups** and **0 identical decoded RGB pixel groups**, including **0 exact train/validation duplicate groups**.
- **2 near-duplicate candidate pairs**, comprising one train/train pair and **one train/validation pair**, under horizontal 64-bit dHash distance ≤4 and relative aspect-ratio difference ≤5%. Exact file/pixel matches are excluded from this count.
- The three unique candidate images were opened and visually reviewed. They share the same gate/entrance construction background and camera viewpoint. The train/train pair has nearly identical pose/background with different visible PPE appearance; this suggests related/edited content but does not verify the editing method. The validation example has different foreground appearance in that same setting. This is **observed shared-scene leakage risk**, even though the files/pixels are distinct. No worker identity is inferred.

Local review references, using only the public source's opaque filenames:

| Pair | References | dHash distance | Review outcome |
| --- | --- | ---: | --- |
| Train/train | `source-3978abe9cfed5d8a5faa5a98dfe4b00a.jpg` ↔ `source-efc23273c04e007083114c0f217335f0.jpg` | 2 | Related scene/pose and different PPE appearance; treat as a scene group pending human adjudication. |
| Train/validation | `source-3978abe9cfed5d8a5faa5a98dfe4b00a.jpg` ↔ `source-9e10b0409f922546c35b276eb5a5756e.jpg` | 4 | Same background/viewpoint observed across splits; review scene-group membership before evaluation. |

These two candidate pairs are a method-specific result, not an exhaustive count of related images. Different crops, large edits, rotations or changed foregrounds can evade dHash; unrelated images can also collide. The pair formed by the two remaining reviewed images need not pass the threshold to belong to the same scene group. No deletion, deduplication, relabeling or split reassignment was performed. **Do not claim independent validation based solely on zero exact duplicates.**

## Real versus generated imagery

The downloaded README confirms a mix of human-collected/generated images and expert-human/AI auto-annotation. The manifest contains only file/split/hash/annotation-count and optional dimensions, **no real/generated or generator/source provenance flag**. There are **293 `source-` filenames** and **707 `ultralytics-ppe-nov2026-` filenames**, but these are naming observations, not verified real/generated counts. Dimensions being supplied for 707 entries likewise does not establish origin. The visually related PPE variations above warrant provenance review but do not identify a generation method. The actual proportion of generated or edited imagery remains unresolved.

## Mapping and missing-PPE limitations

The archive's actual `data.yaml` matches all 12 official source IDs/names, including the five required mappings:

| Proposed target ID | Target | Verified source ID / name |
| --- | --- | --- |
| 0 | worker | 5 / Person |
| 1 | hard_hat | 0 / helmet |
| 2 | safety_vest | 2 / vest |
| 3 | visible_missing_hard_hat | 6 / no_helmet |
| 4 | visible_missing_safety_vest | 11 / no_vest |

This verifies schema compatibility, not semantic completeness or correctness. `Person` is a person box rather than proof of occupation; `vest` includes high-visibility shirts/jackets. Missing-PPE labels refer to visible head/torso regions; no-detection and occlusion do not establish missing PPE. Object boxes do not certify correct fit, ownership, required PPE, or OSHA compliance. Human review and explicit uncertainty remain required. Only three hash-selected images and their labels were spot-reviewed; no representative full-dataset semantic annotation audit has been completed.

## Reproduction and validation

See [audit tool usage](../model/AUDIT_TOOLS.md). Tools use Python 3.12.14, Pillow 13.0.0 and PyYAML 6.0.3; those audit-only dependencies were already available. No training packages were installed.

- Synthetic unit tests cover row validation, tiny rounding excursions, image/label pairing, unreadable/corrupt files, source versus valid class counts, duplicate/overlap detection, manifest verification, YAML/layout mismatch, ZIP traversal/symlink rejection, acquisition URL mismatch and existing-workspace preservation.
- The real archive was acquired with HTTPS/CRC verification, fully decoded, audited and compared against the original acquisition manifest.
- The strict audit outcome is **review required (exit 2)** because of the 94 tiny boundary flags; this is distinct from test failures or an acquisition failure.
- Documentation links, Git exclusions, staged whitespace and tracked-file scope are checked before committing. Raw data and detailed local reports remain ignored.

## Suitability for the next preparation step

**Conditionally suitable for reviewed preparation, not approved for training or final evaluation.** Actual label coverage and readable file/metadata integrity support investigating the five-class derivative. Before any transformation, approve handling of tiny rounding flags, adjudicate the observed cross-split scene overlap and broader grouping, review annotation completeness/ownership/uncertainty, and seek more precise real/generated provenance. Keep the publisher split untouched until that review. No final test split or model suitability claim follows from this audit alone.

See [the proposed preparation plan](DATA_PREPARATION_PLAN.md) for explicit review gates.
