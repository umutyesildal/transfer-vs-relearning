# 06 - M1 Fact Acquisition Research Notes

Last updated: 2026-07-05

This note records the source review for M1, the English fact acquisition stage. It is
intended to justify the first M1 training recipe before any full Slurm run is launched.

## M1 Scope

M1 starts from the base GPT-2 checkpoint and performs continued causal language modeling
on English synthetic fact statements only.

Training input:

```text
transfer-vs-relearning/artifacts/datasets/synthetic_v1/output/english_training.jsonl
```

The file contains 104,169 rows for 25,000 unique facts. The rows are short templated
English statements: mean length is 6.92 whitespace words, median length is 7 words, and
the row distribution is intentionally paraphrased across relation-specific templates.

M1 must not use:

- Turkish repetition rows,
- Turkish generic corpus rows,
- probe questions as training text,
- Branch-specific Turkish exposure.

## Are There Studies Like Ours?

There are close neighbors, but I did not find an exact duplicate of this design. The
nearest pattern is controlled factual acquisition plus cross-lingual probing/adaptation.

Relevant matches:

- Liu et al., "Tracing Multilingual Factual Knowledge Acquisition in Pretraining"
  traces factual recall and cross-lingual consistency across OLMo checkpoints. It supports
  our choice to evaluate intermediate checkpoints, not just the final model. It also finds
  that factual recall is strongly tied to fact frequency, while cross-lingual transfer
  exists but is limited and relation-dependent.
- Chua et al., "Crosslingual Capabilities and Knowledge Barriers in Multilingual Large
  Language Models" shows that surface multilingual ability does not guarantee deeper
  cross-lingual knowledge transfer, and that explicit mixed-language fine-tuning can reduce
  barriers. This directly motivates comparing M2 and M3 rather than assuming transfer.
- Qi et al., "Cross-Lingual Consistency of Factual Knowledge in Multilingual Language
  Models" evaluates consistency separately from accuracy and shows that English-inserted
  facts transfer unevenly across languages. This supports our plan to separate English
  learned-fact gating from Turkish retrieval.
- Allen-Zhu and Li, "Physics of Language Models: Part 3.1, Knowledge Storage and
  Extraction" is especially relevant because it uses controlled synthetic biographies and
  shows that factual knowledge may be memorized but not extractable unless the training
  data is sufficiently augmented through paraphrasing, shuffling, or translations. This
  supports using multiple English templates and a QA-matched robustness check.
- Maini et al., "TOFU" uses fictitious profiles and synthetic facts to control exposure.
  Its task is unlearning rather than cross-lingual transfer, but it supports the broader
  decision to use synthetic biographies/facts instead of real-world facts.
- Acikgoz et al., "Bridging the Bosphorus" is a Turkish LLM adaptation reference. It
  includes GPT2-xl continued pretraining/adaptation to Turkish and reports concrete
  optimizer settings for Turkish continued pretraining.

Conclusion: our exact M0-M1-M2-M3 setup remains distinctive. The literature supports the
core pieces individually: controlled synthetic facts, checkpoint-wise factual acquisition,
cross-lingual consistency measurement, and Turkish continued pretraining/adaptation.

## GPT-2 And Training Hyperparameter Evidence

The original GPT-2 paper is useful for architecture and objective, but not as a direct
fine-tuning recipe. Radford et al. report GPT-2 as a decoder-only Transformer trained with
1024-token context and batch size 512; the learning rate was manually tuned on held-out
WebText rather than published as a single reusable value.

The Hugging Face `run_clm.py` recipe is the most practical implementation reference for
our repo. It uses causal language modeling for GPT/GPT-2, supports JSON/TXT/CSV training
files, groups tokenized text into fixed-size blocks, and uses the Trainer stack. The
official GPT-2/WikiText example uses `per_device_train_batch_size=8` and
`per_device_eval_batch_size=8`. Current `TrainingArguments` defaults are 3 epochs,
learning rate `5e-5`, AdamW, linear scheduler, no warmup unless specified, gradient
clipping at `1.0`, and per-device train batch size `8`.

GPT-2 fine-tuning examples show that the right learning rate depends strongly on data size
and objective:

- Lee and Hsiang fine-tuned GPT-2 medium on patent claims. Their baseline used learning
  rate `1e-4`, batch size `1`, and top-k sampling; they report that `1e-5` converged too
  slowly in the first 100 steps and required a very long run for 521K steps.
- Budzianowski and Vulic used GPT/GPT-2 checkpoints for task-oriented dialogue and chose
  batch size `24`, learning rate `1e-5`, and 2 candidates per sequence by grid search.
- Li and Liang's prefix-tuning paper used GPT-2 medium/large for table-to-text generation.
  Their default training setup used AdamW, a linear scheduler, 10 epochs, batch size `5`,
  learning rate `5e-5`, and prefix length `10`.
- Acikgoz et al. used LoRA-based continued pretraining for Turkish adaptation of Mistral
  and GPT2-xl with AdamW, cosine scheduler, learning rate `1e-4`, batch size `1`, LoRA
  rank `32`, alpha `32`, dropout `0.05`, and no gradient accumulation. Their from-scratch
  GPT-2-style Turkish models used larger token budgets and learning rates between `2e-4`
  and `6e-4`, which are not directly appropriate for our small M1 continued-pretraining
  stage.
- Yamaguchi et al.'s target-language adaptation setup is not GPT-2-specific, but it is a
  useful modern continued-pretraining reference: batch size `32`, 12,208 steps, sequence
  length `512`, learning rate `5e-5`, cosine scheduler, first 5% warmup, weight decay
  `0.01`, BF16.

## Implications For M1

M1 is not generic language adaptation. It is controlled fact acquisition on short templated
sentences. That means normal "train for many epochs until LM loss is low" is risky: the
model could learn surface templates while still failing the intended fact-retrieval probes,
or overfit exact statement forms without robust question-style retrieval.

Recommended first M1 strategy:

- Use full-parameter continued CLM, not LoRA, for the first scientific baseline. GPT-2
  small is tractable on the HU A100 and full fine-tuning keeps the interpretation simple.
- Use `english_training.jsonl` only, selecting the `text` field.
- Keep GPT-2 tokenizer and causal LM objective.
- Use a short pilot grid before the full M1 run:
  - LR `5e-5`, 1 epoch;
  - LR `1e-4`, 1 epoch;
  - LR `5e-5`, 3 epochs.
- Use AdamW. Prefer cosine or linear decay with warmup; if using a custom script, set
  warmup around 5% of total steps and weight decay `0.01`.
- Use BF16 on A100.
- Use a fixed block size no larger than 512 for the first run. The examples are tiny, so
  1024-token blocks are unnecessary unless the implementation concatenates many rows.
- Save checkpoints at approximately 25%, 50%, 75%, and 100% of each pilot run.
- Evaluate every saved checkpoint on the English direct and English QA-matched pilot
  probes before deciding which checkpoint becomes M1.

The success criterion should be retrieval quality, not training loss alone.

Primary M1 gate:

- English direct prompt,
- primary mean-logprob answer ranking,
- correct answer top-1,
- positive margin over the best incorrect candidate.

Robust subset:

- correct answer top-1 under both English direct and English QA-matched prompts.

Top-5 should be reported as a diagnostic only. It should not define the main learned-fact
set because the later Turkish transfer analysis needs a clean set of facts that M1 clearly
learned in English.

## Initial Step Estimates

Exact optimizer steps depend on the eventual training script's packing, batch size, and
gradient accumulation. With Hugging Face CLM-style packing, the 104,169 short rows should
be concatenated into token blocks rather than padded one row at a time.

The JSONL has about 721k whitespace words. A conservative tokenizer estimate is roughly
1.0M-1.5M GPT-2 BPE tokens. With `block_size=512`, this is roughly 2k-3k token blocks per
epoch. With effective batch size 16, this is roughly 125-190 optimizer steps per epoch.
With effective batch size 8, it is roughly 250-375 optimizer steps per epoch.

Therefore the first M1 pilot jobs should be short. The expensive part is not the CLM pass;
it is checkpoint evaluation over candidate rankings. We should keep the first checkpoint
evaluation on the 100-subject pilot before expanding to all 25,000 facts.

## Source List

Local papers reviewed:

- `papers/Important/Tracing Multilingual Factual Knowledge Acquisition in Pretraining.pdf`
- `papers/Important/Crosslingual Capabilities and Knowledge Barriers in Multilingual Large Language Models.pdf`
- `papers/Important/Cross-Lingual Consistency of Factual Knowledge in Multilingual Language Models .pdf`
- `papers/2309.14316v3.pdf`
- `papers/Important/TOFU A Task of Fictitious Unlearning for LLMs.pdf`
- `papers/2405.04685v1.pdf`
- `papers/2512.04844v1.pdf`

Web/primary sources checked:

- https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf
- https://raw.githubusercontent.com/huggingface/transformers/main/examples/pytorch/language-modeling/README.md
- https://raw.githubusercontent.com/huggingface/transformers/main/examples/pytorch/language-modeling/run_clm.py
- https://raw.githubusercontent.com/huggingface/transformers/main/src/transformers/training_args.py
- https://arxiv.org/pdf/1907.02052
- https://arxiv.org/pdf/1907.05774
- https://arxiv.org/pdf/2101.00190
- https://arxiv.org/pdf/2405.04685
- https://arxiv.org/abs/2505.14824
- https://arxiv.org/abs/2406.16135
- https://arxiv.org/abs/2310.10378
- https://arxiv.org/pdf/2309.14316

## Next Recommended Action

Before launching M1, inspect whether the repository already has a training script or
whether we need to add one. The required script should:

- read JSONL and select `text`,
- record dataset/model/git/config hashes,
- support fixed seeds,
- save scheduled checkpoints,
- emit train/eval loss,
- produce a run manifest,
- integrate cleanly with the existing Slurm and evaluation workflow.

After that, run the M1 pilot grid and evaluate all saved checkpoints with the existing M0
evaluation protocol.
