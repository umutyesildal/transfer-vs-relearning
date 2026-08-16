# XNLI Harness compatibility incident

**Project decision:** excluded from the active evaluation protocol on 2026-08-16  
**Upstream status:** reproducible compatibility issue; no upstream patch submitted yet

## Scope

This note is the only prospective reference for the removed XNLI integration. XNLI is not an
active eval-v1 task, does not appear in the machine-readable registry, has no local task overlay and
must not be inserted into M0/M1/M2 evaluation commands. Historical v3/v4 qualification artifacts
remain immutable evidence.

## Reproduction identity

- LM Evaluation Harness: v0.4.12, commit
  `6d642546f4688648fced259eb3302efd36ece5af`;
- Python 3.11.15, Torch 2.6.0+cu124, Transformers 5.13.0, Datasets 5.0.0 and
  Hugging Face Hub from the locked qualification environment;
- upstream common task YAML uses the single-segment dataset path `xnli`;
- the Hub resolves the current official dataset under `facebook/xnli`, observed revision
  `b8dd5d7af51114dbda02c0e3f6133f332186418e`.

The v3 online materializer failed before model load or scoring with:

```text
huggingface_hub.errors.HfUriError: Invalid HF URI
'hf://datasets/xnli@b8dd5d7af51114dbda02c0e3f6133f332186418e/.huggingface.yaml'.
Repository id must be 'namespace/name', got 'xnli'.
```

The exact stderr is preserved at:

```text
/vol/tmp2/yesildau/eval_v1_m0_olmo_qualification_v3/preflight/task_materialize.stderr.log
```

V3 materialized 338 cache files / 409,436,401 bytes for the broader task set before this failure;
its GPU array never started. A local `facebook/xnli` compatibility overlay was then prepared, but
the user removed XNLI from the project before that overlay completed an end-to-end materialization
and model smoke. The overlay is therefore deleted rather than represented as validated.

## Candidate upstream repair

A future isolated Harness contribution may change only the dataset repository identity to
`facebook/xnli` and add a regression test that constructs at least the English and Turkish task
configs with a current supported Datasets/Hub stack. Before proposing a patch, verify:

1. official dataset ownership and immutable revision;
2. every existing language config and split;
3. prompt, label, metric and few-shot equivalence;
4. online materialization followed by offline reload;
5. compatibility with Harness-supported dependency versions.

This candidate repair is an upstream engineering task, not permission to restore XNLI to this
thesis evaluation protocol.

## Preserved project outcomes

- v3 jobs: data `460959`, dependency-dead array `460960`, finalizer `460961`;
- v4 jobs: data `461253` and array `461254` cancelled before GPU work at the user's removal
  decision; finalizer `461255` recorded 0/7 lanes, `scientific_result=false` and gate `blocked`;
- v4 final inventory: 18 files / 3,668,858 bytes;
- v4 qualification-result SHA-256:
  `90c363707d49238e8f9b6c1e9aa10b6f410916c77dbb158149260199e3acf5d8`.

No scientific score or model comparison follows from either attempt.
