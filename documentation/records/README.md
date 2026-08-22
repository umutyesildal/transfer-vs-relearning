# Records

Records preserve what happened. They are not automatically current authority.

## Chronological scientific record

The existing Documents 00–180 remain at `documentation/*.md` so internal links and citations do
not break during the first migration. They include plans, frozen contracts, failed attempts,
results, gates, and append-only corrections.

These numbered records and the legacy gateway files are now default-retired from agent context.
They remain available when the current state or a bounded task cites them; no file was deleted or
moved by the retirement decision.

Do not rewrite them for style or move them casually. A future physical archive reorganization must
use `git mv`, build a link map, run a repository-wide link/citation check, and preserve Git history.

## Preserved workspace guidance

`workspace-guidance/` contains byte-identical copies of the large pre-control-plane README,
AGENTS, agent policy, agent goal, and orchestration README. Their hashes are recorded in
`workspace-guidance/LEGACY_GUIDANCE_MANIFEST.json` and verified by tests.

These files retain all historical instructions and context removed from the active reading set.
They should be opened only for historical investigation.

## Result records

A completed future wave should produce:

- a machine-readable run/result manifest;
- compact normalized tables;
- an immutable human result summary when interpretation is needed;
- a state update pointing to those artifacts.

The result record reports what occurred. It never retroactively edits the contract that defined
what should occur.
