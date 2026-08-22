# eval-v2 M0 metric normalization v1a

**Lifecycle:** operator implemented and locally testable; normalization execution unexecuted

**Execution authorized:** no

This is the operational follow-up to `eval-v2-m0-metric-normalization-v1`. It preserves that
contract’s source identities, lane mapping, missingness policy and zero-rescore rule, and binds the
first fail-closed implementation. It does not authorize HU access, normalization output, metric
interpretation or M1/M2 work.

## Bound implementation

| file | SHA-256 |
| --- | --- |
| `src/transfer_vs_relearning/study/m0_metric_normalization.py` | `650fe0ebaf5e5d563dc51631e89e4b0978d2f9fba5ecd2ff705216100ddb0c69` |
| `scripts/study/normalize_m0_eval_v2.py` | `79772ab237061c29a635fcc5303c330af2387f889681d339cdb18c3ffc984427` |

The operator has two explicit modes:

- `audit`: reads and verifies the completed v1b projection and its declared JSON artifacts, then
  reports missing/ambiguous metric keys without writing an output root;
- `normalize`: requires both execution flags in the frozen config and writes only a fresh root
  after a complete audit pass.

Any source artifact with zero or multiple matches for a required metric alias blocks the audit.
The implementation never guesses between repeated subgroup values, invents missing metrics,
loads a model, rescored a lane, or computes new bootstrap/significance values.

## Remaining execution boundary

The v1a config must remain `execution_authorized: false` and `normalization_authorized: false`
until an exact SHA-bound authorization is supplied. Before that authorization, an `audit` pass may
be used to validate the source adapter, but it must not write the normalization root. A successful
normalization pass produces the six files specified by the parent contract and a terminal
`normalization_complete_pending_m0_interpretation` manifest. It does not apply scientific gates or
select a primary model.
