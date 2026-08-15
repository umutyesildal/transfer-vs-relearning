# Evidence map for the WIP paper

This file maps the manuscript's major claims to the current internal scientific record. It is an authoring aid, not a substitute for the frozen manifests on HU scratch.

## Scope audit

- A full local scan covered 230 source files: 209 files under `documentation/` (including the Notion export and PDFs) and 21 research PDFs under `papers/`.
- Extracted corpus size: 601,534 words across 491 PDF pages.
- The scan manifest and extracted text are local QA intermediates under `.tmp/paper_work/` and are not canonical experiment evidence.

## Claim-to-source map

| Manuscript content | Primary internal authority |
|---|---|
| Original thesis question and proposed no-repetition/repetition branches | `documentation/Expose.pdf` |
| Chronological project synthesis and source-of-truth order | `documentation/100_MASTER_PROJECT_STATUS_AND_EXECUTION_PLAN.md` |
| M0 direct and QA top-1 of 0.006 | `documentation/04_M0_BASELINE_RUN_REPORT.md`; `documentation/05_M0_QA_MATCHED_BASELINE_REPORT.md` |
| Method-development narrative and failed-recipe boundary | `documentation/100_MASTER_PROJECT_STATUS_AND_EXECUTION_PLAN.md`; `documentation/130_COMPLETE_PROJECT_HISTORY_METHODS_RESULTS_AND_FORWARD_PLAN_EN.md` |
| Replicated 2,500-fact Qwen M1 selection, checkpoints, robust/PPL metrics | `documentation/127_QWEN_SCALE_REPLICATION_RESULT_AND_SMOLLM_LAMBDA025_STATUS.md` |
| Completed M2-clean/M3-fact contract, 96/96 endpoint slices, state results, primary interaction and retention gate | `documentation/136_QWEN_M2_M3_ENDPOINT_EVALUATION_GPU_ALLOCATION_STATUS.md` |
| Frozen scientific interpretation and claim boundary | `documentation/138_QWEN_M2_M3_COMPLETED_MILESTONE_AND_SCIENTIFIC_INTERPRETATION_EN.md` |
| Independent read-only recalculation and PASS WITH CONCERNS verdict | `documentation/140a_QWEN_M2_M3_INDEPENDENT_REVIEW_RESULT_EN.md` |
| Relation/form/scaffold/decline/recovery descriptions labeled exploratory | `documentation/142_QWEN_M2_M3_EXPLORATORY_MECHANISM_ANALYSIS_RESULT_EN.md` |
| Model-only retention freeze and checksum verification | `documentation/143_QWEN_M2_M3_ARTIFACT_RETENTION_FREEZE_AND_STORAGE_AUDIT_EN.md` |
| Reinterpretation as parallel M2-A/M2-B siblings and Qwen Wikipedia-only 1M-token pilot | `documentation/144_SUPERVISOR_FEEDBACK_AND_SCIENTIFIC_REALIGNMENT_TR.md` |
| Prospective literature-first source-model/corpus/dose route | `documentation/145_LITERATURE_FIRST_M1_MODEL_AND_TURKISH_ADAPTATION_ROUTE_TR.md` |
| Model-provenance shortlist and literature evidence | `documentation/147_LUNA_MODEL_PROVENANCE_AND_M1_SHORTLIST_AUDIT_TR.md`; `documentation/148_CROSS_LINGUAL_LANGUAGE_ADAPTATION_LITERATURE_MATRIX_TR.md` |
| Prospective Turkish capability and manipulation-check architecture | `documentation/150_TURKISH_CAPABILITY_AND_ADAPTATION_MANIPULATION_CHECK_PLAN_TR.md` |
| Expanded Turkish corpus/model precedent and candidate-pool rationale | `documentation/THESIS_RELEVANT_PAPERS_MASTER_MAP_TR.md`, especially Sections 4.4, 7.6, and 12 |
| Current blocked measurement-design/corpus-selection status | `AGENTS.md`; Documents `151ag`, `151ah`, `151ak`, `151an`--`151at` |

## Terminology policy

- `M2-clean` and `M3-fact` are preserved when referring to immutable historical artifact names.
- `M2-A` and `M2-B` are used as the conceptual sibling-arm labels in the manuscript.
- The completed pilot's frozen primary estimand remains the Branch-B-minus-Branch-A interaction because only Branch-B facts were re-exposed.
- The prospective study's final estimand is not claimed as frozen; its exact subgroup and treatment definition remains part of unresolved measurement design.

## Result boundary

- Frozen completed-pilot decision: `primary_success_criterion_not_met`.
- Independent review: `PASS WITH CONCERNS`, with no blocker or major scientific issue.
- Prospective study: unexecuted; `ready_to_measure=false`; `ready_to_train=false`; global gate `blocked_by_measurement_design` with unresolved corpus-selection/materialization work.
