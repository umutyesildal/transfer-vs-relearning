# 12 — Metric Reference and Glossary

This chapter is the quick-reference layer. Use earlier chapters for derivations and interpretation.

## 1. Core equations

### Causal language-model loss

\[
\mathcal{L}
=
-\frac{1}{N}
\sum_{t\in\text{valid labels}}
\log p_\theta(x_t\mid x_{<t}).
\]

Lower is better.

### Token perplexity

\[
\operatorname{PPL}
=
\exp(\operatorname{NLL}_{\text{token}}).
\]

Lower is better, under an identical tokenizer and protocol.

### PPL retention ratio

\[
\rho_{\text{PPL}}
=
\frac{\operatorname{PPL}_{\text{checkpoint}}}
{\operatorname{PPL}_{\text{base}}}.
\]

- 1.0: unchanged;
- below 1.0: improvement;
- above 1.0: degradation.

### PPL ratio to NLL change

\[
\Delta\operatorname{NLL}=\ln\rho_{\text{PPL}}.
\]

For \(\rho=1.25\), \(\Delta\operatorname{NLL}\approx0.2231\) nats/token.

### Display-only retention score

\[
\text{score}=\frac{100}{\rho_{\text{PPL}}}.
\]

This is not a new scientific metric.

### Bits per byte

\[
\operatorname{BPB}
=
\frac{\operatorname{NLL}_{\Sigma}}
{N_{\text{bytes}}\ln2}.
\]

Lower is better.

### Exact-prefix accuracy

\[
\operatorname{Acc}
=
\frac{1}{n}\sum_i
\mathbf{1}
[\text{generated text begins with canonical answer}].
\]

Higher is better.

### Candidate top-1 accuracy

\[
\hat c_i=\arg\max_{c\in\mathcal C_i}s_\theta(c\mid q_i),
\]

\[
\operatorname{Acc}_{\text{top1}}
=
\frac{1}{n}\sum_i\mathbf{1}[\hat c_i=y_i].
\]

### Candidate margin

\[
\operatorname{margin}_i
=
s_\theta(y_i\mid q_i)
-
\max_{c\neq y_i}s_\theta(c\mid q_i).
\]

Positive means the correct candidate ranks first.

### Robust intersection

\[
R_i=\prod_{p\in\mathcal P_i}I_{i,p},
\qquad
\operatorname{RobustAcc}
=
\frac{1}{n}\sum_iR_i.
\]

The fact succeeds only if every required prompt succeeds.

### Difference-in-differences

\[
\Delta
=
(Y_{M2B,B}-Y_{M2A,B})
-
(Y_{M2B,A}-Y_{M2A,A}).
\]

Positive means the B-specific treatment effect exceeds the A control effect.

### Effective batch

\[
B_{\text{effective}}
=
B_{\text{micro}}
\times K_{\text{accum}}
\times D_{\text{devices}}.
\]

### Relative change

\[
\%\Delta
=
\left(\frac{x_{\text{new}}}{x_{\text{base}}}-1\right)100\%.
\]

### Absolute accuracy change

\[
\Delta_{\text{pp}}
=
100(p_{\text{new}}-p_{\text{base}})
\]

percentage points.

## 2. Project states

| State | Definition | Main measurements |
|---|---|---|
| M0 | frozen source model | source English/Turkish capability, base PPL, tokenizer behavior |
| M1 | M0 after English factual acquisition | exact and robust acquisition, factual directions, drift |
| M2-A | M1 after general Turkish CPT | Turkish improvement, English/factual retention |
| M2-B | matched M1 sibling with controlled Turkish factual re-exposure | same as M2-A plus selective B-specific effect |
| M2-clean | historical Qwen name corresponding conceptually to M2-A | clean-arm endpoint |
| M3-fact | historical Qwen name corresponding conceptually to M2-B | factual re-exposure sibling endpoint |

## 3. Direction reference

| Direction | Prompt | Answer | Interprets mainly |
|---|---|---|---|
| EN→EN | English | English | original factual access/retention |
| TR→EN | Turkish | English | Turkish comprehension plus cross-lingual factual access |
| TR→TR | Turkish | Turkish | target-language comprehension, retrieval, and expression |
| EN→TR | English | Turkish | target-language expression; usually exploratory |

## 4. Precision reference

| Term | Meaning | Project relevance |
|---|---|---|
| FP32 | 32-bit IEEE-like floating point | reference precision, scalar state, sometimes accumulations |
| FP16 | 16-bit floating point with 5 exponent bits | efficient but narrow range; susceptible to underflow/overflow |
| BF16 | 16-bit format with 8 exponent bits | FP32-like range; coarser significand; valid OLMo/Pythia paths |
| autocast | operation-specific dtype selection | “mixed precision” is not one dtype everywhere |
| GradScaler | scales loss/gradients for FP16 range | incompatible with the project’s native-FP16 Pythia path |
| master weights | higher-precision parameter copy | may be needed for stable updates; consumes memory |
| optimizer moments | AdamW running \(m,v\) tensors | major memory cost |
| foreach/fused | multi-tensor optimizer implementations | change memory peak and kernel path |

## 5. Gate/status reference

| Status | Meaning |
|---|---|
| PASS | valid result satisfies frozen gate |
| scientific negative / FAIL | valid computation completed but failed scientific gate |
| null-compatible | uncertainty interval includes the null value |
| NOT_RUN | scientific computation did not validly begin |
| NOT_EVALUATED_GATE_CLOSED | evaluation intentionally skipped under frozen cascade |
| PENDING | scheduler or dependency has not executed the work |
| dependency-dead | upstream failure prevents downstream execution |
| incomplete family | one or more mandatory rows are absent |
| exploratory | analysis is informative but does not alter the primary confirmatory gate |
| superseded-unexecuted | plan was replaced before execution and produced no result |

## 6. Selected project numbers

### Historical Qwen sibling-arm pilot

- 500 subjects;
- 2,500 facts;
- five relations;
- 250 A and 250 B subjects;
- 1,250 B facts × four exposure cycles = 5,000 targeted fact exposures;
- 512-token blocks;
- 2,048 blocks;
- 1,048,576 tokens per arm;
- 128 optimizer updates;
- 24 evaluation slices × 2,500 probes = 60,000 probes per state.

### Qwen primary interactions

| Seed | Point estimate | 95% subject-bootstrap interval | Rule |
|---:|---:|---:|---|
| 42 | 0.0025 | [-0.0051, 0.0101] | fail |
| 43 | 0.0135 | [0.0051, 0.0218] | pass |

The frozen rule required both seeds, so the primary criterion did not pass.

### Three-model 500-fact screen

| Model | Exact | Aggregate hard | Worst profession form-C | PPL ratio | Interpretation |
|---|---:|---:|---:|---:|---|
| OLMo | 100% | about 98% | 59% | 1.510 | valid negative |
| Falcon | 100% | about 98% | 37% | 10.952 | valid negative |
| Pythia | 100% | 98.175% | 65% | 16.1487 | valid negative |

### OLMo dose experiment

- checkpoints: 42, 84, 126, 168, 210, 252;
- microbatch: 5;
- gradient accumulation: 100;
- effective batch: 500;
- precision: BF16 in the valid RTX3090 path;
- exact acquisition: 100% at all six checkpoints;
- PPL ratios: about 1.385–1.429;
- retention ceiling: 1.25;
- result: no checkpoint opened the hard suite.

## 7. Glossary

### Ablation

An experiment that changes or removes one component to estimate its contribution. The M1 learning-rate/EOS study is an ablation. A useful ablation holds other fields fixed.

### Accuracy

Proportion of valid evaluation units scored correct. Always state the unit and denominator.

### AdamW

Adaptive optimizer using first and second gradient moments with decoupled weight decay.

### Alias registry

Frozen list of answer strings accepted as equivalent. It must not be edited after observing failures without changing the evaluation contract.

### AMP

Automatic mixed precision: a framework chooses lower or higher precision by operation, often combined with gradient scaling.

### Answer-only loss

Training objective where prompt and padding labels are ignored and only answer-token positions contribute to cross-entropy.

### Artifact

Any file produced or consumed by the scientific pipeline: data, model, checkpoint, manifest, log, result, or audit record.

### Attention mask

Tensor indicating which input positions are real context versus padding. It is distinct from the causal mask and label ignore mask.

### Autoregressive

Factorization in which each token is predicted from previous tokens.

### Base model

The source checkpoint before the intervention being studied. A ratio must identify which base it uses.

### Batch

Collection of examples used to compute one update or partial update. Distinguish microbatch from effective batch.

### BF16

Bfloat16, a 16-bit floating-point type with FP32-like exponent range and seven stored fraction bits.

### Bits per byte

Negative log-likelihood normalized by input bytes and converted from natural-log units to bits.

### Block

Fixed-length token sequence used for training or evaluation after packing/padding.

### Bootstrap

Resampling method that approximates a statistic’s sampling distribution. In this project the key bootstrap unit is the subject.

### BOS

Beginning-of-sequence token. Its existence, ID, and insertion rule belong to tokenizer/model provenance.

### Candidate ranking

Scoring a closed answer set by conditional sequence likelihood and selecting the highest score.

### Catastrophic forgetting

Large loss of previously supported knowledge or capability after learning a new distribution or task.

### Causal LM

Language model trained to predict the next token using only earlier tokens as context.

### Checkpoint

Saved model state at a particular training dose. It may be model-only or resumable.

### Clean arm

M2-A/M2-clean: target-language adaptation without controlled factual re-exposure, under the contamination rules.

### Confidence interval

Interval generated by a procedure with a stated long-run coverage property under assumptions.

### Contamination

Presence of evaluation targets or controlled facts in training/source data in a way that compromises interpretation.

### Continued pretraining

Further causal-LM training on a new corpus distribution rather than task-specific labels alone.

### Counterbalancing

Swapping form/condition assignments across units to separate treatment effects from unit difficulty.

### Cross-entropy

Expected negative log-probability assigned to the observed target; for one-hot labels it equals NLL.

### Cross-lingual transfer

Use of capability or knowledge learned in one language when operating in another.

### CUDA compute capability

GPU architecture code controlling which kernels and features a software build supports, such as SM70.

### Data leakage

Information from evaluation or future data influences training, selection, or measurement improperly.

### Decoding

Procedure for turning model next-token distributions into a generated sequence, such as greedy or sampling.

### Deduplication

Removal or clustering of exact or near-identical records under a frozen similarity rule.

### Difference-in-differences

Interaction estimator subtracting a control-group arm difference from a treated-group arm difference.

### Dose

Amount of training exposure, specified by updates, tokens, epochs, or fact presentations.

### Drift

Behavioral or parameter change after training. Drift can be helpful adaptation or harmful forgetting.

### Effective batch

Number of examples contributing to one optimizer update across microbatches and devices.

### Embedding

Vector associated with a token ID or internal unit. Tokenizer ID mapping defines which symbol each embedding row represents.

### EOS

End-of-sequence token. EOS input presence and EOS target supervision are separate choices.

### Epoch

One nominal pass through a dataset under the sampler. It is not always a fixed token dose.

### Estimand

Precisely defined target quantity the experiment is designed to estimate.

### Exact-prefix

Criterion that generated normalized text begins with the canonical answer.

### Exposure

One presentation of an example/fact to the model. Repetition across epochs increases exposures.

### Factorial design

Design crossing several factors, such as relation, form, scaffold, direction, and state.

### Fail-closed

Stop when required validity evidence is absent or contradictory.

### Fertility

Average tokens per word/reference unit produced by a tokenizer.

### Fine-tuning

Further parameter training for a new task/data distribution. The term is broad; name the objective and trainable parameters.

### FP16

IEEE half precision with narrow exponent range, often requiring loss scaling in training.

### FP32

32-bit floating point, typically wider range and finer precision than 16-bit formats.

### Full-weight training

Updating all selected base-model parameters, in contrast to adapters such as LoRA.

### Gate

Predeclared rule mapping continuous measurements and integrity states to a decision.

### Generation

Autoregressive production in which the model conditions on previously generated tokens.

### Gradient

Derivative of loss with respect to parameters.

### Gradient accumulation

Summing/scaling gradients from multiple microbatches before one optimizer update.

### Gradient checkpointing

Activation-memory technique that recomputes selected forward activations during backward.

### Gradient clipping

Rescaling or limiting gradients to avoid excessively large updates.

### GradScaler

Dynamic loss-scaling utility primarily used to keep FP16 gradients in representable range.

### Guardrail

Constraint preventing unacceptable harm while optimizing a primary outcome.

### Hard suite

Held-out multi-form, multi-scaffold factual evaluation designed to test robust access beyond seen prompts.

### Hash

Digest such as SHA-256 used to identify exact bytes.

### Headroom

Distance between baseline performance and the maximum or meaningful target, determining possible improvement.

### Inference

Running a trained model without optimizer updates to obtain probabilities or generations.

### Integrity gate

Check that model, tokenizer, data, counts, hashes, and runtime match the intended experiment.

### Interaction

Effect of one factor that depends on another; the project’s main example is factual-arm × B-group.

### Label mask

Use of ignore-index labels to exclude prompt, padding, or EOS positions from loss.

### Language identification

Automated classification of document language, used as one corpus-quality signal.

### Learning rate

Scalar controlling optimizer update magnitude, possibly varying under a schedule.

### Logit

Unnormalized model score for a vocabulary item before softmax.

### LoRA

Low-Rank Adaptation: trainable low-rank matrices add an update to frozen weight matrices.

### Loss

Scalar objective minimized during training; it must be defined with its valid labels and aggregation.

### Margin

Difference between correct-candidate score and strongest incorrect-candidate score.

### Manifest

Structured record binding identities, configurations, inputs, outputs, hashes, and terminal state.

### McNemar test

Paired binary comparison based on discordant outcomes.

### Microbatch

Examples processed in one forward/backward pass before accumulation.

### Mixed precision

Use of more than one numerical dtype across parameters, operations, gradients, or optimizer state.

### NLL

Negative log-likelihood. Lower means higher probability assigned to observed targets.

### NOT-RUN

Scientific computation did not validly begin or reach its measurement stage.

### Optimizer

Algorithm converting gradients and state into parameter updates.

### PAD

Padding token used to equalize sequence lengths. PAD attention and loss must normally be masked.

### Paired design

Comparison of the same units across conditions, preserving within-unit covariance.

### Parameter

Trainable numerical value in the model.

### Pareto frontier

Set of non-dominated trade-off points when improving one objective can worsen another.

### Perplexity

Exponentiated average NLL under a specified unit and protocol.

### Percentage point

Absolute difference between percentages, distinct from relative percent change.

### Plasticity

Ability to acquire new behavior or knowledge.

### Precommitment

Freezing hypotheses, metrics, thresholds, and analysis rules before observing confirmatory outcomes.

### Prompt form

One linguistic rendering of a query or factual statement.

### Provenance

Traceable origin and transformation history of models, tokenizers, data, code, and artifacts.

### Quantization

Representation of weights/activations with reduced precision, often lower than 16 bits; distinct from standard mixed-precision training.

### Relearning

Target-language re-exposure intended to strengthen access to knowledge previously acquired in another language.

### Replay

Mixing examples from an older distribution into new training to mitigate forgetting.

### Replication

Testing whether a scientific conclusion survives a new stochastic run or setting.

### Reproducibility

Ability to reconstruct computation and analysis from frozen inputs, code, configuration, and evidence.

### Retention

Preservation of prior behavior after training, measured across likelihood, factual, capability, and generation dimensions.

### Robust intersection

Binary per-unit success only when all required prompt conditions pass.

### Scaffold

Interaction frame around a prompt, such as direct completion versus QA.

### Seed

Initial state controlling one or more pseudorandom processes. Training seeds and bootstrap seeds have different roles.

### Sequence length

Maximum or actual token positions processed together; affects context, truncation, memory, and compute.

### SFT

Supervised fine-tuning on labeled prompt/response or task examples.

### Sibling arms

Parallel treatments beginning from the same frozen parent checkpoint.

### Slurm

HPC scheduler used to allocate resources and express job dependencies.

### Softmax

Function mapping logits to a probability distribution.

### Stability

Ability to preserve previous behavior during new training.

### Teacher forcing

Scoring every next token while conditioning on the true preceding target sequence.

### Token

Discrete unit from a tokenizer vocabulary. It is not necessarily a word or character.

### Token budget

Number of token presentations allocated to training; must specify whether it counts padding and repetitions.

### Top-1

Candidate or vocabulary item with the highest frozen score.

### Treatment

Controlled experimental intervention whose effect is being estimated.

### Truncation

Dropping tokens beyond a maximum length, potentially removing targets or context.

### Update

One optimizer application after the intended gradient accumulation.

### Warmup

Initial schedule phase that gradually increases learning rate.

### Weight decay

Regularizing parameter magnitude; AdamW applies it separately from the adaptive gradient.

### WikiText-2

English language-modeling corpus used in the project’s generic retention protocol. Exact revision and preprocessing still matter.

### Word PPL

Whole-text NLL normalized by a frozen word count and exponentiated.

## 8. Primary-source reading map

### Architecture and objectives

- Vaswani et al., [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
- PyTorch, [CrossEntropyLoss](https://docs.pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html)

### Tokenization

- Kudo and Richardson, [SentencePiece](https://arxiv.org/abs/1808.06226)
- Toraman et al., [Impact of Tokenization on Language Models: An Analysis for Turkish](https://arxiv.org/abs/2204.08832)

### Optimization and precision

- Loshchilov and Hutter, [Decoupled Weight Decay Regularization](https://arxiv.org/abs/1711.05101)
- Micikevicius et al., [Mixed Precision Training](https://arxiv.org/abs/1710.03740)
- Kalamkar et al., [A Study of BFLOAT16 for Deep Learning Training](https://arxiv.org/abs/1905.12322)
- PyTorch, [Automatic Mixed Precision](https://docs.pytorch.org/docs/stable/amp.html)
- Chen et al., [Training Deep Nets with Sublinear Memory Cost](https://arxiv.org/abs/1604.06174)
- Hu et al., [LoRA](https://arxiv.org/abs/2106.09685)

### Perplexity and evaluation

- Hugging Face, [Perplexity of fixed-length models](https://huggingface.co/docs/transformers/perplexity)
- EleutherAI, [LM Evaluation Harness](https://github.com/EleutherAI/lm-evaluation-harness)
- EleutherAI, [Task Guide](https://github.com/EleutherAI/lm-evaluation-harness/blob/main/docs/task_guide.md)
- EleutherAI, [Model Guide](https://github.com/EleutherAI/lm-evaluation-harness/blob/main/docs/model_guide.md)

### Cross-lingual adaptation and forgetting

- Ebrahimi and Kann, [How to Adapt Your Pretrained Multilingual Model to 1600 Languages](https://aclanthology.org/2021.acl-long.351/)
- Acikgoz et al., [Bridging the Bosphorus](https://aclanthology.org/2024.mrl-1.21/)
- Zheng et al., [Breaking Language Barriers: Cross-Lingual Continual Pre-Training at Scale](https://aclanthology.org/2024.emnlp-main.441/)
- M’hamdi and May, [Leitner-Guided Memory Replay for Cross-lingual Continual Learning](https://aclanthology.org/2024.naacl-long.432/)

## 9. Project-document reading map

For definitions and the current direction:

- [Document 100 — master historical synthesis](../../documentation/100_MASTER_PROJECT_STATUS_AND_EXECUTION_PLAN.md)
- [Document 138 — completed Qwen scientific interpretation](../../documentation/138_QWEN_M2_M3_COMPLETED_MILESTONE_AND_SCIENTIFIC_INTERPRETATION_EN.md)
- [Document 142 — exploratory mechanism analysis result](../../documentation/142_QWEN_M2_M3_EXPLORATORY_MECHANISM_ANALYSIS_RESULT_EN.md)
- [Document 143 — artifact retention freeze](../../documentation/143_QWEN_M2_M3_ARTIFACT_RETENTION_FREEZE_AND_STORAGE_AUDIT_EN.md)
- [Document 145 — literature-first model/Turkish adaptation route](../../documentation/145_LITERATURE_FIRST_M1_MODEL_AND_TURKISH_ADAPTATION_ROUTE_TR.md)
- [Document 157 — Pythia valid scientific negative](../../documentation/157_PYTHIA_OFFICIAL_TOKENIZER_REPAIR_EXECUTION_RESULT_TR.md)
- [Document 158 — three-model post-execution gate](../../documentation/158_PYTHIA_REPAIR_POST_EXECUTION_AND_THREE_MODEL_GATE_TR.md)
- [Document 160 — OLMo dose/Pareto result](../../documentation/160_M1_DOSE_PARETO_OLMO_BF16_EXECUTION_AND_FAMILY_STATUS_TR.md)
- [Document 161 — dose-family gate](../../documentation/161_M1_DOSE_PARETO_POST_EXECUTION_GATE_TR.md)
- [Document 177 — current evaluation-first realignment](../../documentation/177_SUPERVISOR_FEEDBACK_EVALUATION_FIRST_OLMO_AND_M2_PRIORITY_REALIGNMENT_TR.md)

## 10. Final synthesis

The project’s central methodological lesson is that a language-model intervention is never adequately described by “we fine-tuned it and checked accuracy.”

A defensible statement has this structure:

> Starting from an immutable model/tokenizer state, we applied a frozen objective, data treatment, token dose, optimizer, precision topology, and runtime. We evaluated identified checkpoints with complete integrity evidence using prompt-robust factual probes, comparable likelihood metrics, capability measures, and degeneration diagnostics. We estimated paired subject-level contrasts with frozen uncertainty and replication rules, preserved missingness and operational failures honestly, and retained enough artifacts for independent recomputation.

That sentence is the conceptual spine connecting every chapter.

## 11. Chapter summary

- Use the formula section for fast recall.
- Always name the base state, denominator, unit, direction, and aggregation.
- Keep scientific FAIL, null-compatible, gate-closed, incomplete, and NOT-RUN distinct.
- Precision, tokenization, prompts, corpora, and runtime are part of the experimental treatment.
- The glossary is a navigation aid; the earlier chapters explain why each concept matters.
