# M1 General-Capability And Degeneration Control Plan

**Date:** 2026-07-14  
**Status:** Executed; thresholds below were fixed before the run  
**Purpose:** Test whether the successful 500-fact M1 acquisition checkpoints retain broad
English language-model behavior relative to the unchanged SmolLM2-1.7B base model.

Results are reported separately in
`documentation/91_M1_GENERAL_CAPABILITY_DEGENERATION_EVALUATION_REPORT.md` so that this pre-run
decision logic remains auditable.

## 1. Question

Did the narrow, high-exposure M1 factual-acquisition run materially degrade the base model's
general English modeling and continuation behavior?

This control is separate from factual candidate ranking. Near-perfect exact/direct/QA factual
retrieval does not by itself demonstrate preserved general language ability.

## 2. Compared Models

All three models use the same SmolLM2-1.7B tokenizer and architecture family:

1. unchanged base `HuggingFaceTB/SmolLM2-1.7B`;
2. frozen M1 seed-42 checkpoint 200;
3. frozen M1 seed-43/data-seed-43 checkpoint 75.

The two M1 checkpoints are evaluated independently. They must not be averaged before inspecting
whether either trajectory shows a degradation signal.

## 3. Evaluation Layers

### 3.1. Primary: generic English next-token loss

Use a frozen generic English test corpus that contains no M1 synthetic subject names. The first
choice is the raw WikiText-2 test split because it is small, standard, and practical for a
before/after retention control. This experiment uses WikiText only as a matched retention set;
it does not claim that WikiText is unseen by the original base model.

Protocol:

- use the identical tokenizer for all three models;
- append EOS between documents;
- evaluate fixed non-overlapping blocks with identical token IDs;
- report total scored tokens, mean token NLL and perplexity;
- report bootstrap confidence intervals over document/block losses;
- hash and freeze the exact corpus artifact before model evaluation;
- scan the corpus for all synthetic full subject names and require zero matches.

Primary comparisons:

```text
PPL ratio seed42 = PPL(M1 seed42) / PPL(base)
PPL ratio seed43 = PPL(M1 seed43) / PPL(base)
```

Interpretation bands are practical diagnostic bands, not universal language-model thresholds:

- ratio <= 1.10: no material generic-loss degradation detected;
- 1.10 < ratio <= 1.25: measurable drift; inspect secondary controls;
- ratio > 1.25: material generic-loss degradation flag.

Raw values and confidence intervals remain primary; the bands do not replace them.

### 3.2. Secondary: fixed deterministic continuation suite

Use a frozen set of approximately 30 English prefixes covering:

- ordinary factual completion;
- everyday procedural completion;
- short explanation;
- narrative continuation;
- summarization-style continuation;
- question/answer scaffold;
- neutral instruction-like text;
- syntax and discourse continuation.

Because the evaluated model is a base model rather than an instruction-tuned chat model, prompts
must mostly be completion-style. Failure to follow chat instructions is not itself degeneration.

Generation settings:

- greedy decoding for the primary reproducible view;
- fixed `max_new_tokens`;
- identical tokenizer and stopping rules;
- no sampling-based cherry-picking;
- preserve every raw continuation in JSONL.

Report per model:

- empty or near-empty continuations;
- repeated 3-gram and 4-gram fractions;
- longest repeated-token run;
- distinct-1, distinct-2 and distinct-3;
- premature EOS rate;
- non-finite-logit/runtime failures;
- synthetic full-name intrusions in unrelated prompts.

The report must also include side-by-side raw outputs. Automated repetition metrics do not fully
measure coherence.

### 3.3. Secondary: matched generic QA/completion accuracy

Use a small frozen set of unambiguous, non-synthetic, common-knowledge completions with canonical
answers. Score candidate answers using the existing answer-token likelihood path rather than only
open generation.

Examples of task shapes:

- `The capital of France is` -> `Paris`;
- `Water freezes at` -> `0 degrees Celsius`;
- simple vocabulary, arithmetic and everyday causal completions.

This is a regression comparison, not a claim of benchmark-level general intelligence. Items must
be identical across the three models and results must be reported item by item.

### 3.4. Factual-retention link

Reuse the already completed M1 factual evaluation for the selected checkpoints:

- seed 42: exact/direct/QA/overlap = 500/499/498/497;
- seed 43: exact/direct/QA/overlap = 500/500/499/499.

Do not rerun factual acquisition merely to obtain the general-capability result unless an artifact
integrity check fails.

## 4. Precommitted Interpretation

### No material degeneration detected

Use this conclusion only if:

- both M1 checkpoints have generic PPL ratio <= 1.10;
- neither checkpoint shows a material increase in repetition/empty-output failures;
- generic matched-completion performance has no clear broad regression;
- no unrelated prompt produces synthetic full-name intrusion.

### Measurable drift, but not broad degeneration

Use this conclusion if generic loss worsens moderately or a limited prompt category regresses,
while most controls remain stable and there is no broad repetition/collapse behavior.

### Material degeneration detected

Use this conclusion if either M1 checkpoint shows a PPL ratio above 1.25, broad matched-completion
regression, or clear repeated/empty/fact-only output collapse. A single aesthetically weak
continuation is not sufficient.

If seed 42 and seed 43 disagree, report trajectory sensitivity rather than averaging the issue
away.

## 5. Follow-Up Decision

### If no material degeneration is detected

- retain seed-42 checkpoint 200 as canonical M1;
- retain seed-43 checkpoint 75 as replication;
- proceed to M2/M3 without an LR sweep for the 500-fact condition;
- report the general-capability control as an M1 safety check.

### If measurable drift is detected

- evaluate earlier already-existing 1.7B checkpoints before retraining;
- search for the earliest checkpoint that passes the factual gate with lower general drift;
- compare checkpoint 50, 75 and selected checkpoint 200 on the same general set.

This is cheaper and scientifically cleaner than immediately launching new LR runs.

### If material degeneration is detected

Only then launch a controlled LR sensitivity branch on the final 1.7B recipe. Keep dataset,
objective, epochs, effective batch, data order and evaluator fixed. Compare lower LR candidates
against the current `1e-4` reference. A `2e-4` run is not the first remediation because it
increases rather than reduces update magnitude, but it may be retained as an upper-bound
sensitivity control if the full suggested grid is scientifically required.

## 6. Required Artifacts

Each model evaluation must write:

- resolved config;
- model manifest path and hash;
- generic corpus path and SHA-256;
- prompt-suite path and SHA-256;
- `summary_metrics.json`;
- per-block generic-loss CSV;
- per-item generic completion score CSV;
- raw `generations.jsonl`;
- runtime/software/device metadata;
- explicit completion status and errors file.

The combined comparison must write:

- base-vs-seed42-vs-seed43 table;
- confidence intervals and PPL ratios;
- side-by-side generation appendix;
- interpretation under the precommitted categories above.

## 7. Implementation And Verification Order

1. add a model-manifest-based general-capability evaluator;
2. add unit tests for token-loss accounting and repetition metrics;
3. freeze and hash generic corpus and prompt artifacts;
4. run a tiny CPU/model-fixture smoke test locally;
5. run base, seed 42 and seed 43 as separate HU jobs;
6. verify all three used identical token IDs and prompt hashes;
7. generate the comparison report without changing thresholds;
8. decide whether earlier-checkpoint or LR sensitivity work is necessary.

## 8. What This Experiment Can And Cannot Establish

It can establish whether M1 caused a measurable regression relative to its own base model on a
frozen general-English control and fixed continuation suite.

It cannot prove that:

- the model preserves every downstream capability;
- WikiText perplexity is equivalent to instruction-following quality;
- a base model should behave like a chat assistant;
- no subtle representation drift occurred;
- the result automatically generalizes to larger fact scales or M2/M3 adaptation.
