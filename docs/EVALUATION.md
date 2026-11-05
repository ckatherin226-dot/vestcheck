# Model evaluation and real-time performance plan

Status: planned validation for later phases. No experiments, tests of application behavior, or benchmark results exist in Phase 1. Numeric quality/performance thresholds and device coverage must be agreed before their associated acceptance gates.

## Dataset and protocol

Use licensed, provenance-recorded data with worker/hard-hat/vest labels and explicit visibility/uncertainty rules. Split by site/source/scene and remove near duplicates before training. Freeze an untouched test set; collect authorized independent smartphone images and labeled short video sequences without committing private material. Use validation data for confidence, NMS, association and alert thresholds; do not tune against the final test sets.

Record dataset and split versions, model variant and weights provenance, tool/export versions, seeds, input resolution, preprocessing, thresholds, precision/quantization, hardware, OS, and configuration for each run. Colab runs should record GPU/runtime details and preserve non-sensitive experiment metadata outside transient notebook sessions.

## Detection and concern quality

- Report per-class and aggregate precision, recall, mAP50, and mAP50–95, with explicit IoU and matching rules. Include support counts, TP, FP, FN, and confusion/error examples.
- Evaluate worker-to-PPE association and potential concerns separately from object detection. A model can detect a vest correctly while assigning it to the wrong worker.
- On assessable labeled concern opportunities, report false-negative rate FN/(TP+FN), precision, and recall. Report uncertainty coverage and unassessable cases separately so abstention cannot hide missed hazards.
- For a scene/event-level binary concern test with defined true negatives, report false-positive rate FP/(FP+TN). Object detection generally lacks a meaningful background TN count; report false alerts per minute or inspection for video instead of inventing an object-level FPR.
- Break down results by low light, occlusion, camera angle, distance/object size, multiple workers, clothing/vest styles, and independent smartphone images. Inspect missed potential concerns explicitly.
- Use the same held-out inputs to compare PyTorch, Core ML, and LiteRT/TensorFlow Lite artifacts. Check preprocessing, box alignment, class mapping, NMS, numerical differences, and downstream concern regressions after export or quantization.

## Temporal association and duplicate handling

Annotate concern events in videos with session-local references, event start/end, PPE type, visibility, and distinct simultaneous subjects, without recording identities. Define a duplicate as more than one reviewable finding for the same ground-truth concern event within the configured association window.

Measure duplicates per event, missed events, false alerts per minute, incorrect merges/splits, and time to first alert. Include crossings, occlusion, stationary scenes, re-entry, rapid motion, repeated pause/resume, and multiple similar workers. Record association window/expiry policy. Optimize alert burden without hiding distinct or recurring concerns.

## Real-device performance

Select representative low/mid/high-tier Android and iOS devices and record model, RAM, chipset, OS, runtime/delegate, precision, input size, sampling rate, and power conditions. iOS builds and signing require macOS/Xcode and suitable devices; cloud availability is not assumed.

1. Separate cold model-load time from warmed inference. Measure preprocessing, inference, postprocessing, association, and UI overlay costs.
2. Measure end-to-end frame-capture-to-overlay latency at p50/p95/p99 using timestamps; report capture FPS, sampled FPS, inference throughput, rendered FPS, and dropped/stale-frame counts separately.
3. Run a proposed 15-minute sustained inspection per device/configuration, then extend as needed to the intended inspection duration. Record memory, crashes, thermal throttling, and battery change against an equivalent camera-only baseline. This duration is a measurement protocol proposal, not an approved performance budget.
4. Repeat runs under comparable conditions; report variation and thermal state. Exercise pause/resume, backgrounding, interruptions, model failure, and offline operation.
5. Agree on maximum latency, minimum useful inference rate, acceptable battery/thermal behavior, memory budget, and device/OS support before declaring real-time performance accepted.

## Workflow and safety validation

Trace checks to [MVP acceptance criteria](REQUIREMENTS.md): permission handling, overlays, lifecycle and late results, evidence integrity, all review states, persistence after restart, local history, and PDF content/status separation. Verify that no AI message or report certifies safety or compliance. Test unassessable scenes and no-detection states separately.

Audit outbound requests, file storage, retention/deletion, backups and exports against the agreed privacy policy. Public portfolio examples must use licensed/consented non-sensitive material. Document limitations, failures, skipped checks, and the precise tested hardware; never describe unrun checks as passed.
