# Document 175 — M1 Dose/Pareto Falcon Audit-Persistent Recovery Execution Result (TR)

**Tarih:** 2026-08-13, Europe/Berlin  
**Contract:** Document 174 SHA-256
`75964edfdd4e3d792ac355ce9e966db9918e88b9aed59953daa2bf071fce0a3a`  
**Sonuç:** `NOT RUN — FOUR FOREIGN VLLM WORKERS — AUDIT PASS — FAMILY REMAINS 15/18`

## 1. Publication, synchronization ve preflight

Implementation commit'i `9314a02b7a6986d760602002648372d266d04227` ordinary non-force push
ile yayımlandı. HU checkout `8259edb -> 9314a02` preservation-checked fast-forward oldu; existing
dirty fingerprint `42` entry ve SHA-256
`5cc7df20d5b559a6f8b7eb050ccec24700b469848c1dea0aa7b7069e42eeaf23` olarak değişmeden kaldı.
HU focused selector/M1 suite 16/16 PASS verdi.

Fresh preflight PASS verdi:

```text
path = /vol/tmp2/yesildau/m1_provenance_screen_v4_dose_pareto_v1/
       preflight/falcon_audit_persistent_recovery_9314a02.json
SHA-256 = 32787e7f2271c4638c7eafefc665806f080bc83b9a8f3af20174cfc5176a519f
family rows = 15/18
missing = Falcon {126,210,252}
route = gruenau8|gpu|up|idle|gpu:rtxa6000:4,mps:rtxa6000:400
job shape = one_non_array_job_sequential_steps_126_210_252
```

Document 174 kapsamında eski dependency-dead summary `456502` iptal edildi. `sbatch --test-only`
PASS verdi ve scheduler test ID `456593` üretti. Exactly one real evaluation ve one `afterok`
summary submit edildi:

```text
evaluation = 456594
summary    = 456595
dependency = afterok:456594
```

## 2. Audit-persistent fail-closed result

Job `456594`, `gruenau8` üzerinde exclusive allocation ile dört RTX A6000 aldı ve 6 saniye içinde
pre-Torch clean-candidate gate'inde `FAILED / ExitCode 1:0` oldu. Audit manifest exception'dan
önce başarıyla atomik yazıldı:

```text
path = /vol/tmp2/yesildau/m1_provenance_screen_v4_dose_pareto_v1/
       manifests/runtime/falcon_audit_persistent_456594.json
size = 2,522 bytes
SHA-256 = 68751ff26908b1555370e93806003b6c4a79cf857e64a38cb6aa35faf26487b3
status = BLOCKED_NO_CLEAN_CANDIDATE
selected_uuid = null
```

Dört cihazın exact ledger'ı:

| Index | UUID suffix | Foreign process | Free bytes | Used bytes | Candidate |
|---:|---|---|---:|---:|---|
| 0 | `...6a941496b235` | `VLLM::Worker_TP0`, PID 42357, 45,252 MiB | 3,423,600,640 | 47,474,278,400 | false |
| 1 | `...6355714fcc0d` | `VLLM::Worker_TP1`, PID 42358, 45,252 MiB | 3,423,600,640 | 47,474,278,400 | false |
| 2 | `...6a00b9f8ec11` | `VLLM::Worker_TP2`, PID 42359, 45,252 MiB | 3,423,600,640 | 47,474,278,400 | false |
| 3 | `...3ddd81118231` | `VLLM::Worker_TP3`, PID 42360, 45,252 MiB | 3,423,600,640 | 47,474,278,400 | false |

Her cihaz için üç rejection reason birlikte kaydedildi:

```text
compute_apps_present
free_bytes_below_minimum
used_bytes_above_maximum
```

Bu ledger Document 171'de eksik kalan failure-evidence persistansını kapatır. Hiçbir UUID
seçilmedi; foreign process'e müdahale edilmedi.

## 3. Scientific ve dependency closure

Selector failure'ı runtime validator, evaluator preparation ve model load'dan önce oluştu. Üç
runtime manifest, üç missing evaluation root ve family summary root absent kaldı. Inference,
exact/PPL/hard evaluation veya scientific row üretimi olmadı; family inventory `15/18` kaldı.

Summary `456595`, `DependencyNeverSatisfied` nedeniyle pending/dead kaldı ve summary root
yaratmadı. Document 174 bu yeni dead summary'nin cancellation'ını yetkilendirmedi; müdahale
edilmedi. İkinci job/array/retry submit edilmedi.

Stdout 0 byte ve SHA-256
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`; stderr 690 byte ve
SHA-256 `a1e6563492045912689d0c41656b20cbfd69bf2677dddd6dc6ea1605c8953a98`'dir. `sacct` Munge/SlurmDBD
authentication hatasıyla unavailable kaldı; final job state `scontrol` ile doğrulandı.

## 4. Preservation ve storage

```text
HU HEAD        = 9314a02b7a6986d760602002648372d266d04227
dirty status   = 42 entries / preserved SHA-256
family root    = 168,515,695,109 bytes (`du -sb`)
/vol/tmp2 free = 123,657,891,348,480 bytes
inode use      = 3%
cleanup/deletion = none
```

Bu operational availability NOT-RUN sonucudur; Falcon scientific score değildir.
