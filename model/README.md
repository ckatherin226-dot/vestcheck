# Model development boundary

Planned tools for later model work: Python, PyTorch, Ultralytics YOLO, Google Colab, and OpenCV where needed. Phase 2.2A adds **acquisition and read-only quality auditing only**; no training, model weights, exports or inference have been implemented.

- [Audit tools and reproduction commands](AUDIT_TOOLS.md)
- [Actual acquisition and audit findings](../docs/DATASET_AUDIT.md)
- [Proposed next preparation steps](../docs/DATA_PREPARATION_PLAN.md)
- [Dataset research](../docs/DATASETS.md) and [selection](../docs/DATASET_SELECTION.md)
- [Evaluation strategy](../docs/EVALUATION.md) and [known limitations](LIMITATIONS.md)

Original downloads and detailed reports stay in the ignored `model/data/` workspace. Do not commit raw images, label corpora, private data, archives or large artifacts. Do not convert the full dataset or alter train/validation membership until the audit is reviewed; model training requires explicit approval.
