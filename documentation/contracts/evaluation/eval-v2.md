# Evaluation Contract v2

**Lifecycle:** frozen

**Execution authorized:** no

**Supersedes prospectively:** `eval-v1` for all not-yet-run M1/M2 work

## Purpose

eval-v2 is the single evaluation protocol for M0, M1, M2-A and M2-B. It inherits eval-v1 by exact
file identity and changes exactly one scientific element: Pile-10k is retired from the active task
set and every gate, cadence and completeness rule.

The inherited eval-v1 contract is
`documentation/contracts/evaluation/eval-v1.md`, SHA-256
`72403598d7f9c8ba35bdfcc3e4791d097d41c6ef8f4e79c55cf9a6f34a37479e`. The controlling decision is
`documentation/decisions/PILE_10K_RETIREMENT_AND_EVAL_V2_DECISION_2026-08-22.md`, SHA-256
`39e75bfa1e2f1588a861aab72014a3b40bd8aecabaa61319b76107a6c027c10c`.

## Exact active Harness tasks

- `wikitext`;
- `blimp`;
- `hellaswag`;
- `winogender_female`;
- `winogender_male`;
- `winogender_neutral`;
- `turblimp_core`.

Harness remains pinned to release `v0.4.12`, commit
`6d642546f4688648fced259eb3302efd36ece5af`. Dataset revisions, few-shot settings, aggregations and
metrics are inherited unchanged from eval-v1 through the frozen active registry.

## Retention and capability gates

- WikiText: `delta BPB <= log2(1.25) = 0.32192809488736235` relative to the frozen parent;
- BLiMP: absolute accuracy drop at most `0.05`;
- HellaSwag: absolute `acc_norm` drop at most `0.05`;
- WinoGender: diagnostic, no gate;
- Turkish, factual, exact-prefix, generation-integrity, uncertainty and M2 sibling gates: unchanged
  from eval-v1.

There is no Pile row, threshold, completeness requirement or fallback in eval-v2. Missing Pile
evidence cannot block a state and cannot be imputed.

## Cadence

WikiText remains dense at the frozen parent and every epoch-end checkpoint. Full factual and
capability evaluation remains at state entry, precommitted midpoint and endpoint. Exact-prefix is
mandatory at all four states under its existing amendment. All checkpoint mappings must be frozen
before training.

## M0 reuse

eval-v2 M0 is a hash-closed projection of the already completed non-Pile eval-v1 evidence: seven
lanes per model, 21 total. No retained lane is rescored. The historical 24-lane eval-v1 family and
all Pile attempts stay immutable. A separately validated normalizer must record the source path and
SHA-256 of every selected lane before a canonical comparison is claimed.

## Failure and authority semantics

Missing results are not zero; operational failures are not model scores; incomplete required
eval-v2 rows block normalization. Freezing this contract does not authorize evaluation, training,
HU/SSH, Slurm, artifact mutation, cleanup, push or publication.
