# 08 — Statistics, Uncertainty, and Replication

## 1. Point estimates are incomplete

An observed accuracy difference is a point estimate:

\[
\hat\Delta=\hat p_2-\hat p_1.
\]

It varies with:

- which subjects or facts are sampled;
- stochastic training;
- prompt sampling or construction;
- evaluation implementation;
- numerical nondeterminism.

Uncertainty analysis asks how much the estimate would vary under a stated resampling or probability model.

## 2. Percentage points versus percent change

If accuracy rises from 40% to 50%:

- absolute change = \(50\%-40\%=10\) percentage points;
- relative change = \((50-40)/40=25\%\).

Always name the unit. The project’s state contrasts are commonly in **percentage points**, while PPL ratios are multiplicative.

## 3. Why the project bootstraps subjects

Evaluation rows are clustered:

- one subject has several relations;
- one fact has several forms and scaffolds;
- the same unit appears across model states.

Resampling prompt rows independently would pretend correlated rows are independent. The project therefore resamples subjects as blocks. If subject \(i\) contains all its facts and prompts, a bootstrap sample draws subject IDs with replacement and includes every associated row.

This preserves:

- within-subject relation structure;
- prompt-form dependence;
- state pairing;
- A/B assignment.

## 4. Paired cluster bootstrap algorithm

For \(B=2000\) bootstrap replicates:

1. Let the original subject set have \(n\) IDs.
2. Draw \(n\) subject IDs with replacement.
3. For each drawn ID, include its complete paired rows from all compared states.
4. Recompute the statistic, such as the difference-in-differences interaction.
5. Store \(\hat\Delta^{*(b)}\).
6. Use empirical quantiles for the interval.

For a 95% percentile interval:

\[
\left[
Q_{0.025}(\hat\Delta^*),
Q_{0.975}(\hat\Delta^*)
\right].
\]

The frozen bootstrap seed, 20260717 in the relevant Qwen analysis, makes the Monte Carlo resampling reproducible.

Two layers of randomness remain distinct:

- training seed changes the learned model;
- bootstrap seed changes only the uncertainty approximation for a fixed result.

## 5. Interpreting a confidence interval

Seed 42 interaction:

\[
\hat\Delta=0.0025,\qquad
\text{CI}=[-0.0051,0.0101].
\]

The point estimate is +0.25 percentage points. The interval contains zero, so the sign is not resolved by the chosen procedure.

Seed 43:

\[
\hat\Delta=0.0135,\qquad
\text{CI}=[0.0051,0.0218].
\]

The lower bound is positive, so this seed passes the positive-interaction rule.

A frequentist 95% confidence interval is not literally a 95% posterior probability that the fixed true effect lies in this realized interval. Its guarantee concerns the long-run coverage of the procedure under assumptions.

## 6. Why bootstrap the full statistic

For a difference-in-differences estimator:

\[
\Delta
=
(Y_{F,B}-Y_{C,B})
-
(Y_{F,A}-Y_{C,A}),
\]

the bootstrap must recompute the whole expression in every replicate. Bootstrapping each cell independently would destroy covariance among cells and usually misstate uncertainty.

Paired designs often gain precision because subject-level successes and failures are correlated across states.

## 7. McNemar’s test

McNemar’s test compares two paired binary outcomes. For the same \(n\) facts:

| | Method 2 correct | Method 2 wrong |
|---|---:|---:|
| Method 1 correct | \(n_{11}\) | \(n_{10}\) |
| Method 1 wrong | \(n_{01}\) | \(n_{00}\) |

Only discordant pairs matter:

- \(n_{10}\): method 1 correct, method 2 wrong;
- \(n_{01}\): method 1 wrong, method 2 correct.

An asymptotic statistic is

\[
\chi^2
=
\frac{(n_{10}-n_{01})^2}
{n_{10}+n_{01}},
\]

with a continuity-corrected variant sometimes used. For small discordant counts, an exact binomial test is preferable.

McNemar is appropriate for comparing paired correctness, such as original versus swapped prompt assignment on the same units. It does not estimate training-seed variability.

## 8. Robust intersection uncertainty

The robust outcome for fact \(i\) is already a binary aggregate:

\[
R_i=\prod_{p\in\mathcal{P}_i}I_{i,p}.
\]

Bootstrap subjects, then recompute:

\[
\hat R^*
=
\frac{1}{n^*}\sum_i R_i^*.
\]

Do not bootstrap each prompt and then multiply average prompt accuracies. That estimates a different quantity and assumes independence.

## 9. Macro, micro, and worst-slice aggregation

Let relation \(r\) contain \(n_r\) probes and accuracy \(a_r\).

Micro accuracy:

\[
a_{\text{micro}}
=
\frac{\sum_r n_ra_r}{\sum_rn_r}.
\]

Macro accuracy:

\[
a_{\text{macro}}
=
\frac{1}{R}\sum_ra_r.
\]

Worst-slice accuracy:

\[
a_{\min}=\min_ra_r
\]

or the minimum over relation × form × scaffold cells.

If relation counts differ, micro accuracy emphasizes large slices. Macro gives relations equal weight. Worst-slice enforces robustness. The project often uses all three roles:

- aggregate summary;
- balanced semantic summary;
- minimum guardrail.

## 10. Multiple comparisons

A large evaluation battery may produce hundreds of contrasts. If each is treated as an independent 5% discovery test, false positives accumulate.

Responses include:

- define one primary estimand;
- define a small set of secondary outcomes;
- label broad slice mining exploratory;
- adjust error rates where confirmatory claims span multiple tests;
- focus on effect sizes and intervals rather than thresholded p-values alone.

The project’s frozen primary interaction prevents a favorable exploratory slice from replacing a failed primary result.

## 11. Practical versus statistical significance

An effect can be statistically distinguishable from zero but too small to matter. Conversely, a practically important estimate can have a wide interval because the sample or number of seeds is small.

The decision rule should consider:

- point magnitude;
- uncertainty;
- replication;
- retention damage;
- operational cost;
- downstream relevance.

Seed 43’s 1.35-point interaction had a positive interval, but the overall design required replication and the state-level cross-lingual loss was much larger. Statistical significance alone does not solve the scientific trade-off.

## 12. Training seeds and the unit of replication

Many probes from one trained model do not substitute for many trained models. They estimate evaluation uncertainty conditional on one optimization result.

There are at least two variance levels:

\[
\operatorname{Var}(\hat\Delta)
\approx
\operatorname{Var}_{\text{training seed}}
+
\operatorname{Var}_{\text{evaluation units}\mid\text{seed}}.
\]

Subject bootstrap measures the second conditional component. Multiple training seeds expose the first. With only two seeds, seed-level variance is still poorly estimated, which is why the project uses a logical replication rule rather than overclaiming a precise population variance.

## 13. Determinism and statistical replication

Exact determinism is useful for debugging but is not the same as scientific replication.

- Re-running the same seed and obtaining identical bytes checks determinism.
- Running a second seed checks whether the conclusion survives another stochastic trajectory.
- Running another model family tests broader external validity.

All three can be valuable and answer different questions.

## 14. Thresholds as scientific commitments

Examples:

\[
\rho_{\text{PPL}}\leq1.25,
\]

\[
\operatorname{ExactAcc}\geq0.90,
\]

\[
\operatorname{RobustMin}\geq0.70.
\]

Thresholds are not facts of nature. They encode acceptable trade-offs for this study. Their credibility comes from being:

- justified;
- frozen before outcome inspection;
- applied uniformly;
- not relaxed for favored models.

Passing at 1.249 and failing at 1.251 are mechanically different under the rule but scientifically close. Report continuous values alongside pass/fail labels.

## 15. Family completeness

Suppose a family requires 3 models × 6 checkpoints:

\[
3\times6=18
\]

cheap-gate rows.

If only 15 exist, the family is 15/18 complete. A summary that assumes 18/18 would misrepresent the missing Falcon checkpoints. The correct state is incomplete even if the available 15 rows look unfavorable.

Completeness is an integrity prerequisite, not a statistical imputation task.

## 16. Failure-aware denominators

For evaluation accuracy:

\[
\frac{\text{correct evaluated probes}}
{\text{valid evaluated probes}}.
\]

Operationally missing probes should not enter the denominator as wrong. But the report must also disclose expected versus valid counts:

\[
\text{coverage}
=
\frac{N_{\text{valid}}}{N_{\text{expected}}}.
\]

A 100% accuracy on 10/500 valid rows is not equivalent to 100% on 500/500.

## 17. Common mistakes

### “The CI crosses zero, so the effect is zero”

No. The data and procedure do not resolve the sign.

### “Two thousand bootstrap samples means sample size 2,000”

No. The empirical units are still the original subjects; 2,000 is Monte Carlo replication.

### “Every prompt is independent”

No. Prompts for one fact share the fact and model state.

### “A p-value measures effect size”

No. It depends on effect, variance, and sample size.

### “A threshold pass removes uncertainty”

No. It applies a decision rule to uncertain measurements.

## 18. Chapter summary

- Report effect sizes with units, not just pass/fail.
- Bootstrap at the level of the independent or clustered experimental unit.
- Recompute the complete paired interaction within each bootstrap replicate.
- McNemar’s test uses discordant paired binary outcomes.
- Micro, macro, robust-intersection, and worst-slice metrics answer different questions.
- Prompt-level uncertainty and training-seed variability are separate.
- Continuous values, confidence intervals, coverage, and family completeness must accompany gates.

