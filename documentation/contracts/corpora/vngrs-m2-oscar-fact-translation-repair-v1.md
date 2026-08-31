# vngrs M2 OSCAR fact-translation block repair v1

**Date:** 2026-08-31  
**Lifecycle:** `FROZEN / UNEXECUTED / SINGLE CPU M2-B REPAIR WAVE`  
**Contract ID:** `vngrs-m2-oscar-fact-translation-repair-v1`

## Purpose

The all-250 Branch-B human review returned 243 `usable` and seven `issue` verdicts. Source-value
comparison resolved three issue rows as correct unchanged Turkish (`computing -> bilişim` and two
`ecology -> ekoloji`) and approved four exact translation corrections:

| Fact | Old | Corrected |
|---|---|---|
| `S00634_field_of_study` | `didaktik` | `öğretmenlik` |
| `S00971_works_in_industry` | `refah` | `sosyal hizmetler` |
| `S02929_field_of_study` | `sosyal` | `kültürel analiz` |
| `S03025_field_of_study` | `hareket` | `egzersiz bilimi` |

The canonical source CSV, original registry, original decisions, predecessor block family and all
earlier HU roots remain immutable/read-only. The correction is an explicit overlay.

## Frozen local evidence

```text
overlay                           f9e1d7028e948cd3bc4cd43a7e8ad264b6800d2c673df79c701d4fd0f9f1b27d
base registry reproduction       784f78a5a182c329b4b995ee1a97c580da994059a18b1f9702ec657569ccbfec
corrected registry               46a1071d228758013d73fae4ab3925538523eb338001e00bde9d5fe178f1c4a2
corrected review packet          7dea022ba728d0b2aab3a43b5e1074eda18686cf56666e9f87246607760fbccf
corrected decisions              3af9fa0356392ea55a99b962a61453385cbefbb16231ef510c781c12863045e4
corrected review validation      a5e4f04a567de98f85674e8c58e13effe85753738d5de931704e41a153ec20b1
correction manifest              b3855b1377d8f65d8669d1fdbec12c5f93ef55ac28405c7dc15c40022cf62aa6
```

The base registry reproduction exactly matches the preserved HU SHA-256. Corrected packet text,
corrected registry text/relation and all 250 registry-bound decisions were cross-validated.
Terminal local review status is `M2_FACT_REVIEW_PASS`, exact verdicts `usable=250`.

## Single authorized wave shape

Proposed fresh root:

```text
/vol/tmp2/yesildau/vngrs_m2_oscar_fact_translation_repair_v1
```

One later exact SHA-bound authorization may permit:

1. ordinary non-force push of the exact implementation commit;
2. preservation-checked HU active-checkout fast-forward to that commit;
3. targeted HU tests;
4. one 4-CPU/32G/2h CPU-only Slurm job;
5. read-only access to the completed predecessor block manifest/files and tokenizer snapshots;
6. writing only the new corrected M2-B blocks, role audits and final manifest under the fresh root.

The operator does not read the 9.5 GB OSCAR source objects. For each model it verifies the
predecessor M2-A, M2-B and validation hashes, reads the exact immutable M2-A blocks as the generic
source, applies the corrected 976-block factual schedule and writes only a corrected M2-B file.
The new family manifest references the unchanged predecessor M2-A and validation files read-only.
It records exact changed-block/token-position counts versus predecessor M2-B.

## Frozen implementation

```text
config                 35813e5bb18d1bf75df483bc63bedba0458519b965b25cace0c10eafbf4cf690
correction preparer    d330128151535bb22d96e587ebcf106fcaeee75692c829b00d22daeccbb1d181
review validator       ad7ccdc492030db596c74ed77ea711996ff9b3747f7a31911dde04852b340efb
block repair runner    8d31edee3cd6cbf231292fb7d16bdb9da03191a81dfe4617d4bc7f3af36543e1
Slurm                  800f2b6971744e7d011de03982751643e6fab74abc520c01b198ac58f05af05c
submitter               dbe202dd38a3060bd67aa173e503b35d479d8bc4912c60b20f71487f65775de9
focused test file      35e4c4fffe53f9af7331f1ed63e19edd101a8d1224054ec23ca02b00e9305092
```

Python/shell syntax and the relevant combined suite pass `18/18`; `git diff --check` passes.

## Terminal requirements

PASS requires:

- exact corrected registry/review hashes;
- three roles and 250 unique Branch-B facts;
- predecessor M2-A/M2-B/validation SHA-256 and byte-size match;
- exact 97,536 blocks per arm, 512 tokens per block and 976 replacement blocks;
- only scheduled blocks may differ from the immutable generic M2-A source;
- corrected M2-B differs from predecessor M2-B for at least one and at most 976 blocks;
- full three-role manifest status `EXACT_THREE_MODEL_M2_BLOCKS_MATERIALIZED` plus repair status
  `M2_FACT_TRANSLATION_REPAIR_PASS`;
- `ready_to_train=false`.

## Authority boundary

This document authorizes nothing by itself. It does not authorize HU/SSH, push, Slurm, tokenizer
access or root creation until a later user instruction quotes this contract's exact final SHA-256
and implementation commit.

Even after one authorized PASS, it does not authorize GPU, model-weight access, optimizer smoke,
M2-A/M2-B training, evaluation, cleanup, deletion, fallback or automatic retry. The completed
predecessor family and all failed/partial roots remain preserved.
