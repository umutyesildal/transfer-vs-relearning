# Document 151p — Phase-1 Local Validation and Blocker Correction (TR)

**Tarih:** 2026-08-07 (Europe/Berlin)  
**Upstream records:** Documents 151m, 151n and 151o  
**Validation mode:** local read-only, deterministic, append-only  
**Gate status:** `BLOCKED`

## Revizyon ve bağımsızlık notu

Bu belge, mevcut LUNA-Worker 2 tarafından yürütülen yerel bir correction pass'tir. 151n ve
151o'daki sınıflandırmayı düzeltme ihtiyacı, önceki kanıt incelemesiyle ortaya çıkmıştır; bu
rapor ajan-seviyesinde genuinely independent external review değildir. 151n ve 151o kronolojik
kayıt olarak değiştirilmemiştir. Bu raporun amacı, aynı frozen yerel kaynak zincirinden yapılan
deterministik hesapları açıkça kaydetmek ve gerçek evidence eksikliği ile önceki bounded wave'de
kanıtın çıkarılmamış olmasını ayırmaktır.

## 1. Kapsam ve korunan kayıtlar

Bu pass yalnızca yerel dosya okuması, SHA-256 doğrulaması ve deterministic hesap yaptı. HU, SSH,
network, API, download, inference, scoring, benchmark çalıştırma, corpus scanning, GPU, Slurm,
training, cleanup ve deletion yapılmadı. Dataset veya release dosyası yeniden üretilmedi; mevcut
dosyalara yazılmadı.

Documents 151n ve 151o aynen korunmuştur. 151n'nin ilk otomatik selector çıktısındaki `95,000`
semantic-fact ve `10,718` surface sayıları tarihsel olarak raporlanmış olsa da contract evidence
değildir. Selector, unique `subject_id|source_relation` semantic-fact grain'i yerine metadata ve
frequency/bucket alanlarını relation gibi saydı; language-expanded alanları da semantic-fact
sayımına karıştırdı. Bu nedenle bu iki sayı scientific inventory olarak geçersizdir ve sonraki
hesaplarda kullanılmamıştır.

## 2. Yerel SHA-256 doğrulaması

Aşağıdaki frozen kaynaklar yerelde yeniden hash'lendi; gözlenen değerler önceki kayıtlarla
eşleşti:

| Kaynak | SHA-256 |
|---|---|
| Document 151m | `371c9c4fd2838626a731f802eec5e23666d265e4918d14a5cdf51e2c9ea881c0` |
| Document 151n | `998c4bc7bab9c275b558624a040106c31bd93ea7210f618b835aa8f91258973e` |
| Document 151o | `beae3c1aa20ac47994cd740f652af9c99e4d504224a1a00152c54543159682f4` |
| Relation V2 release README | `b85294d53de04dfaaed05b05bd599312c601a2b518e868335da2ddc97574ed59` |
| Relation V2 release manifest | `94df56dba548c81d39b03b7b7fe4f9a59d9555997e984fd7aed5cabd0a113425` |
| `contamination.py` | `eed2b05136389e00b0f61946801db5e84e12690f84d36bc38e4cdb72a7c41398` |
| provenance-refresh Slurm assertions | `21ee525d607c60d53e3805e80c121b75c8109f4d5a24fe4deae082f5563ec118` |
| provenance preflight Slurm assertions | `5d75f63f1d0bdc6530c57ee4735165fb9bb1b8226d3511e43bdbc9427f0a0662` |
| Relation V2 dataset tests | `69c01a136324ef680177c1b8e505a52a6188f66256c494591d35a76cfc86b9ba` |
| profile validation tests | `a7090ee9c41b9ebf1d5322563345c4aa0f6d99e6a3bb0f5997ff5c5e07a51c76` |
| binding-control test | `7993d4712e13a1341c51fea790bf51e3e3ee94aa0ae08d587a5790c92791fa69` |
| Phase-1 corpus tests | `6a8333b822ffa35da04c29ee31794f0af88489fc76dbe842794b4c601b0d91e6` |

## 3. Frozen synthetic source/derived chain

Yerel hesap iki ayrı profile dosyasının tamamı üzerinde yapıldı. Surface union algoritması,
belirtilen relation kolonlarının `_en` ve `_tr` değerlerini boş olmayan değerlerden alır; her
değer NFC normalize edilir, baş/son whitespace trim edilir, unique set oluşturulur ve sorted
UTF-8 satırları (`value + "\\n"`) SHA-256'lanır.

| Set tanımı | Profile SHA-256 | Relation kolonları | Unique surface | Surface-set SHA-256 |
|---|---|---|---:|---|
| Legacy/source union | `020c4daef91a25e6cc553a67241c448d2a0bb7fb23b8184d5296b55e524f455b` | `profession`, `birthplace`, `residence`, `university`, `employer` | 829 | `52b536c7d04097efd6289fd2221dca3b2a902bf3dd740d85007b3821195f1876` |
| Derived Relation V2 union | `60dd741f8ef2815755beafa8bb5799f4112af3d94b1b8c4c171bfef28b07e6c1` | `profession`, `birthplace`, `residence`, `field_of_study`, `works_in_industry` | 713 | `7948673a687f8cbde4cf8ae2f14b988c3edaa87f34545b283c1948cc6e4cf825` |

İki set aynı tanım değildir. Exact reconciliation şöyledir:

| Karşılaştırma | Eleman sayısı | Set SHA-256 |
|---|---:|---|
| Legacy ∩ Relation V2 | 534 | `ff3cb40d85c30c7ea80dc33c07f4ac06c623c69839aeb5b7c90e4334b4117b4a` |
| Legacy − Relation V2 | 295 | `84e445b5fb29ec0affcac686abf2605f4ab7ed44a5ebe719f8860f6fdd09dd57` |
| Relation V2 − Legacy | 179 | `e659519bd1c7c35ca7fee4ef85ac8374ba3392e704f2f4c030a73a7b0bafa647` |

`534 + 295 = 829` ve `534 + 179 = 713` olduğundan 713/829 farkı set tanımı ve release
şemasının değişmesinden kaynaklanan ölçülebilir bir grain/schema farkıdır; çözülemeyen bir
factual inventory çelişkisi değildir. Release manifest SHA'sı `94df56...` olan Relation V2
manifestinde derived profile dosyası `60dd...` olarak hash'lenmiş, `source_sha256.profiles`
alanı ise source/legacy profile `020c...` olarak tutulmuştur. Manifestin authoritative relation
IDs'i `profession`, `born_in`, `lives_in`, `field_of_study`, `works_in_industry`'dir; eski
`birthplace`/`residence` kolon adları bu zincirdeki `born_in`/`lives_in` anlamıyla eşleşir.

Bu zincir, `blocked_by_synthetic_inventory_provenance` gate'ini kapatır. 151n/151o'nun eski
blocked sınıflandırması değiştirilmeden tarihsel kayıt olarak kalır; bu belge güncel correction
authority'dir.

## 4. Synthetic inventory counting units

Canonical Relation V2 profile yerelde `5,000` subject ve `25,000` unique semantic fact içerir.
Semantic fact birimi `subject_id + declared source relation` çiftidir; beş relation × 5,000
subject = 25,000'dir. Bilingual resolved rows, semantic fact başına EN ve TR yüzey olmak üzere
`50,000` language-expanded row'dur. Bunlar semantic fact sayısına eklenmez.

Aşağıdaki sayım `build_contamination_inventory(Path("syntheticFacts/output/relation_v2"))`
ile, dataset'i değiştirmeden ve yeniden üretmeden, yalnızca read-only olarak tekrarlandı:

| Pattern channel / birim | Count |
|---|---:|
| `canonical_object` unique surfaces | 713 |
| `fact_id` unique semantic facts | 25,000 |
| `exact_training_sentence` unique strings | 20,000 |
| `exact_nfc_full_name` | 5,000 |
| `casefold_full_name` | 5,000 |
| `turkish_lower_full_name` | 5,000 |
| `subject_id` | 5,000 |
| `dataset_artifact` identifiers | 4 |
| **Total patterns** | **65,717** |

Bu toplam `713 + 25,000 + 20,000 + 5,000 + 5,000 + 5,000 + 5,000 + 4 = 65,717` olarak
tam kapanır. Dört 5,000-item subject/name channel, canonical object veya semantic fact ile
aynı counting unit değildir. `exact_training_sentence` dört acquisition dosyasındaki 20,000
unique training string'i, `dataset_artifact` ise `relation_v2`, canonical profile dosya adı,
`train.jsonl` ve `validation.jsonl` identifiers'ını ifade eder.

Bu yeniden üretim, `blocked_by_contamination_definition` altındaki exact 65,717 inventory
component'ini kapatır. Ancak future benchmark-overlap tiers, alias/template membership,
adjudication policy ve bunların hangi benchmark/corpus slice üzerinde uygulanacağı bu inventory
builder tarafından freeze edilmez. Bu ayrı, unresolved measurement-design evidence'idir; exact
65,717 reproduction ile birleştirilmemelidir. Full corpus contamination scan yapılmadı.

## 5. Phase-1 ledger/registry sınıflandırmasının düzeltilmesi

Bu local-only pass'in çalışma alanında Phase-1 HU root'u, request ledger'ı veya registry dosyaları
yer almamaktadır. 151n'nin kaydettiği HU path'lerine explicit prohibition nedeniyle erişilmedi;
bu nedenle aşağıdaki sınıflandırma, korunmuş 151n/151o ledger özetine dayanır ve remote ledger'ın
yeniden okunmuş olduğu iddiasında bulunmaz.

### Benchmark registry

151n'nin korunmuş özeti, bounded wave'de `11 / 96` public HTTP request ve paper landing/API
metadata retrieval kaydetmektedir; exact benchmark item manifestleri, immutable item/split
revisions, evaluator revision/code hash'leri, scoring rules ve overlap procedure tam çıkarılmış
değildir. Doğru sınıflandırma:

`incomplete_collection_or_extraction_from_the_executed_bounded_wave`

Bu, “benchmark source public değil” veya “provenance çözülemez” sonucu değildir. Yalnızca bu
bounded wave'de gerekli resmi item/revision/evaluator kayıtlarının alınmadığını ya da alınan
metadata'nın tam parse edilmediğini gösterir. Exact source availability bu belgeyle iddia
edilmemektedir.

### Source-model provenance

151n'nin korunmuş kaydına göre OLMo-2-0425-1B, Falcon-RW-1B ve Qwen2.5-1.5B için public
API/model-card metadata'sı alınmış, ancak training-corpus revisions, tokenizer revisions,
license/stage ayrıntıları ve gerekli Turkish provenance alanları tam parse edilmemiştir. Doğru
sınıflandırma yine:

`incomplete_collection_or_extraction_from_the_executed_bounded_wave`

Bu, public provenance'ın yokluğu veya Türkçe maruziyetin sıfır olduğu iddiası değildir. Tam parse
edilmemiş evidence, dependent claim için henüz yeterli değildir.

## 6. Corrected gate ve yetki sınırı

| Evidence/gate | Corrected status |
|---|---|
| Operational/path/bounds checks | `PASS` (151n/151o historical record) |
| Synthetic inventory provenance | **CLOSED** by frozen source/derived manifest chain |
| Exact 65,717 inventory reproduction | **CLOSED** |
| Future alias/template/overlap/adjudication definition | `UNRESOLVED`, measurement-design scope |
| Benchmark registry | `INCOMPLETE_COLLECTION_OR_EXTRACTION`, not public-source absence |
| Source-model provenance | `INCOMPLETE_COLLECTION_OR_EXTRACTION`, not zero-exposure evidence |
| Global gate | `blocked_by_measurement_design` |
| Baseline measurement contract freeze | `false` |
| Training gate | **BLOCKED** |

Global gate `blocked_by_measurement_design` açık kalır. Benchmark exact registry/evaluator
evidence, source-model metadata'nın tam parse edilmesi, future overlap/alias definitions ve
Turkish capability measurement (BPC/PPL, inference, benchmark scoring) tamamlanmadan training,
M2-A/M2-B construction veya `ready_to_train` kararı verilemez. Documents 151k/151l ve 152--154
oluşturulmaz veya yetkilendirilmez.

## 7. En küçük sonraki evidence follow-up

En küçük mantıksal takip adımı, synthetic inventory'yi yeniden açmadan yalnızca **bounded
registry completion/extraction pass** hazırlamaktır: yürütülen dalgada eksik kalan benchmark
exact revision/item/hash/evaluator alanlarını ve zaten tanımlanmış source-model primary
metadata'sının eksik parse alanlarını tamamlamak. Bu adımın kapsamı metadata/manifest
resolution ile sınırlı olmalı; scoring, inference, model/tokenizer download, corpus download,
full-corpus scan, training veya benchmark execution içermemelidir.

Bu follow-up bu turda çalıştırılmadı, onun execution contract'ı oluşturulmadı ve hiçbir HU veya
network erişimi yapılmadı. İleride yalnızca ayrı ve açık bir kullanıcı yetkisiyle yeni bir
contract hazırlanabilir. Başarılı registry extraction tek başına `blocked_by_measurement_design`
gate'ini veya training yetkisini kapatmaz; unresolved overlap policy ve capability measurement
ayrı kalır.

## 8. Sonuç

151n ve 151o korunmuş provisional chronological records'dur. Bu local correction, önceki
95,000/10,718 selector hatasını düzeltir; frozen source/derived chain üzerinden 829 ve 713'ü
tanımlarıyla ayırır; 5,000 subjects, 25,000 semantic facts, 50,000 bilingual rows ve exact
65,717 pattern inventory'yi yeniden üretir. Buna karşılık benchmark ve source-model registry
kanıtları executed bounded wave açısından incomplete collection/extraction olarak kalır.

Güncel karar `blocked_by_measurement_design`; training yetkisi yoktur.
