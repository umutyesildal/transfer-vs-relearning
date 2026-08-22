# M1 design decisions confirmed — eval-v2 inheritance and vngrs primary

**Date:** 2026-08-22  
**Status:** user-confirmed design boundary; execution contract not yet frozen  
**Training/evaluation/materialization:** not authorized by this memo

## Confirmed decisions

### 1. TurBLiMP identity is inherited from M0

M1 uses the exact TurBLiMP route used by M0/eval-v2:

```text
dataset = juletxara/turblimp
revision = cce94ca73ac04a0fabd9fbd7a56068261e6348ad
task_id = turblimp_core
primary_metric = acc_norm
sensitivity_metric = acc
aggregation = unweighted macro over 16 subtasks
```

The 151ab `ezgibasar/TurBLiMP` identity remains preserved as historical independent-diagnostic
evidence, but it is not substituted into the M1 continuity route. No M0 parity result is rewritten.

### 2. M1 inherits the complete active M0 eval-v2 bundle

Every active M0 eval-v2 family is mandatory for M1, using the same task/evaluator identity and
metric semantics:

- WikiText raw BPB (primary English retention), word/byte PPL and parent-relative ratio;
- BLiMP English grammar;
- HellaSwag normalized accuracy;
- WinoGender female/male/neutral diagnostic slices;
- inherited TurBLiMP `turblimp_core`;
- project-native factual access: Forms A–D, top-1, robust intersections, relation controls and
  exact-prefix supplement;
- generation integrity;
- Turkish PPL/cross-domain control where defined by eval-v2.

M1 cadence follows the frozen trajectory policy: cheap factual/retention/integrity checks at each
epoch-end checkpoint, exact-prefix at every required checkpoint, and the full bundle at entry,
precommitted midpoint and endpoint. The metric identities do not change merely because cadence is
dense.

`pile_10k` is explicitly retired from eval-v2. Its historical M0 artifacts and failures remain
read-only evidence, but it is not silently reintroduced into “all M0 evals” for M1.

### 3. vngrs is the primary Turkish corpus design choice

The user-selected primary adaptation corpus is:

```text
primary_design_choice = vngrs-ai/vngrs-web-corpus
primary_role = in_domain_turkish_adaptation_corpus
```

`trwiki-20260601` remains the frozen cross-domain control and is not substituted for the primary
corpus or its document-disjoint held-out split. CulturaX remains excluded by access status.

This is a scientific design choice, not yet an operational corpus PASS. The existing vngrs evidence
is conditional: exact candidate/sample provenance exists, but the full release/shard manifest,
license capture, quality/LID, dedup, PII, synthetic-fact overlap and primary held-out split
artifacts still need a separately bounded evidence/materialization contract.

## What is now fixed for the future M1 contract

```text
M0 → M1 uses the same eval-v2 metric/task identities
M1 TurBLiMP = M0 juletxara route
primary Turkish adaptation corpus = vngrs
trwiki-20260601 = cross-domain control only
Pile-10k = retired, preserved, not in M1
```

The future contract still must bind exact corpus/model/tokenizer manifests, split hashes, recipe,
checkpoint cadence, thresholds and storage guards. No model or corpus download, materialization,
scoring, HU/Slurm or training occurred while recording these decisions.
