# vngrs M2 OSCAR corrected-family optimizer smoke v1

**Date:** 2026-08-31
**Lifecycle:** `FROZEN / UNEXECUTED / SINGLE THREE-TASK GPU SMOKE ARRAY`
**Contract ID:** `vngrs-m2-oscar-corrected-optimizer-smoke-v1`

## Purpose

The corrected three-model M2-B block family completed PASS in job `482066`. Before any M2-A or
M2-B scientific training can be contracted, this smoke measures whether each exact epoch-036 M1
parent can execute one full effective M2 AdamW update with the frozen BF16 recipe and records peak
GPU memory. It is compatibility evidence, not scientific training.

## Frozen inputs

```text
corrected block-family manifest  96f9867c857b08bfd784660331d1a354be7d7c6bc39250091f427fdfaa3c6486
corrected-family final audit     fc2075cbce7f4d51c8013b7977ec64630d2181c8c9ebf30a64f5cab61514e54d
corrected fact registry          46a1071d228758013d73fae4ab3925538523eb338001e00bde9d5fe178f1c4a2
corrected review decisions       3af9fa0356392ea55a99b962a61453385cbefbb16231ef510c781c12863045e4
corrected review validation      a5e4f04a567de98f85674e8c58e13effe85753738d5de931704e41a153ec20b1
readiness config manifest        755295ddda651466cbf868b52bd24c272475a17e29c7988f9f97c3eb83951784
readiness config validation      5c53f907c26eb3dae602825dbbe0a30aebc0ba0c3c238876cf39ac45a34ab815
readiness final audit            d8cd44eae03ec1c5b5eea334bf94506417730c30f44dfbfbf6df2bf60a144fc8
OLMo M2-A config                 dbf83bcbe585b44e0f230958ee0dbf5bda19ac2476df139286ac034707305835
Qwen M2-A config                 5a15eab72fa84b33535d95dcaf90ce2f9dfd1c0dd7e7a918aaec748ba6cd3e04
SmolLM M2-A config               5ad2a5ef6c5385873643babc1e73bc0754471ce29ff1664aaf66007cbf171f76
```

The existing readiness configs remain execution-disabled scientific-training configs. This smoke
reads only each role's M2-A tensor blocks because M2-A and M2-B have identical block shape and
optimizer memory recipe. Before model load, the runner binds that M2-A file and the role's
corrected M2-B file to the corrected-family manifest by exact path, byte size and SHA-256.

## Exact smoke recipe

One array `0-2%1` executes roles in deterministic alphabetical order: OLMo, Qwen, SmolLM. Each task
uses one exclusive `a10080gb` GPU on the `gpu` partition with 8 CPU, 64G host memory and 90 minutes.
The task must observe at least 61,440 MiB initial free VRAM and zero foreign compute processes.

For each model:

```text
sequence length                 512
microbatch blocks               4
gradient accumulation           32
effective blocks                128
effective tokens                65,536
optimizer updates               1
precision                       BF16 parameters/gradients/state
gradient checkpointing          true
optimizer                       AdamW, foreach=false
checkpoint written              false
scientific training             false
```

The runner loads the exact local epoch-036 model weights read-only, uses the first exact 128 M2-A
blocks, performs forward/backward accumulation, finite loss/gradient checks, gradient clipping and
one AdamW step. It records parameter, gradient and optimizer-state dtypes, loss range, gradient
norm, GPU identity, free memory and peak allocated/reserved bytes. It writes no model or optimizer
checkpoint.

## Fresh output and PASS rule

```text
/vol/tmp2/yesildau/vnd_m2_oscar_optimizer_smoke_corrected_v1
```

The submitter requires a clean exact checkout, every frozen input hash/status, an absent fresh
root, zero duplicate jobs, at least 50 GiB scratch capacity, at least 8,192 free inodes and one
passing `sbatch --test-only`. Exactly one array may be submitted. Tasks are sequential (`%1`) and
there is no fallback or retry.

Family PASS requires exactly one `OPTIMIZER_SMOKE_PASS` report for each role, no failure audit,
finite values, exact BF16 parameter/gradient/AdamW-state gates, one update, 128 blocks, 65,536
tokens, corrected-family manifest SHA binding and `checkpoint_written=false` /
`ready_to_train=false`. Any missing or blocked role leaves the family blocked.

## Frozen implementation

```text
config                 f66924c5c6fefdf18bfc83cd7c321a073c666b2086e65b64ccd12cbe33e32fef
runner                 0647f9aa457f700804f23f884e336802c4e53b5861eb0c2163cbfa16015633d8
Slurm                  2d9abb8120ebfee1c95e2258db801b4ec432bb7b9baf5f6c26803586a9120ff3
submitter              bcff46ce8a540029e78bdbdff39f773f8c918e23b0ecff341f50d7e704e3682e
focused test file      54bd06572d17fb742fcdd567048af6ab07b4b99fafb5cb258be54f41b39c8de5
```

The compatible local suite passes `21/21`; Python, YAML, Bash and diff checks pass.

## Authority boundary

This contract authorizes nothing by itself. A later instruction must quote its exact final
SHA-256 and exact implementation commit to authorize ordinary non-force push, preservation-checked
HU fast-forward, HU tests, model-weight read-only access and this one GPU smoke array.

It does not authorize M2-A/M2-B scientific training, checkpoint creation, evaluation, scoring,
cleanup, deletion, fallback, retry, a second smoke array or automatic retry. Smoke PASS is only a
prerequisite for separately freezing corrected M2-A/M2-B training configs and a training contract;
it is not training authorization.
