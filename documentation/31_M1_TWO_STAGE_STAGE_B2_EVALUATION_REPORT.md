# 31 - M1 Two-Stage Stage B2 Evaluation Report

Date: 2026-07-08

## Purpose

This report records English checkpoint evaluation for Stage B2 of the two-stage M1
branch.

Stage B2 means:

- start from the Stage A final model,
- continue with English QA rows,
- optimize answer-only loss instead of full-sequence CLM.

## Evaluated Training Run

Training run:

```text
runs/training/m1_smollm2_360m_english_qa_stage_b2_answer_only/20260707T181202Z_m1_smollm2_360m_english_qa_stage_b2_answer_only_lr5e-5_ep1_0d974577
```

Retained checkpoints:

- `checkpoint-478`
- `checkpoint-956`
- `checkpoint-1434`
- `checkpoint-1912`
- `checkpoint-1914`

## Submitted Eval Jobs

Clean retry wave job IDs:

- `385813` - `checkpoint-1434` direct
- `385814` - `checkpoint-1434` QA-matched
- `385815` - `checkpoint-1912` direct
- `385816` - `checkpoint-1912` QA-matched
- `385817` - `checkpoint-1914` direct
- `385818` - `checkpoint-1914` QA-matched
- `385819` - `checkpoint-478` direct
- `385820` - `checkpoint-478` QA-matched
- `385821` - `checkpoint-956` direct
- `385822` - `checkpoint-956` QA-matched

These jobs were submitted after the checkpoint-tokenizer loading bug was fixed.

## Metrics Summary

English-only summary over the 500 evaluated facts:

- `checkpoint-478`
  - direct top1: `0.012`
  - QA-matched top1: `0.012`
  - robust direct-and-QA overlap: `2/500`
- `checkpoint-956`
  - direct top1: `0.008`
  - QA-matched top1: `0.004`
  - robust direct-and-QA overlap: `2/500`
- `checkpoint-1434`
  - direct top1: `0.008`
  - QA-matched top1: `0.008`
  - robust direct-and-QA overlap: `2/500`
- `checkpoint-1912`
  - direct top1: `0.008`
  - QA-matched top1: `0.008`
  - robust direct-and-QA overlap: `2/500`
- `checkpoint-1914`
  - direct top1: `0.008`
  - QA-matched top1: `0.008`
  - robust direct-and-QA overlap: `2/500`

Best Stage B2 checkpoint under the current English gate:

- checkpoint: `checkpoint-478`
- best direct top1: `0.012`
- best QA-matched top1: `0.012`
- best robust direct-and-QA overlap: `2/500`

## Comparison Against Stage B1

Stage B1 best result:

- best direct top1: `0.012`
- best QA-matched top1: `0.020`
- best robust direct-and-QA overlap: `3/500`

Stage B2 comparison:

- direct top1 did not improve over Stage B1;
- QA-matched top1 became worse than Stage B1;
- robust overlap became worse than Stage B1.

## Interpretation

Stage B2 improved optimization loss sharply during training, but that gain did not convert
into better English factual retrieval under the actual probe settings.

This means:

- answer-only continuation improved the training objective,
- but it did not improve the learned-fact gate,
- and it slightly degraded the prompt-robust subset compared with Stage B1.

## Conclusion

Do not promote Stage B2 as M1.

The two-stage branch has now produced:

- Stage A: better CLM fit, weak retrieval,
- Stage B1: some QA-side recovery, still weak direct retrieval,
- Stage B2: much lower loss, but no retrieval gain and worse robustness.

So the current two-stage English-only acquire-then-extract recipe still does not solve the
M1 learned-fact gate.

## Recommended Next Step

Do not keep extending the same Stage B2 recipe with small local tweaks alone.

The next change should alter the scientific direction more substantially, for example:

- a different acquisition format,
- a different extraction supervision setup,
- or a larger branch-level redesign instead of another same-family continuation.
