# Relation Assignments V2 Audit V1 - Accepted

Pinned inputs:

- profile SHA-256: `020c4daef91a25e6cc553a67241c448d2a0bb7fb23b8184d5296b55e524f455b`
- candidate SHA-256: `22d06b989dab62e4cfe216fd7788df4b6c5d42bf2ba1f683460b635925fd2060`
- field seed: `2026071101`
- industry seed: `2026071102`

Assignment contract:

- 5,000 subjects;
- 50 field candidates and 50 industry candidates;
- each candidate occurs exactly 100 times globally;
- each candidate occurs exactly twice in every 100-subject block;
- no profession-field, profession-industry, or field-industry compatibility mapping;
- six deterministic within-block industry-label repair swaps;
- all 2,500 field-industry pairs observed between one and three times.

Primary dependence results:

| Pair | NMI | Cramer's V | Conditional gate |
| --- | ---: | ---: | --- |
| profession x field | 0.00337 | 0.03056 | pass |
| profession x industry | 0.00396 | 0.03374 | pass |
| field x industry | 0.00225 | 0.01852 | pass |

All branch, name-type, name-rarity, and popularity slice gates also pass. The conditional gate
uses the precommitted discrete tolerance:

```text
count <= ceil(1.5 * row_total * marginal_probability)
```

Consequently, raw probability ratios can exceed 1.5 for small conditioning groups even when
the smallest representable count remains within the documented tolerance. The complete raw
tables are preserved in `contingency_tables.csv`.

Frozen output hashes:

```text
cf90f80b98534b4cea02f36d7a2ae452b4f182019d30511da1a6275c7a8a0df6  relation_assignments_v2.csv
8a309fd073bffc70fe75e39a6989488ceb28526e038a62ef97fc99e5f701601e  summary.json
412b63652530d3bb48693a2a1d514604002f1abae9f843e51966bb154ad20096  contingency_tables.csv
```

Result: accepted. Dataset regeneration may proceed without overwriting historical V1 data.
