# 151 — Pretraining Model, Corpus ve Measurement Decision Gate

**Tarih:** 2026-08-07 (Europe/Berlin)  
**Durum:** WP5 preliminary/revised gate; WP2 ve WP4 external-validation corrections recorded; yeni execution contract oluşturulmadı  
**Final verdict:** `blocked_by_corpus_evidence`  
**Yetki sınırı:** Bu belge training/HU/Slurm/büyük indirme/artifact mutation izni değildir.

## 1. Yönetici özeti

LUNA-Worker 2'nin WP1 çıktısı tamamlanmış, WP2 birincil kaynak granülerliğinde revize edilmiş,
WP3 planı tamamlanmış fakat sample audit'i açık, WP4 ölçüm mimarisi proposed/preselected fakat
freeze pending ve WP5 gate'i ön karar seviyesindedir. Sonuçlar birbirinden ayrılmıştır:

- **Model:** `shortlist_ready_for_local_baseline_audit`. OLMo-2-0425-1B, Pythia-1.4B ve
  Falcon-RW-1B yeni provenance kısa listesinde; Qwen2.5-1.5B mevcut M1 ve multilingual positive
  control olarak korunuyor; StableLM2 ikinci seviye aday.
- **Corpus:** `wikipedia_control_plus_web_candidate`. `trwiki-20260601` güvenilir frozen control;
  CulturaX/vngrs-web-corpus geniş web adayları; ancak ana corpus seçimi yapılmadı.
- **Measurement:** Within-model Turkish PPL + cross-model BPC/bits-per-byte, conditional
  base-compatible capability, bağımsız TurBLiMP/grammar adayı ve English retention yapısı
  proposed/preselected'dır; numeric threshold, exact item revision, license, hash, overlap ve
  floor/ceiling manifesti henüz frozen değildir. TurkishMMLU/EXAMS geniş knowledge/school/
  reasoning/cultural capability olarak etiketlenir; saf language acquisition değildir.
- **Gate:** Kumru'nun yaklaşık 500GB/300B iddiası ile vngrs-web-corpus'un yaklaşık 84.9GB/25.33B
  iddiası çözülemedi; bu yalnız bir provenance concern'dür. Exact corpus revision/license/file
  manifest, domain/LID, quality, exact/near-dedup, PII, benchmark overlap, synthetic-fact
  contamination ve tokenizer projected budget kapanmadan corpus evidence yeterli değildir.
  Measurement package'ın revision/item/hash/overlap/floor-ceiling/threshold eksikleri de ayrı
  blocker'dır.

Bu nedenle mevcut final karar **`blocked_by_corpus_evidence`** olarak korunur; kararın operasyonel
gerekçesi corpus provenance **ve** measurement freeze eksikleridir. Bu, Qwen pilotunun geçersiz
olduğu veya model kısa listesinin başarısız olduğu anlamına gelmez; bir sonraki deney ailesi için
causal yorumlamayı taşıyacak corpus ve ölçüm kanıtının henüz kapanmadığı anlamına gelir.

## 2. Doğrulanmış proje state'i

### 2.1 Qwen M1 ve M2/M3 geçmişi

Qwen2.5-1.5B English M1 iki seed'de tekrarlanmış, seçili model-only checkpoint'leri manifest ve
SHA-256 ile frozen edilmiştir. Robust factual sonuçlar seed 42'de 96.08%, seed 43'te 96.20%;
WikiText PPL/base 1.082 ve 1.032'dir.

Eski Qwen Türkçe family aynı frozen M1'den çıkan kardeş kollarla yaklaşık 1,048,576-token saf
Türkçe Wikipedia adaptation pilotudur:

- M1 TR→EN: seed 42 52.03%, seed 43 52.52%;
- M2-clean TR→EN: 33.29%, 33.70%;
- M3-fact TR→EN: 35.14%, 35.59%;
- M3−M2 TR→EN: +1.86 pp, +1.89 pp;
- primary two-seed interaction gate: `primary_success_criterion_not_met`.

Bu family operasyonel olarak geçerli, retention ve factual endpoint ölçümleri raporlanmış,
scientific olarak negative/inconclusive pilot olarak korunmuştur. Pilotun başarısız gate'i
Wikipedia corpusunun veya Qwen modelinin teknik failure'ı diye yeniden yazılmayacaktır.

### 2.2 Yeni ana tasarım

```text
same frozen M1
├── M2-A: general Turkish corpus; target facts yok
└── M2-B: aynı adaptation + controlled Turkish factual re-exposure
```

- M2-B'ye ekstra total token/update verilmez.
- Factual rows matched neutral Turkish rows'un yerini alır.
- M2-A ve M2-B aynı model, tokenizer, total budget, sequence length, LR, batch/effective tokens,
  English replay, checkpoint schedule ve measurement package kullanır.
- TR→EN primary, TR→TR secondary, EN→TR exploratory'dir.
- Yeni tasarımın primary estimand'ı `TR→EN(M2-B) − TR→EN(M2-A)` paired sibling-arm treatment
  contrast'ıdır; ayrıca repeated/unrepeated factual subgroup faktörü dondurulmadıkça interaction/
  DID olarak adlandırılmayacaktır.

## 3. Kaynak-model kısa listesi

| Aday | Neden kısa listede | Eksik/riski | Rol |
|---|---|---|---|
| `allenai/OLMo-2-0425-1B` | Açık base model, code/checkpoint/training provenance, 1B compute fit. | Türkçe exposure ve local M1 sonucu bilinmiyor. | Yeni birincil provenance adayı. |
| `EleutherAI/pythia-1.4b` | English base, The Pile/data order/checkpoint ailesi ve kodu açık. | Türkçe exposure bilinmiyor; tokenizer headroom ölçülmeli. | Yeni reproducibility adayı. |
| `tiiuae/falcon-rw-1b` | Model kartı English-only base; RefinedWeb ve yaklaşık 350B-token provenance. | English-only kart gerçek zero Turkish exposure kanıtı değil; tokenizer fertility riski. | Yeni headroom adayı. |
| `Qwen/Qwen2.5-1.5B` | Frozen M1, iki seed reproducibility, mevcut Türkçe pilotu. | Multilingual; Türkçe payı bilinmiyor. | Positive control ve retained pilot baseline. |
| `stabilityai/stablelm-2-1_6b` | Türkçe listelenmeyen multilingual base; Arabic adaptation literatürüyle ilişkili; local endpoint. | Prior screen PPL 1.477 ve robust min 69% ile gate dışı. | Sadece ikinci seviye fallback. |

### 3.1 Seçilmeyen modeller

- **SmolLM2-1.7B:** English training provenance iyi olsa da robust factual gate'i 39.6% referans
  ve remediation sonrası 52.2–55.8% aralığında kaldı; ana M1 sorusuna uygun değil.
- **Gemma-2-2B:** held-out/per-relation factual robustness ve PPL drift ciddi başarısız; gated/lisans
  koşulları da ek provenance yükü getiriyor.
- **Llama-3.2-1B:** multilingual ve Türkçe resmi destek listesinde yok; bu unseen kanıtı değildir,
  fakat local screen'de held-out relation robustness ve PPL ratio başarısız.

Rank-ordering ile frozen gate'i geçemeyen adaylar terfi ettirilmeyecek.

## 4. Türkçe corpus kısa listesi

| Corpus | Durum | Güçlü taraf | Bloker |
|---|---|---|---|
| `trwiki-20260601` | Frozen control | Exact dedup, 729 conservative contamination removal, verified retained synthetic match 0, train/val/final manifest hash. | Wikipedia-only/narrow domain; tokenizer projected budget yok. |
| Turkish CulturaX | Web candidate | Büyük multilingual cleaned corpus; Turkish split Bridging'de yaklaşık 94.2M docs/129.5B reported tokens. | Exact Turkish revision, license, file manifest/bytes, Turkish LID/domain, quality filters, exact+near dedup, PII, benchmark/synthetic-fact overlap ve tokenizer projected budget kapanmadı. |
| `vngrs-ai/vngrs-web-corpus` | Web candidate | Card 84.9GB/50.3M pages/25.33B VBART tokens; Turkish-specific web diversity. | VBART paper's 135GB claim; exact snapshot/license/file manifest, heuristic/LID/semantic quality, exact+near dedup, PII, benchmark/synthetic-fact overlap ve tokenizer projected budget unresolved. |
| Kumru pretraining claim | Evidence only | Turkish model provenance için useful reference; base/instruct ayrımı açık. | 500GB/300B claim vngrs 84.9GB/25.33B ile source manifest olmadan eşlenemez. |

SFT/instruction resources (`Turkish-SFT-Dataset-v1.0`, Kara-Kumru, MODA alignment data) CPT corpus
shortlist'ine eklenmez.

## 5. Kumru/vngrs unresolved kaydı

Bu decision gate şu hypotheses'lerden hiçbirini seçmiyor:

1. 500GB başka/unpublished corpus versionı;
2. 300B multiple-epoch or mixture exposure;
3. tokenizer byte/token farkı;
4. vngrs-web dışında ek sources;
5. paper/card release version farkı.

Resmî file manifest, exact tokenizer, epoch/exposure ve corpus component table olmadan sayıların
aynı şeyi gösterdiği söylenemez. Bu unresolved state, corpus blocker'larından yalnızca biridir;
`blocked_by_corpus_evidence` kararının tek gerekçesi olarak okunmayacaktır.

## 6. Literature-backed adaptation recipe seçenekleri

### R1 — Literature-backed project preference: full CPT + sabit tokenizer + sabit English replay

M2-A/M2-B için proje tercihi aynı general Turkish corpus ve aynı küçük English replay ile full
causal CPT'dir. Tokenizer extension yok; SFT/DPO/merge yok. B'de matched factual rows A'daki
neutral rows'un yerine geçer. Bu, **öneri/inference** düzeyindedir; frozen recipe veya execution
contract değildir.

Gerekçe: [How to Adapt Your Pretrained Multilingual Model to 1600 Languages](https://aclanthology.org/2021.acl-long.351/)
basit continued pretraining'in düşük kaynakta güçlü baseline olabileceğini, [Breaking Language
Barriers](https://aclanthology.org/2024.emnlp-main.441/) CPT ölçek ve convergence etkilerini,
[DIPLomA](https://aclanthology.org/2025.findings-emnlp.1355/) ise English replay ve alignment
ayrımını destekler.

### R2 — Diagnostic: full CPT + tokenizer extension

R1 fertility ciddi sorun gösterirse, aynı data/dose ve A/B eşitliğiyle tokenizer extension tek
faktörlü ablation yapılabilir. [SambaLingo](https://aclanthology.org/2024.mrl-1.1/) ve
[Sherkala-Chat](https://openreview.net/forum?id=wRcTCcb0H5) bunun kaynaklı karşılaştırmalı
motivasyonudur; ilk causal gate'te factual treatment ile karıştırılmamalıdır.

### R3 — Sonraki extension: CPT → ayrı SFT/PEFT/merge

[MODA](https://aclanthology.org/2026.sigturk-1.17/) ve DIPLomA çizgisinde language acquisition
sonrası alignment. Bu, base M2-A/M2-B measurement package'ından ayrıdır ve Document 151'in
öncelediği deney değildir.

## 7. Base vs instruction kararı

Ana deney **base causal LM** üzerinde kalır. Instruction checkpoint, chat template, synthetic
dialogue, SFT, DPO ve delta merge M2-A/M2-B'ye eklenmez. CETVEL/TurkBench'in instruction/chat
alt görevleri yalnız auxiliary context olabilir. Base-compatible likelihood/MCQ/cloze ölçümleri
ana Turkish capability manipulation check'tir.

## 8. Full CPT vs LoRA/adapters kararı

Ana causal estimand için **full CPT** proje tercihi olarak önerilir; M2-A/M2-B'de trainable
parameter set aynı olmalıdır. Full CPT seçimi henüz frozen değildir.
LoRA/adapters ilk ana karşılaştırmada kullanılmayacak, çünkü:

- language acquisition ile parameter-efficient capacity farkını karıştırır;
- target-fact re-exposure'ın full-model storage mı yoksa adapter storage mı olduğunu değiştirir;
- M2-A/M2-B kardeş arm karşılaştırmasına ek faktör sokar.

PEFT, yalnız full-CPT manipulation check ve base/capability gate'i geçtikten sonra ayrı
efficiency/extension sorusu olabilir.

## 9. Tokenizer extension ve English replay

- **Tokenizer:** İlk ana route mevcut tokenizer ile; fertility/byte fallback tanısı yapılır.
  Extension ancak predeclared fertility criterion sonrası, aynı A/B recipe ile ayrı ablation.
- **English replay:** Literature ve forgetting riskine dayanarak A/B'de aynı replay mix'i
  önerilir. Replay, M2-B treatment'ı değil, retention regularizer'ıdır. Exact token ratio,
  update budget ve seed henüz frozen değildir; seçilirse A/B'de birebir aynı olacak ve sonuçlardan
  sonra değiştirilmeyecektir.
- Factual B farkı replay veya tokenizer farkı değil, yalnız matched factual row replacement
  olmalıdır.

## 10. Türkçe capability package

Öncelik sırası (proposed/preselected; freeze pending):

1. Within-model Turkish PPL + cross-model BPC/bits-per-byte;
2. TurBLiMP primary independent linguistic diagnostic candidate, exact release/license/overlap/
   floor-ceiling audit'i geçerse; alternatif olarak CETVEL/TurkBench base-compatible grammar;
3. TurkishMMLU balanced MCQ likelihood subset, broad knowledge/reasoning/cultural capability;
4. EXAMS Turkish MCQ subset, broad school/reasoning capability;
5. TrClaim-19 optional secondary classification diagnostic.

Her item set için revision/hash, license, prompt/choice format, train-overlap, floor/ceiling ve
scoring rule frozen olmadığı için capability gate henüz açılmaz. Freeze edildiğinde M0/M1/M2-A/
M2-B aynı package'ı kullanacaktır.

Manipulation check'in üç parçası:

1. Turkish held-out PPL within-model beklenen yönde iyileşmeli; cross-model kıyas BPC/bits-per-byte
   ile yapılmalı;
2. en az bir bağımsız Turkish linguistic/base-compatible capability ölçümü beklenen yönde iyileşmeli veya
   önceden tanımlı equivalence/no-harm gerekçesi olmalı;
3. TurkishMMLU/EXAMS geniş capability olarak ayrı raporlanmalı;
4. English PPL ve EN→EN retention guardrail içinde kalmalı.

Sayısal thresholds benchmark audit ve bounded baseline görülmeden seçilmeyecek; factual treatment
sonrası geriye dönük seçilmeyecek.

### 10.1 Measurement blocker ledger

Measurement tarafı corpus'tan bağımsız olarak da henüz kapanmamıştır:

- exact Turkish held-out split ve English retention split hash'i;
- TurkishMMLU, EXAMS, TurBLiMP veya alternatif grammar subset için exact release/revision, item
  IDs, license, prompt/choice template ve scoring;
- BPC/bits-per-byte primary choice, UTF-8 byte rule ve tokenizer fertility protocol;
- training-corpus/benchmark/fact/synthetic-fact overlap manifesti;
- small-model baseline ile floor/ceiling ve uncertainty planı;
- predeclared numeric thresholds/equivalence/no-harm guardrail.

Bu kayıtlar olmadan “measurement package frozen” veya “capability gate açıldı” denmeyecektir.

## 11. Bounded M1 screen için gerekli inputlar

Bu bölüm Document 152 değildir; yalnız gelecekteki contract input listesidir:

- en fazla iki yeni model exact revision + Qwen positive control;
- model config/tokenizer/license/provenance manifestleri;
- 500-subject/2,500-fact veya Document 146'da belirlenecek eşdeğer bounded population;
- mevcut M1 factual robustness, relation binding, forms/scaffolds, PPL ve integrity evaluator'ları;
- same seed/checkpoint selection rule; result-seen checkpoint selection yok;
- local English baseline ve Turkish fertility/PPL diagnostic;
- explicit scratch output/cache/log/tmp plan, pre/post storage audit ve artifact retention;
- broad model/corpus download için ayrıca user authorization.

## 12. Factsiz Turkish dose pilotu için gerekli inputlar

M2-A/M2-B ana family öncesi factsiz dose pilotu düşünülürse:

- selected M1 ve exact model-only manifest/SHA;
- corpus exact revision, license, file/sample/contamination manifest;
- Turkish held-out split ve English retention split hash;
- dose ladder raw bytes + tokenizer-specific projected tokens;
- same tokenizer, LR, batch/effective tokens, sequence, updates, replay ve checkpoint rule;
- capability package item IDs, scoring and uncertainty plan;
- Turkish PPL/capability/English retention manipulation-check gates;
- no SFT/instruction data;
- scratch storage estimate and post-run retention policy.

Bu inputlar olmadan M2-B factual treatment planı açılmaz.

## 13. Risk register

| Risk | Olası etki | Önleyici kontrol |
|---|---|---|
| Qwen Turkish pretraining payı bilinmiyor | Unseen adaptation iddiası geçersizleşir | Qwen positive control; English-only ve unknown etiketlerini ayır. |
| Kumru/vngrs sayı uyuşmazlığı | Corpus token dose yanlış hesaplanır | Exact manifest/tokenizer/epoch çözülene kadar corpus block. |
| Web LID/boilerplate/spam | PPL/capability yanlış yorumlanır | Stratified sample, LID confidence, manual quality ve domain report. |
| Near-duplicate/benchmark overlap | Leakage ve sahte capability | Exact+MinHash, benchmark/fact overlap, frozen hashes. |
| Turkish tokenizer fragmentation | Compute dose ve language learning bozulur | Fertility ratio ve fallback audit; extension sadece ayrı ablation. |
| Instruction/SFT confound | Dil edinimi ile alignment karışır | Base CPT only; SFT/PEFT/merge ayrı extension. |
| English catastrophic forgetting | TR kazanımı genel korunum pahasına olur | English PPL + EN→EN guardrail; fixed replay. |
| Public benchmark floor/ceiling | Manipulation check güçsüz olur | Small-model baseline, paired uncertainty, multiple independent tasks. |
| Factual treatment contamination | B advantage genuine adaptation değildir | Synthetic inventory + fact/alias/answer overlap scan. |
| Exact corpus revision/license yok | Reproducibility ve yayın riski | `corpus_choice_blocked`; immutable file/sample manifest şartı. |

## 14. Tamamlanan, açık ve bloke işler

| Durum | İş |
|---|---|
| Tamamlandı | AGENTS + Document 146 zorunlu okuma zinciri; WP0 project-state verification. |
| Tamamlandı | WP1 model provenance ve M1 shortlist; verdict `shortlist_ready_for_local_baseline_audit`. |
| Revize edildi | WP2 Turkish/non-Turkish literature matrix; exact primary-source fields, LlamaTurk ve source-scoped NR kayıtları eklendi. |
| Plan tamamlandı; sample audit açık | WP3 corpus audit plan; existing Wikipedia control ve web candidate ayrımı. |
| Proposed/preselected; freeze pending | WP4 capability/manipulation-check structure; BPC/bits-per-byte, TurBLiMP priority ve sibling-arm estimand correction eklendi. |
| Açık | OLMo/Pythia/Falcon arasından exact bounded local baseline adaylarının seçimi ve metadata/hash audit'i. |
| Bloke | TurkishMMLU/EXAMS/TurBLiMP veya grammar subset exact revision, scoring, license, overlap, BPC rule, floor/ceiling ve threshold freeze. |
| Bloke | CulturaX/vngrs/Kumru provenance; exact revision/license/file manifest, domain/LID/quality, exact+near-dedup, PII, benchmark/synthetic contamination ve tokenizer budget. |
| Bloke | Corpus evidence kapanmadan yeni corpus seçimi ve M2-A/M2-B execution contract. |
| Yapılmadı | HU erişimi, Slurm, training/evaluation submission, large download/materialization, artifact mutation. |

## 15. Önerilen tek sonraki hareket

Kullanıcı onayından sonra **tek bir bounded, read-only provenance/sample audit** başlatılmalıdır:
Qwen positive control ile en fazla iki yeni model adayının metadata/hash kontrolünü ve Turkish
CulturaX/vngrs web adaylarının küçük stratified corpus sample'ını aynı önceden dondurulmuş audit
paketinde karşılaştırmak. Bu hareketin amacı model/corpus evidence'ı kapatmaktır; training,
evaluation sweep, HU/Slurm erişimi veya büyük corpus materialization değildir.

Bu audit tamamlanana kadar `ready_to_freeze_bounded_m1_screen_contract` veya
`ready_to_freeze_fact_free_turkish_dose_contract_using_existing_qwen` verdict'lerine geçilmeyecek;
Document 152–154 oluşturulmayacaktır.

## 16. Günlük çalışma günlüğü

| Alan | Kayıt |
|---|---|
| Tarih/saat | 2026-08-07, Europe/Berlin |
| İş paketi | WP5 birleşik model/corpus/measurement decision gate |
| Okunan kaynaklar | Documents 147, 148, 149, 150; Documents 100, 106, 110, 127, 136, 138, 140a, 142, 143, 144, 145, 146; cited primary model/corpus/literature sources |
| Doğrulanan iddialar | Model shortlist; Qwen pilot state; corpus controls/candidates; unresolved Kumru/vngrs; measurement rule |
| Çelişkiler | Corpus size/token claims unresolved; Qwen Turkish exposure unknown; benchmark revision/license not frozen |
| Üretilen dosya | `documentation/151_PRETRAINING_MODEL_CORPUS_AND_MEASUREMENT_DECISION_GATE_TR.md` |
| Açık sorular | Bounded sample results, exact revisions, overlap, tokenizer budget, thresholds |
| Yetki sınırı | No HU access, no training, no evaluation sweep, no large download, no artifact deletion/transport |

## 17. Kaynaklar (erişim: 2026-08-07)

### Yerel proje evidence

- [Document 106 — M1 Cross-Family Model Screening Result](106_M1_CROSS_FAMILY_MODEL_SCREENING_RESULT.md)
- [Document 110 — Turkish Bridge Corpus Result And Freeze](110_TURKISH_BRIDGE_CORPUS_RESULT_AND_FREEZE.md)
- [Document 127 — Qwen Scale Replication Result And SmolLM Status](127_QWEN_SCALE_REPLICATION_RESULT_AND_SMOLLM_LAMBDA025_STATUS.md)
- [Document 136 — Qwen M2/M3 Endpoint Evaluation Status](136_QWEN_M2_M3_ENDPOINT_EVALUATION_GPU_ALLOCATION_STATUS.md)
- [Document 146 — LUNA-Worker 2 Handoff](146_LUNA_WORKER_2_DETAILED_RESEARCH_AND_AUDIT_HANDOFF_TR.md)

### Dış birincil kaynaklar

- [OLMo-2 model card](https://huggingface.co/allenai/OLMo-2-0425-1B) ve [paper](https://arxiv.org/abs/2501.00656)
- [Pythia model card](https://huggingface.co/EleutherAI/pythia-1.4b) ve [project](https://github.com/EleutherAI/pythia)
- [Falcon-RW-1B model card](https://huggingface.co/tiiuae/falcon-rw-1b)
- [Qwen2.5-1.5B model card](https://huggingface.co/Qwen/Qwen2.5-1.5B)
- [CulturaX paper](https://aclanthology.org/2024.lrec-main.377/) ve [dataset card](https://huggingface.co/datasets/uonlp/CulturaX)
- [vngrs-web-corpus card](https://huggingface.co/datasets/vngrs-ai/vngrs-web-corpus)
- [Kumru-2B-Base card](https://huggingface.co/vngrs-ai/Kumru-2B-Base)
- [Bridging the Bosphorus](https://aclanthology.org/2024.mrl-1.21/)
- [MODA](https://aclanthology.org/2026.sigturk-1.17/)
- [How to Adapt Your Pretrained Multilingual Model to 1600 Languages](https://aclanthology.org/2021.acl-long.351/)
- [Breaking Language Barriers](https://aclanthology.org/2024.emnlp-main.441/)
- [Arabic Stable LM](https://arxiv.org/abs/2412.04277)
- [Sherkala-Chat](https://openreview.net/forum?id=wRcTCcb0H5)
- [DIPLomA](https://aclanthology.org/2025.findings-emnlp.1355/)
- [SambaLingo](https://aclanthology.org/2024.mrl-1.1/)
- [CETVEL](https://aclanthology.org/2026.eacl-long.46/), [TurkBench](https://arxiv.org/abs/2601.07020), [TurkishMMLU](https://arxiv.org/abs/2407.12402), [EXAMS](https://arxiv.org/abs/2011.03080)

## 18. External validation revision — 2026-08-07

- WP0–WP5 için “tamamlandı” ifadesi kaldırıldı; gerçek durum WP1 complete, WP2 revised, WP3
  plan complete/sample audit pending, WP4 proposed/preselected/freeze pending ve WP5 preliminary
  gate olarak kaydedildi.
- Kumru/vngrs mismatch artık tek blocker değildir. Exact corpus revision/license/file manifest,
  domain/LID/quality, exact+near-dedup, PII, benchmark/synthetic-fact contamination ve tokenizer
  budget ayrı corpus blockers olarak eklendi.
- Measurement blocker ledger eklendi: exact benchmark revisions/item IDs/hashes/licenses,
  BPC/bits-per-byte rule, overlap, floor/ceiling ve numeric thresholds tamamlanmadan measurement
  package frozen sayılmayacaktır.
- Full CPT ve English replay, literatür destekli proje önerisi/inference olarak etiketlendi;
  Bridging'in LoRA CPT kullandığı, diğer kaynakların farklı trainable scope kullandığı ve replay
  oranının frozen olmadığı açıklandı. Replay seçilirse A/B'de aynı retention regularizer olacaktır.
- Yeni tasarımın primary estimand'ı `TR→EN(M2-B) − TR→EN(M2-A)` paired sibling-arm treatment
  contrast'tır; repeated/unrepeated factual subgroup faktörü ayrıca dondurulmadıkça interaction/
  DID terimi kullanılmayacaktır.
- Historical Qwen pilot metrics, negative/inconclusive interpretation, `blocked_by_corpus_evidence`
  verdict ve Documents 152–154'ün oluşturulmamış olması korunmuştur.
