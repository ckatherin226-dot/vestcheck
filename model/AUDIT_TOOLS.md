# Dataset acquisition and audit tools

These Python tools download the officially documented Construction-PPE archive and inspect originals without training, rewriting labels, moving images, or creating splits. They do not import YOLO, PyTorch, Flutter or inference runtimes.

## Dependencies and tests

From the repository root, use Python 3.12 and the versions in `model/requirements-audit.txt`. These packages were already available during the recorded run. For a fresh machine:

```bash
python -m venv .venv
.venv/bin/python -m pip install -r model/requirements-audit.txt
.venv/bin/python -m unittest discover -s tests -p 'test_dataset_audit.py' -v
```

Use the active Python executable instead of `.venv/bin/python` if those dependencies are already available. Synthetic images are generated in temporary directories during tests; no source photos are test fixtures.

## Acquire into a fresh ignored workspace

```bash
python model/acquire_dataset.py --workspace model/data/audit-2026-11-05
```

Use a new directory if that path already contains an acquisition; the tool refuses to overwrite it. `/model/data/` is ignored by the repository. The script records a pinned official configuration/documentation revision, verifies the documented download URL and published image/annotation license statement, streams HTTPS with normal certificate verification, verifies the archive against this audit's observed SHA-256, and checks ZIP paths/symlinks/duplicates and CRCs during extraction. An upstream archive change requires human review and an explicit code update, not disabling checks. The pinned digest is an observed release identifier, not a publisher-signed checksum.

Outputs include `acquisition.json`, original ZIP, official source documents, extracted `original/`, and `original-manifest.json` with content hashes. Original files are never rewritten. Failure records report the exception type without copying remote error text that could expose credentials. A partial download is removed; a failed extraction is discarded. Network access uses the environment's normal proxy; no verification or policy bypass is supported.

## Audit originals

```bash
python model/audit_dataset.py \
  --root model/data/audit-2026-11-05/original/construction-ppe \
  --config model/data/audit-2026-11-05/original/construction-ppe/data.yaml \
  --output model/data/audit-2026-11-05/results
```

Output must be outside the original dataset. JSON contains per-file issues and candidate pair references; Markdown summarizes statistics. Detailed reports stay in the ignored workspace; review filenames and metadata before publishing anything from a private dataset. Only non-sensitive aggregate findings are committed in [the audit document](../docs/DATASET_AUDIT.md).

Exit status **0** means the supported layout/mapping, decoding, parsing and strict box checks passed; it does not certify semantic quality or absence of leakage. Exit status **2** means a quality gate needs review and the generated reports remain available. The recorded Construction-PPE audit exits **2** because of the 94 strict corner-boundary flags. Do not suppress this status or describe it as a clean quality pass. Missing/empty labels, duplicate candidates and scene leakage require human review even when status is 0. Missing expected directories or unsupported configured paths raise an error instead of returning a misleading zero-image success.

## Methods and limits

- Source counts include all paired rows with a recognized source class. Valid counts additionally require exactly five fields, finite normalized positive dimensions, and in-frame corners with a `1e-6` tolerance. Repeated rows are counted and flagged separately. Orphan and ambiguous-stem labels are excluded from paired class counts. Nonempty row numbers, rather than physical line numbers, identify label issues.
- Tiny edge excursions at or below `1e-5` are classified separately as rounding candidates, but **not** silently accepted or corrected. These numerical cutoffs are audit definitions, not training or safety thresholds.
- Images are verified and fully decoded with Pillow. SHA-256 of file bytes finds exact files; SHA-256 of EXIF-oriented decoded RGB dimensions/pixels finds identical decoded content, including some re-encodings. Decoded equality does not guarantee identical labels.
- Near duplicates use exhaustive pair comparison for this small dataset: horizontal 64-bit dHash distance at most 4 and relative aspect-ratio difference at most 5%. Exact file/pixel matches are excluded from this candidate list. `--near-threshold` can change the Hamming threshold; record changes with the result. Complexity is O(n²); use a suitable index for much larger datasets. Crops/rotation/color edits can be missed; unrelated/flat images can collide. Flagged pairs are not automatically deleted or moved.
- Opposing helmet/no-helmet and vest/no-vest boxes with IoU at least 0.5 are flagged as review candidates, not proven contradictions; different box extents and missing relational labels limit this screen.
- Optional `manifest.jsonl` is checked against file SHA-256, annotation-row counts, available dimensions and membership. Metadata absence does not prove an image is real or generated.
- All original file hashes are compared before/after an audit; acquisition also stores a baseline manifest. No output or image cache is written inside originals.
