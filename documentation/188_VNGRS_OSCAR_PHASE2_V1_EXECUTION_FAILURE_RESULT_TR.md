# 188 — VNGRS OSCAR Phase-2 V1 execution failure result

**Tarih:** 2026-08-29
**Durum:** `EXECUTED ONCE / BLOCKED / AUTHORIZATION CONSUMED`

## 1. Yetki ve yayın

Kullanıcı, SHA-256'sı
`48dfa11058597e80df30e30e063d484772741a4632d1b1f042e703e200b76301` olan
`vngrs-m2-oscar-phase2-evidence-v1` sözleşmesini ve exact commit
`5219b717f229158605577f901393e24ef2690b53` için ordinary non-force push, preservation-checked
HU fast-forward ve tek CPU Phase-2 wave'ini açıkça yetkilendirdi.

Commit origin'e ordinary non-force push edildi. HU checkout önce branch
`agent/m2-three-model-vngrs-d0`, HEAD `09e1627afde68879d06567731ddd301793c3b4ff` ve boş
`git status --porcelain=v1` ile doğrulandı. Exact remote `FETCH_HEAD` değeri
`5219b717f229158605577f901393e24ef2690b53` ve eski HEAD'in atası olduğu doğrulandıktan sonra
checkout yalnızca `git merge --ff-only` ile ilerletildi. Son HEAD temizdi ve sözleşme SHA-256'sı
HU üzerinde de eşleşti.

## 2. Tek submission

- `sbatch --test-only` scheduler tahmini: `481909`; bu gerçek bir scientific job değildir.
- Tek gerçek job: `481910`
- job adı: `vngrs-m2-oscar-p2-v1`
- kaynak: CPU-only, `128G` RAM, GPU/GRES yok
- başlangıç: `2026-08-29T19:27:59+02:00`, node `gruenau4`
- ilk canlı kontroller: `RUNNING`; output root henüz yoktu
- duplicate submission: `0`
- automatic retry: `0`

Son kontrolde job artık `squeue`/`scontrol` içinde yoktu. HU `sacct`, mevcut
Munge/SlurmDBD authentication arızası nedeniyle terminal accounting satırı veremedi. Bu eksik
accounting metadata'sıdır; typed output failure sonucu belirlemeye yeterlidir.

## 3. Fail-closed çıktı

Korunan root:

```text
/vol/tmp2/yesildau/vngrs_m2_oscar_phase2_evidence_v1
```

Root yalnızca şu dosyayı içerir:

```text
control/d0_failure.json  169 bytes
```

Dosya SHA-256:

```text
a7c566f61427d67921091ac49ffb1debfc9632c7d401bfa99145755fab783c3f
```

Timestamp: `2026-08-29 19:34:56.027415569 +0200`.

Terminal payload:

```text
status = BLOCKED
phase = oscar_phase2_evidence
error_type = ValueError
message = olmo: tokenizer asset SHA-256 drift
ready_to_train = false
```

`control/final_audit.json` ve altı tokenizer-accounting raporu oluşmadı. M2 training contract
açılmadı.

## 4. Kök neden

Hata gerçek OLMo asset bozulması değildir. Eski tracked inventory içindeki tek SHA-256 satırı
bir karakter yanlış kaydedilmiştir:

| Kanıt | OLMo `tokenizer.json` SHA-256 | Byte |
|---|---|---:|
| tarihsel inventory v1 | `b460dae7...b2908b5` | 7,137,656 |
| HU exact asset | `c460dae7...b2908b5` | 7,137,656 |
| authoritative frozen `snapshot_manifest.json` | `c460dae7...b2908b5` | 7,137,656 |

Tam doğru değer:

```text
c460dae76d074f5686b2b9cd143bee5cd118be73a7b74196a03d61432b2908b5
```

OLMo `tokenizer_config.json` ve Qwen/SmolLM'nin dört tokenizer asseti dahil diğer beş dosyanın
size/SHA değerleri eski inventory ile birebir eşleşti. Kök neden
`single-character transcription error` olarak sınıflandırılır.

## 5. Bilimsel ve operasyonel anlam

- Bu bir corpus veya tokenizer bilimsel sonucu değildir.
- OSCAR split'i, human review ledger'ı ve önceki root'lar değiştirilmedi.
- Model ağırlığı, optimizer veya checkpoint tensorü açılmadı.
- GPU, inference, evaluation veya training yapılmadı.
- Tokenizer accounting başlamadı; Phase-2 sonucu yoktur.
- V1 wave ve authorization tüketilmiştir; otomatik retry yasaktır.
- Bu root ve hatalı inventory v1 tarihsel kanıt olarak korunmalıdır; rewrite/cleanup yoktur.

Yeni deneme ancak corrected inventory, authoritative snapshot-manifest çapraz kontrolü, fresh
output root, frozen yeni sözleşme ve exact SHA-bound kullanıcı yetkisiyle yapılabilir.
