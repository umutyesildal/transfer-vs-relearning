# M2 recovery V1A corpus-copy repair and submission

User explicitly authorized compatibility repair and submission after the V1 failure. The narrow
V1A contract SHA is `65ed0d725a8f2b703d05f863635cceb88e5620a06cbb252d6775498fa8029498`.
Commit `b8230dfb88232182a7c92e9283711c8e6d5f7989` was ordinary non-force pushed and clean-
preservation fast-forwarded on HU. All 64 targeted tests passed locally and on HU, including
the actual base evaluator's copied-corpus verification boundary before a GPU sentinel.
All frozen implementation/config hashes matched. Existing guards were not relaxed.

Only the existing heldout JSONL is copied byte-for-byte into an exclusive regular file, bounded
at 128 MiB and verified against its frozen SHA. No reconstruction or download. Completed21
state references and prior roots stay read-only. V1 dead jobs484051/484052 are untouched.

Exactly four test-only checks passed (hypothetical IDs484053–484056) and one chain was submitted:
CPU484057, canary484058(task21), array484059(indices22–62%6), finalizer484060.
The CPU was observed RUNNING on gruenau10 at elapsed11s; other jobs were dependency-pending.
No retry, cancellation or cleanup occurred.

Fresh root: `/vol/tmp2/yesildau/vnd_m2_oscar_eval_v2_recovery_v1a`.
Submission SHA: `6c24e6aa806117460de01a1b17b41dd33048b2f434a432f342aba4d5d924cdbc`.
Matrix SHA: `6d3b8b97f048e1531d2146e2d47626a7cf8475122bb2abf32c124a60536d990d`.
The wave is consumed; do not submit again. The canary must succeed before remaining41 open.

Subsequent inspection: preflight PASS reproduced the frozen source inventory. Canary484058
was RUNNING on gruenau10 at elapsed19s and passed the previously failing corpus boundary and
the actual GPU gate. CUDA free=73,493,839,872 bytes; SMI free=73,494,691,840 bytes. Native
_CUuuid was correctly normalized to GPU-4fc987af-7ab7-e2c3-e2bb-eec01fb1ba9d. This is not
canary completion: the scientific evaluator must still finish successfully before array484059.
GPU audit SHA: `afc92038633c1cb223fc6c6685a19328325cd38da101ab6347ceea2cbb66042f`.
The canary's initial stderr was empty on the subsequent read.

## Terminal continuation — 2026-09-05

Canary and remaining array tasks subsequently completed, and finalizer `484060` closed the family
at 63/63 with zero failed or missing states. The terminal result, integrity hashes and the
prompt-identity bootstrap correction are recorded separately in
`M2_EVAL_RECOVERY_V1A_TERMINAL_RESULT_2026-09-05.md`. This submission record remains the historical
launch/progress record and is not used as the terminal scientific authority.
