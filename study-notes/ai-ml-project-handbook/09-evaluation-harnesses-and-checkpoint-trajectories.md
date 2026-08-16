# 09 — Evaluation Harnesses and Checkpoint Trajectories

## 1. Why an evaluation harness?

An evaluation harness provides standardized task loading, prompt construction, model interfaces, metrics, few-shot handling, and result serialization. The project’s next evaluation-first stage uses EleutherAI’s [Language Model Evaluation Harness](https://github.com/EleutherAI/lm-evaluation-harness) to broaden the capability picture beyond custom factual probes and custom PPL.

A harness improves consistency, but it does not make evaluation automatically valid. Validity still depends on:

- exact package version and commit;
- task version;
- dataset revision;
- model wrapper arguments;
- tokenizer;
- batch size and context limit;
- few-shot count;
- generation settings;
- decontamination and metric definitions.

## 2. Three main model requests

The harness’s model interface conceptually exposes:

### Log-likelihood of a continuation

\[
\log p_\theta(c\mid q)
=
\sum_j\log p_\theta(c_j\mid q,c_{<j}).
\]

Used for multiple-choice and candidate-ranking tasks.

### Rolling log-likelihood

Scores a long corpus through overlapping fixed-context windows. Used for perplexity.

### Generate until

Generates a continuation until a stop condition or token limit. Used for open-ended tasks.

The official [model guide](https://github.com/EleutherAI/lm-evaluation-harness/blob/main/docs/model_guide.md) defines the interface. The [task guide](https://github.com/EleutherAI/lm-evaluation-harness/blob/main/docs/task_guide.md) documents task configuration and metrics.

## 3. Multiple-choice normalization

For choices \(c_1,\ldots,c_K\), raw log-likelihood picks

\[
\arg\max_k\log p(c_k\mid q).
\]

Long choices usually receive more negative summed log-likelihood. Some tasks therefore use length-normalized score:

\[
\bar s(c_k\mid q)
=
\frac{1}{|c_k|}
\log p(c_k\mid q).
\]

Harness result names such as raw accuracy and normalized accuracy can differ. The report must state which metric is primary for each task rather than generically saying “accuracy.”

## 4. Capability task families

[Document 177](../../documentation/177_SUPERVISOR_FEEDBACK_EVALUATION_FIRST_OLMO_AND_M2_PRIORITY_REALIGNMENT_TR.md) proposes a candidate battery whose exact task IDs must be validated against the pinned harness installation:

- **WikiText:** English language modeling and multiple PPL normalizations;
- **BLiMP:** English grammatical minimal pairs;
- **HellaSwag:** English commonsense continuation selection;
- **Winogender:** pronoun/coreference behavior and bias-sensitive slices;
- **TurBLiMP:** Turkish grammatical minimal pairs;
- **TurkishMMLU:** Turkish knowledge/reasoning-style multiple choice;

These tasks do not form a single latent “intelligence” score. They sample different behaviors.

## 5. Base-normalized trajectories

For metric \(S\) where higher is better:

\[
\Delta_S(d)=S(M_d)-S(M_0)
\]

or relative change:

\[
r_S(d)=\frac{S(M_d)}{S(M_0)}.
\]

For loss or PPL where lower is better:

\[
r_{\text{PPL}}(d)
=
\frac{\text{PPL}(M_d)}{\text{PPL}(M_0)}.
\]

Always preserve raw values. Normalized trajectories make changes comparable within a model, but cannot replace task-specific units.

## 6. The checkpoint ledger

Every evaluation row should bind:

| Field | Why it matters |
|---|---|
| model family and revision | distinguishes source weights |
| tokenizer revision/hash | fixes text-to-ID mapping |
| M1 run ID | identifies acquisition state |
| checkpoint update | fixes dose |
| checkpoint hash | prevents path aliasing |
| optimizer update/epoch | interprets training time |
| training-token exposure | interprets actual dose |
| task ID/version | fixes benchmark definition |
| dataset revision | fixes examples |
| harness version/commit | fixes evaluator behavior |
| model arguments | fixes dtype, max length, batch |
| metric name | distinguishes raw and normalized variants |
| valid/expected count | exposes missing coverage |
| result status | completed, gate-closed, or NOT-RUN |

Without this ledger, a line plot can connect incompatible or unidentified points.

## 7. Dose trajectories

The OLMo checkpoint grid is:

\[
d\in\{42,84,126,168,210,252\}.
\]

For each \(d\), the desired vector is

\[
\mathbf y_d
=
\left[
\text{fact exact},
\text{fact robustness},
\text{EN PPL},
\text{EN capability},
\text{TR capability},
\text{degeneration}
\right].
\]

~~~mermaid
flowchart LR
    C42["42"] --> C84["84"] --> C126["126"] --> C168["168"] --> C210["210"] --> C252["252"]
    C42 -.-> E42["same frozen evaluation battery"]
    C84 -.-> E84["same frozen evaluation battery"]
    C126 -.-> E126["same frozen evaluation battery"]
    C168 -.-> E168["same frozen evaluation battery"]
    C210 -.-> E210["same frozen evaluation battery"]
    C252 -.-> E252["same frozen evaluation battery"]
~~~

The same battery matters. Changing prompts or task versions across checkpoints converts the trajectory into a mixture of training change and measurement change.

## 8. Reading trajectory shapes

### Early acquisition, monotonic forgetting

Facts become exact by checkpoint 42 while PPL steadily worsens. This suggests the factual dose was more than enough and retention damage accumulates.

### Delayed acquisition, stable retention

PPL remains flat while exact accuracy rises later. More dose may be justified.

### U-shaped retention

PPL first worsens and later recovers. Endpoint-only evaluation would miss the transient.

### Capability trade-off

Turkish tasks improve while English tasks decline. This is expected adaptation tension and should be quantified, not collapsed.

### Abrupt discontinuity

One checkpoint changes sharply while neighbors do not. Investigate checkpoint corruption, wrong tokenizer, evaluation mismatch, or optimizer instability before proposing a scientific mechanism.

## 9. Cheap-to-expensive evaluation cascade

A frozen cascade may be:

~~~mermaid
flowchart TD
    I["Integrity checks"] -->|pass| X["Cheap exact acquisition"]
    X -->|pass| P["Cheap PPL retention"]
    X -->|fail| Stop1["Hard suite closed"]
    P -->|pass| H["Hard prompt suite"]
    P -->|fail| Stop2["Hard suite closed"]
    H --> S["Family summary after all required rows"]
~~~

The cascade reduces cost, but a new evaluation-first mandate may choose to run a broader battery on all checkpoints. That is a new frozen measurement plan. The key is consistency: do not retroactively fill only the promising checkpoints.

## 10. Cross-checking custom PPL with harness WikiText

The cross-check should compare:

1. raw source dataset and revision;
2. reconstructed text bytes;
3. normalization and detokenization;
4. number of words/bytes/tokens;
5. maximum context and stride;
6. context-only label masking;
7. total log-likelihood;
8. token, word, and byte denominators;
9. final PPL/BPB values.

Since

\[
\operatorname{PPL}=\exp\left(\frac{\operatorname{NLL}_\Sigma}{N}\right),
\]

two evaluators can be reconciled by comparing numerator and denominator before comparing the exponentiated result.

## 11. Prompt-template provenance

For harness tasks, prompts can be defined by:

- task YAML;
- dataset fields;
- few-shot template;
- target delimiter;
- answer choices;
- stop strings.

A template edit changes the measurement. Store:

- the resolved task configuration;
- hashes of local task files;
- rendered sample prompts;
- the harness commit.

This is especially important for multilingual tasks where punctuation, whitespace, and target labels can tokenize differently.

## 12. Few-shot evaluation

With \(k\)-shot evaluation, \(k\) demonstrations precede the query. Scores depend on:

- demonstration selection;
- order;
- separator;
- context truncation;
- random seed;
- whether examples leak related entities.

Zero-shot and few-shot results answer different questions. A model can gain from in-context format learning without any parameter update. The shot count and selection rule are part of the estimand.

## 13. Batch-size invariance checks

Evaluation should ideally produce the same scores across batch sizes. Differences can reveal:

- left/right padding bugs;
- incorrect attention masks;
- numerical threshold sensitivity;
- generation stopping interactions;
- stateful model wrappers.

A small spot check at batch size 1 versus the production batch can validate the vectorized path.

## 14. Precision during evaluation

Evaluation dtype affects memory, speed, and sometimes ranking:

- FP32 is a useful reference but expensive;
- BF16/FP16 may change close log-likelihood comparisons;
- quantization can materially change scores.

Within a trajectory, use the same validated evaluation dtype. If training checkpoints are stored in BF16, loading them into FP32 can improve arithmetic precision but does not restore information already rounded in the weights.

## 15. Integrity before metrics

An evaluation should fail closed if:

- checkpoint hash is unexpected;
- tokenizer vocabulary or special tokens mismatch;
- probe encodings are empty;
- task version is missing;
- expected row counts are incomplete;
- outputs contain NaN or infinity;
- duplicate keys exist;
- a supposedly clean GPU has foreign processes and the contract requires isolation.

Metrics computed after an integrity failure are not “approximate results.” They are invalid.

## 16. Benchmark contamination

A pretrained model may have seen benchmark examples. A continued-pretraining corpus may also contain them. Benchmark scores then mix capability with memorization.

Useful audit strategies:

- exact example hashes;
- substring/entity matching;
- near-duplicate search;
- source dataset provenance;
- train/test overlap reports;
- cautious claim language.

Contamination analysis rarely proves absence. It documents the search space and residual risk.

## 17. Avoiding aggregate “capability soup”

Do not average PPL, accuracy, and BPB into one number without a justified transformation. A better checkpoint table keeps columns separate and applies a precommitted rule:

- acquisition gate;
- retention guardrail;
- Turkish-improvement check;
- worst-slice robustness;
- task-level capability changes.

A radar chart or scalar average can visually hide a catastrophic failure. Tables and aligned trajectories are usually more honest.

## 18. Common mistakes

### “Harness results are standardized, so version does not matter”

False. Tasks and code evolve.

### “Normalized accuracy is always better”

It changes the scoring estimand and is task-dependent.

### “Only the final checkpoint needs broad evaluation”

That can miss an earlier useful state and prevents learning-trajectory analysis.

### “Two PPL implementations disagree, so one is wrong”

They may score different bytes, contexts, or denominators. Decompose first.

## 19. Chapter summary

- An evaluation harness standardizes interfaces but still requires strict version and task provenance.
- Log-likelihood, rolling log-likelihood, and generation probe different behaviors.
- Raw and length-normalized multiple-choice accuracy are different metrics.
- Evaluate a frozen battery across every intended checkpoint to obtain a trajectory.
- Cross-check PPL by comparing text bytes, total NLL, denominators, context, and stride.
- Task files, prompts, shot selection, dtype, and valid-row counts belong in the evaluation manifest.
- Keep capability dimensions separate rather than manufacturing one opaque aggregate.
