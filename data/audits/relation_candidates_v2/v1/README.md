# Relation Candidates V2 Audit V1

Pinned inputs:

- candidate commit: `85badbb`
- audit implementation commit: `9a12716`
- candidate CSV SHA-256: `022dad5f0068cd763a49d225340bda2537da08d0c5433183855d311409a1fc62`
- model: `HuggingFaceTB/SmolLM2-360M`
- Slurm job: `391097`

Result:

- candidates: 100
- pass: 62
- review: 38
- field-of-study English token range: 1-2
- industry English token range: 1-2
- field-of-study Turkish token range: 1-9
- industry Turkish token range: 1-10

Review flags are precommitted and were not relaxed after observing the result. Most flags are
Turkish token-length failures. The candidate draft must be revised and rerun under the same
thresholds before assignment.

Frozen output hashes:

```text
018bb52e0f16b7b707d26e2dd0e53fd26a7a7d6c2b9935167c1ec95e53b451c1  summary.json
85c901b9044d0731c9b90fe80d5070d9cf312d53b28e31c0dbc63c6971df0819  candidate_audit.csv
```
