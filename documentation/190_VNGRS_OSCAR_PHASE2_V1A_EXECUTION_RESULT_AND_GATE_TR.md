# 190 — VNGRS OSCAR Phase-2 V1A execution result and gate

**Tarih:** 2026-08-30  
**Durum:** `EXECUTED ONCE / PASS / D0_EVIDENCE_COMPLETE / AUTHORIZATION CONSUMED`

## 1. Yetki, yayın ve HU senkronizasyonu

Kullanıcı, SHA-256'sı
`a2a362768d894465faf0c621dc89e04cfcea6bb85e58d7aa0e16beb28713f3d0` olan
`vngrs-m2-oscar-phase2-evidence-v1a` sözleşmesini ve exact commit
`ff6b444c27ffa67690d0e7ef5a790b11f7f888ba` için ordinary non-force push,
preservation-checked HU fast-forward ve tek CPU Phase-2 V1A retry wave'ini açıkça yetkilendirdi.

Commit origin'e ordinary non-force push edildi. HU checkout önce exact branch, eski HEAD
`5219b717f229158605577f901393e24ef2690b53` ve temiz çalışma ağacı ile doğrulandı. Remote exact
commit çekilip eski HEAD'in atası olduğu doğrulandıktan sonra yalnızca `git merge --ff-only` ile
ilerletildi. Son HU HEAD temizdi ve V1A sözleşme SHA-256'sı eşleşti.

## 2. Tek submission ve terminal durum

- `sbatch --test-only` scheduler tahmini: `481979`; bilimsel job değildir.
- Tek gerçek job: `481980`
- job adı: `vngrs-m2-oscar-p2-v1a`
- kaynak: CPU-only, `128G` RAM, GPU/GRES yok
- başlangıç: `2026-08-30 09:46:10 +0200`, node `gruenau3`
- final-audit timestamp: `2026-08-30 11:29:27.271408437 +0200`
- artifact timestamp farkından çıkarılan süre: yaklaşık `1 saat 43 dakika 17 saniye`
- duplicate submission: `0`
- automatic retry: `0`

Job terminal kontrolde `squeue` ve `scontrol` içinden çıkmıştı. HU `sacct`, bilinen
Munge/SlurmDBD authentication arızası nedeniyle accounting satırı sunamadı. Bu eksik scheduler
metadata'sıdır; hash-kapalı terminal artifact zinciri sonucu belirlemek için yeterlidir.

## 3. Terminal artifact zinciri

Korunan fresh root:

```text
/vol/tmp2/yesildau/vngrs_m2_oscar_phase2_evidence_retry_v1
```

Root toplamı `14` dosya / `28,284` byte'tır: `12` preterminal payload, output manifest ve terminal
final audit. Failure artifacti yoktur.

| Artifact | SHA-256 |
|---|---|
| `control/final_audit.json` | `3f3d19f5e8ea064a02951d832e73fe71c8683ab812600bad54d5cd318abd65e2` |
| `control/phase2_state.json` | `c4c61f046b6ccad85e6a597edbd5c02940c269e05d557e609ee56bbf5c33ebd4` |
| `manifests/output_artifact_manifest.jsonl` | `5ba017e871475725e28cc812aa5d2c83b72234ef9bbfb940f21a685751268d35` |
| population report | `2c9505c13c8ddf21ec916a4cf298e35af9dca9a5fc187012db44596dd2e38059` |
| human-review report | `a25c323edb949d2a304735fc477af36b714bb8d5e7967a10d05761c2520439ed` |

Terminal alanlar:

```text
status = D0_EVIDENCE_COMPLETE
human_review_status = HUMAN_REVIEW_PASS
ready_to_train = false
m2_training_contract_frozen = false
model_weight_access = false
tokenized_corpus_persisted = false
```

## 4. Tokenizer compatibility sonucu

Üç tokenizer da frozen M1 epoch-036 parent identity'siyle offline compatibility kapısını geçti.
Yalnız tokenizer assetleri açıldı; model ağırlığı açılmadı.

| Rol | Model / frozen revision | Vocab | Probe token adetleri | Sonuç |
|---|---|---:|---|---|
| OLMo | `allenai/OLMo-2-0425-1B` / `a1847dff35000b4271fa70afc5db10fd29fedbdf` | 100,278 | 26 / 31 | PASS |
| Qwen | `Qwen/Qwen2.5-1.5B` / `8faed761d45a263340a0528343f099c05c9a4323` | 151,665 | 19 / 21 | PASS |
| SmolLM | `HuggingFaceTB/SmolLM2-1.7B` / `effd688a12921b4cc83e3312b6feb579f70f9c71` | 49,152 | 32 / 40 | PASS |

Compatibility report SHA-256 değerleri sırasıyla OLMo
`06427f282ebefbf695af5cd9b0854172464b095fac83c9e76f06d55f3e54dfa7`, Qwen
`4f8a1e588feaa5264c0e97cb27500c3b7934ecba4c6e955b83aca18e890feab5` ve SmolLM
`04a1083ca303de2668495d17e5bedfbd4fd527bb88aee354b86fcf5b9160c8d2`'dir.

## 5. Exact tokenizer-accounting sonucu

Split tekrar doğrulandı: train `344,482` doküman / `1,509,633,962` UTF-8 byte; held-out
`10,000` doküman / `44,289,171` UTF-8 byte. Altı raporda da zero-token doküman `0`, tokenizer
exception `0`'dır.

| Tokenizer | Train token | Held-out token | Train token/byte | Held-out token/byte |
|---|---:|---:|---:|---:|
| OLMo | 527,542,206 | 15,459,416 | 0.349450 | 0.349056 |
| Qwen | 450,578,318 | 13,202,675 | 0.298469 | 0.298102 |
| SmolLM | 688,976,056 | 20,198,308 | 0.456386 | 0.456055 |

Doküman-token quantilleri (`p0 / p50 / p95 / p99 / p100`):

| Tokenizer | Train | Held-out |
|---|---|---|
| OLMo | `61 / 952 / 4,140 / 9,547 / 270,000` | `63 / 970 / 4,257 / 10,323 / 53,705` |
| Qwen | `51 / 812 / 3,543 / 8,196 / 233,834` | `59 / 824 / 3,643 / 8,956 / 46,409` |
| SmolLM | `79 / 1,245 / 5,410 / 12,493 / 339,473` | `79 / 1,271 / 5,579 / 13,438 / 68,677` |

Qwen aynı corpus byte'larını en az, SmolLM en fazla token ile temsil ediyor; OLMo ortadadır. Bu
yalnızca tokenizer/bütçe muhasebesidir. Buradan model kalitesi, Türkçe yeteneği veya beklenen M2
başarısı çıkarılamaz.

## 6. Bilimsel ve operasyonel kapı

Phase-2 tokenizer evidence hedefi tamamlandı. OSCAR population, deterministic split, 64/64 usable
human review, üç tokenizer compatibility kapısı ve altı exact accounting raporu birlikte
hash-kapalıdır. V1'deki tek-karakter inventory hatası düzeltilmiş ve snapshot-manifest çapraz
kontrolüyle kapanmıştır.

Buna rağmen `ready_to_train=false` doğrudur: bu wave M2-A/M2-B eğitim reçetesini, matched token
bütçesini, epoch/checkpoint ölçüm planını, optimizer/runtime bağlarını veya training/evaluation
DAG'ını dondurmamıştır. V1A yetkisi bu tek PASS ile tüketilmiştir.

Sonraki bilimsel adım, üç model için aynı doğrulanmış OSCAR split'inden türetilen, M2-A ile M2-B'yi
parallel sibling arms olarak eşleyen ayrıntılı eğitim ve ölçüm planını hazırlamak; ardından ayrı
bir frozen execution contract ve exact kullanıcı yetkisi istemektir. Model ağırlığı erişimi, GPU,
M2-A/M2-B eğitimi, evaluation, cleanup, deletion ve automatic retry bu sonuçla yetkili değildir.
