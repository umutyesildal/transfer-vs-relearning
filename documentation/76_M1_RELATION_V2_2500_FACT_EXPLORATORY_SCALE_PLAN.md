# 76 - M1 Relation V2 2,500-Fact Exploratory Scale Plan

Last updated: 2026-07-12

## Explicit Override

The canonical 500-fact progression gate did not pass: checkpoint 250 reached 500 exact, 378
direct, 377 QA, and 329 overlap against a 450/400/400/350 gate. This history remains unchanged.

The user explicitly approved proceeding to 2,500 facts because Relation V2 materially improved
over V1 and achieved perfect storage. This run is therefore labeled an exploratory scale override,
not a retroactive gate pass.

## Frozen Dataset

- subjects: 500;
- facts: 2,500;
- facts per relation: 500;
- train rows: 17,500;
- train rows per fact: 7;
- held-out validation rows: 2,500;
- exact-prefix probes: 2,500;
- branch x name-type allocation: 125 subjects per cell;
- nesting: complete 100-subject scale set included;
- relations: `profession`, `born_in`, `lives_in`, `field_of_study`, `works_in_industry`;
- city candidate inventory: unchanged and shared by `born_in` / `lives_in`;
- historical `studied_at` / `works_at`: absent.

Frozen hashes:

```text
16f059eeb42d52baf27a8abd9ce83bf08662a849116214546ab62403b57d7576  train.jsonl
738a71eedd6b5e782279900122b3f6f3066980db0f21ac1d93b79615c09d24c1  validation.jsonl
34aafdfb0e229817977f51eef34aad129156da920cae4786a85bcb602e2c9533  exact_prefix_probes_en.csv
6bbb3bdad0f35b53084715e76e50113b53f276d72ffbef48da30c54398fa26ed  summary.json
```

## Matched Recipe

- start from base SmolLM2-360M;
- objective: answer-only CLM;
- learning rate: `1e-4`;
- epochs: 36;
- micro-batch: 50;
- gradient accumulation: 50;
- effective batch: 2,500;
- expected optimizer updates: 252;
- scheduler: constant with warmup;
- weight decay: 0;
- no failed paired-city or hard-negative checkpoint is reused.

This preserves seven optimizer updates per epoch, 36 exposures per row, and 252 total updates.

## Exploratory Evaluation Gate

The proportional 90/80/80/70 thresholds are frozen before training:

- exact at least 2,250/2,500;
- direct at least 2,000/2,500;
- QA at least 2,000/2,500;
- direct/QA overlap at least 1,750/2,500.

These thresholds guide interpretation but do not rewrite the failed canonical 500-fact gate.
Evaluation is staged at checkpoints 25/50/75 first due the larger cost. Report all relations,
nested-100 retention, and both city-swap directions.

## Provenance

- synthetic-data-generation commit: `ec2b96a`;
- synthetic full suite: 59/59 passed;
- release manifest SHA-256: `94df56dba548c81d39b03b7b7fe4f9a59d9555997e984fd7aed5cabd0a113425`.

## Transfer Integration And Launch

- transfer-vs-relearning commit: `43f801c`;
- transfer focused local suite: 38/38 passed;
- HU focused preflight: 38/38 passed;
- nesting and row-count audit: passed;
- local/HU artifact hashes: exact match;
- Slurm training job: `392293`;
- initial state: `PENDING`;
- resource: one A100 80GB;
- expected runtime: approximately 48 minutes;
- safe runtime range: 40-70 minutes;
- monitoring: no sleep process is active.

## Training Result And Initial Evaluation Wave

Training job `392293` completed successfully:

- optimizer updates: 252/252;
- runtime: 2,590 seconds (43.2 minutes);
- aggregate training loss: 0.9441;
- final held-out validation loss: 0.8760;
- OOM/runtime errors: none;
- canonical run timestamp: `20260712T142505Z`.

The precommitted first checkpoint wave was submitted:

| Checkpoint | Evaluation job | Initial state |
| ---: | ---: | --- |
| 25 | 392728 | RUNNING |
| 50 | 392729 | RUNNING |
| 75 | 392730 | PENDING |

Each job evaluates 2,500 exact-prefix, 2,500 held-out direct, and 2,500 QA-matched probes.
Expected parallel wall time is approximately 30 minutes, with a safe 25-45 minute range including
queue delay. No sleep monitor is active.

## Initial Checkpoint Results

Jobs `392728` through `392730` completed without evaluation failures:

| Checkpoint | Exact | Direct | QA | D/Q overlap | Triple | Gate |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 25 | 43 | 37 | 52 | 9 | 7 | fail |
| 50 | 76 | 61 | 74 | 38 | 21 | fail |
| 75 | 261 | 224 | 224 | 134 | 78 | fail |

The initial curve is far below the exploratory 2,250/2,000/2,000/1,750 thresholds but rises
consistently. Compared with the 500-fact run, acquisition begins later under the five-times-denser
binding load. This warrants the precommitted middle checkpoint wave.

| Checkpoint | Evaluation job | Initial state |
| ---: | ---: | --- |
| 100 | 393009 | PENDING |
| 125 | 393010 | PENDING |
| 150 | 393011 | PENDING |

Expected parallel wall time remains approximately 30 minutes, with a safe 25-45 minute range.
No sleep monitor is active.

## Late Checkpoint Results

Jobs `393012` through `393014` completed without evaluation failures:

| Checkpoint | Exact | Direct | QA | D/Q overlap | Triple | Gate |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 175 | 2,326 | 1,143 | 1,203 | 868 | 843 | fail |
| 200 | 2,481 | 1,207 | 1,265 | 925 | 923 | fail |
| 225 | 2,497 | 1,232 | 1,294 | 936 | 935 | fail |

Exact storage is nearly complete by checkpoint 225, but prompt robustness remains far below the
exploratory 2,000/2,000/1,750 thresholds and is approaching a plateau. The final two checkpoints
are required to close the curve, not because a gate pass is currently plausible.

| Checkpoint | Evaluation job | Initial state |
| ---: | ---: | --- |
| 250 | 393015 | PENDING |
| 252 | 393016 | PENDING |

Expected parallel wall time is approximately 30 minutes with a safe 25-45 minute range. No sleep
monitor is active.

Both final jobs completed without evaluation failures. Checkpoint 250 reached 2,498 exact, 1,253
direct, 1,301 QA, 954 overlap, and 953 triple. Checkpoint 252 reached 2,498/1,249/1,293/958/957
and is selected by the primary overlap/triple criterion. The exploratory gate fails. Full results
and the no-full-scale decision are in
`77_M1_RELATION_V2_2500_FACT_EXPLORATORY_EVALUATION_REPORT.md`.

## Middle Checkpoint Results

Jobs `393009` through `393011` completed without evaluation failures:

| Checkpoint | Exact | Direct | QA | D/Q overlap | Triple | Gate |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 100 | 751 | 545 | 572 | 378 | 275 | fail |
| 125 | 1,341 | 837 | 882 | 608 | 497 | fail |
| 150 | 1,912 | 1,009 | 1,080 | 768 | 707 | fail |

The curve remains strongly positive through checkpoint 150 and exact storage has not saturated.
The exploratory gate remains distant, but a late wave is necessary before any capacity or plateau
conclusion.

| Checkpoint | Evaluation job | Initial state |
| ---: | ---: | --- |
| 175 | 393012 | RUNNING |
| 200 | 393013 | PENDING |
| 225 | 393014 | PENDING |

Expected parallel wall time remains approximately 30 minutes with a safe 25-45 minute range.
No sleep monitor is active.
