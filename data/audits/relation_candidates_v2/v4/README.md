# Relation Candidates V2 Audit V4

Pinned inputs:

- candidate commit: `54f0397`
- audit implementation commit: `9a12716`
- candidate CSV SHA-256: `86396743bfd51c04578b3de68e87186b755abee1042126e9fc64cac02b6565a7`
- model: `HuggingFaceTB/SmolLM2-360M`
- Slurm job: `391101`

Result:

- candidates: 100
- pass: 96
- review: 4
- English prior-share reviews: 3
- Turkish token-count reviews: 1

The unchanged thresholds were applied. Removing earlier dominant candidates exposed the next
highest English base-prior candidates through the precommitted within-relation softmax audit.

Frozen output hashes:

```text
1c551076e1d82304e711c4b3e365776cacd8474145fd9f81f934cd3c864e9e19  summary.json
a3a66111a9015a74f34c51664055d59531e07d2bc553a46e05745b6ae865d2d5  candidate_audit.csv
```
