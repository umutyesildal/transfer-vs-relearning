# M1 blocker-resolution packet — read-only preparation boundary

**Date:** 2026-08-22  
**Status:** preparation complete; execution blocked  
**Scientific gate:** `blocked_by_measurement_design`  
**`ready_to_train`:** `false`  
**Training/evaluation authorized:** no

## Purpose

M0 eval-v2 projection, source audit and canonical metric normalization are complete. This packet
turns the next M1 step into an auditable, bounded work order: close the benchmark-registry,
source-model-provenance and measurement-design evidence gaps before an executable M1 contract is
even drafted. It is a preparation record, not a training or evaluation contract.

No model or corpus was downloaded, no source artifact was mutated, and no HU/SSH, Slurm/GPU,
inference, scoring, training, corpus materialization, cleanup or deletion was performed for this
packet.

## Inputs and immutable authorities

| Input | Role | SHA-256 / status |
|---|---|---|
| `documentation/current/PROJECT_STATE.yaml` | current control-plane state | `15cc2d636fe92a5397eb0614e766f7a6b3dfbb0bf0ee15b5953c974d8f5ddb10` |
| `documentation/current/AGENT_BRIEF.yaml` | agent context projection | points to the hash above |
| `documentation/151z_POST_MINIMAL_COVERAGE_MATRIX_REPAIR_DECISION_GATE_TR.md` | latest coverage gate | `51e3cdda3db8a636f1308a42910c2dd76bfdca5ef0906a3a316dc639c4b984db` |
| `documentation/151aa_FINAL_EVIDENCE_GAP_AUDIT_AND_MANIFEST_CORRECTION_TR.md` | missing-field authority | `0a063d7d7465eb8bffdfa47a55fa95adc8420cef0a641e9d967c19ef6cdb69ae` |
| `documentation/151ab_MEASUREMENT_DESIGN_AUTHORITY_AND_MINIMAL_BASELINE_CONTRACT_TR.md` | frozen measurement authority | `3ff0823f8a4aa5f806ab451abfffa989e0d70f1b1ca6b240229306cfac99c06c` |
| `documentation/evaluation/M1_TRAJECTORY_TABLE_V1.md` | epoch/checkpoint review schema | `a3b33a65432d050c35a877ff4622e2e77fe5a7a0b030ef31804f731967c10389` |
| `documentation/decisions/M1_CONTRACT_PREPARATION_PLAN_2026-08-22.md` | preparation order | `ee140cd420e1bb11f15d1febeead33fd72d683af122725a635e9828077a5b09e` |

The 151z gate is authoritative: its nine-file coverage repair was operationally valid, but the
registries were only schema-complete. Schema completeness is not evidence completeness.

## Current blocker ledger

### 1. Benchmark registry — `BLOCKED`

The repair contains three benchmark entities (`TurBLiMP`, `TurkishMMLU`, `Turkish EXAMS`) with 27
fields each: 81 schema fields in total. The 151z audit records the schema as `PASS / schema-only`,
but the evidence-complete registry as `BLOCKED`.

The unresolved classes are deliberately separated:

- C1 identity/compatibility fields: canonical task identity, exact task definition, split/language,
  scientific role, base-model compatibility and registry status;
- C3 measurement fields: chance baseline, floor/ceiling evidence and benchmark-overlap procedure;
- exact item bytes/ordered-ID hashes, prompt/choice rendering rules, evaluator revision and code
  hash, and subject/split manifests required by the expanded 151ab ledger.

The 151aa authority counts 54 non-verified fields overall. It records benchmark fields as
`not_retrieved_in_this_wave`, `not_reported` or derived `blocked`; these values must remain
explicitly missing and must not be replaced with guessed metadata or benchmark scores.

**Closure evidence required:** a bounded, source-read-only registry reconciliation with immutable
task/revision/item/split/evaluator identities and a field-level coverage matrix. It must not run a
benchmark or download a task.

### 2. Source-model provenance — `BLOCKED`

The current 151ab role set is:

| Model | Frozen role | Interpretation constraint |
|---|---|---|
| `allenai/OLMo-2-0425-1B` | provenance-first primary candidate | not proof of zero Turkish exposure |
| `tiiuae/falcon-rw-1b` | secondary English comparator | “English-only” card is not mathematical zero-exposure proof |
| `Qwen/Qwen2.5-1.5B` | multilingual/Turkish positive control | never label as Turkish-unseen |

The registry has three 23-field schema rows, but all three remain evidence-blocked. Required
closure fields include exact model/revision/tokenizer and repository identities, architecture and
runtime compatibility, license, artifact-manifest hashes, stage/training-corpus summary and the
truthful Turkish-evidence label. `not_reported` is retained as uncertainty; it is not silently
converted into `zero Turkish exposure`.

Pythia remains preserved historical provenance-screen evidence, but it is not silently inserted
into the frozen 151ab execution set. No candidate is promoted from the M0/M1 result after looking
at outcomes.

**Closure evidence required:** reconcile only already-available immutable local artifacts and
documented source identities; missing artifacts remain `blocked_by_source_model_provenance` and
require a separately authorized acquisition decision.

### 3. Measurement design — `BLOCKED`

Section 8.2 of 151ab leaves these user-review fields unresolved:

```text
turkish_heldout_v1.sha256
english_retention_v1.sha256
delta_TurBLiMP_equivalence_margin
delta_EN_retention_margin
benchmark_floor_ceiling_saturation_rule
```

The expanded pre-execution ledger also requires exact item-set and ordered-ID hashes, prompt and
choice templates, TurBLiMP pair scoring, TurkishMMLU/EXAMS subject and split manifests,
base-model compatibility, model/tokenizer artifact manifests, BOS/EOS and masking rules, context
and truncation rules, NLL/BPB denominator, bootstrap count/seeds/CI method, paired-unit and
missing-item policy, held-out/control/retention manifests, evaluator code revisions and fixed
checkpoint identities.

These values are design inputs, not outcomes. They cannot be filled by inspecting a future M1
score, and no numeric threshold or hash is invented in this packet.

**Closure evidence required:** a reviewed, immutable measurement ledger that binds the primary
Turkish held-out role, `trwiki-20260601` control role, English retention identity, overlap rules,
thresholds, bootstrap policy and evaluator revisions before any baseline scoring or training.

## M1 trace and evaluation shape already frozen for preparation

The trajectory view is one row per `model × seed × checkpoint`; the source of truth remains
long-form checkpoint, metric and factual-probe tables. A prospective matched M1 run will record at
every epoch end:

- actual cumulative examples and fact exposures;
- supervised/total tokens, update, epoch, effective batch, sequence length, learning rate and
  gradient accumulation;
- checkpoint identity/hash and exact-prefix, top-1, robust factual and relation-control metrics;
- WikiText BPB as primary retention, with byte PPL/PPL ratio as companions;
- cheap integrity status, and full bundle at entry/midpoint/endpoint.

Historical checkpoints are backfilled only when their artifacts exist. `not_observed_historically`,
`not_run` and `failed_pre_scoring` remain typed states; missing rows are never zero-filled or
interpolated. The historical inventory config remains `prepared_unexecuted` and does not create a
matched three-model comparison.

## Closure order and decision boundary

1. Complete benchmark identity/coverage evidence without scoring.
2. Complete source-model identity/artifact provenance without silently downloading missing data.
3. Review and freeze the measurement ledger and all five Section 8.2 fields.
4. Resolve the separate primary-corpus selection/materialization gate; `trwiki-20260601` remains
   control-only until that decision is frozen.
5. Freeze matched M1 recipe, seed, token/update budget, checkpoint cadence and storage guard.
6. Only then draft a new SHA-bound executable M1 contract and request a separate user
   authorization.

Until steps 1–5 pass, the following remain prohibited: M1/M2 contract creation, model/corpus
download, corpus materialization, HU/SSH, Slurm/GPU, training, scoring, inference, primary-model
promotion and cleanup.

## Local validation performed

- Python syntax compilation passed for the study controller, historical inventory module and
  inventory entrypoint.
- YAML execution helpers were not run because the local Python interpreter lacks PyYAML; this is an
  environment limitation, not a scientific result. No fallback parser was used to claim execution.
- Documentation hashes and current-state linkage were checked locally; no external state was
  touched.

**Decision:** M0 is closed. The next authorized work unit is the read-only evidence-resolution
packet above, not M1 training. An executable M1 contract remains intentionally absent until the
blockers are closed and the user authorizes that new boundary.
