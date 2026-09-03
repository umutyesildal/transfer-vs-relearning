# vngrs-m2-oscar-eval-v2-recovery-v1a

Frozen single corpus-file compatibility repair. The user explicitly requested fixing and
sending this repair after V1's canary failure: "uyumlu hale getir ve yolla sana izin veriyorum".
That current authorization covers this narrow implementation/publication/one-wave correction;
no automatic retry beyond this wave is permitted.

Inherit all scientific identities, thresholds, source inventory, runtime, resources, DAG,
failure/STOP semantics and prohibitions from immutable recovery V1 (SHA-256
`cd5731b29f5fa269e9ea98d919062e1160ad4a0af90fc0b3138998137a5c7bc4`) except these explicit changes:

- Fresh root `/vol/tmp2/yesildau/vnd_m2_oscar_eval_v2_recovery_v1a`.
- Names `m2-rec-a-pre`, `m2-rec-a-canary`, `m2-rec-a-array`, `m2-rec-a-final`.
- Copy only the existing frozen OSCAR heldout JSONL, at most 128 MiB, byte-for-byte to an
  exclusively created regular file under the new root instead of a symlink. Verify source and
  destination SHA `0b1eddf91704e2b9b2ef345670141284b7c51002972809f8543907302323c36d`.
  No corpus reconstruction/download or source change. Incomplete copies remain preserved.
- Keep completed-state and control read-reference links; keep the base verifier unchanged.
- Recovery module SHA `4de5c1227252d6f02d5b38e64f5855ba0ca589e42bc371b95ccdd8ffa7c8c2a7`.
  Entrypoint, config, base executor, GPU gate and runtime lock are unchanged from V1.
- Run 64 targeted CPU tests locally and HU, including the actual base executor's corpus
  verification boundary (GPU operation replaced by a sentinel, no model/GPU work in tests).

Ordinary non-force publication and clean preservation-checked HU fast-forward are allowed for
the narrow repair commit recorded before dispatch. Then exactly one CPU preflight, task21 canary,
`afterok` array22–62%6 and `afterany` finalizer. Existing V1 jobs 484051/484052 remain untouched:
no cancellation, release or reuse is included. They are dependency-dead, not a duplicate V1A wave.
The original 21 complete evaluations remain read-only; only the original missing42 are scored.
Parent/checkpoint access is read-only inference only. Training, checkpoint writing, source/prior-
root mutation, cleanup, deletion, fallback, another repair wave and automatic retry are forbidden.
