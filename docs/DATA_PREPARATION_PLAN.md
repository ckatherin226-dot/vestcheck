# Data preparation plan after Phase 2.2A

Status: proposal for review. Phase 2.2A acquired and audited the original Construction-PPE dataset; it did **not** convert the full dataset, change the publisher split, create a test split, train a model, or implement mobile/inference/RAG features. See [actual audit evidence](DATASET_AUDIT.md), [selection](DATASET_SELECTION.md), [evaluation](EVALUATION.md), and [architecture](ARCHITECTURE.md).

## Review gates before transformation

1. Review the downloaded release's provenance, embedded CC BY 4.0 notice, checksums and class inventory. The archive URL uses a shared `v0.0.0` release and is not an immutable content address; require the recorded archive SHA-256 before reusing this audit. Keep dataset and software/weights licensing separate.
2. Review the 94 strict boundary flags. All are approximately 0.000005 beyond an image edge, consistent with coordinate rounding, not proof of a badly localized object. Agree on an explicit tolerance or a documented clipping policy for a **derived copy**; never change originals or silently discard all flagged rows.
3. Review the two dHash candidate pairs and the visually observed train/validation shared-scene cluster. Expand scene/sequence grouping beyond the flagged pairs because perceptual hashing is not an exhaustive scene detector. Do not treat “zero exact duplicates” as proof of no leakage.
4. Approve a scene-group membership and future split policy before moving any data. Keep related originals/edited variants and the same scene/sequence together. Document deviations from the publisher split and recheck class coverage. Do not create a final test split during this task.
5. Approve a human annotation-review rubric covering visibility, PPE ownership, ambiguous cases, incomplete labels, class definitions and positive/negative conflicts. Automated valid boxes and publisher claims of review do not establish semantic completeness.

## Proposed five-class transformation — not executed

The downloaded `data.yaml` was checked against the official configuration and matches all 12 names/IDs. Proposed mapping:

| Target ID | Target name | Original ID / name |
| --- | --- | --- |
| 0 | worker | 5 / Person |
| 1 | hard_hat | 0 / helmet |
| 2 | safety_vest | 2 / vest |
| 3 | visible_missing_hard_hat | 6 / no_helmet |
| 4 | visible_missing_safety_vest | 11 / no_vest |

Preserve source annotations, archive and manifests read-only in practice: audit scripts never write into originals. Future preparation should create a separate ignored derived directory, retain the original-to-derived path and ID mapping, and log every filtered, corrected, clipped, or reassigned item. Do not overwrite source labels. Filter annotations for out-of-scope classes only after verifying target-label completeness; retain legitimate background images. Do not treat an absent label as proof of missing PPE.

`worker` means a person in the worksite scene, not an occupational classifier. Source `vest` includes high-visibility jackets/shirts; the target label must preserve that broader meaning. Source missing-PPE labels describe a visible bare head or torso without high-visibility clothing, not worker-wide compliance. A nearby helmet or vest may be carried or belong to another person. Unassessable/occluded body regions and uncertain ownership require explicit uncertainty and human verification; they cannot be automatically made negative training labels.

## Further annotation and provenance review

- Review examples stratified by all five targets, source filename families, split, small objects, occlusion, lighting and distance. Have a second reviewer adjudicate a subset and record disagreements. The three-image visual review in this audit is not a full-dataset semantic validation.
- Inspect all flagged row locations and candidate scene clusters using the local JSON report; review additional related scenes and possible edited counterparts, even when dHash differs by more than four bits.
- The embedded manifest has no per-image real/generated field. Filename prefixes and visual appearance alone must not be used as verified generation labels. Seek authoritative per-image provenance if a real-only evaluation partition is required; record unknown origin honestly.
- Record per-class and per-image coverage after any approved transformations. Avoid balancing decisions solely from instance counts: many correlated examples or small boxes can overstate usable support. Pay particular attention to the lower frequency of `no_vest` and missed concerns.
- Do not merge SHWD/SH17 without separate rights, box-semantics, completeness, and cross-source duplication review.

## Independent evaluation and future acceptance

Maintain a separate, authorized smartphone test collection as proposed in [DATASET_SELECTION.md](DATASET_SELECTION.md). Obtain permissions and appropriate consent; do not ask workers to remove required PPE in unsafe situations. Keep images and sensitive annotations outside Git. Separate sites/sessions from any future tuning set. Freeze test membership only after duplication/scene-overlap review and an agreed sample/annotation protocol.

Training and real-device export/performance tests require later approval and the appropriate phase. Geometry counts alone do not establish recall, accuracy, mobile latency or safe field performance. Do not claim production suitability, compliance certification, or safe-site determination.

## Reproducible handoff

After this audit is reviewed and the next preparation scope is authorized, implement transformations with synthetic tests, preserve immutable originals, regenerate class and integrity statistics, and document all scene grouping/split changes. The current task authorizes no such transformations or training.
