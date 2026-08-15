# 151f — Bounded Audit Evidence-Integrity Correction and Externally Prompted Validation Report

**Tarih:** 2026-08-07 (Europe/Berlin)  
**İşçi:** LUNA-Worker 2  
**Tür:** Evidence-integrity correction and externally prompted validation  
**Kapsam:** 151a sözleşmesi, 151d resumed result ve 151e resumed decision gate  
**151a SHA-256:** `524c3202df94ec95123bedbd976fe972bc0c2b1baad3eb301356d0b962a10dd4`

## Revision note — authorship and independence (2026-08-07)

Bu belgeyi 151d ve 151e'yi üreten aynı **LUNA-Worker 2**, harici bir Codex evidence review'ün
prompt ettiği internal correction pass olarak yazdı. Bu nedenle LUNA-Worker 2, original resumed
audit'ten bağımsız değildir ve bu belge agent-level independent external review iddiasında
bulunmaz. Core SHA değerleri, `1,564` file count, `162,513,315` total bytes, sample
completeness ve gate interpretation daha sonra Codex tarafından spot-check edilmiştir. Bu
çalışma genuinely independent external review'ün yerini tutmaz.

## 1. Amaç ve değişmez kayıtlar

Bu belge 151d ve 151e'yi overwrite etmez veya sessizce düzeltmez. 151d ve 151e, 7 Ağustos 2026 tarihli resumed audit'in kronolojik/provisional kayıtları olarak korunur. Bu belge onların kanıt ağırlığını yeniden sınıflandırır, doğrudan HU kanıtına dayalı SHA/schema/timing düzeltmelerini kaydeder ve minimal bir repair contract gereksinimi üretir.

Bu correction pass'te training, Slurm, GPU evaluation, model-weight download, corpus materialization, cleanup, deletion, migration veya frozen-artifact mutation yapılmadı. HU'da yalnız mevcut audit kökü okundu. `AGENTS.md`, `ssh-client/README.md`, 151a, 151d ve 151e tamamen okundu. 151a hash'i eşleşti; bu raporun ilk yazımında `AGENTS.md` değiştirilmedi.

## 2. Timing: evidence write window ile response duration ayrımı

HU audit kökündeki regular files'in mtime taraması Europe/Berlin olarak şu pencereyi verdi:

| Ölçüm | Değer | Yorum |
|---|---|---|
| İlk kök dosya mtime | 2026-08-07 13:29:46.596 CET/CEST | İlk home-du preflight yardımcı dosyası |
| Son kök dosya mtime | 2026-08-07 14:21:47.065 CET/CEST | Son post-run storage audit raporu |
| Gözlenen evidence write window | yaklaşık 52 dakika | `mtime` aralığıdır; process runtime değildir |
| HU regular file sayısı | 1,564 | Cache/pyc dahil tüm audit-root regular files |
| Toplam regular-file bytes | 162,513,315 | SHA pass sırasında doğrudan okunan toplam |

Bu aralık audit evidence dosyalarının oluşturulma/değiştirilme penceresini gösterir. Original audit process'in gerçek execution duration'ı için başlangıç/bitiş process logu veya job manifesti yoktur; bu nedenle “audit 52 dakika sürdü” iddiası yapılmaz. Sonraki correction-pass SSH sorgularının birkaç saniyelik response süreleri de original execution duration değildir. Response-generation duration için HU evidence içinde ayrı, güvenilir bir ölçüm yoktur; assistant/API cevap süresi execution kanıtı olarak kullanılmamıştır.

## 3. HU üzerinde tam SHA-256 recomputation

Audit kökündeki bütün regular files, tek tek 1 MiB streaming chunks ile HU üzerinde yeniden hash'lendi. Tam per-file digest satırlarının sıralı birleşimi için aggregate digest:

```text
file_count: 1564
total_bytes: 162513315
complete_manifest_digest: ee518324d1d3aadc928a02cb2e362d016698524cfb9241ff3c78d2772ebf3dfe
```

Bu aggregate digest yeni bir manifest dosyası değildir; mevcut evidence üzerinde yeniden hesaplanan doğrulama özetidir. Hiçbir evidence dosyası değiştirilmedi.

### 3.1 Core evidence SHA tablosu

| HU evidence | Yeniden hesaplanan SHA-256 |
|---|---|
| `reports/bounded_metrics_quality_dedup_fertility_contamination_continuation_20260807.json` | `b2c76740a3cf3faa5125d37c2ddbe801706fa269c057c8ce0fe1b29225a92a26` |
| `reports/lid_metrics_vngrs_continuation_retry2_20260807.json` | `61d3a07a252eb445460fd7842c94b8344c3841512696c1da5346a0fe1214be8b` |
| `reports/lid_metrics_trwiki_continuation_retry2_20260807.json` | `c39eda9418495d4b3f875937892c73fe7a289c5dd551f347d8ed45c181655285` |
| `reports/quality_pii_continuation_retry3_20260807.json` | `be160cc3327cc111cc9c4c9f9824bcdc9bf2c53292c74a238b774c53c1835f39` |
| `samples/vngrs_seed42_max10000_20260807.jsonl` | `6ab077751b567a2973e95c517733c7b9f3c8b7738107687c718c8a8a2bfb6492` |
| `samples/trwiki_20260601_seed42_max10000_20260807.jsonl` | `1a916aca1f3e759ac391f235940b5b31b3a1f7a365f74bcd4b3da977d540e863` |
| `metadata/dataset_vngrs_info_continuation_20260807.json` | `5f1109d20c066f9963c25cde982bc26449cc0f0df21056e84ba848ba68048d18` |
| `metadata/dataset_culturax_info_continuation_20260807.json` | `d26ce68448aeb7808ea2a5d11170f80a2952488cbbc1983d82156fd16d356eff` |
| `metadata/lid.176.ftz_continuation_20260807` | `8f3472cfe8738a7b6099e8e999c3cbfae0dcd15696aac7d7738a8039db603e83` |

### 3.2 Document 151d ile quality SHA mismatch

151d'nin evidence manifest bölümünde `reports/quality_pii_continuation_retry3_20260807.json` için şu farklı digest kayıtlıdır:

```text
151d recorded: be160cc3327cc1118ea2a5d11170f80a2952488cbbc1983d82156fd16d356eff
HU recomputed: be160cc3327cc111cc9c4c9f9824bcdc9bf2c53292c74a238b774c53c1835f39
```

Bu bir SHA mismatch'tir. Evidence overwrite edilmedi, iki değer birleştirilmedi ve yanlış değer geriye dönük sessizce düzeltilmedi. 151d'nin ilgili kaydı tarihsel hata olarak kalır; doğru değer bu correction report'ta açıkça kaydedilir.

## 4. Sample-manifest compliance

151a her sample record/manifest için şu alanları zorunlu kılar: `source_repo`, immutable `revision`, `split/shard`, row/document ID, `sample_index`, transferred/compressed bytes, normalized-text SHA-256 ve UTC retrieval timestamp.

HU'da:

```text
/vol/tmp2/yesildau/luna_bounded_provenance_sample_audit_v1/manifests
```

path'i mevcut değildi; `find` sonucu manifest file count `0` oldu. Bu nedenle “empty manifest directory” değil, **manifest directory absent** denmelidir. Sample JSONL'leri manifest yerine geçmez.

### 4.1 Field-by-field table

| 151a required field | vngrs sample JSONL | trwiki sample JSONL | Compliance |
|---|---|---|---|
| `source_repo` | Exact key yok; `source` var | Exact key yok; `source` var | Fail; semantic source field contract field'i değildir |
| immutable `revision` | `revision` key var; metadata'daki exact repo SHA ile ilişkilendirilebilir | Per-record revision key yok; `source_path` var | vngrs partial, trwiki fail |
| `split/shard` | Exact key yok; `corpus` var | Exact key yok; `source_path` var | Fail |
| row/document ID | `row_idx` ve `original_id` var | `document_id` ve `source_line_index` var | Partial; required canonical field/schema yok |
| `sample_index` | Yok; `offset` sample index olarak deklarasyonlu değil | Yok | Fail |
| transferred/compressed bytes | Yok | Yok | Fail |
| normalized-text SHA-256 | Yok | `normalized_text_sha256` var | vngrs fail, trwiki partial |
| UTC retrieval timestamp | Yok | Yok | Fail |

Observed top-level keys yalnız schema doğrulaması için kaydedildi; raw sample text, isim, PII veya belge içeriği bu rapora alınmadı. Missing timestamp/byte değerleri geriye dönük doldurulmadı. Dolayısıyla iki sample da 151a'nın per-record manifest şartını karşılamaz.

## 5. vngrs completeness ve LID/quality/fertility statüsü

vngrs sample:

```text
documents: 3,400
sample JSONL bytes: 11,179,988
reported transfer-response bytes: 10,887,034
HTTP 429 responses: 66
```

Sample ne 10.000 dokümana ne de 1 GiB hard stop'una ulaştı. Durma nedeni rate-limit/access failure oldu. 151a sözlüğüne göre vngrs durumu:

```text
incomplete
blocked_by_operational_access
```

Mevcut vngrs LID, quality, dedup ve fertility değerleri bu nedenle **exploratory partial-sample diagnostics**'tir. Bunlar frozen, complete, contract-compliant web evidence'i veya full-source quality pass değildir.

## 6. trwiki LID yorum düzeltmesi

Trwiki için iki farklı ölçü açıkça ayrılmalıdır:

| Ölçüm | Sayı |
|---|---:|
| Document-level top-1 `tr` | `9,944 / 10,000 = 99.44%` |
| Strict mixed-line diagnostic | `4,388 / 10,000 = 43.88%` |
| Mutually exclusive Turkish-pass class | `5,484 / 10,000 = 54.84%` |
| Low-confidence class | `84 / 10,000 = 0.84%` |
| Non-Turkish class | `44 / 10,000 = 0.44%` |

`mixed`, ilk 64 non-empty satırın line-level diagnostic'idir: hem non-Turkish top-label line fraction'ı hem Turkish `p>=0.80` line fraction'ı eşiklerini karşılar. `mixed` bir dokümanın non-Turkish olduğu anlamına gelmez. Bu nedenle trwiki “yalnızca %54,84 Turkish” diye özetlenemez; document top-1 Turkish oranı %99,44'tür. %54,84 yalnız mutually exclusive Turkish-pass sınıfıdır.

## 7. Near-dedup contract deviation

151a şu yöntemi dondurmuştu: normalized character 5-gram, MinHash/LSH, `num_perm=128`, seed 42 ve estimated Jaccard `>=0.80`. 151a'da doküman başına 512 feature cap yoktu.

Gerçek implementation iki ayrı cap kullandı:

1. Near-dedup MinHash: doküman başına **512** deterministik feature;
2. Quality/repetition summary: doküman başına **2,048** sampled 5-gram feature.

512 cap 151a'da sonuçlardan önce frozen değildi. 2,048 quality cap de near-dedup contract'inin parçası değildir; ayrı bir diagnostic implementation choice'tur. Bu cap'lere dayanan near-dedup/repetition sonuçları exploratory/non-contract-compliant olarak sınıflandırılır.

151d/151e'deki “bounded tamamlandı” ifadesi bu nedenle tarihsel/provisional wording'dir; near-dedup 151a'nın original frozen contract'ı altında tamamlanmış sayılamaz. 151d/151e değiştirilmez; corrected status bu belge ve 151g'de uygulanır.

## 8. Synthetic inventory reconciliation

Canonical profile HU üzerinde doğrudan okundu:

```text
path: /vol/fob-vol6/mi25/yesildau/synthetic-data-generation/data/canonical_subject_profiles_5000.csv
rows: 5,000
unique subjects: 5,000
relations: profession, birthplace, residence, university, employer
```

Counting unit'ler ayrıştırıldığında:

| Unit | Frozen/observed definition | Count |
|---|---|---:|
| Semantic fact | unique `subject_id | relation`, five relations, language-independent | **25,000** |
| Bilingual resolved row | unique `subject_id | relation | language`, `en` and `tr` separately | **50,000** |
| Language-specific answer strings | unique values across five `_en` columns / five `_tr` columns | 571 en / 571 tr |
| Canonical object surface union | exact union of all ten language-specific answer columns | **829** |
| Alias inventory | inspected release paths | not present |
| Template/pattern inventory | declared 65,717; inspected paths | not materialized |
| Training sentence source | `english_training.jsonl` source lines | 104,169 |
| Declared training-sentence count | 151a inventory declaration | 20,000 |

Dolayısıyla önceki 50.000 sayı, 25.000 semantic fact'in iki dildeki resolved row'larının sayısıdır; semantic fact contradiction değildir. 5.000 subject × 5 relation = 25.000 language-independent facts ve ×2 language = 50.000 resolved rows.

713 ile 829 arasındaki fark ise aynı grain olduğu kanıtlanmış bir sayı değildir. HU'da erişilebilen exact sets ve hash'ler:

```text
English surface set (571): 9e6cf21046ab35c2b03997b374ea90e183229902d8906fbdabf7fb8fe228a8fa
Turkish surface set (571): 5cf365e19c22da55991713c93e8408948217b2b821f3423dd21173ba67e4ab61
Union surface set (829): 18e43a35961a75cf18919ff940555eb31aac96bde5a75adc15e96936262650df
```

151a'daki declared 713 surface setinin exact membership, definition veya hash'i mevcut release path'lerinde bulunmadı. Bu nedenle 713→829 reconciliation **unresolved** bırakılır; 713'ün hangi alt/set tanımına ait olduğu uydurulmaz. Alias, template, training sentence ve language-specific answer strings canonical semantic-fact count'ına dahil edilmez.

## 9. Corrected status and gates

151d ve 151e'nin corrected scientific statusu:

```text
preliminary/provisional evidence
not a completed contract-compliant audit
```

Primary current gate:

```text
blocked_by_operational_access
```

Gerekçe: vngrs required 10,000-record sample'a ulaşmadı, HTTP 429 ile kesildi ve 151a per-record manifest evidence'i yok; CulturaX sample'ı da erişim koşulu nedeniyle yok.

Secondary unresolved gate:

```text
blocked_by_measurement_design
```

Gerekçe: undeclared MinHash cap, benchmark revision/item/hash registry eksikliği ve 713 canonical-surface setinin unresolved olması; contamination definitions ve capability measurement freeze de tamamlanmamıştır.

Bu correction pass Documents 152–154'ü yetkilendirmez. Training veya herhangi bir execution contract'ı açılmaz.

## 10. Correction sınırı

Değiştirilmeyen kronolojik kanıtlar:

- `151a_BOUNDED_MODEL_AND_CORPUS_PROVENANCE_SAMPLE_AUDIT_CONTRACT_TR.md`
- `151b_BOUNDED_MODEL_AND_CORPUS_PROVENANCE_SAMPLE_AUDIT_RESULT_TR.md`
- `151c_POST_AUDIT_MODEL_CORPUS_AND_MEASUREMENT_DECISION_GATE_TR.md`
- `151d_BOUNDED_MODEL_AND_CORPUS_PROVENANCE_SAMPLE_AUDIT_RESUMED_RESULT_TR.md`
- `151e_POST_RESUMED_AUDIT_MODEL_CORPUS_AND_MEASUREMENT_DECISION_GATE_TR.md`

Bu belge yalnız correction evidence ve revised gate interpretation'dır. HU evidence dosyaları, raw samples, frozen model artifacts, synthetic release, caches ve mevcut user worktree outputs silinmedi veya overwrite edilmedi.
