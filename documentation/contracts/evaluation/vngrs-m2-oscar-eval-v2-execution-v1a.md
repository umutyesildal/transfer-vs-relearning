# vngrs-m2-oscar-eval-v2-execution-v1a

Status: `FROZEN / UNEXECUTED / SINGLE REPAIR AUTHORIZATION REQUIRED`

## Exact failure boundary

V1 preflight job `483719` failed before corpus-row loading because the adapter passed the Parquet
materialization root to `load_source_objects_v3`, while the accepted footer/ledger package is held
under the separate immutable metadata root. Prior root
`/vol/tmp2/yesildau/vnd_m2_oscar_eval_v2_execution_v1` has exactly four files / 80,598 bytes,
zero task result, zero model load and zero evaluation. Jobs `483720` and `483721` are unstarted and
dependency-dead. V1 root and all four files remain read-only and must not be reused or cleaned.

## Single correction

The only adapter semantic change is:

- Parquet bytes and `control/materialization_v3.json` remain read from
  `/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v3`;
- the 32-row accepted source-object ledger is read from
  `/vol/tmp2/yesildau/luna_vngrs_metadata_footer_feasibility_v1/shard_metadata_ledger.jsonl`,
  SHA-256 `6c6f27651945043ec2dfbf1b26575f416b5d38a8783d0a22320f0ffbf83d3fa3`;
- both roots remain read-only and the fresh retry root is
  `/vol/tmp2/yesildau/vnd_m2_oscar_eval_v2_execution_v1a`.

The 63-state scientific matrix, model/checkpoint identities, 10,000 held-out IDs, runtime,
precision, all metrics, gates, bootstrap, Slurm resources and no-automatic-retry rule are unchanged
from V1.

Frozen repair implementation identities:

- execution config SHA-256:
  `d209971308e422716262dff163adce171556d11b6522fe3f742d4aac31fdd801`;
- adapter SHA-256:
  `af201694f6f120d061e4592d71d07854ba23350965705c1d39de8445104f0006`;
- unchanged entrypoint SHA-256:
  `141faf323ee85a4407525b51f6f757afdb749b3ac00b168cd6a8963fcfc5b215`.

## One bounded repair wave

After exact checks, a future separately authorized launcher may cancel only dependency-dead,
never-started jobs `483720` and `483721`; it may then submit exactly one 4-CPU/64G preflight, one
`0-62%6` A100-80GB array and one afterany CPU finalizer/scientific analyzer under the fresh V1A
root. Scheduler test-only checks precede all real submissions.

Training, optimizer updates, checkpoint writes, source/prior-root mutation, cleanup, deletion,
fallback, a second repair wave and automatic retry are forbidden. Publication, HU fast-forward,
job cancellation, Slurm, model inference and evaluation remain unauthorized until the user binds
the final SHA-256 of this contract and the exact implementation commit.
