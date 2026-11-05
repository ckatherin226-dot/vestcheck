# Dataset selection — Phase 2.1

Decision date: **2026-11-05**. Status: **research recommendation for review; Step 2.2 is not authorized**. Primary-source citations, fixed revisions, publisher figures and evidence limitations are in [DATASETS.md](DATASETS.md). Architecture and evaluation remain governed by [ARCHITECTURE.md](ARCHITECTURE.md) and [EVALUATION.md](EVALUATION.md).

## Recommendation and comparison

Recommend **Ultralytics Construction-PPE as the primary candidate for a five-class VestCheck training subset**, conditional on the Step 2.2 audits below. It is the only inspected candidate whose published taxonomy directly covers person, hard hat, high-visibility clothing, visible bare head, and visible torso without high-visibility clothing. Its published CC BY 4.0 images/annotations grant and ready YOLO box format reduce licensing and conversion uncertainty compared with the alternatives. These advantages do not establish adequate model accuracy or field safety.

| Criterion | Construction-PPE | SHWD | SH17 |
| --- | --- | --- | --- |
| Published size | 1,000 images; 14,863 boxes | 7,581 images; 9,044 helmet-wearing + 111,514 bare-head objects | 8,099 images; 75,994 instances |
| Label coverage | All five proposed targets, plus seven out-of-scope classes | Helmet-wearing and bare heads only; misleading `person` class is a head | Person/helmet/vest and body parts; no explicit missing-PPE classes |
| Format / split | YOLO boxes; 800 train / 200 validation; no separate test | Pascal VOC; `trainval`/`test` example, sizes unconfirmed | YOLO; README benchmark uses 1,620 evaluation images; full split manifests unverified |
| Published data rights | CC BY 4.0 for images/annotations | MIT repository license; upstream image rights unresolved | CC BY-NC-SA 4.0 plus Pexels-source considerations |
| Primary strengths | Closest target semantics; explicit visible negative regions; construction setting | More helmet/head examples; useful potential auxiliary source | More images, person/PPE/body parts; published small-model baselines |
| Main weaknesses | Small, includes generated imagery; class balance and label quality unaudited | No vests or full workers; strong head/helmet imbalance; box/rights mismatch | Rare helmet/vest instances; industrial stock-photo bias; no explicit negative classes; licensing restrictions |
| Lightweight mobile YOLO suitability | Best starting candidate after audit; no measured mobile performance | Needs conversion and semantic harmonization; cannot cover MVP alone | YOLO-ready but rarity, small objects and five-target gaps remain; not a ready substitute |
| Proposed role | Conditional primary | Defer; possible license-cleared helmet/head supplement | Defer; possible permitted research comparison, not default mixed training data |

Five classes limit the target taxonomy and annotation scope; they do **not** guarantee smaller/faster inference. Model variant, input resolution, export/runtime support, device tests, and domain coverage remain decisive. Do not adopt the publisher's training model or epochs automatically. No model or plugin is selected by this dataset decision.

If Construction-PPE's archive, real-image coverage, label quality or rights cannot pass review, stop and revisit selection. Neither SHWD nor SH17 is an equivalent five-class fallback; a replacement may require additional licensed data and annotations. Do not compensate by silently treating all unannotated people as missing PPE.

## Proposed VestCheck class mapping

This is a **design proposal only**. No labels or training YAML have been generated. Source IDs must come from the pinned Construction-PPE YAML (C2), not alphabetical ordering or another dataset version.

| Proposed target ID | VestCheck label | Construction-PPE source ID / label | Meaning and guardrail |
| --- | --- | --- | --- |
| 0 | `worker` | 5 / `Person` | Person box used as a worksite subject proxy; not evidence of construction occupation or employee identity. |
| 1 | `hard_hat` | 0 / `helmet` | Visible helmet/hard-hat object; presence alone does not prove correct fit or association to a particular worker. |
| 2 | `safety_vest` | 2 / `vest` | Preserve source meaning: high-visibility vest, jacket **or shirt**. UI/documentation must not imply only literal vests or certified garment quality. |
| 3 | `visible_missing_hard_hat` | 6 / `no_helmet` | Visible bare-head region; candidate concern, not a full-worker box or a violation certification. |
| 4 | `visible_missing_safety_vest` | 11 / `no_vest` | Visible torso without high-visibility clothing; candidate concern, not a determination of required PPE for that location. |

Propose excluding source classes 1, 3, 4, 7, 8, 9, and 10 from the target taxonomy after auditing label completeness. Keep legitimate background/no-target images; an image containing only out-of-scope classes must not automatically be dropped. If target objects are present but unlabeled, correct/review them rather than turning the image into a false negative. Preserve source IDs/version and all transformations in a manifest.

**Alternative-source mappings require separate review:** SH17 YAML IDs 0 `person`, 10 `helmet`, 16 `safety-vest` are potential positive targets, not proof of identical box policies or high-visibility definitions. ID 12 `head` is not “no helmet”; there is no explicit no-vest class. SHWD `person` is a bare-head target, never target 0 `worker`; `hat` boxes describe helmet-wearing heads and must not automatically be merged into helmet-object target 1. Do not implement these mappings during Step 2.1.

## Objects, wearing relationships, and uncertainty

An object detector locates boxes. Determining whether **an individual worker is wearing PPE correctly** additionally requires spatial ownership, body-region visibility, wearing/fit criteria and context. A vest carried in a hand or lying nearby is not proof it is worn. A helmet near one person's head can belong to another person. The source taxonomy provides no verified PPE-to-worker IDs, fit labels, occupational requirements, or temporal tracks.

Use the five targets as observations feeding the existing association/concern architecture. A visible negative region may support a potential concern only when it can be associated with an assessable worker. An occluded head, cropped torso, low-confidence box, ambiguous ownership, or conflicting positive/negative result must remain uncertain/unable to assess. **No detected helmet/vest is not equivalent to visible missing helmet/vest.** Correctly worn/certified PPE and OSHA compliance are not outputs of this model.

Step 2.2 should propose a review rubric for visible body regions, box scope, overlap/ownership, ambiguity, and contradictory labels. Additional relational/assessability annotations may be needed. Do not suppress uncertain cases merely to improve reported precision or recall. Final concerns require supervisor confirmation, dismissal, or an unable-to-assess decision.

## Licensing and attribution decision

Treat these as separate records:

1. **Dataset images and labels:** Construction-PPE is published as CC BY 4.0. Retain Ultralytics team attribution, dataset/version/date and license links, relevant notices, and a change log for class filtering/remapping or corrections. Proposed attribution: “Ultralytics Construction-PPE Dataset, Ultralytics team, November 2026, CC BY 4.0; adapted for VestCheck by selecting and remapping five classes.” Use the “adapted” wording only once adaptation actually occurs. Verify release notices and upstream provenance before acquisition/preparation approval is acted on.
2. **Alternative datasets:** SHWD's repository MIT file does not clear all externally sourced imagery. SH17's CC BY-NC-SA 4.0 and Pexels-source considerations must not be overwritten by the primary dataset's license. Preserve applicable notices/citations and resolve compatibility before any mixing or redistribution.
3. **Software, pretrained weights and exports:** Ultralytics software is AGPL-3.0, with Enterprise terms advertised separately (U1/U2). Review applicable conditions for the chosen package, pretrained/fine-tuned weights, export tools, plugins and planned app distribution. Public source hosting alone is not a complete compliance assessment; neither CC BY data nor a TFLite/Core ML export establishes permissive software/model rights. No Enterprise agreement or weight-distribution clearance is assumed.
4. **Independent site imagery:** site authorization, worker privacy/consent, secure storage and sharing permissions are independent of public dataset licenses. Never include private inspection photos, confidential locations, consent records, or credentials in the public repository.

These are identified obligations and open questions, not a legal determination about all possible downstream uses. Dataset/license notices and a provenance ledger should be captured during approved preparation; no dataset redistribution is proposed in this PR.

## Independent authorized smartphone test strategy

**Proposal, not collected data:** begin planning approximately **300–500 still photographs** across at least **three authorized sites** and at least **two different smartphone models**, expanding after a sample-size/power review and based on the number of independent concern opportunities. Those numbers are planning targets, not statistical sufficiency or acceptance thresholds. Report per-class/event support and uncertainty intervals; many near-identical frames do not constitute independent evidence.

- Obtain site permission and appropriate participant consent before collection. Use ordinary permitted work and controlled demonstrations in safe designated areas; never request unsafe PPE removal on an active hazardous site just to create negative examples.
- Include assessable PPE present, safely staged visibly missing PPE, mixed workers, empty scenes, ordinary/high-visibility clothing variations, occlusion, partial/out-of-frame bodies, poor light, motion blur, distance, angles and clutter. Represent uncertain/unassessable cases explicitly rather than forcing them into negative labels.
- Keep the independent test sites/sessions out of training and tuning data. Separate by site/day/sequence, not random neighboring frames. A separate authorized development set can support thresholds; never tune on the final independent test set. If public data overlap is suspected, check hashes/source provenance and exclude overlaps before freezing the set.
- Annotate person and PPE/negative-region boxes, visible/occluded head/torso, PPE-to-person relationships where assessable, concern type and uncertainty. Use ephemeral references without worker names or identity embeddings. Have two reviewers independently label a stratified subset and adjudicate disagreement; define the rubric before scoring.
- Keep original images, private annotations and permission records in approved restricted storage outside Git. Minimize PII, strip unnecessary EXIF/GPS on working copies, control access/retention/deletion, and record non-sensitive provenance/hashes and consent status without publishing identities. Any anonymization that changes a target region must be documented and checked for evaluation distortion.
- Report worker/helmet/vest/visible-negative precision, recall and mAP50/mAP50–95, then evaluate per-worker concern false negatives, false alerts, PPE ownership errors and unassessable coverage separately. Break results down by scene/device/lighting/occlusion and scrutinize missed concerns. Align with the denominators and uncertainty reporting in [EVALUATION.md](EVALUATION.md).
- Later, collect separately authorized short clips with event labels for temporal association/duplicate testing; still-image object detection cannot validate duplicate handling. Measure real-time latency, FPS, dropped frames, battery and thermal behavior on real devices in the appropriate implementation phase. Do not infer phone performance from publisher dataset benchmarks.

## Step 2.2 preparation plan — requires explicit approval

The following is a proposed next-step checklist, **not executed work or authorization**:

1. **Resolve access and rights:** approve Step 2.2; identify the exact November 2026 Construction-PPE release and permissible storage location; inspect and retain license/provenance/attribution notices. Resolve any conflicting release metadata before proceeding. No dataset download command is included or executed here.
2. **Inventory the approved release:** record archive/source/version and SHA-256, verify the 1,000 images/14,863 boxes/800–200 claims, enumerate actual class counts by split, count real/generated images if reliable metadata exists, and validate image/label pairing. Unknown generation provenance must stay marked unknown.
3. **Audit label integrity:** check readable files, image dimensions, class ranges, box coordinates, empty labels, corrupted data, missing target labels and consistent body-region semantics. Review all five classes across lighting/occlusion/distance, prioritizing visible-negative and ambiguous/conflicting examples. Define assessability and ownership annotation policy.
4. **Audit duplicates and split leakage:** exact hashes plus perceptual similarity and manual review of candidate clusters; group same scene/source/sequence before splitting. Record original and revised membership. Do not claim no duplicates because filenames differ. Cross-check any later auxiliary sources before mixing them.
5. **Specify and validate the five-class transformation:** preserve originals read-only, remap IDs exactly as above, exclude only out-of-scope annotations, retain useful background images and a reversible transformation log. Check target coverage after filtering. Do not treat missing annotations as negative labels.
6. **Freeze an evaluation design:** assess the publisher 800/200 split for leakage and label coverage. Keep validation for tuning and define a separate public-data holdout only if support permits; otherwise explicitly document that the authorized external test set is the final generalization test. Do not silently reuse the same 200 images for both tuning and final testing. Keep all group-related images together.
7. **Produce preparation evidence:** non-sensitive class-count/split/quality report, duplicate decisions, license/provenance ledger and annotation rubric; resolve whether sparse negatives or generated-domain bias require additional authorized real images. Training, hyperparameter search and model export are separate later work, not part of this preparation approval.

## Remaining review questions

- Can the published counts, licenses and real/generated proportions be confirmed in the selected release? Are `no_helmet`/`no_vest` labels complete and consistently assessable?
- Do class frequencies and group-disjoint splits provide adequate independent examples, especially of missed concerns and multiple workers?
- Are source PPE/negative regions sufficiently associated to persons, or will additional relationship/visibility labels be needed?
- What is the intended portfolio versus future commercial distribution path, and can it meet the chosen software/weight and data license terms?
- Which authorized sites/devices are available for independent evaluation, and what measurable recall, false-alert and latency targets will be agreed before acceptance?

**Scope check:** this change researches and proposes selection only. It does not prepare data, train models, change Flutter, implement inference, or start Step 2.2.
