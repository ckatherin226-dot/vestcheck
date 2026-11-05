# Validation

Phases 2.2A–B include synthetic unit tests for acquisition, auditing, numerical correction, five-class preparation, immutable originals, deterministic sample selection and scene-search diagnostics:

```bash
python -m unittest discover -s tests -p 'test_dataset*.py' -v
```

Install only the audit dependencies listed in `model/requirements-audit.txt` when needed; see [usage](../model/AUDIT_TOOLS.md). Tests create small synthetic images and labels in temporary directories and do not require downloading a dataset or importing training frameworks.

Application, model-accuracy, inference and device performance tests remain future work. Use the [MVP acceptance criteria](../docs/REQUIREMENTS.md) and [evaluation plan](../docs/EVALUATION.md) when those phases are authorized. Keep private smartphone photographs, inspection records and reports outside the repository.
