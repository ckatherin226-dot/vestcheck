# Requirements

Source: user-provided “VestCheck — Project Requirements and Phase 1 Instructions.” Status: planned product requirements; no functional implementation is claimed.

## Product and scope

VestCheck assists construction site supervisors and safety inspectors with smartphone-based inspections. Android and iOS are required. The initial scope is workers, hard hats, and high-visibility safety vests. Professional human judgment remains authoritative.

## Functional requirements

| ID | Requirement |
| --- | --- |
| FR-01 | Start, pause, resume, and end an inspection session. |
| FR-02 | Request camera access and analyze sampled smartphone camera frames. |
| FR-03 | Detect workers and visible hard hats and vests, displaying real-time annotated feedback. |
| FR-04 | Surface possible missing-PPE concerns for verification, preserving confidence and uncertainty; distinguish insufficient visual information from no detected concern. |
| FR-05 | Associate detections temporarily within a session and avoid excessive duplicate findings without identifying individuals. |
| FR-06 | Capture representative evidence images associated with findings. |
| FR-07 | Allow supervisors to confirm, dismiss, or mark findings as unable to assess. |
| FR-08 | Record inspection date/time, site name or location, findings, and corrective-action notes. GPS collection is not required. |
| FR-09 | Store sessions, findings, review status, and evidence references in local SQLite and provide inspection history. |
| FR-10 | Export a downloadable PDF after a session with inspection details, annotated evidence, verified findings, and corrective-action notes. |

## Non-functional requirements

| ID | Requirement and verification intent |
| --- | --- |
| NFR-01 | Use Flutter/Dart for Android and iOS; Python/PyTorch/Ultralytics YOLO for model work; OpenCV only where needed. Document supported tool and OS versions after compatibility evaluation. |
| NFR-02 | Prefer local inference and local data storage. Evaluate Core ML and LiteRT/TensorFlow Lite compatibility with the selected YOLO model before choosing a deployment plugin. |
| NFR-03 | Bound frame processing, avoid queues of stale frames, and keep the interface responsive. Measure latency, throughput, dropped frames, battery, and thermal behavior on real devices. Numeric budgets require agreement before performance acceptance. |
| NFR-04 | Evaluate precision, recall, mAP50, mAP50–95, false positives and false negatives, with particular attention to missed concerns. Record independent smartphone-image results and challenging conditions. |
| NFR-05 | Persist committed inspection and review information reliably; handle permission denial, unavailable inference, missing evidence, and export failures without implying success. |
| NFR-06 | Minimize sensitive data, use private app storage, avoid raw video retention, and document deletion, retention, backup, and export behavior before release. |
| NFR-07 | Keep modules understandable and independently testable for a student AI engineering portfolio; record model/export provenance and limitations. |

## Safety, privacy, and exclusions

- All AI concerns require human verification. Confidence scores must never be presented as proof of OSHA noncompliance.
- Do not automatically certify a site as safe or compliant. A negative detector output cannot establish compliance.
- Occlusion, poor visibility, and other insufficient information must be represented as uncertain or unable to assess.
- No facial recognition, persistent worker identities, cross-session identity tracking, or identity embeddings.
- No advanced fall or electrocution detection in the MVP.
- Avoid unnecessary PII and distracting or repetitive notifications. Supervisors must remain aware of their surroundings.
- Keep private photos, confidential inspection records, credentials, and restricted datasets out of public GitHub commits.
- Document model limitations and report uncertainty honestly.

## MVP acceptance criteria

These are future acceptance checks, not results. Numeric accuracy, latency, duplicate-handling, battery, and supported-device targets remain open and must be agreed before their respective evaluations.

| ID | Observable acceptance scenario |
| --- | --- |
| AC-01 | On each supported Android/iOS device, grant camera permission and see current frames and aligned overlays; denying permission produces an actionable state without a crash. |
| AC-02 | Start → pause → resume → end a session; paused sessions create no new inference observations or evidence, ended sessions reject new findings, and repeated lifecycle actions do not corrupt state. |
| AC-03 | On held-out annotated smartphone images, report per-class worker, hard-hat, and vest detection metrics, concern-level missed/false alerts, and the agreed quality gates. Never substitute detector confidence for these measurements. |
| AC-04 | A clearly assessable suspected missing item becomes a potential concern; an occluded or unassessable region is marked uncertain rather than assumed to lack PPE. No detected concern is labeled as no detected concern, never as safe. |
| AC-05 | A labeled video fixture showing a recurring concern yields one active finding within the configured association window; distinct concurrent concerns remain separate. Re-entry, crossing, occlusion, and post-window behavior are tested and quantified against agreed duplicate/missed-event targets. |
| AC-06 | Capture evidence, review separate findings as confirmed, dismissed, and unable to assess, and retain the chosen status and notes when reopening history. Pending concerns stay distinguishable from verified findings. |
| AC-07 | Save an inspection with date/time and site, end it, restart the app, and reopen the same committed records and valid evidence references. |
| AC-08 | Export and open a PDF containing inspection details, timestamps, annotated evidence, confirmed findings, notes, and a human-review disclaimer. Pending, dismissed, and unable-to-assess items must not appear as confirmed findings. Missing evidence or export failure is explicitly reported. |
| AC-09 | Run a sustained inspection on representative Android/iOS devices, record end-to-end latency percentiles, inference and display FPS, battery and thermal results, and meet the agreed budgets. |
| AC-10 | Inspect data and network behavior: core on-device inspection/history/report workflows operate without mandatory remote services once the model is installed; no identity recognition or unnecessary raw video is stored. Verify deletion and backup policy once specified. |

## Phase 1 acceptance

Required files and directories exist; product scope, architecture, dataset candidates, technical risks, six-phase roadmap, evaluation strategy, and MVP acceptance criteria are documented. Documentation links, Git exclusions, and repository changes are checked. No model training, live camera, or unnecessary dependencies are introduced. Phase 2 requires explicit approval.
