# Five-class dataset preparation — Phase 2.2B

Date: **2026-11-05**. Result: **five-class staging derivative built and verified; not yet cleared for Phase 2.3 training**. This phase implements the authorized label preparation and visual investigation; it does not train YOLO, implement inference/mobile/RAG, move originals or create a test split.

## Prepared data and verified counts

The source is the exact November 2026 Construction-PPE archive audited in [DATASET_AUDIT.md](DATASET_AUDIT.md), SHA-256 `e5817aa9c73f33e525d76ca6bc6af4e4eac9dcea9bcfef1cfd1a71c09fbc1232`. The acquisition baseline was verified before/after preparation. All **2,004 original files remain unchanged**. All **1,000 copied images are byte-identical** to their source images and use independent copies, not hard links. Original labels were not overwritten.

The local derivative is `model/data/preparation-2026-11-05/five-class-staging/`, beneath the existing Git-ignored `model/data/` path. It contains **800 train / 200 validation images**, matching labels, and **7,215 valid five-class annotation rows**. Membership is the publisher's original split; this is explicitly a staging split, not an independently validated evaluation split.

| Target ID / name | Source ID / name | Train | Validation | Total |
| --- | --- | ---: | ---: | ---: |
| 0 worker | 5 Person | 1,962 | 481 | 2,443 |
| 1 hard_hat | 0 helmet | 1,282 | 294 | 1,576 |
| 2 safety_vest | 2 vest | 1,476 | 340 | 1,816 |
| 3 visible_missing_hard_hat | 6 no_helmet | 634 | 179 | 813 |
| 4 visible_missing_safety_vest | 11 no_vest | 437 | 130 | 567 |
| **Total** | | **5,791** | **1,424** | **7,215** |

From 14,863 source rows, **7,648 out-of-scope rows were excluded**, not relabeled as missing PPE. **Eight train images** contain no retained targets and remain as empty-label background images; all images were retained. No resampling, augmentation or synthetic image generation was performed.

## Review and correction of the 94 boundary flags

The Phase 2.2A flags were checked numerically against the original labels and acquisition baseline: all are tiny corner excursions of approximately `0.000005`, within a maximum permitted rounding excursion of **0.00001 normalized units**. This does not establish whether a box is semantically correct; it is a numerical eligibility check for a minimal geometric correction.

For each retained target box, use exact decimal input, convert center/width/height to corners, intersect only out-of-frame edges with `[0,1]`, and recalculate center/size. Unchanged coordinate strings remain unchanged. Corrected coordinates are serialized to at most 12 decimal places and validated again. A nonfinite/invalid dimension, malformed/unknown-class row or larger excursion fails preparation rather than being silently fixed or dropped. This clips an overhanging edge; it does not shift a whole box or invent new object extent.

- **69 retained rows corrected:** 60 person, 3 helmet, 4 vest, 1 no_helmet, 1 no_vest.
- **25 flagged rows belong to excluded classes** and produce no derived annotation. Their classification and drop action are logged; no source coordinates are edited.
- No retained target rows were discarded. Independent rereading found **zero invalid derived rows** under the existing strict `1e-6` corner tolerance.

Example from a source person row: `5 0.402330 0.574780 0.288170 0.850450` becomes target row `0 0.40233 0.5747775 0.28817 0.850445`. The bottom edge becomes exactly 1; the top edge and horizontal edges retain their values.

## Visual review and scene investigation

See [annotation-review evidence](ANNOTATION_REVIEW.md), [split policy](SPLIT_POLICY.md) and the committed [review record](../model/reviews/phase_2_2b_review.json). The record contains non-sensitive public filenames, source hashes, selection criteria, observed notes, candidate decisions and a five-image confirmed background group; it contains no images or label corpus.

Actual visual work comprised **20 unique stratified annotation images**, annotated overviews and enlarged context crops for the ten `source-` examples, plus **30 scene-search candidate images and 12 additional gate-seed neighbors**. These were inspected by the assistant using image-viewing tools; this is not an independent human expert validation or a full-dataset semantic review.

The expanded search inspected all 1,000 images with reproducible whole/border hashes, yielding **21 candidate pairs / 3 cross-split candidates**. Visual adjudication linked **two additional images** to the original gate scene: a confirmed group of **five images (four train, one validation)**. The other cross-split candidate was a warehouse/scaffold false match. Additional shared source/site relationships remain unresolved; hashes do not certify independence.

## Preserved staging membership and readiness

**Zero split changes were applied.** Every transformation-manifest record retains source and derived split and the explicit staging rationale. The user requested a proposed leakage-resistant policy; known groups and all proposed future reassignments/quarantines are documented for review instead of silently selecting new validation membership.

`preparation.json` records `training_ready: false`. The generated configuration is named **`data.staging.yaml`** and carries a warning; the filename/flag are advisory, not an enforcement mechanism in third-party YOLO tools. Do not train from it until the documented gates are resolved and training is approved. The proposed next policy is atomic scene grouping, quarantine of unresolved cross-split groups, and a reviewed deterministic group-level split. No final test split was created.

## Manifest, provenance and attribution

The ignored `transformation.jsonl` records every image/label source and destination, hashes, unchanged split and rationale, and every row's original line, source/target classes, action and corrected derived value when retained. `preparation.json` records baseline/YAML/review-record hashes, class counts, drops, corrections, split policy and readiness. Manifest SHA-256 for the recorded run: `4f8110cf5593ab6f4d898bc088e6139d295a2ff8d55ef3037518780faef1a60f`.

The derivative retains source README/license copies and an adaptation notice crediting **Ultralytics Construction-PPE Dataset, Ultralytics team, November 2026, CC BY 4.0**, with dataset/license URLs and a description of class selection/remapping and clipping. No dataset redistribution occurs in this branch. Dataset license notices do not establish third-party consent, image provenance, or software/pretrained-weight licensing. Real/generated proportions and per-image provenance remain unresolved. See [licensing analysis](DATASETS.md).

## Reproduce without training

From the repository root, use the existing audit-only dependencies in `model/requirements-audit.txt`. If originals are absent, first follow [acquisition instructions](../model/AUDIT_TOOLS.md); the pinned archive digest must match.

```bash
python model/review_dataset.py \
  --root model/data/audit-2026-11-05/original/construction-ppe \
  --output model/data/preparation-2026-11-05/review

python model/prepare_dataset.py \
  --root model/data/audit-2026-11-05/original/construction-ppe \
  --baseline model/data/audit-2026-11-05/original-manifest.json \
  --review-record model/reviews/phase_2_2b_review.json \
  --output model/data/preparation-2026-11-05/five-class-staging

python model/prepare_dataset.py \
  --verify model/data/preparation-2026-11-05/five-class-staging

python -m unittest discover -s tests -p 'test_dataset*.py' -v
```

Use a fresh derivative output path for another build; existing outputs are never overwritten. Scene features may be reused only when source image hashes match the cache. Review diagnostics do **not** automatically author the committed review notes: a reviewer must actually inspect them and record conclusions. Preparation checks source hashes referenced by that record. It never interprets review text as an instruction to relocate data.

Preparation is atomic: failures discard temporary work instead of leaving a complete-looking dataset. Output inside the repository must be Git-ignored and outside originals. Independent verification rehashes every derived image/label, rereads labels, validates five-class geometry and counts, checks inventory against the transformation manifest, and confirms unchanged membership. It does not establish annotation correctness or scene-disjointness.

## Validation and next gate

**33 synthetic tests passed**, including the existing 18 audit tests and 15 preparation/review tests. Coverage includes exact clipping, all five mappings, rejected gross errors, background retention, immutable source checks, independent copies, atomic failure/overwrite protection, tamper detection, deterministic manifests and stratified sampling, and scene-candidate false-positive limitations. The real derivative independently verifies **1,000 images / 7,215 annotations / zero invalid rows** with matching content hashes. No training packages were installed or model behavior tested.

**Not ready for Phase 2.3 training yet.** Before training: review/apply the group-level split policy, adjudicate ambiguous negative-PPE labels and missing/occluded relations, expand expert annotation/provenance review as needed, settle intended software/weights distribution licensing, and approve the experiment/evaluation protocol. Preparation mechanics are verified; those remaining decisions must not be replaced by a claim of production accuracy or safety compliance.
