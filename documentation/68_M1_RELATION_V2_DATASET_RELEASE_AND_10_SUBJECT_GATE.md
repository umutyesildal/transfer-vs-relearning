# 68 - M1 Relation V2 Dataset Release And 10-Subject Gate

Last updated: 2026-07-12

## Status

Released, reproduced on HU, and submitted for the first fresh base-model acquisition run. The
V2 dataset replaces only `studied_at` and `works_at` with `field_of_study` and
`works_in_industry`; historical `synthetic_v1` artifacts remain intact.

## Dataset Contract

- source repository: `synthetic-data-generation`, branch `relation-redesign-v2`;
- release commit: `ae0399b`;
- generator: `generate_relation_v2_dataset.py`;
- subjects: 5,000;
- facts: 25,000;
- relations: `profession`, `born_in`, `lives_in`, `field_of_study`, `works_in_industry`;
- English training rows: 120,500;
- Turkish repetition rows: 60,235, Branch B only;
- new-relation frequency rule: subject popularity only;
- raw full generated tree: approximately 90 MB, intentionally excluded from Git.

The generated release contains a complete manifest. Historical proper-name university and
employer relations do not appear in V2 output.

## Ten-Subject Acquisition Gate

Selected subject IDs are deterministic under seed 42:

```text
S00634 S00825 S01083 S01854 S02148
S02221 S02868 S02929 S04027 S04944
```

The gate contains 50 facts across all five relations. Each fact has seven English training rows:
three declarative biographies, two Question/Answer prompts, and two scaffold-free direct
questions. It also has one held-out QA prompt and one exact-prefix probe per fact.

| Artifact | Count |
| --- | ---: |
| train rows | 350 |
| rows per fact | 7 |
| held-out validation rows | 50 |
| exact-prefix probes | 50 |

## Frozen Hashes

```text
728c040d3ffa7cc1453c1069876104a3cfb2e2a39c243d97de60f97b9a324ebb  release manifest
51d5428901fe400dd560690d2e16d43050539dbae1f43439d52ac4471b894919  gate train.jsonl
9009af074ea5c1ef1bea3f3b9da7602378e80f25c3cacb9340dcabb4fb779f54  gate validation.jsonl
8f5e91c70a95adf9632b7b90bf8f6a78ded6e8b565e54a63673cfc55764b0cf0  gate exact_prefix_probes_en.csv
b569603a80854d7e499553b32d24799cb03943f06c682b5402a7148c53e561b9  gate summary.json
60dd741f8ef2815755beafa8bb5799f4112af3d94b1b8c4c171bfef28b07e6c1  V2 canonical profiles
```

## HU Regeneration

CPU Slurm job `391105` regenerated the full V2 tree on HU and completed successfully. Its
logged release and gate hashes matched the frozen local values exactly. A direct SSH generation
attempt was allowed to time out only because the helper treats 30 seconds of write-time silence
as a connection timeout; the Slurm job supplied the independent reproducibility check.

## First M1 Run Contract

The transfer repository packages the compact gate, V2 canonical table, and provenance manifest
under `artifacts/datasets/relation_v2_gate_v1/`. Candidate inventories are schema-aware, so old
`synthetic_v1` and V2 profiles can be evaluated without changing the historical pipeline.

The first V2 run starts from base SmolLM2-360M and deliberately reuses the successful earlier
10-subject direct-aware recipe: answer-only loss, learning rate `1e-4`, 36 epochs, batch size
50, and 252 optimizer updates. Evaluation must compare exact-prefix, held-out direct, held-out
QA, and direct/QA robust overlap before any scale-up.

## Deployment Record

- transfer-vs-relearning integration commit: `c154cb4` (`Add relation V2 acquisition gate`);
- GitHub branch: `corpus-update`;
- HU pull: fast-forwarded to `c154cb4`;
- HU preflight: 65/65 tests passed;
- training job: `391106`;
- initial Slurm state: `PENDING`;
- resources: one A100 80GB, 8 CPUs, 64 GB RAM, four-hour allocation cap;
- expected training runtime after start: approximately two minutes, with a safe two-to-five
  minute range based on the matched 350-row / 252-update direct-aware control.

The SSH helper has a 30-second total-call limit, so a combined 25-second test run plus Slurm
submit does not reliably reach the final submit command. The preflight and submit were therefore
run as two explicit operations. This is an orchestration limitation only; it does not alter the
dataset, recipe, or Slurm job.

## Training Result And Duplicate Audit

Canonical job `391106` completed all 252 optimizer updates in 129.6 seconds. Aggregate training
loss was 0.4452 and final held-out validation loss was 0.1082. Its canonical run directory is:

```text
runs/training/m1_smollm2_360m_relation_v2_10_subjects_direct_answer_only/
20260711T221024Z_m1_smollm2_360m_relation_v2_10_subjects_direct_answer_only_lr1e-4_ep36_dc3dff1b
```

The SSH helper returned before two earlier remote commands had finished, but those remote shells
continued. This produced one completed duplicate (`391107`, 122.7 seconds, identical aggregate
training loss) and one non-training failure (`391108`). Job `391108` collided with the duplicate's
same-second run-directory name and exited with `FileExistsError` before training. Neither job is
part of the canonical analysis; all evaluation targets job `391106` only.

## Checkpoint Evaluation Launch

The source exact-prefix CSV contains only the minimal fact columns, while the evaluator requires
branch, frequency, popularity, and name metadata. Before submission, the evaluation launcher
deterministically joined those exact probes with the frozen validation JSONL by `fact_id`. It
also converted the held-out validation prompts into a full evaluator-compatible probe CSV.
No fact, answer, prompt wording, candidate inventory, or training artifact was changed.

Eleven canonical checkpoints were submitted, each evaluating exact-prefix, scaffold-free
held-out direct, and QA-matched views over all 50 facts:

| Checkpoint | Evaluation job |
| ---: | ---: |
| 25 | 391886 |
| 50 | 391887 |
| 75 | 391888 |
| 100 | 391878 |
| 125 | 391879 |
| 150 | 391880 |
| 175 | 391881 |
| 200 | 391882 |
| 225 | 391883 |
| 250 | 391884 |
| 252 | 391885 |

All jobs were initially `PENDING`. Expected parallel wall time after scheduling is about two to
three minutes, with a safe three-to-seven minute range including queue delay. No sleep monitor
is active.

All evaluation jobs subsequently completed. Checkpoint 75 was the earliest aggregate gate pass;
checkpoint 125 was the earliest point on the best stable plateau at 50 exact, 45 direct, 46 QA,
45 direct/QA overlap, and 45 three-view robust facts. Both replacement relations reached 10/10
triple robustness. The five remaining non-robust facts are all `lives_in`; complete analysis and
the resulting scale-up pause are in `69_M1_RELATION_V2_10_SUBJECT_EVALUATION_REPORT.md`.
