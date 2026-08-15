# 65 - M1 Relation Replacement Decision And Data Plan

Last updated: 2026-07-11

## Decision

Keep five relations, but replace the two proper-name relations that failed reliable English
acquisition:

```text
studied_at -> field_of_study
works_at   -> works_in_industry
```

The retained relation set is `profession`, `born_in`, `lives_in`, `field_of_study`, and
`works_in_industry`. Historical `studied_at` and `works_at` artifacts remain archived as
negative evidence; they are not silently deleted.

## Source Taxonomies

Candidate concepts are adapted from official classifications:

- UNESCO UIS ISCED Fields of Education and Training 2013:
  https://uis.unesco.org/en/files/isced-fields-education-and-training-2013-en-pdf
- Eurostat NACE Rev. 2.1 overview and 2025 manual:
  https://ec.europa.eu/eurostat/web/nace
  https://ec.europa.eu/eurostat/web/products-manuals-and-guidelines/w/ks-gq-24-007

The official category is retained with every candidate. Labels are simplified into short
English/Turkish answer surfaces for the synthetic task.

## Why These Replacements

`field_of_study` preserves an education relation using disciplines such as `physics` or
`history`. `works_in_industry` preserves an employment relation using sectors such as
`banking` or `aviation`. This reduces rare proper-name tokenization, punctuation/acronym
effects, heterogeneous entity inventories, and universities-as-employers ambiguity.

Short tokenization alone is insufficient: `3M` was short but became a dominant prior. The new
design therefore combines token constraints with balanced assignment and base-prior screening.

## Candidate Contract

The initial sourced draft contains 50 candidates per new relation at:

```text
syntheticFacts/data/relation_candidates_v2.csv
```

Acceptance requirements:

- unique normalized English and Turkish surfaces within each relation;
- no digits, abbreviations, parentheses, or decorative punctuation;
- target English length: 1-3 pinned SmolLM2 answer tokens;
- target Turkish length: 1-4 pinned SmolLM2 answer tokens;
- no extreme relation-only base-model prior;
- source taxonomy/category retained for traceability.

The draft is not approved for generation until tokenizer and prior audits pass.

## Independent And Balanced Assignment

The new facts must not be inferable from `profession` or from each other:

1. Use separate deterministic seeded permutations for field and industry.
2. Each candidate occurs exactly 100 times globally: 5,000 / 50.
3. Within every 100-subject diagnostic block, each candidate occurs exactly twice.
4. Preserve Branch A/B, name type, rarity, and popularity balance.
5. Do not map profession categories to semantically compatible fields or industries.
6. Do not map fields to semantically compatible industries.
7. The assignment algorithm must not use compatibility rules.

The lack of semantic compatibility is intentional: the experiment must test stored
subject-object binding rather than commonsense inference.

## Dependence Audit

Before promotion, report contingency tables for profession-category x field,
profession-category x industry, and field x industry, plus:

- normalized mutual information;
- Cramer's V;
- maximum conditional candidate probability;
- global and per-100-subject candidate counts;
- Branch/name/rarity/popularity slice counts.

Precommitted targets:

- normalized mutual information at most 0.05;
- Cramer's V at most 0.10;
- no conditional candidate probability above 1.5 times its marginal probability, with a
  documented small-sample tolerance;
- exact global and diagnostic-block balance.

Raw contingency tables must remain visible when a summary statistic is unstable or undefined.

## Tokenizer And Prior Audit

Use the exact pinned SmolLM2-360M tokenizer with the leading answer separator used in
evaluation. Record English/Turkish token IDs and lengths for every candidate.

Before assignment, score candidates under subject-free relation-only null prompts. Reject or
revise extreme prior outliers. Because this occurs before fact assignment and training, no
held-out fact result can influence candidate selection.

## Generation Order

1. Freeze the sourced 50+50 candidate draft.
2. Run lexical, tokenizer, and base-prior audits.
3. Record every rejected/replaced candidate.
4. Implement independent balanced assignment and dependence metrics.
5. Generate a new dataset version without overwriting `synthetic_v1`.
6. Regenerate English/Turkish training and probes.
7. Run 10-subject/50-fact acquisition first.
8. Promote to 100-subject/500-fact only after the small gate passes.
9. Keep 2,500-fact scale blocked until the new 500-fact gate passes.

## Repository Isolation

Work is isolated on the `syntheticFacts` branch `relation-redesign-v2`. Existing untracked
generated outputs from the prior branch are preserved and excluded from this change set.
