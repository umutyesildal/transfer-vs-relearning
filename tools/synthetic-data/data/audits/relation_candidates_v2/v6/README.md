# Relation Candidates V2 Audit V6

Pinned inputs:

- candidate commit: `9499cda`
- audit implementation commit: `9a12716`
- candidate CSV SHA-256: `c2ac751219d6cecaca7e107f91455e08aa7da8c80750f26b1a111ca0aa434b8b`
- model: `HuggingFaceTB/SmolLM2-360M`
- Slurm job: `391103`

Result:

- candidates: 100
- pass: 99
- review: 1
- only review: English `industrial goods` in `works_in_industry`
- flag: English prior share 0.152 above the unchanged 0.10 limit

All field-of-study candidates and all token-length and robust-z checks passed.

Frozen output hashes:

```text
0c81629c9b48a509ba8d7902edd0f20fd3c6706fdc4a2d2441e80bad0904a959  summary.json
3cfb3aff7a4e9b68e5b19246989c945e0294c8c1a95d5f55e30be052d57b5d9e  candidate_audit.csv
```
