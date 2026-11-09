# Root-owned build and run recipe

No build or guest run was executed by this agent. Root must separately grant each step, verify `SOURCE-MANIFEST.json` and the immutable original pins, and copy this source-only directory to the fresh `/lab/protocol-durable` root. Preserve `/lab/protocol-guest`, its original stage/image, the active original trials, and `actual-results-001`.

The build consumes only the already-installed runtime stage `/lab/protocol-guest/initramfs`, its original `BUILD-RECEIPT.json`, and the retained source. It verifies the complete existing stage inventory against that receipt and checks the original compressed image hash. It copies that stage, adds the two small wrappers plus original pins, and changes exactly one copied init entry path. It invokes only existing `find` and `cpio`, with Python gzip compression. It installs/downloads/compiles nothing and starts no guest.

After root verifies the source hash manifest in the owned container:

```sh
cd /lab/protocol-durable
PYTHONDONTWRITEBYTECODE=1 python3 build_variant.py
```

Review the fresh `BUILD-RECEIPT.json`, exact init delta, unchanged original runtime source hashes, added source hashes, and image hash. The archive and build receipt are fsynced, including their directory. The copied stage is bounded at 96 MiB and compressed image at 48 MiB; `/lab` remains bounded at 2 GiB. This adds at most 144 MiB for those build outputs plus this small source package. Reclaiming anything remains root's separate decision.

Before running, create a new root-reviewed `RUNTIME-GRANT.json` here with the exact original controller schema: coordinator `root`; its original ordered eleven cases (`validated`, `after_return`, `marked`, `request_logged`, `provider_head`, `provider_archive`, `provider_receipt`, `acknowledged`, `result_ref`, `result_checkpoint`, `complete`); disk_bytes 33554432; exact fresh image and existing kernel SHA-256; and `source_hashes` pinning `controller_entry.py`, `durable_refs.py`, `variant_entry.py`, `ORIGINAL-PINS.json`, `original/root_controller.py`, `original/oracle.py`, `original/guest.py`, `original/init`, `original/source/protocol.py`, `original/source/run.py`, and `build_variant.py`. Do not substitute the original runtime grant or reduce the cases through the entry wrapper.

After that separate grant:

```sh
cd /lab/protocol-durable
PYTHONDONTWRITEBYTECODE=1 python3 controller_entry.py
```

The entry verifies the pinned original controller and oracle, loads them, and changes only `ROOT`/`OUT` to this fresh package. It retains the original one-CPU/256 MiB QEMU invocation, 32 MiB base plus one working disk, 60-second boot bound, 384 MiB package envelope, and 2 GiB `/lab` envelope. The controller requires its own exact Popen child to be killed with exit -9 for each cut, losslessly archives and fsyncs pre-recovery bytes before booting recovery, requires clean recovery unmount and exit, runs the original oracle, retains post-recovery bytes and raw e2fsck output, stops on mismatch, retains the failing raw disk, and never retries. Two boots per case means 22 maximum boots. New results go only to `/lab/protocol-durable/actual-results`.

Audit all `DURABLE_REF` lines by phase: a successful update-ref must finish its complete ordered barrier before the next source prefix/metadata completion. Reconciliation may legitimately perform no mutation and emit none. Retain the whole serial logs, image/archive hashes, grants, source manifest and build receipt. Interpret `e2fsck -fn` only after the original clean recovery boot; its exit alone is not a cleanliness verdict and it is not a pre-replay observation. Host write caches survive the guest cut.

Passing this fresh variant would support the scoped barrier remedy for this fixture and observed cut positions. It would not establish a production implementation, all timings, general Git storage durability, or new-object durability. An additional failure is retained evidence for the next obligation, not grounds to weaken the oracle or repair the original run.

*Authored by an AI agent acting on joshlf's behalf.*
