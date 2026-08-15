# 06 — Cross-Lingual Adaptation, Transfer, and Relearning

## 1. Three processes that must be separated

The thesis title contains three related but different processes:

### Adaptation

Training a source model on Turkish text so that it models Turkish better.

### Transfer

Using knowledge acquired in one language when prompted or evaluated in another language, without directly reteaching that exact mapping in the target language.

### Relearning or re-exposure

Presenting controlled Turkish evidence for a previously acquired English fact and measuring whether this targeted exposure restores or strengthens cross-lingual access.

Ordinary Turkish continued pretraining can improve tokenization-conditioned language behavior, syntax, and domain familiarity. That alone is not evidence of factual relearning. The M2-A/M2-B contrast isolates the added factual component.

## 2. Continued pretraining versus supervised fine-tuning

**Continued pretraining (CPT)** uses the causal language-model objective on a new text distribution:

\[
\mathcal{L}_{\text{CPT}}
=
-\mathbb{E}_{x\sim D_{\text{TR}}}
\sum_t \log p_\theta(x_t\mid x_{<t}).
\]

It does not require instruction–response pairs. It adapts general next-token prediction.

**Supervised fine-tuning (SFT)** uses examples designed around a task or instruction:

\[
(q_i,a_i)
\]

with full-sequence or answer-only labels. It teaches a more explicit mapping between prompt and response.

The project uses factual acquisition examples that resemble controlled SFT/causal-LM fine-tuning and language adaptation that resembles CPT. These phases have different data-generating processes and should not be called interchangeable “training.”

## 3. Why source-model Turkish provenance matters

Before claiming transfer into Turkish, ask whether the source model already saw Turkish. A model marketed as English-only can still contain:

- Turkish web pages;
- multilingual code or metadata;
- Turkish Wikipedia fragments;
- byte-level capacity that permits Turkish generation;
- contamination from evaluation benchmarks.

Source provenance affects the estimand:

- If \(M_0\) already has substantial Turkish, M2 measures further adaptation.
- If \(M_0\) has very little Turkish, M2 measures stronger language acquisition.
- If provenance is unknown, the phrase “cross-lingual transfer” requires behavioral baselines and cautious interpretation.

Model-card language labels are evidence, not complete proof. Training-corpus composition, tokenizer fertility, and pre-adaptation Turkish benchmarks provide complementary evidence.

## 4. Headroom

A treatment can only show improvement if the baseline leaves room:

\[
\text{headroom}=S_{\max}-S(M_1).
\]

If M1 already scores near the task ceiling on Turkish, M2-A cannot show much gain. Conversely, if M1 is essentially incapable of Turkish, cross-lingual factual prompts may fail because of language comprehension rather than factual storage.

The source-model audit therefore evaluates:

- Turkish tokenization fertility;
- Turkish PPL/BPB;
- Turkish grammar or NLU tasks;
- prompt following in Turkish;
- factual direction baselines;
- contamination risks.

## 5. The sibling-arm design

Let \(D_G\) be a general Turkish corpus and \(D_F\) controlled Turkish factual re-exposure. The arms are:

\[
M2A=\operatorname{Train}(M1,D_G;C)
\]

and

\[
M2B=\operatorname{Train}(M1,D_G\oplus D_F;C'),
\]

where contracts \(C,C'\) are matched so that the intended difference is the factual component.

Matching may require equality of:

- initial M1 bytes;
- total token budget;
- update count;
- sequence length;
- effective batch;
- optimizer and learning-rate schedule;
- sampling rule;
- checkpoint grid;
- general corpus source;
- runtime precision;
- evaluation registry.

If M2-B simply adds \(D_F\) on top of the full M2-A token budget, it receives more total training. A gain could be caused by dose rather than content. A controlled design either replaces a matched portion, compensates budgets, or explicitly models extra dose.

## 6. The manipulation checks

The M2 design needs at least two manipulation checks.

### Language-adaptation check

Both arms should improve Turkish relative to M1:

\[
\Delta_{\text{TR},A}=S_{\text{TR}}(M2A)-S_{\text{TR}}(M1),
\]

\[
\Delta_{\text{TR},B}=S_{\text{TR}}(M2B)-S_{\text{TR}}(M1).
\]

### Factual-treatment check

M2-B should show selective improvement on B facts beyond A facts and beyond M2-A:

\[
\Delta_{\text{interaction}}>0.
\]

Without the first, adaptation may be ineffective. Without the second, there is no evidence that factual re-exposure caused a selective factual change.

## 7. Why A and B must be matched

Branch assignment should balance:

- relation frequencies;
- answer lengths;
- tokenizer lengths;
- subject difficulty;
- baseline M1 confidence;
- lexical frequency;
- language-specific answer form;
- prompt form assignments.

If B contains easier facts, a positive B result is confounded. A matching audit should compare distributions before training, not after outcomes are known.

The historical Qwen design split 500 subjects into 250 A and 250 B subjects, with five facts per subject. B’s 1,250 facts were repeated across four cycles, yielding 5,000 targeted exposures, while A facts received none.

## 8. Cross-lingual directions as diagnostic decomposition

Consider a fact acquired in English.

| Direction | Input requirement | Output requirement | Main diagnostic role |
|---|---|---|---|
| EN→EN | understand English | produce English object | original-channel retention |
| TR→EN | understand Turkish | produce English object | cross-lingual access with stable output language |
| TR→TR | understand Turkish | produce Turkish object | full target-language retrieval |
| EN→TR | understand English | produce Turkish object | target-language expression; often exploratory |

A TR→TR failure with a TR→EN success suggests output-language expression is a problem. Failure in both TR directions with strong EN→EN suggests Turkish prompt understanding or cross-lingual access is the bottleneck. Failure in all directions suggests broader factual forgetting.

## 9. What the historical Qwen results mean

Approximate state accuracies were:

| State | Seed | EN→EN | TR→EN | TR→TR |
|---|---:|---:|---:|---:|
| M1 | 42 | 99.29% | 52.03% | 29.05% |
| M2-clean | 42 | 98.05% | 33.29% | 22.46% |
| M3-fact | 42 | 98.22% | 35.14% | 24.04% |
| M1 | 43 | 99.24% | 52.52% | 30.12% |
| M2-clean | 43 | 96.24% | 33.70% | 23.25% |
| M3-fact | 43 | 96.95% | 35.59% | 24.97% |

The main pattern:

- English factual access remained high.
- Clean Turkish adaptation caused a large TR→EN drop of about 18.8 percentage points from M1.
- Factual re-exposure recovered only about 1.9 points on average at the state level.
- The selective interaction replicated in seed 43 but not seed 42.

This is not “Turkish adaptation erased all facts.” EN→EN remained high. It is evidence that the cross-lingual access pathway was much more fragile than direct English retrieval.

## 10. Transfer versus translation

Cross-lingual factual evaluation is not merely translation quality. A Turkish prompt can require:

1. recognizing the subject;
2. recognizing the requested relation;
3. mapping Turkish syntax and morphology into internal features;
4. retrieving the object;
5. expressing it in the required output language.

A translation model could translate the prompt and still fail the fact. A factual model could store the fact and fail to parse the Turkish relation. Direction-specific controls decompose these possibilities only partially.

## 11. Tokenizer extension

One language-adaptation method extends the tokenizer vocabulary with target-language subwords. New tokens require new embedding and output rows. Their initialization can use:

- random values;
- averages of old token embeddings;
- decomposition-based initialization;
- learned projection.

Potential benefits:

- lower fertility;
- more words per context;
- fewer generation steps;
- better representation of morphology.

Risks:

- changes vocabulary and softmax dimension;
- complicates checkpoint comparability;
- new rows begin poorly trained;
- token-budget matching changes;
- old and new PPL units differ.

Ebrahimi and Kann, [How to Adapt Your Pretrained Multilingual Model to 1600 Languages](https://aclanthology.org/2021.acl-long.351/), and later adaptation literature motivate careful tokenizer/model compatibility. Tokenizer extension must be treated as a scientific intervention.

## 12. Full-weight CPT, adapters, and replay

### Full-weight CPT

Updates shared model parameters. High flexibility, high optimizer memory, and potentially broad interference.

### LoRA/adapters

Adds or modifies a restricted trainable subspace. Lower memory and easy state separation, but different capacity and implicit regularization.

### Replay

Mixes some old-language data during target-language adaptation:

\[
D_{\text{train}}
=
\alpha D_{\text{TR}}
+(1-\alpha)D_{\text{EN-replay}}.
\]

Replay directly reminds the model of the old distribution. It changes the treatment: the study is now testing Turkish adaptation with retention intervention.

### KL/logit retention

Penalizes divergence from the source model:

\[
\mathcal{L}
=
\mathcal{L}_{\text{TR}}
+\lambda
\operatorname{KL}
\left(
p_{\theta_{\text{old}}}(\cdot\mid x)
\|
p_\theta(\cdot\mid x)
\right).
\]

This constrains output distributions on selected anchor inputs. It can reduce drift but may also restrict useful adaptation.

These methods should enter as separately named arms or remediation stages, not be swapped into an existing contract after observing failure.

## 13. Corpus choice changes the meaning of adaptation

A Wikipedia-only corpus adapts to encyclopedic Turkish. A broad web corpus adapts to a different mixture of styles, domains, and quality. The thesis realignment distinguishes:

- a completed Qwen Wikipedia-only pilot;
- the next literature-first general Turkish corpus design;
- trwiki as a control rather than automatically the primary corpus;
- vngrs or another general corpus only after provenance and quality audits.

Corpus domain can affect:

- Turkish capability gains;
- English retention;
- factual contamination;
- style;
- tokenization distribution;
- causal interpretation of “general Turkish adaptation.”

## 14. Contamination and treatment leakage

M2-A is intended to be fact-clean with respect to the controlled synthetic facts. It must not accidentally contain:

- exact fact sentences;
- paraphrases;
- subject and object co-occurrences that reveal the mapping;
- translations of evaluation prompts;
- benchmark answers.

Exact matching catches literal overlap. Near-duplicate detection and entity-pair searches catch paraphrases and formatting changes. A contamination audit is never mathematically perfect, but its scope and detection methods must be documented.

If controlled facts leak into M2-A, the interaction is biased toward zero because the control receives treatment.

## 15. Capability improvement and factual preservation are not interchangeable

A Turkish grammar score can rise while factual retrieval falls. A factual TR→EN score can rise from targeted exposure while general Turkish PPL worsens. Therefore checkpoint selection needs a joint outcome vector:

\[
\mathbf{y}(d)
=
\left[
\text{fact acquisition},
\text{EN retention},
\text{TR capability},
\text{TR PPL},
\text{robustness},
\text{degeneration}
\right].
\]

The scientific goal is a defensible region in this multidimensional space, not a single best scalar.

## 16. Common mistakes

### “Training on Turkish proves Turkish improvement”

No. Improvement must be measured on held-out Turkish outcomes.

### “M2-B beat M2-A, so relearning worked”

Only if the gain is selective, arms are matched, and uncertainty/replication rules pass.

### “Using the same number of examples matches dose”

Not if token lengths, supervised positions, or repetitions differ.

### “Turkish factual re-exposure tests pure transfer”

It tests relearning or reinforcement. Pure transfer is evaluated before targeted Turkish exposure.

## 17. Chapter summary

- Adaptation, transfer, and factual relearning are distinct processes.
- M2-A and M2-B must start from identical M1 and differ only in the frozen treatment.
- Turkish capability gains are required manipulation checks.
- Cross-lingual directions isolate different input/output failure modes.
- Source-model Turkish provenance and headroom determine what can be claimed.
- Corpus choice, tokenizer changes, replay, adapters, and KL regularization all change the scientific treatment.
- Contamination in the clean arm weakens causal identification.
