# Document 174 — M1 Dose/Pareto Falcon Audit-Persistent Single-Allocation Recovery Contract (TR)

**Tarih:** 2026-08-13, Europe/Berlin  
**Durum:** `FROZEN — UNEXECUTED — SINGLE RECOVERY WAVE`

## 1. Amaç ve değişmeyen bilimsel kapsam

Document 171 dalgası clean candidate bulamadığı için bilimsel değerlendirmeden önce doğru biçimde
durdu; fakat selector no-candidate exception'ından önce dört-GPU audit JSON'unu yazmadı. Bu
kontrat yalnız bu evidence-persistence hatasını düzeltir ve missing Falcon checkpoint
`126/210/252` evaluation'ını aynı temiz fiziksel UUID üzerinde, tek allocation içinde sıralı olarak
bir kez daha açar.

Falcon training/checkpoint'leri, BF16, seed 42, model/data/runtime identity, mevcut 15 cheap row,
threshold'lar, exact/PPL/hard cascade ve summary logic değişmez. Completed evaluation tekrar
edilmez.

## 2. Allocation, audit ve binding

```text
partition             = gpu
node                  = gruenau8
GRES request          = gpu:rtxa6000:1
node allocation       = --exclusive
job shape             = one non-array job
evaluation order      = 126 -> 210 -> 252
expected visible GPUs = exactly 4 NVIDIA RTX A6000
```

Selector Torch/CUDA importundan önce dört görünür GPU için index, canonical UUID, exact name,
total/free/used memory, initial `CUDA_VISIBLE_DEVICES` binding ve compute-app rows toplar. GPU
query/parse/binding tamamlandıktan sonra selector, candidate selection'dan **önce** bütün dört-GPU
ledger'ını atomik olarak output path'e yazar.

Clean predicate değişmez:

```text
compute-app rows = exactly 0
free VRAM        >= 42,949,672,960 bytes
used VRAM        <= 536,870,912 bytes
winner           = lexicographically smallest clean GPU UUID
```

Hiç candidate yoksa manifest status'u `BLOCKED_NO_CLEAN_CANDIDATE`, `selected_uuid=null` ve her
GPU için exact rejection reason içerir; selector non-zero çıkar. PASS halinde aynı ledger
`status=PASS` ve selected UUID ile atomik tamamlanır. Shell yalnız PASS sonrasında
`CUDA_VISIBLE_DEVICES=<selected UUID>` yapar. Mevcut runtime validator exact one visible device,
RTX A6000, CC 8.6, `sm_86`, BF16, zero compute-app, 40 GiB free-memory ve finite probe gate'lerini
çalıştırır.

Tek allocation içinde seçilen UUID üç checkpoint boyunca değiştirilemez. Her checkpoint için ayrı
runtime manifest yazılır; bir failure sonraki checkpoint'lere ve summary'ye geçişi keser.

## 3. Preflight, reconciliation ve dependency closure

Fresh preflight exact implementation commit/Document 174 SHA, exact 15/18 inventory, absent
missing roots, absent family summary, preserved existing row hashes, storage/path/inode,
no-home-write ve duplicate-job gates'ini doğrular. Dependency-dead summary `456502` yalnız exact
preflight PASS'ten sonra ve real submission öncesinde iptal edilebilir; başka job iptal edilemez.

Submission sırası:

```text
fresh preflight
exact 456502 reconciliation/cancellation if still dependency-dead
sbatch --test-only PASS
exactly one sequential evaluation job
exactly one afterok summary
```

Herhangi bir failure'da ikinci evaluation job, array veya automatic retry yoktur. Summary yalnız
evaluation job'u tamamen PASS olursa çalışır ve 18/18 unique cheap row olmadan root yaratamaz.

## 4. Artifact ve fail-closed sınırlar

Audit manifest evaluator root dışında runtime-manifest namespace'inde yaşar. Query/parse/binding
failure'ında mümkün olan en son doğrulanmış aşama stderr ile korunur; dört-device query ve binding
tamamlandıysa candidate PASS/FAIL fark etmeksizin dört-GPU ledger zorunludur. Evaluation root GPU
ve runtime gates geçmeden yaratılmaz. Hard suite yalnız exact+PPL gate açarsa çalışır; summary
primary modeli otomatik seçemez.

## 5. Yasaklar ve authorization

Training/checkpoint mutation veya rerun, completed evaluation rerun, OLMo/Pythia, seed-43,
precision/LR/threshold/recipe change, başka node/GPU route, ikinci job/array, başka job cancellation,
polling/threshold relaxation, corpus, Turkish dose, M2-A/M2-B, cleanup ve deletion yasaktır.

Bu local preparation push/publication, HU/SSH, `456502` cancellation, Slurm/GPU veya execution
yetkisi vermez. Tek wave için Document 174 final exact SHA-256'sına bağlı açık kullanıcı izni
gerekir. Documents 175/176 result/gate için ayrılmıştır.
