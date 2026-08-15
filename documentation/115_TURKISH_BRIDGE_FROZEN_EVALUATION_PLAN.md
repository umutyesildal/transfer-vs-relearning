# 115 - Turkish Bridge Frozen Evaluation Plan

**Date:** 2026-07-22  
**Status:** FROZEN BEFORE EVALUATION; implementation and HU preflight pending  
**Authority:** Documents 100, 109, 112--114 and `AGENTS.md`

## 1. Purpose And Scope

Qwen2.5-1.5B and SmolLM2-1.7B Turkish bridge training completed successfully from their frozen M1
checkpoints. This phase evaluates the already-created endpoints. It does not retrain a model,
change the Turkish dose, select a threshold after seeing results, open M2/M3, or authorize scale-up.

For each family the exact four-state sequence is:

| State | Endpoint |
|---|---|
| `m0` | pinned base model before English synthetic acquisition |
| `m1` | frozen English-acquisition endpoint used to start bridge training |
| `low` | Turkish bridge checkpoint at optimizer update 32 / 262,144 model tokens |
| `full` | Turkish bridge checkpoint at optimizer update 128 / 1,048,576 model tokens |

The update-64 and update-96 checkpoints are not evaluated in the frozen primary pilot. They remain
retained on scratch until the result and artifact decision are complete.

## 2. Frozen Inputs

The evaluation uses Contract V2 manifest SHA-256
`f3248f07839f09665d571c22cf729c548e6c7b6a8a88f12fde2260903c739e5e`, its 1,500-probe registry,
its model-specific/shared eligibility files, and the Relation V2 candidate inventories.

English generic loss uses the same frozen WikiText-2 raw test JSONL as the preceding M1 analyses:

```text
/vol/tmp2/yesildau/general_capability_v1/wikitext2_raw_test.jsonl
SHA-256 578a0879807f928e423f61631ee697a865af006df21e60e10e25a534c345097a
```

Turkish generic loss uses the frozen 256-document Contract V2 validation subset:

```text
/vol/tmp2/yesildau/turkish_bridge_v1/contracts/v2/dose/validation_documents.jsonl
SHA-256 586e3fd343c8c04fddcd5e9cdfb4a82ae8df221c5ea764500c76e7adf94b8e52
```

Both corpora are scored as full documents with an EOS boundary per document, 512-token blocks,
token-weighted causal NLL, perplexity, and a 2,000-sample seed-42 block bootstrap interval. PPL is
compared within a model family, never as an absolute cross-tokenizer model ranking.

## 3. Frozen Retrieval And Decision Analysis

At every state, all 500 facts are evaluated in `EN->EN`, `TR->EN`, and `TR->TR`. The primary score
is mean answer-token log probability across the complete relation-family candidate inventory;
top-1 rank and correct-versus-best-distractor margin are retained per probe. No free-generation
result replaces this primary candidate-access measure.

The precommitted promotion classifier from Document 109 is applied on the model-specific
`eligible_3_of_4_heldout` fact set. The following are mandatory sensitivity reports, not alternate
post-hoc promotion targets:

- all 500 facts;
- the model-specific strict 8/8 set;
- the 357-fact shared eligible intersection;
- the 196-fact shared strict intersection.

Every report includes all three directions, all five relations, paired subject bootstrap changes,
English factual retention, English/Turkish PPL, and each frozen gate. A family is not promoted by
choosing whichever stratum looks best after evaluation.

## 4. Execution Layout And Storage

One coordinated evaluation family contains two parallel sibling jobs, one per model. Each sibling
loads its four states sequentially, which limits the family to two GPUs instead of eight. The
planned hardware is one RTX 3090 per sibling; this is an inference-only infrastructure choice and
does not change weights, probes, scores, thresholds, seeds, or corpora. BF16 is used when supported.

All manifests, raw per-probe outputs, PPL block rows, summaries, logs, caches, and temporary files
must remain under:

```text
/vol/tmp2/yesildau/turkish_bridge_v1/evaluation_v1
```

The expected output is below 5 GiB; the family preflight reserves 10 GiB including temporary and
log headroom. It creates eight small endpoint manifests but zero checkpoints and downloads no
model. Existing weights remain read-only on `/vol/tmp` or `/vol/tmp2`. One complete preflight
immediately before the wave must check home usage, capacity, inodes, resolved paths, exact input
hashes, all eight endpoints, queue state, expected outputs, and retention. One post-family audit is
required after both sibling jobs reach a terminal state.

## 5. Runtime And Stop Conditions

Expected runtime is approximately 60--150 minutes per model, with both models running in parallel;
the conservative Slurm limit is four hours. After submission, verify node/GPU selection, the
foreign-process guard, endpoint contract, first output progress, and stderr. Leave the jobs running
if more than five minutes remain and report when the user should check again.

Stop before model load if home exceeds the protected threshold, an output/cache/log/tmp path
resolves to HU home, an input hash or endpoint differs, the evaluation namespace already exists,
the GPU contains another compute process, or the preflight is stale. Preserve partial scratch
results for resume and diagnosis; never submit a duplicate merely because output is quiet.

## 6. Decision After Results

- If Qwen is promising on its frozen eligible set, open only the bounded Qwen retention branch in
  Document 109C.
- If SmolLM2 alone is promising, prepare the separate SmolLM prompt-robustness/eligibility decision.
- If both are promising, retain both results and prioritize Qwen for the bounded intervention.
- If neither is promising, do not scale; audit dose, localization, corpus, and evaluator behavior.

M2, M3, seed-43 replication, 500-subject training, and final-scale M1 remain on HOLD until this
result is documented and its precommitted decision branch is explicitly opened.

## 7. Implementation And HU Submission - 2026-07-22

The evaluation implementation was committed and pushed as `e032fb2`, then HU was fast-forwarded
to exact commit `e032fb24b8cd2ebcbf0780fae6543a382d12e299`. Shell/Python syntax checks and the
authoritative 12-test bridge suite passed on HU. A broader test invocation produced no failure but
the interactive SSH wrapper ended after showing 37% progress, so it is not recorded as a complete
suite pass.

The coordinated wave was submitted exactly once:

| Job | Role | Initial state |
|---:|---|---|
| 411248 | storage/hash/path/endpoint preflight and compact contract materialization | RUNNING on `gruenau` |
| 411249_[0-1%2] | parallel Qwen and SmolLM2 four-state evaluation | PENDING on `afterok:411248` |
| 411250 | one family post-evaluation storage audit | PENDING on `afterany:411249` |

At the first 12-second check, preflight stderr was empty. The evaluation and audit remained
dependency-gated; no GPU model load or output result had started. Do not submit a duplicate while
411248 is hashing and freezing the eight endpoint manifests.

## 8. Passed Preflight And Verified GPU Startup - 2026-07-22

Preflight 411248 passed with empty stderr. It recorded home at 8,298,040 KiB, `/vol/tmp2` with
122,984,260,608 KiB available (approximately 115 TiB), 3% scratch inode use, all repository-local
artifact/dataset paths resolving to approved scratch, zero new checkpoints, and the 10 GiB
evaluation-output reserve. The frozen eight-endpoint evaluation manifest SHA-256 is
`785eff7dbe56b993a38538da33917385691aa151fc55f84fc91bae5463626f12`.

Both evaluation siblings then started on `guppi8`, each on a distinct RTX 3090 with a 15 MiB clean
baseline and zero foreign compute processes:

| Task | Model | Verified progress at 4m36s | stderr |
|---:|---|---:|---:|
| 411249_0 | Qwen | M0 bridge 700/1,500 probes | 0 bytes |
| 411249_1 | SmolLM2 | M0 bridge 550/1,500 probes | 0 bytes |

Audit 411250 remains correctly dependency-gated. No OOM, traceback, path failure, duplicate, or
orphan GPU process is present. Leave both jobs running. At the observed M0 rate, check again in
approximately 10--15 minutes for M0 completion and PPL/next-state transition; complete four-state
results are still expected roughly 50--100 minutes after this checkpoint.

## 9. Qwen Tokenizer-Manifest Failure; SmolLM2 Continues - 2026-07-22

At the 16m21s family check, both models had completed the full 1,500-probe M0 bridge evaluation and
both English/Turkish M0 PPL runs. SmolLM2 had additionally completed all 1,500 M1 bridge probes and
remained running in its M1 PPL/next-state sequence. Its stderr contained only model-loading output,
the Transformers dtype deprecation, and the expected warning that the concatenated token stream is
longer than model context before it is split into 512-token scoring blocks; no traceback or OOM was
present.

Qwen task 411249_0 stopped at the start of M1 bridge scoring with:

```text
ValueError: No answer tokens detected for the prompt/candidate boundary
```

This was not a GPU, OOM, storage, corpus, or training failure. Inspection showed that the generated
Qwen M0 manifest correctly used the pinned base tokenizer snapshot, but the generated Qwen M1
manifest incorrectly set `tokenizer_source_path_absolute` to the tokenizer-incomplete update-50
checkpoint directory. The generic local-manifest helper replaced the explicit tokenizer fallback
already present in Contract V2 with the checkpoint model path. The same construction also affects
the unstarted Qwen low/full evaluation manifests. Therefore Qwen M1/low/full results from this
contract are invalid/unavailable; no threshold or model conclusion may be drawn from the failure.

The completed Qwen M0 bridge and PPL artifacts used the correct tokenizer and remain valid,
reusable frozen inputs. Do not rerun them by default. Preserve the failed V1 contract and stderr as
evidence; do not edit its endpoint manifests in place. After SmolLM2 and audit 411250 finish, the
correct recovery is an append-only Qwen-only evaluation contract that preserves the explicit base-
tokenizer fallback, verifies it before GPU submission, reuses the hashed M0 result, and evaluates
only M1/low/full. SmolLM2 task 411249_1 must remain uninterrupted.

## 10. SmolLM2 Final Result And Family Audit - 2026-07-22

Task 411249_1 completed all four bridge and PPL states and wrote the frozen classifier result.
Audit 411250 also completed with empty stderr. Home remained 8.0 GiB; `/vol/tmp2` retained
approximately 115 TiB free at 3% inode use. The V1 evaluation tree is only 4.2 MiB, all under
scratch. No new large home file or checkpoint was created.

The precommitted primary population is SmolLM2's 359 model-eligible facts. Its classification is
`not_viable_under_frozen_pilot`. Every required sensitivity population agrees: all 500 facts,
model-strict 198, shared-eligible 357, and shared-strict 196 are also not viable.

### 10.1 PPL And English Retention

| State | English PPL | ratio to M0 | Turkish PPL |
|---|---:|---:|---:|
| M0 | 15.9242 | 1.0000 | 9.4237 |
| M1 | 17.1981 | 1.0800 | 10.7784 |
| low | 16.8838 | 1.0603 | 10.0873 |
| full | 16.4436 | 1.0326 | 9.4265 |

Full Turkish adaptation clearly affected the language model: Turkish PPL fell from 10.7784 at M1
to 9.4265 (ratio approximately 0.875), passing the frozen `<= 0.95` gate. English PPL also moved
back toward M0 rather than degrading, and EN->EN eligible-fact top-1 was retained from 96.66% at M1
to 96.10% at full. Therefore this is not a failed adaptation dose or catastrophic-forgetting case.

### 10.2 Cross-Lingual Fact Access

| State | EN->EN top-1 | TR->EN top-1 | TR->TR top-1 | TR->EN mean margin |
|---|---:|---:|---:|---:|
| M0 | 0.84% | 1.11% | 1.11% | -4.1783 |
| M1 | 96.66% | 20.61% | 11.14% | -2.9915 |
| low | 97.49% | 20.06% | 8.91% | -2.8581 |
| full | 96.10% | 16.99% | 7.24% | -2.7890 |

Low-dose TR->EN change was essentially zero at the paired-subject level (estimate +0.0010, 95% CI
[-0.0233, +0.0255]). Full-dose change was negative (estimate -0.0335, 95% CI [-0.0703,
+0.0008]). Full TR->EN remained below the 30% absolute gate, retained a negative mean margin,
missed the M0-adjusted gain gate, and reached at least 20% accuracy in fewer than three relations.
The adaptation-gain/preserved-open-bridge gate also failed.

The defensible interpretation is narrow: SmolLM2 stored the eligible English facts, the Turkish
Wikipedia dose measurably improved Turkish PPL without English collapse, but that dose did not open
or improve robust Turkish-prompt access to those facts. This is a valid negative bridge result, not
evidence that training, PPL scoring, or storage failed.

Qwen still has no valid M1/low/full result because of the recorded tokenizer-manifest construction
failure. The next authorized operational work is the append-only Qwen-only recovery described in
Section 9; no model-family comparison or Phase 109 branching is final until it completes.
