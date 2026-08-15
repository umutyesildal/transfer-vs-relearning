# External Review Handoff Prompt — Qwen M2/M3 Endpoint Evaluation

You are reviewing the completed Qwen 2,500-fact M2/M3 experiment for the thesis project
**Transfer vs. Relearning in Cross-Lingual Factual Adaptation**.

Your task is to perform an independent scientific, reproducibility, and operational review. Do not
assume that the reported gate decision is correct merely because it is documented. Recompute or
cross-check the key claims from the frozen manifests and aggregate outputs wherever practical.

## 1. Read these documents first

Read the project instructions and current documentation in this order:

1. `AGENTS.md` in the implementation workspace;
2. `documentation/00_DOCUMENTATION_INDEX.md`;
3. `documentation/100_MASTER_PROJECT_STATUS_AND_EXECUTION_PLAN.md`;
4. `documentation/133_QWEN_2500_FACT_M2_M3_EXECUTION_HANDOFF_PLAN.md`;
5. `documentation/134_QWEN_PRE_M2_GPU_BLOCKER_AND_OFFLINE_PREPARATION_STATUS.md`;
6. `documentation/135_QWEN_M2_M3_CONTRACT_AND_MATERIALIZATION_STATUS.md`;
7. `documentation/136_QWEN_M2_M3_ENDPOINT_EVALUATION_GPU_ALLOCATION_STATUS.md`;
8. the earlier evidence documents referenced by Documents 100, 133, and 136, especially Documents
   84, 94--98, 102--106, 117--120, and 132.

Document 136 §§23--24 is the compact current result and readiness closure. Document 133 §14 is
the append-only execution handoff closure. Earlier documents are historical evidence and must not
be rewritten to hide failures or superseded decisions.

## 2. Current experiment state

The completed family is:

```text
Qwen M1 seed 42, step 75 -> M2-clean seed 42 and M3-fact seed 42
Qwen M1 seed 43, step 50 -> M2-clean seed 43 and M3-fact seed 43
```

The frozen contract is:

- 500 subjects and 2,500 facts;
- 250 Branch A / 250 Branch B subjects;
- M2-clean has no target synthetic factual bindings;
- M3-fact exposes only correct Branch-B Turkish factual bindings;
- four complete factual cycles over 1,250 Branch-B facts;
- 512-token blocks, 1,048,576 training tokens per arm, 128 optimizer updates;
- independently initialized M2 and M3 arms;
- fixed endpoint `checkpoint-128`;
- 60,000 probes per state, 24 slices × 2,500 probes;
- 2,000 subject-bootstrap samples with seed `20260717`.

All four principal training runs completed. The endpoint evaluation contains six states and
96/96 valid slices. The original M3 seed-43 tasks 83--95 failed before evaluator execution after
an HU checkout/commit-guard mismatch; they were infrastructure evidence, not scientific results.
Only those 13 slices were retried under the synchronized commit. Retry preflight was `440633`,
retry array was `440634_[83-95%3]`, and all 13 retried slices completed successfully.

## 3. Frozen result locations

The complete result package is on HU scratch:

```text
/vol/tmp2/yesildau/qwen_m2_m3_v1/
```

Key paths:

```text
/vol/tmp2/yesildau/qwen_m2_m3_v1/evaluation_v1/evaluation_manifest.json
/vol/tmp2/yesildau/qwen_pre_m2_contract_v1/evaluation/slice_registry.json
/vol/tmp2/yesildau/qwen_m2_m3_v1/analysis_v1/assembled_20260802T2315Z/
/vol/tmp2/yesildau/qwen_m2_m3_v1/analysis_v1/metrics_20260802T2315Z/
/vol/tmp2/yesildau/qwen_m2_m3_v1/analysis_v1/gate_20260802T2325Z/
```

The final gate report is:

```text
/vol/tmp2/yesildau/qwen_m2_m3_v1/analysis_v1/gate_20260802T2325Z/final_gate_report.json
```

The aggregate package contains:

- `state_accuracy.csv` — 462 data rows;
- `paired_state_contrasts.csv` — 462 data rows;
- `branch_interactions.csv` — 118 data rows;
- `robust_state_accuracy.csv` — 108 data rows;
- `robust_paired_contrasts.csv` — 108 data rows;
- completed `analysis_manifest.json` and passed `integrity_summary.json`.

## 4. Reported frozen decision

The documented decision is:

```text
primary_success_criterion_not_met
```

The frozen gates report:

- operational validity: **passed**;
- EN→EN retention guardrail: **passed**;
- primary TR→EN interaction, seed 42: observed `0.0025`, 95% CI `[-0.0051, 0.0101]` — **failed**;
- primary TR→EN interaction, seed 43: observed `0.0135`, 95% CI `[0.0051, 0.0218]` — **passed**.

The primary criterion requires a positive observed interaction and a 95% bootstrap lower bound
above zero for both seeds. Therefore the two-seed primary gate does not pass. No checkpoint,
threshold, seed, factual dose, or gate was selected or changed after seeing the results.

## 5. Review questions

Independently check the following:

1. Does the implementation match the frozen M2/M3 contract, especially independent initialization,
   matched token/update budgets, Branch-B-only factual exposure, four factual cycles, and fixed
   checkpoint-128 evaluation?
2. Do the evaluation manifest, slice registry, model manifests, result manifests, and SHA-256
   records establish complete and reproducible provenance?
3. Are all 96 endpoint slices present, complete, unique, and members of the frozen registry with
   exactly 2,500 probes each?
4. Does the assembly correctly validate and combine the four M2/M3 states without silently
   overwriting, imputing, or selecting results?
5. Do the aggregate CSVs reproduce the reported global, direction, robust, paired, and
   Branch A/B interaction values?
6. Does the primary gate implementation exactly match the precommitted criterion, including the
   subject-level bootstrap, seed handling, confidence-interval direction, and no post-hoc choice?
7. Does the EN→EN retention guardrail use the correct M1 reference for each seed and the frozen
   five-percentage-point limit?
8. Are the baseline PPL and bilingual M1 results correctly connected to the M2/M3 contrasts?
9. Are the documented infrastructure failures correctly separated from scientific observations?
10. Do any contradictions remain among Documents 100, 133, 134, 135, 136, and the index?
11. Is the conclusion “valid operational family, retention passed, primary two-seed interaction
    not replicated” scientifically justified?
12. Are there any hidden reasons to reject the package, or any claim that is stronger than the
    evidence supports?

## 6. Safety and scope rules

- Read `AGENTS.md` before inspecting HU or running project scripts.
- Do not submit Slurm jobs, request GPUs, retrain models, rerun slices, or alter the contract.
- Do not delete, overwrite, migrate, or clean selected artifacts, manifests, datasets, or result
  trees.
- Do not relax the gate, add a seed, change factual dose, choose another checkpoint, or perform
  post-hoc selection.
- Preserve all unrelated local changes and untracked files.
- Never expose credentials, passwords, tokens, or `.env` contents.
- Treat the scratch package as evidence to inspect, not as disposable output.

## 7. Required review deliverable

Write an independent review report with these sections:

1. **Executive verdict:** `PASS`, `PASS WITH CONCERNS`, or `BLOCKED`;
2. **Scientific validity:** contract, estimand, gate, and interpretation review;
3. **Reproducibility:** manifests, hashes, slice completeness, and analysis provenance;
4. **Result cross-check:** independently verified values and any discrepancies;
5. **Operational/storage review:** job history, scratch placement, home-storage compliance, and
   whether infrastructure failures were correctly classified;
6. **Documentation review:** stale statements, missing evidence, or contradictions;
7. **Action list:** classify each issue as `BLOCKER`, `MAJOR`, `MINOR`, or `NONE`, and give the
   exact document/path/line or manifest evidence supporting it;
8. **Final recommendation:** whether the current package is suitable for thesis interpretation,
   whether only documentation work remains, or whether a separately approved amendment is needed.

Do not merely summarize Document 136. The purpose of this handoff is an adversarial but reproducible
independent check of the completed experiment and its frozen negative/inconclusive primary result.
