# Model development boundary

Planned tools for later model work: Python, PyTorch, Ultralytics YOLO, Google Colab, and OpenCV where needed. Phase 2.2A added acquisition and read-only quality auditing. Phase 2.2B adds deterministic five-class staging preparation, visual-review diagnostics and a documented review record. No training, model weights, exports or inference have been implemented.

- [Five-class preparation and reproduction commands](../docs/DATA_PREPARATION.md)
- [Annotation review](../docs/ANNOTATION_REVIEW.md) and [proposed split policy](../docs/SPLIT_POLICY.md)
- [Audit tools and reproduction commands](AUDIT_TOOLS.md)
- [Actual acquisition and audit findings](../docs/DATASET_AUDIT.md)
- [Proposed next preparation steps](../docs/DATA_PREPARATION_PLAN.md)
- [Dataset research](../docs/DATASETS.md) and [selection](../docs/DATASET_SELECTION.md)
- [Evaluation strategy](../docs/EVALUATION.md) and [known limitations](LIMITATIONS.md)

Original downloads and detailed reports stay in the ignored `model/data/` workspace. Do not commit raw images, label corpora, private data, archives or large artifacts. The five-class derivative is staging only; publisher train/validation membership is preserved and known scene overlap remains. Do not start training until split/annotation gates are resolved and training is explicitly approved.
