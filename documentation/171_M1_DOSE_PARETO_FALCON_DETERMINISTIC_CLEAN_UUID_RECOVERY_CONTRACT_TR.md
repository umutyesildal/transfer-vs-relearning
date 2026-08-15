# Document 171 — M1 Dose/Pareto Falcon Deterministic Clean-UUID Recovery Contract (TR)

**Tarih:** 2026-08-13, Europe/Berlin  
**Durum:** `FROZEN — UNEXECUTED — SINGLE RECOVERY WAVE`

## 1. Amaç

Document 168 exclusive allocation'ı requested one GPU yerine dört RTX A6000 görünür kıldı ve
runtime exact-one-device gate'inde durdu. Bu kontrat yalnız missing Falcon checkpoint
`126/210/252` evaluation'ını, Torch importundan önce dört cihazı audit edip temiz tek UUID'yi
deterministik bağlayarak bir kez daha açar.

Training, checkpoint, BF16, seed 42, model/data/runtime identity, existing 15 evaluation,
thresholds ve summary logic değişmez.

## 2. Allocation ve pre-Torch audit

```text
partition             = gpu
node                  = gruenau8
GRES request          = gpu:rtxa6000:1
node allocation       = --exclusive
expected visible GPUs = exactly 4 NVIDIA RTX A6000
array                 = 2,4,5%1
```

Python selector Torch/CUDA import etmeden `nvidia-smi` ile görünür dört GPU'nun index, UUID, exact
name, total/free/used memory ve compute-app rows'unu toplar. Her UUID unique ve canonical olmalı;
query/parse failure fail-closed'dur. Slurm'un başlangıç `CUDA_VISIBLE_DEVICES` değeri tam dört
unique token içermeli ve bu küme audit edilen dört index kümesine veya dört UUID kümesine birebir
eşit olmalıdır; node'daki foreign physical GPU'lar allocation-visible sayılmaz.

Clean candidate:

```text
name                     = NVIDIA RTX A6000
compute-app rows         = exactly 0 for that UUID
free VRAM                >= 42,949,672,960 bytes
used VRAM                <= 536,870,912 bytes
```

En az bir clean candidate yoksa task durur. Birden fazla varsa **lexicographically smallest GPU
UUID** seçilir. Free memory'ye göre winner seçmek, first-visible seçmek veya response-dependent
fallback yasaktır. Dört-GPU audit artifact'i atomik yazıldıktan sonra shell
`CUDA_VISIBLE_DEVICES=<selected UUID>` yapar. Ardından mevcut runtime validator exact one visible
CUDA device, RTX A6000, CC 8.6, `sm_86`, BF16, 40 GiB free-memory ve finite probe gate'lerini
yeniden çalıştırır.

## 3. Fresh preflight ve job reconciliation

Fresh preflight exact implementation commit/Document 171 SHA, 15/18 inventory, absent missing
roots, absent family summary, preserved existing row hashes, route/storage/no-home-write ve
duplicate-job gate'lerini doğrular. Dependency-dead summary `456467` yalnız bu exact preflight
PASS'ten sonra ve real submit öncesinde iptal edilebilir. Başka job iptal edilemez.

Submission sırası:

```text
fresh preflight
exact 456467 reconciliation/cancellation if still dependency-dead
sbatch --test-only PASS
exactly one 2,4,5%1 evaluation array
exactly one afterok summary
```

Herhangi bir failure'da ikinci array veya retry yoktur.

## 4. Artifact ve scientific bounds

GPU audit artifact'i evaluator root dışında runtime manifest namespace'inde yazılır; failure olsa
bile dört-device/selection evidence korunur. Evaluation root GPU/runtime gates geçmeden yaratılmaz.
Hard suite yalnız exact+PPL gate açarsa çalışır. Summary 18/18 unique cheap rows olmadan root
yaratamaz ve primary modeli otomatik seçemez.

## 5. Yasaklar ve authorization

Falcon training/checkpoint mutation, completed evaluation rerun, OLMo/Pythia, seed-43,
precision/LR/threshold/recipe change, başka node/GPU route, ikinci array, başka job cancellation,
corpus, Turkish dose, M2-A/M2-B, cleanup ve deletion yasaktır.

Bu preparation publication, HU synchronization, `456467` cancellation, Slurm/GPU veya execution
yetkisi vermez. Tek wave için Document 171 exact SHA-256'sına bağlı açık kullanıcı izni gerekir.
Documents 172/173 result/gate için ayrılmıştır.
