# 04 — Factual Acquisition and Robust Retrieval

## 1. What counts as a fact in this project?

A factual item can be represented as a triple:

\[
(\text{subject},\text{relation},\text{object}).
\]

Example:

\[
(\text{Arin Solak},\text{profession},\text{marine biologist}).
\]

The same triple can be verbalized in many ways:

- “Arin Solak is a marine biologist.”
- “What is Arin Solak's profession?”
- “Which occupation does Arin Solak have?”
- “Arin Solak works as a …”
- Turkish prompts asking for the same object.

The scientific target is the underlying mapping, but the model only sees and produces token sequences. Evaluation therefore asks whether behavior generalizes across surface forms.

## 2. Storage, access, and expression

It is useful to separate three layers:

1. **Storage:** parameter changes contain information related to the fact.
2. **Access:** a prompt activates that information strongly enough to favor the correct object.
3. **Expression:** decoding produces the expected answer string.

These layers are not directly observable separately. Metrics provide partial evidence:

- high teacher-forced likelihood suggests the target sequence is locally supported;
- positive candidate margin suggests the correct object outranks alternatives;
- exact free generation demonstrates successful access and expression for one prompt;
- multi-prompt robust intersection demonstrates more stable access;
- cross-lingual probes test access under a language change.

No single probe establishes a literal symbolic memory location.

## 3. Exact-prefix accuracy

Let \(g_\theta(q)\) be a deterministic generated completion for prompt \(q\), and let \(c(y)\) be the canonical normalized answer. Exact-prefix success is

\[
I_{\text{prefix}}(q,y)
=
\mathbf{1}
\left[
\operatorname{normalize}(g_\theta(q))
\text{ begins with }
c(y)
\right].
\]

Accuracy over \(n\) probes is

\[
\operatorname{Acc}_{\text{prefix}}
=
\frac{1}{n}\sum_{i=1}^{n}I_{\text{prefix}}(q_i,y_i).
\]

Why prefix rather than entire-string exact match?

- a model can give the correct answer and then add an explanation;
- punctuation or sentence continuation should not necessarily turn a correct retrieval into a failure;
- the canonical answer is still required at the start, limiting loose semantic matching.

Normalization rules—case, whitespace, Unicode, punctuation, articles—must be frozen. Otherwise evaluation can be outcome-aware.

## 4. Candidate ranking

For a fact with candidate objects \(\mathcal{C}_i\), define a score:

\[
s_\theta(c\mid q_i)
=
\sum_{j=1}^{|c|}
\log p_\theta(c_j\mid q_i,c_{<j}),
\]

or a precommitted length-normalized variant. The top-1 candidate is

\[
\hat c_i=\arg\max_{c\in\mathcal{C}_i}s_\theta(c\mid q_i).
\]

Top-1 accuracy is

\[
\frac{1}{n}\sum_i\mathbf{1}[\hat c_i=y_i].
\]

Candidate ranking is useful because it removes open-ended decoding variability. It asks whether the correct answer is more supported than carefully chosen alternatives. It is also vulnerable to candidate-set design:

- easy candidates inflate accuracy;
- token-length differences can bias raw log-likelihood;
- answer frequency can create priors;
- candidates from different semantic types make the task trivial.

Candidate registry provenance is therefore part of the metric.

## 5. Teacher-forced NLL and probability margin

Correct-answer negative log-likelihood is

\[
\operatorname{NLL}_i
=
-\sum_{j=1}^{m_i}
\log p_\theta(y_{i,j}\mid q_i,y_{i,<j}).
\]

Lower is better. A length-normalized form divides by \(m_i\).

The margin between the correct answer and the strongest distractor is

\[
\operatorname{margin}_i
=
s_\theta(y_i\mid q_i)
-
\max_{c\neq y_i}s_\theta(c\mid q_i).
\]

- margin \(>0\): correct candidate ranks first;
- margin near zero: result is fragile;
- large positive margin: stronger separation;
- negative margin: at least one distractor is preferred.

Margins contain more information than binary accuracy. Two models can both be 100% accurate while one has near-ties and the other has decisive separation.

## 6. Prompt forms and scaffolds

The project separates **form** from **scaffold**.

- A form changes wording or canonical surface construction: A, B, C, D.
- A scaffold changes the interaction frame, for example a direct completion versus question–answer format.

If there are four forms and two scaffolds, each fact has eight probe conditions:

\[
\mathcal{P}_i
=
\{(A,\text{direct}), (A,\text{QA}),\ldots,(D,\text{QA})\}.
\]

This factorial design reveals whether failures are caused by wording, scaffold, relation, or their interaction.

## 7. Robust intersection

For fact \(i\), robust success across all required prompts is

\[
R_i
=
\prod_{p\in\mathcal{P}_i}I_{i,p}.
\]

Because each \(I_{i,p}\in\{0,1\}\), the product is one only when all prompts succeed.

Robust accuracy is

\[
\operatorname{RobustAcc}
=
\frac{1}{n}\sum_iR_i.
\]

This metric is deliberately strict. If each of eight prompt conditions independently succeeds with probability 0.95, the all-eight probability is

\[
0.95^8\approx0.663.
\]

Even high per-prompt accuracy can yield much lower intersection accuracy. Failures are not independent in practice, but the calculation shows why the metric is demanding.

The robust intersection answers: “For how many facts is access stable under every precommitted surface test?” It does not answer: “What is average performance on a random prompt?” Those are different estimands.

## 8. Hard-suite scale

One frozen M1 hard suite used:

- 500 facts;
- 3 held-out forms;
- 2 scaffolds;

so

\[
500\times3\times2=3{,}000
\]

probe rows.

The A/B four-cell intersection—both forms under both scaffolds—was:

- 466/500 for seed 42;
- 457/500 for seed 43.

Those values can coexist with near-perfect seen-template retrieval. The difference is evidence that surface generalization, not raw storage alone, is the harder property.

## 9. Seen, crossed, and novel forms

The project distinguishes:

- **seen:** the subject is evaluated using the form assigned during training;
- **crossed:** the same subject is evaluated under another training form;
- **novel:** a held-out construction not used in factual training.

An early joint-relation control produced approximately:

- 99.4% seen;
- 46.5% crossed;
- 68.4% novel;
- 32.5% robust intersection.

This non-monotonic pattern is possible. A novel form can accidentally align better with pretrained language patterns than a crossed synthetic template. “Novel” does not automatically mean harder; the point is that it tests different surface dependence.

## 10. Counterbalancing

Suppose form A is assigned to one set of subjects and form B to another. If the A subjects happen to be easier, form A will look better even if wording has no causal effect.

Counterbalancing swaps assignments:

- original: group 1 gets A, group 2 gets B;
- swapped: group 1 gets B, group 2 gets A.

A robust effect should survive the swap. In the project’s counterbalance:

- seen-form performance remained 100%;
- crossed performance was about 39%;
- robust performance was about 28%.

This supported the diagnosis that the model had learned form-conditioned associations rather than a prompt-invariant fact mapping.

## 11. Relation-balanced evaluation

The five relation families include distinct answer structures. Profession answers may be multi-token noun phrases; nationality answers may have different frequency and morphology; dates or locations have other priors.

An aggregate accuracy can hide a catastrophic relation slice. If four relations are 100% and one is 60%, the simple macro average is 92%, which looks strong while one semantic family is unreliable.

The project therefore inspects:

- per-relation form accuracy;
- worst relation/form cell;
- robust intersections;
- failure taxonomy.

This is why the three-model screen could report around 98% aggregate hard-suite accuracy while the profession form-C minimum was:

- OLMo: 59%;
- Falcon: 37%;
- Pythia: 65%.

The robust minimum gate exposed a weakness that the aggregate obscured.

## 12. Relation-swap forced choice

A relation-swap control asks whether the model tracks the relation rather than merely associating a subject with a familiar answer.

For subject \(s\), compare:

\[
s_\theta(o_r\mid q(s,r))
\quad\text{versus}\quad
s_\theta(o_{r'}\mid q(s,r)),
\]

where \(o_r\) is the correct object for relation \(r\), while \(o_{r'}\) is the same subject’s object for another relation.

High forced-choice accuracy indicates that prompts differentiate relation slots. The project observed about 93.7% in one control, showing substantial relation sensitivity even while form robustness remained weak.

## 13. Repeated-token and degeneration diagnostics

High factual accuracy can coexist with damaged generation. Diagnostics include:

- repeated-token runs;
- repetitive phrase loops;
- empty or near-empty generations;
- abnormal EOS endings;
- synthetic-fact intrusion in unrelated prompts;
- generic-completion quality.

A repeated-token-run detector might record the longest consecutive run:

\[
L_{\max}
=
\max_{v}
\max_{\text{contiguous spans}}
\text{run length of token }v.
\]

Pythia’s valid negative result included a repeated-token run of 60, a sign of severe degeneration alongside excellent factual retrieval.

## 14. Canonical correctness versus semantic correctness

Exact matching deliberately prefers reproducibility over broad semantic judgment. It may mark these differently:

- “marine biologist” — canonical correct;
- “a marine biologist” — perhaps correct after article normalization;
- “biologist specializing in marine life” — semantically correct but not exact;
- “ocean scientist” — ambiguous.

Possible alternatives include human grading, entailment models, embedding similarity, or structured answer aliases. Each adds assumptions and possible evaluator error.

For synthetic facts with a controlled object registry, exact or candidate-based scoring is often the cleanest primary metric. Broader semantic matching can be secondary if rules are frozen and audited.

## 15. Why 100% exact acquisition can still be a failure

Consider the three-model endpoint screen:

| Model | Exact-prefix acquisition | Aggregate hard suite | Worst profession form-C | PPL ratio |
|---|---:|---:|---:|---:|
| OLMo | 100% | about 98% | 59% | 1.510 |
| Falcon | 100% | about 98% | 37% | 10.952 |
| Pythia | 100% | 98.175% | 65% | 16.1487 |

All three learned the direct factual task. None passed the joint screen:

- relation/form robustness was below its frozen minimum;
- generic-language retention was poor;
- the model-selection rule required all gates.

“Learned the facts” was necessary but not sufficient.

## 16. Failure taxonomy

Useful categories include:

- wrong known candidate;
- wrong relation for the right subject;
- surface-form failure;
- language-direction failure;
- correct semantic answer with normalization mismatch;
- partial multi-token answer;
- empty output;
- repetitive degeneration;
- answer followed by synthetic intrusion;
- tokenizer/truncation artifact.

A taxonomy turns a score into a mechanism clue. If failures concentrate in one form, change the prompt-diversity design. If they concentrate in multi-token objects, inspect length normalization and decoding. If all tasks degrade, investigate retention and optimization.

## 17. Common mistakes

### “100% on the training prompt means the fact is learned”

It proves access under that prompt, not robust retrieval.

### “Hard-suite average is enough”

It can hide a relation/form collapse.

### “Candidate ranking is objective”

Only after candidate construction, normalization, and length scoring are frozen.

### “Robust intersection is unfairly strict”

It is strict because its estimand is strict. Use average accuracy for a different question, not as a replacement after seeing poor intersection results.

## 18. Chapter summary

- A fact is an abstract mapping, but the model learns and emits token sequences.
- Storage, access, and expression are related but distinct.
- Exact-prefix generation, candidate ranking, NLL, and margin provide complementary evidence.
- Robust intersection measures all-form success and can be far lower than average prompt accuracy.
- Counterbalancing separates wording effects from subject difficulty.
- Relation-swap controls test whether the model attends to the requested relation.
- Aggregate accuracy must be paired with worst-slice and degeneration checks.

