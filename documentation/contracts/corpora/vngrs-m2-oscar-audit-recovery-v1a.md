# vngrs M2 lowercase OSCAR audit recovery contract v1a

**Status:** `FROZEN / UNEXECUTED — SINGLE DIAGNOSTIC CPU RETRY`

**Owner:** thesis project

**Created:** 2026-08-29

**Predecessor:** `vngrs-m2-oscar-audit-recovery-v1`

**Predecessor result:** `documentation/182_VNGRS_OSCAR_AUDIT_RECOVERY_V1_EXECUTION_RESULT_TR.md`

## Purpose

Correct only the exact candidate-label case mismatch exposed by job `481863`. V1 froze
`corpus == "OSCAR"`; the preserved exact label inventory proves that the release uses lowercase
`oscar`. V1a changes the predicate to exact `corpus == "oscar"` and routes the diagnostic output
to a fresh root. No quality, contamination, threshold, source, resource or authority rule changes.

This remains a diagnostic audit-recovery pass, not D0 Phase 1 and not a training-ready corpus
builder. It must stop after exact label inventory, bounded OSCAR-only audit evidence and terminal
recovery state. It creates no split, review packet or tokenizer accounting.

## Preserved read-only evidence

V3 source:

```text
/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v3

control/materialization_v3.json
  SHA-256 bb413e9acafd0d891ea9c4461abc77acea1c737489560650db56dacf781dbd10

control/d0_failure.json
  SHA-256 a341e4787e38720f27beeaf5815331ef0163084cb2974d91799ee5ffe426c52f
```

V1 recovery evidence:

```text
/vol/tmp2/yesildau/vngrs_m2_oscar_audit_recovery_v1

reports/corpus_label_inventory.json
  SHA-256 178991f311336a4acead1bb00fe8043d60a18c590e809b11629ca64f4920ee2b

control/d0_failure.json
  SHA-256 6ce9a5dfc302498e4713ed03293962ca53f40f97daef28ffeea49d8fbc2e813b
```

Both roots and HU home remain read-only. Every V3 raw Parquet object is size- and SHA-revalidated
against the preserved materialization manifest. The pass performs no HTTP request, download,
copy, hard-link, move, resume, rewrite, cleanup or deletion.

## Single corrected predicate

```text
field: corpus
operator: exact_string_equality
value: oscar
```

The predecessor inventory already observes:

```text
documents: 354,482
UTF-8 bytes: 1,553,923,133
```

V1a must independently reproduce the exact labels during execution and requires more than 10,000
selected documents. It does not case-fold, alias, broaden or fall back to mC4. Any drift stops the
pass fail-closed.

## Audit evidence and terminal meaning

The existing Relation V2 exact and Unicode-normalized contamination surfaces, regex groups and
normalized duplicate semantics remain unchanged. Before applying the audit gate, the pass writes:

```text
reports/corpus_label_inventory.json
reports/lightweight_audit.json
```

The audit report preserves exact counts and at most 256 deterministic examples per contamination
hit kind. It therefore identifies exact contamination, normalized contamination, invalid encoding
or any combination without an unbounded artifact.

It then writes `control/recovery_state.json`. `OSCAR_AUDIT_COMPLETE` means only that this diagnostic
audit gate passed; `BLOCKED` preserves the exact reasons. Both states keep `ready_to_train=false`.
No exclusion policy, threshold change, automatic repair or later-stage authorization is implied.

## Fresh output root

Only this absent root may be created:

```text
/vol/tmp2/yesildau/vngrs_m2_oscar_audit_recovery_retry_v1
```

On a preflight/runtime exception, `control/d0_failure.json` is written fail-closed. Existing
evidence is never overwritten.

## Resource and execution bounds

- one standard CPU allocation;
- 8 requested CPUs, 128 GiB RAM, 12-hour walltime;
- at least 2 GiB free scratch and 1,024 free inodes;
- offline Hugging Face/Transformers mode and no Python bytecode writes;
- one `sbatch --test-only`, then exactly one real job;
- zero duplicate `vngrs-m2-oscar-audit-v1a` jobs;
- no automatic retry.

## Exact implementation route

```text
config:    configs/corpora/vngrs_m2_oscar_audit_recovery_v1a.yaml
operator:  transfer_vs_relearning.corpora.vngrs.d0_oscar_recovery
runner:    scripts/corpora/run_vngrs_m2_oscar_audit_recovery_v1a.py
submitter: scripts/corpora/submit_vngrs_m2_oscar_audit_recovery_v1a.sh
Slurm:     slurm/m2/audit_vngrs_m2_oscar_d0_v1a.slurm
job name:  vngrs-m2-oscar-audit-v1a
```

## Authority boundary

This local preparation does not authorize publication/push, HU synchronization or SSH, Slurm,
corpus read, split/review creation, tokenizer/model access, evaluation, training, cleanup or
deletion.

One later exact SHA-bound user authorization may permit only ordinary non-force push of the
reviewed commit, preservation-checked HU fast-forward, focused tests/preflight, and this single
lowercase-label diagnostic CPU retry. It does not authorize another attempt, Phase 2, M2-A/M2-B
training, cleanup or automatic retry.
