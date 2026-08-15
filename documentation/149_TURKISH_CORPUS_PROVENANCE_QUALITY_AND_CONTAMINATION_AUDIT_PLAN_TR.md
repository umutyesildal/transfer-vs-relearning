# 149 — Türkçe Corpus Provenance, Kalite ve Contamination Audit Planı

**Tarih:** 2026-08-07 (Europe/Berlin)  
**Durum:** WP3 tamamlandı; corpus seçimi sample audit sonrasına bırakıldı  
**WP3 verdict:** `wikipedia_control_plus_web_candidate`  
**Kapsam:** Mevcut Wikipedia kontrolünün ve web-corpus adaylarının metadata/provenance/kalite
denetim planı. Bu belge büyük download, corpus materialization veya training izni değildir.

## 1. Karar özeti

Bir sonraki tasarım için en savunulabilir corpus durumu şudur:

- **Kontrol:** yerel olarak finalized edilmiş `trwiki-20260601`; provenance, contamination scan,
  deterministic split ve SHA-256 kayıtları güçlüdür ancak domain tekdüzedir ve önceki pilot dozu
  yaklaşık 1M tokenla sınırlıdır.
- **Web adayı:** Turkish CulturaX veya `vngrs-ai/vngrs-web-corpus`; ikisi de daha geniş domain
  coverage için adaydır, fakat exact revision, file manifest, Turkish language-ID dağılımı,
  near-dedup, benchmark overlap ve akademik kullanım koşulları M2 contract'ı için henüz
  tamamlanmış değildir.
- **Kumru:** model/corpus provenance için önemli bir external reference'tır; yaklaşık 500GB/300B
  ile 84.9GB/25.33B sayıları aynı corpus gibi birleştirilemez.

Bu nedenle M2-A/M2-B'nin ana corpusu henüz seçilmemiştir. Mevcut Wikipedia kontrolünü web adayıyla
aynı audit şemasında karşılaştırmak gerekir; sample audit geçmeden büyük corpus indirilmeyecek ve
materialize edilmeyecektir.

## 2. Corpus seçenekleri ve provenance tablosu

Erişim tarihi dış kaynaklar için **2026-08-07**. **A** = birincil card/paper veya frozen local
manifest; **B** = yerel proje sonucu; **C** = audit planı/inference.

| Corpus | Canonical source / snapshot | Boyut ve içerik | Tokenizer/token | Filtre/dedup/provenance | Risk ve mevcut karar |
|---|---|---|---|---|---|
| `trwiki-20260601` | [Wikimedia dump](https://dumps.wikimedia.org/trwiki/20260601/trwiki-20260601-pages-articles.xml.bz2); yerel frozen result [Document 110](110_TURKISH_BRIDGE_CORPUS_RESULT_AND_FREEZE.md) | Extracted 684,703; filtered 505,100; dedup 505,016; clean retained 504,287; train 494,253, validation 10,034. Archive/source license Wikimedia Terms/CC BY-SA family; exact attribution manifestte taşınmalı. **A/B** | Kaynak tokenizer ile yayınlanmış total token sayısı yok; Qwen ve aday tokenizerlarda fertility/projected tokens henüz ölçülmedi. **B/C** | Exact dedup 84; 729 conservative contamination removal; retained verified synthetic full-name match 0; final manifest `108c72375bb253742831da3fafb9e4b4b7b736974cb3cf6ef13f9b0f167502f7`. **A/B** | Domain narrow; güçlü control, ana web adayının yerine otomatik konmaz. |
| Turkish CulturaX | [CulturaX dataset](https://huggingface.co/datasets/uonlp/CulturaX), [paper](https://aclanthology.org/2024.lrec-main.377/), Türkçe kullanım örneği [Bridging](https://aclanthology.org/2024.mrl-1.21/) | CulturaX 167 dil için cleaned multilingual dataset; Bridging tablosu Türkçe için yaklaşık 94.2M doküman ve 129.5B raporlanan token gösterir. Exact Turkish snapshot byte size/file list/revision bu auditte dondurulmadı. **A** | Paper/card token sayısı upstream tokenizer bağlamlı; aday tokenizer fertility ölçülmedi. **A/C** | Language ID, URL filtering, metric-based cleaning, document refinement ve dedup pipeline'i paperda raporlanır; exact Turkish post-filter distribution/near-dedup manifesti ayrıca gerekli. **A/C** | Büyük ve potansiyel olarak iyi domain coverage; exact revision/license/overlap çözülmeden seçim yok. |
| `vngrs-ai/vngrs-web-corpus` | [Dataset card](https://huggingface.co/datasets/vngrs-ai/vngrs-web-corpus); VBART paper [arXiv](https://arxiv.org/abs/2403.01308) | Card yaklaşık 84.9 GB, 50.3M pages, 25.33B VBART-token bildirir; VBART paper abstract'ta 135 GB cleaned corpus ifadesi vardır. Bunlar aynı release varsayılmayacak. **A** | 25.33B sayısı VBART tokenizer'a aittir; Qwen/OLMo/Pythia/Falcon fertility ve projected tokens ölçülmedi. **A/C** | MODA/paper/card cleaning sinyali var; heuristic cleaning ve semantic filtering/language-ID/MinHash near-dedup ayrıntıları tam kapanmış değil. **A/C** | Web diversity yüksek; provenance ve contamination audit'i tamamlanmadan ana corpus olamaz. |
| Kumru pretraining corpus claim | [Kumru-2B-Base](https://huggingface.co/vngrs-ai/Kumru-2B-Base), [Kumru-2B instruct](https://huggingface.co/vngrs-ai/Kumru-2B) | Base card yaklaşık 500 GB ve 300B pretraining-token iddiası verir; exact source corpus listesi/release manifesti bu kayıtta vngrs-web ile birebir bağlanmıyor. **A** | 300B'nin tokenizer/epoch/exposure tanımı açık biçimde vngrs 25.33B ile eşlenmedi. **A/C** | Clean/dedup iddiaları var; full component/domain/PII/benchmark overlap manifesti yok. **A/C** | Corpus seçeneği değil, unresolved provenance evidence. M2 corpus kararı bunun üzerinden verilmez. |

### 2.1 SFT verisi ayrı tutulacak

[Turkish-SFT-Dataset-v1.0](https://huggingface.co/datasets/AlicanKiraz0/Turkish-SFT-Dataset-v1.0) ve
Kara-Kumru gibi instruction/task kaynakları genel unlabeled CPT corpus tablosuna eklenmeyecektir.
SFT, language acquisition manipulation check'inin yerine geçmez.

## 3. Mevcut `trwiki-20260601` audit sonucu

Document 110'daki frozen sonuç bir sonraki denetimin kontrol standardıdır:

- archive/date/hash doğrulandı;
- 684,703 extracted document'dan exact dedup ve quality/contamination filtreleriyle 504,287
  temiz kayıt kaldı;
- 729 conservative removal, synthetic full-name surface ile gerçek dünya çakışmalarını güvenli
  tarafta temizledi; bu 729 kaydın hedef fact'i ifade ettiği anlamına gelmez;
- 20 removed, 20 flag-only ve 20 clean örneğin decisive-first review sonucu geçmiştir;
- verified retained synthetic full-name match 0'dır;
- train/validation split ve final manifest hash'i append-only kaydedilmiştir.

Bu corpus **quality/provenance control** olarak güçlüdür; fakat Wikipedia domain'i, web/news/forum
çeşitliliğini temsil etmez. Önceki M2-clean/M3-fact pilotunun negative/inconclusive sonucu
corpusun teknik olarak başarısız olduğu şeklinde yorumlanmayacaktır.

## 4. Kumru/vngrs sayı uyuşmazlığı: çözülmemiş kayıt

| Kaynak | Raporlanan iddia | Şu an söylenebilecek |
|---|---|---|
| Kumru-2B-Base card | yaklaşık 500 GB; 300B pretraining tokens | Model training exposure iddiası; corpus snapshot/tokenizer/epoch tanımı tam eşlenmedi. |
| vngrs-web-corpus card | yaklaşık 84.9 GB; 50.3M pages; 25.33B VBART tokens | Dataset release metadata; yalnız VBART tokenizer bağlamı. |
| VBART paper | yaklaşık 135 GB cleaned corpus | Paper publication snapshotı; current card ile aynı release olduğu kanıtlanmadı. |

Test edilmesi gereken hypotheses:

1. 500 GB başka veya unpublished corpus versionı olabilir.
2. 300B, 25.33B'nin birden fazla epoch/mixture exposure toplamı olabilir.
3. Tokenizer farkı byte/token oranını değiştirebilir, fakat tek başına 12x corpus byte farkını
   açıklayıp açıklamadığı ölçülmemiştir.
4. Kumru, vngrs-web-corpus dışı kaynaklar kullanmış olabilir.
5. Card/paper yayın sürümleri farklı olabilir.

**Sonuç:** Resmî source manifest, file list, tokenizer definition, epoch ve corpus component
tablosu bulunmadan uyuşmazlık **unresolved** kalır. Bu worker herhangi bir uzlaştırma yapmamıştır.

## 5. Büyük corpus indirmeden önce bounded audit planı

Bu bölüm bir sonraki aşama için test protokolüdür; bu oturumda sample indirilmedi ve corpus
materialize edilmedi.

### A. Metadata ve immutable file manifest

Her aday için önce yalnız card/paper/repository metadata'sı kaydedilir:

1. exact repo revision/commit veya snapshot date;
2. file path, shard sayısı, compressed/uncompressed byte, row/document count;
3. license, attribution, academic/commercial use kısıtları;
4. kaynak component (Wikipedia, mC4, OSCAR, web, news, forum vb.);
5. upstream tokenizer ve raporlanan token definition;
6. source URL, access date ve response/hash kaydı.

Revision, lisans veya shard listesi yoksa aday `corpus_choice_blocked` olarak işaretlenir.

### B. Stratified sample ve language ID

Metadata yeterliyse, her web adayından önceden sınırlandırılmış küçük sample alınır; önerilen
üst sınır sonraki contract'ta **source başına en fazla 10,000 document veya 1 GiB compressed**
olarak dondurulmalıdır. Sample şu strata'ları korumalıdır:

- shard/source/domain;
- document length quantile;
- page title/URL host;
- yayın zamanı varsa time bucket;
- random seed ve immutable row ID.

Her dokümanda language-ID confidence dağılımı, mixed-language oranı, Unicode script dağılımı ve
Turkish olmayan örneklerin manuel audit'i raporlanır. Language-ID yöntemi ve model/version manifest'e
yazılır; “dataset Turkish” etiketi tek başına yeterli kanıt değildir.

### C. Encoding, length, boilerplate ve quality

Sample üzerinde:

- UTF-8/Unicode normalization, replacement character ve control character sayıları;
- character/word/token length quantiles;
- duplicate paragraph, repeated n-gram ve low-information repetition;
- HTML/navigation boilerplate, URL soup, code/table oranı;
- spam, adult/zararlı içerik, PII ve kişisel iletişim bilgisi risk örnekleri;
- source/domain bazında kalite ve retention oranı.

Heuristic filter ile semantic quality filter ayrı sütunlarda tutulur. Kalite örnekleri “model
training için iyi/kötü” şeklinde tek bir skora indirgenmez.

### D. Exact ve near-duplicate

1. Unicode-normalized exact document hash;
2. normalized sentence/paragraph hash;
3. MinHash/LSH veya eşdeğer near-duplicate tahmini;
4. source/domain ve shard içi/arası duplicate oranları;
5. train/validation split öncesi ve sonrası duplicate leakage;
6. Wikipedia–web overlap ve corpus component overlap.

Exact hash ve MinHash seed/num-permutation/threshold parametreleri contract'ta önceden dondurulmalı;
sonuç görüldükten sonra eşik seçilmemelidir.

### E. Synthetic subject/object ve benchmark contamination

Frozen local Relation V2 inventory ile üç katmanlı tarama yapılır:

- exact surface match;
- lowercase/Unicode-normalized match;
- predeclared fuzzy/alias match ve manual decisive-first review.

Inventory referansı:

- 5,000 synthetic subject;
- 25,000 synthetic fact;
- 713 canonical-object surface;
- 65,717 total patterns;
- 20,000 declared training sentence.

Her candidate corpus için ayrıca:

- factual evaluation prompt/answer/alias surface overlap;
- M1 English factual corpus overlap;
- Turkish capability benchmark items ve açıklamalarının overlap'i;
- benchmark train/dev/test contamination;
- object-only collision ile decisive full-name/fact collision ayrımı

raporlanır. Flag-only hit training'den otomatik silme değildir; removal policy, manual sample ve
manifest ile birlikte dondurulur.

### F. Tokenizer fertility ve projected budget

Aynı frozen sample, aday modellerin kendi tokenizerlarıyla ölçülür:

- token/document, token/word, character/token;
- Turkish/English fertility ratio;
- uzun morfolojik kelimelerde parçalanma;
- byte fallback veya special-token oranı;
- projected tokens per source, per dose ve per update.

VBART-token, Qwen-token, OLMo/Pythia/Falcon-token sayıları tek bir raw total gibi karşılaştırılmaz.
Tokenizer fertility bir model kalite skoru değildir; compute exposure ve erişilebilirlik tanısıdır.

### G. SHA-256 ve freeze

Seçilecek aday için immutable manifest en az şu alanları içermelidir:

```text
source_url
source_revision_or_date
license
file_manifest_sha256
sample_manifest_sha256
normalization_version
language_id_version
dedup_method_and_parameters
contamination_inventory_sha256
tokenizer_revision_and_sha256
projected_token_budget
```

Sample audit sonucu `quality_pass`, `quality_conditional` veya `blocked` olarak kaydedilir. Ana
training corpusu yalnız frozen revision + hash + license + contamination report tamamlandıktan
sonra seçilebilir.

## 6. M2-A/M2-B için corpus tasarım ilkeleri

Corpus seçildikten sonra iki kardeş kol:

```text
same frozen base M1
├── M2-A: general Turkish corpus, target facts yok
└── M2-B: aynı corpus + matched target-fact rows
```

- Aynı toplam token/update budget.
- M2-B extra total token almaz; factual rows matched neutral Turkish rows'un yerine geçer.
- Aynı tokenizer, sequence length, LR, batch/effective tokens, checkpoint schedule ve replay.
- Target facts corpusdan önce contamination scan ile dışlanır veya predeclared policy ile ayrıştırılır.
- Turkish general corpus ve factual treatment corpusu ayrı manifest/hash alanlarına sahip olur.
- SFT/instruction data hiçbir kola gizlice eklenmez.

## 7. Günlük çalışma günlüğü

| Alan | Kayıt |
|---|---|
| Tarih/saat | 2026-08-07, Europe/Berlin |
| İş paketi | WP3 corpus provenance/quality/contamination audit planı |
| Okunan kaynaklar | Document 84, 110, 145, 146; Wikimedia dump metadata; CulturaX paper/card; vngrs-web-corpus card; Kumru base/instruct cards; VBART paper; Turkish-SFT card |
| Doğrulanan iddialar | Frozen Wikipedia counts/hashes; CulturaX/vngrs/Kumru published claims; SFT/CPT ayrımı |
| Çelişkiler | Kumru 500GB/300B vs vngrs 84.9GB/25.33B; VBART paper 135GB vs current card |
| Üretilen dosya | `documentation/149_TURKISH_CORPUS_PROVENANCE_QUALITY_AND_CONTAMINATION_AUDIT_PLAN_TR.md` |
| Açık sorular | Exact web revision, license, domain/LID/dedup/PII/overlap statistics, tokenizer projected budget |
| Yetki sınırı | HU erişimi yok; training/evaluation yok; büyük indirme/materialization yok; artifact silme/taşıma yok |

## 8. Dış kaynaklar

- [Wikimedia Turkish 2026-06-01 dump](https://dumps.wikimedia.org/trwiki/20260601/trwiki-20260601-pages-articles.xml.bz2) — **A**
- [Wikimedia Terms of Use](https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use) — **A**
- [Document 110 — frozen Turkish bridge corpus](110_TURKISH_BRIDGE_CORPUS_RESULT_AND_FREEZE.md) — **B**
- [CulturaX dataset card](https://huggingface.co/datasets/uonlp/CulturaX) — **A**
- [CulturaX paper](https://aclanthology.org/2024.lrec-main.377/) — **A**
- [Bridging the Bosphorus](https://aclanthology.org/2024.mrl-1.21/) — **A**
- [vngrs-web-corpus card](https://huggingface.co/datasets/vngrs-ai/vngrs-web-corpus) — **A**
- [VBART](https://arxiv.org/abs/2403.01308) — **A**
- [Kumru-2B-Base](https://huggingface.co/vngrs-ai/Kumru-2B-Base) — **A**
- [Kumru-2B](https://huggingface.co/vngrs-ai/Kumru-2B) — **A**
- [Turkish-SFT-Dataset-v1.0](https://huggingface.co/datasets/AlicanKiraz0/Turkish-SFT-Dataset-v1.0) — **A**

