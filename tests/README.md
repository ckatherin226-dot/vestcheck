# Validation plan

This tracked directory contains documentation only in Phase 1. No executable application tests exist and no application behavior has been validated.

Future checks should map to [MVP acceptance criteria](../docs/REQUIREMENTS.md) and the [evaluation plan](../docs/EVALUATION.md):

- Unit checks for session transitions, stale-result rejection, concern/uncertainty rules, association and duplicate handling, review state, and report selection.
- Integration checks for camera permissions/rotation, export preprocessing/output parity, SQLite and private-file consistency, history recovery, and PDF export.
- Real-device and labeled-video checks for latency, FPS, battery/thermals, missed concerns, duplicate rates, and interrupted/offline workflows.

Use licensed, synthetic, or expressly approved non-sensitive fixtures. Store private smartphone images, inspection records, and reports outside the repository. Choose test runners after the relevant stack and packages are pinned; do not install test dependencies during Phase 1.
