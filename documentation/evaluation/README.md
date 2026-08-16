# Evaluation control plane

This directory contains the small read set for evaluation work. It separates current evidence from
the prospective protocol so an agent does not need the chronological archive by default.

## Read order

1. [`EVALUATOR_INVENTORY_V1.md`](EVALUATOR_INVENTORY_V1.md) — what already exists and what is reusable;
2. [`LM_EVAL_TASK_QUALIFICATION_V1.md`](LM_EVAL_TASK_QUALIFICATION_V1.md) — verified and frozen upstream task set;
3. [`RESULT_SCHEMA_V1.md`](RESULT_SCHEMA_V1.md) — canonical normalized artifacts;
4. [`../contracts/evaluation/eval-v1.md`](../contracts/evaluation/eval-v1.md) — frozen prospective protocol;
5. [`../pipeline/README.md`](../pipeline/README.md) — deterministic train/trace/eval/normalize/
   presentation foundation and its execution boundary.

The removed XNLI integration and a possible future upstream Harness repair are isolated in
[`XNLI_HARNESS_COMPATIBILITY_INCIDENT.md`](XNLI_HARNESS_COMPATIBILITY_INCIDENT.md). It is incident
evidence, not part of the active task read set.

The machine-readable frozen registry is
[`../../configs/evaluation/eval_v1_registry.yaml`](../../configs/evaluation/eval_v1_registry.yaml).
Documents 177 and 178 remain the supervisor/design inputs. Historical numbered evaluation reports
remain evidence and are not rewritten by this layer.

The completed OLMo qualification and parity evidence is summarized in
[`../179_M0_OLMO_EVAL_V1_PARITY_EXECUTION_RESULT_AND_FREEZE_GATE_TR.md`](../179_M0_OLMO_EVAL_V1_PARITY_EXECUTION_RESULT_AND_FREEZE_GATE_TR.md).
The final input/gate closure is recorded in
[`../180_EVAL_V1_SCIENTIFIC_INPUT_AND_PROTOCOL_FREEZE_TR.md`](../180_EVAL_V1_SCIENTIFIC_INPUT_AND_PROTOCOL_FREEZE_TR.md).
The frozen three-model scientific M0 binding is
[`../contracts/evaluation/m0-three-model-scientific-v1.md`](../contracts/evaluation/m0-three-model-scientific-v1.md).

`eval-v1` is frozen, but this directory grants no evaluation, download, HU, Slurm, training, or
publication authority.
