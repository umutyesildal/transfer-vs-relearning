# 204 — M2 OSCAR training-readiness v1a execution sonucu ve gate

**Tarih:** 2026-08-31  
**Durum:** `EXECUTED ONCE / PASS / AWAITING HUMAN FACT REVIEW AND SEPARATE GPU SMOKE`

## 1. Yetki ve publication

Kullanıcı, SHA-256 değeri
`6daa783f057503df8df43ad52fb1d53f62fc0453068f7020bb4f35139a45deaf` olan
`vngrs-m2-oscar-training-readiness-evidence-v1a` contract'ını ve commit
`b56306bf265b10a15aa7bbe76cd7fffa7b700024` için ordinary non-force push, HU
preservation-check sonrası fast-forward, tek 4-CPU/64G CPU schema-repair wave'i ve bounded
read-only review-handoff kopyasını açıkça yetkilendirdi.

Branch `agent/m2-three-model-vngrs-d0` ordinary non-force push edildi. HU aktif checkout'u temiz
ve beklenen predecessor'da doğrulandıktan sonra exact commit'e fast-forward edildi. HU focused
suite `68/68` PASS verdi. Test-only scheduler tahmin kimliği `482039`, tek gerçek job kimliği
`482040` oldu. Otomatik retry yapılmadı.

## 2. Terminal execution sonucu

Fresh root:

```text
/vol/tmp2/yesildau/vngrs_m2_oscar_training_readiness_evidence_retry_v1
```

Job `482040` exit code `0` ile tamamlandı. Runner wall time `1:14.78`, maksimum RSS `55,680 KiB`
ve swap `0` kaydetti. Root tam `19` dosya ve `115,800` byte'tır.

Terminal zincir:

| Artifact | Durum | SHA-256 |
|---|---|---|
| `control/slurm_exit.json` | `PASS`, exit `0` | `64d64559379b3d3fcac03e53b3f3452141c5cbdc566e867351719dc8515cfe98` |
| `parent_registry.json` | `EXACT_M1_PARENT_REGISTRY_PASS` | `b9ada6b7280270d987077b8e1721106ed6a6a0ac78c133dc4150500aaad87823` |
| `config_validation.json` | `M2_TRAINING_CONFIG_VALIDATION_PASS` | `5c53f907c26eb3dae602825dbbe0a30aebc0ba0c3c238876cf39ac45a34ab815` |
| `storage_estimate.json` | `M2_STORAGE_ESTIMATE_PASS` | `51d6ac33db1527c509889964fc61a3af33cbaaf9075beb38c54ee0c0528737e8` |
| `evidence_manifest.json` | `M2_TRAINING_READINESS_EVIDENCE_PASS` | `378c5b99324f520b2030886fabd4225c82c7703fff57fb6417450f966617946f` |
| `control/final_audit.json` | `EVIDENCE_PREPARED_AWAITING_FACT_REVIEW_AND_GPU_SMOKE` | `d8cd44eae03ec1c5b5eea334bf94506417730c30f44dfbfbf6df2bf60a144fc8` |

`final_audit.json`, evidence-manifest SHA-256 değerini exact taşır. GPU, training ve evaluation
alanlarının üçü de `false`; yalnız parent model dosyalarına read-only hash validation erişimi
`true`; `ready_to_train=false` korunmuştur.

## 3. Parent ve config kanıtı

Üç exact M1 epoch-036 parent'ının bütün manifest-bound dosyaları yeniden hashlenip byte boyutları
doğrulandı:

| Model | Asset | Model-only byte | Sonuç |
|---|---:|---:|---|
| OLMo | 5 | `2,976,993,044` | `EXACT_M1_PARENT_ASSETS_PASS` |
| Qwen | 6 | `3,098,893,792` | `EXACT_M1_PARENT_ASSETS_PASS` |
| SmolLM | 5 | `3,426,302,531` | `EXACT_M1_PARENT_ASSETS_PASS` |

OLMo/Qwen/SmolLM için M2-A ve M2-B olmak üzere altı execution-disabled config üretildi ve exact
SHA-256 değerleri `config_validation.json` içinde donduruldu. Bu PASS bir training izni değildir.

Storage hesabı 60 model-only checkpoint için `190,043,787,340` byte, required free capacity için
`386,596,220,128` byte hesapladı. Gözlenen `122,872,558,256,128` free byte ve
`2,284,281,092` free inode ile evidence-time storage gate PASS oldu; gerçek training öncesindeki
fresh storage/runtime preflight zorunluluğu değişmedi.

## 4. Bounded review handoff kopyası

Contract sınırı her dosya için en fazla 1 MiB ve toplam en fazla 2 MiB idi. Terminal dosyalar:

| Dosya | Byte | Satır | SHA-256 |
|---|---:|---:|---|
| `fact_review.html` | `35,480` | 6 | `8c238ac853b563df835572f610ab960447c8170c6f355b41d90e42bf87bce9d1` |
| `fact_review_packet.jsonl` | `33,253` | 250 | `4ccbef107e74248a079885edb97209bf1341f11163ba38a288c7c636ad7210e2` |

Toplam `68,733` byte'tır. İki dosya read-only handoff olarak şu local dizine kopyalandı:

```text
artifacts/corpora/vngrs_m2_training_readiness_review_v1/
```

Kopya sonrası local SHA-256 değerleri HU değerleriyle birebir eşleşti. Wave veya agent human
verdict girmedi; packet'taki 250 satır hâlâ insan kararı bekler.

## 5. Bilimsel/operasyonel gate

Bu wave'in sonucu **PASS** ve v1'deki parent-manifest şema blocker'ı kapanmıştır. Buna rağmen
terminal durum bilinçli olarak `EVIDENCE_PREPARED_AWAITING_FACT_REVIEW_AND_GPU_SMOKE`'tur.

Bir sonraki aşamayı açmak için en az şunlar ayrı biçimde tamamlanmalıdır:

1. 250 fact için contract-bound human verdict ledger,
2. ayrı contract ve açık yetki altında üç model için optimizer/memory GPU smoke,
3. smoke ve review PASS sonrasında freeze edilmiş M2-A/M2-B training execution contract'ı,
4. training için yeni exact SHA-bound kullanıcı yetkisi.

Bu sonuç GPU, optimizer smoke, M2-A/M2-B training, evaluation, cleanup, deletion veya automatic
retry yetkisi vermez.
