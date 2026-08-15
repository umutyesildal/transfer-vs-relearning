# Repository Migration V1

**Status:** In progress; local-only migration branch; not published  
**Branch:** `migration/monorepo-v1`  
**Base:** `transfer-vs-relearning` `corpus-update` at
`9314a02b7a6986d760602002648372d266d04227`

## Objective

Create one canonical project repository without deleting, overwriting, or silently omitting any
existing project material. The migration must preserve both Git histories, the immutable
scientific record, authored paper and study material, operational scripts, local-only evidence,
and user-generated artifacts.

This migration does not authorize HU access, Slurm work, training, evaluation, network downloads,
publication, cleanup, or deletion.

## Preservation Rules

1. The existing `transfer-vs-relearning/`, `syntheticFacts/`, and workspace-root files remain
   untouched until the migrated tree passes count, hash, history, and test verification.
2. Migration is copy/import based. No source path is moved or deleted in V1.
3. The main code history remains the repository spine. The committed synthetic-data history is
   imported under `tools/synthetic-data/` without squashing.
4. Chronological documentation is imported byte-for-byte at its existing `documentation/` paths.
   Historical reports are not rewritten during migration.
5. Secrets, virtual environments, caches, temporary render trees, and large generated datasets
   are never committed. They remain locally preserved and are bound to a private hash inventory.
6. Reference-paper PDFs are copied into the local migrated workspace but remain Git-ignored until
   copyright/license and Git LFS policy are decided. Their authored index/notes remain tracked.
7. No GitHub push or default-branch change occurs during V1.

## Source Inventory Baseline

The private pre-migration inventory excludes every `.git/` directory and the `.migration/`
workspace itself. It records regular-file SHA-256, byte size, mode, and symlink targets.

- inventory SHA-256:
  `0fd8caaf2dcfba1b6aa180875d23748fe03b993f2bc2438fb4ee3bd55fab5dfb`
- regular files: `35,598`
- symlinks: `13`
- directories: `3,669`
- total regular-file bytes: `2,962,980,827`
- secret-local-only files: `1`

The full manifest is local migration evidence and is intentionally outside Git because it includes
the identity of local-only secret and runtime paths.

## V1 Import Map

| Existing source | V1 destination | Git policy |
|---|---|---|
| `transfer-vs-relearning/` tracked tree | repository root | Existing history retained |
| `syntheticFacts/` committed branch | `tools/synthetic-data/` | Full history imported, no squash |
| `syntheticFacts/` untracked outputs | original path, plus private inventory | Never auto-added |
| `documentation/` | `documentation/` | Byte-identical tracked scientific record |
| `AGENTS.md` | `AGENTS.md` | Imported unchanged in V1 |
| `LUNA_WORKER_CURRENT_HANDOFF.md` | same path | Imported unchanged as historical handoff |
| `.agents/` source/config/prompts/schemas/tests | `.agents/` | Tracked control-plane source |
| `.agents/runs/`, `.agents/state/`, `.agents/STOP` | local copy/private inventory | Git-ignored local evidence/state |
| `ssh-client/` scripts and README | `ssh-client/` | Tracked historical operations material |
| `ssh-client/.env` | local copy/private inventory | Git-ignored secret; never printed |
| `paper/` authored source/data/figures | `paper/` | Tracked |
| `paper/` build products | local copy/private inventory | Git-ignored |
| `papers/` notes and index | `papers/` | Tracked |
| `papers/**/*.pdf` | local copy/private inventory | Git-ignored pending distribution policy |
| `study-notes/` | `study-notes/` | Tracked |
| authored presentation files/renders | `presentations/legacy/` | Tracked with source-path ledger |
| workspace `scripts/` | repository `scripts/` | Merged only after collision check |
| `output/`, `outputs/`, `tmp/`, `.tmp/` | original path/private inventory | Local generated material; not committed |
| empty `configs/`, `slurm/`, `src/`, `tests/` | inventory only | Git cannot preserve empty directories |
| main-repo untracked artifacts and `uv.lock` | original path/private inventory | Reviewed separately; never auto-added |

## Verification Gates

V1 is not complete until all of the following pass:

- source Git worktrees still have their exact original branch, HEAD, dirty, untracked, and ignored
  state;
- the synthetic source branch is reachable from the monorepo history and its imported tracked tree
  matches the source tree byte-for-byte;
- every imported workspace file has the same SHA-256 as its source, allowing only documented path
  relocation for presentations;
- secret and generated local-only paths are ignored and absent from the Git index;
- no file larger than the agreed Git publication limit is accidentally staged;
- repository tests pass from a fresh environment or the reason for any unavailable dependency is
  recorded;
- the original two repositories and workspace material remain present after verification.

## Rollback

Rollback means abandoning the migration worktree and branch. Because V1 does not mutate or delete
source material, rollback does not require restoring project files. The worktree and branch must
not be removed until the user separately authorizes that cleanup.
