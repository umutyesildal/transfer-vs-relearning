# 79 - M1 Relation V2 Relation-Conditioned Retrieval Plan

Last updated: 2026-07-12
Status: training submitted

## Decision

The canonical development scale remains Relation V2 at 100 subjects / 500 facts. The selected
starting point is the clean job `391918` checkpoint 250, which stores 500/500 exact facts but
retrieves only 329/500 facts robustly. The exploratory 2,500-fact result is retained as evidence of
scale-dependent retrieval interference; the project does not scale to 25,000 facts with the
current recipe.

## Hypothesis

Previous ranking continuations were ineffective because the model already separated candidates
on their seen training prompts. They supplied no new signal for transferring relation semantics
to held-out prompt forms. The new intervention therefore combines unseen training paraphrases,
explicit relation wording, same-relation candidate discrimination, and mandatory same-subject
city negatives.

## Frozen Inputs

- model: SmolLM2-360M;
- starting checkpoint: clean Relation V2 job `391918`, checkpoint 250;
- subjects/facts: 100 / 500;
- relation definitions and candidate inventories: unchanged;
- external exact, held-out direct, and held-out QA probes: unchanged and excluded from training;
- score: mean answer log probability;
- seed: 42.

## Controlled Intervention

Three new relation-explicit prompt templates are generated for every fact. None is copied from the
external held-out validation probe. This creates 1,500 ranking examples, 300 per relation. Each
example compares the correct answer against 15 deterministic same-family negatives. For
`born_in` and `lives_in`, the same subject's object from the other city relation is always one of
the negatives.

Training starts from the stored checkpoint rather than the base model:

- learning rate: `5e-6`;
- epochs: 1;
- effective example batch: 10;
- expected optimizer updates: 150;
- scheduler: constant with 5% warmup;
- weight decay: 0;
- checkpoint interval: every 15 updates, yielding checkpoints 15 through 150.

## Leakage Rule

The relation-conditioned templates are authored before evaluation and use only canonical subject,
relation, and answer fields from the training artifact. The external held-out direct/QA questions,
their errors, and checkpoint-250 predictions are not read by the builder. The intervention is
therefore evaluation-aware at the task level but not adapted to individual held-out errors.

## Precommitted Gate

A checkpoint is promoted only if all conditions hold:

- exact at least 495/500;
- direct at least 400/500;
- QA at least 400/500;
- direct/QA overlap and triple robustness at least 350/500;
- no relation loses more than five triple-robust facts relative to clean checkpoint 250;
- residence-to-birthplace and birthplace-to-residence swaps are both reported;
- the result is reproduced with at least one additional seed before final M1 freezing.

The earliest passing checkpoint and the best stable checkpoint are reported separately. A run
that improves direct/QA while damaging exact storage below 495 is rejected.

## Decision After The Run

- Pass: repeat the identical intervention with a second seed, then freeze the M1 learned-fact list.
- Partial improvement: run one precommitted learning-rate control, without changing templates or
  candidates after inspecting individual errors.
- Neutral/regression: reject the continuation and redesign the objective at the 500-fact scale;
  do not return to exposure-only scaling and do not launch 25,000 facts.

## Implementation And Launch

- transfer-vs-relearning commit: `def71ad`;
- branch: `corpus-update`;
- local focused tests: 34/34 passed;
- HU focused tests: 34/34 passed;
- real-data preflight: 1,500 examples, 500 facts, 300 examples per relation, 16 candidates each;
- canonical base: clean job `391918`, checkpoint 250;
- Slurm job: `393017`;
- node: `gruenau9`;
- first observed state: `RUNNING`;
- observed start: 2026-07-12 21:07:35 CEST;
- expected training duration: approximately 5-6 minutes;
- safe runtime range: 4-10 minutes;
- monitoring policy: no local sleep process; evaluate after a later explicit check.

## Training Result

Job `393017` completed 150/150 optimizer updates without a runtime error. The trainer wrote ten
checkpoints at 15-update intervals from checkpoint 15 through checkpoint 150. External evaluation
is required before interpreting the ranking loss; the configured validation split is empty, so
logged zero validation values are placeholders rather than scientific results.

## Evaluation Launch

All ten checkpoints are submitted under the unchanged three-view evaluator:

- checkpoint 15: job `393022`;
- checkpoint 30: job `393023`;
- checkpoint 45: job `393024`;
- checkpoint 60: job `393025`;
- checkpoint 75: job `393026`;
- checkpoint 90: job `393027`;
- checkpoint 105: job `393018`;
- checkpoint 120: job `393019`;
- checkpoint 135: job `393020`;
- checkpoint 150: job `393021`.

At the first queue check, six jobs were running across `gruenau9` and `gruenau10`; four remained
pending for resources or priority. Each job evaluates exact-prefix, held-out direct, and held-out
QA sequentially over all 500 facts. Expected wall time for the complete wave is approximately
12-18 minutes, with a safe 12-25 minute range. No sleep monitor is active.
