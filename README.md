# VestCheck

**AI-assisted construction safety inspections on Android and iOS.**

VestCheck is a planned mobile application for construction site supervisors and safety inspectors. It will analyze smartphone camera frames for workers, hard hats, and high-visibility vests, surface potential PPE concerns for human review, and produce inspection reports.

VestCheck assists professional judgment. It does not certify a site as safe or OSHA compliant. Model confidence is not proof of a violation; no detected concern is not evidence that a scene is assessable or safe.

## Objectives and MVP

- Provide live annotated camera feedback using lightweight object detection.
- Start, pause, resume, and end inspection sessions.
- Associate observations within a session without identifying workers, reducing duplicate findings and excessive alerts.
- Capture representative evidence and let supervisors confirm, dismiss, or mark concerns as unable to assess.
- Store site details, dates, findings, review status, and corrective-action notes locally.
- Provide local inspection history and downloadable PDF reports with annotated evidence and verified findings.

The MVP excludes facial recognition, worker identity tracking, autonomous compliance judgments, and advanced fall or electrocution detection.

## Planned technology stack

| Area | Plan |
| --- | --- |
| Mobile | Flutter and Dart; Android and iOS |
| Model development | Python, PyTorch, Ultralytics YOLO; OpenCV where needed |
| Training | Google Colab, construction PPE datasets, transfer learning and fine-tuning |
| Mobile inference | Prefer on-device; evaluate Core ML on iOS and LiteRT/TensorFlow Lite on Android |
| Persistence | SQLite for inspection metadata and evidence references; private app storage for images |
| Reports | PDF generation on the device; package to be selected |
| Version control | Git and GitHub |

The YOLO model variant, export settings, Flutter deployment plugin, and package versions are not selected. Compatibility and licensing must be checked before committing to them.

## Architecture

Camera frames → sampling → YOLO detection → temporal association and duplicate handling → potential PPE concerns → supervisor verification → local storage → PDF reports.

A modular, local-first Flutter application is proposed. Python supports model development and export rather than a required runtime backend. See [architecture and tradeoffs](docs/ARCHITECTURE.md).

## Repository structure

```text
mobile/              Flutter application boundary; documentation only in Phase 1
model/               Model development boundary; documentation only in Phase 1
docs/                Requirements, architecture, roadmap, and evaluation plans
  decisions/         Architecture decision records
tests/               Validation plan; no executable application tests yet
```

## Development roadmap

1. **Initialization and architecture:** repository, requirements, architecture, dataset candidates, technical constraints, MVP acceptance criteria.
2. **AI model development:** evaluate datasets, prepare splits, fine-tune, evaluate unseen images, document limitations.
3. **Mobile application and live camera:** Flutter UI, camera integration, mobile inference, overlays.
4. **Inspection session intelligence:** lifecycle, temporal association, duplicate reduction, evidence and human review.
5. **Reporting:** local persistence and history, PDF export.
6. **Testing and portfolio:** real-device evaluation, usability, limitations, demonstrations and documentation.

See [deliverables and phase gates](docs/ROADMAP.md). Phase 1 documentation is complete; Phase 2 has not started and requires explicit approval.

## Documentation

- [Requirements and MVP acceptance criteria](docs/REQUIREMENTS.md)
- [Architecture, data flow, risks, and open decisions](docs/ARCHITECTURE.md)
- [Dataset candidates and selection constraints](docs/DATASETS.md)
- [Model evaluation and mobile performance plan](docs/EVALUATION.md)
- [Known model limitations](model/LIMITATIONS.md)
- [Architecture decisions](docs/decisions/README.md)
- [Validation organization](tests/README.md)

## Working in this repository

Phase 1 is documentation only: there are no dependency manifests, training scripts, application startup commands, or executable tests. No additional dependencies are needed. Use the existing cloud checkout; each cloud task is already isolated, so do not create another Git worktree unless requested.

Keep credentials, inspection photographs, private datasets, databases, reports, and model artifacts out of Git. The root `.gitignore` provides initial exclusions; it cannot protect files already tracked or private content saved under arbitrary names. Review staged changes before every commit. Only use appropriately licensed, consented, non-sensitive assets in public demonstrations.
