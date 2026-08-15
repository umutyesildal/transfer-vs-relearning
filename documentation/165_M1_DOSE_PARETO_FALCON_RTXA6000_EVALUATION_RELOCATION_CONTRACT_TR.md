# Document 165 — M1 Dose/Pareto Falcon RTX A6000 Evaluation Relocation Contract (TR)

**Tarih:** 2026-08-13, Europe/Berlin  
**Durum:** `FROZEN — UNEXECUTED — EXACT SHA-BOUND AUTHORIZATION REQUIRED`

## 1. Gerekçe ve tek amaç

Documents 163/164, Document 162 recovery'sinin exact 15/18 inventory preflight'lerini geçtiğini,
ancak frozen `guppi5` route'unun `wbimlgpu` partition group access gate'inde hiçbir job ID
oluşturmadan durduğunu kaydeder. Falcon checkpoint `126/210/252` evaluation roots ve family
summary hâlâ absent'tir.

Read-only live scheduler inspection, local `gpu` partition'ında erişilebilir
`gruenau8 / gpu:rtxa6000` kapasitesini göstermiştir. Bu contract'ın tek amacı:

> Existing Falcon seed-42 checkpoint'lerini değiştirmeden yalnız missing `126/210/252` cheap
> evaluation'larını bir RTX A6000 allocation üzerinde tamamlamak ve ancak 18/18 row varsa frozen
> family summary üretmek.

Bu training retry veya scientific recipe change değildir.

## 2. Immutable scientific identity

Documents 159/159a/159b/162'nin tüm bilimsel alanları korunur:

```text
model/revision   = tiiuae/falcon-rw-1b@e4b9872bb803165eb22f0a867d4e6a64d34fce19
training run     = existing single completed Falcon v4 seed-42 run
data             = frozen 3,500 train / 500 validation, 500 facts
LR/batch/updates = 5e-5 / 500 / 252
checkpoint grid  = 42,84,126,168,210,252
evaluation       = exact-prefix -> WikiText-2 PPL/generic integrity -> conditional hard suite
gates            = exact >=0.90; PPL ratio <=1.25; existing robust thresholds unchanged
```

Training checkpoints, completed 15 gates, prompts, evaluator, thresholds ve tie-breaker
read-only korunur.

## 3. Exact relocation binding

```text
partition          = gpu
node               = gruenau8
GRES               = gpu:rtxa6000:1
expected GPU name  = RTX A6000
compute capability = 8.6
compiled arch      = sm_86
precision          = existing Falcon BF16 evaluation binding
minimum free VRAM  = 40 GiB before evaluator preparation
array              = 2,4,5%1
mapping            = 2->126, 4->210, 5->252
network            = offline
```

`gruenau8` live idle observation execution garantisi değildir. Scheduler pending bırakabilir;
yanlış node/GPU, `<40 GiB` free VRAM, foreign process contamination veya runtime drift evaluator
namespace yaratılmadan fail-closed durur. `guppi5/6/7/8`, `wbimlgpu`, `viscomgpu` ve başka GPU
route'u kullanılmaz.

## 4. Mandatory access and inventory preflight

Execution öncesi fresh CPU preflight şu exact state'i doğrular:

```text
required/present rows      = 18 / 15
OLMo/Pythia present        = six each
Falcon present             = 42,84,168
Falcon absent              = 126,210,252
summary root               = absent
active duplicates          = zero
partition/node/GRES view   = gpu / gruenau8 / gpu:rtxa6000
```

Real submission'dan önce aynı exports/script üzerinde `sbatch --test-only` zorunludur. Non-zero
veya access/partition/node/GRES rejection olursa gerçek `sbatch` çalışmaz. Test-only job ID
yaratmaz ve scientific attempt değildir.

## 5. Tek evaluation array ve summary

Preflight ve test-only PASS sonrası exactly one real `2,4,5%1` array submit edilir. Her task:

- exact commit/preflight/contract SHA binding'i;
- Python/Torch/CUDA/BF16/compute-capability/compiled-arch;
- exact RTX A6000 identity ve 40 GiB free-VRAM guard;
- kendi absent checkpoint namespace'i;
- frozen cheap/hard evaluation cascade

kontrollerini yapar. Bir task fail olursa ikinci array/retry yoktur.

Summary job yalnız `afterok:<array>` ile submit edilir ve 18/18 exact cheap-gate path'i olmadan
fail olur. Existing tie-break ve `automatic_primary_promotion=false` korunur. Summary root:

```text
/vol/tmp2/yesildau/m1_provenance_screen_v4_dose_pareto_v1/
analysis/three_model_dose_pareto_summary_v1
```

## 6. Implementation surface

Append-only implementation yalnız şu yüzeylerdir:

```text
src/transfer_vs_relearning/experiments/m1_dose_pareto.py
scripts/validate_m1_dose_pareto_runtime.py
scripts/preflight_m1_dose_pareto_falcon_rtxa6000_recovery.py
scripts/submit_m1_dose_pareto_falcon_rtxa6000_recovery.sh
slurm/eval_m1_dose_pareto_falcon_recovery_rtxa6000.slurm
slurm/summarize_m1_dose_pareto_falcon_recovery_rtxa6000.slurm
tests/test_m1_dose_pareto.py
```

Tests exact 15/18 inventory, `gpu/gruenau8/rtxa6000`, 40 GiB guard, runtime override'ın yalnız
Falcon + exact Document 165 SHA için açılması, `sbatch --test-only` before real submit,
`2,4,5%1`, no-training/no-cleanup ve `afterok` dependency'sini kanıtlar.

## 7. Future execution sırası

Yeni exact SHA-bound kullanıcı yetkisi verilirse:

1. local focused/compatible tests;
2. narrow commit ve ordinary non-force push;
3. HU preservation/status/path-overlap ve fast-forward only;
4. fresh exact 15/18/storage/inode/duplicate/route preflight;
5. preflight SHA freeze;
6. exact script için `sbatch --test-only`;
7. exactly one real `2,4,5%1` evaluation array;
8. exactly one `afterok` summary job;
9. terminal artifact/log/hash/storage verification;
10. reserved Documents 166/167 execution result/gate.

## 8. Kapsam dışı

Training rerun, completed 15 evaluation'ın rerun'ı, new checkpoint/LR/prompt/data/seed/threshold,
outcome-aware selection, second array, automatic primary promotion, seed-43, Turkish corpus/dose,
M2-A/M2-B, foreign-job action, cleanup/deletion kapsam dışıdır.

Bu belge tek başına publication, HU/SSH, Slurm/GPU, evaluation veya summary execution yetkisi
vermez.
