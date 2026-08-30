# vngrs M2 OSCAR exact block materialization adapter repair contract v1

**Date:** 2026-08-31  
**Lifecycle:** `FROZEN / UNEXECUTED / SINGLE CPU ADAPTER REPAIR WAVE`  
**Contract ID:** `vngrs-m2-oscar-exact-block-materialization-adapter-repair-v1`

## Purpose and terminal evidence

Job `482007` started before the pending-only relocation decision and stopped fail-closed at OLMo
`stream_train_blocks`. The exact exception is `AttributeError: 'FrozenTokenizerAdapter' object has
no attribute 'eos_token_id'`. The preserved root
`/vol/tmp2/yesildau/vngrs_m2_oscar_exact_blocks_recovery_v1` has exactly eight files / 123,392
bytes, zero block files and no manifest. Its terminal hashes are:

```text
failure.json            1ce489502583f900a039e1776e67d4d2992d945405d49cfac3bf385a93c799d7
progress.json           2badd02ca329ea7ce4ef5808981746fbd3e85bc88d29a4f01f15b1b24d69af38
slurm_exit.json         e427d45ca3e911b5c11b5a77b703e8ffdfa2f4192095e63a180155a3b0bbf914
slurm-482007.stderr.log 0e48d7e87d46078a5b8acc91e4e55a349dda2b1ecc0b1578a8d1df5e420de821
```

Peak RSS was 32,807,744 KiB (about 31.29 GiB), so this was not an OOM. The 4-CPU/128G pending-only
relocation contract remains unexecuted and became ineligible when `482007` terminalized.

## Narrow repair

The only code correction resolves EOS from either the tokenizer object itself or the production
adapter's nested `tokenizer.eos_token_id`, and rejects absent, negative or non-integer IDs. A
regression fixture exactly mirrors the production adapter shape and exercises matched M2-A/M2-B
stream creation.

The recovery runner, OSCAR source, deterministic split, exact epoch-036 tokenizers, 250 Turkish
facts, 97,536 × 512 train blocks per arm, 2,048 × 512 validation blocks, 976 replacement blocks,
seed 42 and document-order namespace are unchanged. The operational allocation is 4 CPU / 64G /
six hours because the observed 31.29 GiB peak fits with more than 2× memory headroom. No GPU is
requested.

## Fresh-root and fail-closed gates

The proposed root is:

```text
/vol/tmp2/yesildau/vngrs_m2_oscar_exact_blocks_adapter_repair_v1
```

Before any separately authorized submission, the frozen submitter must prove that job `482007` is
absent from `squeue`, the exact eight-file failed root and four hashes above match, no block or
manifest was published, the original partial predecessor/source/split hashes match, the new root
is absent, the HU checkout is clean at the exact authorized commit, no matching job exists,
capacity/inodes pass and Slurm `--test-only` passes. It performs no hold, cancellation, release or
cleanup and submits at most one job. The previous roots remain immutable/read-only.

Success still requires all three exact role audits, the closed family manifest and final PASS
audit. Even on success, `ready_to_train=false`; M2 training is not opened. Failure preserves the
fresh root and permits no automatic retry.

## Frozen implementation

```text
config       3388f98b738ac6936e413da3a98cfc38f5c892fd4303e49e5f716fd6cbf97a84
runner       5820113e09e45d5bfb2d2cabb4f9c110fc6c3b5cf123f18f541055b9d2f6f196
streaming    1cc66107a193ca425481beaf3d7df9f08ca5f6c6a27a9a6538593e95d96d3433
fact/order   fe5455062eaa7de6eacbbb96dac7bf7af86420fd463c353d6e8028fd91fad005
Slurm        5471b8c475d81602448f28b424137bc6b6e0c89fa6eab77e856eb92085b06dfd
submitter    da601b7070c3b94ef2b8d9a773191c0637ffbdee91015837042700408f8280c4
recovery test 9744c69dfe6e674c4cae2bbce057886a4c8746232ffeea7548ef4bf3b870c92c
repair test   d23b1e40b51e2f2490086abc8cef1d12d0b71a68e96a9adac9a7fb8e0b81544f
```

Focused compatible suite: `12 passed`. Bash syntax, YAML parse and `git diff --check`: PASS.

## Authority boundary

This contract authorizes nothing by itself. A later explicit authorization bound to this
contract's final SHA-256 and exact implementation commit may permit ordinary non-force push,
preservation-checked HU fast-forward and exactly one fresh-root CPU repair wave.

It does not authorize another relocation, hold/cancellation/release, automatic retry, GPU,
model-weight access, optimizer smoke, M2-A/M2-B training, evaluation, cleanup, deletion or any
mutation of prior evidence roots.
