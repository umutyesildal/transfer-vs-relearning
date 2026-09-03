# vngrs-m2-oscar-eval-v2-execution-v1b

Status: `FROZEN / UNEXECUTED / SINGLE SCHEMA-REPAIR AUTHORIZATION REQUIRED`

## Exact V1A failure boundary

V1A CPU preflight job `483826` passed the corrected Parquet/metadata-root binding and then stopped
before held-out corpus materialization because `materialize_oscar_heldout()` received the canonical
task matrix but attempted to read the preparation-config shape `config["output"]["root"]`. The
canonical matrix deliberately stores that same path as top-level `output_root`; Python therefore
raised `KeyError: 'output'`.

The preserved V1A root `/vol/tmp2/yesildau/vnd_m2_oscar_eval_v2_execution_v1a` has exactly four
files / 80,453 bytes, zero task results, zero model loads and zero evaluation results. Its frozen
identities are:

- submission manifest SHA-256:
  `208969264b553afe4e0f09e57443848e9dc1783d3ededec791151704a9f92928`;
- task matrix SHA-256:
  `be232e6c87033836cb4b0c7c2777eb64799600d554d91d26bf9333effc594b3b`;
- preflight stderr SHA-256:
  `8ffb3d97834280ff13943cbf32af15fc9d814f035029454fafa14583c410d9fc`.

Array `483827` and finalizer `483828` never started and are dependency-dead. The V1 and V1A roots
and all their files remain immutable/read-only and must not be reused or cleaned.

## Single correction

The only adapter semantic change is:

```python
# V1A
root = Path(config["output"]["root"])

# V1B
root = Path(config["output_root"])
```

This makes held-out materialization consume the same canonical matrix schema already used by
`preflight`, `run_task`, `finalize` and `submit`. The separated immutable OSCAR Parquet and metadata
roots, exact 10,000 held-out IDs, 63-state matrix, model/checkpoint identities, runtime, FP16,
metrics, gates, bootstrap, Slurm resources and no-automatic-retry rule remain unchanged.

The fresh V1B root is `/vol/tmp2/yesildau/vnd_m2_oscar_eval_v2_execution_v1b`.

Frozen implementation identities:

- execution config SHA-256:
  `7f407acbc7a5f4098bd0a55d856423c7bbfac42defb073da2a3467ba598803e9`;
- adapter SHA-256:
  `b37734b58239b0e4517c9909984dacb506c39f0ed54e73741f943dcbeb952e3b`;
- unchanged entrypoint SHA-256:
  `141faf323ee85a4407525b51f6f757afdb749b3ac00b168cd6a8963fcfc5b215`.

## One bounded V1B wave

After exact pending/never-started, zero-result, source-root, fresh-root, storage, commit, contract,
config and implementation checks, a future separately authorized launcher may cancel only jobs
`483827` and `483828`. It may then submit exactly one 4-CPU/64G preflight, one `0-62%6`
A100-80GB evaluation array and one afterany CPU finalizer/scientific-analysis job under the fresh
V1B root. Scheduler test-only checks must precede every real submission.

Parent and checkpoint models may be accessed only read-only for the frozen inference tasks.
Training, optimizer updates, checkpoint writes, source/prior-root mutation, cleanup, deletion,
fallback, a second V1B wave and automatic retry are forbidden. Publication, HU fast-forward, job
cancellation, Slurm, model inference and evaluation remain unauthorized until the user binds the
final SHA-256 of this contract and the exact implementation commit.
