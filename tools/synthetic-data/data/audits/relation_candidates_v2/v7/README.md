# Relation Candidates V2 Audit V7 - Final

Pinned inputs:

- candidate commit: `351cae5`
- audit implementation commit: `9a12716`
- candidate CSV SHA-256: `22d06b989dab62e4cfe216fd7788df4b6c5d42bf2ba1f683460b635925fd2060`
- model: `HuggingFaceTB/SmolLM2-360M`
- Slurm job: `391104`

Final result:

- candidates: 100
- pass: 100
- review: 0
- `field_of_study`: 50/50 accepted
- `works_in_industry`: 50/50 accepted
- English token ranges: 1-2 for fields, 1 for industries
- Turkish token ranges: 2-4 for both relations
- maximum absolute robust z-score: below 3.5 in every relation/language slice
- maximum prior share: below 0.10 in every relation/language slice

All precommitted thresholds were kept unchanged. This V7 inventory is the accepted candidate
set for independent balanced assignment and dependence auditing.

Frozen output hashes:

```text
9c01365bd20e37723d8ac4e4fb17231b490872ff88db7415ecd3a1fca274b8fc  summary.json
2d2a231b1bee9beab84eb3b4796e4f4dd9411d8290dbcc65bbea4763f1a2a070  candidate_audit.csv
```
