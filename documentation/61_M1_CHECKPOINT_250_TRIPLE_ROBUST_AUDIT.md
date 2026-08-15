# 61 - M1 Checkpoint-250 Triple-Robust Audit

Last updated: 2026-07-11

## Purpose

This report freezes and audits the English facts learned robustly by the 500-fact
direct-supervision M1 acquisition run. Checkpoint 250 was selected because it had the
strongest final direct/QA overlap and QA score.

## Reproducibility

- audit implementation commit: `055db5a`
- source checkpoint: `checkpoint-250`
- source facts: 500 across 100 subjects and five relations
- frozen rule: exact-prefix rank 1 AND held-out direct rank 1 AND QA-matched rank 1
- HU audit directory:
  `runs/analysis/m1_acquisition_500_facts_direct_checkpoint-250_audit`
- versioned artifact directory:
  `artifacts/analysis/m1_acquisition_500_facts_direct_checkpoint-250`

The audit tool validates identical fact-id sets and stable metadata across all three views.
It fails closed on duplicates, missing facts, or answer/relation/subject metadata drift.

## Frozen Result

| Measure | Count | Rate |
|---|---:|---:|
| exact-prefix top-1 | 451/500 | 90.2% |
| held-out direct top-1 | 317/500 | 63.4% |
| QA-matched top-1 | 349/500 | 69.8% |
| direct and QA top-1 | 277/500 | 55.4% |
| exact, direct, and QA top-1 | **265/500** | **53.0%** |

The frozen CSV contains 265 data rows plus one header row. Its SHA-256 is
`b5b2ed4d25487846c7299032212942bf1b1f5303c740a07b99970248a3651bf7` after LF
line-ending normalization for version control.

## Relation Audit

| Relation | Facts | Exact | Direct | QA | Triple robust | Rate |
|---|---:|---:|---:|---:|---:|---:|
| `profession` | 100 | 100 | 90 | 92 | 85 | 85% |
| `lives_in` | 100 | 100 | 77 | 87 | 74 | 74% |
| `born_in` | 100 | 100 | 64 | 67 | 53 | 53% |
| `studied_at` | 100 | 82 | 47 | 56 | 29 | 29% |
| `works_at` | 100 | 69 | 39 | 47 | 24 | 24% |

The global failure is not evenly distributed. `profession` is robust, while `studied_at`
and `works_at` account for most missing triple-robust facts.

## Balance Audit

| Slice | Triple robust | Rate |
|---|---:|---:|
| Branch A | 130/250 | 52.0% |
| Branch B | 135/250 | 54.0% |
| English-like names | 136/250 | 54.4% |
| Turkish-like names | 129/250 | 51.6% |
| Common names | 93/165 | 56.4% |
| Medium-rarity names | 83/165 | 50.3% |
| Rare names | 89/170 | 52.4% |

There is no material Branch A/B or English-like/Turkish-like imbalance. High-frequency
objects are stronger at 68.8% triple robust than low-frequency objects at 50.4%, which is
consistent with an object-frequency or candidate-prior effect.

All 100 subjects have at least one triple-robust fact. Only five subjects have all five facts
triple robust: `S00842`, `S01037`, `S01171`, `S01804`, and `S03638`.

## Error Diagnosis

The weak relations show concentrated candidate collapse:

- `studied_at` direct errors predict `19 Mayis Universitesi` in 48 of 53 failures;
- `studied_at` QA errors predict the same candidate in 42 of 44 failures;
- `works_at` direct errors predict `3M` in 44 of 61 failures;
- `works_at` QA errors predict `3M` in 49 of 53 failures.

Most misses are still near the top of the candidate ranking. For `studied_at`, 42 of 53
direct misses and 39 of 44 QA misses are ranks 2-5. For `works_at`, 41 of 61 direct misses
and 43 of 53 QA misses are ranks 2-5. This indicates that many correct facts remain
competitive, but a strong relation-level candidate prior overrides subject-specific binding.

City binding is also incomplete outside the exact-prefix view. The correct city outranks the
paired alternative city for 200/200 exact-prefix facts, 153/200 direct facts, and 163/200 QA
facts.

## Leakage And Integrity

- exact-prefix normalized prompt matches in training: 500/500, expected by design;
- held-out direct normalized prompt matches in training: 0/500;
- QA-matched normalized prompt matches in training: 0/500;
- candidate inventory sizes are stable within every relation;
- input and frozen-output SHA-256 hashes are recorded in `summary.json`.

The held-out direct and QA results are therefore not explained by exact prompt duplication.

## Decision

The checkpoint-250 triple-robust subset is frozen for analysis, but the recipe is not promoted
to 2,500 facts. The next controlled experiment must remain at 500 facts and target
subject-object discrimination in `studied_at` and `works_at`, rather than merely adding more
epochs to the unchanged recipe.
