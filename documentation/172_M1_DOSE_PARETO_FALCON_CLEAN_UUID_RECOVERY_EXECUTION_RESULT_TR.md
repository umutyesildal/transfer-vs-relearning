# Document 172 — M1 Dose/Pareto Falcon Clean-UUID Recovery Execution Result (TR)

**Tarih:** 2026-08-13, Europe/Berlin  
**Contract:** Document 171 SHA-256
`b54983a5638391fec575a47f3934b4d674b9e8d655de7c6b5e8818fabc69778e`  
**Sonuç:** `NOT RUN — NO CLEAN UUID — FAILURE AUDIT NOT PERSISTED — FAMILY REMAINS 15/18`

## 1. Publication, preflight ve submission

Local implementation commit'i `8259edb6aaa9de7c853af44e658b8c1d356db7ea` ordinary
non-force push ile yayımlandı ve HU repository aynı commit'e preservation-checked fast-forward
edildi. HU focused Falcon clean-UUID suite 14/14 PASS verdi.

Fresh preflight PASS verdi:

```text
path = /vol/tmp2/yesildau/m1_provenance_screen_v4_dose_pareto_v1/
       preflight/falcon_clean_uuid_recovery_8259edb.json
SHA-256 = 01ecab114349674598fe88b09afc5fcfb83419f8c598a7d1e5904f1e3cbe2bc7
family rows = 15/18
missing = Falcon {126,210,252}
route = gruenau8|gpu|up|idle|gpu:rtxa6000:4,mps:rtxa6000:400
expected visible GPUs = 4
selection = lexicographically_smallest_clean_gpu_uuid
```

Document 171'in izin verdiği dependency-dead summary `456467` iptal edildi. `sbatch --test-only`
PASS verdi; scheduler test job ID `456500` idi. Exactly one real array ve one `afterok` summary
submit edildi:

```text
evaluation array = 456501_[2,4,5%1]
summary          = 456502
dependency       = afterok:456501
```

## 2. Runtime fail-closed result

Üç sequential task da pre-Torch selector içinde aynı exact hata ile durdu:

```text
ValueError: No clean RTX A6000 candidate satisfies the frozen process/memory gates
```

Hatanın `choose_clean_uuid(rows, apps)` içinde oluşması; dört GPU row parse'ının, initial
`CUDA_VISIBLE_DEVICES` set doğrulamasının ve dört UUID için compute-app sorgularının bu noktadan
önce tamamlandığını gösterir. Buna karşılık captured row değerleri stdout/stderr'e basılmadığı için
hangi UUID'nin hangi memory/process bileşeniyle elendiği terminal loglarından yeniden üretilemez.

Task ledger:

| Step/task | Slurm JobId | State | Elapsed | Exit |
|---|---:|---|---:|---:|
| 126 / `_2` | `456503` | FAILED | 00:00:07 | 1:0 |
| 210 / `_4` | `456504` | FAILED | 00:00:02 | 1:0 |
| 252 / `_5` | `456501` | FAILED | 00:00:02 | 1:0 |

Üç stdout da 0 byte ve SHA-256
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`; üç stderr de 690 byte
ve SHA-256 `763ed0b2589f6c939347aca4f7a2dcebbca42ec82fd0b3040ca03ba4b051aad7`'dir.

## 3. Audit-persistence contract breach

Document 171 §4, failure olsa bile dört-device/selection evidence'ın korunmasını zorunlu kılar.
Implementation ise audit JSON'u ancak `choose_clean_uuid` başarılı bir winner döndürdükten sonra
yazmaktadır. No-candidate exception bu yazımdan önce oluştuğu için üç zorunlu audit manifest'i
absent kaldı:

```text
falcon_clean_uuid_audit_126_456501_2.json = absent
falcon_clean_uuid_audit_210_456501_4.json = absent
falcon_clean_uuid_audit_252_456501_5.json = absent
```

Dolayısıyla fail-closed safety davranışı korundu, fakat Document 171'in failure-evidence
persistansı karşılanmadı. Bu sonuç temiz GPU bulunmadığını task anında kanıtlayan exception
evidence'ını korur; dört cihazın exact UUID/memory/process ledger'ını korumaz.

## 4. Scientific ve dependency closure

Selector failure'ı runtime validator, evaluator namespace preparation ve model load'dan önce
oluştu. Üç runtime manifest, üç evaluation root ve family summary root absent kaldı. Inference,
exact/PPL/hard evaluation ve scientific row üretimi olmadı; family inventory `15/18` kaldı.

Summary job `456502`:

```text
state  = PENDING
reason = DependencyNeverSatisfied
root   = absent
```

Document 171 yalnız eski `456467` cancellation'ını yetkilendirdi; yeni dead summary'ye müdahale
edilmedi. İkinci array veya retry submit edilmedi.

## 5. Preservation

```text
HU HEAD        = 8259edb6aaa9de7c853af44e658b8c1d356db7ea
family root    = 168,515,683,839 bytes (`du -sb`)
/vol/tmp2 free = 123,657,891,348,480 bytes
inode use      = 3%
cleanup/deletion = none
```

Bu operasyonel NOT-RUN ve audit-persistence failure sonucudur; Falcon scientific score değildir.
