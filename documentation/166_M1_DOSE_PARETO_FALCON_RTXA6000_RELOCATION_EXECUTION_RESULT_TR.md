# Document 166 — M1 Dose/Pareto Falcon RTX A6000 Relocation Execution Result (TR)

**Tarih:** 2026-08-13, Europe/Berlin  
**Contract:** Document 165 SHA-256
`e8e1d772ed7726e959f5ec5e24d81f1a4a3aeed2973f6aa3bbe5c22b078e9fda`  
**Sonuç:** `NOT RUN — ALLOCATION-TIME LOW FREE VRAM — FAMILY REMAINS 15/18`

## 1. Yetki ve preparation

Kullanıcı Document 165'in exact SHA-256'sına bağlı tek Falcon RTX A6000 missing-evaluation
recovery ve dependency-closed summary wave'ini açıkça yetkilendirdi. Shared implementation
commit `68e5be9b1c15a86c8dc8071d55c5de2789600c75` ordinary non-force push ve
preservation-checked HU fast-forward ile yayımlandı. Local complete suite `382/382`, HU focused
suite `102/102` geçti; existing dirty state değişmedi.

## 2. Fresh preflight

Preflight artifact:

```text
/vol/tmp2/yesildau/m1_provenance_screen_v4_dose_pareto_v1/
preflight/falcon_rtxa6000_recovery_68e5be9.json
SHA-256 = 2e8e46c906948de47fd86dff4c3aca2878f057abc387de524bae1a761c23196b
```

Frozen preflight PASS:

```text
rows                     = 15 present / 18 required
missing                  = falcon {126,210,252}
summary root             = absent
duplicates               = zero
route                    = gruenau8|gpu|up|idle|gpu:rtxa6000:4,mps:rtxa6000:400
requested GRES           = gpu:rtxa6000:1
minimum task free VRAM   = 42,949,672,960 bytes
relocation contract SHA  = exact Document 165
```

## 3. Submission ledger

Mandatory `sbatch --test-only` PASS verdi:

```text
test-only scheduler job = 456413
predicted start         = 2026-08-13T13:46:07
node/partition          = gruenau8 / gpu
```

Exactly one real array ve exactly one dependency-closed summary submit edildi:

```text
evaluation array = 456414_[2,4,5%1]
summary job      = 456415
dependency       = afterok:456414
```

İkinci array/retry submit edilmedi.

## 4. Runtime fail-closed result

Üç task sırasıyla `gruenau8` üzerinde exact `gpu:rtxa6000:1` GRES allocation aldı. Runtime
validator her task'ta aynı free-memory değerini gözledi:

```text
observed free VRAM = 3,142,844,416 bytes
required free VRAM = 42,949,672,960 bytes
result             = ValueError: Insufficient free VRAM: 3142844416
```

Task states:

| Step / task | Slurm task | State | Elapsed | Exit |
|---|---:|---|---:|---:|
| 126 / `_2` | `456416` (`ArrayJobId=456414`) | FAILED | 00:00:14 | 1:0 |
| 210 / `_4` | `456419` (`ArrayJobId=456414`) | FAILED | 00:00:04 | 1:0 |
| 252 / `_5` | `456414` | FAILED | 00:00:04 | 1:0 |

Allocation-time free VRAM guard evaluator preparationından önce çalıştığı için scientific
evaluation başlamadı. Low-free-memory'nin başka process, GRES isolation veya node-local state
nedeni bu wave tarafından doğrudan ölçülmedi; yalnız observed 3.14 GB kanıtı raporlanır.

Üç stdout boş ve aynı SHA-256'dır:

```text
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

Üç 401-byte stderr aynı SHA-256'dır:

```text
f7fec397a1914271606bb08a25930282f0a55df8c96544cc257bbbf6d9870330
```

## 5. Dependency-closed summary ve artifacts

Array başarısız olduğu için summary:

```text
job     = 456415
state   = PENDING
reason  = DependencyNeverSatisfied
details = afterok:456414_*(failed)
```

Document 165 cleanup/cancellation yetkisi vermediğinden dead dependency job'una müdahale
edilmedi. Summary script çalışmadı ve summary root absent kaldı.

Üç evaluation root da absent kaldı:

```text
evaluations/falcon/checkpoint-126
evaluations/falcon/checkpoint-210
evaluations/falcon/checkpoint-252
```

Runtime manifest yazılmadı. Launcher yalnız üç boş task tmp directory ve scratch loglarını
oluşturdu; cleanup yapılmadı.

## 6. Terminal reconciliation

```text
available/required rows = 15 / 18
family root bytes       = 168,515,664,567
/vol/tmp2 free bytes    = 123,657,891,348,480
/vol/tmp2 inode use     = 3%
HU HEAD                 = 68e5be9b1c15a86c8dc8071d55c5de2789600c75
HU status               = 42 entries / 6,989 bytes / exact preserved SHA-256
sacct                    = unavailable, existing Munge/SlurmDBD auth failure
```

## 7. Honest result

```text
Document 165 execution       = NOT RUN SCIENTIFICALLY
array submission             = consumed
runtime guard                = FAIL / low free VRAM
Falcon evaluations           = 0/3 started
family rows                  = 15/18
summary                      = NOT GENERATED
automatic primary promotion  = false
second retry                 = NOT AUTHORIZED
cleanup/deletion             = none
```

Bu Falcon scientific failure değildir; model load/inference/evaluation gerçekleşmedi ve missing
değerler impute edilmedi.
