# Development roadmap

Only Phase 1 is authorized in the current task. Phase 2 requires explicit approval; completing documentation does not authorize training or dataset preparation.

| Phase | Deliverables | Exit evidence |
| --- | --- | --- |
| 1 — Project Initialization and Architecture | README, requirements, proposed architecture, dataset candidates/constraints, MVP acceptance criteria, evaluation plan, initial directories and Git exclusions. | Documentation and repository structure validated; no training or live-camera implementation. |
| 2 — AI Model Development | Audit and select licensed PPE datasets, label mapping, leakage-resistant training/validation/test splits, Colab experiments, lightweight YOLO fine-tuning, unseen-image evaluation, model card and limitations. | Reproducible experiment records, class/concern metrics, independent smartphone-image results, provenance and licensing; assess export feasibility before locking the mobile model. |
| 3 — Mobile Application and Live Camera | Flutter UI, permissions, Android/iOS camera, sampling, inference adapter, compatible mobile exports and live annotations. | Real-device camera/overlay smoke checks, denied-permission handling, output parity and initial latency measurements. |
| 4 — Inspection Session Intelligence | Start/pause/resume/end, ephemeral association, duplicate handling, evidence selection, supervisor review. | Lifecycle/race tests, labeled-video duplicate and missed-event evaluation, evidence and review checks. |
| 5 — Reporting | SQLite persistence, inspection history, PDF generation, verified findings/evidence/timestamps/notes. | Reopen saved inspection after restart; validate PDF content and status separation, missing-evidence and export errors. |
| 6 — Testing and Portfolio Preparation | Real-device performance, accuracy and usability evaluation, privacy checks, limitations, consented demonstrations, technical portfolio documentation. | Agreed MVP acceptance criteria met, unresolved limitations disclosed, no private data in public artifacts. |

## Decisions before Phase 2 work

- Obtain explicit approval to begin Phase 2.
- Confirm dataset acquisition/license permissions and data provenance. No datasets have been downloaded or evaluated in Phase 1.
- Plan the worker/hard-hat/vest label mapping, assessability annotations, independent smartphone evaluation set, and site-separated splits.
- Shortlist lightweight YOLO variants and investigate export/plugin/license constraints before choosing a model that cannot be deployed.
- Establish the initial quality goals, especially missed-concern tolerance; agree on device/latency/battery budgets before performance acceptance.

## Decisions before mobile and release work

Resolve deployment plugin and OS support, access to macOS/Xcode and physical devices, camera and inference lifecycle behavior, retention/deletion/backup policy, PDF package, and notification policy. Build dependencies will be installed only when the relevant implementation phase needs them.
