# M0 OLMo v8 English-capability recovery v1

**Status:** `frozen / execution-authorized` | **Owner:** project | **Date:** 2026-08-16
**Parent:** `m0-olmo-qualification-v1.md`

## Decision

Recover exactly one failed test-only lane from the completed OLMo v8 qualification namespace and
assemble it with the six already valid lanes. Do not repeat data acquisition, the six successful
lanes, or any scientific evaluation.

This remains `test_only_non_scientific`. It may qualify mechanics, but no metric from this wave may
enter thesis tables, model gates, trajectory plots, or model-selection decisions.

## Immutable source evidence

- source root: `/vol/tmp2/yesildau/eval_v1_m0_olmo_qualification_v8`;
- plan ID: `b4065be7c013d8e3`;
- config SHA-256: `79ef439adb445d49bdbef43a0f0993578b7e6ddf753b5f72664d942dd713153d`;
- source `parallel_plan.json` SHA-256:
  `d2d45a67d69d10d95d207a5058ceb2725452a52f7712bc403cf81505fdeaca20`;
- source `bundle_status.json` SHA-256:
  `8bc66ee20fba02c0052de8ea8bf83134e93c3b2459681ffc5da28af8873fa4c8`;
- source `evaluation_results.json` SHA-256:
  `28809af24fdbb4d39edae678c3acbc7c6b81b62dfb77f9f43c0e791da6728f42`;
- source `qualification_result.json` SHA-256:
  `4d54e5253d85764bb0d6468d12bcfb3bc88d68240651f002f8e7a3057b43ab03`;
- source `final_inventory.json` SHA-256:
  `6e5804e1aa6ea41dddf649b0c1d9775ed7cb9a59382689324cb884aae77202c5`;
- reusable lanes: `english_retention_wikitext`, `english_retention_pile_10k`,
  `english_grammar_blimp`, `turkish_capability`, `factual_access`, and
  `generation_integrity`;
- incomplete lane: `english_capability`, job `461465`, node `gruenau2`, route `rtx6000`;
- incomplete lane-result SHA-256:
  `96bf42388dc3272aab9827ba74980bf59ebd013e778e070b71098f088df67e65`;
- incomplete lane stderr SHA-256:
  `b05a4963e1788780d5f7e7a134fed1d4a57408825a22a8a69a9e760c87beea08`.

Job `461465` failed before scoring during model-load allocator warm-up. The allocated RTX6000 had
only 1.39 GiB free while a foreign process used 20.41 GiB; the attempted 2.77 GiB allocation
failed. This is resource-contamination evidence, not a model/task result.

## Frozen recovery bindings

- implementation commit: `383c44ea4e689194b962308e56310d5c64346ab1`;
- entrypoint: `scripts/study/recover_m0_lane.py`;
- entrypoint SHA-256:
  `bdabf06640217afb20973e3ef5003716ad355ad9b5e6a270332a53441c7ac183`;
- recovery module: `src/transfer_vs_relearning/study/m0_recovery.py`;
- recovery module SHA-256:
  `7f1a73f25473c38fdc92608dc8e0f8b8c8df15c98cc04f7514fdccd2521de214`;
- regression tests: `tests/study/test_m0_recovery.py`;
- regression-test SHA-256:
  `d99cce499ade3386852006841972749b4d214f3cc938351e849c0ea3bf5db60e`;
- exact target lane: `english_capability`, index 3;
- exact task IDs: `hellaswag`, `winogender_female`, `winogender_male`,
  `winogender_neutral`;
- exact route: `v10032gb` / `gpu:v10032gb:1`;
- runtime free-memory gate: at least 17,179,869,184 bytes before model load;
- fresh recovery root:
  `/vol/tmp2/yesildau/eval_v1_m0_olmo_qualification_v8_english_capability_recovery_v1`.

All model, tokenizer, Harness, runtime, seed, few-shot, task, limit, precision, batching and prompt
bindings come unchanged from the exact v8 plan. The recovery uses v8's already materialized cache
offline. It must not download or rematerialize task data.

## Fail-closed execution protocol

1. Verify the current config/plan identity and every artifact hash for all six reusable lanes.
2. Require a fresh scratch-only recovery root and clean implementation worktree.
3. Copy v8's cache and preflight evidence into the fresh recovery namespace without modifying v8.
4. Require Slurm `--test-only` acceptance of the exact V100 route.
5. Submit exactly one GPU job for lane index 3 and one `afterany` CPU finalizer.
6. After allocation, measure CUDA free/total memory and stop before model load unless at least
   16 GiB is free.
7. Run the existing v8 lane adapter unchanged and offline.
8. Build a composite manifest using the recovery result only for `english_capability` and source
   v8 results for the other six lanes.
9. Emit `evaluation_manifest.json` only if all seven selected lane results and artifacts validate.
   Missing or invalid evidence remains `partial_invalid`; no zero filling is allowed.

Even after 7/7 assembly, the qualification gate remains blocked on the separately required
WikiText count/result/heading parity and TurBLiMP 16-subtask macro parity checks. A complete recovery
therefore closes the operational lane gap only; it does not authorize or constitute scientific M0.

## Explicit prohibitions

- no rerun of the six completed lanes;
- no write to or cleanup of v8 or any older evidence root;
- no alternate model, revision, task, limit, prompt, seed, precision, batch, or threshold;
- no RTX6000/RTX3090/A100/A6000 fallback in this recovery contract;
- no scientific M0 claim;
- no M1 or M2 training;
- no corpus materialization, artifact deletion, or cleanup.

The user's 2026-08-16 instruction to finish OLMo and then build the three-model system authorizes
this exact bounded recovery wave. Any retry after this single submission requires a new recorded
decision.
