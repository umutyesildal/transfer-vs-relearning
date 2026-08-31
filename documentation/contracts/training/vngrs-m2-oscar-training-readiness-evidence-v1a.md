# vngrs M2 OSCAR training-readiness evidence contract v1a

**Date:** 2026-08-31  
**Lifecycle:** `FROZEN / UNEXECUTED / SINGLE CPU SCHEMA-REPAIR WAVE`  
**Contract ID:** `vngrs-m2-oscar-training-readiness-evidence-v1a`

## Purpose and predecessor

Job `482035` stopped before evidence publication because v1 incorrectly expected `file_hashes` in
the compact parent model manifest. The failed root is immutable/read-only, exactly 5 files /
14,971 bytes, with stderr SHA-256
`e31ebce25931b74eda597610a6dfb65bf8879c78dff3e59713adfa49ec2cd118` and exit-audit SHA-256
`29f49bf6beb885d0990dbdfe041d945b4f2eaad6149d85d2e978f6e772b6bdcd`.

V1a changes only the parent asset registry reader and uses a fresh root. The compact model
manifest remains the path/checkpoint identity binding. The linked exact snapshot manifest supplies
the canonical file list, byte sizes and SHA-256 values. V1a requires both manifests to carry the
same non-empty `checkpoint_sha256`, requires the model manifest's path to equal the exact epoch-036
snapshot, rehashes every listed file, verifies byte sizes, rejects duplicates/nested paths/trainer
state, and requires `config.json` plus at least one model weight asset.

## Preserved scope

Corpus, blocks, 250-fact registry, parent paths and manifest hashes, six-run scientific recipe,
storage formula and review-handoff semantics are unchanged from v1. The new root is:

```text
/vol/tmp2/yesildau/vngrs_m2_oscar_training_readiness_evidence_retry_v1
```

The original failed root and every earlier M1/corpus/block root remain read-only. Terminal PASS is
still `EVIDENCE_PREPARED_AWAITING_FACT_REVIEW_AND_GPU_SMOKE`; `ready_to_train=false`.

After PASS, `fact_review.html` and `fact_review_packet.jsonl` may be copied read-only to the local
workspace only if each is at most 1 MiB and combined size is at most 2 MiB. No human verdict is
entered by the wave.

## Frozen implementation

```text
wave config       a2158bbb3221adb36b52a16f7625f04acf038823f906197465f40f62f41e949e
preparation v3    8e20a48afd83335b9fc18212d1808a0f5eee4e438eed9374bc081b2fe0d18d0f
readiness runner  3f66ebc79e2a7f08b367de5016d5bf7b2694c290f129c579b7e15cdf3e2fe256
family preparer   fb00ca7ff7a498b930db7d91034c7d1dc3e4506b110c84c60c84e4ba14d22f98
family validator  9190bfb25220cd8c951efdcb30d68219e67acbf68a5e65c032a05e7cc4b1d36c
Slurm             5b880d35305cf07cbe877c06d9483f261f393e0d7928facfb96691fbd03464bc
submitter         eb8d7fbbc6a98c78285738e09625e771f36f418238f0cc8acc73e09a6defd43a
focused tests     9fdac861d2475be547de894a841c736ff58204d7720c7f6fc5b4621eb198cc8c
```

Compatible suite: `68 passed`. Python/Bash syntax, YAML parse and `git diff --check`: PASS.

## Authority boundary

This document authorizes nothing by itself. A later exact SHA-bound authorization may permit
ordinary non-force push, preservation-checked HU fast-forward, exactly one fresh-root 4-CPU/64G
CPU repair job and the bounded read-only handoff copy.

It does not authorize reuse/mutation of the failed root, a second retry, GPU, optimizer smoke,
human verdict entry, model inference, M2-A/M2-B training, evaluation, cleanup or deletion.
