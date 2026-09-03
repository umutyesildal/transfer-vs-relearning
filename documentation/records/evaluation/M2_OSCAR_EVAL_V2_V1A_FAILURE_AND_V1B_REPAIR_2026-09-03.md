# M2 OSCAR eval-v2 V1A failure and V1B repair

Date: 2026-09-03  
State: `V1A OPERATIONAL NOT-RUN / V1B FROZEN UNEXECUTED`

## V1A publication and submission

The exact V1A contract SHA-256
`e152dab3ecfb3b54540716b0fd0d7046276c0d8d930797757e66f05616786541` and commit
`bc3d4f7dcb36bdc7c865b6092a0d9f722c9f8ca8` were authorized by the user. The commit was
ordinary non-force pushed and the clean HU checkout was preservation-checked and fast-forwarded.
The HU focused and compatibility suite passed 23/23. The preserved V1 dependency-dead jobs
`483720/483721` were cancelled only after the contract's exact checks passed.

The one real V1A DAG was submitted as preflight `483826`, evaluation array `483827` and afterany
finalizer `483828`. Earlier typo-bearing launcher invocations stopped during local argument/path
resolution, before root creation or Slurm submission, and therefore created no additional wave.

## Fail-closed result

Preflight `483826` stopped before held-out materialization, GPU allocation, model load or scoring:

```text
KeyError: 'output'
materialize_oscar_heldout: root = Path(config["output"]["root"])
```

The function received the canonical task matrix, whose output field is top-level `output_root`.
The V1A root `/vol/tmp2/yesildau/vnd_m2_oscar_eval_v2_execution_v1a` contains exactly four files /
80,453 bytes and zero result files. Exact evidence hashes are:

- submission manifest: `208969264b553afe4e0f09e57443848e9dc1783d3ededec791151704a9f92928`;
- task matrix: `be232e6c87033836cb4b0c7c2777eb64799600d554d91d26bf9333effc594b3b`;
- stderr: `8ffb3d97834280ff13943cbf32af15fc9d814f035029454fafa14583c410d9fc`;
- empty stdout: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

Array `483827` is `DependencyNeverSatisfied`; finalizer `483828` is dependency-pending. Both are
never-started and no cancellation is authorized by this preparation record.

## V1B correction

V1B changes only the held-out materializer's root lookup from preparation-config shape
`config["output"]["root"]` to canonical-matrix shape `config["output_root"]`. A regression test
binds that invariant. Every scientific identity, denominator, metric, threshold, checkpoint,
runtime and Slurm resource remains identical to V1A. The new root
`/vol/tmp2/yesildau/vnd_m2_oscar_eval_v2_execution_v1b` must be fresh.

The frozen V1B contract is
`documentation/contracts/evaluation/vngrs-m2-oscar-eval-v2-execution-v1b.md`, SHA-256
`f05ff162e9b5288b693a2e8ad7b0f9b64a3e51b102f12458fa03ffdccfb7b7aa`. Its preparation
does not authorize push, HU fast-forward, cancellation, Slurm/GPU, inference, evaluation, cleanup,
deletion or retry. Those actions require one new exact contract-SHA and commit-bound user
authorization.
