# 56 - M1 All-Relations 50-Fact Direct-Supervision Plan

Last updated: 2026-07-11

## Decision

The direct-aware recipe achieved perfect exact, direct, and QA retrieval for ten `born_in`
facts. This level increases only relation diversity and binding count: all five relations for
the same ten subjects.

## Controlled Scope

- subjects: 10
- relations: `profession`, `born_in`, `lives_in`, `studied_at`, `works_at`
- facts: 50
- rows per fact: 7
- train rows: 350
- held-out direct validation rows: 50
- exact train/validation text overlap: 0
- model: base SmolLM2-360M
- candidate inventories: complete relation-specific inventories

The model starts from the base checkpoint, not from a previous diagnostic run.

## Matched Budget

- epochs: 36
- batch size: 50
- optimizer steps: 252
- learning rate: `1e-4`
- scheduler: constant with warmup
- answer-only loss
- no weight decay
- block size: 128

Every row is seen 36 times, matching the successful 10-fact run. Increasing batch size keeps
the optimizer-update count fixed while increasing bindings from 10 to 50.

## Precommitted Gate

A checkpoint passes only if all conditions hold:

- exact-prefix top-1 at least 45/50;
- held-out direct top-1 at least 40/50;
- held-out QA top-1 at least 40/50;
- direct/QA top-1 overlap at least 35/50.

Select the earliest passing checkpoint. Report each relation separately over its ten facts.

Interpretation:

- pass: direct-aware acquisition handles relation diversity at 50 facts; proceed to the
  nested 100-subject / 500-fact level with the same format contract;
- relation-specific failure: investigate relation templates/candidate inventory before scale;
- global degradation: binding interference appears between 10 and 50 facts;
- exact succeeds but prompt views fail: format extraction becomes unstable under relation
  diversity.

Do not launch 500 facts until this gate is evaluated and documented.

