# vngrs M2 OSCAR fact-translation block repair v1b

**Date:** 2026-08-31
**Lifecycle:** `FROZEN / UNEXECUTED / SINGLE RUNTIME-TMP COMPATIBILITY WAVE`
**Contract ID:** `vngrs-m2-oscar-fact-translation-repair-v1b`

## Preserved v1a result

V1a publication, preservation-checked HU fast-forward and `19/19` HU tests passed. Test-only
submission passed and the single real job was `482057`. The job began on `longrun`, but stopped
before source validation, tokenizer loading or block writing because `conda run` created a
temporary file under the job-bound `TMPDIR` before Python entered the operator:

```text
ValueError: Unexpected pre-run fact-translation repair artifact: tmp/tmpiltx1wfc
```

The v1a root is immutable evidence. It has four files / 17,674 bytes, zero block files and no
manifest. Its exact files are:

```text
control/submission_state.json                 c65c87e404e287c7925752e7ddd250f7795517c2d2f2d5aa22fdf7ee27d29556
control/submission_result.json                62bb3c6176fb1a6c2c25ab4fbbc99d309a679448bc808c9edd16fdb88022a277
logs/m2-fact-tr-repair-v1a-482057.err          1d91bdbe067c61a9b630b1e40e15c14dab61a0b2440ffc392acbe6fc831573c1
logs/m2-fact-tr-repair-v1a-482057.out          e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

Slurm accounting was unavailable because of the known Munge/SlurmDBD authentication failure;
the terminal stderr and absent queue entry establish the operational stop. No automatic retry ran.

## Exact correction

The operator's precreated-root validator changes one condition: runtime-owned files under `tmp/`
are allowed alongside the already allowed `logs/` and two submission-control files. Every other
pre-run artifact remains rejected. A regression test proves that a runtime `tmp/` file passes and
an unexpected `blocks/` file fails.

The new root is:

```text
/vol/tmp2/yesildau/vngrs_m2_oscar_fact_translation_repair_retry_v2
```

Partition `longrun`, 4 CPU, 32G, two-hour limit, corrected registry, tokenizer snapshots,
predecessor manifest, 97,536 blocks per arm, 976 replacement blocks and all scientific invariants
remain unchanged. The launcher additionally verifies all four v1a evidence hashes before creating
the new root.

## Frozen implementation

```text
config                 77aeb8f435d6f175619053d82ced8945ac66a390ef3c71777ca15a4522347ff1
block repair runner    31fac19520d3352c7991e5a76932544f7278bcd6af81970631b3d3edcef36e17
Slurm                  f75d1144b88ec891bbcaeef5c795ef484734f2a35b35fffce06b1c36ba45ad7f
submitter              e748ac82a00d2cf6302169c5a8957715e9d05df2d5b0a3daee4b0c21931ecbb6
focused test file      1f2ad3c51cf34c83e8ca5ec22cc0146a59f4b2f33fee7d1c302ec636883bdc09
```

The compatible local suite passes `20/20`; Python, shell and YAML checks pass.

## One separately authorized wave

A later exact SHA-bound instruction may authorize ordinary non-force push of the exact commit,
preservation-checked HU fast-forward, targeted HU tests and exactly one fresh-root 4-CPU/32G
`longrun` job after one passing `sbatch --test-only`. Read-only access is limited to the preserved
v1a evidence, exact predecessor block family and exact tokenizer snapshots. Writes are limited to
the new retry-v2 root.

PASS still requires the three corrected M2-B files, three role audits, exact block/token and
predecessor invariants, terminal `M2_FACT_TRANSLATION_REPAIR_PASS` and `ready_to_train=false`.

## Authority boundary

This contract authorizes nothing by itself. Exact final SHA-256 and exact implementation-commit
authorization are required. GPU, model-weight access, optimizer smoke, M2-A/M2-B training,
evaluation, cleanup, deletion, fallback, a further retry and automatic retry remain forbidden.
All earlier roots remain preserved read-only.
