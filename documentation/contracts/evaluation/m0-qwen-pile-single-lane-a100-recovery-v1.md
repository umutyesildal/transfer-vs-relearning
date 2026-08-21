# M0 Qwen Pile-10k Single-Lane A100 Recovery Contract v1

Date: 2026-08-21  
Status: `FROZEN / UNEXECUTED / EXACT AUTHORIZATION REQUIRED`

## 1. Purpose

Run exactly one missing scientific lane: Qwen2.5-1.5B full Pile-10k English retention. Preserve
the 23 valid M0 lanes by exact lane-result and artifact hashes. This is a bounded retry of an
operational `NOT_RUN` target, not an outcome-aware scientific rerun.

## 2. Scientific identity remains unchanged

The target keeps the original eval-v1 identity and execution semantics:

- model: `Qwen/Qwen2.5-1.5B`, revision
  `8faed761d45a263340a0528343f099c05c9a4323`;
- Harness: v0.4.12 commit `6d642546f4688648fced259eb3302efd36ece5af`;
- task: full frozen `pile_10k`, all 10,000 rows, zero-shot;
- batch behavior: `auto:4`, unchanged;
- precision, tokenizer, seeds, context handling and logging: unchanged;
- no `--limit`, truncation, subsampling or metric change;
- free-VRAM gate: exactly `68,719,476,736` bytes, unchanged.

OLMo and SmolLM full Pile-10k lanes already completed on V100-32GB. The high Qwen guard is a
conservative recovery condition inherited from its earlier V100 attention-allocation OOM; it is
not interpreted as a general Pile-10k requirement or a scientific model property.

## 3. Frozen 23-lane evidence

The original 24-lane source ledger remains bound through
`configs/evaluation/m0_scientific_recovery_v1.yaml` SHA-256
`d934b782fe307d1d54b7fdce47be8ebc2409a6b6c2acf3f2aa435aa4577ac6d7`.
Six operationally repaired lanes are retained from two immutable recovery roots:

- first isolation root: OLMo English capability
  `b254691b103bfae7fb9294b3078ae2a794e6c282d7afd3892e68eff4238df598` and Turkish capability
  `3c934519740b45f62d6ead3c34e3e3871f62ef9ba9f8e748b663d17c12101c64`;
- five-lane root: OLMo Turkish PPL
  `79d32ebff7677b026478913f233bad3ed23041a96d31bcdb2634a2c7d5dd81bd`, Qwen Turkish capability
  `d8391afcad0ece157da54858cdde25cd3b9aaa5ba1f0bbcdcde38c42421ec73b`, Qwen Turkish PPL
  `d2548faccb9d15b1176310c429e7c4a61f68fd95ab70d78cdcef9bb4b6ccb904` and SmolLM English
  capability `d4cf359cda792569ea9abe597d55759034c6b51b2c928f2f9991bc6f1ef60908`.

The prior terminal ledger, composite and family inventory are additionally bound by path, byte
size and SHA-256 in the config. The three known source-root PPL append artifacts remain explicitly
bound and preserved. Validation fails if any referenced result or artifact changes.

## 4. Fresh namespace and route

The only writable scientific root is:

`/vol/tmp2/yesildau/eval_v1_m0_scientific_three_model_qwen_pile_single_lane_v1`

The route remains one exclusive `gruenau10` allocation requesting all three A100-80GB devices.
Before the lane, all three UUID/name/total/free rows are recorded. The deterministic selector uses
the maximum-free eligible UUID. If none crosses the unchanged 64 GiB free-memory gate, it polls
every 60 seconds for at most 7,200 seconds and stops `NOT_RUN` without model load.

A read-only snapshot on 21 August found two A100-80GB devices above the memory gate, with 74,938
MiB and 78,310 MiB free respectively. This observation is not an availability guarantee and does
not bypass the execution-time selector.

## 5. One wave and finalization

The operator submits exactly five Slurm jobs:

1. one exclusive controller executing only `qwen:english_retention_pile_10k`;
2. three `afterany` model finalizers assembling retained plus new lane evidence;
3. one `afterany` family finalizer.

Only a complete target result with return code zero and full artifact path/byte/hash validation may
produce a 24/24 composite and set `normalization_allowed: true`. The raw finalizer does not perform
normalization or scientific interpretation.

## 6. Frozen implementation

- implementation commit: `615d572e553884473bf56d5ac2917aff55d8264a`;
- operator SHA-256:
  `65cd5465e5bb1f4bad83094e85875ebdb112d629f63437756a77bc261d6bcdbc`;
- recovery module SHA-256:
  `153b53b421c5e688d89333dbad5719c2df817af78329bfd1a2272df1cf4703d9`;
- recovery tests SHA-256:
  `fa7a49d7268fa3d91c69edeb4171d5a02a30353a73d36f5e41eed931871e8f70`;
- compatible full suite: all tests passed;
- pre-authorization config SHA-256:
  `f394ca3ecf0e056f825545675b41f7fc7b970da240b41156fff030019a36cf36`.

## 7. Prohibitions and authorization boundary

This contract forbids rescoring any of the 23 valid lanes, changing `auto:4`, lowering the memory
gate, changing model/data/task/metric identity, mutating prior roots, automatic resubmission, a
second single-lane wave, normalization, M1/M2 work, cleanup, deletion, HU-home writes and
foreign-process intervention.

The config remains `execution_authorized: false`. Execution requires a new exact user instruction
binding the final contract SHA-256 and pre-authorization config SHA-256 and authorizing
publication/HU fast-forward, final preflight and exactly one five-job DAG. That authorization will
be consumed by one submission and will not authorize retry or downstream work.
