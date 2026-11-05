# Model limitations register

Status: no model selected or evaluated. These are anticipated limitations to investigate, not measured claims about trained model performance.

| Limitation | Intended handling / evidence needed |
| --- | --- |
| Occluded head/torso, poor light, distant workers, blur, unusual angles | Visibility/uncertainty handling and stratified held-out evaluation. |
| Dataset/domain bias and incomplete annotations | Provenance and label audit, independent smartphone images, class/scene breakdowns. |
| Missing detection does not prove missing PPE | Assessability and association rules, human verification, explicit uncertain states. |
| Correct object detection does not ensure correct worker/PPE association | Multi-worker and crossing tests; concern-level metrics. |
| Temporal IDs may drift, merge, split, or duplicate on re-entry | Ephemeral session-local association and labeled event tests; no identity claims. |
| Mobile export/quantization can change outputs | PyTorch-to-device parity and missed-concern regression evaluation. |
| Sustained camera/inference can affect battery, thermals, and responsiveness | Real-device sustained tests and bounded sampling. |

For each evaluated model, add version/date, datasets and licenses, hardware, metrics, failure cases, thresholds, tested conditions, and unresolved limitations. Do not claim OSHA compliance or safe-site certification. Findings require professional human review.
