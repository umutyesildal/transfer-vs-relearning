# Pile-10k Retirement and eval-v2 Decision — 2026-08-22

**Status:** accepted prospective protocol change

**Execution authority:** none

**Effective boundary:** before M1 training and before any M1/M2 scientific result exists

## Decision

Pile-10k is retired from the canonical M0/M1/M2-A/M2-B evaluation protocol. It is not a required
task, retention gate, submission lane, normalization denominator, dashboard metric or blocker in
`eval-v2`.

The frozen and already executed `eval-v1` contract, configs, job records and raw Pile artifacts
remain immutable historical evidence. OLMo and SmolLM Pile observations are retained as
exploratory results; the failed or missing Qwen Pile attempts remain operational evidence. None of
them may be used for canonical cross-model ranking or state gates.

## Rationale

1. The thesis estimands concern factual acquisition, cross-lingual transfer/relearning and
   language-retention effects. Pile-10k adds only a secondary broad-domain English control.
2. WikiText BPB already provides the frozen primary English retention signal. BLiMP and HellaSwag
   provide separate English capability controls.
3. The three models expose different native maximum contexts (OLMo 4,096; SmolLM 8,192; Qwen
   131,072). The prior Harness configuration inherited those model-specific limits, so raw Pile BPB
   values were not a clean equal-context cross-model estimand.
4. Qwen's full Pile lane repeatedly encountered pre-scoring resource failures, including a
   post-forward logits/log-softmax memory peak. Turning that operational workaround into a new
   scientific context policy would add complexity without resolving a thesis-critical measurement.
5. This retirement is prospective: it is fixed before M1 training and therefore cannot be selected
   in response to M1/M2 scientific outcomes.

## eval-v2 active English panel

- WikiText-2 raw BPB and absolute delta to the frozen parent: primary English retention gate;
- BLiMP accuracy: English grammar capability gate;
- HellaSwag `acc_norm`: English commonsense capability gate;
- WinoGender female/male/neutral slices: diagnostic only.

All factual, Turkish, generation-integrity, uncertainty, exact-prefix, checkpoint and M2 sibling
rules from eval-v1 remain unchanged unless the eval-v2 contract explicitly says otherwise.

## M0 transition rule

The three already completed non-Pile lanes per model are retained by immutable path and SHA-256.
The canonical eval-v2 M0 panel therefore has `21/21` standard/project lanes available without
rescoring (`7` per model), plus the separately completed three-model exact-prefix supplement.
Creating a normalized comparison artifact from those retained results is a separate local,
hash-closed operation; this decision does not itself execute normalization.

## Prohibitions

- no deletion or mutation of historical Pile artifacts, configs, contracts or records;
- no Qwen Pile retry;
- no substitution with an outcome-aware broad-domain corpus;
- no claim that retired Pile observations are comparable canonical scores;
- no training, evaluation, HU synchronization, Slurm submission, cleanup or publication granted by
  this decision.
