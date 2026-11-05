# Mobile application boundary

Planned stack: Flutter and Dart for Android and iOS. This directory is a tracked placeholder in Phase 1; no Flutter project, live camera, inference plugin, or runtime dependencies are installed here.

Future modules: presentation, session lifecycle, camera/sampling adapter, inference adapter, ephemeral association, concern assessment, evidence storage, SQLite repository, history, and PDF export. See [architecture](../docs/ARCHITECTURE.md) for boundaries and [roadmap](../docs/ROADMAP.md) for phase timing.

Evaluate model/export compatibility before choosing Core ML or LiteRT/TensorFlow Lite Flutter integration. Record minimum OS and package versions after verification. iOS build/signing needs macOS/Xcode; real-device validation is required on both platforms.
