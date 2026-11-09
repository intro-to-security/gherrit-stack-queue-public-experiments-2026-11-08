# Git durability settings are version-specific

The actual guest runs Git 2.34.1. The [2.34 manual](https://git-scm.com/docs/git-config/2.34.0#Documentation/git-config.txt-corefsyncObjectFiles) documents `core.fsyncObjectFiles` for object files. It does not supply a reference-hardening promise for this experimental completion sequence. Existing objects were deliberately synced before dispatch, so this run does not test new object creation.

The [2.56 manual](https://git-scm.com/docs/git-config/2.56.0#Documentation/git-config.txt-corefsync) describes component-specific hardening, including `reference`. Its `committed` aggregate is described as objects, so the name alone is not evidence that every newly written ref is durable. The manual also distinguishes `fsync`, `writeout-only` and `batch`, and explicitly qualifies crash durability by method and platform. These settings were not exercised by the Git 2.34.1 guest. A future production implementation should select and validate the actual supported Git/backend/filesystem mechanism instead of copying a flag from another version.

The separate proposed experimental repair adds a scoped file-and-directory barrier for the known loose refs. That can test the captured local gap without claiming support for packed refs, reftable, linked worktrees, object creation, concurrent Git maintenance, macOS or physical host loss. It is a test realization, not a portable production Git persistence API.

The manuals were read on November 9, 2026. Source descriptions and finite guest observations establish different evidence: documentation describes a supported configuration, while the guest records one exact implementation/environment outcome.

*Authored by an AI agent acting on joshlf's behalf.*
