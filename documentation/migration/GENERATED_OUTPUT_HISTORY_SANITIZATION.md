# Generated-output history sanitization

**Status:** completed locally; not published | **Date:** 2026-08-15
**Scope:** `migration/monorepo-v1` only

## Purpose

Remove generated output data from the monorepo's reachable Git history after explicit user
approval, while retaining a complete recovery route and leaving both original source repositories
unchanged.

## Removed history paths

```text
output/
tools/synthetic-data/output/
```

The filter applied to these complete generated directories, not to source code, configs,
documentation, tests, paper material, or scientific manifests elsewhere in the repository.

## Pre-filter preservation

- branch: `migration/monorepo-v1`
- head: `9b5ab31a891cacbb978ff02122bf1d7ef4e2f0e3`
- commits: `249`
- private bundle:
  `.migration/safety/monorepo-pre-generated-output-filter-9b5ab31.bundle`
- bundle bytes: `24,961,147`
- bundle SHA-256:
  `e1f55503191b19f2dfa230d44311363e079d2d3b7c4efc25899504128de3243b`
- `git bundle verify`: PASS; complete history recorded

The bundle is local migration evidence and is intentionally not committed into the repository.
The original `transfer-vs-relearning` and `syntheticFacts` worktrees also remain unchanged.

## Operation

```bash
git filter-repo --force \
  --refs refs/heads/migration/monorepo-v1 \
  --path output/ \
  --path tools/synthetic-data/output/ \
  --invert-paths
```

This rewrote only the local migration branch. No remote operation or push occurred.

## Result

- immediate filter-result head: `619b0d6342f836bdc91a9c050a1de387eef52850`
- commits: `249`
- pre-filter reachable blobs ≥10 MiB: `8`
- pre-filter bytes in those blobs: `360,973,310`
- post-filter reachable blobs ≥10 MiB: `0`
- tracked files under the removed paths: `0`
- local ignored output copies: restored from the original workspace/source repository
- checksum-aware `rsync --dry-run` after restoration: empty/PASS
- branch worktree status after filtering: clean
- original source worktrees: unchanged

Commit topology remains unsquashed, but rewritten commit IDs differ from the exact imported source
history. Recovery of the pre-filter monorepo is possible from the verified bundle; recovery of the
original synthetic history is also possible from the untouched source repository.

## Authority boundary

This completed cleanup does not authorize:

- push, publication, pull request, merge, or default-branch cutover;
- deletion of the private bundle or original worktrees;
- deletion of local ignored outputs or scientific artifacts;
- HU/SSH, Slurm, evaluation, training, or corpus work.

The machine-readable companion is
[`GENERATED_OUTPUT_HISTORY_SANITIZATION.json`](GENERATED_OUTPUT_HISTORY_SANITIZATION.json).
