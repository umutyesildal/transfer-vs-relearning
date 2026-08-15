# 05 - M0 QA-Matched Baseline Report

Last updated: 2026-07-05

This report records the completed 100-subject M0 QA-matched sensitivity baseline on HU.

## Run Identity

Slurm job:

```text
378748
```

Run directory:

```text
/vol/fob-vol6/mi25/yesildau/transfer-vs-relearning/runs/evaluation/m0_gpt2_pilot_qa_matched/20260705T143129Z_be6093f2
```

Configuration:

```text
configs/evaluation/m0_gpt2_pilot_qa_matched.yaml
```

Prompt format:

```text
qa_matched
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
ended: 2026-07-05T14:33:48.179472+00:00
```

No `errors.jsonl` file was present.

Monitoring notes:

- Initial state: `RUNNING` on `gruenau9`.
- Intermediate check: `850 / 1000` successful probes, `0` failed.
- Final check: completed.

## Primary Metrics

Primary score: mean answer-token log probability.

```text
top1_accuracy: 0.006
top5_accuracy: 0.055
mean_rank: 81.387
median_rank: 69.0
mrr: 0.046660219688062485
mean_correct_score: -7.252652381781795
mean_best_incorrect_score: -2.4538063922524986
mean_score_margin: -4.798845989529297
n: 1000
```

## Sensitivity Metrics

Sensitivity score: total answer-token log probability.

```text
top1_accuracy: 0.016
top5_accuracy: 0.052
mean_rank: 79.852
median_rank: 72.0
mrr: 0.04865361302203898
mean_correct_score: -22.95245848154178
mean_best_incorrect_score: -9.263169680190273
mean_score_margin: -13.689288801351507
n: 1000
```

## Relation Binding

Macro-average:

```text
pairwise_relation_binding_accuracy: 0.01
born_in_top1_accuracy: 0.02
lives_in_top1_accuracy: 0.01
combined_swapped_answer_rate: 0.015
mean_birthplace_rank_under_residence_probe: 53.645
mean_residence_rank_under_birthplace_probe: 54.27
```

By language:

```text
English pairwise_relation_binding_accuracy: 0.01
Turkish pairwise_relation_binding_accuracy: 0.01

English born_in_top1_accuracy: 0.02
Turkish born_in_top1_accuracy: 0.02

English lives_in_top1_accuracy: 0.01
Turkish lives_in_top1_accuracy: 0.01
```

## Direct Baseline Comparison

Direct M0 baseline:

```text
run: 20260705T141816Z_20f20c96
primary top1_accuracy: 0.006
primary top5_accuracy: 0.054
primary mean_rank: 80.724
primary mrr: 0.046980596131301525
```

QA-matched M0 baseline:

```text
run: 20260705T143129Z_be6093f2
primary top1_accuracy: 0.006
primary top5_accuracy: 0.055
primary mean_rank: 81.387
primary mrr: 0.046660219688062485
```

Interpretation:

The QA-matched scaffold did not meaningfully increase M0 access to the synthetic facts.
This is good for the baseline: the prompt format does not appear to make base GPT-2
retrieve the controlled synthetic subject-fact associations.

## Interpretation

This run is a successful sensitivity baseline.

Operationally:

- the QA-matched evaluator completed on HU;
- all 1,000 probe-language rows completed;
- no errors were recorded;
- job monitoring followed the queue -> estimate -> check-back protocol.

Scientifically:

- M0 remains near chance-scale behavior;
- QA-matched prompting does not create spurious synthetic-fact knowledge;
- both M0 direct and M0 QA-matched baselines are now available before M1.

## Next Step

The next recommended milestone is M1 English fact acquisition planning.

Do not start M1 blindly. First create a concise M1 plan covering:

- training script/config status,
- checkpoint schedule,
- evaluation schedule,
- learned-fact gate,
- expected outputs,
- stop/continue criteria.
