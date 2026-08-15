# Document 151ap — POST-EXECUTION DECISION GATE FOR 151an (TR)

## 1. Gate decision

Document 151an’s single authorized wave is closed fail-closed at the HU synchronization and
preflight stage.

```text
decision                         = BLOCKED
operational_gate                 = blocked_by_operational_access
operational_reasons              = {blocked_by_hu_checkout_dirty_or_unsynchronized,
                                     blocked_by_storage_preflight_parse}
global_gate                      = blocked_by_measurement_design
contributing_scientific_gate     = blocked_by_corpus_selection_or_materialization
ready_to_measure                 = false
ready_to_train                   = false
```

## 2. Evidence basis

Document 151an was verified unchanged at SHA-256
`937ec22c4b0f32d6c15a43ef872e497a0c62266383d46d2e74fca9069f952b79`. The reviewed executor was
published without force-push as the exact three-commit fast-forward ending at
`c1a3127a4e4c6d9afd3bb0fd06741ce4114ecf23`, but the HU checkout remained dirty at the old base
`9f1755219ba003d4aaf962558b3c0512fc74f99a` with 42 status entries. Pulling it would risk
overwriting unrelated HU work and was correctly not attempted.

The mandatory preflight also failed closed because both the human-readable and byte-form `du`
checks returned no parseable home-usage value. Capacity/inode and resolved-path checks were
observed, and the frozen root
`/vol/tmp2/yesildau/luna_vngrs_metadata_footer_feasibility_v1` remained absent. The no-write
post-attempt audit found no new root, no output files and no large new HU-home file.

## 3. What this gate does and does not establish

The result establishes only that this authorized wave could not safely reach the source-access
stage. It does not establish that the vngrs immutable routes, Parquet footers, license bytes,
response bounds or metadata feasibility are unavailable. There are zero request, retry, response,
footer, license, manifest or artifact measurements from this attempt.

The 151an operational evidence component therefore remains unresolved. The primary active gate is
`blocked_by_operational_access`; the global scientific gate remains
`blocked_by_measurement_design`. A successful future 151an metadata/footer wave could address
only its narrow route/footer/byte feasibility scope and could not authorize corpus materialization,
sample calibration, scoring, evaluation, training or `ready_to_train`.

## 4. Conditions for any future authorization

No automatic retry is authorized by this document. Before a separately authorized new wave:

1. the HU checkout owner must reconcile the 42 dirty status entries without deleting or
   overwriting unrelated work;
2. HU `corpus-update` must be synchronized to the published reviewed commit
   `c1a3127a4e4c6d9afd3bb0fd06741ce4114ecf23` using a clean non-destructive fast-forward;
3. the mandatory home-usage `du` result must be byte-parseable and satisfy the frozen storage
   rules;
4. the independent PyArrow-writer self-check must pass on the synchronized executor before any
   public request; and
5. a new explicit authorization must name the unchanged Document 151an SHA and permit one
   bounded execution only.

All prior evidence roots remain immutable/read-only. Corpus rows, full shards, model/tokenizer
weights or snapshots, scoring, inference, evaluation, GPU/Slurm, training, cleanup/deletion and
Documents 152–154 remain forbidden.
