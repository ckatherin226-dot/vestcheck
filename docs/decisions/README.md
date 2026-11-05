# Architecture decisions

Phase 1 establishes the following design direction from the supplied requirements:

- Flutter/Dart mobile application for Android and iOS.
- Local SQLite metadata and private evidence files.
- Prefer on-device inference; Python/Colab supports model development rather than a mandatory backend.
- Human-reviewed findings with explicit uncertainty and ephemeral session-only association.

The model variant, export settings, deployment plugin, performance budgets, data retention policy, and package versions remain open. See [architecture and tradeoffs](../ARCHITECTURE.md).

For each later significant decision, add a numbered record with status/date, relevant requirements, options, rationale, consequences, and validation evidence. Do not mark unresolved compatibility assumptions as verified decisions.
