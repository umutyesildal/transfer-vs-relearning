# Document 151ag — CORPUS SELECTION DECISION AND EXACT C1 RECONCILIATION (TR)

**Tarih:** 2026-08-08  
**Authority:** Documents 145, 148, 149, 150, 151, 151h, 151i, 151p, 151aa, corrected 151ab,
151ae, 151af ve bu altı dosyalık read-only reconciliation  
**Durum:** `FROZEN DECISION — vngrs CONDITIONAL; MATERIALIZATION NOT AUTHORIZED`

## 1. Kapsam ve karar özeti

Bu belge, corrected Document 151ab inventory wave'inin tamamlanmış operational çıktısını ve
HU'daki tam olarak izin verilen altı dosyayı reconcile eder. HU üzerinde yalnızca aşağıdaki
dosyalar read-only okunmuştur; hiçbir HU dosyası, root'u veya source path'i değiştirilmemiştir:

```text
/vol/tmp2/yesildau/luna_measurement_design_input_preparation_v1/
  source_allowlist_ledger.jsonl
  model_tokenizer_inventory.jsonl
  evaluation_input_inventory.jsonl
  c1_reconciliation.jsonl
  inventory_report.json
  final_inventory_audit.json
```

Bu pass network, public HTTP, download, corpus materialization, scoring, inference, evaluation,
GPU/Slurm, training, cleanup/deletion veya başka bir HU read işlemine izin vermemiştir. Karar:

| Kaynak | Frozen rol | Karar | Açıklama |
|---|---|---|---|
| `vngrs-ai/vngrs-web-corpus` | primary in-domain Turkish adayı | `CONDITIONAL PRIMARY MATERIALIZATION CANDIDATE` | Exact revision ve 10.000-record operational/sample evidence var; full release file/shard route, execution-time license capture, full-corpus quality/LID/dedup/PII/contamination evidence henüz yok. |
| `trwiki-20260601` | cross-domain control | `CONTROL ONLY` | Primary in-domain corpus değildir; ayrı frozen control olarak tutulur. |
| `uonlp/CulturaX` | comparative alternative | `excluded_access_blocked` | Erişim koşulu kabul edilmemiştir. CulturaX–vngrs comparative selection veya superiority claim yapılmaz. |

`vngrs` bu kararla `quality_pass`, frozen training corpus, selected adaptation corpus veya
`ready_to_train` değildir. Primary scientific gate
`blocked_by_measurement_design`; corpus-specific contributing gate
`blocked_by_corpus_selection_or_materialization` olarak kalır.

## 2. Yerel ve HU evidence kimliği

Ön koşul olarak local authority hash'leri doğrulanmıştır:

| Belge | SHA-256 |
|---|---|
| corrected `151ab` | `3ff0823f8a4aa5f806ab451abfffa989e0d70f1b1ca6b240229306cfac99c06c` |
| `151ae` | `b6a90ce5573de1c29828186dbc278c7c92c87dc1e435ef44965d0eff6f8e1601` |
| `151af` | `1e96a4b8d29edc50a8f151a34990c93edf3b5115dfb76416500261f8f8d817d1` |

HU'da yeniden hesaplanan altı dosyanın kimliği şöyledir:

| Dosya | Format/satır | Bytes | SHA-256 |
|---|---:|---:|---|
| `source_allowlist_ledger.jsonl` | 60 JSONL satırı | 51,879 | `ba2680ebcd7c76a16899673a446dba5b2dc1f60889b4d45d52776744b4e62827` |
| `model_tokenizer_inventory.jsonl` | 5 JSONL satırı | 4,142 | `cb67300fc08460d51ea7b92ccd2db1f897983216d6e8dcc3df872dc082fabbec` |
| `evaluation_input_inventory.jsonl` | 6 JSONL satırı | 2,938 | `db1652a284c8bae33ca8159329c93311bc1c3784e3123fa2c8072a987ed16eab` |
| `c1_reconciliation.jsonl` | 17 JSONL satırı | 12,885 | `c8d5968bde15cdfd11dbd9db5d62186a5aaba9fded07e5711db305194385d3c8` |
| `inventory_report.json` | tek JSON object | 3,004 | `b7b5661a8ac14476ac3d156d95baa9ebf709c6f13d5212bff5cc20c62fc2d08b` |
| `final_inventory_audit.json` | tek JSON object | 2,702 | `23ef2d0929a7b97ce3b9cf33c2108e39e335552678f63df4492c472a548cb503` |

Inventory report'undaki 78,118-byte pre-final-audit toplamı ve final audit hariç 80,820-byte
toplamı birbirini doğrular. Final audit self-reference içermez ve en son yazılmıştır.

## 3. Exact C1 status/count reconciliation

### 3.1 Satır ve status sayıları

| Inventory | Exact satır | Status dağılımı | Doğal kimlik duplicate | C1 sonucu |
|---|---:|---|---:|---|
| source allowlist | 60 | Bu ledger'da `status` alanı yok; her kayıt `source_path` identity metadata'sıdır | 0 (`source_path`) | Identity ledger tamam; status alanı bu dosya için uygulanamaz. |
| model/tokenizer | 5 | 3 `metadata_manifest_verified`; 2 `not_in_this_inventory_allowlist` | 0 | Qwen selected manifest coverage var; OLMo/Falcon yokluğu çıkarılmamış, allowlist dışı olarak doğru sınıflanmış. |
| evaluation input | 6 | Tekil status enum yok; 2 `candidate_evidence_only`, 1 `cross_domain_control`, 1 `general_language_control`, 1 `not_created`, 1 `primary_in_domain_turkish_input` | 0 (`role,path,purpose`); `purpose` tek başına 2 kez tekrar eder ve duplicate değildir | Corpus rolleri ve eksik seçili artifact açıkça ayrılmış. |
| C1 reconciliation | 17 | 12 `observed_existing_compact_evidence`; 2 `verified_existing_selected_manifest`; 1 `blocked`; 1 `existing_control_identity_stat_only`; 1 `existing_input_identity_stat_only` | 0 (`source_path` veya scalar `field`) | Exact C1 evidence status reconciliation tamam; corpus seçimi ayrı blocker olarak kalıyor. |
| inventory report | 1 object | `PASS_OPERATIONAL_INVENTORY`; scientific `BLOCKED`; primary `blocked_by_measurement_design`; contributing `blocked_by_corpus_selection_or_materialization` | 0 | Operational PASS, scientific completion yok. |
| final audit | 1 object | `PASS`; `ready_to_measure=false`; `ready_to_train=false` | 0 | Output-chain integrity PASS; scientific gate açılmaz. |

Toplam C1 reconciliation status count:

```text
observed_existing_compact_evidence = 12
verified_existing_selected_manifest = 2
blocked = 1
existing_control_identity_stat_only = 1
existing_input_identity_stat_only = 1
total c1_reconciliation rows = 17
```

### 3.2 Required-field ve duplicate değerlendirmesi

“Missing” ile “bu row türünde uygulanamaz” ayrımı korunmuştur. Source ledger'ın tüm 60 satırında
`source_path` vardır; bu dosyada status beklenmediği için status eksikliği evidence failure
sayılmamıştır. Evaluation inventory'nin altı satırında contract identity, access mode, role ve
`selected_adaptation_corpus_artifact` alanları vardır. C1 scalar rows için source-path/field-list
alanlarının uygulanmaması doğrudan row semantiğidir; bu satırlar selected corpus, trwiki control
ve WikiText identity durumunu bildirir.

| Alan grubu | Exact bulgu | Yorum |
|---|---|---|
| Model rows | Beşinin `contract_sha256`, `model`, `status` alanı vardır. Üç allowlisted Qwen row'unda `state`, `tokenizer_bytes_read=0` ve `large_weight_rehash_bytes=0` vardır; iki allowlist-dışı row `state`/byte alanlarını taşımaz. | İki satır model absence değildir; `not_in_this_inventory_allowlist` olarak fail-open yapılmadan kaydedilmiştir. |
| Evaluation rows | Zorunlu inventory alanlarında eksik yoktur. | `exists=false`, null path ve corpus blocker açıkça kaydedilmiştir. |
| C1 rows | 12 compact evidence row'unda field list/source path; iki selected-manifest row'unda field identity; üç scalar row'unda field semantiği vardır. | Üç scalar row'da `source_path` veya `fields` olmaması, schema varyantıdır; gizli evidence gibi yorumlanmaz. |
| Natural keys | Source `source_path`, model `(model,state veya allowlist-dışı model)`, evaluation `(role,path,purpose)`, C1 `(source_path veya scalar field)` anahtarlarında duplicate yoktur. | `purpose=candidate_corpus_or_provenance_evidence_inventory` iki farklı path için tekrar eder; bu beklenen non-unique label'dır. |

### 3.3 Model-state ve corpus-evidence coverage

Model-state coverage exact olarak:

| State/role | Count | Status | Bilinen sınır |
|---|---:|---|---|
| Qwen M1 seed42 step75 | 1 | `metadata_manifest_verified` | Manifest identity okundu/hash'lendi; large weights rehash edilmedi. |
| Qwen M1 seed43 step50 | 1 | `metadata_manifest_verified` | Aynı sınırlı metadata kapsamı. |
| Qwen home durability fallback | 1 | `metadata_manifest_verified` | Archive manifest identity; model bytes rehash edilmedi. |
| OLMo-2-0425-1B | 1 | `not_in_this_inventory_allowlist` | Acquisition yapılmadı; absent sonucu çıkarılamaz. |
| Falcon RW-1B | 1 | `not_in_this_inventory_allowlist` | Acquisition yapılmadı; absent sonucu çıkarılamaz. |

Corpus/input evidence coverage exact olarak:

| Evidence | Count | Status/role |
|---|---:|---|
| WikiText-2 raw input identity | 1 | stat-only, general-language control; content hash yeniden hesaplanmadı |
| `trwiki-20260601` sample identity | 1 | stat-only, frozen cross-domain control |
| Candidate evidence directories | 2 | stat-only, selected adaptation artifact değildir |
| Selected adaptation corpus | 1 logical row | `exists=false`, `blocked_by_corpus_selection_or_materialization` |
| Primary in-domain held-out split | 1 logical row | `exists=false`, bu inventory contract'ında authorize edilmedi |

151h/151i'den gelen vngrs candidate evidence ayrıca şunları destekler: immutable revision
`ee5c6201ee84457a18182bfc483a7d8a7f3655ba`, `train` split, 50,336,214-row universe, ilk istekten
önce üretilmiş 100 unique page ID, 10,000 unique record, 102 request ve 2 retry. Sample LID
`9,988/10,000 = 99.88%` document top-1 Turkish ve `201/10,000 = 2.01%` strict mixed-line
diagnostic'tir. Mixed line-level bir işarettir; document'ın non-Turkish olduğunu söylemez.
Near-dedup repair'i cap-free 5-gram/MinHash/LSH ile raporlanmıştır. Bunlar full corpus quality
pass veya frozen training-corpus evidence değildir.

## 4. Corpus selection decision

### 4.1 vngrs — conditional primary materialization candidate

`vngrs-ai/vngrs-web-corpus` seçilebilirlik için şu olumlu, fakat sınırlı, gerekçelere sahiptir:

1. 151h/151i ile exact revision ve 10,000-record operational/sample-manifest gate'i
   kapatılmıştır; sample complete ve duplicate source ID sayısı sıfırdır.
2. Sample document-level Turkish LID sonucu yüksektir; mixed-line oranı document non-Turkish
   kararı olarak kullanılmamıştır.
3. Documents 145, 148 ve 149 vngrs-web corpus'u Turkish web diversity, VBART/MODA ve CPT
   literatür bağlamında makul bir primary candidate olarak gösterir.

Ancak şu koşullar çözülmeden primary corpus seçimi tamamlanmış sayılmaz: exact release file ve
shard listesi, her shard için immutable route/byte/hash/row manifesti, execution-time license
evidence, full-corpus LID/quality/dedup/PII aggregates, 65,717 synthetic inventory ve benchmark
overlap ledgers. Dataset card'daki yaklaşık `84.9 GB`, `50.3M pages` ve `25.33B VBART tokens`
aynı immutable release'ın execution evidence'i olarak kullanılmayacaktır; token sayısı VBART
bağlamındadır ve aday model tokenlarına çevrilmez.

### 4.2 trwiki ve CulturaX

`trwiki-20260601` dar fakat frozen cross-domain control'dur. Primary Turkish in-domain split'in
yerine geçirilmez ve vngrs ile aynı domain olarak yorumlanmaz.

`uonlp/CulturaX` `excluded_access_blocked` olarak kalır. Erişim şartı kabul edilmediği için
CulturaX örneklenmeyecek, materialize edilmeyecek ve vngrs–CulturaX comparative selection veya
quality üstünlüğü iddiası yapılmayacaktır. Bu durum vngrs-only repair/materialization candidate
kararını otomatik olarak iptal etmez; karşılaştırmalı seçim unavailable kalır.

## 5. Gate ve sonraki authority

```text
c1_inventory_reconciliation = PASS
vngrs_selection = CONDITIONAL_PRIMARY_MATERIALIZATION_CANDIDATE
vngrs_quality_pass = false
selected_adaptation_corpus = false
primary_in_domain_split = false
primary_gate = blocked_by_measurement_design
corpus_contributing_gate = blocked_by_corpus_selection_or_materialization
ready_to_measure = false
ready_to_train = false
```

Bu karar training, baseline scoring, model/tokenizer acquisition, corpus materialization veya
Documents 152–154 yetkisi değildir. Ayrı frozen contract Document 151ah'dir; 151ah mevcut
metadata boşlukları nedeniyle `PREPARATION_BLOCKED` ve `UNEXECUTED` kalır. 151ai/151aj yalnızca
gelecekteki execution result/gate için reserve edilir; bu turda oluşturulmaz.

