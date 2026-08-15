# 140a - Qwen M2/M3 Independent Review Result

**Date:** 2026-08-03  
**Reviewer:** Codex (`/root`)  
**Review mode:** Read-only independent verification  
**Status:** Completed — PASS WITH CONCERNS  
**Scope:** Completed Qwen 2,500-fact M2-clean/M3-fact family

## 1. Executive verdict

```text
PASS WITH CONCERNS
```

The independent, read-only examination of the HU scratch evidence reproduces the frozen result.
The four endpoint models, 96 endpoint slices, assembly package, aggregate CSVs, integrity package,
and final gate are internally consistent and traceable to the frozen registry. The two EN→EN
retention checks per seed/arm pass the precommitted five-percentage-point guardrail. The primary
TR→EN Branch-B-specific interaction passes for seed 43 but not for seed 42 because the latter's
95% subject-bootstrap interval crosses zero. The frozen final decision,
`primary_success_criterion_not_met`, is therefore correct.

This is a valid completed operational family and is suitable for the thesis interpretation stated
in Documents 136 and 138: correct factual re-exposure is associated with modest descriptive
M3-over-M2 recovery, but the precommitted two-seed causal interaction criterion was not met.

The two concerns are procedural/documentary rather than scientific evidence failures:

1. the frozen evaluation manifest is intentionally a pre-execution input but still says
   `frozen_ready_to_submit`, which could be misread as the final status if separated from its
   assembly and gate descendants; and
2. the final recorded HU-home `du` audit timed out, although the result paths are on scratch and
   the accompanying large-home-file scan was clean.

No selected artifact, raw result, manifest, contract, threshold, checkpoint, or training state was
modified. No job was submitted, rerun, canceled, or monitored as part of this review.

## 2. Materials and provenance inspected

### 2.1 Documentation and implementation read before the evidence review

The review followed the ordered handoff in Document 137. It read `AGENTS.md`, the documentation
index, Documents 100, 133--136, and the specifically relevant historical evidence documents,
including Documents 84, 94--98, 102--106, 117--120, and 132. It also read Documents 138--142 to
separate the current frozen primary conclusion from the later exploratory analysis and from
historical HOLD language.

The following local implementation files were inspected read-only to establish the calculation and
gate semantics rather than trusting the prose description:

| Item | Path / identifier | Relevant review check | Checked |
|---|---|---|---|
| Matched-metric implementation | `transfer-vs-relearning/src/transfer_vs_relearning/metrics/qwen_m2_m3.py` | Static-field validation, subject bootstrap, paired contrasts, robust cells, Branch A/B interaction | Yes |
| Assembly implementation | `transfer-vs-relearning/scripts/assemble_qwen_m2_m3_results.py` | Hash checks, registry membership, completion checks, no partial aggregate output on failure | Yes |
| Analysis implementation | `transfer-vs-relearning/scripts/analyze_qwen_m2_m3_results.py` | Six-state loading, fixed bootstrap parameters, no overwrite, no gate selection | Yes |
| Gate implementation | `transfer-vs-relearning/scripts/finalize_qwen_m2_m3_gate_report.py` | Completeness condition, retention limit, primary two-seed criterion, decision ordering | Yes |
| Training-manifest implementation | `transfer-vs-relearning/training/clm.py` | Meaning of normalized `config_sha256` in a training manifest | Yes |

### 2.2 HU evidence package and SHA-256 verification

All paths below are on HU scratch. The review calculated SHA-256 values directly from the
read-only artifacts and compared them with the values recorded by the assembly, analysis, gate,
and completion documentation.

| Item | Path / identifier | SHA-256 | Checked |
|---|---|---|---|
| Evaluation manifest | `/vol/tmp2/yesildau/qwen_m2_m3_v1/evaluation_v1/evaluation_manifest.json` | `cf4c046899596f3f26b735119aa68c2b75e97c883129b749c90e51e2f1cd5a69` | Yes |
| Frozen slice registry | `/vol/tmp2/yesildau/qwen_pre_m2_contract_v1/evaluation/slice_registry.json` | `e47aeece03cef0c02d781980b622a88f6439017b0be0346be3b6a295802e3474` | Yes |
| Training-family config manifest | `/vol/tmp2/yesildau/qwen_m2_m3_v1/family/config_manifest.json` | `3a35d5a943c4c595e43e3ac4ba191994fbf9a5704f45ef08d5cae0752be5ab99` | Yes |
| Training-block manifest | `/vol/tmp2/yesildau/qwen_m2_m3_v1/blocks/manifest.json` | `978582d13499219f1f531839a19836bc51f95313711753361935c68e0b92f02d` | Yes |
| Training-block matching audit | `/vol/tmp2/yesildau/qwen_m2_m3_v1/blocks/matching_audit.json` | `0f46b6a1be97126ed4c334ae994afc2824029848ce0d0d62f7d8490feabb2173` | Yes |
| Assembled results manifest | `/vol/tmp2/yesildau/qwen_m2_m3_v1/analysis_v1/assembled_20260802T2315Z/results_manifest.json` | `dfccc1b5f37a72fed687323258f871dbc4188304bd4c087f0a93a8ee1239708a` | Yes |
| Assembly manifest | `/vol/tmp2/yesildau/qwen_m2_m3_v1/analysis_v1/assembled_20260802T2315Z/assembly_manifest.json` | `60bdb420406fb774aaa191304dddedadfb382cf7273d3986a2b5d7acd4167684` | Yes |
| Analysis manifest | `/vol/tmp2/yesildau/qwen_m2_m3_v1/analysis_v1/metrics_20260802T2315Z/analysis_manifest.json` | `d8122d948360201ff17f434fdf220b15216a849fe14de0e8c5171342cc9b1419` | Yes |
| Integrity summary | `/vol/tmp2/yesildau/qwen_m2_m3_v1/analysis_v1/metrics_20260802T2315Z/integrity_summary.json` | `5d46c4d8ce94dc293e58e26469d3fdc451c703cdaa59c060c35fa1511812b882` | Yes |
| Frozen gate report | `/vol/tmp2/yesildau/qwen_m2_m3_v1/analysis_v1/gate_20260802T2325Z/final_gate_report.json` | `e5dbe0c7631a2590c5087946635f1f18ccdd39abbb136e54ec621d7efe8419a5` | Yes |

### 2.3 Aggregate-output hash verification

| Aggregate file | Data rows | SHA-256 | Result |
|---|---:|---|---|
| `state_accuracy.csv` | 462 | `5394dd8b12f176a672c3008e7aa1f55d4851dbde92d7b06f348c77eca50e4431` | Matched |
| `paired_state_contrasts.csv` | 462 | `1ec55af44904cbeef9c2c9f888c52778590288ffb3bd3e5a663d42dc829ad8d4` | Matched |
| `branch_interactions.csv` | 118 | `61680518448161d94d1b0180a036a14d89d4107f1dad49b4839b8c40375a9c59` | Matched |
| `robust_state_accuracy.csv` | 108 | `d3f701de7d63a232b4ab7b42e6580b6d3523796cd2707ae7ab6b027a9efd1c86` | Matched |
| `robust_paired_contrasts.csv` | 108 | `48217e44ae6cf5247e3d399d3af77495f19e106afa194b8b9efb15e2f83a66ba` | Matched |

The raw result tree, assembled state-level CSVs, analysis CSVs, and gate package are therefore
cryptographically connected. The review found no mismatched final hash.

## 3. Contract and causal validity

### 3.1 Frozen family reconstructed from raw manifests

The raw `config_manifest.json`, four training manifests, block manifest, and matching audit confirm
the following frozen family:

| Contract item | Independently observed evidence | Result |
|---|---|---|
| Starting states | M2 and M3 seed-42 runs both reference the selected M1 seed-42 step-75 artifact; seed-43 runs both reference the selected M1 seed-43 step-50 artifact | PASS |
| Independent arms | Each M2/M3 run has its own output root and training manifest; M3 is initialized from M1, not from M2 | PASS |
| Arm-specific input | M2 uses `m2_clean_train_blocks.jsonl`; M3 uses `m3_fact_train_blocks.jsonl`; validation input is shared | PASS |
| Matched budget | 512-token blocks; 2,048 blocks; 1,048,576 tokens; 128 updates; learning rate `1e-5`; gradient accumulation 8; warm-up 4; checkpoint/evaluation cadence 32 | PASS |
| Factual cycles | Four cycles over the Branch-B factual exposure schedule | PASS |
| M2 treatment | Zero target factual exposure | PASS |
| M3 treatment | 5,000 scheduled Branch-B exposures, 1,250 unique Branch-B facts, zero Branch-A exposure | PASS |
| Endpoint | All four runs completed through `checkpoint-128`; this is the frozen evaluated endpoint | PASS |
| Evaluation design | 24 slices × 2,500 probes = 60,000 probes per state; 96 M2/M3 endpoint slices | PASS |

The block matching audit further records equal total blocks and tokens per arm. It is not merely a
statement in a planning document: the audit fields for matching, factual cycles, Branch-B facts,
and Branch-A exposure are present in the frozen artifact and were read directly.

### 3.2 Training-manifest reconciliation

The four run manifests each report `status=complete`, the expected source M1 checkpoint,
2,048 blocks, 128 updates, and retained endpoint checkpoints at 32, 64, 96, and 128. The observed
seed-to-source relationship is:

| State | Seed | Source selected M1 endpoint | Final endpoint |
|---|---:|---|---|
| `m2_clean_seed42` | 42 | M1 seed 42, step 75 | `checkpoint-128` |
| `m3_fact_seed42` | 42 | M1 seed 42, step 75 | `checkpoint-128` |
| `m2_clean_seed43` | 43 | M1 seed 43, step 50 | `checkpoint-128` |
| `m3_fact_seed43` | 43 | M1 seed 43, step 50 | `checkpoint-128` |

The apparent difference between some raw YAML file hashes in the family config manifest and a
training manifest's `config_sha256` is not a contradiction. `training/clm.py` normalizes the parsed
configuration before hashing it; the family manifest records the raw YAML file hash. The
corresponding paths, training parameters, and arm data files agree.

### 3.3 Precommitted estimand, bootstrap, and gate implementation

The reviewed implementation establishes the following definitions:

- Top-1 is `correct_rank_mean == 1`.
- The analysis groups probe-level top-1 outcomes by subject before bootstrapping.
- The primary estimand is exactly `(M3 − M2)_B − (M3 − M2)_A` for TR→EN.
- Each bootstrap uses 2,000 samples, `random.Random(20260717)`, and the documented 2.5th/97.5th
  percentile rule.
- The Branch-A and Branch-B components are resampled independently, as implemented by
  `bootstrap_independent_difference`.
- Robust results require all eight `(form A–D, direct/QA)` cells; they are not a selective
  post-hoc subset.
- The gate reads only the fixed `direction=tr_to_en` interaction rows for both seeds. It requires
  `observed > 0` **and** `bootstrap_ci_low > 0` for both seeds.
- EN→EN retention is evaluated separately against the matching seed's M1 state with the fixed
  point-estimate limit `M2/M3 − M1 >= -0.05`.
- The analysis script declares `gate_selection=not_performed`; the gate script applies the frozen
  rule without selecting a checkpoint, threshold, or seed after observing results.

**Finding: PASS.** The raw manifests and code establish a controlled M1→M2/M3 contrast and the
frozen causal criterion. The contract does not support a claim that a positive M3-minus-M2 average
alone is a passed causal result; the reviewed gate correctly requires the two-seed interaction.

## 4. Evaluation completeness and integrity

### 4.1 Slice-level raw-output audit

An in-memory, read-only verifier iterated every expected M2/M3 state and every slice in the frozen
registry. For each slice it checked directory membership, `summary.json` and `run_manifest.json`
completion markers, row count, unique probe IDs, exact registry membership, and raw/slice/run
manifest hashes against the assembly manifest. It did not create an output directory or write a
file on HU.

| State | Registered slice directories | Raw rows | Unique probe IDs | Errors |
|---|---:|---:|---:|---|
| `m2_clean_seed42` | 24 / 24 | 60,000 | 60,000 | None |
| `m2_clean_seed43` | 24 / 24 | 60,000 | 60,000 | None |
| `m3_fact_seed42` | 24 / 24 | 60,000 | 60,000 | None |
| `m3_fact_seed43` | 24 / 24 | 60,000 | 60,000 | None |
| **M2/M3 endpoint total** | **96 / 96** | **240,000 state rows** | **60,000 per state (same frozen registry)** | **None** |

The direct file inventory independently found exactly 96 terminal `summary.json` result files.
Every audited slice reported 2,500 raw rows with 2,500 unique probe IDs and exactly the
corresponding frozen registry ID set.

### 4.2 State assembly and baseline linkage audit

The assembly manifest includes the two required M1 baseline state tables alongside the four
endpoint states. The review directly loaded all six state-level tables and verified the following:

| State | Rows | Unique IDs | Same probe-ID set as reference | Static-field mismatches |
|---|---:|---:|---|---:|
| `m1_seed42` | 60,000 | 60,000 | Yes | 0 |
| `m1_seed43` | 60,000 | 60,000 | Yes | 0 |
| `m2_clean_seed42` | 60,000 | 60,000 | Yes | 0 |
| `m2_clean_seed43` | 60,000 | 60,000 | Yes | 0 |
| `m3_fact_seed42` | 60,000 | 60,000 | Yes | 0 |
| `m3_fact_seed43` | 60,000 | 60,000 | Yes | 0 |

The matched static fields were exactly `subject_id`, `fact_id`, `direction`, `relation`,
`form_id`, `scaffold_id`, `branch_group`, `frequency_bucket`, `name_type`,
`name_rarity_bucket`, and `popularity_bucket`. There were zero duplicate probe IDs, zero missing
state rows, and no silent imputation, overwrite, or cross-state metadata substitution.

The evaluation manifest records the matching M1 baseline hashes:

| Baseline | State-table SHA-256 |
|---|---|
| M1 seed 42 / step 75 | `a8521731e80563a7bb568618ccff2c7b90e1a79391a306b6f8d4d18911eb5a5a` |
| M1 seed 43 / step 50 | `914eea06e5dbf7d033d1c1ec66f8c09eeaa7bd3711e657f1a8994b08d2b66908` |

These are the same M1 references used for the seed-specific retention comparisons.

### 4.3 Assembly and analysis fail-closed properties

The reviewed assembly program validates expected slice count and probe count before assembly,
checks every raw artifact before creating output, and refuses hash, metadata, registry, completion,
or row-count mismatches. The analysis program rejects an existing output directory, validates all
six matched states before writing aggregate tables, records its exact input hashes, and reports no
gate selection. These properties are consistent with the observed complete frozen output package.

**Finding: PASS.** The endpoint package is complete, unique, registry-conformant, and
cryptographically traceable from slice output through the frozen gate.

## 5. Independent metric and gate cross-check

### 5.1 Recalculation method

The primary and retention results were reproduced directly from the raw per-probe state tables,
not copied from the gate report. The read-only calculation:

1. converted `correct_rank_mean == 1` to top-1 outcomes;
2. averaged those outcomes within subject for the selected state, direction, and branch;
3. computed the observed paired arm changes and the Branch-B minus Branch-A interaction;
4. used 2,000 subject bootstrap resamples with seed `20260717` and the implementation's percentile
   convention; and
5. compared the independently produced numeric triples with the frozen CSV rows and gate report.

The recomputed triples below agree exactly with the raw aggregate precision. The aggregate file
hashes in Section 2.3 additionally verify the complete global, direction, relation, form,
scaffold, branch, frequency, name, rarity, popularity, robust, paired, and interaction tables.

### 5.2 State-level headline values

Top-1 state accuracy from the immutable aggregate file is shown as percent. The direction columns
are the values used to contextualize the gate, rather than a replacement estimand.

| State | Global | EN→EN | TR→EN | TR→TR |
|---|---:|---:|---:|---:|
| M1 seed 42 | 60.12% | 99.29% | 52.03% | 29.05% |
| M1 seed 43 | 60.63% | 99.24% | 52.52% | 30.12% |
| M2-clean seed 42 | 51.27% | 98.05% | 33.29% | 22.46% |
| M2-clean seed 43 | 51.06% | 96.24% | 33.70% | 23.25% |
| M3-fact seed 42 | 52.47% | 98.22% | 35.14% | 24.04% |
| M3-fact seed 43 | 52.50% | 96.95% | 35.59% | 24.97% |

The robust-intersection table is consistent with the same qualitative result. These values require
a subject to succeed across all eight form/scaffold cells:

| State | EN→EN robust | TR→EN robust | TR→TR robust |
|---|---:|---:|---:|
| M1 seed 42 | 96.08% | 22.52% | 14.96% |
| M1 seed 43 | 96.28% | 23.44% | 16.80% |
| M2-clean seed 42 | 91.96% | 16.72% | 12.52% |
| M2-clean seed 43 | 88.48% | 15.28% | 11.96% |
| M3-fact seed 42 | 92.20% | 18.20% | 13.68% |
| M3-fact seed 43 | 89.64% | 16.72% | 13.32% |

### 5.3 Retention guardrail reproduction

The gate uses the EN→EN top-1 point estimate against the matching M1 seed and does not use a
post-hoc threshold. The fixed criterion is at least `-0.0500` (no loss worse than five percentage
points). All four required comparisons pass.

| Seed | Contrast | Independently observed difference | 95% CI | Gate result |
|---:|---|---:|---|---|
| 42 | M2-clean − M1 | −0.01240 | [−0.01545, −0.00965] | PASS |
| 42 | M3-fact − M1 | −0.01070 | [−0.01330, −0.00810] | PASS |
| 43 | M2-clean − M1 | −0.03000 | [−0.03655, −0.02425] | PASS |
| 43 | M3-fact − M1 | −0.02295 | [−0.02820, −0.01850] | PASS |

The worst observed EN→EN change is −0.03000, which is 0.02000 above the frozen rejection limit.

### 5.4 Primary interaction reproduction

| Check | Frozen expected value | Independently observed from raw per-probe tables | Status |
|---|---|---|---|
| Operational validity | Six states, 60,000 probes/state, passed integrity | Six matched states, 60,000 rows/state, all integrity checks passed | PASS |
| Seed-42 TR→EN interaction | `+0.0025`, CI `[−0.0051, +0.0101]` | `+0.0025000000000000126`, CI `[−0.005100000000000006, +0.010100000000000033]` | FAILS primary CI rule |
| Seed-43 TR→EN interaction | `+0.0135`, CI `[+0.0051, +0.0218]` | `+0.013500000000000003`, CI `[+0.005100000000000009, +0.0218]` | PASS |
| Overall frozen decision | `primary_success_criterion_not_met` | Seed 42 fails the required lower-bound condition; seed 43 passes | PASS |

The review also independently reproduced the TR→EN paired M3-fact minus M2-clean contrast,
which is descriptive support for the observed recovery but is not the primary interaction gate:

| Seed | M3-fact − M2-clean | 95% CI |
|---:|---:|---|
| 42 | +0.01855 | [+0.01480, +0.02215] |
| 43 | +0.01895 | [+0.01485, +0.02330] |

The aggregate exploratory summaries are compatible with those cross-checks: the M2-minus-M1
TR→EN decline is −18.74 percentage points for seed 42 and −18.83 points for seed 43; the
M3-minus-M2 TR→EN recovery is +1.86 and +1.90 points. This does **not** supersede the interaction
test. In particular, a positive M3-minus-M2 average cannot turn seed 42's non-positive lower
confidence bound into a passed Branch-B-specific result.

### 5.5 Gate logic review

The final gate program declares an integrity failure first if the exact six required states,
60,000-probe package, completed analysis manifest, or passed integrity summary is absent. Only
after that does it apply the primary interaction; only after a primary pass would it consider an
EN→EN retention failure. The observed package reaches the primary gate and correctly receives
`primary_success_criterion_not_met`.

No threshold, confidence direction, checkpoint, seed, factual dose, M3-lexical arm, or subgroup
was selected or altered after results were observed. The robust and exploratory tables remain
descriptive/secondary and do not affect the frozen decision.

**Finding: PASS.** The frozen global, direction, robust, paired, and interaction outputs agree
with the hashes and selected raw-data recomputations; the primary and retention gates were applied
exactly as precommitted.

## 6. Operational and storage review

### 6.1 Infrastructure versus scientific evidence

The raw completion package and the chronological ledger support the documented separation between
infrastructure failures and scientific observations:

| Event | Classification confirmed by review | Reason |
|---|---|---|
| Contaminated A100/RTX devices in initial arrays | Infrastructure only | Allocated-device guard stopped tasks before model loading/evaluation |
| V100 attempts | Infrastructure only | Installed CUDA build reported no compatible kernel image; no endpoint result used |
| Empty early task directories | Not scientific observations | No terminal summary or result was used; final assembly requires valid artifacts |
| M3 seed-43 tasks 83--95 in array `440344` | Infrastructure only | Checkout/commit guard failed before evaluator execution; original logs were empty |
| Retry preflight `440633` and retry array `440634_[83-95%3]` | Valid controlled recovery | Retried only the 13 missing task IDs under the synchronized commit; all completed |

The final 96-slice inventory and hash audit show that none of these infrastructure events was
silently counted as a scientific score. The completion of the M3 seed-43 retry fills required
registry entries; it does not duplicate a valid existing slice or introduce a new condition.

### 6.2 Storage placement and artifact preservation

The inspected raw output, assembly, analysis, and gate paths are all rooted in:

```text
/vol/tmp2/yesildau/qwen_m2_m3_v1/
```

This is approved scratch, not the HU home filesystem. The reviewed documentation records the
preflight and post-run checks, scratch capacity/inode observations, resolved run/artifact paths,
and no newly identified large project output in home. The review did not see a result path that
resolves under `/vol/fob-vol6/mi25/yesildau`.

The raw package remains intact. No model, checkpoint, raw result, aggregate table, manifest,
cache, log, or selected artifact was deleted, copied, moved, or overwritten during this review.

### 6.3 Remaining operational closure point

Document 136 records that the post-run home `du` check timed out due to NFS behavior. Its
large-home-file scan was nevertheless clean, and all inspected high-volume paths are scratch
paths. This is sufficient to conclude that it does not invalidate the scientific evidence, but it
leaves one required capacity observation incomplete before later artifact-lifecycle closure.

**Finding: CONCERN.** The completed family is operationally valid and scratch-contained; repeat
the non-mutating home capacity/inode/path audit before a future retention or cleanup decision.

## 7. Documentation review

The review compared historical documents with the current index and the raw results. Historical
status text has not been treated as a contradiction where a dated correction preserves the history
and explicitly redirects readers to later evidence.

| Severity | Document/path/line or field | Finding | Recommended correction |
|---|---|---|---|
| NONE | `documentation/136_QWEN_M2_M3_ENDPOINT_EVALUATION_GPU_ALLOCATION_STATUS.md:3-11` versus §§21--24 | The top status is a preserved progress snapshot stating that evaluation was partial; the later append-only closure records 96/96, integrity, metrics, and gate. | Preserve chronology. Use §§21--24 and Documents 138/140a for current status. |
| NONE | `documentation/100_MASTER_PROJECT_STATUS_AND_EXECUTION_PLAN.md:5-27` and later dated corrections | The opening text contains historical M2/M3 HOLD language, but it labels itself superseded and redirects to subsequent workstreams; the index identifies the current authority. | Do not rewrite historical evidence. Keep explicit source-of-truth guidance. |
| NONE | `documentation/00_DOCUMENTATION_INDEX.md:8-12, 50-68` | The current-source paragraph correctly points to Documents 133 §14, 136 §§21--24, 138, and 139. | This report is added to the same current-source guidance. |
| NONE | `documentation/142_QWEN_M2_M3_EXPLORATORY_MECHANISM_ANALYSIS_RESULT_EN.md` | Exploratory M3 recovery is clearly labeled post-hoc and does not alter the primary gate. | Keep this boundary. |
| MINOR | `evaluation_manifest.json`, field `status` | The immutable frozen input manifest says `frozen_ready_to_submit` although downstream assembly, analysis, and gate artifacts are complete. It is a correct input artifact, but not a suitable standalone final-status indicator. | Do not alter the frozen manifest. Point final consumers to `results_manifest.json`, `analysis_manifest.json`, and `final_gate_report.json`. |
| NONE | Documents 133--136 retry ledger | The failed GPU/commit-guard events are retained and explicitly separated from valid slices. | Preserve the ledger; no result correction is required. |

No documentation claim reviewed was stronger than the data support when the current source order is
followed. Specifically, Documents 136, 138, 139, and 142 do not claim a replicated passed primary
interaction, a successful third seed, a selected alternative checkpoint, or a conclusion based on
the exploratory output.

## 8. Issue ledger

Only the permitted severity vocabulary is used below.

| ID | Severity | Finding | Evidence | Resolution required |
|---|---|---|---|---|
| R-001 | MINOR | The frozen evaluation input manifest retains `status=frozen_ready_to_submit`. | `/vol/tmp2/yesildau/qwen_m2_m3_v1/evaluation_v1/evaluation_manifest.json`, while its descendants are completed and hash-linked in Sections 2 and 4. | None for scientific validity. Preserve the frozen input; use downstream manifests and gate report as final-status sources. |
| R-002 | MINOR | The final HU-home `du` observation timed out during the post-run audit. | Document 136 §21 post-run audit record; scratch paths and large-home-file scan remain consistent with compliant placement. | Repeat the read-only home capacity, inode, resolved-path, and large-file audit before artifact-retention/cleanup closure. |
| R-003 | NONE | Initial GPU contamination, V100 incompatibility, empty pre-evaluator attempts, and the M3 seed-43 commit-guard failure are not scientific observations. | Document 136 retry ledger plus final exact 96/96 raw slice audit. | No action; retain the infrastructure record. |
| R-004 | NONE | M1 references, M2/M3 budgets, exposure construction, endpoint, registry, metadata, and hashes are matched. | Family config/block audits, four training manifests, evaluation manifest, registry, assembly, integrity, and direct raw-table checks. | No action. |
| R-005 | NONE | The final gate outcome is not a documentation-only assertion. | Direct raw-data bootstrap reproduction and exact aggregate/gate hash match in Section 5. | No action. |

There are no `BLOCKER` or `MAJOR` findings.

## 9. Final recommendation

Accept this package for the constrained thesis interpretation recorded in Document 138:

```text
The M2/M3 family is operationally valid and passes the fixed English-retention guardrail.
M3-fact is descriptively higher than M2-clean on TR→EN in both seeds, but the precommitted
Branch-B-specific interaction is not replicated under the required two-seed confidence rule.
The frozen conclusion is primary_success_criterion_not_met.
```

Only documentation and artifact-lifecycle work remains within the currently authorized scope.
Before any retention or cleanup decision, complete the non-mutating storage audit noted in R-002
and preserve model-only endpoint manifests/checksums according to the authorized closure plan.

This review does **not** authorize a new seed, training family, factual dose, checkpoint choice,
M3-lexical arm, gate change, threshold relaxation, or 25,000-fact run. Any such step requires a
separately approved scientific amendment with a new frozen contract.

## Appendix A. Exact evidence topology

```text
/vol/tmp2/yesildau/qwen_m2_m3_v1/
├── blocks/
│   ├── manifest.json
│   └── matching_audit.json
├── family/
│   └── config_manifest.json
├── runs/
│   ├── m2_clean_seed42/.../training_manifest.json
│   ├── m2_clean_seed43/.../training_manifest.json
│   ├── m3_fact_seed42/.../training_manifest.json
│   └── m3_fact_seed43/.../training_manifest.json
├── evaluation_v1/
│   ├── evaluation_manifest.json
│   └── results/<four states>/<24 frozen slices>/
│       ├── hard_suite_per_fact.csv
│       ├── summary.json
│       └── run_manifest.json
└── analysis_v1/
    ├── assembled_20260802T2315Z/
    │   ├── results_manifest.json
    │   ├── assembly_manifest.json
    │   └── states/<six states>/per_probe_results.csv
    ├── metrics_20260802T2315Z/
    │   ├── analysis_manifest.json
    │   ├── integrity_summary.json
    │   ├── state_accuracy.csv
    │   ├── paired_state_contrasts.csv
    │   ├── branch_interactions.csv
    │   ├── robust_state_accuracy.csv
    │   └── robust_paired_contrasts.csv
    └── gate_20260802T2325Z/
        └── final_gate_report.json
```

The frozen registry is separately rooted at:

```text
/vol/tmp2/yesildau/qwen_pre_m2_contract_v1/evaluation/slice_registry.json
```

The M1 reference tables are separately rooted at:

```text
/vol/tmp2/yesildau/qwen_pre_m2_baseline_rtx3090_v1/summaries_final/
```

## Appendix B. Independent verification coverage matrix

| Review question from Document 137 | Method | Outcome |
|---|---|---|
| Independent M2/M3 initialization and matched budgets | Read four training manifests, family config manifest, block manifest, matching audit | Confirmed |
| Branch-B-only M3 factual exposure and zero M2 target exposure | Read frozen matching audit and arm-specific block provenance | Confirmed |
| Fixed endpoint | Checked all four training manifests and evaluation manifest for `checkpoint-128` | Confirmed |
| 96 complete registry members | Iterated all state/slice directories and exact frozen IDs | Confirmed |
| 2,500 probes/slice and 60,000/state | Counted raw rows and unique probe IDs | Confirmed |
| Assembly provenance | Compared raw/slice/run hashes with assembly records; checked six assembled state tables | Confirmed |
| Matched metadata and M1 references | Compared six state probe sets and static fields; verified seed-specific baseline hashes | Confirmed |
| Global, direction, robust, paired, and interaction tables | Verified all aggregate file hashes; inspected schema and representative values | Confirmed |
| Primary and retention calculations | Recomputed selected frozen gates directly from raw per-probe CSVs | Exact match |
| Bootstrap/gate semantics | Read calculation and gate source code; compared to manifests/gate report | Confirmed |
| Infrastructure classification | Read retry ledger and reconciled it with final raw inventory | Correctly non-scientific |
| Documentation consistency | Compared Documents 00, 100, 133--136, 138--142 and raw evidence | No scientific contradiction |

## Appendix C. Claim boundary retained by this review

The evidence supports all of the following:

- a complete four-run, two-seed M2-clean/M3-fact endpoint family;
- valid frozen registry membership and matched state-level evidence;
- passed operational and EN→EN retention conditions;
- positive descriptive M3-fact minus M2-clean TR→EN recovery in both seeds; and
- failure of the precommitted two-seed primary interaction criterion.

The evidence does not support any of the following:

- a passed replicated primary causal interaction;
- a claim that seed 43 alone establishes replication;
- selection of another endpoint checkpoint after inspecting results;
- a claim that exploratory form, scaffold, relation, or robust patterns amend the gate;
- a conclusion that M3-lexical, a third seed, a larger factual dose, or the 25,000-fact branch is
  automatically required or authorized; or
- a relaxation of the confidence-bound or retention rules.

## Appendix D. Review-side mutation log

```text
HU artifact writes:             none
Slurm submissions/cancellations: none
Model/evaluation reruns:        none
Manifest/data modifications:    none
Local code modifications:       none
Documentation change:           this append-only independent review record and its index entry
```
