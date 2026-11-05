# Leakage-resistant split policy — proposed, not applied

Phase 2.2B preserved publisher membership in the five-class **staging** copy: 800 train / 200 validation images and zero moves. Source files and split membership remain unchanged. This document proposes the policy needed before training/evaluation. A passed geometry check does not make that staging validation split independent.

## Actual investigation

All 1,000 source images were searched using:

- Whole-frame horizontal 64-bit dHash distance ≤12; **or** four 64-bit border hashes combined (≤32/256 bits), with 2×2 RGB color mean absolute difference ≤25.
- Relative aspect-ratio difference ≤10% for candidate pairs.
- All-pairs comparison with recorded distances, followed by visual inspection. Unlike Phase 2.2A's ≤4-bit screen, this broader screen deliberately admits more false positives.
- Twelve additional, previously unqueued neighbors ranked against the three audited gate seeds by minimum `whole_distance/64 + border_distance/256`, with no acceptance threshold. This is a bounded retrieval review, not a claim of exhaustive site discovery.

Results: **21 candidate pairs, 3 cross-split pairs, 30 unique candidate endpoints**, plus **12 seed-neighbor images**. All 42 were opened in diagnostic pages. Feature caches, scores and diagnostic images remain ignored; decisions and public source references are in [the review record](../model/reviews/phase_2_2b_review.json).

Two cross-split pairs connect members of the already known gate scene; the third (warehouse aisle versus exterior scaffold) was visually rejected as same-scene evidence. Two more gate images were linked by visual background review rather than automatic connected components. Common work poses, doorways and industrial equipment generated candidate matches without establishing shared scene/source. Suspected relationships remain marked unresolved.

## Confirmed gate scene group

Group ID: `gate-entrance-01`. Evidence is matching gate structure, red barrier, ground and background layout, not faces or worker identity.

| Original split | Public source filename | Relationship |
| --- | --- | --- |
| train | source-3978abe9cfed5d8a5faa5a98dfe4b00a.jpg | Audited seed |
| train | source-efc23273c04e007083114c0f217335f0.jpg | Audited related appearance/scene |
| val | source-9e10b0409f922546c35b276eb5a5756e.jpg | Audited cross-split background |
| train | source-40471b5afe759eb420a90db737aa9a93.jpg | Newly linked gate view, foreground closer to camera |
| train | source-9ec80cefaef867295b0c9b5b6c7757c8.jpg | Newly linked gate view, similar framing to preceding image |

The membership is a confirmed minimum, not a complete source-site inventory. Two other validation doorway images (`source-00f1fbfd9c8193a3c5a071512cf8c0a7.jpg` and `source-8497dd5065ce426e2d223085b4a773a0.jpg`) remain a possible source/site relation; differences in viewpoint/background prevent a confirmed merge from this review.

## Proposed policy and explicit rationale

1. Build a reviewed group ledger using authoritative site/source/sequence provenance when available and manually confirmed background/edited-variant links otherwise. Group by scene/sequence, not worker identity or filenames alone. Record evidence and uncertainty.
2. Keep each confirmed scene, near-duplicate, sequence or edited-original family wholly in **one partition**. Do not split neighboring frames or edited variants independently. Do not automatically merge every hash candidate: false matches were observed.
3. Quarantine unresolved cross-split scene families from **both** training and validation until adjudicated. As a first proposed quarantine, removing the five confirmed gate-group members from the active staging lists would leave **796 train / 199 validation images**; this is **not applied**. Review all additional possible family links before treating those numbers as a finalized split.
4. Once group membership is reviewed, either retain unaffected publisher groups with explicit quarantines or approve a fresh deterministic group-level assignment targeting roughly 80/20. For the latter, record a seed and compare SHA-256 of `seed + group_id` with a fixed validation threshold. Exact image ratios need not equal 80/20 when groups are indivisible. Check class support before accepting the assignment; record any group-level balancing adjustments and rationale instead of silently moving individual images.
5. Publish only the non-sensitive policy/aggregate statistics to Git; keep full source/derived path membership and hashes in an ignored split manifest. Record each old split, proposed/applied split or quarantine status, group ID and rationale. Re-audit cross-partition hashes, groups, class/visibility support and source domains after any approved changes.
6. Use validation for model/threshold development. Keep a separately authorized smartphone collection independent of all future training and tuning sites. Do not create a final test split as part of this task or call a validation set an untouched test set.

No classifier, embedding model or source-site ground truth was available for this search. Hashes can miss crops, viewpoint changes and generated-series correlations. Visual review of 42 retrieved images is not a full 1,000-image site audit. No split-quality clearance is claimed for unreviewed images, and per-image real/generated provenance remains unknown.
