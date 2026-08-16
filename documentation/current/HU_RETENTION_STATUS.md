# HU legacy retention status

**As of:** 2026-08-16  
**Status:** inventory complete; cleanup proposal not authorized

## Result

The bounded, non-deleting inventory covered the legacy `artifacts`, `runs` and pre-pull backup
roots. It recorded 9,825 files and 742,915,363,463 bytes. The inventory manifest SHA-256 is
`daad386c19a74186f37e1319f7cf07a39161d5571c2478549710d7a25d138966`.

| Root | Files | Bytes |
|---|---:|---:|
| legacy artifacts | 283 | 17,692,941,423 |
| legacy runs | 9,534 | 725,222,410,134 |
| pre-pull backup | 8 | 11,906 |

Post-inventory file counts and byte totals matched all three source roots exactly. No source file,
scientific result, model or training state was changed or deleted.

## Retention classes

- 8,590 scientific-evidence files / 2,030,136,356 bytes are mandatory keep.
- 1,160 model/training-state files occupy 740,885,197,962 bytes.
- 55 cache files occupy only 12,995 bytes; 14 empty markers occupy 14 bytes.
- four incomplete and two review-required evidence files total 16,136 bytes and remain preserved.

The storage issue is therefore not cache. It is historical optimizer and checkpoint state:

| Category | Files | Bytes | Current decision |
|---|---:|---:|---|
| optimizer state | 204 | 432,357,623,753 | 203 proposed only; 1 mandatory preserve |
| checkpoint models | 264 | 259,859,746,176 | review; not a cleanup candidate |
| final models | 34 | 31,798,653,312 | keep pending equivalence review |
| artifact models | 5 | 11,540,113,939 | mandatory keep |
| other model state | 16 | 5,324,504,669 | review |
| scheduler/RNG/small state | 637 | 4,556,113 | keep; negligible size |

## Optimizer proposal

Thirty-four of 36 training namespaces contain both a final model and a manifest. Their exact 203
optimizer paths total 426,066,757,577 bytes and are recorded in a hash-bound proposal list. One
6,290,866,176-byte optimizer belongs to a run without a final model and is explicitly excluded.

This is not deletion authority. Before removing any optimizer, every run needs a selected/frozen
model mapping and a proof that no resume or downstream dependency needs the state. The exact
machine proposal is
[`../../configs/operations/hu_legacy_cleanup_proposal_v1.yaml`](../../configs/operations/hu_legacy_cleanup_proposal_v1.yaml).

## Existing recovery evidence

- the 39 tracked deletions in the legacy checkout remain recoverable from commit `9314a02` and
  `origin/corpus-update`;
- the eight-file, 64 KiB-on-disk pre-pull backup is byte-identical to the current monorepo;
- the verified 24 MiB local Git bundle preserves the complete pre-filter monorepo history;
- Git recovery does not replace the HU raw-run evidence, so `runs` remains protected.

## Current boundary

Use the clean HU monorepo checkout and let the agent perform fast-forward-only pulls. Do not use or
clean the legacy checkout. No optimizer, checkpoint, run, result, model, backup or cache deletion
is authorized by this inventory or proposal.
