# M2 recovery V1: preflight PASS, canary input-link failure

The exact authorized commit abd446f8512b6ab335269ca25edaa85223f8b676 was ordinary non-force
pushed and clean-preservation fast-forwarded on HU. Contract/config/code/runtime hashes passed;
63 targeted CPU tests passed locally and on HU. Available scratch was 121,546,721,984,512 bytes
with 2,283,843,878 free inodes. Four test-only checks passed (hypothetical IDs 484045–484048).

Exactly one recovery chain was submitted under
`/vol/tmp2/yesildau/vnd_m2_oscar_eval_v2_recovery_v1`:

- CPU preflight 484049: COMPLETED, exit0, 27 seconds, 01:09:14–01:09:41 cluster time.
- Canary 484050: FAILED, exit1, four seconds, 01:09:41–01:09:45, gruenau10 A10080GB.
- Array 484051, indices22–62%6: never started, DependencyNeverSatisfied.
- Finalizer 484052: never started, dependency pending.

Submission SHA: `2972c31d4c2629a8f1098a65966ef600f1cb6adc4d1d5f1f128d496ab448c32c`.
Matrix SHA: `d8c6f66ac1fc3f85df7faad2062aee9c9c2514693878bfcfbca2518879d07ba1`.
Preflight SHA: `40694f5cd98842d4e0b5d2bdbf77f9cda91466446c9a3069e05bae106f500494`.
Canary stderr SHA: `9ee183c938449230dce10462de41f7d8e59cde0803e9dcbc387a7e3a1e6bc4b7`.

## Confirmed cause and boundaries

Preflight reproduced the exact frozen source inventory
`bc930b814634530538c7ec4cb3642ffe1d5eed10e3d6ebe150bc75d3e8ec4839` and created read-reference
links. Canary reached base.run_task's OSCAR `_verify`, which rejects path.is_symlink() even
when the target bytes match. The wrapper deliberately linked this input, creating an integration
incompatibility. Read-only rehash returned the expected corpus SHA
`0b1eddf91704e2b9b2ef345670141284b7c51002972809f8543907302323c36d`; there is no observed
corpus-content drift. CPU mock tests covered wrapper links and mocked dispatch, not the actual
base verifier on that linked corpus. That coverage gap is retained explicitly.

No GPU identity probe, model loading or scientific scoring was reached. The wrapper persisted
control/STOP; the canary dependency prevented all 41 remaining tasks from starting. Existing
21 completed states remain preserved; family remains 21/63, not a scientific negative result.
The one wave is consumed. No retry, cancellation, cleanup, source mutation or new publication
was attempted. Dead downstream jobs remain untouched as required by the contract.

Next repair must reconcile the exact bound read-only corpus input with the base verifier, test
that real boundary without models, and use a separately authorized fresh root. Do not weaken
the global symlink guard or silently reuse the failed root. A new exact contract and user
authorization are required for further execution or pending-job cancellation.
