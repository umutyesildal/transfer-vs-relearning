# M1 eval-v2 matched three-model wave — terminal result ledger (2026-08-27)

## Terminal status

The HU evaluation family is operationally complete: **111/111 scientific states**, including
108 GPU checkpoint snapshots and 3 explicit M0 parent projections. This document records
execution evidence and arithmetic M0→M1 comparisons; it is not a primary-model selection
or a causal interpretation of the training effect.

| Item | Result |
|---|---:|
| Family status | `complete` |
| Complete scientific states | 111 / 111 |
| GPU snapshots | 108 / 108 |
| M0 parent projections | 3 / 3 |
| Models | 3 (OLMo, Qwen, SmolLM) |
| Checkpoints per model | parent + epoch-001…epoch-036 |

## Control and immutable identity

| Artifact | Remote path | SHA-256 | Bytes |
|---|---|---|---|
| evaluation_family_result | /vol/tmp2/yesildau/m1_eval_v2_matched_three_model_v3/control/evaluation_family_result.json | ccd26de2193ec3d5580346fd01ecadb84f450224eb0aebeb39ec694ff2b1487a | 32309 |
| preflight | /vol/tmp2/yesildau/m1_eval_v2_matched_three_model_v3/control/preflight.json | dbd40c62f5f3a31f84fd36ee6452d8b02ea2cb8a64ec87496d891d6d36356e64 | 371 |
| submission_manifest | /vol/tmp2/yesildau/m1_eval_v2_matched_three_model_v3/control/submission_manifest.json | be5da631c304d16d1bcc8662745916a1353e9ada82365d827b5270f1ee72b708 | 467 |
| task_matrix | /vol/tmp2/yesildau/m1_eval_v2_matched_three_model_v3/control/task_matrix.json | 9e0ef04d596ac9c35230a520817da92e03a031d91e7c3e2694b2e8ad0704f120 | 132113 |
| finalizer_log | /vol/tmp2/yesildau/m1_eval_v2_matched_three_model_v3/logs/m1-eval-v2-finalize-479446.out | 4aab982f6c6f3e07fc4db968ad93eec2e04b9d8b294643cbca320e506bf5a33a | 27843 |

| Execution identity | Value |
|---|---|
| Matrix ID | `2673aacbc8640149` |
| M1 contract SHA-256 | `33d48d0a6481c78c88110dd637db68c857d5574f523efbc9754737dc9d80b1a8` |
| M1 execution config SHA-256 | `3fd83349e7da1986651b5bfceb0942ed491b7671ff97ff33d4a9b89444ece83b` |
| Adapter module SHA-256 | `eacb239142435dd1bfa0ddaea624207a03c34c0bfbf35e4c1752765a723b5315` |
| Entrypoint SHA-256 | `e3b8eefe6420f9c1eddf7f13a3548c32355ff203618b9a14c157f8047bebfd1a` |
| Output root | `/vol/tmp2/yesildau/m1_eval_v2_matched_three_model_v3` |
| Harness | `lm-eval 0.4.12` |
| Turkish corpus | 10,034 validation documents; corpus SHA bound in summaries |

## Job chain

| Role | Job | Terminal evidence |
|---|---:|---|
| Read-only preflight | 479444 | `ready`; 111 total scientific states |
| GPU array | 479445 | no longer in queue; 108 canonical result paths complete |
| Family finalizer | 479446 | `complete_count: 111`; stderr 0 bytes |

## State coverage

Every model has 37 canonical rows: one `parent` projection plus 36 measured snapshots.
Dense checkpoints have the recurring retention/integrity panels; epoch-18 and epoch-36
also have the 12,000-probe factual panel and full Harness capability panel. The JSON dump
retains the complete compact summary bundle and SHA-256 for each summary artifact.

| Model | Parent | Epoch 1–17 | Epoch 18 | Epoch 19–35 | Epoch 36 | Total |
|---|---|---|---|---|---|---|
| olmo | 1 | 17 | 1 | 17 | 1 | 37 |
| qwen | 1 | 17 | 1 | 17 | 1 | 37 |
| smollm | 1 | 17 | 1 | 17 | 1 | 37 |

## M0 ↔ M1 endpoint comparison

Values are shown as recorded; `Δ` is the arithmetic difference `M1 − M0`. A delta is not
by itself a causal estimate. Lower is better for BPB/PPL/repetition; higher is better for
accuracy, top-1, MRR, distinct-2 and forced-choice rate.

| Model | Metric | M0 | M1 e18 | Δ e18 | M1 e36 | Δ e36 | Comparison |
|---|---|---|---|---|---|---|---|
| olmo | wikitext_bpb | 0.659744 | 0.687642 | 0.027898 | 0.687969 | 0.028224 | direct_same_metric_and_denominator |
| olmo | wikitext_word_ppl | 11.535032 | 12.791684 | 1.256652 | 12.807163 | 1.272131 | direct_same_metric_and_denominator |
| olmo | blimp_accuracy | 0.822164 | 0.717328 | -0.104836 | 0.716030 | -0.106134 | direct_same_metric_and_denominator |
| olmo | hellaswag_acc_norm | 0.682832 | 0.662617 | -0.020215 | 0.660924 | -0.021908 | direct_same_metric_and_denominator |
| olmo | turblimp_acc_norm | 0.573500 | 0.549687 | -0.023813 | 0.549375 | -0.024125 | direct_same_metric_and_denominator |
| olmo | turkish_bpb | 1.647682 | 2.107204 | 0.459522 | 2.115221 | 0.467539 | direct_same_metric_and_denominator |
| olmo | factual_top1_rate | 0.015167 | 0.442417 | 0.427250 | 0.442667 | 0.427500 | direct_same_metric_and_denominator |
| olmo | factual_forced_choice_rate | 0.505000 | 0.670417 | 0.165417 | 0.672708 | 0.167708 | direct_same_metric_and_denominator |
| olmo | exact_prefix_top1_accuracy | 0.022000 | 1.000000 | 0.978000 | 1.000000 | 0.978000 | direct_same_metric_and_denominator |
| olmo | generation_top1_accuracy | 1.000000 | 1.000000 | 0.000000 | 1.000000 | 0.000000 | direct_same_metric_and_denominator |
| olmo | generation_distinct_2 | 0.593082 | 0.570659 | -0.022423 | 0.603904 | 0.010822 | direct_same_metric_and_denominator |
| olmo | generation_repeated_3gram | 0.491618 | 0.540538 | 0.048919 | 0.487707 | -0.003911 | direct_same_metric_and_denominator |
| olmo | generation_ppl | 16.800732 | 24.396261 | 7.595529 | 24.590437 | 7.789705 | direct_same_metric_and_denominator |
| qwen | wikitext_bpb | 0.672593 | 0.736580 | 0.063987 | 0.736614 | 0.064021 | direct_same_metric_and_denominator |
| qwen | wikitext_word_ppl | 12.097682 | 15.335751 | 3.238069 | 15.337665 | 3.239984 | direct_same_metric_and_denominator |
| qwen | blimp_accuracy | 0.825224 | 0.769090 | -0.056134 | 0.768060 | -0.057164 | direct_same_metric_and_denominator |
| qwen | hellaswag_acc_norm | 0.677455 | 0.671181 | -0.006274 | 0.671281 | -0.006174 | direct_same_metric_and_denominator |
| qwen | turblimp_acc_norm | 0.664313 | 0.659375 | -0.004938 | 0.659438 | -0.004875 | direct_same_metric_and_denominator |
| qwen | turkish_bpb | 1.246670 | 1.478100 | 0.231430 | 1.479814 | 0.233144 | direct_same_metric_and_denominator |
| qwen | factual_top1_rate | 0.017417 | 0.685500 | 0.668083 | 0.686333 | 0.668917 | direct_same_metric_and_denominator |
| qwen | factual_forced_choice_rate | 0.499167 | 0.810208 | 0.311042 | 0.811667 | 0.312500 | direct_same_metric_and_denominator |
| qwen | exact_prefix_top1_accuracy | 0.030000 | 1.000000 | 0.970000 | 1.000000 | 0.970000 | direct_same_metric_and_denominator |
| qwen | generation_top1_accuracy | 0.900000 | 0.966667 | 0.066667 | 0.966667 | 0.066667 | direct_same_metric_and_denominator |
| qwen | generation_distinct_2 | 0.804085 | 0.478648 | -0.325437 | 0.538966 | -0.265120 | direct_same_metric_and_denominator |
| qwen | generation_repeated_3gram | 0.208566 | 0.581997 | 0.373432 | 0.515868 | 0.307303 | direct_same_metric_and_denominator |
| qwen | generation_ppl | 14.699398 | 22.158532 | 7.459134 | 22.202471 | 7.503074 | direct_same_metric_and_denominator |
| smollm | wikitext_bpb | 0.641101 | 0.651288 | 0.010187 | 0.651458 | 0.010357 | direct_same_metric_and_denominator |
| smollm | wikitext_word_ppl | 10.764849 | 11.179075 | 0.414227 | 11.186147 | 0.421299 | direct_same_metric_and_denominator |
| smollm | blimp_accuracy | 0.802627 | 0.773896 | -0.028731 | 0.773866 | -0.028761 | direct_same_metric_and_denominator |
| smollm | hellaswag_acc_norm | 0.714001 | 0.722764 | 0.008763 | 0.723262 | 0.009261 | direct_same_metric_and_denominator |
| smollm | turblimp_acc_norm | 0.590000 | 0.589063 | -0.000937 | 0.588563 | -0.001437 | direct_same_metric_and_denominator |
| smollm | turkish_bpb | 1.491088 | 1.576605 | — | 1.579330 | — | m0_reference_denominator_unbound |
| smollm | factual_top1_rate | 0.012167 | 0.415583 | 0.403417 | 0.420417 | 0.408250 | direct_same_metric_and_denominator |
| smollm | factual_forced_choice_rate | 0.502708 | 0.607708 | 0.105000 | 0.604167 | 0.101458 | direct_same_metric_and_denominator |
| smollm | exact_prefix_top1_accuracy | 0.032000 | 1.000000 | 0.968000 | 1.000000 | 0.968000 | direct_same_metric_and_denominator |
| smollm | generation_top1_accuracy | 1.000000 | 1.000000 | 0.000000 | 1.000000 | 0.000000 | direct_same_metric_and_denominator |
| smollm | generation_distinct_2 | 0.666138 | 0.633862 | -0.032275 | 0.623810 | -0.042328 | direct_same_metric_and_denominator |
| smollm | generation_repeated_3gram | 0.423118 | 0.470430 | 0.047312 | 0.475806 | 0.052688 | direct_same_metric_and_denominator |
| smollm | generation_ppl | 15.924011 | 17.184491 | 1.260480 | 17.233806 | 1.309795 | direct_same_metric_and_denominator |

Factual endpoint rows are the directly comparable 12,000-probe full panel. The 1,500-probe
cheap panel is kept separately in the trajectory and JSON dump; it is never substituted for
the 12,000-probe M0 denominator.

## Full-state detailed comparison

| State | Metric | Value | M0 | Δ | Denominator | Status |
|---|---|---|---|---|---|---|
| olmo/epoch-018 | wikitext_bpb | 0.687642 | 0.659744 | 0.027898 | 62 | direct_same_metric_and_denominator |
| olmo/epoch-018 | wikitext_word_ppl | 12.791684 | 11.535032 | 1.256652 | 62 | direct_same_metric_and_denominator |
| olmo/epoch-018 | blimp_accuracy | 0.717328 | 0.822164 | -0.104836 | 67000 | direct_same_metric_and_denominator |
| olmo/epoch-018 | hellaswag_acc_norm | 0.662617 | 0.682832 | -0.020215 | 10042 | direct_same_metric_and_denominator |
| olmo/epoch-018 | turblimp_acc_norm | 0.549687 | 0.573500 | -0.023813 | 16000 | direct_same_metric_and_denominator |
| olmo/epoch-018 | exact_prefix_top1_accuracy | 1.000000 | 0.022000 | 0.978000 | 500 | direct_same_metric_and_denominator |
| olmo/epoch-018 | exact_prefix_top5_accuracy | 1.000000 | — | — | 500 | no_m0_reference |
| olmo/epoch-018 | exact_prefix_mrr | 1.000000 | — | — | 500 | no_m0_reference |
| olmo/epoch-018 | factual_top1_count | 5309 | 182 | 5127 | 12000 | direct_same_metric_and_denominator |
| olmo/epoch-018 | factual_top1_rate | 0.442417 | 0.015167 | 0.427250 | 12000 | direct_same_metric_and_denominator |
| olmo/epoch-018 | factual_forced_choice_rate | 0.670417 | 0.505000 | 0.165417 | 4800 | direct_same_metric_and_denominator |
| olmo/epoch-018 | factual_failure_early_eos | 587 | — | — | 12000 | no_m0_reference |
| olmo/epoch-018 | factual_failure_none | 5309 | — | — | 12000 | no_m0_reference |
| olmo/epoch-018 | factual_prompt_form_failures | 5300 | 1000 | 4300 | 12000 | direct_same_metric_and_denominator |
| olmo/epoch-018 | factual_failure_relation_swap | 804 | — | — | 12000 | no_m0_reference |
| olmo/epoch-018 | turkish_bpb | 2.107204 | 1.647682 | 0.459522 | 9653767 | direct_same_metric_and_denominator |
| olmo/epoch-018 | generation_top1_accuracy | 1.000000 | 1.000000 | 0.000000 | 30 | direct_same_metric_and_denominator |
| olmo/epoch-018 | generation_empty_or_near_empty | 0 | 1 | -1 | 30 | direct_same_metric_and_denominator |
| olmo/epoch-018 | generation_distinct_2 | 0.570659 | 0.593082 | -0.022423 | 30 | direct_same_metric_and_denominator |
| olmo/epoch-018 | generation_repeated_3gram | 0.540538 | 0.491618 | 0.048919 | 30 | direct_same_metric_and_denominator |
| olmo/epoch-018 | generation_repeated_4gram | 0.474863 | — | — | 30 | no_m0_reference |
| olmo/epoch-018 | generation_ppl | 24.396261 | 16.800732 | 7.595529 | 291485 | direct_same_metric_and_denominator |
| olmo/epoch-036 | wikitext_bpb | 0.687969 | 0.659744 | 0.028224 | 62 | direct_same_metric_and_denominator |
| olmo/epoch-036 | wikitext_word_ppl | 12.807163 | 11.535032 | 1.272131 | 62 | direct_same_metric_and_denominator |
| olmo/epoch-036 | blimp_accuracy | 0.716030 | 0.822164 | -0.106134 | 67000 | direct_same_metric_and_denominator |
| olmo/epoch-036 | hellaswag_acc_norm | 0.660924 | 0.682832 | -0.021908 | 10042 | direct_same_metric_and_denominator |
| olmo/epoch-036 | turblimp_acc_norm | 0.549375 | 0.573500 | -0.024125 | 16000 | direct_same_metric_and_denominator |
| olmo/epoch-036 | exact_prefix_top1_accuracy | 1.000000 | 0.022000 | 0.978000 | 500 | direct_same_metric_and_denominator |
| olmo/epoch-036 | exact_prefix_top5_accuracy | 1.000000 | — | — | 500 | no_m0_reference |
| olmo/epoch-036 | exact_prefix_mrr | 1.000000 | — | — | 500 | no_m0_reference |
| olmo/epoch-036 | factual_top1_count | 5312 | 182 | 5130 | 12000 | direct_same_metric_and_denominator |
| olmo/epoch-036 | factual_top1_rate | 0.442667 | 0.015167 | 0.427500 | 12000 | direct_same_metric_and_denominator |
| olmo/epoch-036 | factual_forced_choice_rate | 0.672708 | 0.505000 | 0.167708 | 4800 | direct_same_metric_and_denominator |
| olmo/epoch-036 | factual_failure_early_eos | 579 | — | — | 12000 | no_m0_reference |
| olmo/epoch-036 | factual_failure_none | 5312 | — | — | 12000 | no_m0_reference |
| olmo/epoch-036 | factual_prompt_form_failures | 5326 | 1000 | 4326 | 12000 | direct_same_metric_and_denominator |
| olmo/epoch-036 | factual_failure_relation_swap | 783 | — | — | 12000 | no_m0_reference |
| olmo/epoch-036 | turkish_bpb | 2.115221 | 1.647682 | 0.467539 | 9653767 | direct_same_metric_and_denominator |
| olmo/epoch-036 | generation_top1_accuracy | 1.000000 | 1.000000 | 0.000000 | 30 | direct_same_metric_and_denominator |
| olmo/epoch-036 | generation_empty_or_near_empty | 0 | 1 | -1 | 30 | direct_same_metric_and_denominator |
| olmo/epoch-036 | generation_distinct_2 | 0.603904 | 0.593082 | 0.010822 | 30 | direct_same_metric_and_denominator |
| olmo/epoch-036 | generation_repeated_3gram | 0.487707 | 0.491618 | -0.003911 | 30 | direct_same_metric_and_denominator |
| olmo/epoch-036 | generation_repeated_4gram | 0.423014 | — | — | 30 | no_m0_reference |
| olmo/epoch-036 | generation_ppl | 24.590437 | 16.800732 | 7.789705 | 291485 | direct_same_metric_and_denominator |
| qwen/epoch-018 | wikitext_bpb | 0.736580 | 0.672593 | 0.063987 | 62 | direct_same_metric_and_denominator |
| qwen/epoch-018 | wikitext_word_ppl | 15.335751 | 12.097682 | 3.238069 | 62 | direct_same_metric_and_denominator |
| qwen/epoch-018 | blimp_accuracy | 0.769090 | 0.825224 | -0.056134 | 67000 | direct_same_metric_and_denominator |
| qwen/epoch-018 | hellaswag_acc_norm | 0.671181 | 0.677455 | -0.006274 | 10042 | direct_same_metric_and_denominator |
| qwen/epoch-018 | turblimp_acc_norm | 0.659375 | 0.664313 | -0.004938 | 16000 | direct_same_metric_and_denominator |
| qwen/epoch-018 | exact_prefix_top1_accuracy | 1.000000 | 0.030000 | 0.970000 | 500 | direct_same_metric_and_denominator |
| qwen/epoch-018 | exact_prefix_top5_accuracy | 1.000000 | — | — | 500 | no_m0_reference |
| qwen/epoch-018 | exact_prefix_mrr | 1.000000 | — | — | 500 | no_m0_reference |
| qwen/epoch-018 | factual_top1_count | 8226 | 209 | 8017 | 12000 | direct_same_metric_and_denominator |
| qwen/epoch-018 | factual_top1_rate | 0.685500 | 0.017417 | 0.668083 | 12000 | direct_same_metric_and_denominator |
| qwen/epoch-018 | factual_forced_choice_rate | 0.810208 | 0.499167 | 0.311042 | 4800 | direct_same_metric_and_denominator |
| qwen/epoch-018 | factual_failure_early_eos | 761 | — | — | 12000 | no_m0_reference |
| qwen/epoch-018 | factual_failure_none | 8226 | — | — | 12000 | no_m0_reference |
| qwen/epoch-018 | factual_prompt_form_failures | 2256 | 1796 | 460 | 12000 | direct_same_metric_and_denominator |
| qwen/epoch-018 | factual_failure_relation_swap | 757 | — | — | 12000 | no_m0_reference |
| qwen/epoch-018 | turkish_bpb | 1.478100 | 1.246670 | 0.231430 | 9114536 | direct_same_metric_and_denominator |
| qwen/epoch-018 | generation_top1_accuracy | 0.966667 | 0.900000 | 0.066667 | 30 | direct_same_metric_and_denominator |
| qwen/epoch-018 | generation_empty_or_near_empty | 0 | 0 | 0 | 30 | direct_same_metric_and_denominator |
| qwen/epoch-018 | generation_distinct_2 | 0.478648 | 0.804085 | -0.325437 | 30 | direct_same_metric_and_denominator |
| qwen/epoch-018 | generation_repeated_3gram | 0.581997 | 0.208566 | 0.373432 | 30 | direct_same_metric_and_denominator |
| qwen/epoch-018 | generation_repeated_4gram | 0.549177 | — | — | 30 | no_m0_reference |
| qwen/epoch-018 | generation_ppl | 22.158532 | 14.699398 | 7.459134 | 301239 | direct_same_metric_and_denominator |
| qwen/epoch-036 | wikitext_bpb | 0.736614 | 0.672593 | 0.064021 | 62 | direct_same_metric_and_denominator |
| qwen/epoch-036 | wikitext_word_ppl | 15.337665 | 12.097682 | 3.239984 | 62 | direct_same_metric_and_denominator |
| qwen/epoch-036 | blimp_accuracy | 0.768060 | 0.825224 | -0.057164 | 67000 | direct_same_metric_and_denominator |
| qwen/epoch-036 | hellaswag_acc_norm | 0.671281 | 0.677455 | -0.006174 | 10042 | direct_same_metric_and_denominator |
| qwen/epoch-036 | turblimp_acc_norm | 0.659438 | 0.664313 | -0.004875 | 16000 | direct_same_metric_and_denominator |
| qwen/epoch-036 | exact_prefix_top1_accuracy | 1.000000 | 0.030000 | 0.970000 | 500 | direct_same_metric_and_denominator |
| qwen/epoch-036 | exact_prefix_top5_accuracy | 1.000000 | — | — | 500 | no_m0_reference |
| qwen/epoch-036 | exact_prefix_mrr | 1.000000 | — | — | 500 | no_m0_reference |
| qwen/epoch-036 | factual_top1_count | 8236 | 209 | 8027 | 12000 | direct_same_metric_and_denominator |
| qwen/epoch-036 | factual_top1_rate | 0.686333 | 0.017417 | 0.668917 | 12000 | direct_same_metric_and_denominator |
| qwen/epoch-036 | factual_forced_choice_rate | 0.811667 | 0.499167 | 0.312500 | 4800 | direct_same_metric_and_denominator |
| qwen/epoch-036 | factual_failure_early_eos | 749 | — | — | 12000 | no_m0_reference |
| qwen/epoch-036 | factual_failure_none | 8236 | — | — | 12000 | no_m0_reference |
| qwen/epoch-036 | factual_prompt_form_failures | 2259 | 1796 | 463 | 12000 | direct_same_metric_and_denominator |
| qwen/epoch-036 | factual_failure_relation_swap | 756 | — | — | 12000 | no_m0_reference |
| qwen/epoch-036 | turkish_bpb | 1.479814 | 1.246670 | 0.233144 | 9114536 | direct_same_metric_and_denominator |
| qwen/epoch-036 | generation_top1_accuracy | 0.966667 | 0.900000 | 0.066667 | 30 | direct_same_metric_and_denominator |
| qwen/epoch-036 | generation_empty_or_near_empty | 0 | 0 | 0 | 30 | direct_same_metric_and_denominator |
| qwen/epoch-036 | generation_distinct_2 | 0.538966 | 0.804085 | -0.265120 | 30 | direct_same_metric_and_denominator |
| qwen/epoch-036 | generation_repeated_3gram | 0.515868 | 0.208566 | 0.307303 | 30 | direct_same_metric_and_denominator |
| qwen/epoch-036 | generation_repeated_4gram | 0.478139 | — | — | 30 | no_m0_reference |
| qwen/epoch-036 | generation_ppl | 22.202471 | 14.699398 | 7.503074 | 301239 | direct_same_metric_and_denominator |
| smollm/epoch-018 | wikitext_bpb | 0.651288 | 0.641101 | 0.010187 | 62 | direct_same_metric_and_denominator |
| smollm/epoch-018 | wikitext_word_ppl | 11.179075 | 10.764849 | 0.414227 | 62 | direct_same_metric_and_denominator |
| smollm/epoch-018 | blimp_accuracy | 0.773896 | 0.802627 | -0.028731 | 67000 | direct_same_metric_and_denominator |
| smollm/epoch-018 | hellaswag_acc_norm | 0.722764 | 0.714001 | 0.008763 | 10042 | direct_same_metric_and_denominator |
| smollm/epoch-018 | turblimp_acc_norm | 0.589063 | 0.590000 | -0.000937 | 16000 | direct_same_metric_and_denominator |
| smollm/epoch-018 | exact_prefix_top1_accuracy | 1.000000 | 0.032000 | 0.968000 | 500 | direct_same_metric_and_denominator |
| smollm/epoch-018 | exact_prefix_top5_accuracy | 1.000000 | — | — | 500 | no_m0_reference |
| smollm/epoch-018 | exact_prefix_mrr | 1.000000 | — | — | 500 | no_m0_reference |
| smollm/epoch-018 | factual_top1_count | 4987 | 146 | 4841 | 12000 | direct_same_metric_and_denominator |
| smollm/epoch-018 | factual_top1_rate | 0.415583 | 0.012167 | 0.403417 | 12000 | direct_same_metric_and_denominator |
| smollm/epoch-018 | factual_forced_choice_rate | 0.607708 | 0.502708 | 0.105000 | 4800 | direct_same_metric_and_denominator |
| smollm/epoch-018 | factual_failure_early_eos | 1189 | — | — | 12000 | no_m0_reference |
| smollm/epoch-018 | factual_failure_none | 4987 | — | — | 12000 | no_m0_reference |
| smollm/epoch-018 | factual_prompt_form_failures | 4500 | 3165 | 1335 | 12000 | direct_same_metric_and_denominator |
| smollm/epoch-018 | factual_failure_relation_swap | 1324 | — | — | 12000 | no_m0_reference |
| smollm/epoch-018 | turkish_bpb | 1.576605 | 1.491088 | — | 12207027 | m0_reference_denominator_unbound |
| smollm/epoch-018 | generation_top1_accuracy | 1.000000 | 1.000000 | 0.000000 | 30 | direct_same_metric_and_denominator |
| smollm/epoch-018 | generation_empty_or_near_empty | 0 | 0 | 0 | 30 | direct_same_metric_and_denominator |
| smollm/epoch-018 | generation_distinct_2 | 0.633862 | 0.666138 | -0.032275 | 30 | direct_same_metric_and_denominator |
| smollm/epoch-018 | generation_repeated_3gram | 0.470430 | 0.423118 | 0.047312 | 30 | direct_same_metric_and_denominator |
| smollm/epoch-018 | generation_repeated_4gram | 0.426230 | — | — | 30 | no_m0_reference |
| smollm/epoch-018 | generation_ppl | 17.184491 | 15.924011 | 1.260480 | 304243 | direct_same_metric_and_denominator |
| smollm/epoch-036 | wikitext_bpb | 0.651458 | 0.641101 | 0.010357 | 62 | direct_same_metric_and_denominator |
| smollm/epoch-036 | wikitext_word_ppl | 11.186147 | 10.764849 | 0.421299 | 62 | direct_same_metric_and_denominator |
| smollm/epoch-036 | blimp_accuracy | 0.773866 | 0.802627 | -0.028761 | 67000 | direct_same_metric_and_denominator |
| smollm/epoch-036 | hellaswag_acc_norm | 0.723262 | 0.714001 | 0.009261 | 10042 | direct_same_metric_and_denominator |
| smollm/epoch-036 | turblimp_acc_norm | 0.588563 | 0.590000 | -0.001437 | 16000 | direct_same_metric_and_denominator |
| smollm/epoch-036 | exact_prefix_top1_accuracy | 1.000000 | 0.032000 | 0.968000 | 500 | direct_same_metric_and_denominator |
| smollm/epoch-036 | exact_prefix_top5_accuracy | 1.000000 | — | — | 500 | no_m0_reference |
| smollm/epoch-036 | exact_prefix_mrr | 1.000000 | — | — | 500 | no_m0_reference |
| smollm/epoch-036 | factual_top1_count | 5045 | 146 | 4899 | 12000 | direct_same_metric_and_denominator |
| smollm/epoch-036 | factual_top1_rate | 0.420417 | 0.012167 | 0.408250 | 12000 | direct_same_metric_and_denominator |
| smollm/epoch-036 | factual_forced_choice_rate | 0.604167 | 0.502708 | 0.101458 | 4800 | direct_same_metric_and_denominator |
| smollm/epoch-036 | factual_failure_early_eos | 1182 | — | — | 12000 | no_m0_reference |
| smollm/epoch-036 | factual_failure_none | 5045 | — | — | 12000 | no_m0_reference |
| smollm/epoch-036 | factual_prompt_form_failures | 4431 | 3165 | 1266 | 12000 | direct_same_metric_and_denominator |
| smollm/epoch-036 | factual_failure_relation_swap | 1342 | — | — | 12000 | no_m0_reference |
| smollm/epoch-036 | turkish_bpb | 1.579330 | 1.491088 | — | 12207027 | m0_reference_denominator_unbound |
| smollm/epoch-036 | generation_top1_accuracy | 1.000000 | 1.000000 | 0.000000 | 30 | direct_same_metric_and_denominator |
| smollm/epoch-036 | generation_empty_or_near_empty | 0 | 0 | 0 | 30 | direct_same_metric_and_denominator |
| smollm/epoch-036 | generation_distinct_2 | 0.623810 | 0.666138 | -0.042328 | 30 | direct_same_metric_and_denominator |
| smollm/epoch-036 | generation_repeated_3gram | 0.475806 | 0.423118 | 0.052688 | 30 | direct_same_metric_and_denominator |
| smollm/epoch-036 | generation_repeated_4gram | 0.427869 | — | — | 30 | no_m0_reference |
| smollm/epoch-036 | generation_ppl | 17.233806 | 15.924011 | 1.309795 | 304243 | direct_same_metric_and_denominator |

## All-checkpoint trajectory list

The following is the compact review list requested for M0-style comparison. `parent` is
the M0 evidence projection; all epoch rows are measured M1 GPU snapshots. Missing cells are
not zero and mean that the panel was not scheduled at that cadence.

| model | checkpoint | epoch | update | state_kind | wikitext_bpb | wikitext_bpb_m0 | wikitext_bpb_delta | exact_prefix_top1_accuracy | factual_cheap_top1_rate | factual_top1_rate | factual_forced_choice_rate | turkish_bpb | generation_top1_accuracy | generation_distinct_2 | generation_repeated_3gram | generation_ppl | blimp_accuracy | hellaswag_acc_norm | turblimp_acc_norm |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| olmo | parent | 0 | 0 | m0_parent_projection | 0.659744 | 0.659744 | 0 | 0.022000 | — | 0.015167 | 0.505000 | 1.647682 | 1.000000 | 0.593082 | 0.491618 | 16.800732 | 0.822164 | 0.682832 | 0.573500 |
| olmo | epoch-001 | 1 | 7 | m1_gpu_snapshot | 0.663985 | 0.659744 | 0.004241 | 0.046000 | — | — | — | 1.677021 | 1.000000 | 0.648148 | 0.451075 | 18.134869 | — | — | — |
| olmo | epoch-002 | 2 | 14 | m1_gpu_snapshot | 0.673418 | 0.659744 | 0.013674 | 0.114000 | — | — | — | 1.772693 | 1.000000 | 0.556244 | 0.557320 | 20.057909 | — | — | — |
| olmo | epoch-003 | 3 | 21 | m1_gpu_snapshot | 0.677772 | 0.659744 | 0.018028 | 0.404000 | — | — | — | 1.866490 | 1.000000 | 0.558640 | 0.565353 | 21.130940 | — | — | — |
| olmo | epoch-004 | 4 | 28 | m1_gpu_snapshot | 0.681417 | 0.659744 | 0.021672 | 0.846000 | — | — | — | 1.962605 | 1.000000 | 0.599471 | 0.480108 | 22.230953 | — | — | — |
| olmo | epoch-005 | 5 | 35 | m1_gpu_snapshot | 0.683946 | 0.659744 | 0.024202 | 0.988000 | — | — | — | 2.031099 | 1.000000 | 0.624949 | 0.448387 | 22.968354 | — | — | — |
| olmo | epoch-006 | 6 | 42 | m1_gpu_snapshot | 0.686563 | 0.659744 | 0.026819 | 0.998000 | — | — | — | 2.088632 | 1.000000 | 0.595979 | 0.519201 | 23.985723 | — | — | — |
| olmo | epoch-007 | 7 | 49 | m1_gpu_snapshot | 0.686865 | 0.659744 | 0.027121 | 1.000000 | — | — | — | 2.090411 | 1.000000 | 0.597663 | 0.518895 | 24.045475 | — | — | — |
| olmo | epoch-008 | 8 | 56 | m1_gpu_snapshot | 0.687091 | 0.659744 | 0.027346 | 1.000000 | — | — | — | 2.094653 | 1.000000 | 0.629918 | 0.476589 | 24.133792 | — | — | — |
| olmo | epoch-009 | 9 | 63 | m1_gpu_snapshot | 0.687244 | 0.659744 | 0.027499 | 1.000000 | — | — | — | 2.097885 | 1.000000 | 0.569916 | 0.543930 | 24.192052 | — | — | — |
| olmo | epoch-010 | 10 | 70 | m1_gpu_snapshot | 0.687318 | 0.659744 | 0.027574 | 1.000000 | — | — | — | 2.100034 | 1.000000 | 0.597663 | 0.508329 | 24.239023 | — | — | — |
| olmo | epoch-011 | 11 | 77 | m1_gpu_snapshot | 0.687380 | 0.659744 | 0.027635 | 1.000000 | — | — | — | 2.101466 | 1.000000 | 0.613309 | 0.473138 | 24.267841 | — | — | — |
| olmo | epoch-012 | 12 | 84 | m1_gpu_snapshot | 0.687430 | 0.659744 | 0.027685 | 1.000000 | — | — | — | 2.102631 | 1.000000 | 0.583473 | 0.523414 | 24.297502 | — | — | — |
| olmo | epoch-013 | 13 | 91 | m1_gpu_snapshot | 0.687467 | 0.659744 | 0.027722 | 1.000000 | — | — | — | 2.103591 | 1.000000 | 0.552826 | 0.562766 | 24.311513 | — | — | — |
| olmo | epoch-014 | 14 | 98 | m1_gpu_snapshot | 0.687512 | 0.659744 | 0.027768 | 1.000000 | — | — | — | 2.104361 | 1.000000 | 0.602955 | 0.498271 | 24.333705 | — | — | — |
| olmo | epoch-015 | 15 | 105 | m1_gpu_snapshot | 0.687535 | 0.659744 | 0.027790 | 1.000000 | — | — | — | 2.105189 | 1.000000 | 0.592546 | 0.498620 | 24.350427 | — | — | — |
| olmo | epoch-016 | 16 | 112 | m1_gpu_snapshot | 0.687578 | 0.659744 | 0.027833 | 1.000000 | — | — | — | 2.105860 | 1.000000 | 0.587797 | 0.519034 | 24.369875 | — | — | — |
| olmo | epoch-017 | 17 | 119 | m1_gpu_snapshot | 0.687623 | 0.659744 | 0.027879 | 1.000000 | — | — | — | 2.106532 | 1.000000 | 0.616926 | 0.474368 | 24.382997 | — | — | — |
| olmo | epoch-018 | 18 | 126 | m1_gpu_snapshot | 0.687642 | 0.659744 | 0.027898 | 1.000000 | 0.439333 | 0.442417 | 0.670417 | 2.107204 | 1.000000 | 0.570659 | 0.540538 | 24.396261 | 0.717328 | 0.662617 | 0.549687 |
| olmo | epoch-019 | 19 | 133 | m1_gpu_snapshot | 0.687658 | 0.659744 | 0.027914 | 1.000000 | — | — | — | 2.107783 | 1.000000 | 0.582275 | 0.514374 | 24.405728 | — | — | — |
| olmo | epoch-020 | 20 | 140 | m1_gpu_snapshot | 0.687674 | 0.659744 | 0.027930 | 1.000000 | — | — | — | 2.108324 | 1.000000 | 0.605908 | 0.503545 | 24.424206 | — | — | — |
| olmo | epoch-021 | 21 | 147 | m1_gpu_snapshot | 0.687688 | 0.659744 | 0.027944 | 1.000000 | — | — | — | 2.108964 | 1.000000 | 0.568676 | 0.534039 | 24.442186 | — | — | — |
| olmo | epoch-022 | 22 | 154 | m1_gpu_snapshot | 0.687737 | 0.659744 | 0.027993 | 1.000000 | — | — | — | 2.109388 | 1.000000 | 0.606109 | 0.490538 | 24.454827 | — | — | — |
| olmo | epoch-023 | 23 | 161 | m1_gpu_snapshot | 0.687751 | 0.659744 | 0.028006 | 1.000000 | — | — | — | 2.109918 | 1.000000 | 0.641887 | 0.428813 | 24.458560 | — | — | — |
| olmo | epoch-024 | 24 | 168 | m1_gpu_snapshot | 0.687761 | 0.659744 | 0.028017 | 1.000000 | — | — | — | 2.110434 | 1.000000 | 0.585495 | 0.499884 | 24.475247 | — | — | — |
| olmo | epoch-025 | 25 | 175 | m1_gpu_snapshot | 0.687762 | 0.659744 | 0.028018 | 1.000000 | — | — | — | 2.110903 | 1.000000 | 0.601347 | 0.480323 | 24.483021 | — | — | — |
| olmo | epoch-026 | 26 | 182 | m1_gpu_snapshot | 0.687773 | 0.659744 | 0.028029 | 1.000000 | — | — | — | 2.111333 | 1.000000 | 0.570130 | 0.523871 | 24.495330 | — | — | — |
| olmo | epoch-027 | 27 | 189 | m1_gpu_snapshot | 0.687801 | 0.659744 | 0.028057 | 1.000000 | — | — | — | 2.111824 | 1.000000 | 0.554390 | 0.546405 | 24.503278 | — | — | — |
| olmo | epoch-028 | 28 | 196 | m1_gpu_snapshot | 0.687786 | 0.659744 | 0.028041 | 1.000000 | — | — | — | 2.112302 | 1.000000 | 0.568356 | 0.513871 | 24.514619 | — | — | — |
| olmo | epoch-029 | 29 | 203 | m1_gpu_snapshot | 0.687827 | 0.659744 | 0.028083 | 1.000000 | — | — | — | 2.112555 | 1.000000 | 0.609524 | 0.467204 | 24.526101 | — | — | — |
| olmo | epoch-030 | 30 | 210 | m1_gpu_snapshot | 0.687849 | 0.659744 | 0.028105 | 1.000000 | — | — | — | 2.113077 | 1.000000 | 0.536817 | 0.573539 | 24.536437 | — | — | — |
| olmo | epoch-031 | 31 | 217 | m1_gpu_snapshot | 0.687874 | 0.659744 | 0.028130 | 1.000000 | — | — | — | 2.113469 | 1.000000 | 0.621453 | 0.450753 | 24.541802 | — | — | — |
| olmo | epoch-032 | 32 | 224 | m1_gpu_snapshot | 0.687887 | 0.659744 | 0.028143 | 1.000000 | — | — | — | 2.113781 | 1.000000 | 0.574402 | 0.520534 | 24.558059 | — | — | — |
| olmo | epoch-033 | 33 | 231 | m1_gpu_snapshot | 0.687902 | 0.659744 | 0.028158 | 1.000000 | — | — | — | 2.114138 | 1.000000 | 0.609057 | 0.482339 | 24.566725 | — | — | — |
| olmo | epoch-034 | 34 | 238 | m1_gpu_snapshot | 0.687924 | 0.659744 | 0.028180 | 1.000000 | — | — | — | 2.114502 | 1.000000 | 0.594380 | 0.502761 | 24.573682 | — | — | — |
| olmo | epoch-035 | 35 | 245 | m1_gpu_snapshot | 0.687949 | 0.659744 | 0.028204 | 1.000000 | — | — | — | 2.114863 | 1.000000 | 0.595767 | 0.488886 | 24.577436 | — | — | — |
| olmo | epoch-036 | 36 | 252 | m1_gpu_snapshot | 0.687969 | 0.659744 | 0.028224 | 1.000000 | 0.442000 | 0.442667 | 0.672708 | 2.115221 | 1.000000 | 0.603904 | 0.487707 | 24.590437 | 0.716030 | 0.660924 | 0.549375 |
| qwen | parent | 0 | 0 | m0_parent_projection | 0.672593 | 0.672593 | 0 | 0.030000 | — | 0.017417 | 0.499167 | 1.246670 | 0.900000 | 0.804085 | 0.208566 | 14.699398 | 0.825224 | 0.677455 | 0.664313 |
| qwen | epoch-001 | 1 | 7 | m1_gpu_snapshot | 0.687793 | 0.672593 | 0.015199 | 0.028000 | — | — | — | 1.292513 | 0.933333 | 0.742043 | 0.317563 | 16.209178 | — | — | — |
| qwen | epoch-002 | 2 | 14 | m1_gpu_snapshot | 0.713152 | 0.672593 | 0.040558 | 0.108000 | — | — | — | 1.361507 | 0.966667 | 0.559764 | 0.560114 | 18.669798 | — | — | — |
| qwen | epoch-003 | 3 | 21 | m1_gpu_snapshot | 0.726364 | 0.672593 | 0.053771 | 0.470000 | — | — | — | 1.403883 | 0.966667 | 0.577438 | 0.493376 | 20.368308 | — | — | — |
| qwen | epoch-004 | 4 | 28 | m1_gpu_snapshot | 0.732781 | 0.672593 | 0.060187 | 0.918000 | — | — | — | 1.445760 | 0.966667 | 0.487154 | 0.589273 | 21.590027 | — | — | — |
| qwen | epoch-005 | 5 | 35 | m1_gpu_snapshot | 0.735011 | 0.672593 | 0.062418 | 0.994000 | — | — | — | 1.464349 | 0.966667 | 0.540542 | 0.500815 | 21.904799 | — | — | — |
| qwen | epoch-006 | 6 | 42 | m1_gpu_snapshot | 0.736024 | 0.672593 | 0.063431 | 0.996000 | — | — | — | 1.475747 | 0.966667 | 0.571822 | 0.483913 | 22.082547 | — | — | — |
| qwen | epoch-007 | 7 | 49 | m1_gpu_snapshot | 0.736519 | 0.672593 | 0.063926 | 1.000000 | — | — | — | 1.476022 | 0.966667 | 0.542344 | 0.499202 | 22.113514 | — | — | — |
| qwen | epoch-008 | 8 | 56 | m1_gpu_snapshot | 0.736643 | 0.672593 | 0.064050 | 1.000000 | — | — | — | 1.475900 | 0.966667 | 0.514332 | 0.552153 | 22.116635 | — | — | — |
| qwen | epoch-009 | 9 | 63 | m1_gpu_snapshot | 0.736643 | 0.672593 | 0.064050 | 1.000000 | — | — | — | 1.476247 | 0.966667 | 0.512190 | 0.542752 | 22.105256 | — | — | — |
| qwen | epoch-010 | 10 | 70 | m1_gpu_snapshot | 0.736620 | 0.672593 | 0.064027 | 1.000000 | — | — | — | 1.476684 | 0.966667 | 0.483110 | 0.573106 | 22.111079 | — | — | — |
| qwen | epoch-011 | 11 | 77 | m1_gpu_snapshot | 0.736589 | 0.672593 | 0.063996 | 1.000000 | — | — | — | 1.476965 | 0.966667 | 0.523460 | 0.527646 | 22.118902 | — | — | — |
| qwen | epoch-012 | 12 | 84 | m1_gpu_snapshot | 0.736591 | 0.672593 | 0.063998 | 1.000000 | — | — | — | 1.477221 | 0.966667 | 0.512140 | 0.555455 | 22.126717 | — | — | — |
| qwen | epoch-013 | 13 | 91 | m1_gpu_snapshot | 0.736592 | 0.672593 | 0.063998 | 1.000000 | — | — | — | 1.477390 | 0.966667 | 0.531049 | 0.529223 | 22.132553 | — | — | — |
| qwen | epoch-014 | 14 | 98 | m1_gpu_snapshot | 0.736574 | 0.672593 | 0.063980 | 1.000000 | — | — | — | 1.477538 | 0.966667 | 0.499955 | 0.556643 | 22.136014 | — | — | — |
| qwen | epoch-015 | 15 | 105 | m1_gpu_snapshot | 0.736576 | 0.672593 | 0.063983 | 1.000000 | — | — | — | 1.477711 | 0.966667 | 0.536554 | 0.516132 | 22.140569 | — | — | — |
| qwen | epoch-016 | 16 | 112 | m1_gpu_snapshot | 0.736594 | 0.672593 | 0.064001 | 1.000000 | — | — | — | 1.477844 | 0.966667 | 0.493463 | 0.569094 | 22.150064 | — | — | — |
| qwen | epoch-017 | 17 | 119 | m1_gpu_snapshot | 0.736580 | 0.672593 | 0.063987 | 1.000000 | — | — | — | 1.477980 | 0.966667 | 0.514179 | 0.542212 | 22.151625 | — | — | — |
| qwen | epoch-018 | 18 | 126 | m1_gpu_snapshot | 0.736580 | 0.672593 | 0.063987 | 1.000000 | 0.689333 | 0.685500 | 0.810208 | 1.478100 | 0.966667 | 0.478648 | 0.581997 | 22.158532 | 0.769090 | 0.671181 | 0.659375 |
| qwen | epoch-019 | 19 | 133 | m1_gpu_snapshot | 0.736584 | 0.672593 | 0.063991 | 1.000000 | — | — | — | 1.478226 | 0.966667 | 0.541285 | 0.512105 | 22.160414 | — | — | — |
| qwen | epoch-020 | 20 | 140 | m1_gpu_snapshot | 0.736583 | 0.672593 | 0.063989 | 1.000000 | — | — | — | 1.478346 | 0.966667 | 0.513104 | 0.555637 | 22.162294 | — | — | — |
| qwen | epoch-021 | 21 | 147 | m1_gpu_snapshot | 0.736588 | 0.672593 | 0.063995 | 1.000000 | — | — | — | 1.478458 | 0.966667 | 0.507733 | 0.554839 | 22.167401 | — | — | — |
| qwen | epoch-022 | 22 | 154 | m1_gpu_snapshot | 0.736589 | 0.672593 | 0.063996 | 1.000000 | — | — | — | 1.478579 | 0.966667 | 0.521705 | 0.536790 | 22.172501 | — | — | — |
| qwen | epoch-023 | 23 | 161 | m1_gpu_snapshot | 0.736586 | 0.672593 | 0.063993 | 1.000000 | — | — | — | 1.478679 | 0.966667 | 0.470915 | 0.581460 | 22.172129 | — | — | — |
| qwen | epoch-024 | 24 | 168 | m1_gpu_snapshot | 0.736588 | 0.672593 | 0.063995 | 1.000000 | — | — | — | 1.478777 | 0.966667 | 0.505246 | 0.557180 | 22.177516 | — | — | — |
| qwen | epoch-025 | 25 | 175 | m1_gpu_snapshot | 0.736590 | 0.672593 | 0.063997 | 1.000000 | — | — | — | 1.478889 | 0.966667 | 0.539140 | 0.511646 | 22.178006 | — | — | — |
| qwen | epoch-026 | 26 | 182 | m1_gpu_snapshot | 0.736591 | 0.672593 | 0.063997 | 1.000000 | — | — | — | 1.478956 | 0.966667 | 0.518473 | 0.547503 | 22.182656 | — | — | — |
| qwen | epoch-027 | 27 | 189 | m1_gpu_snapshot | 0.736586 | 0.672593 | 0.063993 | 1.000000 | — | — | — | 1.479031 | 0.966667 | 0.479706 | 0.593825 | 22.182249 | — | — | — |
| qwen | epoch-028 | 28 | 196 | m1_gpu_snapshot | 0.736591 | 0.672593 | 0.063997 | 1.000000 | — | — | — | 1.479176 | 0.966667 | 0.503516 | 0.563718 | 22.189506 | — | — | — |
| qwen | epoch-029 | 29 | 203 | m1_gpu_snapshot | 0.736604 | 0.672593 | 0.064011 | 1.000000 | — | — | — | 1.479257 | 0.966667 | 0.463833 | 0.607804 | 22.190992 | — | — | — |
| qwen | epoch-030 | 30 | 210 | m1_gpu_snapshot | 0.736599 | 0.672593 | 0.064006 | 1.000000 | — | — | — | 1.479341 | 0.966667 | 0.496318 | 0.561745 | 22.193434 | — | — | — |
| qwen | epoch-031 | 31 | 217 | m1_gpu_snapshot | 0.736606 | 0.672593 | 0.064013 | 1.000000 | — | — | — | 1.479413 | 0.966667 | 0.509989 | 0.556856 | 22.193312 | — | — | — |
| qwen | epoch-032 | 32 | 224 | m1_gpu_snapshot | 0.736602 | 0.672593 | 0.064009 | 1.000000 | — | — | — | 1.479512 | 0.966667 | 0.479177 | 0.594363 | 22.197404 | — | — | — |
| qwen | epoch-033 | 33 | 231 | m1_gpu_snapshot | 0.736613 | 0.672593 | 0.064020 | 1.000000 | — | — | — | 1.479580 | 0.966667 | 0.511452 | 0.538449 | 22.202095 | — | — | — |
| qwen | epoch-034 | 34 | 238 | m1_gpu_snapshot | 0.736602 | 0.672593 | 0.064009 | 1.000000 | — | — | — | 1.479682 | 0.966667 | 0.503658 | 0.559868 | 22.201819 | — | — | — |
| qwen | epoch-035 | 35 | 245 | m1_gpu_snapshot | 0.736610 | 0.672593 | 0.064016 | 1.000000 | — | — | — | 1.479730 | 0.966667 | 0.477590 | 0.588987 | 22.204886 | — | — | — |
| qwen | epoch-036 | 36 | 252 | m1_gpu_snapshot | 0.736614 | 0.672593 | 0.064021 | 1.000000 | 0.686667 | 0.686333 | 0.811667 | 1.479814 | 0.966667 | 0.538966 | 0.515868 | 22.202471 | 0.768060 | 0.671281 | 0.659438 |
| smollm | parent | 0 | 0 | m0_parent_projection | 0.641101 | 0.641101 | 0 | 0.032000 | — | 0.012167 | 0.502708 | 1.491088 | 1.000000 | 0.666138 | 0.423118 | 15.924011 | 0.802627 | 0.714001 | 0.590000 |
| smollm | epoch-001 | 1 | 7 | m1_gpu_snapshot | 0.641397 | 0.641101 | 0.000296 | 0.032000 | — | — | — | 1.490545 | 1.000000 | 0.612169 | 0.500000 | 15.887286 | — | — | — |
| smollm | epoch-002 | 2 | 14 | m1_gpu_snapshot | 0.642618 | 0.641101 | 0.001517 | 0.032000 | — | — | — | 1.494640 | 1.000000 | 0.634921 | 0.461290 | 15.949741 | — | — | — |
| smollm | epoch-003 | 3 | 21 | m1_gpu_snapshot | 0.643850 | 0.641101 | 0.002749 | 0.038000 | — | — | — | 1.500951 | 1.000000 | 0.608466 | 0.510215 | 16.055462 | — | — | — |
| smollm | epoch-004 | 4 | 28 | m1_gpu_snapshot | 0.644785 | 0.641101 | 0.003684 | 0.064000 | — | — | — | 1.507964 | 1.000000 | 0.642328 | 0.466129 | 16.152467 | — | — | — |
| smollm | epoch-005 | 5 | 35 | m1_gpu_snapshot | 0.645588 | 0.641101 | 0.004487 | 0.116000 | — | — | — | 1.514879 | 1.000000 | 0.605291 | 0.525269 | 16.242601 | — | — | — |
| smollm | epoch-006 | 6 | 42 | m1_gpu_snapshot | 0.646369 | 0.641101 | 0.005268 | 0.224000 | — | — | — | 1.522659 | 1.000000 | 0.647619 | 0.453226 | 16.351560 | — | — | — |
| smollm | epoch-007 | 7 | 49 | m1_gpu_snapshot | 0.647155 | 0.641101 | 0.006054 | 0.338000 | — | — | — | 1.530601 | 1.000000 | 0.636508 | 0.475806 | 16.473485 | — | — | — |
| smollm | epoch-008 | 8 | 56 | m1_gpu_snapshot | 0.648000 | 0.641101 | 0.006899 | 0.494000 | — | — | — | 1.538582 | 1.000000 | 0.633333 | 0.484409 | 16.608059 | — | — | — |
| smollm | epoch-009 | 9 | 63 | m1_gpu_snapshot | 0.648652 | 0.641101 | 0.007551 | 0.676000 | — | — | — | 1.546035 | 1.000000 | 0.657672 | 0.440860 | 16.714165 | — | — | — |
| smollm | epoch-010 | 10 | 70 | m1_gpu_snapshot | 0.649316 | 0.641101 | 0.008215 | 0.816000 | — | — | — | 1.554377 | 1.000000 | 0.658201 | 0.434409 | 16.836001 | — | — | — |
| smollm | epoch-011 | 11 | 77 | m1_gpu_snapshot | 0.649815 | 0.641101 | 0.008714 | 0.936000 | — | — | — | 1.560460 | 1.000000 | 0.620106 | 0.496237 | 16.925551 | — | — | — |
| smollm | epoch-012 | 12 | 84 | m1_gpu_snapshot | 0.650353 | 0.641101 | 0.009252 | 0.980000 | — | — | — | 1.567228 | 1.000000 | 0.652910 | 0.446237 | 17.010168 | — | — | — |
| smollm | epoch-013 | 13 | 91 | m1_gpu_snapshot | 0.650625 | 0.641101 | 0.009524 | 0.998000 | — | — | — | 1.569623 | 1.000000 | 0.633333 | 0.477419 | 17.054087 | — | — | — |
| smollm | epoch-014 | 14 | 98 | m1_gpu_snapshot | 0.650863 | 0.641101 | 0.009762 | 1.000000 | — | — | — | 1.572017 | 1.000000 | 0.619048 | 0.496774 | 17.093313 | — | — | — |
| smollm | epoch-015 | 15 | 105 | m1_gpu_snapshot | 0.651000 | 0.641101 | 0.009899 | 1.000000 | — | — | — | 1.573684 | 1.000000 | 0.617460 | 0.490323 | 17.131023 | — | — | — |
| smollm | epoch-016 | 16 | 112 | m1_gpu_snapshot | 0.651160 | 0.641101 | 0.010059 | 1.000000 | — | — | — | 1.575013 | 1.000000 | 0.608995 | 0.510753 | 17.153544 | — | — | — |
| smollm | epoch-017 | 17 | 119 | m1_gpu_snapshot | 0.651207 | 0.641101 | 0.010106 | 1.000000 | — | — | — | 1.576069 | 1.000000 | 0.652910 | 0.446774 | 17.174054 | — | — | — |
| smollm | epoch-018 | 18 | 126 | m1_gpu_snapshot | 0.651288 | 0.641101 | 0.010187 | 1.000000 | 0.418000 | 0.415583 | 0.607708 | 1.576605 | 1.000000 | 0.633862 | 0.470430 | 17.184491 | 0.773896 | 0.722764 | 0.589063 |
| smollm | epoch-019 | 19 | 133 | m1_gpu_snapshot | 0.651312 | 0.641101 | 0.010211 | 1.000000 | — | — | — | 1.577047 | 1.000000 | 0.612698 | 0.507527 | 17.190142 | — | — | — |
| smollm | epoch-020 | 20 | 140 | m1_gpu_snapshot | 0.651336 | 0.641101 | 0.010235 | 1.000000 | — | — | — | 1.577327 | 1.000000 | 0.651323 | 0.448387 | 17.196050 | — | — | — |
| smollm | epoch-021 | 21 | 147 | m1_gpu_snapshot | 0.651362 | 0.641101 | 0.010260 | 1.000000 | — | — | — | 1.577617 | 1.000000 | 0.603175 | 0.519355 | 17.199469 | — | — | — |
| smollm | epoch-022 | 22 | 154 | m1_gpu_snapshot | 0.651356 | 0.641101 | 0.010255 | 1.000000 | — | — | — | 1.577719 | 1.000000 | 0.635979 | 0.450538 | 17.205112 | — | — | — |
| smollm | epoch-023 | 23 | 161 | m1_gpu_snapshot | 0.651365 | 0.641101 | 0.010264 | 1.000000 | — | — | — | 1.577876 | 1.000000 | 0.612698 | 0.494086 | 17.206538 | — | — | — |
| smollm | epoch-024 | 24 | 168 | m1_gpu_snapshot | 0.651386 | 0.641101 | 0.010285 | 1.000000 | — | — | — | 1.578016 | 1.000000 | 0.668783 | 0.409677 | 17.209623 | — | — | — |
| smollm | epoch-025 | 25 | 175 | m1_gpu_snapshot | 0.651387 | 0.641101 | 0.010286 | 1.000000 | — | — | — | 1.578094 | 1.000000 | 0.643386 | 0.441935 | 17.211714 | — | — | — |
| smollm | epoch-026 | 26 | 182 | m1_gpu_snapshot | 0.651406 | 0.641101 | 0.010305 | 1.000000 | — | — | — | 1.578262 | 1.000000 | 0.659259 | 0.432796 | 17.212477 | — | — | — |
| smollm | epoch-027 | 27 | 189 | m1_gpu_snapshot | 0.651386 | 0.641101 | 0.010285 | 1.000000 | — | — | — | 1.578352 | 1.000000 | 0.624868 | 0.479032 | 17.217117 | — | — | — |
| smollm | epoch-028 | 28 | 196 | m1_gpu_snapshot | 0.651420 | 0.641101 | 0.010319 | 1.000000 | — | — | — | 1.578456 | 1.000000 | 0.621693 | 0.482796 | 17.220204 | — | — | — |
| smollm | epoch-029 | 29 | 203 | m1_gpu_snapshot | 0.651429 | 0.641101 | 0.010328 | 1.000000 | — | — | — | 1.578593 | 1.000000 | 0.631746 | 0.468280 | 17.219915 | — | — | — |
| smollm | epoch-030 | 30 | 210 | m1_gpu_snapshot | 0.651410 | 0.641101 | 0.010309 | 1.000000 | — | — | — | 1.578714 | 1.000000 | 0.616402 | 0.488710 | 17.222757 | — | — | — |
| smollm | epoch-031 | 31 | 217 | m1_gpu_snapshot | 0.651433 | 0.641101 | 0.010332 | 1.000000 | — | — | — | 1.578836 | 1.000000 | 0.650265 | 0.440323 | 17.225990 | — | — | — |
| smollm | epoch-032 | 32 | 224 | m1_gpu_snapshot | 0.651446 | 0.641101 | 0.010345 | 1.000000 | — | — | — | 1.578882 | 1.000000 | 0.642857 | 0.446237 | 17.229031 | — | — | — |
| smollm | epoch-033 | 33 | 231 | m1_gpu_snapshot | 0.651438 | 0.641101 | 0.010337 | 1.000000 | — | — | — | 1.579034 | 1.000000 | 0.655556 | 0.443548 | 17.226216 | — | — | — |
| smollm | epoch-034 | 34 | 238 | m1_gpu_snapshot | 0.651443 | 0.641101 | 0.010342 | 1.000000 | — | — | — | 1.579064 | 1.000000 | 0.646032 | 0.453226 | 17.232510 | — | — | — |
| smollm | epoch-035 | 35 | 245 | m1_gpu_snapshot | 0.651443 | 0.641101 | 0.010342 | 1.000000 | — | — | — | 1.579251 | 1.000000 | 0.664021 | 0.416667 | 17.233375 | — | — | — |
| smollm | epoch-036 | 36 | 252 | m1_gpu_snapshot | 0.651458 | 0.641101 | 0.010357 | 1.000000 | 0.417333 | 0.420417 | 0.604167 | 1.579330 | 1.000000 | 0.623810 | 0.475806 | 17.233806 | 0.773866 | 0.723262 | 0.588563 |

## Missingness, retry and evidence notes

- The final canonical family is complete. Historical failed attempts remain on HU scratch and
  are represented through each task's `archived_failed_attempts` field; they are not counted as
  additional scientific states.
- Qwen epoch-018 records `epoch-018__killed_0` as an archived hard-killed attempt. The final
  canonical result is complete and is counted once.
- `sacct` accounting metadata was unavailable during live inspection because of the cluster's
  Munge/SlurmDBD authentication failure. This does not invalidate the independently written
  finalizer family result, task results, or metric-summary hashes.
- Raw sample JSONL, CSV/parquet evidence, checkpoints and weights remain on HU scratch. The
  compact Git layer stores summary values, provenance paths and hashes only.
- Token PPL is a within-tokenizer companion. BPB is the primary retention metric for cross-model
  comparison. Exact-prefix is candidate ranking, not free-generation exact-match accuracy.

## Reproducible local views

- `artifacts/evaluations/m1_three_model_v1/dump/m1_metrics.json` — compact canonical result layer
  for this snapshot, including state bundles, normalized metric rows and provenance.
- `artifacts/evaluations/m1_three_model_v1/dump/m0_m1_comparison.csv` — long-form M0/M1 comparison
  with denominators, deltas and comparison status for every normalized row.
- `artifacts/evaluations/m1_three_model_v1/dump/m1_trajectory.csv` — one row per model × parent/epoch
  with the recurring trajectory metrics.
