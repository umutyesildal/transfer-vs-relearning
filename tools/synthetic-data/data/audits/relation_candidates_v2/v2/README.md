# Relation Candidates V2 Audit V2

Pinned inputs:

- candidate commit: `bde7a88`
- audit implementation commit: `9a12716`
- candidate CSV SHA-256: `95f62231152229c42269333913c91209bf8f1017f456494f2b3cdc8492733118`
- model: `HuggingFaceTB/SmolLM2-360M`
- Slurm job: `391098`

Result:

- candidates: 100
- pass: 76
- review: 24
- field-of-study review candidates: 13
- works-in-industry review candidates: 11
- field-of-study Turkish token range: 1-6
- works-in-industry Turkish token range: 1-7

The unchanged V1 thresholds were applied. The revision improved the result by 14 candidates,
but the complete gate did not pass. Remaining flags include 13 Turkish token-count failures,
7 Turkish robust-prior-z outliers, 4 Turkish prior-share outliers, 3 English prior-share
outliers, and 1 English robust-prior-z outlier. Counts exceed 24 because some candidates have
multiple flags.

Frozen output hashes:

```text
855f156741c4b67f1a1681125970f3d8298f8e23e3ab0bb61a8532d7ba45ab0c  summary.json
bc235ae334509f9162a9cb1cde74e9356c375f0b10f852801cbc12b1b1cab84c  candidate_audit.csv
```
