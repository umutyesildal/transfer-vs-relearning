# Document 161 — M1 Dose/Pareto Post-Execution Gate (TR)

**Tarih:** 2026-08-12, Europe/Berlin  
**Related result:** Document 160  
**Gate:** `OLMo NEGATIVE; FAMILY BLOCKED BY THREE MISSING FALCON EVALUATIONS`

## 1. OLMo gate

Document 159b'nin BF16 repair'ı runtime ve scientific execution bakımından geçerlidir. Smoke,
training ve altı-checkpoint evaluation tamamlanmıştır. OLMo bütün checkpoint'lerde 100% exact
acquisition almış, fakat frozen PPL-ratio `<=1.25` gate'ini hiçbir checkpoint'te geçememiştir.

```text
OLMo execution validity = PASS
OLMo retention gate     = FAIL
OLMo hard-stage opening = 0/6
OLMo eligible nominee   = none
OLMo classification     = VALID SCIENTIFIC NEGATIVE
```

Precision repair limitation korunur: OLMo v4 BF16 result, historical FP16 endpoint ile bitwise
eşitlik karşılaştırması değildir. Aynı model/data/LR/effective-batch/update/checkpoint/gate recipe'i
korunduğu için frozen dose/Pareto sorusuna geçerli negatif kanıt sağlar.

## 2. Family gate

Pythia'nın 6/6 cheap gate'i complete ve retention-negative'dir. Falcon training complete olmasına
rağmen yalnız checkpoint 42, 84 ve 168 cheap gate'leri vardır. Checkpoint 126, 210 ve 252 görevleri
contaminated/low-free-VRAM allocation'da runtime preflight tarafından scientific evaluation
öncesi durdurulmuştur.

```text
required checkpoint rows = 18
available checkpoint rows = 15
missing rows              = falcon {126,210,252}
summary readiness         = false
family decision           = BLOCKED_INCOMPLETE_FALCON_EVALUATION
```

Bu blocker Falcon modelinin bilimsel failure'ı değildir. Missing değerler observed PPL trendinden
impute edilmez. Summary script'in required evidence'i eksik olduğundan summary artifact'i
oluşturulmamıştır.

## 3. Current project decision

```text
selected English-centric M1 model = none
automatic primary promotion       = false
seed43 replication                = CLOSED / NOT AUTHORIZED
Turkish dose ladder               = CLOSED / NOT AUTHORIZED
M2-A/M2-B                         = CLOSED / NOT AUTHORIZED
ready_to_train                    = false
```

Corpus hattındaki vngrs statüsü ve measurement-design blocker'ları bu M1 sonucu ile değişmez.

## 4. Minimal next action

Tek savunulabilir sonraki M1 işi, yeni exact SHA-bound contract altında yalnız Falcon'un üç eksik
cheap evaluation task'ını clean RTX3090 allocation/guard ile çalıştırmak, existing 15 gate'i
yeniden çalıştırmamak ve ancak 18/18 rows present olduktan sonra frozen summary üretmektir.

Bu recovery:

- Falcon training'i tekrar çalıştırmamalı;
- OLMo/Pythia evaluation'larını tekrar çalıştırmamalı;
- hard suite'i yalnız checkpoint exact+PPL gate'i geçerse açmalı;
- threshold, model, dataset, prompt, seed veya checkpoint grid değiştirmemeli;
- outcome-aware shard/GPU/checkpoint seçmemeli;
- existing roots ve failed logs'u korumalıdır.

Document 161 tek başına bu recovery'yi, yeni Slurm submission'ı veya summary execution'ı authorize
etmez. Yeni frozen contract ve exact kullanıcı onayı gerekir.
