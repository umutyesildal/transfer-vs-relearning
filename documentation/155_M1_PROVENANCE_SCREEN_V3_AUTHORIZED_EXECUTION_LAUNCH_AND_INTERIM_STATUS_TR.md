# 155 — M1 Provenance Screen v3 Yetkili Execution Launch ve Ara Durum

**Tarih:** 2026-08-11 (Europe/Berlin)  
**Durum:** `IN_PROGRESS — TWO VALID CANDIDATES QUEUED — PYTHIA FAIL-CLOSED`  
**Kontrat:** Document 152b SHA-256
`1b55a03484682e065c9eaec106f8803b9ffdecba9301e3a0261df9e6ecd154fa`

## 1. Publication ve pre-submit gate

- Correction commit `f0caa05b7ac487b376ed7f2e070a5dd5c8d9415e` ordinary non-force push edildi.
- HU checkout aynı commit'e preservation-checked fast-forward oldu.
- Dirty-status SHA-256 `8d6c5d44b4a387b29e3803e8bbc122f0dbbabf4ecd9fbe46a82c65c32c6d3297`
  olarak korundu.
- Frozen home reference `14,689,423,360 < 32,212,254,720` byte olarak doğrulandı;
  per-stage recursive `du` çalıştırılmadı.
- `runs` ve `artifacts` scratch'a resolve edildi; `/vol/tmp2` yaklaşık 113 TiB free ve %3 inode
  kullanımındaydı.
- Authoritative HU targeted suite: `98 passed`.
- Shared acquisition preflight job `452142`: PASS.

## 2. Submitted independent DAGs

| Candidate | Acquire | Train preflight | Train | Eval preflight | Eval |
|---|---:|---:|---:|---:|---:|
| OLMo | `452143` | `452144` | `452145` | `452146` | `452147` |
| Pythia | `452148` | `452149` | `452150` | `452151` | `452152` |
| Falcon | `452153` | `452154` | `452155` | `452156` | `452157` |

Family terminal assembler: `452158`.

## 3. Acquisition outcome and Pythia adjudication

OLMo and Falcon resolved exactly to their frozen revisions and passed meaningful non-empty
model-native tokenizer probes:

| Candidate | Tokenizer | Vocab | Frozen-probe token counts | State |
|---|---|---:|---|---|
| OLMo | `TokenizersBackend` | 100,278 | 7 / 10 / 15 / 17 | acquisition PASS |
| Falcon | `GPT2Tokenizer` | 50,257 | 7 / 10 / 17 / 23 | acquisition PASS |

Pythia's exact pinned snapshot contained model/config files but no tokenizer vocabulary asset.
`AutoTokenizer` produced a two-token `GPTNeoXTokenizer`; all four frozen probes returned empty
`input_ids`, attention masks, offsets and decoded strings. The round-trip validator incorrectly
classified empty-to-empty equality as PASS. Training had not started. Jobs `452150`, `452151` and
`452152` were fail-closed cancelled before GPU work.

Pythia's interim terminal class is:

```text
NOT_RUN_MASKING_COMPATIBILITY_GATE
```

This is not a factual-learning result. No revision fallback or external tokenizer was substituted.
The historical false-positive access/preflight manifests remain preserved; final assembly must
apply this adjudication instead of interpreting their `passed/PASS` fields scientifically.

## 4. Current state at 2026-08-11T07:47:57+02:00

- OLMo train `452145`: PENDING / Resources.
- Falcon train `452155`: PENDING / Priority.
- Both training preflights: PASS.
- Both training artifact counts: zero; GPU work had not begun at this cutoff.
- OLMo/Falcon downstream evaluation and family summary remain dependency-pending.

No cleanup, retry, seed-43, corpus or M2/M3 action is authorized by this interim record.

## 5. Append-only GPU reroute update (2026-08-11)

The user rejected the approximately three-day A100 scheduler estimate and explicitly requested
cancellation, live free-GPU discovery and restart. All remaining original v3 jobs were cancelled;
completed acquisition evidence was preserved.

Live Slurm and allocated `nvidia-smi` probes showed:

- `guppi5` RTX3090: clean, 15 MiB used;
- `guppi6` RTX3090: Slurm-idle but contaminated by two foreign processes using about 21.4 GiB;
- `guppi7` RTX3090: clean, 15 MiB used.

Falcon was restarted as training job `452163` on `guppi7`. Its smoke passed with one optimizer
step, finite loss `8.555147`, checkpoint save/reload and peak allocated bytes `13,262,103,040`;
training remains active. Downstream preeval/eval jobs are `452165`/`452167`.

OLMo job `452162` on clean `guppi5` failed before scientific training during optimizer smoke:
23.42 GiB was in use and another 784 MiB allocation failed. A single recipe-identical allocator
retry `452169` with `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` also failed before training;
it remained about 229 MiB short. Its dead downstream jobs were cancelled. No OLMo training
manifest/run exists.

All A100 nodes are currently wholly allocated in Slurm through the scheduler estimate
`2026-08-14T11:37:11`. The remaining immediate OLMo option is a separately approved operational
batch decomposition change from microbatch/accumulation `10×50` to `5×100`, preserving effective
batch 500, 252 updates, BF16, LR, epochs, data and endpoint. It has not been applied at this cutoff.

## 6. Append-only OLMo RTX3090 batch-decomposition retry (2026-08-11)

The user explicitly approved the recommended OLMo-only operational decomposition change. Narrow
commit `f7b2b6d527b84328792c773e84b34c46e6cbaeae` adds a separate retry template and a test proving
that only `per_device_train_batch_size: 10 -> 5` and
`gradient_accumulation_steps: 50 -> 100` changed. Effective batch remains 500; BF16, LR, 36
epochs, seed/data seed, dataset, loss mode, EOS policy, gradient checkpointing and update-252
endpoint remain unchanged. The original v3 template was not rewritten.

The commit was ordinary non-force pushed and preservation-checked fast-forwarded on HU. Dirty
status SHA-256 remained
`8d6c5d44b4a387b29e3803e8bbc122f0dbbabf4ecd9fbe46a82c65c32c6d3297`; the HU targeted suite
passed 60/60. No recursive HU-home `du` was repeated. The OLMo-only training preflight job
`452173` passed against retry-template SHA-256
`fae9920356c64ab19ceb2fab666dbb40a9f6bf0429fe552fadac59da90caf380`.

The single retry chain is:

| Stage | Job ID | State at launch cutoff |
|---|---:|---|
| OLMo training preflight | `452173` | PASS |
| OLMo training | `452174` | RUNNING on `guppi5` RTX3090 |
| OLMo evaluation preflight | `452175` | dependency-pending |
| OLMo base/endpoint evaluation | `452176` | dependency-pending |

The training root was absent immediately before this retry. This update does not yet claim smoke
PASS, completed training, evaluation metrics or a scientific result; those require artifact/log
verification after the corresponding stage completes.

## 7. Append-only OLMo 5×100 retry outcome

Job `452174` failed during the pre-training optimizer smoke; real training never began. Model
weights loaded successfully, but the first AdamW multi-tensor optimizer step requested an
additional 784 MiB while only 715.38 MiB remained free. PyTorch reported 22.84 GiB total process
use, 22.26 GiB allocated and 267.20 MiB reserved-but-unallocated. Thus `5×100` improved the memory
margin but remained approximately 69 MiB short at the same optimizer-state peak.

No smoke PASS manifest, training run or checkpoint was produced. Dead downstream jobs `452175`
and `452176` were cancelled. This is an operational fit failure, not a scientific OLMo result.
Falcon job `452163` remains independent and active. Any further OLMo attempt must explicitly
address AdamW optimizer-step peak memory; silently counting this failure as a model score is
forbidden.

## 8. Append-only AdamW `foreach=False` retry outcome

The user explicitly authorized the narrower single-tensor AdamW attempt and asked whether V100
would be preferable. Commit `5407161a0b3a978fafef9d1ac4d7eb736552d910` added an isolated
`optimizer_foreach: false` template plus smoke/training wiring; the 5×100 BF16 recipe and all
scientific settings remained unchanged. The commit was ordinary non-force pushed and
preservation-checked fast-forwarded; HU targeted tests passed 61/61 and dirty-status SHA-256
remained unchanged.

Preflight `452177` passed and training job `452178` started on clean `guppi5`. The traceback
verified that PyTorch selected `_single_tensor_adam`, but the first optimizer step still requested
a 784 MiB `exp_avg_sq.sqrt()` temporary for the largest parameter while only 715.38 MiB remained
free. The job therefore failed at smoke before scientific training. No smoke PASS, run,
checkpoint or evaluation exists; downstream `452179`/`452180` were cancelled.

This evidence corrects the earlier hypothesis: the 784 MiB peak is not specific to the foreach
multi-tensor kernel. A later attempt must use either a still smaller BF16 microbatch decomposition,
a fused/offloaded optimizer implementation with separately reviewed equivalence implications, or
a higher-memory device. V100 has 32 GiB but lacks native BF16, so moving there would additionally
change mixed precision to FP16/FP32 and is not recipe-identical.

## 9. Append-only V100 FP16 compatibility and successful smoke

The user explicitly selected the idle V100 route. Commit
`4b14cc811cdc0723d87d49153346bb0e59cbc1df` restored the original `10×50` batch decomposition
and changed only mixed precision from BF16 to FP16. It also added FP16 autocast and GradScaler to
the optimizer smoke. HU targeted tests passed 62/62. Preflight `452181` passed, but job `452182`
failed at the first kernel because the existing Torch 2.7/CUDA 12.8 project wheel was compiled
only for `sm_75+`; V100 is `sm_70`. No training began and downstream `452183`/`452184` were
cancelled.

The user-authorized V100 path then used a scratch-only compatibility environment, leaving the
base project env and the active Falcon job unchanged. Commits
`5d51914c2a5949030f1ef24355701cfdea4d0825` and
`0151847c88ca98c887806a2e2eb77f0c76e3238c` added optional scratch-Python launch routing, a
Torch 2.6.0/CUDA 12.4 installation job and an allocated-V100 validation job. Install job `452185`
successfully installed the environment but failed its initial CPU-side `get_arch_list()` check;
the compiled wheel itself declared `sm_70`. Its dependency-dead chain `452187`–`452189` was
cancelled without training.

Allocated-V100 validation `452190` then passed on `Tesla V100-PCIE-32GB`: compute capability 7.0,
compiled `sm_70`, finite FP16 forward/backward, Torch `2.6.0+cu124`, Transformers `5.13.0` and
Datasets `5.0.0`. Fresh OLMo preflight `452191` passed. Training job `452192` subsequently passed
the full optimizer smoke with:

- FP16 autocast and GradScaler enabled;
- finite loss `7.916508674621582`;
- all 179 gradient tensors present;
- peak allocated bytes `29,973,358,592`;
- smoke checkpoint save/reload PASS with 1,484,916,736 parameters.

Job `452192` entered real 252-update training on `gruenau1`; its first update completed in 15.56
seconds, giving an initial training-only estimate of roughly 65 minutes after startup. Downstream
evaluation preflight/evaluation jobs are `452193`/`452194`. These are launch/progress facts only;
no completed OLMo metrics or scientific gate result is claimed yet.

## 10. Append-only Pythia repair-contract cross-reference

Pythia'nın preserved v3 snapshot'ındaki boş tokenizer adjudication'ı değişmez. Document 156,
exact aynı Pythia weight revision'ını EleutherAI/Pythia'nın immutable commit ve SHA-256 ile
dondurulmuş resmî GPT-NeoX-20B tokenizerına bağlamak için ayrı fresh-root repair kontratıdır.
Document 156 SHA-256:

```text
0e48ec4882768d92d2a88e75e8d54a7d505d95a1605b015692e31b3b9e5c8985
```

Bu cross-reference execution sonucu değildir. Document 156 için ayrı exact authorization
verilmeden push, HU tokenizer retrieval, Pythia Slurm/GPU, training veya evaluation açılamaz.
