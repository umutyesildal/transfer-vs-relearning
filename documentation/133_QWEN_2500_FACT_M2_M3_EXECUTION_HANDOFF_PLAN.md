# 133 - Qwen 2,500-Fact M2/M3 Execution Handoff Plan

**Date:** 2026-07-31  
**Status:** Execution handoff; preparation may continue, but M2/M3 training remains gated  
**Audience:** A future AI agent continuing the HU implementation and execution  
**Scope:** Only the ordered 2,500-fact M2/M3 readiness and execution plan

## 1. Objective

Use the two frozen, independently replicated Qwen M1 artifacts to run the controlled Turkish
adaptation comparison at 500 subjects / 2,500 facts:

```text
Qwen M1 seed 42, step 75 -> M2-42 and M3-42
Qwen M1 seed 43, step 50 -> M2-43 and M3-43
```

Every M2 and M3 arm starts independently from its selected M1 artifact. M3 is never a continuation
of M2. The core first family contains M2-clean and M3-fact only; M3-lexical is optional later work
and is not a blocker.

## 2. Completed prerequisites

The next agent must not repeat these tasks:

- Qwen 2,500-fact English M1 passed all frozen gates in seed 42 and seed 43;
- the selected endpoints are seed-42 step 75 and seed-43 step 50;
- both selected model-only artifacts have manifests and SHA-256 records;
- an authorized verified durability copy exists in HU home;
- the Turkish Wikipedia corpus is cleaned, contamination-audited, split, hash-frozen, and stored
  on scratch;
- the 500-subject population is exactly balanced: 250 Branch A and 250 Branch B subjects;
- the local pre-M2 implementation is committed and pushed as `b7ce9dc`;
- local code can build 60,000 bilingual hard probes, 24 balanced evaluation slices, 1,250 Branch-B
  Turkish factual rows, and matched pretokenized M2/M3 blocks.

Do not run another M1 optimization, Qwen seed, SmolLM remediation, Turkish corpus build, or subject
selection step under this plan.

## 3. Phase A - synchronize and validate HU code

1. Inspect the local and HU Git status and preserve unrelated files.
2. Fast-forward HU branch `corpus-update` to commit `b7ce9dc` or a documented narrow successor.
3. Run the authoritative tests on a compatible compute node.
4. Run Python compilation, shell syntax, and Git whitespace checks for every new launcher.
5. Record the exact commit used by all following materialization and evaluation jobs.

No training is authorized by completing Phase A.

## 4. Phase B - review and freeze Turkish templates

Review every Turkish Form A/B/C/D question and each of the five canonical Turkish factual sentence
templates in:

```text
src/transfer_vs_relearning/data/qwen_pre_m2.py
```

Require:

- grammatical Turkish;
- equivalent relation meaning across Forms A/B/C/D;
- no accidental answer cue;
- no born-in/lives-in or other relation ambiguity;
- factual rows state exactly one correct subject-relation-object binding;
- no Branch A factual row.

Any correction must occur before canonical HU materialization. After materialization, use a new
append-only version rather than overwriting a frozen registry.

## 5. Phase C - materialize the compact pre-M2 contract

Run the compact builder on HU with a new scratch-only output root:

```text
scripts/build_qwen_pre_m2_contract.py
```

The result must contain:

- 500 selected subjects;
- 2,500 facts;
- 250/250 Branch A/B subject balance;
- 1,250/1,250 Branch A/B fact balance;
- 60,000 unique bilingual hard probes;
- 24 evaluation slices with 2,500 probes each;
- 1,250 unique correct Turkish Branch-B factual rows;
- source and output SHA-256 hashes;
- an append-only manifest.

Perform the mandatory HU home, capacity, inode, resolved-path, and large-home-file audit. All new
materialized data and logs must remain on scratch.

## 6. Phase D - run the two current-M1 bilingual baselines

Before any Turkish training, verify and evaluate both frozen Qwen artifacts:

1. seed-42 step 75;
2. seed-43 step 50.

For each artifact:

- verify the selected manifest and declared file hashes;
- load model weights plus the frozen shared tokenizer;
- evaluate EN-to-EN, TR-to-EN, and TR-to-TR;
- cover Forms A/B/C/D under direct and QA scaffolds;
- report global, relation, form, scaffold, Branch A/B, and robust-intersection results;
- re-establish English and Turkish generic PPL baselines;
- check forced-choice binding, tokenizer boundaries, empty answers, and synthetic intrusion;
- preserve compact per-probe results and hashes.

The two seed baselines and their frozen evaluation slices may run in parallel because neither
depends on the other's result and every metric/probe is fixed in advance. Apply a bounded array
throttle and one coordinated family preflight. Do not select a preferred seed after the outcomes.

Low Turkish retrieval at M1 is not a stop condition. A failure to reproduce the frozen English M1
gate, an artifact/hash mismatch, or an evaluator error is a stop condition.

## 7. Phase E - freeze the M2/M3 adaptation contract

After the bilingual baseline artifacts are complete, record before training:

1. the number of complete exposures (`fact_cycles`) of all 1,250 Branch-B facts;
2. the fixed optimizer-update endpoint;
3. the shared checkpoint schedule;
4. the primary and secondary bilingual outcomes;
5. the success/failure gates and causal estimand;
6. the two seed identities and matched data-order seeds;
7. the retention and cleanup policy.

Do not choose different factual doses, endpoints, or checkpoint rules for M2 and M3. Do not use
observed Turkish factual outcomes to choose an arm-specific checkpoint.

## 8. Phase F - materialize matched M2/M3 inputs

Use:

```text
scripts/materialize_qwen_m2_m3_blocks.py
```

Materialize one frozen shared validation set and the matched training inputs:

```text
M2-clean = generic Turkish blocks with no target synthetic binding
M3-fact  = the same number of blocks, with deterministic generic-token positions replaced by
           complete Turkish Branch-B factual sentences
```

The materialization must prove:

- identical block size and block count;
- identical total supervised-token budget;
- identical update budget;
- deterministic replacement positions;
- exactly the precommitted number of Branch-B fact exposures;
- zero Branch-A factual exposure;
- M3 factual material replaces generic material rather than adding tokens;
- M2 contamination audit passes;
- source files, output files, configs, order, and audit reports are hash-frozen.

This CPU materialization may run independently of completed baseline summarization once Phase E's
factual dose and endpoint have been frozen. It must finish before any training smoke.

## 9. Phase G - smoke and launch readiness

Before the principal family:

1. validate all prompt/candidate tokenizer boundaries;
2. validate every pretokenized block length and full attention mask;
3. run a short M2 smoke and a short M3 smoke from one selected artifact;
4. confirm finite loss, correct dataset identity, expected update count, and checkpoint/resume
   behavior;
5. run a compact English factual-retention check after the smoke;
6. complete the mandatory storage, inode, path, cache, log, temporary-file, checkpoint-size, and
   retention preflight;
7. confirm that no principal output root already exists.

M2 and M3 smoke jobs may run in parallel only after one common preflight passes and the allocated
devices are independently clean. A failed smoke does not authorize changing a scientific variable
without a new documented amendment.

## 10. Phase H - run the principal M2/M3 family

The four sibling runs are:

```text
M1-42 -> M2-42
M1-42 -> M3-42
M1-43 -> M2-43
M1-43 -> M3-43
```

M2 and M3 within a seed must share:

- starting M1 artifact family;
- adaptation seed and data-order seed;
- total block/token/update budget;
- optimizer and scheduler settings;
- batch decomposition;
- checkpoint schedule and fixed endpoint;
- generic Turkish source and validation set.

Only correct Branch-B factual exposure differs.

Once the full contract is frozen, M2 and M3 sibling runs may be submitted in parallel. The two seed
families may also run in parallel because their independent identities and analysis rules are
already fixed. A staged seed-42 family followed by seed-43 is also permitted when the purpose is
only operational validation; no scientific setting may change between stages after inspecting
seed-42 outcomes.

## 11. Phase I - evaluate and summarize

After training, evaluate the frozen endpoint of every arm with the same bilingual contract used at
M1 baseline. Report separately:

- M1-to-M2 change for Branch A and Branch B;
- M1-to-M3 change for Branch A and Branch B;
- M3-minus-M2 difference-in-differences;
- EN-to-EN retention;
- TR-to-EN and TR-to-TR without merging them;
- English and Turkish PPL;
- relation, form, scaffold, branch, name, rarity, popularity, and frequency results;
- robust intersections, margins, confidence intervals, failures, and missing results.

Evaluation jobs may be parallelized by frozen seed, arm, direction, form, or scaffold. Summary and
causal analysis must wait until every required evaluation and post-run storage audit is complete.

## 12. Terminal readiness definition

The project is ready to start principal M2/M3 training only when all of the following are true:

- Turkish templates are reviewed and frozen;
- compact registries are materialized and hash-verified on HU scratch;
- both selected M1 artifacts reload correctly;
- both bilingual/PPL baseline packages are complete;
- factual cycles, endpoint, outcomes, gates, and estimand are frozen;
- matched M2/M3 inputs pass all balance and contamination assertions;
- smoke and resume checks pass;
- mandatory storage/path/queue/device preflight passes;
- no principal output already exists.

Any later agent must document job IDs, terminal states, paths, manifests, metrics, stderr status,
and post-run storage audits in the next numbered result report. Do not rewrite this plan or earlier
negative reports to hide failures.

## 13. Explicit exclusions

This handoff intentionally does not prescribe:

- GPU/node allocation strategy beyond mandatory clean-device and preflight rules;
- queue-dependent timing choices;
- M3-lexical execution;
- another M1 or SmolLM experiment.

Those decisions may be made separately from live HU conditions without changing this ordered
M2/M3 scientific plan.

## 14. Execution outcome and handoff closure

This handoff was executed on 2026-08-01--02. The detailed chronological operational record and
complete aggregate result package are in Document 136 §§18--24; this append-only section closes the
handoff without rewriting the original plan or hiding any failed infrastructure attempts.

### 14.1 Readiness and principal execution ledger

| Handoff phase | Final status | Evidence / terminal record |
|---|---|---|
| Turkish template and evaluator corrections | complete | Document 134 §3; ambiguity correction, answer-language and loader fixes |
| Compact 2,500-fact bilingual registry | complete | 60,000 probes, 24 slices, 1,250 Branch-B factual rows; Documents 134--135 |
| Frozen M1 bilingual baseline and PPL | complete | Baseline array `439788`; final CI/PPL jobs `439955_1` and `439956`; Document 134 §22 |
| Phase-E contract freeze | complete | Four factual cycles, checkpoint-128 endpoint, fixed estimand and gates; Document 135 §§1--3 |
| Matched M2-clean/M3-fact materialization | complete | Job `439961`; `matched_m2_m3_blocks_ready`, 1,048,576 tokens/arm, 5,000 Branch-B exposures, zero Branch-A exposure |
| Technical smoke and resume rehearsal | complete | Smoke array `439983_[0-1]`; both reports passed; Document 135 §10 |
| Principal M2/M3 training | complete | Preflight `439988`; initial `439989_0`; clean retry `439996_[1-3%1]`; all four manifests `status=complete` |
| Endpoint evaluation | complete | Main array `440344`; controlled retry preflight `440633`; retry array `440634_[83-95%3]`; 96/96 summaries |
| Strict assembly and bootstrap analysis | complete | `assembled_20260802T2315Z`; `metrics_20260802T2315Z`; integrity `passed` |
| Frozen gate application | complete | `gate_20260802T2325Z/final_gate_report.json`; operational validity/retention passed, primary interaction failed |

The 13-slice retry was limited to the missing M3 seed-43 tasks `83--95`. The original pending
tasks failed the synchronized launcher's commit guard before evaluator execution; they were
infrastructure evidence, not scientific observations. The retry used commit
`9b3a3ded1be2933285e5a2ebac3e293105eeb37f`, passed the RTX6000 clean-device guard, and produced
the final 13/13 valid slices without overwriting the original 83 valid slices.

### 14.2 Final scientific result

The endpoint package contains six states with 60,000 probes each and 1,258 aggregate metric rows.
The frozen decision is **`primary_success_criterion_not_met`**:

- operational validity: passed;
- EN→EN retention guardrail: passed;
- seed 42 primary TR→EN interaction: `0.0025`, CI `[-0.0051, 0.0101]`, failed because the CI crosses zero;
- seed 43 primary TR→EN interaction: `0.0135`, CI `[0.0051, 0.0218]`, passed.

The complete metric CSVs, manifests, hashes, baseline anchors, robust results, paired contrasts,
and gate outputs are recorded in Document 136 §23 and remain on `/vol/tmp2`; no raw evaluation
tree was copied into the HU home filesystem.

### 14.3 Handoff state for the next agent

There are **no remaining pre-M2/M3 readiness tasks**. In particular, the following are closed:
template/evaluator review, registry materialization, M1 bilingual/PPL baseline, factual-dose and
endpoint freeze, matched-block balance/contamination audit, smoke/resume/retention checks,
storage/device preflight, four principal training runs, full endpoint evaluation, strict assembly,
and gate analysis.

The separate 25,000-fact M1 scale branch and optional M3-lexical arm remain explicitly excluded
from this handoff and are not prerequisites. No new GPU job, third seed, dose change, checkpoint
change, or gate relaxation should be started automatically. The next action requires an explicit
scientific decision about interpreting this valid two-seed negative/inconclusive causal result or
designing a separately amended experiment.
