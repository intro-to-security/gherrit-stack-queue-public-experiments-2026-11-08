# Independent v3 guest source/evidence audit

The retained v3 records support the eight stated single-trial outcomes. Full
old/new JSON values independently match the actual case records: unsynced temp
absent in case1; file-synced temp present in case2; case3's active old plus temp
new after an acknowledged rename without directory fsync; active new in cases4/5;
durable intent in case6; ref1/checkpoint0 in case7; both1 in case8. Sixteen exact
owned QEMU children reached their expected cut/recovery barriers and were killed
individually. No process-name kill or shared-runtime reset appears in the source.

The boundary is correctly described as guest/emulator loss with outer caches
alive. File/directory fsync syscalls and barrier order are explicit. These are
useful observed persistence-prefix distinctions, not universal durability claims.

Several acceptance/oracle limits matter:

- Records are small JSON strings, without a multi-block payload/checksum. The
  controller accepts active old or new even before rename and compares only
  generations for the ref/checkpoint paths. Raw observed values happen to match
  the intended values, but the original oracle does not reject every meaningful
  wrong full value or foreign-result association.
- A matching generation pair is not itself completed-operation evidence. V3
  records no separate done marker or actual provider outcome. Case7's actual
  ref1/checkpoint0 makes a reference-only success classifier concretely wrong;
  the offline extension audit exposes that control using the retained records.
- Ref/checkpoint are JSON proxies. No actual Git object/ref/reflog transaction or
  corrected Python executor runs inside this guest.
- Only the pre-inspection disk hash was saved. The read-write recovery mount and
  journal replay changed disk bytes, then inspection ended with another cut.
  Retaining the actual pre-inspection image is necessary to revisit that prefix.
- Every retained `e2fsck -fn` result has exit0 **and** text reporting skipped
  journal recovery, wrong free-block/free-inode counts and declined fixes. Exit0
  does not mean a clean filesystem. Fsck ran after the rw recovery mount and
  second cut, so its diagnostics do not directly inspect the first-cut snapshot.

The extension addresses these discriminators with complete multi-block bytes,
checksums and full-value checks, explicit pending-versus-done classification,
bad controls, exact pre/post disk archives and a clean-unmount inspector contrast.
It does not expand those observations into a production implementation claim.

The actual package manifest includes Python3.10 and the required C/QEMU tools,
but no Git package. A separately scoped actual-prototype integration could copy
Linux Python/runtime libraries and an available Linux Git into a new initramfs,
or add a bounded Git package in the owned container. That would need exact
version/dependency/size checks and root approval; it is not part of this extension.
It could test the experimental local executor's Git/ref/checkpoint prefixes
under guest cuts. There is no production native GHerrit client to validate yet.
It would still supply no GitHub arbitration guarantee or physical power-loss
evidence. No package, container or emulator action was performed by this auditor.

*Authored by an AI agent acting on joshlf's behalf.*
