# M2 evaluation recovery preparation

The user requested completing and submitting the missing evaluations tonight. Preparation and
bounded read-only HU evidence inspection were performed; no new jobs or publication occurred.
The prior GPU qualification succeeded as job 484043; its record is M2_GPU_IDENTITY_V1A_PASS_2026-09-04.md.

The source audit found 21 complete and 42 failed states. Failed directories contain exactly
task_result.json and two generated configs; all failures retain the same pre-model GPU guard
message. Full state-file hashing covers 1,288 files / 1,091,411,786 bytes. A first overly verbose
metadata response was truncated and was not treated as a complete inventory. A subsequent
bounded hash pass returned complete compact per-state records, and a second reproduction bound
the canonical aggregate SHA `bc930b814634530538c7ec4cb3642ffe1d5eed10e3d6ebe150bc75d3e8ec4839`.
The existing heldout file hash passed. No source file was written; model weights were not read.

The new wrapper reuses the scientific executor unchanged. New root references existing completed
states and heldout input read-only, runs task21 as canary, and gates array22–62%6 on its success.
Input/task errors set STOP for later tasks; active peers may finish and process-kill cannot ensure
STOP persistence. This limitation is explicit in the contract. Original results are hash-checked
before and after the wave. Partial submissions retain their known IDs and never retry.

Local test result: 63 passing targeted tests, including 14 recovery tests for source byte drift,
unexpected failed-state scoring files, symlinks, source preservation, no rescoring, canary/fail-stop,
fresh destinations, exact DAG/index/dependency resources, partial submission and combined finalizer.
These are offline tests, not evidence that scientific inference has restarted.

The frozen contract is `documentation/contracts/evaluation/vngrs-m2-oscar-eval-v2-recovery-v1.md`.
The final exact SHA/commit authorization is still needed before push/HU synchronization/submission.
