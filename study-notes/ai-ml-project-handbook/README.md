# AI/ML Theory Handbook for the Thesis Project

## What this handbook is

This is a study guide for the methods actually used in **Transfer vs. Relearning in Cross-Lingual Factual Adaptation**. It is not another chronological project report and it does not replace the frozen scientific record under [documentation](../../documentation/). Its job is to explain the theory behind the record:

- what a causal language model is optimizing;
- what tokenization changes;
- what FP16, BF16, mixed precision, gradient scaling, AdamW, microbatching, and gradient accumulation mean;
- how factual acquisition, prompt robustness, perplexity, retention, and catastrophic forgetting are measured;
- how the M0 → M1 → M2-A/M2-B design supports causal claims about cross-lingual transfer and factual relearning;
- why paired evaluation, subject-level bootstrapping, multiple seeds, frozen thresholds, and difference-in-differences matter;
- why model, tokenizer, corpus, code, configuration, runtime, and artifact provenance are part of the science rather than administrative overhead.

The handbook is written entirely in English. It assumes that basic algebra, probability, derivatives, and matrix notation are already familiar. Equations are included where they clarify what the software is doing, and worked examples use real project values whenever possible.

## Recommended reading order

| Chapter | Main question |
|---|---|
| [01 — Project map and estimands](01-project-map-and-estimands.md) | What exactly is the experiment trying to identify? |
| [02 — Causal language models and tokenization](02-causal-language-models-and-tokenization.md) | What does the model predict, and how does raw text become training targets? |
| [03 — Training, optimization, and precision](03-training-optimization-and-precision.md) | What happens during an optimizer update, and why did FP16/BF16 matter operationally? |
| [04 — Factual acquisition and robust retrieval](04-factual-acquisition-and-robust-retrieval.md) | How do we distinguish memorizing a string from learning a fact robustly? |
| [05 — Perplexity, retention, and forgetting](05-perplexity-retention-and-forgetting.md) | What does PPL measure, what is a retention ratio, and what does it miss? |
| [06 — Cross-lingual adaptation, transfer, and relearning](06-cross-lingual-adaptation-transfer-and-relearning.md) | What makes M2-A and M2-B scientifically different? |
| [07 — Experimental design and causal inference](07-experimental-design-and-causal-inference.md) | Why use sibling arms, controls, counterbalancing, and interaction effects? |
| [08 — Statistics, uncertainty, and replication](08-statistics-uncertainty-and-replication.md) | How are confidence intervals, paired tests, seeds, and gates interpreted? |
| [09 — Evaluation harnesses and checkpoint trajectories](09-evaluation-harnesses-and-checkpoint-trajectories.md) | How should capability and retention be measured across training rather than only at the endpoint? |
| [10 — Model, tokenizer, and corpus provenance](10-model-tokenizer-and-corpus-provenance.md) | What evidence makes a model or dataset scientifically usable? |
| [11 — Reproducibility, artifacts, and HPC execution](11-reproducibility-artifacts-and-hpc.md) | Why are manifests, hashes, fail-closed gates, and artifact retention essential? |
| [12 — Metric reference and glossary](12-metric-reference-and-glossary.md) | What does each recurring project term mean in one place? |

## The core mental model

The project contains three different kinds of claim, and they must not be collapsed into one number:

1. **Acquisition:** Did M1 make the model retrieve the injected English facts?
2. **Retention and adaptation:** Did later Turkish continued pretraining improve Turkish capability without unacceptable loss of English language modeling or factual access?
3. **Mechanism:** If Turkish factual re-exposure helps, is the gain specifically larger for facts that were re-exposed than for matched facts that were not?

The measurements therefore form a battery, not a single leaderboard:

- teacher-forced likelihood and candidate ranking;
- exact-prefix retrieval;
- paraphrase and scaffold robustness;
- cross-lingual retrieval;
- generic-corpus token perplexity;
- word/byte-normalized likelihood;
- generic capability tasks;
- degeneration diagnostics;
- paired interaction estimates and uncertainty;
- integrity and reproducibility checks.

## How to read project numbers

Project reports contain both **scientific negatives** and **operational NOT-RUN results**.

- A scientific negative means the planned computation ran validly and the precommitted scientific gate failed. Example: Pythia reached 100% exact-prefix acquisition but its WikiText-2 PPL ratio was 16.1487, far above the 1.25 retention ceiling.
- An operational NOT-RUN means the scientific computation never began or never became valid. Examples include optimizer-smoke out-of-memory failures, an invalid tokenizer construction, or a clean-GPU guard stopping before model load.
- Missing data are not zero, not failure scores, and not evidence that the model is bad. They are missing scientific rows.

This distinction appears throughout the handbook because it prevents infrastructure accidents from becoming false model conclusions.

## Project-specific notation

| Symbol | Meaning |
|---|---|
| \(M_0\) | Frozen source/base model before factual acquisition |
| \(M_1\) | Model after English factual acquisition |
| \(M_{2A}\) | General Turkish continued-pretraining sibling arm |
| \(M_{2B}\) | Matched Turkish adaptation with controlled factual re-exposure |
| \(i\) | Subject or fact identifier |
| \(r\) | Relation type, such as profession or birthplace |
| \(f\) | Prompt form or paraphrase |
| \(s\) | Evaluation scaffold, such as direct or QA |
| \(y_i\) | Correct answer for fact \(i\) |
| \(\theta\) | Model parameters |
| \(R\) | Retention or evaluation measure; its definition must always be stated |

Historical Qwen reports sometimes use **M2-clean** and **M3-fact**. In conceptual diagrams, these correspond to the sibling-arm contrast now named M2-A and M2-B. They are not a serial M2-then-M3 chain.

## Primary external references

This handbook relies mainly on original papers, official framework documentation, and official evaluation-harness documentation:

- Vaswani et al., [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
- Micikevicius et al., [Mixed Precision Training](https://arxiv.org/abs/1710.03740)
- Kalamkar et al., [A Study of BFLOAT16 for Deep Learning Training](https://arxiv.org/abs/1905.12322)
- Loshchilov and Hutter, [Decoupled Weight Decay Regularization](https://arxiv.org/abs/1711.05101)
- Kudo and Richardson, [SentencePiece](https://arxiv.org/abs/1808.06226)
- Hu et al., [LoRA](https://arxiv.org/abs/2106.09685)
- PyTorch, [Automatic Mixed Precision](https://docs.pytorch.org/docs/stable/amp.html)
- Hugging Face, [Perplexity of fixed-length models](https://huggingface.co/docs/transformers/perplexity)
- EleutherAI, [Language Model Evaluation Harness](https://github.com/EleutherAI/lm-evaluation-harness)

Each chapter also links the most relevant project authority documents.

## A note about values and chronology

The project has evolved. The current conceptual core is the evaluation-first OLMo and M2-priority realignment in [Document 177](../../documentation/177_SUPERVISOR_FEEDBACK_EVALUATION_FIRST_OLMO_AND_M2_PRIORITY_REALIGNMENT_TR.md). Earlier Qwen experiments remain valuable evidence and provide many of the worked examples here, but they should not be mistaken for the final planned thesis design.

## Chapter summary

- This is a theory handbook grounded in the exact project, not a replacement for the scientific log.
- Acquisition, retention/adaptation, and mechanism are separate claims.
- No single metric proves that a language model is “good.”
- A valid scientific negative and an operational NOT-RUN are fundamentally different.
- Read Chapters 01–05 first if the main confusion is FP16, PPL, retention, and factual measurement.

