# Entrypoint layout v2 migration

**Date:** 2026-08-16 | **Method:** Git renames plus exact active-reference repair

The previously flat roots contained 129 scripts and 135 Slurm files. All 264 files remain present
and are now grouped by scientific state or reusable role. No script or launcher content was
discarded.

## Layout

- `scripts/study/`: current pipeline and full-study control;
- `scripts/training/`, `evaluation/`, `data/`, `corpora/`, `operations/`: reusable entrypoints;
- `scripts/m1/`, `scripts/m2/`: contract-specific and historical state workflows;
- `slurm/m0/`, `slurm/m1/`, `slurm/m2/`: state/family launchers;
- `slurm/study/`: reserved for future frozen full-study adapters.

[`../../configs/entrypoints/catalog.json`](../../configs/entrypoints/catalog.json) is the complete
machine-readable old-path→new-path ledger. Active code, tests, shell launchers and SSH helpers had
683 exact path references repaired. Python namespace/dynamic-path tests were updated separately.

Numbered chronological documents were intentionally not rewritten: their old path strings record
what existed at that historical time. The catalog and Git rename history resolve those names now.
Moving a file does not change its scientific meaning, contract status or authorization.

Validation requires:

- all 264 catalog destinations exist and are unique;
- no catalog old path remains as a live file;
- flat roots contain only their navigation README;
- active operational surfaces contain no unresolved old-path reference;
- the complete offline test suite passes.
