# M2 eval-v2 bootstrap correction — preparation

**Date:** 2026-09-05

**Status:** locally prepared, frozen, unexecuted

The completed 63/63 M2 evaluation family needs no GPU or inference rerun. Review found that the
executed paired-subject bootstrap keyed repeated prompt rows by `fact_id`, silently retaining only
one of eight prompt variants. The local pairing implementation now uses unique `probe_id`, rejects
duplicates and preserves every matched prompt before subject aggregation.

Read-only calculation over the frozen endpoint CSVs produced deterministic corrected transfer and
relearning values without writing HU. The family-level gate remains unchanged: OLMo, Qwen and
SmolLM all fail the frozen +0.05 relearning point-gain minimum. The detailed result record is
`M2_EVAL_RECOVERY_V1A_TERMINAL_RESULT_2026-09-05.md`.

The new contract `documentation/contracts/evaluation/vngrs-m2-oscar-eval-v2-analysis-correction-v1.md`
permits one future 4-CPU/8-GiB append-only publication job under a fresh root. It binds 14 exact
inputs, rechecks all 63 task-result hashes, hashes inputs before and after, writes three compact
control outputs and forbids model/GPU/evaluation/training/cleanup/retry work.

Frozen contract SHA-256:
`da2f3cb0251ae0bf9abc95e5663cb924988e77c1188dbdba4bc9c46066196b3f`.

Focused evaluation/recovery/correction tests pass 38/38. Preparation itself performed no source
write, job submission, model load, evaluation, training or cleanup. The user's instruction allows
local commit and ordinary push; HU fast-forward and execution remain separately SHA-bound.
