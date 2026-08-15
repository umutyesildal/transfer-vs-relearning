# Document 162 — M1 Dose/Pareto Falcon Missing-Evaluation Recovery Contract (TR)

**Tarih:** 2026-08-12, Europe/Berlin  
**Durum:** `FROZEN — UNEXECUTED — EXACT SHA-BOUND AUTHORIZATION REQUIRED`

## 1. Gerekçe ve tek amaç

Documents 160/161, OLMo ve Pythia'nın altışar cheap gate'ini tamamladığını; Falcon training'in
complete olmasına rağmen yalnız checkpoint 42/84/168 gate'lerinin mevcut olduğunu kaydeder.
Falcon checkpoint 126/210/252 görevleri (`453302_2/_4/_5`) scientific evaluation başlamadan
free-VRAM runtime guard'da durmuş, aynı stderr SHA'sını üretmiştir. Aile 15/18 row'dur ve summary
oluşturulmamıştır.

Bu contract'ın tek amacı:

> Existing Falcon seed-42 training checkpoint'lerini değiştirmeden yalnız missing
> 126/210/252 cheap evaluation'larını clean RTX3090'da tamamlamak ve ancak 18/18 row varsa frozen
> family summary üretmek.

Bu bir training retry, scientific recipe change veya outcome-aware checkpoint search değildir.

## 2. Immutable scientific identity

Documents 159/159a/159b'nin bütün bilimsel alanları korunur:

```text
model/revision   = tiiuae/falcon-rw-1b@e4b9872bb803165eb22f0a867d4e6a64d34fce19
training run     = existing single completed Falcon v4 seed-42 run
dataset          = frozen 3,500 train / 500 validation, 500 facts
LR               = 5e-5
effective batch  = 500
updates          = 252
checkpoint grid  = 42,84,126,168,210,252
evaluation       = exact-prefix -> WikiText-2 PPL/generic integrity -> conditional hard suite
gates            = exact >=0.90; PPL ratio <=1.25; existing robust thresholds unchanged
```

Base summaries, training checkpoints, completed 15 cheap gates, prompts, evaluators, thresholds ve
tie-breaker değişmez ve read-only korunur.

## 3. Frozen recovery inventory

CPU preflight execution öncesi exact state'i fail-closed doğrular:

```text
required rows             = 18
present rows              = 15
OLMo present              = 42,84,126,168,210,252
Pythia present            = 42,84,126,168,210,252
Falcon present            = 42,84,168
Falcon absent namespaces  = 126,210,252
family summary root       = absent
active duplicate jobs     = zero
```

Present cheap/final gate identity ve SHA-256 ledger'ı preflight JSON'a yazılır. Missing Falcon
evaluation root'larından biri mevcut, completed row sayısı 15 dışında, summary root existing veya
training checkpoint inventory drift etmişse wave başlamaz.

## 4. Tek GPU evaluation array'i

Exactly one Slurm array:

```text
task indices       = 2,4,5
checkpoint mapping = 2->126, 4->210, 5->252
throttle           = 1
node               = guppi5
GRES               = gpu:rtx3090:1
precision          = existing Falcon BF16 evaluation binding
minimum free VRAM  = 20 GiB before evaluator preparation
network            = offline
```

Her task exact runtime Python/Torch/CUDA/compute capability/template/scratch binding'ini ve finite
BF16 probe'u yeniden doğrular. Runtime gate evaluator namespace yaratılmadan önce çalışır. Task
yalnız kendi absent checkpoint root'unu oluşturabilir. `guppi6` ve historical guppi7 dirty UUID
route'u kullanılmaz; foreign process/job'a dokunulmaz.

Array task'larından biri yanlış GPU, `<20 GiB` free VRAM, namespace collision, hash drift,
non-finite evaluation veya evaluator failure görürse yalnız o task fail-closed durur. Contract
ikinci array/retry yetkisi vermez.

## 5. Frozen evaluation cascade

Her missing checkpoint için mevcut launcher semantiği korunur:

1. exact-prefix evaluation;
2. frozen WikiText-2 PPL ve generic/integrity evaluation;
3. cheap gate;
4. yalnız exact ve PPL gate birlikte PASS ise hard suite/final gate.

Observed Falcon 42/84/168 sonuçları yeni tasks için branch kararı vermez. Missing PPL impute
edilmez, threshold değişmez ve hard suite cheap failure sonrasında zorla açılmaz.

## 6. Dependency-closed family summary

Tek summary job yalnız `afterok:<recovery-array>` dependency'siyle submit edilir. Summary script:

- 18/18 exact cheap-gate paths olmadan fail olur;
- hard-open row için final gate yoksa fail olur;
- output root existing ise fail olur;
- existing earliest-all-gates ve model tie-break rules'u uygular;
- Document 162 final SHA-256'sını summary JSON'a bağlar;
- `automatic_primary_promotion=false` kuralını korur.

Summary output:

```text
/vol/tmp2/yesildau/m1_provenance_screen_v4_dose_pareto_v1/
analysis/three_model_dose_pareto_summary_v1
```

Summary sonucu bir model nominee üretse bile seed-43 veya primary promotion otomatik açılmaz.

## 7. Implementation surface

Append-only local implementation yalnız şu yeni/değişen yüzeylerdir:

```text
src/transfer_vs_relearning/experiments/m1_dose_pareto.py
scripts/preflight_m1_dose_pareto_falcon_recovery.py
scripts/submit_m1_dose_pareto_falcon_recovery.sh
scripts/summarize_m1_dose_pareto.py
slurm/eval_m1_dose_pareto_falcon_recovery_rtx3090.slurm
slurm/summarize_m1_dose_pareto_falcon_recovery.slurm
tests/test_m1_dose_pareto.py
```

Code preflight/summary evidence'ini bu Document 162'nin final SHA-256'sına bağlar. Tests exact
15/18 inventory, missing-root collision rejection, only-array `2,4,5`, guppi5/RTX3090 binding,
no-training/no-cleanup ve afterok summary dependency'sini doğrular.

## 8. Future execution sırası

Yeni exact SHA-bound kullanıcı yetkisi verilirse:

1. local focused/compatible tests;
2. narrow commit ve ordinary non-force push;
3. HU preservation/status/path-overlap checks ve fast-forward only;
4. exact 15/18/no-duplicate/storage/inode preflight;
5. preflight JSON hash freeze;
6. exactly one `2,4,5%1` evaluation array;
7. exactly one dependency-closed summary job;
8. terminal artifact/log/hash/storage verification;
9. reserved Documents 163/164 execution result/gate.

No reset, merge, force push, cancellation of foreign jobs veya cleanup yapılır.

## 9. Scope dışı

- Falcon/OLMo/Pythia training rerun;
- completed 15 checkpoint evaluation'ının rerun'ı;
- new checkpoint, LR, prompt, data, seed veya threshold;
- outcome-aware GPU/checkpoint selection;
- seed-43 veya automatic primary promotion;
- Turkish corpus/dose, M2-A/M2-B;
- deletion/cleanup veya prior-artifact mutation;
- ikinci recovery array/retry.

Bu belge tek başına push, HU/SSH, Slurm/GPU, evaluation veya summary execution yetkisi vermez.
