# M1 matched three-model training wave v1

**Status:** frozen, unexecuted, unauthorized

This contract opens exactly one matched M1 training family for the frozen OLMo, Qwen and SmolLM
M0 identities. It does not authorize itself.

## Scientific identity

- Relation V2: 100 subjects, 500 facts, 3,500 English factual rows;
- seed 42, 36 epochs, 252 updates, effective batch 500;
- answer-only objective, sequence length 128, LR `5e-5`, BF16 and frozen per-model microbatch;
- parent plus every epoch end: 37 states/model, 111 future evaluation states;
- every epoch records fact exposure, tokens, loss, LR, gradient norm and a model-only snapshot;
- successful training must produce hash-closed training/checkpoint/model manifests.

## One-wave DAG

```text
CPU identity/data/storage preflight
  -> A10080 array 0-2%3: OLMo | Qwen | SmolLM
  -> afterany family audit
```

The preflight requires the fresh root
`/vol/tmp2/yesildau/m1_matched_three_model_v1`, exact checkout commit, exact config/data/model
manifest hashes and at least 60,000,000,000 free scratch bytes. All model access is offline and HU
home writes are forbidden. A failed model is recorded as missing; there is no automatic retry.

## Scope boundary

This is the training wave only. It creates the immutable 111-state checkpoint input layer required
by the already frozen eval-v2 policy. It does not run evaluation, normalization, M2, cleanup or
publication. The checkpoint-evaluation wave must consume the produced hashes under its own exact
contract; it may be prepared while training runs but cannot invent missing states.

## Authorization rule

Publication to HU and one submission require a new explicit user authorization naming the final
SHA-256 of this contract and its companion config. Old M0 or read-only authorizations are invalid.
