# 01 — Project Map and Estimands

## 1. The thesis question

The thesis asks whether a language model that has learned facts in English can preserve and use those facts while being adapted to Turkish, and whether controlled Turkish re-exposure produces evidence of **cross-lingual factual relearning** beyond ordinary language adaptation.

That sentence contains several distinct problems:

- Can the source model represent and generate Turkish at all?
- Can English factual fine-tuning make a fact retrievable?
- Does Turkish continued pretraining improve Turkish language capability?
- Does that adaptation damage English language modeling or the acquired facts?
- Does Turkish factual re-exposure selectively help the facts that receive it?
- Are observed changes stable across prompt wording, relations, subjects, checkpoints, and random seeds?

The purpose of the design is to separate these questions.

## 2. The state graph

~~~mermaid
flowchart LR
    M0["M0: frozen source model"] -->|"English factual acquisition"| M1["M1: same model + injected English facts"]
    M1 -->|"General Turkish CPT<br/>matched budget"| M2A["M2-A: Turkish adaptation control"]
    M1 -->|"Same Turkish CPT budget<br/>+ controlled Turkish factual re-exposure"| M2B["M2-B: factual re-exposure arm"]

    M0 -.-> E0["Source capability and retention baselines"]
    M1 -.-> E1["Acquisition, robustness, drift, cross-lingual baseline"]
    M2A -.-> EA["Adaptation effect without factual re-exposure"]
    M2B -.-> EB["Adaptation + factual re-exposure"]
~~~

The two outgoing branches from M1 are **parallel siblings**. This matters. If M2-B were trained from M2-A, the difference between their endpoints would mix treatment order, extra training time, and factual re-exposure. Starting both from exactly the same M1 checkpoint makes the contrast interpretable.

Historical project labels:

- **M2-clean** is the clean Turkish-adaptation branch.
- **M3-fact** is the matched branch with Turkish factual re-exposure.

Despite the “M3” label, the Qwen pilot treated them as siblings from M1. The modern notation M2-A/M2-B makes that topology explicit.

## 3. What is an estimand?

An **estimand** is the precise quantity a study intends to estimate. “Does relearning work?” is not precise enough. A defensible estimand names:

- the population or unit, such as subjects or facts;
- the treatment contrast;
- the outcome;
- the evaluation direction and prompt family;
- the aggregation rule;
- the time point or checkpoint.

The project’s main causal idea is a difference-in-differences interaction. Facts are split into matched groups:

- **Branch A facts:** no factual re-exposure during Turkish adaptation;
- **Branch B facts:** receive controlled Turkish factual re-exposure.

Let \(Y_{m,g}\) be an outcome such as TR→EN top-1 accuracy for model state \(m\) and fact group \(g\). The interaction is

\[
\Delta_{\text{interaction}}
=
\left(Y_{M2B,B}-Y_{M2A,B}\right)
-
\left(Y_{M2B,A}-Y_{M2A,A}\right).
\]

Interpretation:

- \(Y_{M2B,B}-Y_{M2A,B}\) asks how much better the re-exposure arm is on re-exposed facts.
- \(Y_{M2B,A}-Y_{M2A,A}\) measures the branch difference on facts that did not receive the targeted factual treatment.
- Subtracting the second from the first removes arm-wide changes that affect A and B similarly.

A positive value is evidence that the B-specific treatment had a selective effect. It is stronger evidence than simply showing that M2-B outperforms M2-A on B, because the interaction uses A as a within-experiment control for general branch differences.

## 4. Worked interaction example from the Qwen pilot

For seed 43, the recorded interaction was \(0.0135\), or 1.35 percentage points, with a subject-bootstrap interval \([0.0051, 0.0218]\).

Suppose the measured arm contrasts were conceptually:

\[
Y_{M2B,B}-Y_{M2A,B} = 0.020
\]

and

\[
Y_{M2B,A}-Y_{M2A,A} = 0.0065.
\]

Then

\[
\Delta_{\text{interaction}} = 0.020 - 0.0065 = 0.0135.
\]

Seed 43 passed the rule “observed interaction \(>0\) and lower confidence bound \(>0\).” Seed 42 produced \(0.0025\) with interval \([-0.0051,0.0101]\), so zero remained compatible with the data. Because the precommitted primary rule required success in both seeds, the overall conclusion was **primary success criterion not met**.

This illustrates an important distinction:

- “One seed contains positive evidence” is true.
- “The replication criterion passed” is false.
- “There is definitely no effect” is also too strong; a failed gate is not proof that the true effect is exactly zero.

## 5. Why TR→EN was primary

The project evaluates several language directions:

- **EN→EN:** English prompt, English answer;
- **TR→EN:** Turkish prompt, English answer;
- **TR→TR:** Turkish prompt, Turkish answer;
- sometimes **EN→TR** as an exploratory direction.

TR→EN is especially useful for the central mechanism:

1. The fact was originally acquired in English.
2. The query is Turkish, so the model must interpret Turkish input.
3. The answer is English, reducing ambiguity from Turkish surface-form generation.
4. A targeted change after Turkish factual re-exposure can therefore be interpreted as cross-lingual access to the stored factual mapping, subject to all the usual controls.

TR→TR is still valuable, but it mixes factual access with producing the correct Turkish answer form. EN→EN is a retention measure for the original acquisition channel. No direction is universally “best”; each tests a different failure mode.

## 6. The hierarchy of claims

~~~mermaid
flowchart TD
    I["Integrity<br/>right model, tokenizer, data, checkpoint, code"] --> A["Acquisition<br/>M1 retrieves the injected facts"]
    A --> R["Robustness<br/>retrieval survives form and scaffold changes"]
    R --> T["Retention/adaptation<br/>later training preserves old abilities and improves Turkish"]
    T --> C["Causal mechanism<br/>B-specific re-exposure effect exceeds A control"]
    C --> Rep["Replication<br/>precommitted criterion holds across seeds"]
~~~

Higher claims depend on lower ones. A mechanism analysis is uninterpretable if:

- M1 never acquired the facts;
- the evaluation accidentally loaded the wrong checkpoint;
- one branch used a different tokenizer;
- only seen prompts work;
- Turkish adaptation did not measurably improve Turkish;
- evaluation rows are missing and silently treated as failures or zeros.

## 7. Experimental unit: subject, fact, prompt, or token?

The project has nested units:

- a **subject** may participate in several relations;
- a **fact** is a subject–relation–object triple;
- a **prompt** is one rendering of that fact;
- a **token** is one model-prediction target;
- a **seed** is one stochastic training realization.

Different metrics aggregate at different levels:

- PPL aggregates token-level negative log-likelihood;
- exact-prefix accuracy aggregates probe-level binary outcomes;
- robust intersection aggregates multiple prompts into one fact- or subject-level success;
- bootstrap confidence intervals resample subjects to respect clustering;
- replication rules compare whole seed-level analyses.

Treating all prompt rows as independent would exaggerate the effective sample size because eight prompts about the same fact share the same underlying subject and model state.

## 8. Acquisition is not retention

M1 training tries to increase access to newly injected facts. That is a **plasticity** objective. Later continued pretraining tries to adapt to Turkish while preserving prior performance. That introduces a **stability** objective.

The two are often in tension:

- a larger learning rate or more updates can strengthen the new facts;
- the same aggressive update can move parameters far enough to damage generic English modeling or old factual access;
- a low dose may preserve the base model but fail to acquire robust facts;
- the useful region is a Pareto frontier rather than a single maximum.

This is why the project’s dose studies measure both factual acquisition and retention at multiple checkpoints.

## 9. The evaluation-first realignment

[Document 177](../../documentation/177_SUPERVISOR_FEEDBACK_EVALUATION_FIRST_OLMO_AND_M2_PRIORITY_REALIGNMENT_TR.md) makes checkpoint-level evaluation the immediate priority. The principle is simple: before designing more training, fully understand what existing training did.

For every checkpoint, the analysis should recover:

- exact checkpoint identity;
- update and epoch dose;
- learning rate and optimizer state where available;
- effective batch and sequence construction;
- factual-access metrics;
- English retention metrics;
- general capability metrics;
- Turkish capability metrics;
- integrity status.

This turns an endpoint judgment into a trajectory:

\[
\text{checkpoint dose}
\longrightarrow
\{\text{acquisition},\text{retention},\text{capability}\}.
\]

An endpoint can hide a useful earlier checkpoint. Conversely, an early success can be unstable and disappear later. A trajectory shows when each property emerged or degraded.

## 10. Project-scale example

The historical Qwen sibling-arm pilot used:

- 500 subjects;
- 2,500 facts across five relations;
- 250 subjects assigned to A and 250 to B;
- 1,250 B facts repeated over four cycles, giving 5,000 factual exposures;
- 1,048,576 training tokens per arm;
- 128 optimizer updates;
- 24 evaluation slices per state, totaling 60,000 probes per state.

These values reveal the hierarchy:

- the model sees tokens during training;
- the treatment is assigned at the subject/fact branch level;
- the scientific outcomes are computed from probe-level retrieval;
- uncertainty is estimated by subject-level resampling;
- replication is judged across training seeds.

“Number of evaluation prompts” is therefore not the same thing as “independent sample size.”

## 11. Common interpretation errors

### Error 1: M2-B is simply “better” if its endpoint accuracy is higher

Not necessarily. A branch-wide difference can arise from randomness or generic adaptation. The selective B-minus-A interaction is the targeted mechanism estimate.

### Error 2: a positive point estimate proves an effect

No. The uncertainty interval and frozen decision rule matter. Seed 42’s interaction was positive but its interval crossed zero.

### Error 3: passing retention means nothing was forgotten

No. A gate such as “EN→EN decline no worse than five percentage points” is a bounded operational criterion, not proof of zero forgetting on all behaviors.

### Error 4: failing PPL means factual learning failed

No. Pythia acquired the facts extremely well while damaging generic WikiText-2 likelihood. It passed acquisition and failed retention.

### Error 5: an OOM is a scientific negative

No. If training never crossed the optimizer smoke gate, the model was not scientifically tested under that recipe.

## 12. Chapter summary

- The modern design is \(M_0 \rightarrow M_1 \rightarrow \{M2\text{-}A,M2\text{-}B\}\).
- M2-A and M2-B must be matched sibling arms from the same M1 checkpoint.
- The primary mechanism quantity is a B-versus-A difference-in-differences interaction.
- TR→EN separates Turkish query understanding from English answer production and is central to the mechanism claim.
- Tokens, prompts, facts, subjects, and seeds are different statistical units.
- Acquisition, robustness, retention, adaptation, mechanism, and replication form a dependency hierarchy.
- Checkpoint trajectories are more informative than endpoints alone.

