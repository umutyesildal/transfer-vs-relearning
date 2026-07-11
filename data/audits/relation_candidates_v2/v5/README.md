# Relation Candidates V2 Audit V5

Pinned inputs:

- candidate commit: `f898f95`
- audit implementation commit: `9a12716`
- candidate CSV SHA-256: `f3d5c133e0f7d44c2661c8b78b0833f5454ec5f7bdc80cd5e2349fd3a720f276`
- model: `HuggingFaceTB/SmolLM2-360M`
- Slurm job: `391102`

Result:

- candidates: 100
- pass: 97
- review: 3
- field-of-study reviews: `didactics`, `exercise science`
- works-in-industry review: `agribusiness`

`agribusiness` reached English prior share 0.832 and triggered both English prior thresholds.
Its three-token representation appears advantaged by mean token log-probability, so the next
revision returns to a single-token surface. Thresholds remain unchanged.

Frozen output hashes:

```text
08a40e6992f17cf1f810bb11765495703be0b39ce8755e88eabd65acc2b2ecd3  summary.json
bc60dbefbfe7447b19bad649fe4953698fc7a55114fa36edf53950c4f2e8016c  candidate_audit.csv
```
