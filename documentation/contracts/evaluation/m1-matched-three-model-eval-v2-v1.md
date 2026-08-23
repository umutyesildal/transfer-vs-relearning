# M1 matched three-model eval-v2 execution contract v1

**Date:** 2026-08-22  
**Status:** `FROZEN / AWAITING EXACT SHA-BOUND AUTHORIZATION`  
**Scientific scope:** completed matched M1 trajectories for OLMo, Qwen and SmolLM

## 1. Single authorized objective

Execute one evaluation-only M1 wave over the already completed, immutable training family at
`/vol/tmp2/yesildau/m1_matched_three_model_retry_v1`. The wave evaluates the M0 parent and all 36
epoch-end M1 snapshots for each of the three fixed models, writes only to the fresh root
`/vol/tmp2/yesildau/m1_eval_v2_matched_three_model_v1`, and performs no training, network retrieval,
cleanup or source-artifact mutation.

The frozen execution config is
`configs/evaluation/m1_eval_v2_matched_three_model_v1.yaml` with SHA-256
`d08c175c94ee3c70edcb204c4bd1e3ec3929ceeb81e092783f1dddcf6b040d66`.

## 2. Closed input family

| Model | M1 checkpoint-manifest SHA-256 | M1 training-manifest SHA-256 | M0 parent-manifest SHA-256 |
|---|---|---|---|
| OLMo | `f1681974fb5aa8da8dece1d0af9786eca1013302a6bf39d3b4920015587c289c` | `68ad5c6b394918bbe5a57189ada0ebe6a14fe9c9213f658ffc1d4177d2935630` | `8702b80d5b7e4c996c8ce2ff5fe771ada08ab0080bde1926c0b1f53c607303dc` |
| Qwen | `08636e6df7d0fc532ccb5743f1a406da96d00dcdd4f0ab31194714a83d299dc0` | `0323b0088e2804b181cc0ade03a17868f8d37c16fe1ad7f483d73c501cc60b15` | `c9d3562b717784251fe14c2b7972660fe4a20fe4687e15f69746bc1713d2d4fb` |
| SmolLM | `6d64e96f4aab69df6621ca6506d06bc8bb55145e262caea2d76794a3b33e5d7c` | `638a9066484e8695f9600f7991441b9622a1b63596d3184d55e25606d13a138c` | `e5d04302087b8b41828f734c1d88c4620a74bb80d6919de62df37b9d57dadbfc` |

Every checkpoint manifest must contain exactly `parent, epoch-001, …, epoch-036` in order. Every
referenced model manifest and training manifest is re-hashed before namespace creation and again
inside the execution chain. Missingness is never converted to zero.

## 3. Frozen scientific evaluation

Every one of the 111 states receives:

- identity and training-trace binding;
- 1,500-probe bilingual cheap factual access;
- the historical 500-probe exact-prefix candidate-ranking supplement;
- WikiText English retention through LM Evaluation Harness;
- frozen `trwiki-20260601` Turkish cross-domain retention control;
- generation-integrity evaluation.

The parent, epoch 18 and epoch 36 for every model additionally receive:

- the 12,000-probe bilingual full factual suite;
- BLiMP;
- HellaSwag;
- Winogender female/male/neutral slices;
- the pinned `juletxara/turblimp` TurBLiMP task family.

Pile-10k remains retired and is forbidden. Eval-v2, all frozen registries, prompt identities,
scoring definitions, seeds, revisions and comparison gates remain unchanged.

## 4. Execution adapter and topology

The registered adapter is `slurm_m1_matched_wave_v1`:

- `src/transfer_vs_relearning/study/m1_wave_executor.py` —
  `fa2aafdd0d465a01d53036788395968428bb0460ac16de329587de3ee4cd3734`
- `scripts/study/execute_m1_eval_v2.py` —
  `6205c1365588a0d006109c0c93e0c813a154e8c302a8045aac57b1c5adb981f9`

The only permitted DAG is:

```text
read-only final preflight
→ A10080 array 0-110%3 (one checkpoint state per task)
→ afterany family finalizer
```

The finalizer records every complete, failed or missing state and emits `complete` only at 111/111.
It does not normalize incomplete results or choose a model.

## 5. Storage and safety

- HU home is read-only and remains below the existing 30 GiB policy limit.
- Dataset/model caches are reused offline; network retrieval is forbidden.
- Training outputs, M0 results and prior failed roots are immutable.
- The output root must not exist at final preflight.
- No retry, rerun, threshold change, M2 action, cleanup or deletion is authorized.
- A submission failure after partial job creation must be recorded; it does not authorize a second
  wave.

## 6. Authorization boundary

Preparation, local tests and hashing do not authorize publication, HU fast-forward, output-root
creation, Slurm submission or evaluation. One exact authorization naming this contract SHA-256
and the frozen execution-config SHA-256 is required. After that authorization, the permitted
sequence is ordinary non-force push, preservation-checked HU fast-forward, final preflight and one
three-job DAG submission.

## 7. Append-only correction 1 (2026-08-23, pre-execution)

This correction is recorded before any execution. The original sections above remain preserved;
where a statement below conflicts with them, the statement below governs.

7.1 Superseded statements. The §4 adapter hashes `fa2aafdd…` / `6205c136…` are superseded; the
§4 DAG line "A10080 array 0-110%3 (one checkpoint state per task)" is superseded; and the §1
execution-config SHA-256 `d08c175c94ee3c70edcb204c4bd1e3ec3929ceeb81e092783f1dddcf6b040d66` is
superseded by `65c70265844a7ea94be80498546da2625b41bf2ea83beeafbda156ae70e28db8`. No other
section is reinterpreted.

7.2 Rebound execution adapter. The registered adapter `slurm_m1_matched_wave_v1` now binds:

- `src/transfer_vs_relearning/study/m1_wave_executor.py` —
  `d573a0e0aaf342971cbc68068f9004e80f46de988b3de7513381aa01ced098e9`
- `scripts/study/execute_m1_eval_v2.py` —
  `0123fe5921b9e4e7c2ce61e74785ad5ead810914155e095d0beb55e3624b004d`

7.3 Topology. The permitted DAG is:

```text
read-only final preflight
→ A10080 array 0-107%3 over the 108 real M1 epoch snapshots (36 per model)
→ afterany family finalizer that projects the three M0 parent states
```

The wave closes scientifically only at 111/111 states: 108 measured snapshot states plus three
parent projections. A missing or failed state is never converted to zero or rescored.

7.4 Parent projection without rescoring. The M0 parent of each model is not re-measured on GPU.
At finalization the parent state is written as a reference projection from the canonical,
hash-closed M0 evidence bundle `/vol/tmp2/yesildau/eval_v2_m0_metric_normalization_v1f`
(config `configs/evaluation/eval_v2_m0_metric_normalization_v1f.yaml`, SHA-256
`3781cd62e6bfa1d3484bd87f54b44000eb9aae35a8b0260ad31b93cc15d56047`; v1b source registry with 24
rows). The bundle must close through its own `final_inventory.json` hash chain and yield exactly
42 attributed metric rows, 14 per model; otherwise the finalizer fails closed and the wave is
incomplete.

7.5 Full-state cheap-factual derivation. At the nine full states (parent, epoch 18 and epoch 36
per model), the 12,000-probe full factual suite is scored once and the 1,500-probe cheap rows are
derived by filtering the precommitted cheap probe IDs from the full scores. The cheap rows at
full states are never separately rescored; their metric definition is unchanged and each derived
row carries its source full-probe identity. Dense states measure the 1,500-probe registry
directly as before.

7.6 Per-state validation gate. A snapshot task may record `complete` only after: byte-level
snapshot verification against the training-time snapshot manifest, harness results including full
denominators without limits, complete factual outputs, a complete 500-probe exact-prefix result,
a complete trwiki cross-domain perplexity result bound to corpus SHA-256
`15480c1f543acf6df7aac1b2a2ee15fdcb3a544814f0063a181bd7a9cb0ca4f8` with exactly 10,034
documents, and a complete generation-integrity panel.

7.7 Authorization binding. The single authorization sentence must name this corrected contract
SHA-256 and the corrected execution-config SHA-256 recorded in `documentation/current/
PROJECT_STATE.yaml` under `m1_evaluation`. Authorization remains one wave; no retry, rerun or
threshold change is authorized.

## 8. Append-only correction 2 (2026-08-23, dual-route acceleration)

This correction is recorded after the user explicitly chose to cancel the Correction-1 wave
before any scientific result was produced. Where a statement below conflicts with earlier
sections, the statement below governs.

8.1 Superseded statements. The §7.2 adapter hashes are superseded by the hashes in 8.2; the
§7.3 single-array topology is superseded by the dual-route topology in 8.3; and the Correction-1
execution-config identity `configs/evaluation/m1_eval_v2_matched_three_model_v1.yaml`
(SHA-256 `65c70265844a7ea94be80498546da2625b41bf2ea83beeafbda156ae70e28db8`) is superseded by
the frozen `configs/evaluation/m1_eval_v2_matched_three_model_v2.yaml`.

8.2 Rebound execution adapter:

- `src/transfer_vs_relearning/study/m1_wave_executor.py` —
  `49ed94d37b5000421b23b51dea914b25db8c3fe35c0e5e192ffb36b719c05290`
- `scripts/study/execute_m1_eval_v2.py` —
  `85c5e8f0488cab89f787266e116262f806c46a5cdfba48842b7d1fadd3594d53`

8.3 Dual-route topology. The permitted DAG is:

```text
read-only final preflight
→ A6000 array 0-71%8 over the qwen+smollm epoch snapshots (gpu:a6000:1)
→ A10080 array 0-35%3 over the olmo epoch snapshots (gpu:a10080gb:1)
→ afterany family finalizer that projects the three M0 parent states
```

Array-local task ids map to global matrix indices through frozen offsets: the A100 array covers
indices 0–35 (olmo), the A6000 array covers indices 36–107 (qwen, smollm). All other §3
evaluation semantics — bundles, cadence, full-state cheap derivation, parent projection,
111/111 closure — are unchanged from Corrections 0 and 1.

8.4 Route policy. Only two GPU resource types are authorized for this wave:
`gres=gpu:a6000:1` and `gres=gpu:a10080gb:1`. V100, RTX6000, RTX3090 and every other card type
are forbidden. The A6000 pool is expected to resolve to the currently idle gruenau7/gruenau8
nodes; the scheduler may place either route on any node offering the declared resource type.

8.5 Per-task GPU free-memory gate. Before scoring, every task probes free memory on its Slurm-
allocated GPU (`CUDA_VISIBLE_DEVICES`, first entry) via `nvidia-smi`. Fewer than
21,474,836,480 bytes (20 GiB) free is a fail-closed task failure recorded as `failed`; missing
values are never converted to zero or skipped. The gate threshold is frozen and not
outcome-aware.

8.6 Cancelled Correction-1 attempt. The Correction-1 wave was submitted as preflight job
`475878` (completed), evaluation array `475879` and finalizer `475880`. The user cancelled it
roughly fifteen minutes after the first three snapshot tasks started; no task had reached a
scientific result. The root `/vol/tmp2/yesildau/m1_eval_v2_matched_three_model_v1` is preserved
read-only as the cancelled-attempt evidence with an appended cancellation marker, and the fresh
output root for this correction is `/vol/tmp2/yesildau/m1_eval_v2_matched_three_model_v2`.
The cancellation consumed no scientific measurement and does not count as the one authorized
wave of this correction.

8.7 Authorization binding. The single authorization sentence must name this corrected contract
SHA-256 and the frozen v2 execution-config SHA-256. Authorization remains exactly one wave
across both arrays plus preflight and finalizer; no retry, rerun, throttle change after
submission, or threshold change is authorized.

