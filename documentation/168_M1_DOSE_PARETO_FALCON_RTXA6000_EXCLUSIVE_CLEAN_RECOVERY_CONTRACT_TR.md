# Document 168 — M1 Dose/Pareto Falcon RTX A6000 Exclusive Clean Recovery Contract (TR)

**Tarih:** 2026-08-13, Europe/Berlin  
**Durum:** `FROZEN — UNEXECUTED — SINGLE RECOVERY WAVE`

## 1. Amaç ve korunan bilimsel durum

Document 165 wave'i exact `gruenau8/gpu/gpu:rtxa6000:1` allocation aldı; fakat üç task da 40 GiB
minimuma karşı yalnız 3,142,844,416 free byte gördüğü için evaluator başlamadan durdu. Aile 15/18
ve eksikler yalnız Falcon checkpoint `126/210/252`'dir.

Bu kontrat yalnız aynı üç missing evaluation'ı temiz allocation kanıtıyla bir kez daha açar.
Falcon training'i, checkpoint'leri, mevcut 15 evaluation row'u, BF16, model/data/runtime identity,
seed 42, thresholds, evaluation cascade ve summary logic değişmez.

## 2. Exact job kapsamı

```text
partition                 = gpu
node                      = gruenau8
GRES                      = gpu:rtxa6000:1
Slurm node allocation     = --exclusive
array                     = 2,4,5%1
steps                     = 126,210,252
scientific evaluation jobs = exactly one array
summary jobs              = exactly one afterok job
second array/retry        = forbidden
```

Document 165'in dependency-dead summary job'u `456415`, yeni preflight bütün 15/18 ve absent-root
kontrollerini geçtikten sonra ve yeni submit'ten hemen önce iptal edilebilir. Başka hiçbir user,
foreign, training, evaluation veya summary job iptal edilemez.

## 3. Clean-allocation runtime evidence

Her array task evaluator namespace yaratmadan önce yalnız allocated CUDA device için şu evidence'i
stdout ve runtime manifest'e bağlar:

```text
SLURM_JOB_ID / SLURM_ARRAY_JOB_ID / SLURM_ARRAY_TASK_ID
SLURM_JOB_NODELIST / CUDA_VISIBLE_DEVICES
GPU index and UUID
GPU name = NVIDIA RTX A6000
compute capability = 8.6
compiled arch contains sm_86
total/free/used VRAM bytes
compute-app rows = exactly zero
minimum free VRAM = 42,949,672,960 bytes
maximum used VRAM before probe = 536,870,912 bytes
```

`CUDA_VISIBLE_DEVICES` tam bir logical CUDA device'a çözülmeli; `torch.cuda.device_count()` tam 1
olmalıdır. `nvidia-smi --query-compute-apps` başarısız, parse edilemez veya non-empty ise task
fail-closed durur. UUID, `nvidia-smi` ve Torch device identity eşleşmelidir. Runtime evidence
başarıyla ve atomik yazılmadan model load/evaluator preparation başlayamaz.

`--exclusive`, kendi başına temizlik kanıtı değildir; yalnız runtime process/memory gate ile
birlikte kabul edilir.

## 4. Preflight ve submission

Fresh preflight şunları zorunlu kılar:

- exact implementation commit ve bu Document 168 SHA binding;
- original family root, complete Falcon training ve checkpoint `126/210/252` varlığı;
- exact 15/18 existing row identity ve missing evaluation root'larının absent olması;
- summary root absent;
- active duplicate evaluation/recovery/summary job olmaması; yalnız exact dead `456415`
  reconciliation kaydı;
- `gruenau8/gpu/gpu:rtxa6000` route görünürlüğü;
- scratch capacity/inode ve no-home-write policy;
- `sbatch --test-only` PASS.

Sıra: fresh preflight → exact `456415` cancellation/reconciliation → `sbatch --test-only` → tek
real array → tek `afterok` summary. Bir adım başarısızsa sonraki submit yapılmaz.

## 5. Dependency-closed completion

Summary yalnız array `afterok` bağıyla çalışır ve 18/18 unique cheap-gate row bulunmadan output
root yaratamaz. Missing değerler impute edilmez; completed evaluation tekrar edilmez. Hard suite
yalnız mevcut exact+PPL gate açarsa çalışır. Summary hiçbir modeli otomatik primary yapmaz.

## 6. Yasaklar

Bu kontrat Falcon training rerun, checkpoint mutation, completed evaluation rerun, OLMo/Pythia
work, seed-43, threshold/LR/precision/recipe değişimi, ikinci recovery array, başka job
cancellation, corpus, Turkish dose ladder, M2-A/M2-B, cleanup veya deletion yetkisi vermez.

Bu belgenin hazırlanması publication, HU synchronization, `456415` cancellation, Slurm/GPU veya
execution yetkisi değildir. Tek wave ancak kullanıcının Document 168 exact SHA-256'sına bağlı açık
yetkisiyle çalıştırılabilir. Documents 169/170 result/gate için ayrılmıştır.
