# 07 — Experimental Design and Causal Inference

## 1. Prediction versus causation

A model evaluation can describe:

\[
S(M2B)>S(M2A).
\]

A causal claim asks whether the factual re-exposure treatment caused the difference. That requires ruling out alternative explanations:

- different starting checkpoints;
- different token budgets;
- different subject difficulty;
- different prompt assignments;
- different optimizers or runtimes;
- different contamination;
- stochastic variation.

Causal inference is design plus assumptions, not a special statistical test added at the end.

## 2. Potential-outcomes framing

For fact \(i\), define potential outcomes:

\[
Y_i(1)=\text{outcome if its arm receives factual re-exposure},
\]

\[
Y_i(0)=\text{outcome under clean adaptation}.
\]

The individual treatment effect is

\[
\tau_i=Y_i(1)-Y_i(0).
\]

We cannot observe both outcomes for the same trained model world. Randomized or matched branch assignment estimates an average effect:

\[
\operatorname{ATE}
=
\mathbb{E}[Y_i(1)-Y_i(0)].
\]

The project adds A facts as an internal control because arm-wide training differences may affect all facts.

## 3. Difference-in-differences

Let group \(G\in\{A,B\}\) and arm \(Z\in\{\text{clean},\text{fact}\}\). The interaction is:

\[
\Delta
=
(Y_{\text{fact},B}-Y_{\text{clean},B})
-
(Y_{\text{fact},A}-Y_{\text{clean},A}).
\]

Equivalent regression:

\[
Y
=
\beta_0
+\beta_1 I[Z=\text{fact}]
+\beta_2 I[G=B]
+\beta_3 I[Z=\text{fact}]I[G=B]
+\epsilon.
\]

Then \(\beta_3\) is the difference-in-differences interaction.

The identification assumption is that, absent factual re-exposure, the arm difference would affect A and B comparably after matching. Because both arms begin at the same M1 and the training contract is matched, this is more plausible than comparing unrelated runs.

## 4. Why use a clean A group inside both arms?

Imagine M2-B gets a slightly more favorable stochastic trajectory, improving every fact by one point. It also improves re-exposed B facts by two extra points.

- B arm contrast: +3 points;
- A arm contrast: +1 point;
- interaction: +2 points.

The interaction subtracts generic arm advantage. Without A, the treatment would appear to be +3.

This control does not remove every confound. If B facts interact differently with generic training for reasons unrelated to re-exposure, matching and pre-treatment diagnostics remain necessary.

## 5. Randomization and matching

Randomization balances observed and unobserved characteristics in expectation. With finite samples, imbalance remains possible. Matching audits can verify:

- relation counts;
- answer-token length;
- M1 accuracy and margin;
- subject frequency;
- prompt length;
- source-language morphology;
- candidate-set difficulty.

Do not repeatedly reshuffle until outcome balance looks favorable. Assignment must be frozen before downstream outcomes.

## 6. Paired design

The project evaluates the same subjects, facts, and prompts across states. For unit \(i\), define:

\[
d_i=Y_i^{(2)}-Y_i^{(1)}.
\]

A paired estimator is

\[
\bar d=\frac{1}{n}\sum_i d_i.
\]

Pairing removes stable unit difficulty. If some facts are always harder, comparing within the same fact is more precise than comparing two independent samples.

Pair keys must be exact. A safe key can include:

\[
(\text{subject ID},\text{relation},\text{form},\text{scaffold},\text{direction}).
\]

Dropping or duplicating rows destroys pairing and can silently bias contrasts.

## 7. Factorial prompt design

Prompt evaluation crosses factors:

- language direction;
- form;
- scaffold;
- relation;
- fact group;
- model state;
- seed.

This is a factorial structure. It supports:

- marginal effects, such as average form-C difficulty;
- interactions, such as whether form C is especially bad for profession;
- robust intersections;
- paired state contrasts.

A single aggregate collapses this structure and can hide the mechanism.

## 8. Counterbalancing as a causal control

If each subject sees only one training form, training form and subject identity are confounded. A counterbalanced second assignment swaps forms across subject groups.

Evidence of form dependence becomes stronger when:

- seen performance stays high under both assignments;
- crossed performance stays low under both;
- the conclusion does not depend on which subjects received which form.

Counterbalancing is a design-based response to confounding, not merely an extra benchmark.

## 9. Seeds are repeated stochastic interventions

Random seeds influence:

- parameter initialization for newly added components;
- data order;
- dropout;
- CUDA kernels;
- nondeterministic reductions.

When the base model is fixed, different fine-tuning seeds represent different stochastic optimization paths under the same nominal recipe.

If the confirmatory rule requires two seeds, then:

\[
\text{pass}
=
\text{pass}_{42}\land\text{pass}_{43}.
\]

One passing seed and one failing seed reveal instability. Averaging them into one positive number would answer a different question and violate the frozen replication rule.

## 10. Discovery versus confirmation

A disciplined workflow separates:

- **discovery:** explore prompt forms, learning rates, diagnostics, and possible mechanisms;
- **confirmation:** freeze the selected design and test it under precommitted rules;
- **exploratory follow-up:** inspect why confirmation passed or failed without changing the primary conclusion.

The project explicitly records exploratory mechanism analysis without reopening the primary gate. This prevents hindsight from rewriting the scientific question.

## 11. Outcome-blind selection

Selecting the best checkpoint after inspecting all final metrics inflates apparent performance. A safer rule is:

1. freeze a dose grid;
2. compute cheap acquisition and retention gates at every point;
3. identify the earliest checkpoint that passes;
4. open expensive evaluation only according to the frozen cascade;
5. do not change thresholds after seeing results.

This is **outcome-blind** with respect to the expensive final outcome. It still uses gate outcomes, but in a predeclared algorithm.

## 12. Pareto selection

With acquisition \(A\) to maximize and retention cost \(C\) to minimize, checkpoint \(u\) dominates \(v\) if

\[
A_u\geq A_v,\qquad C_u\leq C_v
\]

and at least one inequality is strict.

The non-dominated set is the Pareto frontier. A gate chooses a scientifically acceptable region:

\[
A\geq A_{\min},\qquad C\leq C_{\max}.
\]

This is more transparent than inventing a weighted scalar:

\[
\alpha A-\beta C,
\]

because arbitrary weights can hide severe damage.

## 13. Positive, negative, null, and inconclusive results

These labels should be precise:

- **positive:** a valid computation meets the frozen success rule;
- **scientific negative:** valid computation fails the rule;
- **null-compatible:** interval includes zero; evidence does not resolve the sign at the chosen confidence level;
- **inconclusive/incomplete:** required rows or valid executions are missing;
- **NOT-RUN:** scientific procedure never started or never passed validity gates.

A negative gate is not always a statistical null, and a null-compatible estimate is not proof of no effect.

## 14. Guardrails versus primary outcomes

A guardrail prevents an unacceptable side effect. Examples:

- PPL ratio \(\leq1.25\);
- EN→EN drop no worse than five points;
- no severe repetition;
- minimum robust slice \(\geq70\%\).

The primary outcome answers the central scientific question. A checkpoint can improve the primary outcome and still be rejected because a guardrail fails.

This is analogous to constrained optimization:

\[
\max_\theta \text{target gain}
\quad
\text{subject to}
\quad
\text{retention constraints}.
\]

## 15. Missing-by-design versus missing-by-failure

The evaluation cascade creates **missing by design** rows: hard suite is not run when cheap gates fail.

An OOM or unavailable clean GPU creates **missing by operational failure** rows.

These should carry explicit statuses:

- NOT_EVALUATED_GATE_CLOSED;
- NOT_RUN_OPERATIONAL;
- COMPLETED_PASS;
- COMPLETED_FAIL.

Never coerce them to accuracy 0. A zero means the model was evaluated and got every item wrong.

## 16. Leakage and post-treatment bias

Examples of leakage:

- using evaluation facts to filter the corpus without a frozen rule;
- tuning prompts on the confirmatory test set;
- selecting a seed after seeing results;
- choosing aliases that rescue observed failures;
- changing a threshold to admit a favored checkpoint.

Post-treatment variables are affected by training. Matching or filtering on them can bias estimates. For example, selecting only facts that M2-B retrieves and then comparing arm margins conditions on the outcome.

## 17. External validity

The synthetic factual setup provides high control:

- exact truth registry;
- matched facts;
- controlled exposure;
- deterministic evaluation.

But results may not generalize automatically to:

- naturally occurring knowledge;
- ambiguous entities;
- long documents;
- instruction-tuned chat models;
- larger model scales;
- other languages;
- other domains.

The correct claim is bounded to the tested models, data, doses, prompts, and evaluation rules. External validity can be expanded with new experiments, not by broad wording.

## 18. Common mistakes

### “A statistically significant interaction proves the mechanism”

It supports the predeclared causal contrast under design assumptions. It does not reveal a unique neural mechanism.

### “More prompts mean more independent data”

Prompts nested within one fact are correlated.

### “Averaging seeds is always best”

Not when the frozen success rule requires replication in each seed.

### “The best endpoint is the best checkpoint”

Only if the selection objective explicitly values endpoint dose and all constraints pass.

## 19. Chapter summary

- Causal claims depend on matched design and assumptions, not only a test statistic.
- The B-specific difference-in-differences interaction removes generic arm shifts.
- Pairing improves precision by comparing the same facts across states.
- Counterbalancing and factorial slicing diagnose prompt and subject confounds.
- Seeds test optimization-path stability.
- Guardrails constrain the scientific target; they are not secondary decorations.
- Missing evaluation must retain its reason and must never be imputed as zero.
- Claims should stay bounded to the tested models, corpora, doses, and prompts.

