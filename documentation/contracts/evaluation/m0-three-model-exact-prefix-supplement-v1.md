# M0 Three-Model Historical Exact-Prefix Supplement v1

Date: 2026-08-21  
Status: `FROZEN / UNEXECUTED / EXACT AUTHORIZATION REQUIRED`

## 1. Purpose

Measure the historical 500-probe English completion-stem panel at M0 for OLMo, Qwen and SmolLM.
This is a separate scientific supplement. It does not rerun or replace the completed robust A--D
direct/QA factual lanes and does not change eval-v1.

## 2. Exact semantic meaning

The historical name `exact-prefix` must not be interpreted as free generation followed by literal
string-prefix matching. The existing evaluator appends every candidate answer to the prompt,
scores its answer tokens and ranks candidates. The frozen semantic label is:

`historical_exact_prefix_candidate_ranking_not_free_generation`

Primary ranking uses mean answer-token log probability; total log probability is retained as a
secondary diagnostic, and exact ties use canonical object ID. Prompts, candidate sets and scoring
are unchanged from the historical implementation.

## 3. Frozen input panel

- 500 unique facts from 100 frozen pilot subjects;
- five relations, exactly 100 facts each: profession, birth place, residence, field of study and
  industry;
- English direct completion stems such as `... works as a`;
- probe SHA-256:
  `1644288d0d62c51c56ceaae71b9eef7225b88326267281c8df8aeef9d7619c8e`;
- the same 500 fact/answer identities as the robust registry, with zero byte-identical prompt
  overlap with A--D direct/QA prompts;
- robust registry SHA-256:
  `5125850a2db24c6b570971a58e9ba8a8586cabdec9084eb0e99bbd639691d93f`.

The input audit must pass before model scoring.

## 4. Models, runtime and outputs

The exact pretrained revisions and model-manifest hashes are frozen in
`configs/evaluation/m0_exact_prefix_three_model_v1.yaml`. Evaluation uses the existing frozen
Torch 2.6/CUDA 12.4 environment, BF16 CUDA execution and a 20 GiB free-VRAM guard. The only
writable family root is:

`/vol/tmp2/yesildau/eval_v1_m0_three_model_exact_prefix_supplement_v1`

Each lane preserves per-probe scores, subgroup metrics, summary metrics, audits and artifact
hashes. The family finalizer validates every model artifact and reports the three top-1
accuracies; it performs no normalization, model selection or scientific interpretation.

## 5. Parallel single-wave topology

One Slurm array `0-2%3` launches the three models concurrently on one RTX A6000 each. One CPU
finalizer runs with `afterany` after the array. Thus the bounded DAG contains three GPU array tasks
plus one finalizer. A failed route probe writes a no-job terminal manifest. If the array is
submitted but finalizer submission fails, the active array ID is persisted fail-closed.

## 6. Frozen implementation

- implementation commit: `246f4764ec5d2bfdcffa58012b25bcd31ea1f166`;
- operator SHA-256:
  `928060d9930bf733e3dcd43f340ac9fdec2c9b7f2ae14a91dc1417e59e9a9639`;
- study module SHA-256:
  `e4c959ad48db673a448374ad201c3b6d4d92224e9b1b55edc690adbe4188ec12`;
- focused test SHA-256:
  `d0c1d7af1393ccbe3b13260dee6d8332f1cd13873b968df1adf099a629ed6717`;
- pre-authorization config SHA-256:
  `4d42a3700fb1f5302d38cba7fcb06f40a3eb0c288642d5e254f81b7c41f1178a`.

## 7. Authorization boundary

The config remains `execution_authorized: false`. Execution requires a new user instruction bound
to the exact contract SHA-256 and the pre-authorization config SHA-256. That instruction may
authorize publication/HU fast-forward, one final preflight and exactly one four-job DAG.

It does not authorize rerunning robust A--D lanes, changing inputs/scoring/models, calling the
metric free-generation exact match, automatic retry, a second wave, normalization, M1/M2 training,
cleanup, deletion, HU-home writes or intervention in foreign jobs/processes. The active Qwen
Pile-10k recovery DAG remains independent and must not be altered or duplicated.
