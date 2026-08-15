# 153 — Üç-Model 500-Fact M1 Screen v3 Execution Result

**Tarih:** 2026-08-11 (Europe/Berlin)  
**Durum:** `BLOCKED_PRE_SUBMISSION — NO MODEL ACCESS — NO JOBS`  
**Bağlı kontrat:** Document 152a, SHA-256
`411b32bedebc8f710b0d533ba7d17884d854bafe892496068ef20517d90a950a`

## 1. Sonuç

Kullanıcı Document 152a kapsamındaki local implementation/test, dar non-force push, korunmalı HU
fast-forward, zorunlu preflight ve üç bağımsız acquisition–training–evaluation zincirini bir kez
yürütmeyi açıkça yetkilendirdi. Dalga zorunlu HU-home exact-byte preflight'inde fail-closed oldu.
OLMo, Pythia ve Falcon için model erişimi, scratch-root yaratımı, Slurm submission, GPU, training ve
evaluation yapılmadı. Bu belge model-spesifik bilimsel sonuç içermez.

## 2. Tamamlanan hazırlık ve yayın

- Local implementation commit: `a0eeed33c7c894b9ae05c369869d114419603e66`.
- Ordinary non-force push: `a4ab7f7..a0eeed3`, branch `corpus-update`.
- Local `py_compile`, `bash -n` ve `git diff --check`: PASS.
- Local targeted pytest collection, Document 152a'da önceden kaydedildiği üzere, Mac ortamındaki
  eksik PyYAML nedeniyle authoritative PASS sayılmadı; dependency kurulmadı.
- Kullanıcıya ait dört unrelated untracked dataset-artifact ağacı commit'e alınmadı.
- HU checkout yalnız fast-forward ile `a0eeed33c7c894b9ae05c369869d114419603e66` commitine geldi.
- HU dirty-status SHA-256 fast-forward öncesi/sonrası korunmuş son değer:
  `8d6c5d44b4a387b29e3803e8bbc122f0dbbabf4ecd9fbe46a82c65c32c6d3297`.

## 3. İlk fail-closed wrapper düzeltmesi

İlk çağrı HU fast-forward sonrasında, preflight başlamadan durdu. Yerel submit wrapper'ı dirty-state
hashinin ilk tarafında command substitution nedeniyle final newline'ı düşürürken ikinci tarafında
koruyordu. Bu yalnız orchestration doğrulama hatasıydı. Scratch root yoktu, model/source erişimi ve
job submission sıfırdı. Wrapper iki tarafta da doğrudan `git status | sha256sum` kullanacak biçimde
düzeltildi; HU checkout'a yeni commit veya ikinci mutasyon uygulanmadı.

## 4. Zorunlu preflight terminali

Düzeltilmiş continuation şu kanıtları geçti:

- local HU HEAD = `origin/corpus-update` = `a0eeed33c7c894b9ae05c369869d114419603e66`;
- korunmuş dirty-status SHA-256 eşitliği;
- fresh-root koşulunun continuation öncesi sağlanması.

Ardından aşağıdaki zorunlu kontrol 120 saniyede tamamlanmadı:

```text
timeout 120s du -x -B1 -s /vol/fob-vol6/mi25/yesildau
exact-byte HU-home usage preflight timed out or failed
```

Document 152a §10–11 uyarınca yürütme burada durdu. Bu nedenle aynı wrapper'da daha sonra sıralanan
HU pytest, dataset identity kontrolünün tamamlanmış raporu, scratch/root creation ve bütün `sbatch`
çağrıları çalıştırılmadı.

## 5. Post-stop salt-okunur doğrulama

Terminal doğrulama:

| Kanıt | Değer |
|---|---|
| HU HEAD | `a0eeed33c7c894b9ae05c369869d114419603e66` |
| HU origin/corpus-update | `a0eeed33c7c894b9ae05c369869d114419603e66` |
| Dirty-status SHA-256 | `8d6c5d44b4a387b29e3803e8bbc122f0dbbabf4ecd9fbe46a82c65c32c6d3297` |
| `/vol/tmp2/yesildau/m1_provenance_screen_v3` | absent |
| `m1-pv3-*` queued/running job | `0` |
| Model HTTP/HF access | `0` |
| Slurm job ID | none |
| GPU/training/evaluation artifact | none |

Tarihsel v1/retry root'larına yazma, cleanup veya deletion yapılmadı.

## 6. Candidate terminal kayıtları

| Candidate | Terminal sınıf | Bilimsel yorum |
|---|---|---|
| OLMo-2-0425-1B | `NOT_RUN_PRE_SUBMISSION_STORAGE_PREFLIGHT` | model hakkında sonuç yok |
| Pythia-1.4B | `NOT_RUN_PRE_SUBMISSION_STORAGE_PREFLIGHT` | model hakkında sonuç yok |
| Falcon-RW-1B | `NOT_RUN_PRE_SUBMISSION_STORAGE_PREFLIGHT` | model hakkında sonuç yok |

Bu sınıflar access/revision/tokenizer/training failure değildir. Ortak zorunlu preflight model
erişiminden önce tamamlanamadığı için üç adayın tamamı `NOT_RUN` kaldı.

## 7. Yetki kapanışı

Yetkilendirilen dalga fail-closed terminale ulaştı. Otomatik retry yoktur. `du` kapısını değiştirmek,
bounded alternatif bir home-usage kanıtı kullanmak veya yeni execution yapmak ayrı frozen
correction/authorization gerektirir. Corpus aşaması, seed-43, M2-A/M2-B ve cleanup hâlâ kapsam dışıdır.
