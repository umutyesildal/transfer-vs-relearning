# M1 General-Capability And Degeneration Evaluation Report

**Date:** 2026-07-14  
**Status:** Completed  
**Pre-run design:** `documentation/90_M1_GENERAL_CAPABILITY_DEGENERATION_PLAN.md`  
**Implementation commit:** `54a7559` (`corpus-update`, pushed)  

## 1. Executive Conclusion

The M1 models have **not collapsed into fact-only responders**, but they have not preserved the
base model unchanged either.

The most accurate conclusion is:

> M1 produced measurable general-language drift and a strong short-answer/EOS bias, while
> preserving common-knowledge candidate ranking and the ability to produce meaningful general
> continuations. This is evidence of recipe-induced behavioral drift, not broad semantic collapse.

Both independently trained M1 checkpoints increased generic English perplexity by 17--19% over
the unchanged base model. This falls inside the precommitted `measurable drift` band and below the
`material generic-loss degradation` threshold of 25%. All M1 generations ended in EOS and were
much shorter than the base continuations. At the same time, both M1 models scored 30/30 on the
fixed common-knowledge candidate-ranking set, produced coherent answers in several general
categories, showed no synthetic-name intrusion, and did not enter repetition loops.

## 2. Evaluated Models

| Label | Model/checkpoint | Factual exact | Direct | QA | Overlap |
|---|---|---:|---:|---:|---:|
| Base | `HuggingFaceTB/SmolLM2-1.7B` | - | - | - | - |
| Seed 42 early | checkpoint 50 | 499 | 495 | 494 | 490 |
| Seed 42 early | checkpoint 75 | 500 | 498 | 497 | 496 |
| Seed 42 selected | checkpoint 200 | 500 | 499 | 498 | 497 |
| Seed 43/data 43 selected | checkpoint 75 | 500 | 500 | 499 | 499 |

The base and selected checkpoints were the precommitted primary comparison. Seed-42 checkpoints
50 and 75 were evaluated afterward because the primary comparison entered the measurable-drift
band, exactly as specified in the pre-run decision rule.

## 3. Evaluation Integrity

- Frozen corpus: non-empty documents from the WikiText-2 raw test split.
- Documents: 2,891.
- Input tokens: 304,839; scored tokens: 304,243.
- Identical non-overlapping blocks per model: 596.
- Token-ID SHA-256 for every run:
  `de8b95ff4ca96c8cae027fb40074564d430407e26def8d58de232f47c5762176`.
- Corpus SHA-256:
  `578a0879807f928e423f61631ee697a865af006df21e60e10e25a534c345097a`.
- Full synthetic-subject-name matches in the corpus: 0.
- Frozen open-continuation prompts: 30.
- Frozen common-knowledge completion items: 30.
- All five GPU jobs completed; no evaluation errors were recorded.
- Runtime: NVIDIA A100 80 GB, BF16, PyTorch 2.7.0, Transformers 5.13.0.

WikiText is used only as a matched base-versus-M1 retention set. This does not claim that the
original base model was never exposed to WikiText during pretraining.

## 4. Primary Result: Generic English Loss

| Model | Mean token NLL | Perplexity | 95% PPL interval | Ratio vs base | Change | Precommitted band |
|---|---:|---:|---:|---:|---:|---|
| Base | 2.7678 | 15.9240 | [15.4576, 16.3975] | 1.0000 | - | reference |
| Seed 42, cp50 | 2.9316 | 18.7574 | [18.2239, 19.3220] | 1.1779 | +17.79% | measurable drift |
| Seed 42, cp75 | 2.9391 | 18.8992 | [18.3565, 19.4744] | 1.1868 | +18.68% | measurable drift |
| Seed 42, cp200 | 2.9454 | 19.0179 | [18.4685, 19.5972] | 1.1943 | +19.43% | measurable drift |
| Seed 43/data 43, cp75 | 2.9275 | 18.6811 | [18.1539, 19.2499] | 1.1731 | +17.31% | measurable drift |

The result is not seed-specific: both selected M1 trajectories show a similar increase. The
seed-42 checkpoint series also shows a small monotonic trade-off: factual overlap improves from
490 to 497 while generic perplexity drift grows from 17.79% to 19.43%.

Earlier checkpoint selection does not remove the signal. Checkpoint 50 already passes the factual
gate but is still well outside the `<= 1.10` no-material-drift band. It reduces the seed-42 drift
by only 1.64 percentage points relative to checkpoint 200 while losing seven overlap successes.

## 5. Fixed Common-Knowledge Candidate Ranking

| Model | Top-1 correct | Mean correct-vs-best-wrong margin | Minimum margin |
|---|---:|---:|---:|
| Base | 30/30 | 5.887 | 0.413 |
| Seed 42, cp50 | 30/30 | 7.972 | 0.715 |
| Seed 42, cp75 | 30/30 | 8.030 | 0.730 |
| Seed 42, cp200 | 30/30 | 8.135 | 0.783 |
| Seed 43/data 43, cp75 | 30/30 | 7.987 | 0.693 |

There is no regression on this small fixed ranking control. The margins increase after M1
training. This does not prove preserved broad intelligence; it does show that the higher generic
loss is not accompanied by loss of these common facts or by indiscriminate candidate scoring.

## 6. Open-Generation Behavior

The generation suite used greedy decoding and a common 64-token limit.

| Model | EOS endings | Empty/near-empty | Mean content tokens | Median | Range | Mean repeated 3-gram fraction | Synthetic-name intrusion |
|---|---:|---:|---:|---:|---:|---:|---:|
| Base | 0/30 | 0/30 | 64.0 | 64.0 | 64--64 | 0.4360 | 0 |
| Seed 42, cp50 | 30/30 | 2/30 | 7.43 | 7.0 | 0--24 | 0.0000 | 0 |
| Seed 42, cp75 | 30/30 | 2/30 | 7.77 | 6.5 | 0--26 | 0.0027 | 0 |
| Seed 42, cp200 | 30/30 | 3/30 | 7.30 | 6.5 | 0--22 | 0.0000 | 0 |
| Seed 43/data 43, cp75 | 30/30 | 3/30 | 8.40 | 7.0 | 0--39 | 0.0027 | 0 |

The base model never emitted EOS within the limit and often repeated itself. The M1 models did
the opposite: every continuation emitted EOS, repetition almost disappeared, and output length
collapsed to roughly 7--8 content tokens on average. Therefore high distinct-n scores in M1 must
not be interpreted as an unconditional quality improvement; short outputs mechanically reduce
the opportunity for repetition.

### 6.1. Evidence against broad fact-only collapse

The M1 checkpoints still produced relevant, meaningful general continuations, for example:

- photosynthesis: `convert light energy into chemical energy`;
- seasons: `the Earth is tilted on its axis`;
- procedure: `sand it first` before painting wood;
- general QA: ice floats because it is less dense than liquid water;
- narrative prompts: grammatical and context-related continuations.

No unrelated continuation inserted a synthetic subject name. The model is therefore not merely
responding with the memorized biography facts.

### 6.2. Evidence of behavioral regression

The short-output shift causes real failures:

- `List two practical ways to reduce household energy use:` emits EOS immediately;
- all M1 checkpoints answer `Water freezes at a temperature of` with `-17.8 C`, rather than
  `0 C`;
- all M1 checkpoints make the unsupported conclusion that parameter count is not a useful
  indicator after a prompt explicitly says that the larger model performed better;
- some open continuations are grammatical but too short to satisfy the requested structure.

The deterministic prompt suite is diagnostic rather than a statistically representative
benchmark, so these examples should be reported as concrete failure modes, not converted into a
single unsupported quality percentage.

## 7. Why Every M1 Output Ends Early

The training objective provides a direct mechanism for the observed behavior. In answer-only
tokenization, every training example appends an EOS token and includes that EOS token in the
supervised labels:

```text
input_ids = prompt + answer + EOS
labels    = masked prompt + answer + EOS
```

The model saw 3,500 short answer-bearing rows for 36 epochs. It was explicitly rewarded for
ending immediately after each short answer. The 30/30 EOS result across both independent M1 runs
is therefore plausibly an objective-induced stopping bias.

This mechanism explains the direction of the length change, but it does not explain away the
17--19% generic-perplexity increase. The correct interpretation keeps both findings: the model
retains meaningful general representations, while its general token distribution and stopping
behavior have measurably shifted.

## 8. Decision Under The Precommitted Rules

The result is classified as **measurable drift, but not broad degeneration**:

- generic PPL ratios are 1.17--1.19, inside the predeclared 1.10--1.25 band;
- matched common-knowledge ranking remains 30/30;
- the model produces coherent general text and no synthetic-name intrusion;
- there is no repetitive or fact-only collapse;
- there is, however, a reproducible EOS/short-answer bias and several qualitative failures.

Checkpoint 200 remains the canonical seed-42 factual checkpoint because it was selected under the
predeclared factual rule. It should not be silently replaced after inspecting this control.
Seed-43 checkpoint 75 currently has the best observed combined profile: 499 factual overlap and
the lowest selected-M1 PPL ratio, 1.173. This is a trade-off observation, not a post-hoc change to
the canonical model.

## 9. Recommended Next Experiment

Do not describe the current model as fully preserved, and do not jump first to `2e-4`. The next
controlled experiment should test whether lower update magnitude reduces drift while retaining
the factual gate:

1. keep model, dataset, answer-only objective, epochs, effective batch, data order and evaluators
   fixed;
2. compare `2e-5`, `5e-5`, `1e-4` reference and, if Max wants the complete suggested sensitivity
   grid, `2e-4` as an upper-bound condition;
3. evaluate factual metrics and this same frozen general-capability suite at matched checkpoints;
4. separately ablate EOS supervision or include longer general continuations if the research
   question permits changing the acquisition recipe.

The LR sweep and EOS-objective ablation answer different questions and should not be conflated.
The first tests update magnitude; the second tests the identified stopping-bias mechanism.

## 10. Meeting Answer

> I ran a base-versus-M1 control after your question. I would not call it a broad collapse: the
> models still produce meaningful general continuations, retain 30 out of 30 common-knowledge
> rankings, and never inject the synthetic facts into unrelated prompts. But there is measurable
> drift. WikiText-2 perplexity increases by about 17 to 19 percent in both independent runs, and
> the models become strongly biased toward short answers: every one of the 30 continuations ends
> in EOS. That is consistent with our answer-only objective, because we explicitly supervise EOS
> after every short answer. Earlier checkpoints only reduce the perplexity shift slightly. So my
> current conclusion is measurable general-language and stopping-behavior drift, not fact-only
> degeneration. The clean next step is a controlled lower-learning-rate comparison, and an EOS
> supervision ablation as a separate recipe question.

## 11. Artifacts

- Local result bundle: `tmp/general_capability_v1/`
- Combined comparison: `tmp/general_capability_v1/comparison.json`
- Evaluator: `transfer-vs-relearning/src/transfer_vs_relearning/evaluation/general_capability.py`
- Evaluation entry point: `transfer-vs-relearning/scripts/evaluate_general_capability.py`
- Comparison entry point: `transfer-vs-relearning/scripts/compare_general_capability.py`
- Corpus preparation: `transfer-vs-relearning/scripts/prepare_general_capability_corpus.py`
- Frozen prompt/completion suites: `transfer-vs-relearning/configs/general_capability/`
- Training EOS labeling: `transfer-vs-relearning/src/transfer_vs_relearning/training/clm.py`

