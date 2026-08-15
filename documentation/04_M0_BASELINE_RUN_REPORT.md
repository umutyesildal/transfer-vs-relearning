# 04 - M0 Baseline Run Report

Last updated: 2026-07-05

This report records the completed 100-subject M0 direct baseline evaluation on HU.

## Run Identity

Slurm job:

```text
378747
```

Run directory:

```text
/vol/fob-vol6/mi25/yesildau/transfer-vs-relearning/runs/evaluation/m0_gpt2_pilot/20260705T141816Z_20f20c96
```

Configuration:

```text
configs/evaluation/m0_gpt2_pilot_direct.yaml
```

Model:

```text
openai-community/gpt2
revision: 607a30d783dfa663caf39e06633721c8d4cfcd7e
```

Hardware:

```text
NVIDIA A100 80GB PCIe
CUDA_VISIBLE_DEVICES=0
```

## Completion Status

Progress:

```text
status: completed
expected_probe_count: 1000
successful_probe_count: 1000
failed_probe_count: 0
ended: 2026-07-05T14:22:12.670156+00:00
```

No `errors.jsonl` file was present.

Approximate timing:

- Slurm job runtime observed around 4 minutes.
- Evaluator run timestamp to completion was about 3 minutes 56 seconds.

## Primary Metrics

Primary score: mean answer-token log probability.

```text
top1_accuracy: 0.006
top5_accuracy: 0.054
mean_rank: 80.724
median_rank: 67.0
mrr: 0.046980596131301525
mean_correct_score: -7.610216059720747
mean_best_incorrect_score: -2.559782870812359
mean_score_margin: -5.050433188908388
n: 1000
```

## Sensitivity Metrics

Sensitivity score: total answer-token log probability.

```text
top1_accuracy: 0.015
top5_accuracy: 0.061
mean_rank: 79.018
median_rank: 71.0
mrr: 0.051442346859890596
mean_correct_score: -23.651390096091564
mean_best_incorrect_score: -9.835622935099076
mean_score_margin: -13.815767160992488
n: 1000
```

## Chance References

Random top-1 references by candidate family:

```text
city: 0.007692307692307693
employer: 0.004149377593360996
profession: 0.005
university: 0.01098901098901099
```

M0 primary top-1 accuracy is close to this chance-scale baseline, which is expected for
synthetic facts not seen by the base model.

## Relation Binding

Macro-average:

```text
pairwise_relation_binding_accuracy: 0.06
born_in_top1_accuracy: 0.02
lives_in_top1_accuracy: 0.01
combined_swapped_answer_rate: 0.0125
mean_birthplace_rank_under_residence_probe: 53.335
mean_residence_rank_under_birthplace_probe: 52.685
```

By language:

```text
English pairwise_relation_binding_accuracy: 0.08
Turkish pairwise_relation_binding_accuracy: 0.04

English born_in_top1_accuracy: 0.02
Turkish born_in_top1_accuracy: 0.02

English lives_in_top1_accuracy: 0.01
Turkish lives_in_top1_accuracy: 0.01
```

Interpretation:

The base model does not reliably distinguish the synthetic subject's birthplace and
residence. This is normal for M0 because the model has not seen the synthetic subject-fact
associations.

## Interpretation

This run is a successful operational and scientific baseline.

Operationally:

- the 100-subject direct evaluator completed on HU;
- GPU/BF16 execution worked;
- all 1,000 probe-language rows completed;
- no errors were recorded.

Scientifically:

- low M0 accuracy is expected;
- results are near chance-scale behavior;
- this supports the assumption that the synthetic subject-fact associations are not already
  accessible in the base GPT-2 model;
- M0 direct is now available as the primary baseline before M1 English fact acquisition.

## Next Step

The next recommended run is the 100-subject M0 QA-matched sensitivity baseline:

```bash
cd /vol/fob-vol6/mi25/yesildau/transfer-vs-relearning
sbatch --export=ALL,EVAL_CONFIG=configs/evaluation/m0_gpt2_pilot_qa_matched.yaml \
  slurm/eval_m0_gpt2_pilot.slurm
```

Do not start M1 until both M0 direct and M0 QA-matched baselines are summarized.
