# 151d — Bounded Model ve Corpus Provenance Sample Audit: Resumed Result

**Tarih:** 2026-08-07 (Europe/Berlin)  
**İşçi:** LUNA-Worker 2  
**Durum:** Tamamlandı; read-only bounded audit sonucu  
**Önceki kayıtlar:** `151b` ve `151c` ilk, erişim nedeniyle bloklanan denemenin append-only kaydıdır; bu belge onları değiştirmez.  
**Yetki:** Bu devam turu, kullanıcı tarafından açıkça verilen resumed-audit talimatı ve 151a'nın bounded HU read-only istisnası ile sınırlıdır.

## 1. Sonuç özeti

151a sözleşmesinin tamamlanabilir bounded bölümü gerçekleştirildi: üç model reposu için revision/config/tokenizer/weight-metadata provenance, iki web kaynağı için erişilebilen deterministik sample, `trwiki-20260601` control sample, fastText LID, kalite/PII aggregate, exact/near-dedup, tokenizer fertility/projection ve frozen Relation V2 contamination taraması üretildi.

Audit training readiness üretmedi. Final ölçüm kararı:

```text
blocked_by_measurement_design
```

Ana nedenler: CulturaX Turkish sample'ı gated/access-condition ve HTTP 429 nedeniyle alınamadı; benchmark revision/item-set/hash kanıtı yok; synthetic release'teki sözleşme sayıları erişilebilen profil tablosuyla uyuşmadı; 65.717 pattern ve frozen alias/fuzzy listesi erişilebilir release yolunda materialize edilmemiş; near-dedup bounded feature cap ile hesaplandı. Bu eksikler sonucu “clean corpus”, “zero contamination”, true BPC/bpb/PPL veya `ready_to_train` iddiası kurulmadı.

## 2. Sözleşme bütünlüğü ve değişmeyen sınırlar

151a dosyası:

```text
documentation/151a_BOUNDED_MODEL_AND_CORPUS_PROVENANCE_SAMPLE_AUDIT_CONTRACT_TR.md
SHA-256: 524c3202df94ec95123bedbd976fe972bc0c2b1baad3eb301356d0b962a10dd4
```

Audit başlangıcında ve sonuç yazılmadan önce hash yeniden doğrulandı. Aday, revision selector, seed 42, 10.000 doküman/1 GiB hard stop, LID eşikleri, quality alanları, dedup parametreleri veya verdict sözlüğü sonuç görüldükten sonra değiştirilmedi.

Kullanıcı tarafından verilen dar HU istisnasıyla yalnızca metadata/API/sample okuması yapıldı. Training, fine-tuning, GPU evaluation, full model-weight download, full corpus download/materialization, checkpoint/optimizer üretimi, frozen artifact mutation/cleanup ve Documents 152–154 oluşturma yapılmadı. Model weight içerikleri indirilmedi; küçük config/tokenizer dosyaları scratch'e alındı. Falcon'un `trust_remote_code` çalıştırması, untrusted remote Python code inceleme sınırı nedeniyle yapılmadı.

## 3. Storage preflight ve audit kökü

Sabit bounded audit kökü:

```text
/vol/tmp2/yesildau/luna_bounded_provenance_sample_audit_v1
```

Kullanılan alt dizinler `samples/`, `metadata/`, `manifests/`, `reports/`, `cache/`, `logs/`, `tmp/` kapsamındadır. Web sample'ları ve raporlar scratch'te kaldı; home'a kopyalanmadı.

İlk preflight sonucu:

| Kontrol | Sonuç |
|---|---:|
| Home usage | `14G /vol/fob-vol6/mi25/yesildau` |
| Home filesystem available | yaklaşık `610G` |
| `/vol/tmp` available | yaklaşık `18T` |
| `/vol/tmp2` available | yaklaşık `113T` |
| Home free inodes | `159,706,720` |
| `/vol/tmp` free inodes | `2,274,115,003` |
| `/vol/tmp2` free inodes | `2,284,473,909` |
| Audit scratch sonunda | `160M` |

Remote repository path resolution da kontrol edildi: `runs` `/vol/tmp/yesildau/transfer-vs-relearning/runs`, `artifacts` `/vol/tmp/yesildau/transfer-vs-relearning/artifacts` yoluna çözülüyor. Bu audit bunlara yeni run/artifact yazmadı.

Post-run kayıtları:

```text
/vol/tmp2/yesildau/luna_bounded_provenance_sample_audit_v1/reports/postrun_storage_capacity_20260807.txt
/vol/tmp2/yesildau/luna_bounded_provenance_sample_audit_v1/reports/postrun_home_large_files_20260807.txt
```

Post-run home usage yine `14G` olarak kaydedildi. `find ... -size +500M` kontrolü home'daki önceden yetkilendirilmiş iki frozen Qwen modelini ve mevcut Conda/CUDA environment library dosyalarını listeledi; audit kökünün sample, metadata, cache veya output dosyaları home'a yazılmadı. Bu mevcut büyük dosyalar audit tarafından oluşturulmadı veya değiştirilmedi. `/vol/tmp` ve `/vol/tmp2` kapasite/inode sonuçları yukarıdaki preflight ile uyumludur. Scratch'te cleanup yapılmadı; başarısız/boş retry metadata dosyaları da korundu.

## 4. Model provenance sonucu

### 4.1 Exact revision ve uzak ağırlık metaverisi

| Rol | Model / frozen selector | Resolved revision | Erişim/lisans evidence | Weight metadata; indirme durumu | Ara sonuç |
|---|---|---|---|---|---|
| A priori preferred candidate | `allenai/OLMo-2-0425-1B` / `stage1-step140000-tokens294B` | Hub snapshot `905c75e135fe579d16fad3639bf22e7abb0a5d29`; selector exact checkpoint adı olarak kaydedildi | public, `gated=false`; exact revision API `license=null`, cardData yok | `model-00001-of-00002.safetensors`: 4,983,360,992 B, LFS SHA `dac447e5...25671`; ikinci: 956,326,560 B, LFS SHA `853414...2ed43`; weight içerikleri indirilmedi | `metadata_conditional` |
| Secondary | `tiiuae/falcon-rw-1b` / `e4b9872bb803165eb22f0a867d4e6a64d34fce19` | exact contract SHA | public, `gated=false`; card `license: apache-2.0`, language `en`, dataset `tiiuae/falcon-refinedweb` | `pytorch_model.bin`: 2,623,348,889 B, LFS SHA `3a0d68...019251`; weight indirilmedi | `metadata_conditional` |
| Positive control | `Qwen/Qwen2.5-1.5B` / `8faed761d45a263340a0528343f099c05c9a4323` | exact contract SHA | public, `gated=false`; card `license: apache-2.0` | `model.safetensors`: 3,087,467,144 B, LFS SHA `a961db...aec796`; weight indirilmedi | `metadata_pass` |

Kısaltılmış LFS SHA'lar yalnız okunabilirlik içindir; tam değerler scratch metadata JSON'larında tutulmaktadır. OLMo için public/gated durumu ve exact repo snapshot çözüldü, ancak exact revision API'si license/cardData vermediği için provenance “pass” değil “conditional” bırakıldı. `main` veya başka checkpoint'e sessiz geçiş yapılmadı.

### 4.2 Config ve tokenizer runtime kontrolü

Küçük dosya manifestleri yalnız scratch'te tutuldu; full weight indirilmedi.

| Model | Config/architecture | Tokenizer | Türkçe probe |
|---|---|---|---:|
| OLMo | `olmo2`, `Olmo2ForCausalLM`, vocab 100,352, context 4,096, hidden 2,048, 16 layer | `TokenizersBackend`, fast, vocab 100,278; config SHA `3dc581...f32882a`, tokenizer SHA `73fd52...eaecca` | 40 karakterde 12 token |
| Falcon | `falcon`, `FalconForCausalLM`, vocab 50,304, context metadata `null`, hidden 2,048, 24 layer | `GPT2Tokenizer`, fast, vocab 50,257; config SHA `290abb...ee438f` | 40 karakterde 13 token |
| Qwen | `qwen2`, `Qwen2ForCausalLM`, vocab 151,936, context 131,072, hidden 1,536, 28 layer | `Qwen2Tokenizer`, fast, vocab 151,665; config SHA `0e8c8a...1e66f77`, tokenizer SHA `c03821...e87539` | 40 karakterde 12 token |

OLMo ve Qwen tokenizer/config yüklemesi local-only ve `trust_remote_code=false` ile tamamlandı. Falcon için güvenli JSON config ve tokenizer kontrolü tamamlandı; custom `configuration_falcon.py`/`modeling_falcon.py` dosyaları metadata olarak alındı, fakat çalıştırılmadı. Bu nedenle Falcon full runtime compatibility condition olarak kaldı.

## 5. Corpus provenance ve bounded sample

| Kaynak | Resolved metadata | Sample sonucu |
|---|---|---|
| `vngrs-ai/vngrs-web-corpus` | main SHA `ee5c6201ee84457a18182bfc483a7d8a7f3655ba`; public; `cc-by-nc-sa-4.0`; Turkish card; 50,336,214 train docs; dataset 141,807,806,497 B; download 84,893,303,434 B; 284 parquet shard | seed 42, viewer API block sample: 3,400 doc, 11,179,988 B sample JSONL / 10,887,034 B transfer response; 66 HTTP 429 ile durdu; 1 GiB sınırı aşılmadı |
| `uonlp/CulturaX`, Turkish config | main SHA `6a8734bc69fefcbb7735f4f9250f43e4cd7a442e`; `gated=auto`; private değil; card içinde `tr` config mevcut; metadata sibling listesi exact Turkish shard manifestinin tamamını vermedi | rows probe HTTP 429/erişim koşulu nedeniyle boş; sample alınmadı; full corpus indirilmedi/materialize edilmedi |
| frozen `trwiki-20260601` | Document 149 frozen manifest SHA `108c72375bb253742831da3fafb9e4b4b7b736974cb3cf6ef13f9b0f167502f7`; mevcut normalized source 684,703 satır; final clean retained 504,287; train 494,253 / validation 10,034 | mevcut scratch source'tan seed 42 reservoir sample: 10,000 doc, 24,464,725 B; source line read 684,703 |

Vngrs örneğinde row schema `text`, `corpus`, `original_id` olarak doğrulandı. CulturaX için card metadata'sı erişilebilir olsa da row sample erişimi kanıtlanmadı; bu nedenle CulturaX için kalite/dedup/fertility/overlap sayısı uydurulmadı.

### 5.1 CulturaX sayı açıklaması

CulturaX güncel card'ındaki **94,207,460 Turkish doküman** ve **64,292,787,164 upstream token** toplamı ile Bridging paper'da geçen yaklaşık **129.5B token** sayısı aynı ölçüm değildir. İlki dataset card/upstream doküman ve token accounting'i; ikincisi paper'ın kendi tokenizer/preprocessing ve corpus accounting'idir. Bu nedenle doğrudan çelişki ilan edilmedi ve iki sayı birleştirilmedi. Exact Turkish shard manifesti ve aynı preprocessing olmadan reconciliation yapılmadı.

## 6. LID sonucu

Official `lid.176.ftz` kullanıldı. Model SHA-256:

```text
8f3472cfe8738a7b6099e8e999c3cbfae0dcd15696aac7d7738a8039db603e83
```

Runtime `fasttext-wheel 0.9.2`, `numpy 1.26.4`; NFC, horizontal whitespace collapse, 65,536 karakter kap, ilk 64 non-empty line ve 151a eşikleri aynen uygulandı. `fasttext==0.9.2` kaynak kurulumunun pybind11/build bağımlılığı nedeniyle başarısız olması saklandı; wheel ile aynı resmi model kullanıldı.

| Sample | Docs | Turkish | Mixed | Low-confidence | Non-Turkish | Mean/median/min/max `p(tr)` |
|---|---:|---:|---:|---:|---:|---|
| vngrs | 3,400 | 3,342 (98.29%) | 57 (1.68%) | 0 | 1 (0.03%) | 0.9895 / 0.9925 / 0.2926 / 0.9984 |
| trwiki | 10,000 | 5,484 (54.84%) | 4,388 (43.88%) | 84 (0.84%) | 44 (0.44%) | 0.9467 / 0.9713 / 0 / 0.9981 |

Vngrs top-label dağılımı `tr=3397`, `en=2`, `tk=1` idi. Trwiki'de `tr=9944`; kalan top-label'lar çoğunlukla `en`, `de`, `az`, `fr` ve daha küçük sayılı dillerdir. Trwiki mixed oranı, Wikipedia control sample'ında multilingual/alıntı/karışık satır sinyalinin bulunduğunu gösterir; source'nin bütünü için Türkçe purity iddiası değildir.

## 7. Kalite ve PII aggregate

Quality geçişi 151a'daki alanlarla sınırlı kaldı. Character 5-gram repetition summary belgedeki sample başına 2,048 evenly-spaced feature cap ile üretildi; ayrıca MinHash dedup cap'i aşağıda ayrı kaydedilmiştir.

| Alan | vngrs (n=3,400) | trwiki (n=10,000) |
|---|---:|---:|
| normalized chars p50 / p90 | 1,720 / 5,605 | 664 / 4,054 |
| short `<50` | 0 | 6 |
| URL bulunan doküman | 60 | 369 |
| repeated-line flag `>=0.50` | 0 | 32 |
| sampled 5-gram repetition flag `>=0.50` | 16 | 104 |
| empty / replacement | 0 / 0 | 0 / 0 |
| HTML-tag bulunan | 8 | 6 |
| code/table marker | 0 | 0 |
| PII pattern hit bulunan doküman | 39 | 28 |

Aggregate PII pattern kategorileri yalnız `email`, `iban`, `ipv4`, `phone` olarak yazıldı; raw PII veya sample text bu belgeye alınmadı. Vngrs aggregate hit counts `email=35`, `iban=0`, `ipv4=8`, `phone=33`; trwiki `email=1`, `iban=0`, `ipv4=14`, `phone=36` idi. Bu sonuç hukuki güvenlik veya training suitability garantisi değildir.

## 8. Exact/near dedup ve overlap

Exact key 151a'daki NFC → Unicode whitespace runs tek ASCII space → strip → UTF-8 SHA-256 zinciriyle üretildi. Near dedup: normalized character 5-gram, MinHash `num_perm=128`, seed `42`, 32 band × 4 row LSH, estimated Jaccard `>=0.80`. CPU/bellek sınırı nedeniyle doküman başına en fazla 512 deterministik feature kullanıldı; bu bir full-corpus dedup sonucu değildir.

| Karşılaştırma | Exact | Near candidate | Near `J>=0.80` |
|---|---:|---:|---:|
| vngrs internal | 4 duplicate doc / 4 group; 3,396 unique hash | 103 | 5 |
| trwiki internal | 176 duplicate doc / 50 group; 9,824 unique hash | 845,768 | 2,385 |
| vngrs–trwiki cross-source | 0 shared exact hash | 328 | 0 |

CulturaX sample'ı yoktu; bu nedenle CulturaX internal, CulturaX–vngrs ve CulturaX–trwiki sonuçları yoktur. Near sonuçları bounded diagnostic'tir; full source contamination veya clean split kanıtı değildir.

## 9. Synthetic contamination inventory ve tarama

Frozen release bağlantısı:

```text
release commit: ec2b96a
release manifest SHA-256: 94df56dba548c81d39b03b7b7fe4f9a59d9555997e984fd7aed5cabd0a113425
derived inventory SHA-256: bf74e7d959785999d73a7081c71ffa903262ef32648224a6f97dbac4784097bf
```

151a'nın declared inventory'si `5,000 subject / 25,000 fact / 713 object surface / 65,717 pattern / 20,000 training sentence` idi. Erişilebilen remote profile tablosu ve training JSONL üzerinde yeniden sayımda `5,000 subject`, dil alanları ayrı fact-row sayıldığında `50,000 resolved rows`, `829 object surface`, 20,000 seed-42 training sentence sample ve 104,169 source line görüldü. Bu 25,000-vs-50,000 ve 713-vs-829 farkı açıklanmadığı için frozen contamination inventory doğrulanmış sayılmadı; 65,717 pattern erişilebilir release yolunda materialize değildi.

| Sample | Subject-only | Object-only | Subject + object/full-fact | Exact declared training sentence |
|---|---:|---:|---:|---:|
| vngrs | 17 doc / 17 hit | 3,039 doc / 9,761 hit | 0 doc / 0 hit | 0 |
| trwiki | 367 doc / 391 hit | 6,637 doc / 21,720 hit | 17 doc / 33 hit | 0 |

Object-only/common-surface hit'leri target fact sonucu olarak yorumlanmadı. Frozen alias/fuzzy listesi mevcut olmadığı için probable alias/fuzzy scan ve manuel adjudication yapılmadı; raw subject/object isimleri belgeye yazılmadı. Bu nedenle “zero contamination” sonucu yoktur.

## 10. Tokenizer fertility ve bütçe projection

Full model inference yapılmadı; true BPC/bpb/PPL ölçülmedi. Aşağıdaki sayılar aynı bounded sample üzerinde yalnız tokenizer fertility ve reference-byte projection'dır. `byte_fallback_ratio`, `unknown_token_ratio` ve `special_token_ratio` üç tokenizerda da sample düzeyinde `0.0` raporlandı; diacritic probe token sayıları Falcon/OLMo/Qwen için sırasıyla `18/13/11` idi.

| Model | Source | Tokens | tok/word | tok/char | bytes/token | Projected tokens at reference bytes |
|---|---|---:|---:|---:|---:|---:|
| OLMo | vngrs | 3,683,401 | 2.965 | 0.386 | 2.838 | 29.91B |
| OLMo | trwiki | 7,394,021 | 3.083 | 0.394 | 2.732 | 0.713B |
| Falcon | vngrs | 4,774,533 | 3.843 | 0.500 | 2.190 | 38.77B |
| Falcon | trwiki | 8,731,986 | 3.641 | 0.465 | 2.313 | 0.842B |
| Qwen | vngrs | 3,175,001 | 2.555 | 0.333 | 3.293 | 25.78B |
| Qwen | trwiki | 6,976,953 | 2.909 | 0.371 | 2.895 | 0.673B |

Vngrs projection card download bytes `84,893,303,434`, trwiki projection normalized source bytes `1,948,052,715` üzerine kuruludur. Bunlar compute budget estimate'idir; model likelihood veya BPC değildir. Cross-tokenizer raw PPL sıralaması çıkarılmadı.

## 11. Benchmark contamination

TurkishMMLU, Turkish EXAMS, TurBLiMP ve CETVEL/TurkBench için exact immutable revision + item-set + hash bu frozen 151a scope içinde çözülemedi. Durum:

```text
blocked_by_measurement_design — clean claim yok
```

Sayı, item veya “benchmark temiz” sonucu uydurulmadı.

## 12. Operasyonel başarısızlıklar ve korunmuş kanıt

- İlk `151b`/`151c` denemesi HU erişim/approval koşulunda bloklandı; bu belgeler değiştirilmedi.
- CulturaX rows probe HTTP 429/access condition nedeniyle boş kaldı; metadata korunmuş, sample uydurulmamıştır.
- Vngrs sample 66 HTTP 429 sonrasında bounded hard stop yaptı; 3,400 kayıt ve byte sınırı kaydedildi.
- `fasttext==0.9.2` source build pybind11/build bağımlılığı nedeniyle başarısız oldu; aynı resmi `lid.176.ftz` ile `fasttext-wheel 0.9.2` fallback runtime kaydedildi.
- Falcon `trust_remote_code` compatibility path untrusted remote Python code çalıştırılmadan bırakıldı; güvenli JSON config/tokenizer yolu ayrı raporlandı.
- Boş veya başarısız retry dosyaları overwrite edilmedi: ilk Falcon metadata, ilk OLMo/Qwen small-manifest ve bazı tokenizer retry dosyaları 0-byte/başarısız kayıt olarak korundu.

## 13. Evidence manifest

Ana scratch kanıtları:

```text
metadata/model_olmo_hfapi_continuation_20260807.json
metadata/model_olmo_files_metadata_continuation_20260807.json
metadata/model_falcon_files_metadata_continuation_retry1_20260807.json
metadata/model_qwen_files_metadata_continuation_20260807.json
metadata/model_small_{olmo,qwen,falcon}_manifest*_20260807.json
metadata/model_runtime_tokenizer_*_20260807.json
metadata/dataset_culturax_info_continuation_20260807.json
metadata/dataset_vngrs_info_continuation_20260807.json
metadata/vngrs_rows_probe_continuation_20260807.json
samples/trwiki_20260601_seed42_max10000_20260807.jsonl
samples/vngrs_seed42_max10000_20260807.jsonl
reports/lid_metrics_*_continuation_retry2_20260807.json
reports/quality_pii_continuation_retry3_20260807.json
reports/bounded_metrics_quality_dedup_fertility_contamination_continuation_20260807.json
reports/postrun_storage_capacity_20260807.txt
reports/postrun_home_large_files_20260807.txt
```

Ana rapor SHA'ları:

```text
reports/bounded_metrics_quality_dedup_fertility_contamination_continuation_20260807.json
  b2c76740a3cf3faa5125d37c2ddbe801706fa269c057c8ce0fe1b29225a92a26
reports/lid_metrics_vngrs_continuation_retry2_20260807.json
  61d3a07a252eb445460fd7842c94b8344c3841512696c1da5346a0fe1214be8b
reports/lid_metrics_trwiki_continuation_retry2_20260807.json
  c39eda9418495d4b3f875937892c73fe7a289c5dd551f347d8ed45c181655285
reports/quality_pii_continuation_retry3_20260807.json
  be160cc3327cc1118ea2a5d11170f80a2952488cbbc1983d82156fd16d356eff
```

Kaynak sample JSONL'leri ham içerik içerdiğinden Git'e veya Markdown'a kopyalanmadı.

## 14. Verdict ve kapanış

- **OLMo:** `metadata_conditional`; revision/config/tokenizer/weight metadata çözüldü, fakat exact revision license/card evidence yok.
- **Falcon:** `metadata_conditional`; exact revision/license/config/tokenizer geçerli, fakat custom runtime çalıştırılmadı.
- **Qwen:** `metadata_pass`; positive control olarak exact revision/license/config/tokenizer metadata kanıtı var.
- **vngrs:** `quality_conditional`; bounded sample güçlü Türkçe LID gösteriyor, fakat 429 nedeniyle partial sample ve contamination/benchmark kanıtı eksik.
- **trwiki:** `quality_conditional`; frozen control sample ve LID/quality/dedup mevcut, fakat mixed sample ve contamination/benchmark/near-dedup sınırlamaları sürüyor.
- **CulturaX:** `quality_conditional`; metadata ve Turkish config kanıtı var, row sample ise `blocked_by_access_condition`; source için sayısal clean/pass iddiası yok.

Bir sonraki execution contract'ı için gerekli measurement gate kapanmadığından bu belge 152/153 hazırlama yetkisi vermez. 151a'nın “no cleanup” kuralına uyuldu; frozen model, canonical manifest, unique dataset veya bilimsel sonuç silinmedi/overwrite edilmedi.
