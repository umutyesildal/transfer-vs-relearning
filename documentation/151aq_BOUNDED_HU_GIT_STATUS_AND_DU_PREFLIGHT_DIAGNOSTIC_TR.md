# Document 151aq — Bounded HU Git-Status and Home-Usage Preflight Diagnostic (TR)

**Date:** 2026-08-09 (Europe/Berlin)  
**Worker:** LUNA-Worker 2  
**Status:** `COMPLETED — READ-ONLY OPERATIONAL DIAGNOSTIC`  
**Scope:** one explicitly authorized HU-source-read-only diagnostic; no 151an execution

## 1. Authority and integrity boundary

This report diagnoses the two pre-source blockers recorded in Documents 151ao and 151ap. It
does not rewrite those chronological records and does not convert this diagnostic into a new
151an execution authorization. Documents 151an, 151ao and 151ap were read-only verified before
HU access and remained unchanged:

| File | SHA-256 before and after this task |
|---|---|
| `151an_BOUNDED_VNGRS_ROUTE_FOOTER_BYTE_AND_SAMPLING_SCHEDULE_EVIDENCE_RESOLUTION_CONTRACT_TR.md` | `937ec22c4b0f32d6c15a43ef872e497a0c62266383d46d2e74fca9069f952b79` |
| `151ao_BOUNDED_VNGRS_METADATA_FOOTER_EXECUTION_RESULT_TR.md` | `5b8cb4be094e78f9e37a927348efab4491e5f00355496f2996d1170494dfae46` |
| `151ap_POST_BOUNDED_VNGRS_METADATA_FOOTER_EXECUTION_GATE_TR.md` | `aef81d9b72dd856b802310daaa4c64c7e37089ef22e2527cb6c88bbba8923468` |

Before HU access, the local `corpus-update` HEAD, local `origin/corpus-update`, and live
`git ls-remote origin refs/heads/corpus-update` all resolved to
`c1a3127a4e4c6d9afd3bb0fd06741ce4114ecf23`. The reviewed published range is therefore the
non-force-published `9f1755219ba003d4aaf962558b3c0512fc74f99a..c1a3127a4e4c6d9afd3bb0fd06741ce4114ecf23`
range.

No HU file, Git ref, working-tree entry, scratch root or output file was written. No source or
footer route, corpus row, PyArrow check, executor, retry, scoring, inference, evaluation,
GPU/Slurm or training operation was performed.

## 2. HU checkout identity and status classification

The documented helper ran the read-only command:

```text
git -C /vol/fob-vol6/mi25/yesildau/transfer-vs-relearning status --porcelain=v2 --branch
```

Observed branch identity:

```text
branch.oid      9f1755219ba003d4aaf962558b3c0512fc74f99a
branch.head     corpus-update
branch.upstream origin/corpus-update
branch.ab      +0 -0
```

The `+0 -0` line is relative to the HU checkout's own configured upstream ref; it is not a
statement that this checkout contains the newly published `c1a3127` commit. The HU checkout is
still at the old `9f17552` base.

The diagnostic mechanically parsed 42 porcelain-v2 entries:

| Porcelain class | Count | Meaning |
|---|---:|---|
| `.D` | 39 | tracked path unchanged in the index but deleted in the HU worktree |
| `?` | 3 | untracked top-level/path entries, collapsed by the default porcelain-v2 untracked-directory display |
| **Total** | **42** | **dirty entries** |

There were no tracked modifications, additions or renames in the captured status set. The three
untracked entries were not recursively read:

```text
? .codex_pre_pull_backup_20260707T142553Z/
? artifacts
? runs
```

The 39 tracked `.D` entries were:

```text
artifacts/analysis/m1_acquisition_500_facts_direct_checkpoint-250/README.md
artifacts/analysis/m1_acquisition_500_facts_direct_checkpoint-250/summary.json
artifacts/analysis/m1_acquisition_500_facts_direct_checkpoint-250/triple_robust_facts.csv
artifacts/corpora/.gitkeep
artifacts/corpora/trwiki_20260601/audited/.gitkeep
artifacts/corpora/trwiki_20260601/contamination/.gitkeep
artifacts/corpora/trwiki_20260601/deduplicated/.gitkeep
artifacts/corpora/trwiki_20260601/extracted/.gitkeep
artifacts/corpora/trwiki_20260601/filtered/.gitkeep
artifacts/corpora/trwiki_20260601/manifests/.gitkeep
artifacts/corpora/trwiki_20260601/normalized/.gitkeep
artifacts/corpora/trwiki_20260601/raw/.gitkeep
artifacts/corpora/trwiki_20260601/reports/.gitkeep
artifacts/corpora/trwiki_20260601/splits/.gitkeep
artifacts/datasets/.gitkeep
artifacts/datasets/relation_v2_binding_control_v1/manifest.json
artifacts/datasets/relation_v2_binding_control_v1/train.jsonl
artifacts/datasets/relation_v2_gate_v1/README.md
artifacts/datasets/relation_v2_gate_v1/acquisition_100_subjects_direct/exact_prefix_probes_en.csv
artifacts/datasets/relation_v2_gate_v1/acquisition_100_subjects_direct/summary.json
artifacts/datasets/relation_v2_gate_v1/acquisition_100_subjects_direct/train.jsonl
artifacts/datasets/relation_v2_gate_v1/acquisition_100_subjects_direct/validation.jsonl
artifacts/datasets/relation_v2_gate_v1/acquisition_10_subjects_direct/exact_prefix_probes_en.csv
artifacts/datasets/relation_v2_gate_v1/acquisition_10_subjects_direct/pilot.json
artifacts/datasets/relation_v2_gate_v1/acquisition_10_subjects_direct/summary.json
artifacts/datasets/relation_v2_gate_v1/acquisition_10_subjects_direct/train.jsonl
artifacts/datasets/relation_v2_gate_v1/acquisition_10_subjects_direct/validation.jsonl
artifacts/datasets/relation_v2_gate_v1/acquisition_500_subjects_direct/exact_prefix_probes_en.csv
artifacts/datasets/relation_v2_gate_v1/acquisition_500_subjects_direct/summary.json
artifacts/datasets/relation_v2_gate_v1/acquisition_500_subjects_direct/train.jsonl
artifacts/datasets/relation_v2_gate_v1/acquisition_500_subjects_direct/validation.jsonl
artifacts/datasets/relation_v2_gate_v1/data/canonical_subject_profiles_5000.csv
artifacts/datasets/relation_v2_gate_v1/manifest.json
artifacts/datasets/synthetic_v1/manifest.json
artifacts/datasets/synthetic_v1/pilot_100_subjects.json
artifacts/datasets/synthetic_v1/validation_summary.json
artifacts/datasets/synthetic_v1/validation_summary.md
artifacts/models/.gitkeep
runs/.gitkeep
```

The status paths are artifact/run paths only. They do not expose source contents or corpus text
in this report.

## 3. Published change-set overlap

The exact local read-only comparison was:

```text
git diff --name-only 9f1755219ba003d4aaf962558b3c0512fc74f99a c1a3127a4e4c6d9afd3bb0fd06741ce4114ecf23
```

It returned 13 paths:

```text
src/transfer_vs_relearning/corpora/vngrs/__init__.py
src/transfer_vs_relearning/corpora/vngrs/contamination.py
src/transfer_vs_relearning/corpora/vngrs/dedup.py
src/transfer_vs_relearning/corpora/vngrs/manifest.py
src/transfer_vs_relearning/corpora/vngrs/metadata.py
src/transfer_vs_relearning/corpora/vngrs/metadata_executor.py
src/transfer_vs_relearning/corpora/vngrs/outputs.py
src/transfer_vs_relearning/corpora/vngrs/pipeline.py
src/transfer_vs_relearning/corpora/vngrs/quality.py
src/transfer_vs_relearning/corpora/vngrs/records.py
src/transfer_vs_relearning/corpora/vngrs/sampling.py
src/transfer_vs_relearning/corpora/vngrs/split.py
tests/test_vngrs_preparation.py
```

Set intersection between all 42 HU status paths and these 13 published paths:

```text
overlap_count = 0
overlap_paths = []
```

This is useful evidence for a future owner-controlled fast-forward review, but it is not
permission to mutate the dirty HU checkout. The 39 tracked deletions and three untracked
top-level entries still require explicit preservation/reconciliation.

## 4. Exact home-usage and filesystem preflight evidence

The executor implementation freezes `COMMAND_TIMEOUT_SECONDS = 30` and its mandatory human-size
command as `du -xsh /vol/fob-vol6/mi25/yesildau`. The diagnostic used a read-only in-memory Python
capture with GNU `timeout 30` around each exact `du` form; the inner command, timeout, exit code and
captured stream byte counts are the evidence below. No output was redirected to a HU file.

| Inner command | Bound | Exit | Timed out | stdout bytes | stderr bytes | Numeric result |
|---|---:|---:|---|---:|---:|---|
| `du -xsh /vol/fob-vol6/mi25/yesildau` | 30 s | 0 | no | 32 | 0 | `14G` parseable; byte-form is authoritative |
| `du -x -B1 -s /vol/fob-vol6/mi25/yesildau` | 30 s | 0 | no | 40 | 0 | `14687617024` bytes |

Exact captured streams:

```text
human stdout = b'14G\\t/vol/fob-vol6/mi25/yesildau\\n'
human stderr = b''
byte stdout  = b'14687617024\\t/vol/fob-vol6/mi25/yesildau\\n'
byte stderr  = b''
```

A supplemental five-second sensitivity probe of the human-size form returned exit `124`,
stdout `0` bytes and stderr `0` bytes. The bounded 30-second rerun completed with the evidence
above. This establishes that the earlier no-output observation in 151ao/151ap was not a current
numeric usage value; it does not erase the historical preflight result. The current diagnostic
classifies the 30-second checks as successful and parseable, not as a permission or stderr-only
failure.

The accompanying read-only capacity/inode/path checks returned:

```text
df -h
  /vol/fob-vol6: 1.3T total, 667G used, 611G available, 53%
  /vol/tmp:      140T total, 122T used, 18T available, 88%
  /vol/tmp2:     140T total, 27T used, 113T available, 19%

df -i
  /vol/fob-vol6: 334561280 total, 174652962 used, 159908318 free, 53%
  /vol/tmp:      2344153088 total, 69482815 used, 2274670273 free, 3%
  /vol/tmp2:     2343983104 total, 59509423 used, 2284473681 free, 3%

readlink -f runs     = /vol/tmp/yesildau/transfer-vs-relearning/runs
readlink -f artifacts = /vol/tmp/yesildau/transfer-vs-relearning/artifacts
readlink -f 151an root = /vol/tmp2/yesildau/luna_vngrs_metadata_footer_feasibility_v1
151an root existence  = ABSENT
```

The 151an scratch root was not created by this diagnostic.

## 5. Corrected operational interpretation

The current exact `du` blocker is closed as an isolated preflight component: both the mandated
human-size form and the GNU byte-form returned successful, parseable output. The operational
execution gate is nevertheless still `blocked_by_operational_access` because the HU checkout is
at the old `9f17552` base and has 42 dirty entries whose preservation has not been authorized or
performed. The global gate remains `blocked_by_measurement_design`; `ready_to_measure` and
`ready_to_train` remain false.

This diagnostic provides no source/footer feasibility result, no corpus evidence, no benchmark
result and no scientific measurement. It does not authorize a new 151an execution, source access,
PyArrow, row sampling, corpus materialization, scoring, evaluation, model/tokenizer access,
GPU/Slurm or training.

## 6. Safest separately authorized remediation (not executed)

The safest next operational path is owner-controlled and reversible:

1. Preserve the complete 42-entry HU state outside any Git mutation, with the three untracked
   top-level identities and all tracked deletion identities retained as an owner-reviewed
   inventory/backup. This report did not create that backup.
2. Have the owner explicitly classify whether the 39 tracked deletions and three untracked
   directories are intentional, and confirm that no preserved entry may be discarded.
3. Only after that confirmation, separately authorize a non-destructive fast-forward of the HU
   checkout to `c1a3127…` (or an owner-selected clean scratch checkout pinned to that commit),
   with no `reset`, `clean`, `restore`, deletion or overwrite. The measured zero path overlap is
   evidence supporting review of a fast-forward, not a substitute for owner authorization.
4. Repeat the mandatory storage/path/inode preflight and independent-writer self-check, then
   request a separate, explicit one-time 151an execution only if all fail-closed prerequisites
   pass.

No part of this remediation was executed in the present task. In particular, no HU Git command
that changes state, no checkout/scratch-root creation and no 151an retry occurred.

## 7. Final gate and preserved records

```text
Document 151aq diagnostic: COMPLETED — READ-ONLY
151an new execution: NOT AUTHORIZED / BLOCKED BY OPERATIONAL ACCESS
primary gate: blocked_by_operational_access
global gate: blocked_by_measurement_design
ready_to_measure: false
ready_to_train: false
```

Documents 151an, 151ao and 151ap remain preserved unchanged. The next authorization, if desired,
must separately authorize only the owner-controlled HU reconciliation/preflight path described in
Section 6; it must not be inferred from this diagnostic.
