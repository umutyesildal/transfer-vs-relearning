# 147 — LUNA-Worker 2 Model Provenance ve M1 Kısa Liste Denetimi

**Tarih:** 2026-08-07 (Europe/Berlin)  
**Durum:** WP1 tamamlandı; yalnızca read-only denetim  
**Kapsam:** Model provenance, mevcut M1 kanıtı ve bir sonraki bounded local baseline audit için
kısa liste. Bu belge training izni, model indirme izni veya HU çalışma izni değildir.

## 1. Karar özeti

**WP1 verdict: `shortlist_ready_for_local_baseline_audit`.**

Bu verdict yalnızca kaynaklı metadata kontrolünün bir sonraki sınırlı, yerel baseline audit'ine
yeterli olduğunu söyler. Yeni M1/M2 eğitimi, büyük model indirmesi veya Slurm işi başlatma yetkisi
vermez.

Önerilen Pareto kısa liste:

1. **`allenai/OLMo-2-0425-1B`** — güçlü açık provenance, base model, eğitim artefaktlarının ve
   recipe bilgisinin açıklığı nedeniyle birincil aday.
2. **`EleutherAI/pythia-1.4b`** — English tabanlı, base, veri sırası/checkpoint ailesi ve eğitim
   kodu açık olduğu için yüksek yeniden üretilebilirlik adayı.
3. **`tiiuae/falcon-rw-1b`** — model kartında açıkça English-only olarak belgelenmiş base model;
   Türkçe headroom'ı ölçmek için en temiz provenance adayı, fakat Türkçe adaptation başındaki
   olası tokenizer maliyeti ayrıca ölçülmeli.
4. **`Qwen/Qwen2.5-1.5B`** — ana “unseen Turkish” adayı değil; mevcut tez zincirinin
   **multilingual positive control** ve tekrarlanmış M1 referansı olarak tutulmalı.
5. **`stabilityai/stablelm-2-1_6b`** — yalnız ikinci seviye yeniden test adayı; önceki M1 ekranında
   global robustness güçlü olsa da held-out/min cell ve PPL kapıları geçilmedi, ayrıca kartta
   listelenen diller arasında Türkçe yok.

## 2. WP0'dan devralınan M1 kanıtı

### 2.1 Qwen M1: geçerli ve dondurulmuş referans

Yerel proje kayıtları Qwen2.5-1.5B ile 2.500 İngilizce fact üzerinde iki seed'li M1 tekrarını
geçerli bir storage/robustness referansı olarak kaydediyor. Seçim, sonuç görüldükten sonra serbest
seçim değil, her run'da bütün kapıları geçen en erken checkpoint kuralıyla yapılmış:

| Seed | Seçili step | Robust factual | Minimum relation robust | WikiText-2 PPL | PPL/base |
|---|---:|---:|---:|---:|---:|
| 42 | 75 | 96.08% | 88.2% | 15.909 | 1.082 |
| 43 | 50 | 96.20% | 90.2% | 15.169 | 1.032 |

Seçili model-only manifest hash'leri Document 127'de dondurulmuştur:

- seed 42 / step 75: `aed52ff8baeb01b89efef443caa560b707871dfe52fde6bcec1d8ae3e46fb032`
- seed 43 / step 50: `af3569aae2bd8066f51bb0ff1fecd4eec13eb74b5ba794915eae565f13f8bd53`

Bu kanıt **Qwen'i yeni Türkçe model adayı olarak temizlemez**. Qwen model kartı modelin 29'dan
fazla dili kapsayan multilingual bir base/pretraining modeli olduğunu söylüyor; Türkçenin kesin
token veya veri payı kartta verilmemiştir. Bu nedenle Qwen'de “Türkçe görülmedi” varsayımı
yapılmayacak, yalnızca pozitif multilingual kontrol olarak kullanılacaktır.

### 2.2 Eski Qwen Türkçe pilotunun yorumu

M2-clean ve M3-fact, aynı M1'den çıkan kardeş kollarla yaklaşık 1,048,576 token saf Türkçe
Wikipedia adaptasyonu üzerinden yürütülen geçerli fakat dar dozlu bir pilot olarak korunur. M3-fact
TR→EN başlığında M2-clean'e göre seed 42'de +1.86 pp, seed 43'te +1.89 pp yükselmiştir; ancak
önceden dondurulan iki-seed primary interaction kapısı toplamda geçmemiştir
(`primary_success_criterion_not_met`). Bu, “training teknik olarak bozuktu” veya “Qwen geçersizdi”
sonucu değildir; yaklaşık 1M-token Wikipedia dozunun ana causal soruyu çözmeye yetmediğine dair
negative/inconclusive pilot kanıtıdır.

## 3. Kaynaklı model provenance tablosu

Erişim tarihi tüm dış kaynaklar için **2026-08-07**'dir. Kanıt düzeyi: **A** = birincil model
kartı veya model makalesi; **B** = yerel frozen proje sonucu; **C** = bu belgedeki inference veya
gelecek audit planı.

| Model | Kaynak iddiası | Base/stage | Dil provenance | Reproducibility | Tez için yorum |
|---|---|---|---|---|---|
| OLMo-2 0425 1B | Model kartı 1B OLMo 2 base ailesini, açık repo/checkpoint/training bilgilerini ve Apache-2.0 lisansını verir. OLMo 2 makalesi yaklaşık 4T-token ilk aşama ve 50B-token mid-training düzenini açıklar. **A** | Base; stage bilgisi açık | English odaklı; Türkçe görünürlüğü “unseen” diye iddia edilemez. **A/C** | Kod, checkpoint ve eğitim raporu güçlü. **A** | Birincil yeni provenance adayı; Türkçe headroom ölçülebilir. |
| Pythia 1.4B | Model kartı English base model, The Pile ve yaklaşık 299.9B training-token bilgisini verir; Pythia projesi aynı veri sırası, 154 checkpoint ve kodu açıklar. **A** | Base; checkpoint ailesi açık | English; Türkçe özel miktarı raporlanmıyor. **A** | Çok güçlü checkpoint/data-order izi. **A** | Birincil reproducibility adayı; gerçek adaptation headroom'ı audit ile ölçülmeli. |
| Falcon-RW-1B | Kart, modeli English-only base model olarak tanımlar; RefinedWeb üzerinde yaklaşık 350B token, GPT-2 tokenizer ve 2048 context bilgisini verir ve başka dillerde uygun genelleme beklenmemesi konusunda uyarır. **A** | Base; recipe özeti açık | **English-only açıkça belgeli.** Bu, Türkçe hiç görülmediğinin matematiksel kanıtı değildir; fakat en temiz provenance sinyalidir. **A/C** | Veri/recipe ve lisans bilgisi yeterli; tam training trace sınırlı. **A** | Birincil headroom adayı; tokenizer fertility riski yüksek olabilir. |
| Qwen2.5 1.5B | Kart multilingual base/pretraining modelini, 29+ dil ve 1.54B parametre sınıfını verir; Türkçe miktarı verilmez. **A** | Base; seçili M1 checkpoint'leri yerel olarak frozen. **A/B** | Türkçe exposure bilinmiyor; “unseen” olarak sınıflandırılamaz. **A** | Yerel M1 iki seed ile tekrarlanmış. **B** | Multilingual positive control ve mevcut M2-A/M2-B başlangıç referansı. |
| StableLM 2 1.6B | Kart yaklaşık 2T diverse multilingual/code token, yedi dil listesi, 4096 context ve Stability AI Community License bildirir; Türkçe listede değildir. **A** | Base | Türkçe listelenmiyor; multilingual olduğu için unseen varsayımı yapılamaz. **A** | Kaynak recipe orta; yerel M1 screen sonucu mevcut. **A/B** | İkinci seviye aday; önceki robustness/PPL başarısızlığı nedeniyle ana kısa listeye alınmıyor. |

## 4. Ordinal provenance skoru ve Pareto okuması

Document 146'daki 0–2 ölçeği yardımcı tanıdır; toplam puan otomatik seçim değildir.

| Model | Turkish provenance | Stage | Reproducibility | Existing M1 evidence | Turkish headroom | Compute fit | Ana trade-off |
|---|---:|---:|---:|---:|---:|---:|---|
| OLMo-2 1B | 1 | 2 | 2 | 1 | 1 | 2 | Provenance güçlü; yerel M1 kanıtı yok. |
| Pythia 1.4B | 1 | 2 | 2 | 1 | 1 | 2 | Açıklık güçlü; Türkçe exposure belirsiz. |
| Falcon-RW-1B | 2 | 2 | 1 | 1 | 2 | 2 | English-only sinyali güçlü; tokenizer maliyeti olası. |
| Qwen 1.5B | 0 | 2 | 1 | 2 | 1 | 2 | M1 kanıtı güçlü; Türkçe headroom temiz değil. |
| StableLM2 1.6B | 0 | 1 | 1 | 1 | 1 | 2 | Mevcut screen faydalı ama iki ana gate başarısız. |

**Inference:** OLMo/Pythia/Falcon aynı “en iyi model” iddiasını temsil etmiyor; üç farklı
provenance–headroom Pareto noktasını temsil ediyor. Bu yüzden bir sonraki bounded baseline audit'i
en fazla iki yeni adayı ve Qwen positive control'ü birlikte değerlendirmeli; başarısız adayları
rank-ordering ile kurtarmamalıdır.

## 5. Ana listeye alınmayan modeller

- **SmolLM2-1.7B:** güçlü English veri provenance'ına rağmen yerel robust factual kapılarda
  39.6% referans ve remediation sonrasında 52.2–55.8% aralığı ile ana M1 sorusuna uygun kanıt
  vermedi. Bu dal kapalıdır.
- **Gemma-2-2B:** English ağırlıklı base model olarak açıkça gated/lisans ve erişim koşullarına
  sahiptir; yerel screen'de held-out/per-relation robustness ve PPL drift ciddi biçimde başarısız
  oldu. Yeni ana aday yapmak mevcut negatif kanıtı yok saymak olur.
- **Llama-3.2-1B:** multilingual base olup resmi destek listesinde Türkçe yok; bu yokluk Türkçe
  exposure yokluğu değildir. Yerel screen'de relation-specific robustness ve PPL ratio başarısız
  olduğu için ana liste dışıdır.

## 6. Bounded local baseline audit için zorunlu girdiler

Bu audit henüz yapılmadı ve model indirme başlatılmadı. Onaylanırsa aşağıdaki girdiler kaynak
revision'larıyla dondurulmalıdır:

1. En fazla iki yeni aday: OLMo-2/Pythia/Falcon arasından provenance ve tek-GPU fit ile seçilmiş
   iki model; Qwen positive control ayrı tutulur.
2. Her aday için exact model-card revision veya commit, config/tokenizer hash, lisans ve kaynak
   corpus/training-stage özeti.
3. Mevcut M1 factual screen'in aynı population, forms, relation binding, PPL ve retention
   evaluator'ları; model-family karşılaştırması için yeni threshold seçilmemeli.
4. Türkçe tokenizer fertility ve held-out PPL için küçük, frozen, modelden bağımsız audit sample;
   büyük corpus indirme veya materialization bu aşamaya dahil değildir.
5. Her model için “Türkçe exposure bilinmiyor” ile “English-only belgeli” ayrımını manifestte ayrı
   alanlar olarak tutmak.

## 7. Açık provenance riskleri

| Risk | Etki | Karar |
|---|---|---|
| Qwen Türkçe pretraining payı yayımlanmıyor | Türkçe unseen iddiası kurulamaz | Qwen yalnız positive control. |
| English-only kartlar gerçek sıfır Türkçe maruziyetini kanıtlamaz | Headroom aşırı yorumlanabilir | Baseline capability ve tokenizer ölçümü zorunlu. |
| Model kartı ile paper arasında stage/token tanımları farklı olabilir | Exposure karşılaştırması bozulur | Raw token, epoch ve tokenizer bağlamı ayrı tutulur. |
| Lisans veya gated erişim modeli değiştirebilir | Reproducibility/uygulanabilirlik riski | Contract öncesi exact revision ve izin audit'i. |

## 8. Günlük çalışma günlüğü

| Alan | Kayıt |
|---|---|
| Tarih/saat | 2026-08-07, Europe/Berlin |
| İş paketi | WP0 doğrulaması ve WP1 model provenance |
| Okunan kaynaklar | AGENTS.md; Documents 100, 106, 110, 127, 136, 138, 140a, 142, 143, 144, 145, 146; OLMo-2, Pythia, Falcon-RW-1B, Qwen, StableLM, SmolLM2, Gemma, Llama model kartları; OLMo-2/Pythia/SmolLM2 makaleleri |
| Doğrulanan iddialar | Qwen M1 iki seed; eski Türkçe pilot verdict'i; candidate stage/language/reproducibility metadata |
| Çelişkiler | Kartta “English-only/English” yazması Türkçe exposure sıfır demek değildir; Qwen Türkçe payı bilinmiyor |
| Üretilen dosya | `documentation/147_LUNA_MODEL_PROVENANCE_AND_M1_SHORTLIST_AUDIT_TR.md` |
| Açık sorular | Exact revisions, local tokenizer/PPL audit ve corpus seçimi |
| Yetki sınırı | HU erişimi yok; training/evaluation yok; büyük indirme yok; artifact silme/taşıma yok |

## 9. Dış kaynaklar

Erişim: 2026-08-07. Bağlantılar birincil model kartı veya makale sayfasıdır.

- [OLMo-2-0425-1B model card](https://huggingface.co/allenai/OLMo-2-0425-1B) — **A**
- [OLMo 2 paper](https://arxiv.org/abs/2501.00656) — **A**
- [Pythia-1.4B model card](https://huggingface.co/EleutherAI/pythia-1.4b) — **A**
- [Pythia project](https://github.com/EleutherAI/pythia) — **A**
- [Falcon-RW-1B model card](https://huggingface.co/tiiuae/falcon-rw-1b) — **A**
- [Qwen2.5-1.5B model card](https://huggingface.co/Qwen/Qwen2.5-1.5B) — **A**
- [StableLM 2 1.6B model card](https://huggingface.co/stabilityai/stablelm-2-1_6b) — **A**
- [SmolLM2-1.7B model card](https://huggingface.co/HuggingFaceTB/SmolLM2-1.7B) — **A**
- [Gemma-2-2B model card](https://huggingface.co/google/gemma-2-2b) — **A**
- [Llama-3.2-1B model card](https://huggingface.co/meta-llama/Llama-3.2-1B) — **A**

## 10. Yerel proje kaynakları

- [Document 106 — M1 Cross-Family Model Screening Result](106_M1_CROSS_FAMILY_MODEL_SCREENING_RESULT.md)
- [Document 110 — Turkish Bridge Corpus Result And Freeze](110_TURKISH_BRIDGE_CORPUS_RESULT_AND_FREEZE.md)
- [Document 127 — Qwen Scale Replication Result And SmolLM Lambda025 Status](127_QWEN_SCALE_REPLICATION_RESULT_AND_SMOLLM_LAMBDA025_STATUS.md)
- [Document 136 — Qwen M2/M3 Endpoint Evaluation GPU Allocation Status](136_QWEN_M2_M3_ENDPOINT_EVALUATION_GPU_ALLOCATION_STATUS.md)
- [Document 146 — LUNA-Worker 2 Detailed Research And Audit Handoff](146_LUNA_WORKER_2_DETAILED_RESEARCH_AND_AUDIT_HANDOFF_TR.md)

