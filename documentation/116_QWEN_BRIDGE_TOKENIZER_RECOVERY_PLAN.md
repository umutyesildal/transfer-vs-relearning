# 116 - Qwen Bridge Tokenizer Recovery Plan

**Date:** 2026-07-22  
**Status:** FROZEN BEFORE RECOVERY  
**Authority:** Documents 100, 109, 112--115 and `AGENTS.md`

## 1. Failure And Scientific Scope

Evaluation task 411249_0 completed Qwen M0 bridge and English/Turkish PPL, then stopped before its
first M1 result with `No answer tokens detected for the prompt/candidate boundary`. The generated
M1/low/full manifests had replaced Contract V2's explicit Qwen base-tokenizer fallback with the
tokenizer-incomplete model checkpoint directory. This is an evaluation-manifest construction bug,
not evidence about Qwen transfer, training, PPL, GPU memory, or storage.

The failed V1 contract and stderr remain unchanged. Recovery is append-only under:

```text
/vol/tmp2/yesildau/turkish_bridge_v1/evaluation_v2_qwen
```

It changes only tokenizer-path preservation and evaluates only the three missing states: M1,
update-32 low, and update-128 full. Models, weights, probes, candidate inventories, corpora,
thresholds, bootstrap procedure, PPL scoring, seeds, and primary/sensitivity populations remain
identical to Document 115.

## 2. Frozen Reusable M0 Evidence

The completed V1 Qwen M0 evidence used the correct pinned tokenizer and will not be recomputed. Its
parent evaluation-manifest SHA-256 is
`785eff7dbe56b993a38538da33917385691aa151fc55f84fc91bae5463626f12`.

The nine frozen M0 file hashes are:

| Artifact | SHA-256 |
|---|---|
| bridge/per_probe_results.csv | `29b3f4517a8d32fa57909d1df4828072fc18ee4f29ced21ac30fae950997996a` |
| bridge/progress.json | `66e07a2612e2e5bf6482b42a9939013dc9e8791351d95d6d8cea45da2461d486` |
| bridge/summary.json | `5c36328cbce72dae1e9f76d21ea51f7ddb4952f64ea77cf8bcefc08c756e94d9` |
| bridge/summary_by_direction_relation.csv | `21390ddb922a5bf49804cbd332b3420e76a4b3f14987cf3412795cd17df36840` |
| ppl/english/loss_blocks.csv | `d0af708cb4eea8ca16b719501de8cb594734a3941986375480fbe05700a8b396` |
| ppl/english/summary.json | `e9b5902c5f4a95560b18369e07736b85e337964b8e7bf919f464241f269f649f` |
| ppl/summary.json | `e6387e681d4d7e0ed57fe40822fbd0c8176475a07ec50de2089219b611368f83` |
| ppl/turkish/loss_blocks.csv | `4d07fb0e22a9d1f280a1f46561025c22147668750ab716f9da8fc5aa33330729` |
| ppl/turkish/summary.json | `d09fdb206bf31f89c76f619f236c6fab956393eff79b786b7d5e130673b21a8c` |

Recovery finalization must verify these exact files and combine them read-only with the new
M1/low/full outputs.

## 3. Tokenizer Correction And Preflight Gate

The generic local-manifest helper will preserve an explicit
`tokenizer_source_path[_absolute]` from its source manifest instead of replacing it with the new
model directory. Contract V2 Qwen manifest hash remains
`fb860231dec3c2d0f6053675d7297343b9c5aa6f70d73f5ff77cb6516a11fc0a`; its tokenizer is pinned to:

```text
/vol/tmp2/yesildau/m1_cross_family_screen_v1/models/Qwen__Qwen2.5-1.5B/8faed761d45a263340a0528343f099c05c9a4323
```

All three recovered endpoint manifests must resolve to that same scratch tokenizer and must not
resolve tokenizer loading to their checkpoint directories. Before GPU submission, the CPU
preflight must load the pinned tokenizer and validate answer-token/shifted-label boundaries across
every frozen probe and every relation-family candidate batch. This gate directly reproduces the
failed evaluator boundary operation without loading model weights.

## 4. Execution, Storage, And Decision

One Qwen-only RTX 3090 job evaluates M1, low, and full sequentially, then runs the unchanged frozen
classifier using hashed V1 M0. Expected runtime after GPU start is approximately 30--50 minutes;
the conservative Slurm limit is three hours. The recovery creates zero checkpoints and reserves
5 GiB for compact results, logs, cache metadata, and temporary files. All high-volume paths remain
on `/vol/tmp2`; current training/model artifacts remain read-only.

A fresh preflight must check home/capacity/inodes, every resolved path, the original V1 and Contract
V2 hashes, all M0 hashes, all three endpoint/tokenizer paths, the exhaustive tokenizer-boundary
gate, queue state, and the 5 GiB reserve. One `afterany` post-run audit is mandatory.

The resulting Qwen classification is combined with the already frozen SmolLM2 negative result.
No threshold changes, M2/M3, scale-up, seed-43 run, or retention intervention is authorized until
the Qwen recovery result and storage audit are documented.

## 5. Implementation And HU Submission - 2026-07-22

The tokenizer-fallback preservation fix and append-only recovery were committed and pushed as
`fbdedff`, then HU was fast-forwarded to exact commit
`fbdedffa189ee0baef9377089c1dd57ecaa067f6`. Shell/Python syntax checks and the authoritative
15-test recovery/bridge subset passed on HU; the wider relevant local subset passed 89 tests with
two expected optional skips.

The recovery wave was submitted exactly once:

| Job | Role | Initial state |
|---:|---|---|
| 411256 | fresh storage/hash/path plus exhaustive tokenizer-boundary preflight | RUNNING on `gruenau3` |
| 411257 | Qwen-only M1/low/full evaluation | PENDING on `afterok:411256` |
| 411258 | recovery post-run storage audit | PENDING on `afterany:411257` |

The first preflight snapshot recorded home at 8,298,172 KiB, `/vol/tmp2` with 122,984,255,488 KiB
available (approximately 115 TiB), 3% scratch inode use, correct artifact/run symlinks, zero new
checkpoints, and a 5 GiB output reserve. Initial stderr was 0 bytes. The GPU job remains correctly
dependency-gated while endpoint weights are hashed and every prompt/candidate boundary is checked.
Do not submit a duplicate.

## 6. Recovery Result And Storage Audit - 2026-07-22

Preflight 411256 passed with empty stderr. It verified all nine frozen V1 M0 hashes, preserved the
exact Contract V2 Qwen base tokenizer, and successfully checked 168,000 frozen prompt/candidate
answer-token boundaries before GPU submission. Recovery-manifest SHA-256 is
`90fb1cd3b38a93929278bb8660bdec48d4ab3105b5da95dfb0dd926e63e3431b`.

Job 411257 then completed M1, low, and full on a clean 15 MiB-baseline RTX 3090 on `guppi8`. The
three-state GPU interval was approximately 22 minutes. All three bridge suites reached 1,500/1,500
probes and all six English/Turkish PPL scores completed. Its 1,720-byte stderr contains only normal
model-loading progress and the Transformers dtype deprecation; there is no traceback, OOM,
boundary error, or failed assertion.

Audit 411258 completed with empty stderr. Home remained 8.0 GiB; `/vol/tmp2` retained approximately
115 TiB free at 3% inode use. The append-only recovery tree is 2.5 MiB and created no checkpoint or
large home artifact.

### 6.1 PPL And English Retention

| State | English PPL | ratio to M0 | Turkish PPL |
|---|---:|---:|---:|
| M0 reused | 14.6997 | 1.0000 | 14.1357 |
| M1 | 21.3890 | 1.4551 | 22.0069 |
| low | 17.1507 | 1.1667 | 14.4823 |
| full | 16.3699 | 1.1136 | 13.3780 |

Turkish PPL improved strongly from 22.0069 at M1 to 13.3780 at full (ratio 0.6079), passing the
frozen Turkish-effect gate. English PPL also recovered substantially from the high-drift M1 value,
although full remained 1.114 times M0. EN->EN eligible-fact top-1 stayed exactly 100% at M1, low,
and full, so the adapted model did not lose English candidate retrieval.

### 6.2 Cross-Lingual Fact Access

The primary population is Qwen's 497 frozen model-eligible facts.

| State | EN->EN top-1 | TR->EN top-1 | TR->TR top-1 | TR->EN mean margin |
|---|---:|---:|---:|---:|
| M0 | 1.81% | 1.01% | 1.81% | -5.4107 |
| M1 | 100.00% | 66.20% | 32.80% | +0.4262 |
| low | 100.00% | 52.31% | 32.60% | -0.4473 |
| full | 100.00% | 46.48% | 30.99% | -0.7695 |

Qwen M1 already exposed substantial Turkish-prompt access before Turkish adaptation. The generic
Turkish dose did not preserve or improve it: paired-subject TR->EN change was -0.1400 at low with
95% CI [-0.1765, -0.1060], and -0.1985 at full with 95% CI [-0.2410, -0.1570]. Full still passed
absolute access, M0-adjusted access, and relation-breadth gates, but its mean margin became negative
and the adaptation-gain/preserved-open-bridge gate failed because access dropped far beyond the
allowed five points.

The frozen primary classification is `not_viable_under_frozen_pilot`. All sensitivity populations
agree: all 500 facts, model-strict 496, shared-eligible 357, and shared-strict 196 are also not
viable. This does not mean Qwen lacks cross-lingual access; it means the tested general Turkish
adaptation actively reduced a strong bridge already present at M1, despite improving PPL and
preserving EN->EN retrieval.

## 7. Combined Pilot Decision

Neither family passes the precommitted bridge promotion rule. SmolLM2 retained English facts and
improved Turkish PPL but never opened useful TR->EN access; Qwen began with much stronger M1 access
but the tested Turkish dose degraded it monotonically. Therefore Document 109C's bounded Qwen
retention intervention is not automatically opened, and no scale-up/M2/M3 run is authorized.

The next scientific decision should explicitly choose between stopping this bridge recipe as a
valid negative feasibility result or designing a newly documented dose/evaluation diagnostic. Any
new experiment must be labeled exploratory and must not reinterpret the frozen failed gates.
