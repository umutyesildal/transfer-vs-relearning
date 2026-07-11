# Relation Candidates V2 Audit V3

Pinned inputs:

- candidate commit: `588e7e8`
- audit implementation commit: `9a12716`
- candidate CSV SHA-256: `0ed99c1d62a4b1045fe43ec995b094ff1b712efa1cda5897ba3afda8f0ff9026`
- model: `HuggingFaceTB/SmolLM2-360M`
- canonical Slurm job: `391100`

Launch note:

- job `391099` failed before execution because `MODEL_MANIFEST` was not exported;
- job `391100` explicitly pinned the manifest and completed successfully.

Result:

- candidates: 100
- pass: 94
- review: 6
- Turkish token-count failures: 0
- English token ranges: 1-2 for both relations
- Turkish token ranges: 1-4 for both relations

All six remaining reviews are base-prior outliers. Thresholds were unchanged.

Frozen output hashes:

```text
a5466dc748d0a5a5a3339947d0acf9a415ed568f78e525333ed7f101044935fd  summary.json
2994fd7cc7edb8890b0a0bf23695d37f59d997c17a984cb17bc3de8166430392  candidate_audit.csv
```
