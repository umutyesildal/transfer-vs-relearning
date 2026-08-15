# 132 - Pre-M2 Qwen Readiness And Baseline Plan

**Date:** 2026-07-31  
**Status:** In progress; compact registries and matched-block materializer implemented and tested locally; no M2/M3 training authorized yet  
**Scope:** Work that can be completed before the optional 25,000-fact M1 scale result and before the next supervisor meeting

## 1. Direct decision

The replicated Qwen 500-subject / 2,500-fact English M1 stage is complete. No additional English
M1 optimization, seed, or checkpoint search is required before an intermediate-scale M2/M3 causal
family. The 25,000-fact seed-42 run is a separate scale-validation branch and is not a prerequisite
for the work in this plan.

Four concrete readiness packages remain before M2/M3 training:

1. materialize and freeze the new 2,500-fact bilingual probe/fact registries;
2. reload both selected Qwen M1 artifacts and measure their pre-adaptation bilingual baselines;
3. materialize token-matched M2-clean and M3-fact adaptation inputs from the frozen Turkish corpus;
4. pass evaluator, tokenizer, storage/path, clean-GPU, and short training smoke checks.

Branch A/B assignment, the frozen Turkish corpus, both selected Qwen model-only artifacts, and the
English M1 gate evidence are already complete.

## 2. Frozen starting population and models

The intermediate population is the exact population used by the successful Qwen scale runs:

- 500 subjects;
- 2,500 facts;
- 250 Branch A subjects / 1,250 Branch A facts;
- 250 Branch B subjects / 1,250 Branch B facts;
- five relations per subject.

The sibling downstream chains start from:

| Chain | Selected M1 endpoint | Frozen manifest SHA-256 |
|---|---|---|
| Qwen seed 42 | step 75 | `aed52ff8baeb01b89efef443caa560b707871dfe52fde6bcec1d8ae3e46fb032` |
| Qwen seed 43 | step 50 | `af3569aae2bd8066f51bb0ff1fecd4eec13eb74b5ba794915eae565f13f8bd53` |

Both M2 and M3 must start independently from the selected M1 endpoint in their own seed chain.
M3 is not a continuation of M2.

## 3. Package A - compact registries

Implemented locally on 31 July:

- exact 500-subject selection and 250/250 Branch A/B assertion;
- 60,000 bilingual hard probes:
  - 2,500 facts;
  - EN-to-EN, TR-to-EN, and TR-to-TR;
  - Forms A/B/C/D;
  - direct and QA scaffolds;
- 1,250 canonical Turkish factual bindings for Branch B only;
- append-only output and SHA-256 manifest generation;
- tests for population balance, direction/answer-language separation, probe uniqueness, and
  Branch-B-only factual material.

The local dry materialization passed and produced a 21-MiB compact tree. This is development
evidence, not the final HU scratch artifact. Before freezing on HU, the Turkish prompt and factual
sentence templates require one manual language review.

## 4. Package B - current-M1 reload and bilingual baseline

This is the remaining scientific evaluation before Turkish adaptation. For both selected Qwen
artifacts:

1. verify the selected-artifact manifest and every declared model/tokenizer hash;
2. load the model from the frozen model-only package without using an ordinary trainer checkpoint;
3. evaluate EN-to-EN, TR-to-EN, and TR-to-TR on the frozen 60,000-probe registry;
4. report every direction by relation, form, scaffold, and Branch A/B;
5. reproduce the frozen English hard gate and forced-choice binding result;
6. measure frozen English and Turkish generic PPL baselines;
7. record zero evaluator error, empty-answer bug, tokenizer-boundary failure, and synthetic
   intrusion.

Low Turkish retrieval at M1 is not a failure. It provides headroom. High Turkish retrieval is
reported as an already-open baseline and changes later interpretation toward preservation or
degradation.

Collecting all three directions does not require choosing the final primary outcome before this
descriptive baseline. The primary causal outcome must nevertheless be fixed before M2/M3 result
inspection.

## 5. Package C - matched M2/M3 inputs

The core first family contains only the two Expose-required arms:

```text
M2-clean = frozen generic Turkish blocks; no target synthetic binding
M3-fact  = the same total block/update budget, with preselected neutral Turkish token positions
           replaced by the 1,250 correct Branch B Turkish factual bindings
```

Required assertions:

- identical total token blocks and optimizer updates;
- identical seed, data seed, batch decomposition, schedule, checkpoint interval, and endpoint;
- identical Branch A exposure: zero Turkish factual repetition;
- all correct Turkish factual rows restricted to Branch B;
- factual material replaces generic material and is never added on top of the M2 budget;
- exact corpus, factual registry, block order, replacement positions, configs, and manifests are
  hash-frozen before training;
- no synthetic subject/object contamination in the M2-clean blocks.

M3-lexical is an optional later control and is not a blocker for the core M2-clean versus M3-fact
family.

The only unresolved scientific dose parameter is the number of complete exposures of the 1,250
Branch B facts inside the fixed Turkish block budget. The builder should accept this as an explicit
precommitted parameter and report the resulting factual-token share before training.

The local implementation now does this parametrically. It packs only complete factual sentences,
places their blocks at deterministic spread positions, preserves the original generic-token tail
of a partially filled replacement block, and writes equal-length pretokenized M2/M3 block files.
The CLM trainer now validates this frozen pretokenized full-sequence mode and rejects non-full masks,
wrong block lengths, negative token IDs, or auxiliary-objective combinations. No factual-cycle
value has been selected and no HU materialization has occurred.

## 6. Package D - execution readiness

Before the first M2/M3 training submission:

- freeze the endpoint/update rule; do not choose treatment-specific checkpoints from Turkish
  factual outcomes;
- run an exhaustive prompt/candidate tokenizer-boundary check;
- run a short clean-GPU training smoke from one selected artifact;
- verify that the smoke does not catastrophically destroy the English factual gate;
- run the mandatory HU capacity, inode, home-usage, and resolved-path preflight;
- record expected checkpoints, checkpoint bytes, family reserve, and retention policy;
- route every dataset, cache, checkpoint, log, evaluation, and temporary file to scratch.

## 7. What is not left before M2

The following are already complete or unnecessary:

- another Qwen English M1 optimization;
- another Qwen M1 seed;
- another SmolLM remediation;
- rebuilding the Turkish Wikipedia corpus;
- changing Relation V2 or the 500-subject selection;
- completing 25,000-fact M1 before preparing or measuring this intermediate family;
- implementing M3-lexical before the core causal family.

## 8. Execution order

```text
manual Turkish template review
-> HU compact registry materialization and hash freeze
-> two-artifact reload + bilingual/PPL baseline evaluation
-> matched M2/M3 block materialization and audit
-> fixed endpoint + launch/storage contract
-> short clean-GPU smoke and English-retention check
-> M2/M3 ready
```

No principal M2/M3 outcome may be interpreted before the final primary outcome and causal estimand
are recorded. That decision can be discussed with the supervisor later without delaying the
descriptive baseline, registry, data-builder, or operational readiness work above.

## 9. Local verification record

On 31 July 2026:

- the compact registry dry materialization produced 500 subjects, 2,500 facts, exact 250/250
  subject and 1,250/1,250 fact branch balance, 60,000 unique probes, and 1,250 unique Branch-B
  Turkish factual rows;
- 20 targeted Qwen-pre-M2, Turkish-bridge, and Qwen-scale config tests passed;
- the remainder of the locally runnable suite passed with seven expected optional skips when the
  single PyYAML-dependent collection module was excluded because PyYAML is absent from the local
  system interpreter;
- Python compilation and `git diff --check` passed;
- no HU job, model evaluation, training run, or canonical scratch artifact was created by this
  local implementation.
