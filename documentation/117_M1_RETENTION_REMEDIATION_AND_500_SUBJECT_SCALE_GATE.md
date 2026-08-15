# 117 - M1 Retention Remediation and Mandatory 500-Subject Scale Gate

**Date:** 23 July 2026  
**Status:** Seed-42 training/evaluation complete; see Document 118; formal promotion HOLD  
**Authority:** Explicit user decision after the completed Documents 115--116 bridge pilot  
**Supersedes:** Document 109 only where it made Qwen retention work conditional on a positive
Turkish-bridge classification. The negative bridge result remains valid and is not reinterpreted.

## 1. Decision

The project will not proceed to final M2/M3 from a 100-subject acquisition result. A successful
M1 at **500 subjects / 2,500 facts** is now a mandatory scale gate.

The project will not scale the already-failing Qwen recipe unchanged. It will first run one bounded
100-subject retention remediation. A recipe may advance to 500 subjects only after it jointly
passes factual storage, held-out prompt robustness, generic English retention, and replication.

This decision separates two claims:

- Documents 115--116 remain a valid negative result for the tested Turkish bridge recipe.
- Qwen's strong English factual acquisition remains useful enough to justify one explicitly
  authorized M1-retention remediation, independently of bridge promotion.

No M2, M3, 1,000-subject, or 5,000-subject run is opened by this document.

## 2. Why Qwen Is the Primary Candidate

At 100 subjects / 500 facts, Qwen passed the frozen factual gates but failed English retention:

- exact-prefix: 100%;
- held-out hard prompts: approximately 99.9%;
- robust intersection: 99.6% global and 99% minimum relation;
- English PPL ratio: approximately 1.455--1.461, above the 1.25 maximum.

The retained checkpoint sweep in Document 108 showed that early stopping cannot solve this:
update 50 is already at PPL ratio 1.455 when the factual gates first pass. The intervention must
therefore change the learning objective, not merely checkpoint selection.

SmolLM2 remains the low-drift reference. It is not the first remediation target because its
English PPL ratio passes at 1.080 while its all-form robust intersection is only 39.6%.

## 3. Phase 117A - Seed-42 Bounded Retention Discovery

### 3.1 Frozen population and acquisition contract

Both conditions use:

- Qwen/Qwen2.5-1.5B from the authenticated, frozen local base snapshot;
- the same 100 subjects, five relations, and 500 facts;
- the canonical + Form A + Form B acquisition curriculum;
- 3,500 factual training rows and 500 validation rows;
- answer-only factual loss with `supervise_eos: false`;
- LR `5e-5`, 252 optimizer updates, the same effective factual batch, warmup, scheduler,
  checkpoint schedule, seed 42, and data seed 42;
- native Qwen tokenizer and unchanged frozen evaluators.

### 3.2 Conditions

| Condition | Change from the factual contract |
|---|---|
| `q_control_seed42` | None; matched factual-only reproducibility control |
| `q_replay_w0_5_seed42` | Clean English next-token replay loss at coefficient 0.5 on every factual optimizer step |

There is one primary mechanism and one precommitted coefficient. No coefficient sweep is allowed.
A replacement coefficient requires an outcome-blind implementation report showing numerical
invalidity before any factual or PPL outcome for the primary condition is inspected.

The replay implementation must compute two token-normalized losses in the same optimizer step:

```text
L_total = L_fact_answer_only + 0.5 * L_clean_english_next_token
```

This preserves every factual row, factual answer-token exposure, shuffle contract, and optimizer
update. Replay may increase forward-pass compute, but it must not replace factual examples or
silently reduce factual exposure.

### 3.3 Frozen English anchor

The anchor source is `Salesforce/wikitext`, configuration `wikitext-2-raw-v1`, using only its
official **train** split for training anchors and **validation** split for internal validation.
The frozen English PPL evaluator continues to use the disjoint official **test** split.

Before training, anchor materialization must record:

- source dataset/config/split and requested revision;
- deterministic selection seed 42;
- Qwen-native token counts and exact supervised anchor-token budget;
- row counts aligned one-to-one with the 3,500 factual train and 500 validation rows;
- SHA-256 hashes for both JSONL files and the manifest;
- zero occurrence of any of the 100 synthetic subject names;
- a diagnostic count of answer-label occurrences, reported but not treated as leakage by itself
  because many labels are ordinary real-world words or locations;
- proof that no WikiText-2 test row entered the anchor files.

Anchor rows are truncated deterministically to at most 64 Qwen tokens plus EOS. Empty lines,
section-heading-only lines, and duplicate normalized texts are excluded.

## 4. Frozen Seed-42 Evaluation and Selection

Every retained checkpoint is evaluated using the same canonical, A/B, C/D, eight-cell robust,
integrity, generation, and frozen WikiText-2 test PPL suites used in Documents 106--108.

A checkpoint passes only if all conditions hold:

- exact-prefix >= 90%, globally and per relation;
- each required held-out A/B and C/D form >= 80%, globally and per relation;
- eight-cell robust intersection >= 70%, globally and per relation;
- English PPL ratio to Qwen M0 <= 1.25; `< 1.10` remains preferred, not required;
- no dataset-integrity failure, common-knowledge collapse, or generation degeneration.

The selected checkpoint is the earliest checkpoint passing every gate. The control is evidence for
reproducibility and cannot relax the replay condition's thresholds. If neither condition passes,
500-subject scale-up remains blocked and the failure is documented.

## 5. Phase 117B - Seed-43 Replication

Only the seed-42 treatment selected under Section 4 advances. Replication changes model seed and
data seed to 43 while keeping the subject population, factual rows, anchor rows, coefficient,
training budget, checkpoint rule, and thresholds fixed.

Failure on seed 43 blocks scale-up. No third seed or post-hoc coefficient is added automatically.

## 6. Phase 117C - Mandatory 500 Subjects / 2,500 Facts

After seed 42 and seed 43 pass, the same frozen model family and recipe are trained on:

```text
500 subjects x 5 relations = 2,500 facts
```

The 500-subject population must preserve Branch A/B, relation, name type, rarity, popularity, and
object-frequency balance. The first 100-subject population remains nested and is reported
separately to detect scale-induced forgetting.

Before this run, a separate frozen scale manifest must specify the exact 17,500-row curriculum,
anchor construction and token budget, effective factual exposure, checkpoint schedule, runtime and
storage estimate. Thresholds may be made stricter before results are viewed, but not weaker.

The minimum scale-promotion gates are:

- the same percentage gates from Section 4 over all 2,500 facts and per relation;
- English PPL ratio <= 1.25;
- at least 70% of subjects are **eligible subjects**, where an eligible subject has at least four
  of its five facts correct across every required held-out prompt family;
- strict 5/5 eligible-subject count is reported separately;
- the nested original 100-subject subset does not fall below any Section 4 gate;
- no branch or relation collapses and all integrity/generation checks pass.

Passing this gate means that a 500-subject M1 is scientifically eligible for the later causal
design. It does not mean every one of the 500 subjects was learned perfectly; eligible and strict
5/5 counts must both be stated explicitly.

## 7. HU Operational Contract

All anchor files, caches, materialized configs, checkpoints, optimizer state, logs, temporary files,
and raw evaluations must remain under a new `/vol/tmp2/yesildau` experiment root. Nothing large may
be written under `/vol/fob-vol6/mi25/yesildau`.

Before each coordinated submission wave, perform one complete family preflight under `AGENTS.md`:

- home `du`, capacity, and inode state;
- resolved `runs`, `artifacts`, output, cache, log, dataset, and temporary paths;
- queue state;
- exact job list and destinations;
- checkpoint count, bytes per checkpoint, combined family reserve, and retention policy.

After all sibling jobs reach terminal state, perform one post-run audit and record Slurm IDs,
nodes, state, stderr, output roots, selected checkpoint, retained size, manifest, and SHA-256.

## 8. Execution Order

1. Implement and locally test paired replay loss, anchor materialization, manifests, and preflight.
2. Commit/push and synchronize the exact commit on HU.
3. Materialize and audit the frozen anchor corpus on scratch.
4. Run the family preflight and submit seed-42 control + replay as one coordinated wave.
5. Evaluate every retained checkpoint and document the frozen decision.
6. If and only if one treatment passes, run seed-43 replication.
7. Freeze the 500-subject scale manifest and run the mandatory scale gate.
8. Only after a passing 500-subject result, decide whether 500 subjects provide adequate power or
   whether 1,000 subjects are scientifically necessary.

## 9. Current Stop

Implementation was committed as `e5d8685` and the exact factual-surface anchor audit correction as
`ff4170d`; both were pushed to `corpus-update` and fast-forwarded on HU. Local targeted tests pass
(38 tests). HU targeted tests also pass (38 tests); the wider HU suite was observed running without
an early failure, but its detached terminal summary was not used as a gate after the SSH client
returned before completion.

The first coordinated seed-42 wave was submitted once on 23 July 2026:

| Role | Slurm ID | Initial state |
|---|---:|---|
| family storage/path/inode preflight | 411273 | RUNNING on `gruenau` |
| frozen anchor materialization | 411274 | PENDING (dependency) |
| control + replay training array | 411275_[0-1%2] | PENDING (dependency) |
| family post-run audit | 411276 | PENDING (dependency) |

The family preflight records a 500 GiB combined reserve, 11 expected checkpoints per condition,
22 family checkpoints plus two final models, all high-volume paths under
`/vol/tmp2/yesildau/m1_retention_v1`, and the post-evaluation cleanup policy. The first preflight
stderr was empty. A frontend `sacct` query returned a transient Munge/database authentication
error; this did not affect the jobs, whose dependency states were visible through `squeue`.

Do not submit a duplicate. Next verify preflight 411273, anchor manifest 411274, then both training
tasks' allocation, GPU, stdout/stderr, and terminal results. Seed 43 and the 500-subject run remain
blocked until frozen evaluation shows a seed-42 treatment passing every Section 4 gate.

### 23 July 2026 - Preflight manifest-field correction and resubmission

Preflight 411273 failed before any anchor or training work because it required the optional
`tokenizer_source_path_absolute` field in the Qwen base manifest. The frozen Qwen manifest stores
its model and tokenizer together under `local_path_absolute`, which is also the fallback already
used by the training core and the corrected Document 116 evaluator. The failure was operational,
not a storage, model, or scientific-result failure. No training output was created. Permanently
unsatisfied jobs 411274--411276 were explicitly cancelled.

Commit `87a9ed8` changes preflight to resolve the tokenizer with the same ordered rule as training:
explicit absolute tokenizer path, then explicit tokenizer path, then the frozen model directory.
Local 38-test validation and shell syntax checks passed; the commit was pushed and fast-forwarded
on HU. The corrected wave was submitted once:

| Role | Slurm ID | Initial state |
|---|---:|---|
| corrected family preflight | 411277 | RUNNING on `gruenau`, initial stderr empty |
| anchor materialization | 411278 | PENDING (dependency) |
| control + replay training array | 411279_[0-1%2] | PENDING (dependency) |
| post-run audit | 411280 | PENDING (dependency) |

Do not duplicate this corrected wave. Check after approximately 5--10 minutes for the preflight
manifest and anchor progress; training timing begins only after both dependency gates pass.

### 23 July 2026 - Corrected preflight/anchor pass and live training check

Preflight 411277 passed at commit `87a9ed8` with home usage 8,298,388 KiB (approximately 7.91 GiB),
122,983,641,088 KiB available on `/vol/tmp2`, the frozen 500 GiB reserve, 3,500/500 factual rows,
252 expected updates, and all destinations under `/vol/tmp2/yesildau/m1_retention_v1`.

Anchor job 411278 completed and froze 3,500 train plus 500 validation anchors. Selected train and
validation anchor SHA-256 values are respectively
`ef289d5e4a6780506a55ffb67337c6742768cf287b543256b77ea95f681de48b` and
`65c8a9b52a21385d687db6bcd9186d84e5473cb3bf9690e653ec8f30ee9f5b94`.
The train/validation supervised token budgets including EOS are 171,145 and 23,761. No selected
anchor contains one of the 100 synthetic subject surfaces. Ordinary answer-label surfaces occur
1,988 times in selected train rows and 284 times in validation, as anticipated and recorded as a
diagnostic rather than subject-bound fact leakage. The only anchor stderr was the harmless warning
that the public WikiText download was unauthenticated.

Tasks 411279_0 (control) and 411279_1 (replay) started together on `gruenau9`, assigned distinct
A100-80GB devices IDX 0 and IDX 1. Both initial and ten-minute training stderr files were empty.
The node nevertheless had unrelated/orphan `TextJEPA` processes already holding approximately
40.5 GiB and 37.0 GiB on those assigned devices before this project's trainers loaded. At the live
check, this project's Python processes used approximately 18.3 GiB and 19.5 GiB; aggregate use was
60.6 GiB and 56.5 GiB, leaving approximately 21--25 GiB headroom with no OOM. Control had produced
checkpoint-25 (approximately 8.7 GiB active tree); replay was active but had not yet reached its
first checkpoint. The jobs were left running because memory was stable, progress was demonstrated,
and stderr was clean. Compute contention may extend replay runtime toward 90--140 minutes; do not
duplicate. Recheck checkpoint progress and stderr after approximately 20--30 minutes.

At 44m28s elapsed, control had reached checkpoint-150/252 and replay checkpoint-75/252. Stable
checkpoint intervals were approximately 6.6 minutes per 25 updates for control and 12.6 minutes
per 25 updates for replay, including periodic evaluation/save overhead. Both stderr files remained
zero bytes; project GPU use remained approximately 18.3/19.5 GiB while the unrelated processes
remained resident. Projected remaining times were approximately 30--35 minutes for control and
90--100 minutes for replay. Replay was projected to finish inside its 2h30 limit with only roughly
10--15 minutes of margin, so it remains a live timing risk but not yet a failure. Leave both jobs
running and recheck after approximately 25--30 minutes; do not submit replacements while progress
continues.

### 23 July 2026 - Seed-42 training family completed

Both tasks reached update 252 and wrote complete training manifests:

| Condition | Runtime | Checkpoints | Final model weight | Error scan |
|---|---:|---:|---:|---|
| control | 4,059.99 s (67.7 min) | 25--250 every 25 plus 252 (11) | 3,087,467,144 bytes | no traceback/OOM/runtime-error/NaN/Inf signature |
| replay w=0.5 | 7,535.79 s (125.6 min) | 25--250 every 25 plus 252 (11) | 3,087,467,144 bytes | no traceback/OOM/runtime-error/NaN/Inf signature |

Each active run tree is approximately 98 GiB; the complete family tree is approximately 196 GiB,
within the frozen 500 GiB reserve. The replay implementation recorded 12,600 training microbatches,
mean factual loss 0.2772885, mean anchor loss 0.7599715, and coefficient 0.5. The Hugging Face
aggregate `train_loss` of 32.8637 is accumulation-scaled reporting and is not an M1 gate; frozen
factual/robustness/PPL evaluation determines promotion.

Post-run job 411280 completed the material storage checks before its final accounting command:
home remained 8,298,388 KiB (approximately 7.91 GiB), no new >500 MiB home file appeared,
`/vol/tmp2` retained approximately 115 TiB free with 3% inode use, and the family occupied 196 GiB.
The script then exited non-zero because cluster `sacct` could not access the Munge/slurmdbd socket.
This is an accounting-service/audit-script robustness failure, not a training or storage failure.
A compact recovery audit should tolerate unavailable `sacct` while preserving manifest and
`scontrol` evidence.

No condition is promoted from training loss. The next scientific operation is the precommitted
all-checkpoint exact-prefix, held-out A/B/C/D, eight-cell robust, integrity/generation, and frozen
WikiText-2 PPL evaluation. Seed 43 and 500 subjects remain blocked until that result is summarized.

### 23 July 2026 - Frozen checkpoint-evaluation implementation contract

Before inspecting any factual or PPL outcome, the evaluation wave is frozen as follows:

- root: `/vol/tmp2/yesildau/m1_retention_v1/evaluation_v1`;
- 22 read-only checkpoint tasks: 11 control and 11 replay, steps
  25/50/75/100/125/150/175/200/225/250/252;
- maximum three concurrent GPU tasks;
- `gruenau9` and `gruenau10` excluded because of observed unrelated/orphan GPU processes;
- no new model checkpoint or model copy; only model manifests and compact evaluator outputs;
- combined new-output reserve: 50 GiB;
- frozen Qwen M0 WikiText-2 PPL 14.6988390227992 and token-stream hash
  `be2effefc9f0655b0fc5bc3052ecfd18b51bdfa48bffa1ab2d4f0c217b81c78f`;
- exact-prefix >=90% globally and per relation;
- minimum A/B and C/D relation-form/scaffold accuracy >=80%;
- eight-cell robust intersection >=70% globally and per relation;
- PPL ratio <=1.25;
- zero empty/near-empty generic generations and zero synthetic-subject intrusion;
- within each condition, select the earliest checkpoint passing every gate;
- seed 43 opens only if replay has a fully passing checkpoint.

The dependency order is preparation -> family storage/path/inode preflight -> 22-task evaluation
array -> frozen summary, with one evaluation post-run audit. A separate compact recovery audit
closes the completed training family while tolerating unavailable `sacct`; it may use training
manifests and `scontrol` as accounting fallback. Expected wall time after GPU allocation is roughly
90--150 minutes for the throttled family. No threshold or checkpoint may be changed after results
appear.

The first submission attempt created only recovery-audit 411287, preparation 411288, and pending
preflight 411289 before Slurm rejected the evaluation array: excluding both `gruenau9` and
`gruenau10` removed the entire A100-80GB inventory. No evaluation task or result was created.
Preflight 411289 was cancelled while the preparation and recovery audit were preserved.

An immediate read-only node audit showed that the supposedly idle A100 nodes were not usable:
`gruenau10` GPUs held approximately 74.2/42.3/38.1 GiB through VLLM/TextJEPA processes, while
`gruenau9` had already shown the two large TextJEPA processes during training. The frozen evaluation
is therefore operationally amended, before any result exists, to use `gpu:rtx3090:1`, excluding
currently allocated `guppi6,guppi7`. RTX3090 BF16 inference is already validated in this project;
model, checkpoint, prompts, tokenization, candidate batching, metrics, thresholds, and selection
rule remain unchanged. The 22-task throttle remains three. A prepared-wave resume launcher prevents
duplicate manifest preparation.

Implementation commit `0c9c752` passed 41 targeted HU tests. The initial submission created
recovery audit 411287 and preparation 411288; no evaluation task was accepted. Recovery audit
411287 then passed all storage checks with the expected warning that `sacct` was unavailable:
home remained below 10 GiB, no new large home file appeared, `/vol/tmp2` remained approximately
115 TiB free at 3% inode use, and the training family remained 196 GiB. Preparation 411288 was
still hashing the 22 read-only checkpoint manifests at 4m33s with empty stdout/stderr. Per the
project's five-minute monitoring rule, leave it running and do not wait or duplicate.

Commit `13bafe6` changes only evaluation hardware routing to `gpu:rtx3090:1`, excludes allocated
guppi6/7, and adds a prepared-wave resume launcher. Local tests pass. It must be fast-forwarded on
HU only after preparation 411288 reaches terminal state; then run the new preflight and evaluation
chain. No scientific result exists yet.

Preparation 411288 subsequently completed with an empty stderr and froze registry SHA-256
`66d8864cac30b6422148ebbe956849f2040c538f4d6556d146687ae6416a0e54`; all 22 tasks and both
conditions were present and no result namespace existed. Commit `13bafe6` was fast-forwarded on HU;
four targeted HU tests and shell syntax passed. Slurm `--test-only` placed the RTX3090 task on clean
idle node `guppi5`.

The prepared wave was submitted once:

| Role | Slurm ID | Initial state |
|---|---:|---|
| evaluation family preflight | 411297 | RUNNING on `gruenau`, initial stderr empty |
| 22-task checkpoint evaluation, throttle 3 | 411298_[0-21%3] | PENDING (dependency) |
| frozen summarizer | 411299 | PENDING (dependency) |
| evaluation post-run audit | 411300 | PENDING (dependency) |

Do not duplicate. Expected wall time after the first evaluation tasks start is approximately 2--4
hours on RTX3090, depending on per-checkpoint hard/PPL evaluation time. Under the five-minute rule,
recheck preflight and first-task allocation after approximately 5--10 minutes.

Preflight 411297 passed with home 8,298,592 KiB, 122,778,526,720 KiB available on `/vol/tmp2`,
22 tasks, throttle three, RTX3090 routing, and guppi6/7 excluded. Tasks 411298_0 and _1 entered
RUNNING on guppi5 and task _2 on guppi8; the remaining tasks were correctly held by the array
throttle. Initial stderr files were zero bytes. A diagnostic `srun --overlap` could not attach to
the array parent under this Slurm version, but `squeue` and `scontrol` independently confirmed all
three RUNNING allocations; this diagnostic failure did not alter the jobs. Leave the wave running.

### 24 July 2026 - Evaluation complete; integrity adjudication required

All 22 evaluation tasks, frozen summary 411299, and post-run audit 411300 completed. The unchanged
summarizer reports `retention_remediation_failed`: control never overlaps factual success with the
PPL gate, while replay step 50 passes every factual, held-out, robust-intersection, and PPL gate but
fails the literal generic-integrity veto. Its metrics are 99.8% exact, 99% minimum exact relation,
100% minimum A/B, 91% minimum C/D, 98% robust global, 91% robust minimum relation, and PPL ratio
1.24684. The only integrity flag is the correct continuation `navigation` plus EOS for the compass
purpose question; the evaluator labels every output of at most two token IDs as near-empty without
examining lexical content. Intrusion count is zero and generic-completion top-1 is 96.67%.

Document 118 preserves the literal frozen failure and records the evaluator defect separately.
No threshold is relaxed and no checkpoint is formally promoted yet. A narrow, tested lexical-empty
correction and deterministic re-summary are open. If corrected seed-42 identifies replay step 50,
seed-43 replication opens; the 500-subject gate remains blocked until that replication passes.
Post-wave storage remained safe: home approximately 7.91 GiB, `/vol/tmp2` approximately 115 TiB
free at 3% inode use, training tree approximately 196 GiB, and evaluation tree approximately
404 MiB.
