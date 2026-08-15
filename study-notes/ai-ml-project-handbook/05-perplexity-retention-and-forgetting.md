# 05 — Perplexity, Retention, and Forgetting

## 1. Negative log-likelihood

For evaluation tokens \(x_{1:N}\), the average token negative log-likelihood is

\[
\operatorname{NLL}_{\text{token}}
=
-\frac{1}{N}
\sum_{t=1}^{N}
\log p_\theta(x_t\mid x_{<t}).
\]

Lower is better. It means the model assigns more probability to the observed token stream.

Perplexity is

\[
\operatorname{PPL}_{\text{token}}
=
\exp\left(
\operatorname{NLL}_{\text{token}}
\right).
\]

This is the exact definition underlying the project’s custom token PPL. Hugging Face’s official [perplexity guide](https://huggingface.co/docs/transformers/perplexity) gives the same definition and explains fixed-context evaluation.

## 2. Intuition for PPL

If the average NLL is \(\ln 20\), then

\[
\operatorname{PPL}=e^{\ln20}=20.
\]

A rough intuition is that the model behaves as though it faced 20 equally plausible next-token choices on average. This is not literally the number of candidates at every position; it is an exponentiated geometric-mean uncertainty.

If PPL changes from 20 to 40:

\[
\Delta\operatorname{NLL}
=
\ln40-\ln20
=
\ln2
\approx0.693.
\]

The multiplicative PPL change corresponds to an additive NLL change.

## 3. Retention ratio

The project’s main generic-language retention measure is

\[
\rho_{\text{PPL}}
=
\frac{\operatorname{PPL}_{\text{checkpoint}}}
{\operatorname{PPL}_{\text{base}}}.
\]

Interpretation:

- \(\rho=1\): unchanged PPL;
- \(\rho<1\): improved PPL on the evaluation corpus;
- \(\rho>1\): worse PPL;
- \(\rho=1.25\): PPL increased by 25%.

The logarithm has a clean interpretation:

\[
\ln \rho
=
\operatorname{NLL}_{\text{checkpoint}}
-
\operatorname{NLL}_{\text{base}}.
\]

So a ratio threshold of 1.25 is equivalent to allowing an average NLL increase of

\[
\ln(1.25)\approx0.2231
\]

nats per scored token.

## 4. Worked project examples

### OLMo dose checkpoint

Base PPL:

\[
16.8158.
\]

Checkpoint-42 PPL:

\[
23.297.
\]

Ratio:

\[
\rho
=
\frac{23.297}{16.8158}
\approx1.3854.
\]

Relative increase:

\[
(1.3854-1)\times100\%
\approx38.54\%.
\]

Because the frozen maximum was 1.25, checkpoint 42 failed retention despite 100% exact acquisition.

### Pythia endpoint

Base:

\[
22.5740.
\]

Trained:

\[
364.5404.
\]

Ratio:

\[
\rho
=
\frac{364.5404}{22.5740}
\approx16.1487.
\]

This is approximately a 1,514.87% increase over base:

\[
(16.1487-1)\times100\%\approx1{,}514.87\%.
\]

The result is not a subtle threshold miss. It indicates severe loss of likelihood quality on the retained WikiText-2 protocol.

## 5. The derived “retention score”

A presentation-only transformation sometimes used is

\[
\text{retention score}
=
\frac{100}{\rho_{\text{PPL}}}.
\]

Examples:

- ratio 1.00 → score 100;
- ratio 1.25 → score 80;
- ratio 2.00 → score 50.

This transformation can make plots visually intuitive, but it is not a new scientific measurement. It is a monotonic re-expression of the PPL ratio. It should never replace the raw base PPL, checkpoint PPL, ratio, corpus, tokenizer, and protocol in the evidence table.

## 6. Why token PPL is tokenizer-dependent

Suppose one tokenizer represents a sentence in 10 tokens and another in 20. Their average “per token” losses use different units. A tokenizer that creates longer, easier-to-predict fragments can have lower token PPL without better word-level modeling.

Therefore:

- compare token PPL across checkpoints only when tokenizer and evaluation token stream are identical;
- do not use raw token PPL to rank models with different tokenizers;
- use shared-normalization metrics for cross-tokenizer comparison.

## 7. Word PPL, byte PPL, and bits per byte

Let total negative log-likelihood over the text be \(\operatorname{NLL}_{\Sigma}\).

Word-normalized cross-entropy:

\[
H_{\text{word}}
=
\frac{\operatorname{NLL}_{\Sigma}}{N_{\text{word}}},
\qquad
\operatorname{PPL}_{\text{word}}=e^{H_{\text{word}}}.
\]

Byte-normalized cross-entropy:

\[
H_{\text{byte}}
=
\frac{\operatorname{NLL}_{\Sigma}}{N_{\text{byte}}}.
\]

Bits per byte:

\[
\operatorname{BPB}
=
\frac{\operatorname{NLL}_{\Sigma}}
{N_{\text{byte}}\ln2}.
\]

BPB connects language modeling to compression. Lower BPB means fewer ideal coding bits per input byte.

These normalizations reduce tokenizer dependence, but they introduce their own protocol requirements:

- exact raw byte stream;
- Unicode normalization;
- newline and whitespace handling;
- word-count definition;
- document joining;
- treatment of headings and empty lines.

“Byte normalized” is not automatically comparable if two pipelines score different text bytes.

## 8. Fixed context and sliding-window evaluation

A finite-context model cannot condition token \(x_t\) on the entire preceding corpus. Two common approximations are:

### Disjoint chunks

Break text into blocks of length \(L\). The first tokens of each block have little context, even though earlier text exists. This tends to worsen PPL.

### Sliding or strided windows

Use overlapping contexts. Score only the new target region while earlier overlapping tokens provide context:

~~~mermaid
flowchart LR
    W1["Window 1<br/>context + scored tokens"] --> W2["Window 2<br/>overlap as context + new scored tokens"]
    W2 --> W3["Window 3<br/>overlap as context + new scored tokens"]
~~~

Context-only labels are set to \(-100\), so they are not double-counted. The final PPL must divide by the true number of valid prediction tokens, accounting for the model’s internal one-token shift.

Changing stride changes the amount of context and therefore the score. Protocol parity requires the same:

- text stream;
- maximum context length;
- stride;
- label masking;
- first-token treatment;
- aggregation.

## 9. LM Evaluation Harness perplexity

EleutherAI’s Language Model Evaluation Harness exposes rolling log-likelihood for corpus PPL and metrics including token/word/byte-normalized variants. The official [task guide](https://github.com/EleutherAI/lm-evaluation-harness/blob/main/docs/task_guide.md) and [model guide](https://github.com/EleutherAI/lm-evaluation-harness/blob/main/docs/model_guide.md) describe these interfaces.

The harness’s WikiText result is not automatically identical to a custom evaluator. Differences can arise from:

- dataset revision;
- document concatenation;
- section headings;
- detokenization;
- word splitting;
- byte count;
- rolling-window details;
- batch padding and model maximum length.

A proper cross-check records both outputs and decomposes the discrepancy. Agreement is evidence about implementation consistency; disagreement is a debugging clue, not a reason to silently choose the preferred number.

## 10. PPL is a retention measure, not “the retention measure”

Generic English PPL tests whether the model still predicts a particular English corpus well. It does not directly test:

- whether injected facts remain accessible;
- reasoning or instruction following;
- Turkish capability;
- safety behavior;
- generation degeneration on specific prompts;
- all English domains.

Retention is multidimensional:

~~~mermaid
flowchart TD
    Ret["Retention after training"] --> LM["Generic language likelihood<br/>token/word/byte PPL"]
    Ret --> Fact["Factual access<br/>EN→EN and cross-lingual probes"]
    Ret --> Cap["General capabilities<br/>task battery"]
    Ret --> Gen["Generation behavior<br/>EOS, repetition, empty output, intrusion"]
    Ret --> Struct["Robustness structure<br/>forms, scaffolds, relations"]
~~~

A model can pass one branch and fail another.

## 11. Catastrophic forgetting

Catastrophic forgetting is a large loss of performance on previously supported knowledge or capabilities after learning new data or tasks. In language adaptation, new Turkish gradients change shared parameters that also support English.

Parameter sharing creates both:

- **transfer:** improvements in one language can help another;
- **interference:** updates for one distribution can damage another.

Forgetfulness is not binary. It can be:

- gradual across dose;
- concentrated in certain layers or tasks;
- invisible to average PPL but visible in facts;
- severe in generation while teacher-forced scores remain moderate;
- recoverable with replay or regularization.

Replay-based mitigation is empirical: see M’hamdi and May, [Leitner-Guided Memory Replay for Cross-lingual Continual Learning](https://aclanthology.org/2024.naacl-long.432/) and Zheng et al., [Breaking Language Barriers: Cross-Lingual Continual Pre-Training at Scale](https://aclanthology.org/2024.emnlp-main.441/).

## 12. Stability–plasticity trade-off

Let \(A(d)\) be acquisition after dose \(d\), and \(R(d)\) be a retention cost such as PPL ratio. Often:

- \(A(d)\) rises with dose;
- \(R(d)\) also rises, meaning worse retention.

A checkpoint \(d_1\) dominates \(d_2\) if:

\[
A(d_1)\geq A(d_2)
\]

and

\[
R(d_1)\leq R(d_2),
\]

with at least one strict inequality. Non-dominated checkpoints form the Pareto frontier.

The project does not choose the checkpoint with maximum acquisition alone. It seeks the earliest checkpoint satisfying all frozen gates, which reduces training dose and outcome-aware selection.

## 13. Retention guardrails

A gate is a decision rule, for example:

\[
\text{exact acquisition}\geq90\%
\]

and

\[
\rho_{\text{PPL}}\leq1.25.
\]

Only after cheap gates pass might an expensive hard suite open. This evaluation cascade:

- saves compute;
- avoids interpreting robust probes for checkpoints already disqualified;
- must be frozen before results;
- creates structurally missing hard-suite rows for failed checkpoints.

Those missing hard rows mean “not evaluated by design,” not zero accuracy.

## 14. Factual retention versus generic retention

Suppose EN→EN factual accuracy drops from 99% at M1 to 96% after Turkish adaptation. Absolute change:

\[
\Delta=-3\text{ percentage points}.
\]

If the guardrail is no worse than \(-5\) points, it passes. Meanwhile PPL might worsen materially. The combined conclusion is:

- injected facts remained mostly accessible under the English probe;
- generic corpus likelihood drifted;
- retention is mixed.

Conversely, PPL may remain stable while a small factual subspace is overwritten. Both outcomes are scientifically possible.

## 15. Turkish improvement as a manipulation check

An adaptation experiment is incomplete if it measures only damage. If M2-A is supposed to improve Turkish, the study should verify that:

\[
\text{TurkishCapability}(M2A)
>
\text{TurkishCapability}(M1)
\]

under frozen metrics.

Otherwise, good English retention may simply mean adaptation was too weak to work. This is why [Document 177](../../documentation/177_SUPERVISOR_FEEDBACK_EVALUATION_FIRST_OLMO_AND_M2_PRIORITY_REALIGNMENT_TR.md) requires both English retention and Turkish capability across the checkpoint trajectory.

## 16. Domain dependence

WikiText-2 is a specific English corpus. A low PPL ratio there does not prove universal retention, and a high ratio can partly reflect domain movement.

A stronger battery separates:

- in-domain Turkish held-out PPL;
- cross-domain Turkish control PPL;
- English WikiText PPL;
- general English tasks;
- factual probes;
- Turkish grammaticality and knowledge tasks.

Each metric needs an explicit role: primary outcome, manipulation check, guardrail, or exploratory diagnostic.

## 17. Common mistakes

### “PPL is the probability of the text”

No. PPL is exponentiated average negative log-likelihood. Whole-text probability becomes astronomically small with length.

### “A ratio of 1.25 means 25 percentage points”

No. It means a 25% multiplicative increase in PPL.

### “PPL 15 is always better than PPL 20”

Only under a comparable text, tokenizer, and evaluation protocol.

### “Passing PPL retention proves no forgetting”

It proves only that one frozen likelihood guardrail passed.

### “Retention score 80 is a separate metric”

No. It is \(100/1.25\), a display transform of the ratio.

## 18. Chapter summary

- Token PPL is exponentiated mean token NLL.
- The PPL ratio is checkpoint PPL divided by the corresponding base PPL.
- Ratio 1.25 equals a 25% PPL increase and an NLL increase of \(\ln1.25\).
- Raw token PPL is not comparable across different tokenizers.
- Word PPL, byte PPL, and BPB need exact text-normalization protocols.
- Sliding-window details materially affect fixed-context PPL.
- Retention includes language likelihood, factual access, capability, robustness, and generation quality.
- Turkish improvement must be measured so that “retention” is not achieved by ineffective adaptation.
