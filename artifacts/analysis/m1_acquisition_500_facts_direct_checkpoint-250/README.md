# Checkpoint-250 Triple-Robust Fact Freeze

This directory freezes the downstream-eligible English facts from the 500-fact
direct-supervision acquisition run.

Selection rule:

```text
exact-prefix rank 1 AND held-out direct rank 1 AND QA-matched rank 1
```

Result: 265 of 500 facts (53.0%).

Generated with implementation commit `055db5a`:

```bash
python scripts/audit_acquisition_checkpoint.py \
  --exact <checkpoint-250-exact-prefix>/per_fact_results.csv \
  --direct <checkpoint-250-direct>/per_fact_results.csv \
  --qa <checkpoint-250-qa-matched>/per_fact_results.csv \
  --train artifacts/datasets/acquisition_diagnostics_v1/all_relations_100_subjects_direct_supervision/train.jsonl \
  --validation artifacts/datasets/acquisition_diagnostics_v1/all_relations_100_subjects_direct_supervision/validation.jsonl \
  --output-dir runs/analysis/m1_acquisition_500_facts_direct_checkpoint-250_audit
```

Frozen artifact hashes:

```text
c8945ae43241624c94df92887dab9ce325b43a1003e481463b1d94f47bb10882  summary.json
b5b2ed4d25487846c7299032212942bf1b1f5303c740a07b99970248a3651bf7  triple_robust_facts.csv
```

The full 500-row `fact_audit.csv` remains with the HU run output. The compact summary and
the exact frozen membership list are versioned here.
