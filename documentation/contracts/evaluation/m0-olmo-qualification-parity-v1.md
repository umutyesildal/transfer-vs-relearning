# M0 OLMo qualification parity v1

**Status:** `frozen v2 completed / authorization consumed` | **Owner:** project | **Created:** 2026-08-16
**Parent:** `m0-olmo-qualification-v1`

## Purpose

This bounded test-only wave resolves exactly two open qualification checks from the completed OLMo
seven-lane bundle:

1. `wikitext_count_result_and_heading_parity`; and
2. `turblimp_16_subtask_macro_parity`.

It cannot produce a scientific M0 score and cannot freeze eval-v1 by itself. A PASS only removes
these two named verification blockers. Dataset revisions, Pile-10k cadence, TurkishMMLU disposition,
scientific factual registries, numerical margins and exact checkpoint bindings remain separate
eval-v1 freeze requirements.

## Frozen semantics at preparation time

The source bundle is the immutable qualification-v8 namespace. The completed targeted recovery is
used only as evidence that the full seven-lane bundle is available; the parity computation reads
the original WikiText and TurBLiMP lane artifacts bound by their lane-result SHA-256 values.

WikiText canonical parity recomputes, from every logged sample:

- the upstream detokenized target;
- the upstream word denominator from the original `page` string;
- the UTF-8 byte denominator from the original `page` string;
- word perplexity, byte perplexity and bits-per-byte from the summed rolling
  log-likelihood; and
- result/sample counts and exact document IDs.

The absolute floating-point parity tolerance is `1e-12`. The predefined heading sensitivity maps
each `= heading =` line to a same-depth Markdown heading such as `# heading`, evaluates the same two
documents and recomputes its own transformed denominators. Its numeric deltas are descriptive only:
there is no outcome-aware magnitude threshold.

TurBLiMP parity binds all 16 upstream subtasks in their emitted order and exactly two logged samples
per subtask. Per-example `acc` is recomputed from the two raw choice log-likelihoods. Decision metric
`acc_norm` is recomputed after dividing each choice log-likelihood by its candidate sentence's UTF-8
byte length. Per-subtask means and the unweighted 16-subtask macro are then compared with the Harness
result. The duplicated upstream `aggregate_metric_list` key and its effective last-value-wins
`acc_norm` meaning must both be recorded; no silent YAML repair is permitted.

## Execution boundary

The user authorized continuing this sequence on 2026-08-16. The implementation and companion
config are now frozen as follows:

- implementation commit: `b503d9ca6471bd6e40a59ca823d6a2c9d963b8a7`;
- operator entrypoint SHA-256:
  `63cd9bb33bfc2640ea628c4880b33afcd6e047928db82a0a5acc09b117b85ca6`;
- parity module SHA-256:
  `3583e0916bd0f151d96993ad2bae64d7484f8e586f4e9fa8378c0c1b95868d78`;
- WikiText heading preprocessor SHA-256:
  `9f331af3df4da84fdd5bfc6b2b52cbbfc4a0fb87d1bf51d4e3de4b01c4f59829`;
- WikiText heading task YAML SHA-256:
  `b8b66fa5ff4ef376596f1d1e046633193f1e261bb77ad40ac9831564a19a7eaa`;
- initial companion config SHA-256:
  `cf2191108a3a7c28f6cedd747ebd531496e473a366147677ec0339a897a7ca1a`;
- completed seven-lane recovery result SHA-256:
  `a5e8dcc72e0a7303505be975b0bc2f8422c02b6b17ca7d08a182adecd54d00c8`;
- source WikiText lane-result SHA-256:
  `23bbf0ca68202abc1633dc132cf803b537e341e4129ee14192bef7b9be1afbde`;
- source TurBLiMP lane-result SHA-256:
  `c1da6b48bed624c49088c2add56eb9c051ab37f9b163b5a0cd201f9911631ab4`.

The executable wave uses:

- one fresh root: `/vol/tmp2/yesildau/eval_v1_m0_olmo_qualification_parity_v1`;
- the pinned lm-eval v0.4.12 environment and exact OLMo manifest;
- a CPU structural recomputation before any GPU submission;
- one V100-32GB heading-sensitivity job after a Slurm `--test-only` gate and a 16 GiB runtime
  free-memory gate; and
- one `afterany` CPU finalizer that preserves PASS or blocked evidence.

HU home and every prior evidence root remain read-only. No training, scientific M0 evaluation,
corpus work, cleanup, deletion, threshold change or eval-v1 freeze is authorized by this contract.

## Required outputs

- `parity_plan.json`;
- `structural_parity.json`;
- `gpu_route_selection.json`;
- `heading/gpu_memory_preflight.json`;
- raw heading Harness result and logged samples;
- `heading_sensitivity.json`;
- `parity_results.jsonl`;
- `parity_manifest.json`;
- `parity_result.json`; and
- `final_inventory.json`.

## Freeze blockers

None for the frozen test-only v2 correction. A blocked v2 result does not authorize another retry
or any further semantic repair.

## Append-only source plan-ID binding correction

The first frozen preflight completed without creating the proposed namespace and without submitting
any Slurm job. Every implementation, environment, upstream task, cache, recovery, model and file
identity gate passed. It stopped only because the companion config bound source plan ID
`b406caea29643888`, while the immutable WikiText lane, TurBLiMP lane, v8 `parallel_plan.json` and
completed recovery result all independently record `b4065be7c013d8e3`.

This correction changes that one source plan-ID field. Lane-result byte hashes, sample artifacts,
model, runtime, task semantics, tolerance, route, root and prohibitions are unchanged. The corrected
companion config SHA-256 is
`49876c2f5240c0249ae374da5ac62b15aab15bb60ee0699ac47b279d4f6f88c4`. The user's bounded
test-only authorization remains applicable to this identity-only correction; it does not authorize
an outcome-aware scientific rerun.

## Append-only upstream `acc_norm` semantic correction

The corrected-plan preflight passed every gate. Submission initialization created the v1 parity
root and copied the already materialized offline cache. Before probing a GPU route or calling
`sbatch`, structural validation produced:

- WikiText canonical count/result parity: PASS, with exact reproduction of word PPL
  `13.325301724411347`, byte PPL `1.6503868248492586` and BPB `0.722804209249961`;
- TurBLiMP task ordering, duplicated-key observation, group sample count and 16-subtask discovery:
  PASS; and
- TurBLiMP `acc_norm` recomputation: BLOCKED, `0.34375` versus Harness `0.40625`.

No Slurm job ID, GPU allocation, model load or new scoring run was created. The v1 parity root is
preserved read-only with 406 files / 413,897,338 bytes. Its `structural_parity.json` SHA-256 is
`8bf52585239d6bd61f076ba09a4a8814755d78a46e74fed598081a7a4273e370`; its
`parity_plan.json` SHA-256 is
`d9bee3dda03942767dd12bc567a21e4712207bed45b133839abbe39a6e6a6554`.

The mismatch exposed an implementation error in this contract's prepared interpretation, not a
model outcome. Pinned lm-eval v0.4.12 `api/task.py` computes both lengths, but defines `acc_norm`
with `len(choice)` and defines a separate `acc_bytes` with `len(choice.encode("utf-8"))`.
TurBLiMP declares `acc_norm` and does not declare `acc_bytes`. Therefore the parity validator must
use Python Unicode string length for its decision metric. Byte normalization may be retained only
as a labelled descriptive sensitivity. The upstream `task.py` SHA-256 is
`310d5e10c44a3e66683db374a4be955bee8b697ab9675a47a12bd8330e085784`.

The prepared correction changes only this denominator binding, adds the pinned `task.py` identity,
records byte-normalized sensitivity separately, persists a no-job submission manifest when a
future structural gate blocks, and proposes fresh root
`/vol/tmp2/yesildau/eval_v1_m0_olmo_qualification_parity_v2`. All source artifacts, task order,
sample counts, model/runtime identities, tolerance, heading sensitivity and scientific
prohibitions remain unchanged. It is not executable until the corrected implementation and config
are frozen; those bindings are supplied below.

Those corrected bindings are now frozen:

- corrected implementation commit: `cb48fddadcbaa1e6ef145d6be7d7568359723573`;
- corrected operator SHA-256:
  `bfe2832517f214059539f5cb97763a92407ad9efe62cad98e4ea640f349b9380`;
- corrected parity module SHA-256:
  `a7d66c49224828ed997a29f0e8caeefd0cce93c3ad97351a8188d30fffdcbda0`;
- unchanged heading preprocessor SHA-256:
  `9f331af3df4da84fdd5bfc6b2b52cbbfc4a0fb87d1bf51d4e3de4b01c4f59829`;
- unchanged heading task YAML SHA-256:
  `b8b66fa5ff4ef376596f1d1e046633193f1e261bb77ad40ac9831564a19a7eaa`;
- frozen corrected companion config SHA-256:
  `b855225f13355989877e988e90f8049df790ce0e244348417b42fb31054920b5`.

The user's 2026-08-16 instruction to continue the agreed parity → eval-v1 sequence authorizes this
single fresh v2 test-only correction because it restores the exact pinned upstream definition and
does not select a denominator after observing a scientific model outcome. It authorizes no v3.

## Append-only v2 execution result

V2 preflight passed with no blockers. Structural WikiText parity and TurBLiMP parity both passed
before submission. Heading job `461668` completed on V100 `gruenau1`, and `afterany` finalizer
`461669` emitted `parity_pass`. The final result has no blockers, is explicitly
`test_only_non_scientific`, and records `scientific_work_started=false` and
`eval_v1_frozen=false`.

The canonical WikiText recomputation exactly matched Harness word PPL `13.325301724411347`, byte
PPL `1.6503868248492586` and BPB `0.722804209249961`. TurBLiMP's exact 16-subtask `acc_norm`
macro reproduced `0.40625`; byte-normalized sensitivity was `0.34375`. Markdown heading sensitivity
passed identity and algebra gates and remained descriptive-only.

The complete result and gate are recorded in
[`../../179_M0_OLMO_EVAL_V1_PARITY_EXECUTION_RESULT_AND_FREEZE_GATE_TR.md`](../../179_M0_OLMO_EVAL_V1_PARITY_EXECUTION_RESULT_AND_FREEZE_GATE_TR.md).
The v2 root is immutable. This contract's execution authority is consumed and authorizes no retry,
scientific M0 evaluation, eval-v1 freeze, training, corpus work, cleanup or deletion.
