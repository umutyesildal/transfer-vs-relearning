# 70 - M1 Relation V2 City-Binding Control Plan

Last updated: 2026-07-12

## Decision

Keep both `born_in` and `lives_in`. Their shared city candidate inventory is intentional and
scientifically useful: it tests whether the model binds a city to the requested relation rather
than merely retrieving any city associated with the subject.

The first Relation V2 run stored all 50 facts exactly but reached only 5/10 three-view robustness
for `lives_in`. Four failures selected the same subject's birthplace. This control tests whether
explicit symmetric relation contrast resolves that binding error without changing facts,
candidates, model capacity, exposure count, held-out prompts, or optimizer budget.

## Controlled Intervention

Source: `relation_v2_gate_v1`, canonical job `391106`.

For each of the ten `born_in` and ten `lives_in` facts, exactly three of seven training rows are
replaced:

- third declarative row;
- second QA row;
- second scaffold-free direct row.

Every replacement row contains both the subject's birthplace and residence, explicitly names
the relation distinction, and places the target answer surface last. The intervention is
symmetric: the same three template positions are replaced for both city relations.

Examples:

```text
Although Doğan Uluba currently lives in Istanbul, Doğan Uluba was born in Adana.
Question: Doğan Uluba was born in Adana. Where does Doğan Uluba currently live instead?
Answer: Istanbul
```

## Frozen Invariants

- subjects: 10;
- facts: 50;
- relations: unchanged;
- candidate inventories: unchanged;
- training rows: 350;
- rows per fact: 7;
- changed rows: 60;
- unchanged rows: 290;
- held-out validation rows: unchanged and hash-identical;
- exact-prefix and held-out evaluation prompts: unchanged;
- base model: SmolLM2-360M;
- epochs: 36;
- batch size: 50;
- optimizer updates: 252;
- learning rate: `1e-4`;
- objective: answer-only.

Frozen artifact hashes:

```text
f93773cdce47050abbf3dc6943c11418dd068aa001ad2c141b3dc4e254b9b5d0  train.jsonl
ca38016932546ed7c342c5b77e4ee2da7a44a46eda738e834a687e8f6ec621e1  manifest.json
```

## Precommitted Evaluation Gate

The baseline comparison checkpoint is Relation V2 checkpoint 125:

```text
global exact/direct/QA/overlap/triple = 50/45/46/45/45
lives_in exact/direct/QA/overlap/triple = 10/5/6/5/5
```

The control is successful only if one checkpoint satisfies all of the following:

- global aggregate gate remains passed: exact at least 45/50, direct at least 40/50,
  QA at least 40/50, and direct/QA overlap at least 35/50;
- `lives_in` exact remains 10/10;
- `lives_in` direct, QA, overlap, and triple each reach at least 8/10;
- `born_in` triple remains at least 9/10;
- each non-city relation remains at least 9/10 triple robust;
- birthplace-for-residence errors decrease from four to at most one.

Select the earliest passing checkpoint, then report the best stable plateau. If this gate passes,
the city relations remain as the deliberate hard binding pair and the project may prepare the
500-fact Relation V2 scale-up. If it fails, keep both relations but investigate objective-level
binding supervision before scaling.

## Implementation And Launch

- transfer-vs-relearning commit: `6d145c2`;
- branch: `corpus-update`;
- local focused tests: 28/28 passed;
- HU pull: fast-forwarded to `6d145c2`;
- HU focused preflight: 28/28 passed;
- frozen train SHA-256: `f93773cdce47050abbf3dc6943c11418dd068aa001ad2c141b3dc4e254b9b5d0`;
- Slurm training job: `391889`;
- initial state: `PENDING`;
- resources: one A100 80GB, 8 CPUs, 64 GB RAM;
- expected runtime after start: approximately two minutes, safe range two to five minutes;
- monitoring: no sleep process is active.

## Training Result And Evaluation Launch

Job `391889` completed successfully:

- optimizer updates: 252/252;
- runtime: 115.7 seconds;
- aggregate training loss: 0.4378;
- final held-out validation loss: 0.09264;
- canonical run timestamp: `20260712T073808Z`;
- runtime errors: none.

The validation loss is lower than the unmodified Relation V2 control's final 0.1082, but the
precommitted retrieval gate remains the decision criterion.

Eleven canonical checkpoints were submitted with the unchanged exact-prefix, held-out direct,
and QA-matched evaluator:

| Checkpoint | Evaluation job |
| ---: | ---: |
| 25 | 391899 |
| 50 | 391900 |
| 75 | 391901 |
| 100 | 391891 |
| 125 | 391892 |
| 150 | 391893 |
| 175 | 391894 |
| 200 | 391895 |
| 225 | 391896 |
| 250 | 391897 |
| 252 | 391898 |

All evaluation jobs were initially `PENDING`. Expected parallel wall time after scheduling is
approximately three to four minutes, with a safe three-to-seven minute range. No sleep monitor
is active.

All evaluation jobs subsequently completed. No checkpoint passed the precommitted gate. The
earliest stable checkpoint, 100, reached 50 exact, 45 direct, 46 QA, 44 overlap, and 44 triple;
`lives_in` remained 5/10 triple robust and unique residence-to-birthplace swaps increased from
four to five. The control is rejected. Full results are in
`71_M1_RELATION_V2_CITY_BINDING_CONTROL_EVALUATION_REPORT.md`.
