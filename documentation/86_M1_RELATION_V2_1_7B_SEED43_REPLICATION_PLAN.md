# M1 Relation V2 1.7B Seed-43 Replication Plan

## Rationale

The first valid SmolLM2-1.7B capacity-control run passed the full gate decisively. Checkpoint 200
achieved 500 exact, 499 direct, 498 QA, 497 direct/QA overlap, and 497 triple successes. Before
freezing this M1 family for M2/M3, the result must be replicated under a second training seed.

This is an independent training replication from the pinned base model, not continued training from
checkpoint 200. Continuing checkpoint 200 would test additional exposure; starting from the base
model with a new seed tests whether the capacity result is stable.

## Controlled Change

The replication preserves:

- the same 100 subjects, 500 facts, five relations, and seven rows per fact;
- dataset split seed 42 and identical train/validation files;
- SmolLM2-1.7B pinned snapshot;
- answer-only objective;
- learning rate `1e-4`, 36 epochs, effective batch 500, and 252 optimizer updates;
- micro-batch 10, gradient accumulation 50, evaluation batch 1;
- constant-with-warmup schedule, 2% warmup, no weight decay;
- identical exact-prefix, held-out direct, and QA-matched evaluators;
- unchanged full gate: exact >= 450, direct >= 400, QA >= 400, overlap >= 350.

The only scientific change is:

```text
training seed: 42 -> 43
```

Run naming and output paths differ only to isolate artifacts.

## Launch

- config commit: `9b3e941` on `corpus-update`;
- remote focused tests: 27/27 passed;
- preflight: 3,500 rows, 500 facts, seven rows/fact, effective batch 500, 252 updates;
- verified seeds: split seed 42, training seed 43;
- Slurm job: `399077`;
- node: `gruenau9`;
- first state: `RUNNING`;
- run manifest: `/vol/tmp/yesildau/transfer-vs-relearning/runs/training/m1_smollm2_1_7b_relation_v2_100_subjects_500_facts_direct_seed43/20260713T145424Z_m1_smollm2_1_7b_relation_v2_100_subjects_500_facts_direct_lr1e-4_ep36_seed43_6a47c8c9/training_manifest.json`;
- logs and cache: `/vol/tmp2/yesildau/m1_relation_v2_1_7b_500_seed43`;
- expected training runtime: approximately 47-55 minutes;
- safe observation window: 40-75 minutes;
- monitoring: no continuing sleep process is active.

## Decision Rule

- If seed 43 passes the unchanged full gate, freeze the replicated 1.7B M1 family and proceed to
  the planned M2/M3 stage using a predeclared checkpoint-selection rule.
- If seed 43 shows a material but still passing reduction, report seed variability and use the more
  conservative replicated checkpoint for downstream planning.
- If seed 43 fails the gate, do not scale facts or enter M2/M3 until the variance source is audited.

Checkpoint selection is based on overlap, then triple, direct, QA, and the earlier checkpoint as the
final tie-breaker. The seed-42 checkpoint-200 result is not used to relax the replication gate.

## Replication Correction

Job `399077` completed successfully in 2,779 seconds, but inspection showed that it was not an
independent stochastic replication. The config changed `training.seed` to 43 while the Trainer's
`data_seed` still inherited dataset `split_seed: 42`. SmolLM2-1.7B has `attention_dropout: 0.0`, so
the unchanged data order made training deterministic: the full logged loss trajectory matched the
seed-42 run, the first 64 MiB of checkpoint-25 weights matched byte-for-byte, and the first 16 MiB
of checkpoint-200 weights also matched. Job `399077` is therefore classified as a successful
deterministic reproducibility control and is not submitted for duplicate retrieval evaluation.

The training code now supports an explicit `training.data_seed`, falling back to the previous
split-seed behavior when absent. This preserves backward compatibility while allowing data order
to vary independently of the fixed train/validation split. A focused test verifies both paths.

The corrected replication preserves dataset split seed 42 and sets both training seed and data seed
to 43. It starts from the pinned base model and keeps all other scientific and operational controls
unchanged.

- correction commit: `0b1d30a` on `corpus-update`;
- remote focused tests: 28/28 passed;
- corrected Slurm job: `399078`;
- node: `gruenau9`;
- first state: `RUNNING`;
- corrected run manifest: `/vol/tmp/yesildau/transfer-vs-relearning/runs/training/m1_smollm2_1_7b_relation_v2_100_subjects_500_facts_direct_seed43_data43/20260713T160909Z_m1_smollm2_1_7b_relation_v2_100_subjects_500_facts_direct_lr1e-4_ep36_seed43_data43_f8319fd2/training_manifest.json`;
- logs and cache: `/vol/tmp2/yesildau/m1_relation_v2_1_7b_500_seed43_data43`;
- expected runtime: approximately 47-55 minutes;
- monitoring: no continuing sleep process is active.

## Corrected Training Completion And Evaluation Launch

Job `399078` completed successfully in 2,690 seconds (44 minutes 50 seconds), executing all 36
epochs and 252 optimizer updates. All eleven planned checkpoints were written. Its loss trajectory
differs from seed 42, confirming that the explicit data-order seed changed the training path. Final
validation loss was 0.005654, compared with 0.007413 for seed 42; this is an optimization signal,
not a retrieval conclusion.

The unchanged exact-prefix, held-out direct, and QA-matched sweep was launched for every checkpoint:

```text
checkpoint-100 -> 399079
checkpoint-125 -> 399080
checkpoint-150 -> 399081
checkpoint-175 -> 399082
checkpoint-200 -> 399083
checkpoint-225 -> 399084
checkpoint-250 -> 399085
checkpoint-252 -> 399086
checkpoint-25  -> 399087
checkpoint-50  -> 399088
checkpoint-75  -> 399089
```

At first observation, jobs `399079-399081` were running concurrently on the three gruenau9 A100s;
the remaining jobs were pending for those resources. Evaluation stderr logs were empty. All configs,
logs, model manifests, and outputs are under
`/vol/tmp2/yesildau/m1_relation_v2_1_7b_500_seed43_data43`. No continuing sleep process is active.

All 33 views later completed successfully. Selected checkpoint 75 achieved 500 exact, 500 direct,
499 QA, 499 overlap, and 499 triple successes. The replication gate passes decisively. See
`87_M1_RELATION_V2_1_7B_SEED43_REPLICATION_EVALUATION_REPORT.md` for the complete checkpoint table,
cross-seed comparison, remaining-error audit, and M1 freeze decision.
