# 104 - M1 Canonical Plus Form-Diversity Remediation Result

**Date:** 2026-07-19  
**Status:** Discovery gate failed; M2/M3, seed-43 replication, and scale-up remain HOLD.

## Frozen treatment and operations

Treatment T used the Document 103 seven-row curriculum: three historical declarative rows plus
Form A and B under direct and QA scaffolds. It kept the 100-subject / 500-fact population,
3,500 rows, answer-only EOS-false recipe, seed/data-seed 42, and update-252 endpoint.

- Training preflight `409076`: PASS.
- Training `409077` on `gruenau9` A100 80GB: completed in 51m52s; 252/252 updates.
- Final model: `/vol/tmp2/yesildau/m1_canonical_form_diversity_v1/training/seed42/20260719T064019Z_m1_canonical_form_diversity_seed42_453625c6/final_model`.
- Final validation loss: `0.003113` (monitoring only; no checkpoint selection).
- Evaluation preflights `409078` and `409080`: PASS.
- First evaluator `409079` failed before scoring because it used a stale repository-local generic-corpus path. It produced no result files. Commit `350ae24` replaced it with verified scratch corpus `/vol/tmp2/yesildau/general_capability_v1/wikitext2_raw_test.jsonl`; the empty namespace was removed with `rmdir`.
- Corrected evaluator `409081` completed the frozen four-form, exact-prefix, relation-swapped, and generic suites. Stderr had no scientific/runtime error (only a Transformers deprecation notice).

All products, caches, and Slurm logs are on `/vol/tmp2`. The post-training audit found home usage at 8.0 GiB and no new experiment artifact in home.

## Results

| Precommitted gate | Treatment T result | Decision |
|---|---:|---|
| Exact-prefix | 500/500 (100%) | PASS |
| Trained A/B cells | 2,000/2,000 (100%) | PASS |
| Held-out C/D cells | 1,501/2,000 (75.05%) | FAIL; requires >=80% globally and in every relation-cell |
| Eight-cell robust intersection | 198/500 (39.6%) | FAIL; requires >=70% |
| Generic PPL | 17.198; ratio 1.080 vs frozen base PPL 15.924 | PASS; preferred <1.10 |
| Generic behavior | 30/30 generic completions correct, 0 empty, 1/30 EOS ending, no synthetic-subject intrusion | PASS |

The four-form evaluator scored 3,501/4,000 top-1 probes (87.5%). Robust intersection by relation:
born_in 46/100, field_of_study 59/100, lives_in 39/100, profession 21/100, and works_in_industry 33/100.
Every relation misses the 70/100 robustness floor.

Exact canonical acquisition was fully restored, including relation binding: born_in and lives_in were both 100% top-1 and paired relation-binding accuracy was 100%, with zero swapped-answer rate. The failed gate is therefore prompt-invariant access, not exact storage.

## Interpretation and next decision

This is Document 103's "exact recovery but held-out failure" path. Do not run seed-43 replication, paired-relation work, 500-subject scale-up, final M1, M2, or M3. Any next remediation must precommit a genuinely broader representation or objective rather than more A/B repetition. Preserve the Treatment T endpoint, manifests, evaluator outputs, and exposure audit as the evidence record.
