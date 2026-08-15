# Document 163 — M1 Dose/Pareto Falcon Missing-Evaluation Recovery Execution Result (TR)

**Tarih:** 2026-08-12, Europe/Berlin  
**Contract:** Document 162 SHA-256
`4ada146f01c777a2995d6bc4901e1cbaf9bae574b9d93263440fdfe9cca355fd`  
**Sonuç:** `BLOCKED BEFORE ALLOCATION — GUPPI5 PARTITION ACCESS — FAMILY REMAINS 15/18`

## 1. Yetki ve kapsam

Kullanıcı Document 162'nin exact SHA-256'sına bağlı tek Falcon missing-evaluation recovery ve
dependency-closed summary wave'ini yetkilendirdi. Kapsam yalnız existing Falcon seed-42
checkpoint `126/210/252` cheap evaluation'ları ve yalnız bunların tamamı başarıyla biterse 18/18
family summary idi. Training, completed 15 evaluation row'u, model/data/LR/seed/threshold,
foreign jobs ve cleanup kapsam dışında kaldı.

## 2. Initial publication ve preflight

Document 151bh ve 162'nin initial implementation'ı aynı dar commit ile ordinary non-force
yayımlandı ve HU'ya preservation-checked fast-forward edildi:

```text
initial commit = 37a7d29a182f049054483915f4ceee5bc7fdd1d4
branch         = corpus-update
local suite    = 380/380 PASS
HU focused     = 100/100 PASS
```

İlk CPU preflight exact inventory'yi doğruladı:

```text
preflight = /vol/tmp2/yesildau/m1_provenance_screen_v4_dose_pareto_v1/
            preflight/falcon_recovery_37a7d29.json
SHA-256   = 37d3d4471d504f9e3d506d48c4ab1f00c99ec2c49f09dd9a7a80e0342cac9b4f
status    = PASS
rows      = 15 present / 18 required
missing   = falcon {126,210,252}
summary   = absent
duplicates = zero
target    = guppi5 / gpu:rtx3090:1 / array 2,4,5%1
```

## 3. Pre-allocation scheduler reconciliation

İlk remote shell çağrısı SSH default directory'sinde launcher bulunmadığı için exit `127` ile,
`sbatch` çalışmadan durdu. Preservation-checked repository path'inden yapılan ilk scheduler
çağrısı job yaratmadan şu hatayı verdi:

```text
sbatch: error: Batch job submission failed: Requested nodes not in this partition
```

Read-only scheduler inspection exact nedeni gösterdi:

```text
guppi5 visible partition = wbimlgpu
state                    = mix
GRES                     = gpu:rtx3090:3,mps:rtx3090:300
original launcher        = partition gpu + nodelist guppi5
gpu partition nodes      = gruenau1-2,7-10; guppi5 absent
```

Document 162 partition adını dondurmuyor; `guppi5`, `gpu:rtx3090:1`, sequential array ve bütün
bilimsel alanları donduruyor. Ayrıca ilgili Slurm/test dosyalarını implementation surface'e dahil
ediyor. Bu nedenle hiçbir job/array yaratılmadan yalnız partition binding
`gpu -> wbimlgpu` olarak düzeltildi; node, GRES, array, runtime guard ve recipe değişmedi:

```text
correction commit = 2c1e49c86b92e116cae77857b31d77293a048564
push/HU sync      = ordinary non-force / preservation-checked fast-forward
local focused     = 100/100 PASS
HU focused        = 100/100 PASS
HU status SHA     = 71a2e3b1d03a5c73ab3fb16c02e59910b7ec35f553956b079edcf71f3a3c59e9
```

## 4. Fresh preflight ve terminal submission blocker

Yeni commit kimliğine bağlı fresh preflight de exact state'i doğruladı:

```text
preflight = /vol/tmp2/yesildau/m1_provenance_screen_v4_dose_pareto_v1/
            preflight/falcon_recovery_2c1e49c.json
SHA-256   = c49e3139427030d8f20c4e1a27e0b73197e99a064e84765fbf414e6ed2643d88
status    = PASS
rows      = 15 present / 18 required
missing   = falcon {126,210,252}
summary   = absent
duplicates = zero
scratch free bytes = 123,708,663,398,400
```

Correct partition üzerindeki terminal `sbatch` çağrısı scheduler authorization gate'inde yine
job ID üretmeden fail-closed durdu:

```text
sbatch: error: Batch job submission failed:
User's group not permitted to use this partition
```

Launcher `set -euo pipefail` kullandığı için evaluation array ID'si oluşmadan dependent summary
submission satırına geçilmedi. Dolayısıyla:

```text
created evaluation arrays = 0
created evaluation tasks  = 0
created summary jobs      = 0
GPU allocations           = 0
scientific evaluations    = 0
hard-suite openings       = 0
```

Node değişimi, başka partition/GPU route'u veya yeni submission denenmedi.

## 5. Terminal artifact reconciliation

Live validator execution sonunda da aynı exact state'i verdi:

```text
available rows = 15
required rows  = 18
missing rows   = falcon {126,210,252}
active matching jobs = zero
```

Missing namespaces ve summary root absent kaldı:

```text
/vol/tmp2/yesildau/m1_provenance_screen_v4_dose_pareto_v1/evaluations/falcon/checkpoint-126
/vol/tmp2/yesildau/m1_provenance_screen_v4_dose_pareto_v1/evaluations/falcon/checkpoint-210
/vol/tmp2/yesildau/m1_provenance_screen_v4_dose_pareto_v1/evaluations/falcon/checkpoint-252
/vol/tmp2/yesildau/m1_provenance_screen_v4_dose_pareto_v1/analysis/three_model_dose_pareto_summary_v1
```

Existing cheap-gate hashes değişmedi; Falcon'ın mevcut üç row'u:

```text
step42  034c44fd2057e3198fe4438b9503be104beb9d05105a1fecea0c970eda6ba273
step84  21d9b5f1ce02d2036641e3475d1f06d26583fe40c8db96b3fa1f73abf5b4bd8f
step168 6f790d1a5bf88ca5f3209124c25816997c5c8a4403660842889ac566f284090c
```

## 6. Honest result

```text
Document 162 wave          = BLOCKED BEFORE ALLOCATION
primary operational blocker = guppi5_partition_group_access_denied
Falcon missing evaluation   = NOT RUN
three-model family          = INCOMPLETE_FALCON_EVALUATION
checkpoint rows             = 15/18
three-model summary         = NOT GENERATED
automatic primary selection = false
second recovery route/retry = NOT AUTHORIZED
seed43 / M2-A / M2-B        = NOT AUTHORIZED
cleanup/deletion            = none
```

Bu sonuç Falcon'ın scientific failure'ı değildir. Hiç model load, inference veya evaluation
başlamadı; missing değerler impute edilmedi.
