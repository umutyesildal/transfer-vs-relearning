# 67 - M1 Relation V2 Assignment And Dependence Audit

Last updated: 2026-07-11

## Status

Passed. The accepted 50+50 candidate inventory was assigned to all 5,000 subjects under exact
global and per-block balance. All precommitted dependence and slice gates passed. Historical
`studied_at` and `works_at` data remains unchanged.

## Inputs

- repository: `synthetic-data-generation`;
- branch: `relation-redesign-v2`;
- accepted candidate freeze commit: `984231e`;
- profile SHA-256: `020c4daef91a25e6cc553a67241c448d2a0bb7fb23b8184d5296b55e524f455b`;
- candidate SHA-256: `22d06b989dab62e4cfe216fd7788df4b6c5d42bf2ba1f683460b635925fd2060`;
- field seed: `2026071101`;
- industry seed: `2026071102`.

## Assignment Design

The implementation is isolated in `build_relation_assignments_v2.py`. It creates a separate
assignment artifact rather than overwriting existing university/employer columns.

Hard invariants:

- 5,000 unique subjects;
- 50 `field_of_study` and 50 `works_in_industry` candidates;
- every candidate occurs exactly 100 times globally;
- every candidate occurs exactly twice in every 100-subject block;
- separate deterministic seeds;
- no semantic compatibility mapping between profession, field, or industry;
- branch, name type, name rarity, and popularity included in the dependence audit.

The final algorithm uses seeded block-capacity assignment. It balances profession and metadata
slices without consulting the meaning of any candidate. Industry assignment initially uses the
same non-semantic balancing objective and is then repaired with six deterministic swaps between
subjects in the same 100-subject block. These swaps preserve global and block candidate counts.
They reduce the only overfull field-industry cells while refusing any swap that would cross a
profession or metadata conditional-count limit.

## Iterations And Corrections

The first implementation used independent random block shuffles. Global and block counts were
exact and field-industry NMI was low, but chance concentration caused profession and metadata
conditional failures. It was rejected without changing thresholds.

The second implementation balanced field assignment and used an orthogonal industry schedule.
This made the field-industry table exactly uniform, but constrained industry placement enough
to retain profession/slice failures. A deterministic shift search improved but did not eliminate
them, so that design was also rejected.

The accepted implementation starts from direct seeded balancing. It already passed profession
and metadata gates; only four field-industry cells exceeded the discrete conditional limit.
Six within-block label swaps repaired those cells. The resulting 2,500 field-industry pairs all
remain represented, with counts between one and three.

## Gate Contract

- normalized mutual information: at most 0.05;
- Cramer's V: at most 0.10;
- conditional candidate count:

```text
count <= ceil(1.5 * row_total * marginal_probability)
```

The ceiling is the precommitted small-sample tolerance. A raw probability ratio can therefore
exceed 1.5 for a small conditioning group even when one additional observation is the smallest
representable increment. Raw contingency tables are retained so this behavior is inspectable.

## Primary Results

| Pair | NMI | Cramer's V | Conditional gate |
| --- | ---: | ---: | --- |
| profession x field | 0.00337 | 0.03056 | pass |
| profession x industry | 0.00396 | 0.03374 | pass |
| field x industry | 0.00225 | 0.01852 | pass |
| industry x field | 0.00225 | 0.01852 | pass |

All branch, name-type, name-rarity, and popularity pair audits pass. Global balance, all fifty
100-subject block checks, and the complete dependence gate pass.

## Verification

- complete local test suite: 53/53 passed;
- real 5,000-subject assignment run: passed;
- assignment implementation commit: `0da69cf`;
- cross-Python metric serialization commit: `e13e182`;
- both commits pushed to `origin/relation-redesign-v2`;
- HU checkout: `e13e182`;
- HU verbose test suite: 53/53 passed;
- HU real assignment builder: passed;
- local/HU assignment, summary, and contingency hashes: exact match;
- subjects: 5,000;
- field-industry pair cells observed: 2,500/2,500;
- field-industry cell range: 1-3;
- industry repair swaps: 6.

Frozen hashes:

```text
cf90f80b98534b4cea02f36d7a2ae452b4f182019d30511da1a6275c7a8a0df6  data/relation_assignments_v2.csv
8a309fd073bffc70fe75e39a6989488ceb28526e038a62ef97fc99e5f701601e  data/audits/relation_assignments_v2/v1/summary.json
412b63652530d3bb48693a2a1d514604002f1abae9f843e51966bb154ad20096  data/audits/relation_assignments_v2/v1/contingency_tables.csv
```

The first combined HU test/builder command hit the SSH helper's 30-second silence timeout
during the test suite. This was not treated as a pass or failure. The test suite was rerun in
verbose mode and passed 53/53; the builder/hash check was then run separately. Initial summary
hashes differed only in final floating-point digits between local Python and HU Python. Commit
`e13e182` pins NMI/Cramer's V serialization to 12 decimals, after which all hashes matched.

## Decision

The assignment/dependence gate is passed. The next stage may regenerate the five-relation V2
dataset and its English/Turkish training/probe artifacts under a new version name. It must not
overwrite historical `synthetic_v1` outputs. The first training gate remains 10 subjects / 50
facts before any return to the 500-fact level.
