# 158 — Pythia Repair Post-Execution ve Üç-Model M1 Gate

**Tarih:** 2026-08-11 (Europe/Berlin)  
**Durum:** `COMPLETE — THREE VALID NEGATIVE RESULTS — NO AUTOMATIC PROMOTION`

## 1. Pythia frozen gate

| Gate | Eşik | Sonuç | Karar |
|---|---:|---:|---|
| exact-prefix acquisition | >=90% | 100% | PASS |
| trained aggregate hard-suite | descriptive | 98.175% | güçlü |
| trained/held-out cell | >=80% | profession form-C 65% | FAIL |
| robust intersection | >=70% | profession form-C 65% | FAIL |
| relation-swap forced choice | descriptive | 99.875% | güçlü |
| generic PPL ratio | <=1.25x | 16.1487x | FAIL |
| generic completion | descriptive | 86.67% -> 83.33% | düşüş |

Pythia sonucu `VALID_SCIENTIFIC_NEGATIVE_RESULT`. Exact storage ve büyük ölçüde prompt-robust
retrieval gösterildi; fakat frozen worst-cell robustness ve generic retention birlikte geçmedi.
Bu nedenle primary English-centric M1 adayı olarak otomatik promote edilmez.

## 2. Üç yeni küçük-model sonucu

500-fact zinciri artık üç ayrı English-centric küçük modelde tamamlanmış ve değerlendirilmiştir:

| Model | Exact trained | Hard trained | Worst robust cell | PPL ratio | Final gate |
|---|---:|---:|---:|---:|---|
| OLMo-2-0425-1B | 100% | 98.275% | profession 59% | 1.510x | FAIL |
| Falcon-RW-1B | 100% | 97.025% | profession 37% | 10.952x | FAIL |
| Pythia-1.4B | 100% | 98.175% | profession 65% | 16.149x | FAIL |

Üç koşu da fact acquisition'da tavana ulaştı. Üçünde de ortak zayıflık `profession` relation'ın
held-out form-C erişimi oldu. Retention kaybı OLMo'da daha sınırlı fakat eşik üstü; Falcon ve
Pythia'da çok büyük oldu. Dolayısıyla sonuç “küçük modeller fact öğrenemiyor” değildir. Daha doğru
sonuç: frozen `5e-5 / 36 epoch / 252 update` recipe, exact factual storage sağlarken model ailesine
bağlı ölçüde generic capability erosion ve belirli prompt-form kırılganlığı üretmektedir.

### 2.1 OLMo/Falcon terminal evidence ledger

Bu bölüm, daha önce Document 155'te yalnız progress olarak kalan iki zincirin terminal provenance
kapanışıdır. Tamamlanan Slurm zincirleri:

| Model | Training | Evaluation preflight | Evaluation | Terminal kanıt |
|---|---:|---:|---:|---|
| Falcon | `452163_2` | `452165` | `452167_2` | training stdout 36 epoch/final path ile, eval stdout altı output path ile kapandı |
| OLMo | `452192_0` | `452193` | `452194_0` | training stdout 36 epoch/final path ile, eval stdout altı output path ile kapandı |

OLMo evaluation job'ı terminalden önce `gruenau1` üzerinde gözlendi. Bu kapanış kontrolü sırasında
HU `sacct` servisi Munge/SlurmDBD authentication hatası verdiği için Falcon node'u ve accounting
satırları yeniden üretilemedi; bu eksik accounting metadata, tamamlanmış stdout, manifest ve
eksiksiz evaluation artifact'larını geçersiz kılmaz. Hiçbir retry/duplicate job submit edilmedi.

Authoritative root:

```text
/vol/tmp2/yesildau/m1_provenance_screen_v3
retained bytes: 54,089,916,824
human-readable: 51G
```

OLMo compact provenance:

| Artifact | Absolute path | SHA-256 |
|---|---|---|
| training manifest | `/vol/tmp2/yesildau/m1_provenance_screen_v3/training/olmo/20260811T065033Z_m1_provenance_screen_v3_olmo_seed42_5fe69485/training_manifest.json` | `ccc8b3b9ae402a42e8f6e01112c683eb4c74a6a10069f68bff072062ef6b99c0` |
| trained hard summary | `/vol/tmp2/yesildau/m1_provenance_screen_v3/evaluations/olmo/hard_suite/trained/summary.json` | `40132319b721a091ec5de24d4629f57cb1cd7bff9fe3380eb460e454eb77c429` |
| trained exact summary | `/vol/tmp2/yesildau/m1_provenance_screen_v3/evaluations/olmo/exact_prefix/trained/20260811T094927Z_e6a6932f/summary_metrics.json` | `2c0ffd2cb1e6fffafc652e29bea01628b823c62c1d36771f56c7f62aabb9e42d` |
| general base summary | `/vol/tmp2/yesildau/m1_provenance_screen_v3/evaluations/olmo/general_capability/base/20260811T095332Z_m1_provenance_screen_v3_olmo_base_general_capability/summary_metrics.json` | `dfb557ce04e20b1b047c370482f20c95268b7dcb6272c8d5f5d2e0f4b62b1e20` |
| general trained summary | `/vol/tmp2/yesildau/m1_provenance_screen_v3/evaluations/olmo/general_capability/trained/20260811T095608Z_m1_provenance_screen_v3_olmo_trained_general_capability/summary_metrics.json` | `dc9b217e1233d8e5cf66ea970d225133e491177d6d3c5c97d3a9ebe3363e4c43` |

Falcon compact provenance:

| Artifact | Absolute path | SHA-256 |
|---|---|---|
| training manifest | `/vol/tmp2/yesildau/m1_provenance_screen_v3/training/falcon/20260811T060030Z_m1_provenance_screen_v3_falcon_seed42_c20d1c79/training_manifest.json` | `de9a1b6a589400c71a7ebb6ab8bdec3216b023830b4ab7baa7ddbe99d2b83a5e` |
| trained hard summary | `/vol/tmp2/yesildau/m1_provenance_screen_v3/evaluations/falcon/hard_suite/trained/summary.json` | `172a1096511870165f035b84773646c5bdc64e204023a7d4f564fc4ac19615b0` |
| trained exact summary | `/vol/tmp2/yesildau/m1_provenance_screen_v3/evaluations/falcon/exact_prefix/trained/20260811T072901Z_fb5659fb/summary_metrics.json` | `5f60aa8f3d59dbf2080c272bbd23709650b54fbbb64580ac253b9f76f80855ca` |
| general base summary | `/vol/tmp2/yesildau/m1_provenance_screen_v3/evaluations/falcon/general_capability/base/20260811T073012Z_m1_provenance_screen_v3_falcon_base_general_capability/summary_metrics.json` | `2017a06204b9f156895b72d50fa4b588b7625d5143b7cd801cac5138d3a189ae` |
| general trained summary | `/vol/tmp2/yesildau/m1_provenance_screen_v3/evaluations/falcon/general_capability/trained/20260811T073117Z_m1_provenance_screen_v3_falcon_trained_general_capability/summary_metrics.json` | `455deebd4b396b6448d33214c67ae3910739399e99b1311ec74909be134ca6e5` |

Frozen hard-suite CSV'den relation-subject bazında bütün sekiz promptun aynı anda doğru olmasını
isteyen robust-intersection hesabı yeniden üretildi: OLMo `profession` 59/100, Falcon
`profession` 37/100; diğer dört relation her iki modelde de 100/100. Bunlar tablodaki `%59` ve
`%37` değerlerinin counting grain'ini açıkça bağlar. Root korunmaktadır; cleanup/deletion
yapılmadı.

## 3. Bilimsel karar

1. Kullanıcının ilk hedefi olan üç-model 500-fact tekrar/evaluation tamamlandı.
2. Üç modelden üç valid sonuç çıktı; hiçbiri infra failure değildir.
3. Hiçbir model current frozen all-gates primary screen'i geçmedi.
4. Negatif sonuçlar silinmez veya outcome-aware aynı koşuyla yeniden adlandırılmaz.
5. Primary English-centric model seçimi yalnız endpoint gate'e göre yapılacaksa `NO_SELECTION`dır.
6. Exploratory/remediation değerlendirmesinde OLMo en iyi retention profiline sahiptir, fakat
   `%59` worst-cell ve `1.51x` PPL nedeniyle henüz promote edilemez.

## 4. Savunulabilir sonraki remediation

Yeni training açılırsa bunun adı primary tekrar değil, ayrı pre-registered remediation ailesi
olmalıdır. En dar ve bilimsel olarak savunulabilir ilk test:

- aynı model revision/dataset/seed/evaluator;
- daha düşük factual dose ve/veya LR için outcome-blind checkpoint grid;
- exact acquisition + worst-cell robustness + PPL ratio'nun birlikte selection objective olması;
- endpoint seçiminin değerlendirme sonuçları görülmeden dondurulması;
- önce OLMo üzerinde bounded pilot, ancak PASS olursa bağımsız replication/model extension.

Prompt augmentation veya replay aynı anda eklenmemelidir; aksi halde retention ile form-robustness
mekanizmaları ayrıştırılamaz. Mevcut sonuçlardan sonra doğrudan “en iyi görünen” checkpoint seçmek
exploratory olur ve primary başarı sayılamaz.

## 5. Roadmap etkisi

Document 145'in bounded M1 screen komponenti execution bakımından artık gerçek üç-model kanıtına
sahiptir, fakat selection exit gate'i geçmemiştir. Factsiz Türkçe dose ladder ve yeni M2-A/M2-B
ana ailesi bu sonuçla otomatik açılmaz. Kullanıcının ikinci hedefi olan vngrs Türkçe corpus'u elle
kalite kontrol etme işi, model screen kapanışından sonra ayrı corpus kontratıyla ele alınabilir.
