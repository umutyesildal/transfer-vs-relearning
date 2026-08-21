# M0 SmolLM exact-prefix recovery submission — 2026-08-21

## Outcome

The exact SHA-bound SmolLM-only recovery authorization was consumed once. Local publication and
the preservation-checked HU scratch-checkout fast-forward completed at commit
`d827d6c23685cadd106bb76d66025cf54c7d8d73`. The final fail-closed preflight passed with no
blockers before submission.

## Final preflight evidence

- plan ID: `c7f394ed28718e24`;
- authorized runtime config SHA-256:
  `aa862896b333b8a13358a196d70254ee7c47e3e59b026fec0f326247f76022cc`;
- HU-home usage: `14,703,169,536` bytes, below the 30 GiB limit;
- fresh family root: pass;
- 500-probe/100-subject/five-relation input audit: pass;
- zero prompt overlap with robust A–D registry: pass;
- preserved source family-result/inventory hashes: pass;
- retained OLMo and Qwen lane plus artifact hashes: pass;
- all three model manifests and frozen runtime lock: pass;
- clean Git/implementation ancestry and no duplicate job: pass.

## Submitted DAG

- SmolLM array parent: `473844`;
- only array task: `473844_2`;
- array specification: `2`;
- route: exclusive `gpu:a10080gb:1` on `gruenau9`;
- immediate observed state: `RUNNING`;
- family finalizer: `473845`;
- dependency: `afterany:473844`;
- immediate finalizer state: `PENDING (Dependency)`.

The test-only route probe was eligible. Its estimate was `2026-08-22T03:22:31`, but the actual
SmolLM task began on `gruenau9` at `2026-08-21T19:25:32`.

## Immutable submission artifacts

- `family_manifest.json` SHA-256:
  `ed51b84e069389aab876ead51ec58350154d87b3055207ccc7b29eea37e812f7`;
- `route_probe.json` SHA-256:
  `25d8e31531c0b54b63b87dad09bc552020b19b2be650a39b306be4b394cb41e5`;
- `submission_manifest.json` SHA-256:
  `b48c84907f06d253102fe93d2d53d5a339e649860a0044ed712235f9cd2c67fe`.

## Current boundary

This is a submission record, not a completed SmolLM score or a three-model comparison. The single
wave is consumed. No retry, second submission, OLMo/Qwen rerun, normalization, M1/M2 work, cleanup
or deletion is authorized. The next action is read-only monitoring followed by hash verification
of the SmolLM lane and combined family artifacts after finalizer `473845` becomes terminal.
