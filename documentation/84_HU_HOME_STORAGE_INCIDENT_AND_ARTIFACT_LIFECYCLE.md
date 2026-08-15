# HU Home Storage Incident And Artifact Lifecycle

## Incident

On 13 July 2026, the HU Rechnerbetriebsgruppe reported that
`/vol/fob-vol6/mi25/yesildau` occupied approximately 474 GB. The shared student fileserver is
planned around an average allocation of approximately 10 GB per student. According to the
administrator, processes from this project filled the server over the weekend and contributed to
a service outage.

This incident also explains the observed 100% capacity and 100% inode state on `/vol/fob-vol6`
during the SmolLM2-1.7B capacity-control launch. At that point even Git could not update
`.git/FETCH_HEAD`.

Official references supplied by the administrator:

- `https://www.informatik.hu-berlin.de/de/org/rechnerbetriebsgruppe/dienste/fileserver`
- `https://www.informatik.hu-berlin.de/de/org/rechnerbetriebsgruppe/dienste/hpc/hpcfileserver`

## Root Cause

The project treated the backed/shared home fileserver as a training-artifact store. Repeated M1
runs retained every intermediate Hugging Face checkpoint, including optimizer state required only
for training resumption.

A representative completed 360M checkpoint occupied approximately 2.1 GB:

```text
model.safetensors  ~691 MB
optimizer.pt       ~1.4 GB
other state        small
```

The canonical 36-epoch run alone retained eleven such checkpoints. The repository contains many
training families and hundreds of evaluation directories accumulated during diagnosis and recipe
development. The problem is therefore artifact retention and storage placement, not the scientific
dataset or a single anomalously large model.

## Immediate Containment

The active 1.7B training and evaluation family was already redirected to
`/vol/tmp2/yesildau/m1_relation_v2_1_7b_500` before this email was received. Its configs, logs,
caches, checkpoints, and evaluator outputs do not write to the home fileserver. The active
evaluation jobs use checkpoints and configs under `/vol/tmp2`; moving the old repository `runs`
tree does not invalidate them.

Migration job `394069` was submitted on the `longrun` partition and confirmed `RUNNING` on
`gruenau`. It uses `rsync -a --remove-source-files` to move:

```text
/vol/fob-vol6/mi25/yesildau/transfer-vs-relearning/runs/
-> /vol/tmp/yesildau/transfer-vs-relearning/runs/
```

Each source file is removed only after rsync has successfully written it to the destination. The
operation is restartable. After all files move, empty source directories are removed and the
original repository path is replaced with a symlink to `/vol/tmp`, preserving existing script and
documentation paths. No scientific result has been deleted.

## Required Follow-Up

The migration is not considered complete until all of the following are verified:

1. Job `394069` completes with empty stderr and a successful rsync summary.
2. The original `runs` path resolves to the `/vol/tmp` destination.
3. Home usage is measured again and reported to the administrator/user.
4. Remaining large consumers are audited, especially `.conda`, model snapshots, caches, old
   backups, and the synthetic-data repository.
5. Reproducible model snapshots and caches are moved to temporary storage if home remains materially
   above the expected allocation.
6. Launchers are changed so future large outputs default to `/vol/tmp` rather than repository-local
   paths on `/vol/fob-vol6`.

## Artifact Retention Policy

From this incident onward:

- Home storage is for source code, small configs, manifests, documentation, and compact summary
  tables only.
- Training checkpoints, optimizer states, model snapshots, caches, generated corpora, and raw
  evaluation outputs belong under `/vol/tmp` or another approved HPC scratch filesystem.
- Active runs may retain resumable optimizer state while training is in progress.
- Completed runs retain model-only checkpoints needed for comparison; unnecessary `optimizer.pt`,
  scheduler, RNG, and duplicate final-model copies are removed or archived outside home.
- The best/final checkpoint and compact evaluation outputs must be identified before bulk cleanup.
- Storage location and retention actions must be written into each run report.
- Home usage must be checked before and after every new scale-up family.

## Final Status

- `/vol/fob-vol6` recovered from 100% to approximately 79% filesystem usage before migration began.
- Initial broad `runs` migration job `394069` ran for approximately 1 hour 45 minutes. Its rsync
  output did not report incremental progress, but a file-level audit after cancellation showed
  that it had already moved approximately 410 GB of the original 474 GB home footprint. The job
  was cancelled to replace the slow broad metadata walk with a targeted completion pass.
- Remaining measured home-resident data after the initial pass was approximately 59-60 GiB:
  38.46 GiB training runs, 10.09 GiB repository artifacts, 7.48 GiB Conda, 2.62 GiB cache, and
  0.39 GiB synthetic-data repository content.
- Targeted completion job `396071` ran on the `std` partition to move the remaining `runs` tree and
  `.cache` to `/vol/tmp`, then restore their original paths with symlinks.
- Job `396071` completed successfully with empty stderr. It transferred approximately 38.40 GB of
  remaining runs and 2.81 GB of cache. Both original home paths now resolve through verified
  symlinks to `/vol/tmp`.
- All 33 1.7B evaluator outputs completed before the artifact move.
- Artifact migration job `397819` completed successfully with empty stderr. It transferred all 242
  regular artifact files, totaling 10.83 GB, and replaced the repository artifact path with a
  verified symlink to `/vol/tmp/yesildau/transfer-vs-relearning/artifacts`.
- Final measured home-resident regular-file total: **7.88 GiB**, below the approximately 10 GB
  average allocation stated by the administrator.
- No completed experiment result has been deleted.
- Large training, evaluation, cache, model, and dataset artifacts now live on scratch storage while
  their established repository paths continue to work through symlinks.

## 30 July 2026 storage-policy clarification

Ralf Moritz subsequently confirmed in writing that current usage below 30 GB in the user's HU
home is acceptable. He explicitly authorized copying the additional approximately 6.2 GB
represented by the two frozen selected Qwen thesis models from `/vol/tmp2` into home. He also
confirmed that `/vol/tmp` and `/vol/tmp2` have no backup or retention guarantees and recommended
chair-provided storage or HU-Box for an additional backup.

This changes only selected-artifact durability: ordinary checkpoints, optimizer state, run trees,
datasets, caches, logs, and evaluation sweeps remain scratch-only. Job `439465` created the
verified model-only home archive under
`/vol/fob-vol6/mi25/yesildau/frozen-models/qwen_m1_selected_v1`; post-copy home use is approximately
14 GiB, below the new 30-GB ceiling. See Document 127 for artifact and manifest hashes.
