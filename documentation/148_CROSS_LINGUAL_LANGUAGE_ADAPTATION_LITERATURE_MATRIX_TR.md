# 148 — Cross-Lingual Language Adaptation Literatür Matrisi

**Tarih:** 2026-08-07 (Europe/Berlin)  
**Durum:** WP2 external-validation revision; required primary-source fields extracted to reported-source granularity; read-only  
**Kapsam:** Türkçe ve karşılaştırmalı düşük-kaynak dil adaptation çalışmaları. Bu belge recipe
önerir; execution contract, corpus indirme veya training yetkisi vermez.

Erişim tarihi dış kaynakların tamamı için **2026-08-07**'dir. Bu revizyonda **NR (not reported in
the reviewed primary sources)** yalnızca birincil makale/ek/model card içinde raporlanmayan alanlar
için kullanılır; “sonra çıkarılmalı” anlamına gelmez. Her NR kaydı, incelenen bölüm/sayfayı da
belirtir. Kanıt düzeyi **A** birincil makale/model card, **B** paper içindeki özetlenmiş deney
sonucu, **C** proje için inference/öneridir.

## 1. Literatürden ortak çerçeve

Çalışmalar üç ayrı soruyu çoğu zaman aynı model ailesinde ele alıyor:

1. **Dil edinimi:** unlabeled target-language CPT ile perplexity, morphology ve temel capability.
2. **Task alignment:** instruction/SFT/DPO/chat davranışı.
3. **Bilgi veya cross-lingual transfer:** hedef dildeki bilginin başka dilde erişimi.

Bu tezde birinci soru (Türkçe adaptation) ile üçüncü soru (TR→EN factual access) ayrılmalıdır.
İkinci soru ana M2-A/M2-B causal koluna sokulmayacak; base causal LM ölçümü tamamlandıktan sonra
ayrı bir extension olarak tutulacaktır.

## 2. Türkçe çekirdek kaynaklar

### 2.1 Bridging the Bosphorus

[Acikgoz, Erdogan, Yuret — Bridging the Bosphorus](https://aclanthology.org/2024.mrl-1.21/)
(MRL 2024, **A**).

- **Source model/stage:** English-pretrained modelleri Türkçeye adapte etme, Türkçe from-scratch
  model ve sonrasında instruction tuning karşılaştırmaları; exact model/checkpoint tablosu paper
  içinde, tek satırlık özetten daha ayrıntılıdır.
- **Hedef dil ve önceden görülme:** Türkçe; English-pretrained branch için Türkçe exposure'ın
  model bazında exact provenance'ı ayrı audit gerektirir, “unseen” genellemesi yapılmaz.
- **Tokenizer:** Adaptation branch'inde mevcut tokenizer; from-scratch branch'inde Türkçe
  tokenizer ayrımı paper'da incelenir. Yeni tezde tokenizer extension ana faktör yapılmamalıdır.
- **Corpus:** mC4, farklı OSCAR sürümleri ve CulturaX Türkçe splitlerini içeren tablolar; paper,
  Türkçe CulturaX için yaklaşık 94.2M doküman ve 129.5B raporlanan token gösterir. Bu, mevcut
  `trwiki-20260601` ile aynı corpus değildir.
- **Filtre/dedup:** Kaynak datasetlerin kendi cleaning/dedup pipeline'ları; exact dedup, language ID
  ve kalite ayrıntıları her upstream kaynağın provenance'ına bağlıdır.
- **Objective/mix:** CPT, from-scratch pretraining ve SFT karşılaştırmaları; dose/scaling
  deneyleri vardır. Exact LR, effective batch, sequence length, step ve replay oranı contract'a
  doğrudan kopyalanmayacak, paper tablo/eklerinden ayrıca dondurulacaktır.
- **Checkpoint/forgetting/capability:** Türkçe benchmark ve source-language catastrophic forgetting
  tartışılır; aynı fikir proje için PPL + EN→EN retention guardrail'ine çevrilmelidir.
- **Ders:** Wikipedia-only 1M-token pilotundan daha geniş domain ve dose ladder gerekir.
- **Kopyalanmayacak fark:** Instruction-tuning ve from-scratch sonuçları M2-A/M2-B'nin aynı frozen
  base'den full CPT causal karşılaştırmasıyla aynı estimand değildir.

### 2.2 MODA

[Bayar et al. — MODA](https://aclanthology.org/2026.sigturk-1.17/)
(SIGTURK 2026, **A**).

- **Source model/stage:** Qwen2.5-7B base; önce large-scale Turkish CPT, sonra parameter-efficient
  supervised fine-tuning ve model merging.
- **Hedef dil ve exposure:** Türkçe; base model multilingual olduğundan Türkçe unseen varsayımı
  yapılmamalı.
- **Corpus:** Turkish web corpus; paper/model kaynaklarında `vngrs-web-corpus` ile ilişkili
  provenance bulunur. Exact document/byte/token sürümü ve tüm karışım oranları contract'ta yeniden
  doğrulanmalı.
- **Tokenizer/filtre:** Paper özetinde tokenizer extension, language-ID yöntemi, exact dedup ve
  quality thresholds tam verilmez; bu nedenle tokenizer recipe kopyalanmayacak.
- **Objective/mix:** CPT → PEFT/SFT → merge. Exact LR, batch, sequence length, steps/epochs,
  target-language exposure ve replay ratio paperın ayrıntılı bölümlerinden alınmalı; abstract bu
  alanları dondurmaz.
- **Ölçüm:** TurkishMMLU, Turkish EXAMS alt kümesi ve TRCLAIM-19; base ve instruction-tuned
  Qwen2.5 karşılaştırmaları.
- **Ders:** Dil edinimini task alignment'dan ayırmak doğru; bizim ana factual kapıda SFT/merge yok.
- **Kopyalanmayacak fark:** MODA 7B, instruction ve merge ile görev odaklı nihai modeldir; küçük
  base modelde M2-B factual re-exposure ile aynı deney değildir.

### 2.3 VBART

[Turker, Ari, Han — VBART](https://arxiv.org/abs/2403.01308)
(arXiv/paper, **A**).

- **Source model/stage:** Türkçe encoder-decoder BART/mBART çizgisinde from-scratch sequence-to-
  sequence pretraining; decoder-only causal CPT değildir.
- **Hedef dil:** Türkçe monolingual model; source modelin Türkçe önceden görülme sorusu burada
  geçerli değildir çünkü model from-scratch kurulmuştur.
- **Corpus/tokenizer:** Paper cleaned `vngrs-web-corpus` ve Türkçe monolingual tokenizer bildirir;
  abstract 135 GB cleaned corpus ve multilingual tokenizerlara göre 11x'e kadar efficiency
  iddiasını verir. Güncel dataset card'daki 84.9 GB/25.33B VBART-token bilgisiyle aynı snapshot
  olduğu varsayılmayacaktır.
- **Filtre/dedup:** “cleaned” corpus var; exact pipeline, semantic filtering, spam/PII ve near-
  dedup alanları reviewed primary sources'ta **NR** (ayrıntılı source-scoped kayıt §8.4).
- **Objective/ölçüm:** Sequence-to-sequence pretraining ve çeşitli generation/understanding
  fine-tuning görevleri; tokenizer efficiency ve downstream Türkçe görevler raporlanır.
- **Ders:** Türkçe tokenizer fertility ölçümü gereklidir.
- **Kopyalanmayacak fark:** encoder-decoder architecture, from-scratch pretraining ve generation
  fine-tuning, decoder-only M2-A/M2-B'nin causal factual erişim testine aktarılmaz.

### 2.4 TURNA

[Uludoğan et al. — TURNA](https://aclanthology.org/2024.findings-acl.600/)
(Findings ACL 2024, **A**).

- **Source model/stage:** Türkçe encoder-decoder UL2 language model; curated Turkish corpus ile
  pretraining.
- **Hedef dil/exposure:** Monolingual Turkish model; from-scratch/monolingual setup olduğu için
  mevcut multilingual base exposure kıyasına doğrudan eşlenmez.
- **Corpus/filtre/tokenizer:** Paper corpusu “diverse, specifically curated” diye tanımlar; exact
  document/byte/token büyüklüğü, language-ID, dedup ve tokenizer bilgileri bu abstract seviyesinde
  dondurulmamıştır.
- **Objective/ölçüm:** UL2 pretraining; üç generation ve beş understanding görevi. Source-language
  forgetting ve cross-lingual factual direction bizim tasarımla aynı değildir.
- **Ders:** Türkçe görev coverage'ı yalnız chat benchmark'ıyla değil, understanding + language
  diagnostics ile kurmak gerekir.
- **Kopyalanmayacak fark:** UL2 encoder-decoder ve from-scratch training; M2-A/M2-B için recipe
  olarak yalnız “dil edinimini ölç” ilkesi alınır.

### 2.5 Kumru ve vngrs model/dataset cards

- [Kumru-2B-Base model card](https://huggingface.co/vngrs-ai/Kumru-2B-Base) — **A**: base/pretrained
  varyant.
- [Kumru-2B instruct model card](https://huggingface.co/vngrs-ai/Kumru-2B) — **A**: instruction
  varyant; CPT base ile karıştırılamaz.
- [vngrs-web-corpus dataset card](https://huggingface.co/datasets/vngrs-ai/vngrs-web-corpus) — **A**:
  corpus metadata; yaklaşık 84.9 GB, 50.3M sayfa ve VBART tokenizer ile 25.33B token iddiası.

Kumru base card yaklaşık 500 GB corpus ve 300B pretraining-token exposure bildirirken vngrs
dataset card 84.9 GB/25.33B VBART-token bildiriyor. Paper/card kaynakları bu iki sayıyı aynı
snapshot, aynı tokenizer veya aynı epoch toplamı olarak kesin bağlamıyor. Bu nedenle bu matrix'te
uyuşmazlık **unresolved** bırakılmıştır. Kumru, hazır M2 recipe'i değil provenance sorusunu
gösteren bir vaka çalışmasıdır.

### 2.6 CETVEL ve TurkBench

- [CETVEL](https://aclanthology.org/2026.eacl-long.46/) (**A**) 23 görevi yedi kategoriye ayıran,
  discriminative ve generative görevleri birleştiren kapsamlı Türkçe benchmark'tır. Base causal
  LM için tüm generative/instruction alt görevleri ana gate yapmak uygun değildir; grammar,
  likelihood/MCQ'ya çevrilebilen ve overlap audit'i geçmiş küçük alt set seçilmelidir.
- [TurkBench](https://arxiv.org/abs/2601.07020) ve [online space](https://huggingface.co/turkbench)
  (**A**) 8,151 örnek/21 alt görev ve knowledge, language understanding, reasoning, moderation,
  grammar-vocabulary, instruction-following kategorileri bildirir. Instruction-following ve
  judge tabanlı bölümler base-model manipulation check'inin ana kapısı değildir.

### 2.7 Kara-Kumru ve Turkish-SFT

- [Kara-Kumru-v1.0-2B](https://huggingface.co/AlicanKiraz0/Kara-Kumru-v1.0-2B) (**A**) Kumru-2B
  üzerinde Türkçe task fine-tuning modelidir; CPT corpus recipe'i değildir.
- [Turkish-SFT-Dataset-v1.0](https://huggingface.co/datasets/AlicanKiraz0/Turkish-SFT-Dataset-v1.0)
  (**A**) instruction/SFT kanıtıdır; genel unlabeled CPT corpus tablosuna eklenmeyecektir.

### 2.8 Türkçe capability kaynakları

- [TurkishMMLU](https://arxiv.org/abs/2407.12402) (**A**): 10,000'den fazla native Turkish,
  curriculum-expert, multiple-choice soru; dokuz subject. Causal LM için answer-choice likelihood
  puanlaması mümkündür; public benchmark overlap ayrıca taranmalıdır.
- [EXAMS](https://arxiv.org/abs/2011.03080) (**A**): 16 dilde 24,000+ high-school exam sorusu;
  Turkish subset MCQ olarak base-compatible olabilir, fakat çeviri/source overlap denetlenmelidir.
- [TrClaim-19](https://aclanthology.org/2020.conll-1.31/) (**A**): 2,287 Türkçe tweet ve
  check-worthiness/rationale etiketleri. Küçük ikincil classification diagnostic olabilir; native
  LM likelihood ile nasıl ölçüleceği önceden sabitlenmelidir.

## 3. Türkçe dışı karşılaştırmalı kaynaklar

### 3.1 Unseen/low-resource adaptation

[Ebrahimi & Kann — How to Adapt Your Pretrained Multilingual Model to 1600 Languages](https://aclanthology.org/2021.acl-long.351/)
(ACL-IJCNLP 2021, **A**).

- **Source:** XLM-R pretrained multilingual model; target language New Testament bulunan diller,
  çoğu için düşük kaynak ve dar domain.
- **Tokenizer:** XLM-R tokenizer; vocabulary extension yok.
- **Objective/ölçüm:** Continued pretraining dahil birkaç adaptation yöntemi; POS tagging ve NER.
  Makale, basit continued pretraining'in ortalama olarak en iyi yöntem olduğunu ve dar/küçük
  corpusla bile gains görülebildiğini bildirir.
- **Ders:** Önce temiz full-CPT baseline; karmaşık PEFT/tokenizer değişiklikleri sonra.
- **Sınır:** Encoder model, New Testament domain ve token/step/mix değerleri M2-A/M2-B'ye birebir
  aktarılmaz.

### 3.2 Ölçekli cross-lingual CPT

[Breaking Language Barriers: Cross-Lingual Continual Pre-Training at Scale](https://aclanthology.org/2024.emnlp-main.441/)
(EMNLP 2024, **A**).

- **Source/stage:** Çeşitli pretrained multilingual/source modeller üzerinde CPT; paper 40M–5B
  aralığında 40 model-size deneyini özetler.
- **Corpus/mix/recipe:** Target-language data scaling ve joint data-parameter scaling incelenir;
  family-level exact model–corpus–LR–batch–sequence–step kombinasyonu **NR** (source-scoped kayıt
  §8.10); abstract tek bir recipe vermez.
- **Ölçüm:** Target language ve cross-lingual transfer; CPT'nin daha hızlı yakınsadığı ve resource
  savings sağladığı raporlanır.
- **Ders:** Dose ve model scale önceden dondurulmalı; target-language token exposure ayrı raporlanmalı.
- **Sınır:** 1B Turkish factual thesis için abstract'taki average scaling claim'i tek başına
  threshold değildir.

### 3.3 Arabic Stable LM

[Arabic Stable LM: Adapting Stable LM 2 1.6B to Arabic](https://arxiv.org/abs/2412.04277)
(**A**; ilgili [Arabic base card](https://huggingface.co/stabilityai/ar-stablelm-2-base)).

- **Source/stage:** Stable LM 2 1.6B'den Arabic Stable LM 1.6B base ve chat varyantı; base ve chat
  aşamaları ayrı raporlanır.
- **Corpus/tokenizer:** Arabic base card CulturaX dataset kullanımını listeler; paper'daki exact
  token/step/scheduler alanları §8.8'de çıkarılmış, raw bytes ve bazı manifest alanları **NR**.
- **Objective/ölçüm:** Base language adaptation ile chat/instruction tuning ayrılır; chat modelde
  synthetic instruction mixing ayrıca gösterilir.
- **Ders:** StableLM'i Türkçe kısa listede tutmanın kaynaklı gerekçesi var; ancak chat/SFT sonucu
  M2-A/M2-B CPT gate'ine taşınmayacak.

### 3.4 Kazakh continual pretraining

[Sherkala-Chat](https://openreview.net/forum?id=wRcTCcb0H5) ve [paper PDF](https://openreview.net/pdf?id=wRcTCcb0H5)
(COLM 2025, **A**).

- **Source/stage:** Llama-3.1-8B base üzerinde Kazakh continual pretraining; sonra instruction/safety
  alignment.
- **Hedef dil/exposure:** Kazakh; base multilingual fakat dengesiz; Turkish, Russian, English de
  recipe içinde yer alır. Türkçe exposure bu nedenle “unseen” karşılaştırması değildir.
- **Corpus/mix:** Toplam 45.3B token Kazakh/English/Russian/Turkish olarak raporlanır; bir CPT
  ablation'ında Kazakh:Russian+Turkish:English `3:1:3` mix karşılaştırması görülür. Exact
  dedup/filter/source distribution ve checkpoint selection **NR**; LR/sequence alanları §8.9'da
  çıkarılmıştır.
- **Tokenizer:** Kazakh/Russian/Turkish için monolingual BPE tokenizerlar eğitilip Llama tokenizer'a
  extension yapılır.
- **Ders:** Fertility ve language-mix manipulation check zorunludur.
- **Sınır:** 8B ve multilingual multi-target mix; M2-B factual re-exposure ile aynı değildir.

### 3.5 DIPLomA

[DIPLomA](https://aclanthology.org/2025.findings-emnlp.1355/)
(Findings EMNLP 2025, **A**).

- **Source/stage:** Instruction-tuned LLM'in foundational counterpart'ına önce target-language
  CPT + English replay uygulanır; sonra instructed counterpart'ın delta'sı merge edilir.
- **Hedef diller:** Basque ana çalışma; Welsh ve Swahili validation. Türkçe değil; low-resource
  adaptation transferidir.
- **Corpus/mix:** Modest monolingual target data ve English replay; exact token/byte, LR, batch,
  sequence, steps ve checkpoint bilgisi paper tablolarından ayrıca dondurulmalıdır.
- **Ölçüm:** Linguistic proficiency, instruction-following ve safety; multilingual performance
  korunumu raporlanır.
- **Ders:** Base language acquisition ile instruction behavior'ı ayrı aşamalar yap.
- **Kopyalanmayacak fark:** Delta merge ana M2-A/M2-B causal kolunda yok; sonradan alignment
  extension olabilir.

### 3.6 Çok-dilli karşılaştırmalı adaptation: SambaLingo

[SambaLingo: Teaching Large Language Models New Languages](https://aclanthology.org/2024.mrl-1.1/)
(MRL 2024, **A**).

- **Source/stage:** Existing Llama-2 çizgisinden yeni diller öğretme; 9 dil ve 7B/70B ölçekleri.
- **Tokenizer:** Vocabulary extension, adaptation ve DPO gibi faktörleri birlikte inceler.
- **Corpus/ölçüm:** Low-resource language corpusları ve language-specific evaluation; exact source
  model, target exposure, token/byte, mix, LR, batch, sequence length, steps ve checkpoint
  selection paperın ilgili deney tablolarından dondurulmalı.
- **Ders:** Tokenizer extension değerli bir karşılaştırma faktörüdür ancak ana ilk deneyde sabit
  tutulmazsa factual treatment ile karışır. Önce existing tokenizer fertility audit, sonra gerekirse
  tek faktörlü extension.
- **Sınır:** 7B/70B ve multi-language setup; 1B Türkçe pilotuna doğrudan başarı beklentisi taşınmaz.

## 4. Kaynakların M2-A/M2-B'ye çevrilen dersleri

| Ders | M2-A/M2-B karşılığı | Ana causal faktör mü? |
|---|---|---|
| Basit CPT güçlü başlangıçtır | Aynı frozen base + aynı tokenizer + aynı general Turkish corpus | Evet, ortak arm omurgası |
| Replay forgetting'i azaltabilir | A ve B'de seçilirse aynı, önceden dondurulacak English replay | Hayır; iki arm arasında sabit |
| Tokenizer extension bazı dillerde gereklidir | Fertility manipulation check; gerekirse ayrı sonraki ablation | İlk ana gate'te hayır |
| Dil edinimi ile alignment ayrılmalıdır | Base CPT önce; SFT/DPO/merge ayrı extension | Hayır, ana gate dışı |
| Target-language dose ve model scale önemlidir | Token budget, updates, sequence ve dose ladder dondurulur | Evet, fakat B farkı değildir |
| Public benchmark leakage olabilir | Capability/factual corpora overlap audit'i | Kontrol |

## 5. En fazla üç literature-backed recipe family

### R1 — Baseline full CPT + sabit tokenizer + sabit English replay (project preference; freeze pending)

M2-A ve M2-B aynı frozen base'den başlaması, aynı general Turkish corpus, aynı total token/update
budget, aynı tokenizer ve seçilirse aynı küçük English replay kullanması önerilir. M2-B'de matched
neutral rows yerine kontrollü Turkish target-fact rows gelir; ekstra total token verilmez. SFT yoktur.
Bu aile en az confound ile Türkçe capability ve `TR→EN(M2-B) − TR→EN(M2-A)` paired treatment
contrast'ını ölçer; recipe henüz execution contract değildir.

### R2 — Full CPT + tokenizer extension (yalnız diagnostic ablation)

R1 tokenizer fertility ciddi bir maliyet gösterirse, aynı data/dose ile tokenizer extension ayrı
tek faktörlü ablation olarak denenebilir. Extension M2-A ve M2-B'de aynı olmalı; M2-B factual
re-exposure farkının yerine geçmemelidir.

### R3 — CPT sonra ayrı alignment/merge (gelecek extension)

MODA/DIPLomA/SambaLingo çizgisinden, base language adaptation bittikten sonra SFT, DPO veya delta
merge. Bu, “Türkçe öğrenildi mi ve factual knowledge transfer oldu mu?” ana sorusuna cevap vermek
için gerekli değildir; yalnız base sonuçları ve lisans/corpus audit'i tamamlanırsa sonraki çalışma
olarak değerlendirilebilir.

## 6. Günlük çalışma günlüğü

| Alan | Kayıt |
|---|---|
| Tarih/saat | 2026-08-07, Europe/Berlin |
| İş paketi | WP2 literatür matrisi |
| Okunan kaynaklar | Bridging, MODA, VBART, TURNA, Kumru/vngrs cards, CETVEL, TurkBench, Kara-Kumru/SFT, TurkishMMLU, EXAMS, TrClaim-19, 1600 Languages, Breaking Language Barriers, Arabic Stable LM, Sherkala, DIPLomA, SambaLingo |
| Doğrulanan iddialar | CPT/SFT ayrımı; tokenizer/replay rolü; Türkçe benchmark türleri; Kumru/vngrs sayı ayrışması |
| Çelişkiler | Kumru 500GB/300B ile vngrs 84.9GB/25.33B aynı snapshot olarak çözülemedi; VBART paper 135GB ile güncel card da aynı varsayılmadı |
| Üretilen dosya | `documentation/148_CROSS_LINGUAL_LANGUAGE_ADAPTATION_LITERATURE_MATRIX_TR.md` |
| Açık sorular | Exact appendices, corpus revisions, benchmark license/overlap ve threshold freeze |
| Yetki sınırı | HU erişimi yok; training/evaluation yok; büyük indirme yok; artifact silme/taşıma yok |

## 7. Kaynak özeti

Bu belgede kullanılan tüm dış bağlantılar erişim tarihi 2026-08-07 olan birincil makale, model
kartı veya dataset card'dır. Tam URL'ler ilgili madde içinde verilmiştir; ayrıca ana kaynak listesi:

- [Bridging the Bosphorus](https://aclanthology.org/2024.mrl-1.21/)
- [MODA](https://aclanthology.org/2026.sigturk-1.17/)
- [VBART](https://arxiv.org/abs/2403.01308)
- [TURNA](https://aclanthology.org/2024.findings-acl.600/)
- [LlamaTurk](https://aclanthology.org/2024.mrl-1.3/)
- [CulturaX](https://aclanthology.org/2024.lrec-main.377/)
- [CETVEL](https://aclanthology.org/2026.eacl-long.46/)
- [TurkBench](https://arxiv.org/abs/2601.07020)
- [TurkishMMLU](https://arxiv.org/abs/2407.12402)
- [EXAMS](https://arxiv.org/abs/2011.03080)
- [TrClaim-19](https://aclanthology.org/2020.conll-1.31/)
- [How to Adapt Your Pretrained Multilingual Model to 1600 Languages](https://aclanthology.org/2021.acl-long.351/)
- [Breaking Language Barriers](https://aclanthology.org/2024.emnlp-main.441/)
- [Arabic Stable LM](https://arxiv.org/abs/2412.04277)
- [Sherkala-Chat](https://openreview.net/forum?id=wRcTCcb0H5)
- [DIPLomA](https://aclanthology.org/2025.findings-emnlp.1355/)
- [SambaLingo](https://aclanthology.org/2024.mrl-1.1/)

## 8. External validation revision — 2026-08-07

Bu bölüm, bağımsız doğrulama incelemesinin ardından önceki WP2 özetini tamamlar ve onunla
çelişen “exact alanlar daha sonra çıkarılmalı” ifadelerini supersede eder. Sayı veya yöntem
birincil kaynakta yoksa aşağıda açıkça **NR** olarak yazılmıştır. NR, proje için tahmin değildir.
Bu bölüm read-only'dir; hiçbir corpus, model veya execution artifact'i üretilmemiştir.

### 8.1 Standart alan sözlüğü

Her kaynak için aşağıdaki alanlar aynı sırayla tarandı: paper/model; source model ve exact
revision/checkpoint; adaptation stage; target language ve base exposure evidence; corpus,
document count, raw/compressed bytes ve tokenizer-specific token count; epochs/exposure; LID,
quality filtering, exact/near-dedup; tokenizer change; objective/trainable scope; source/target
mix veya replay; LR/optimizer/scheduler/batch/effective tokens/sequence length/steps/epochs;
checkpoint selection; LM metric; target capability; forgetting; factual direction; positive,
negative veya limited finding; M2 lesson; non-copyable difference.

### 8.2 Bridging the Bosphorus — exact recipe extraction

Birincil kaynak: [paper](https://aclanthology.org/2024.mrl-1.21/) ve [PDF, §§3.1–4.1,
Appendix C/F, pp. 2–4, 7–8, 17–18](https://aclanthology.org/2024.mrl-1.21.pdf), erişim
2026-08-07.

- **Paper/model, source, stage:** Mistral-7B ve GPT2-xl English-pretrained source modelleriyle
  Turkish adaptation; ayrıca Hamza adlı Turkish from-scratch model ve instruction-tuned türevler
  ayrı deneylerdir. Adaptation branch'i Turkish CPT + LoRA'dır; from-scratch Hamza bu recipe ile
  birleştirilmemelidir.
- **Exact revision/checkpoint:** Reviewed §§3.1–3.2, Table 2, Appendix C/F içinde Hugging Face
  revision hash veya seçilmiş checkpoint ID **NR**. Makale düzeyinde model adları raporlanır,
  immutable revision raporlanmaz.
- **Target exposure/corpus:** Turkish adaptation için CulturaX dose ladder Table 2'de yaklaşık
  **0.05B, 0.13B, 0.25B, 0.5B, 1.1B ve 2.5B Turkish tokens** olarak verilir. Turkish CulturaX
  mC4 + OSCAR kaynaklarından gelir; paper'daki Türkçe büyük-corpus özetinde yaklaşık 94.2M
  document ve 129.5B token raporlanır. Hamza from-scratch için 128 parquet × yaklaşık 1.4 GB
  (yaklaşık 179.2 GB dataset storage) ve 129,486,207,634 training token raporlanır; raw
  uncompressed byte sayısı **NR**. Bu sayılar mevcut `trwiki-20260601` ile eşlenemez.
- **LID/quality/dedup:** Upstream CulturaX/mC4/OSCAR cleaning pipeline'larına atıf vardır;
  reviewed adaptation recipe içinde Turkish sample-level LID, exact dedup, near-dedup, PII veya
  benchmark-contamination manifesti **NR**.
- **Tokenizer:** Adaptation branch'i mevcut source tokenizer ile çalışır; Turkish-specific
  tokenizer extension adaptation faktörü olarak raporlanmaz. Hamza from-scratch tokenizer
  ayrıntıları adaptation branch'ine kopyalanamaz; exact tokenizer revision/vocabulary field'i
  bu extraction için **NR**.
- **Objective/trainable scope:** CPT/causal LM objective; LoRA only. **LoRA r=32, alpha=32,
  dropout=0.05**, yalnız projection layers trainable; original model weights frozen.
- **Mix/replay:** Adaptation dose Turkish-only segments olarak tarif edilir; English replay veya
  source-language mixing için raporlanan oran **0%/none in the reported adaptation method**.
  Bu, English retention kaybının yorumlanması açısından önemlidir.
- **Hyperparameters:** AdamW; cosine scheduler; learning rate **1e-4**; batch size **1**;
  gradient accumulation yok. Exact AdamW betas/epsilon, effective token batch, sequence length,
  total optimization steps, epoch equivalence ve checkpoint selection **NR** in reviewed
  §§3.1–3.2/Appendix F. Dose token counts yukarıdaki gibi raporlanmıştır.
- **Metrics/capability:** Cross-tokenizer PPL/NLL karşılaştırmasının yanıltıcı olduğu gerekçesiyle
  **BPC** kullanılır; `trnews-64` test seti **5,000 sample** içerir. ARC-TR, TruthfulQA-TR ve
  GSM8K-TR Turkish capability sonuçları raporlanır; bunlar saf grammar/language-acquisition
  testi değil, knowledge/reasoning/capability karışımıdır.
- **Forgetting/factual direction:** Turkish LM/capability artarken English validation loss ve
  source-language ability düşer; conclusion, LoRA altında da catastrophic forgetting görüldüğünü
  ve ileride English mixing denenmesi gerektiğini belirtir. TR→EN factual access için bu paper'da
  M2-A/M2-B matched fact replacement estimand'i yok; **factual direction NR/not studied**.
- **Finding and M2 lesson:** Dose ladder, BPC ve explicit EN retention birlikte alınmalıdır.
  Kopyalanabilir ders, “Türkçe dose + source retention” ayrımıdır; LoRA, projection-only scope,
  Mistral/GPT2 model ölçeği, mixed benchmark seti ve from-scratch Hamza koşulları yeni 1B
  sibling-arm causal kontrata kopyalanmayacaktır.

### 8.3 MODA — exact recipe extraction

Birincil kaynak: [MODA paper](https://aclanthology.org/2026.sigturk-1.17/) ve [PDF, §§3.1–3.2,
pp. 2–4; Tables 1–3, pp. 6–7](https://aclanthology.org/2026.sigturk-1.17.pdf), erişim
2026-08-07.

- **Paper/model/stage:** Qwen2.5-7B base → Turkish causal CPT → PEFT/SFT → model merge.
  CPT-only sonuç ile instruction/merge sonucu ayrıdır.
- **Revision/exposure:** Exact Qwen revision/checkpoint ID **NR** in reviewed paper §§3.1–3.2;
  base'ın Turkish exposure'ı da **NR**, bu nedenle “Turkish unseen” denemez.
- **Corpus/bytes/tokens:** `vngrs-web-corpus`; 50.3M pages ve **25.33B VBART tokens** paperda
  raporlanır; raw/compressed file bytes ve exact dataset snapshot **NR**. Corpus source history
  cleaned OSCAR-2201 + mC4 ile ilişkilendirilir.
- **Quality/LID/dedup:** Rule-based heuristics; semantic filtering yok. Extra LID methodu
  raporlanmamış; CPT için MinHash near-dedup raporlanmamış. SFT aşamasında web/institutional
  data ve proprietary GPT-5-mini synthetic yaklaşık 80K sample; SFT'de MinHash near-dedup var,
  ek automatic filters ve large-scale manual inspection yok.
- **Tokenizer/objective/trainable scope:** CPT tokenizer extension/change raporlanmıyor;
  causal LM, sequence length **1024**, token packing. CPT full model trainable olduğu raporlanır;
  SFT LoRA: r=64, alpha=128, dropout=.05, q/k/v/o ve MLP gate/up/down projections, bias yok,
  base frozen.
- **Mix/replay/hyperparameters:** CPT target Turkish web only olarak raporlanır; source replay
  oranı **NR/none specified in reviewed §§3.1–3.2**. Fused AdamW, LR **2e-5**, weight decay
  **.01**, linear warmup **3% of total steps**, 3 epochs ve yaklaşık **93,750 optimization
  steps**. AdamW betas/epsilon, effective token batch ve exact checkpoint selection **NR**.
- **Capability/forgetting/factual:** TurkishMMLU, Turkish EXAMS ve TRCLAIM-19; CPT-only
  sometimes underperforms or matches instruction baseline, while combined CPT+SFT+merge helps
  task benchmarks. These are knowledge/school/reasoning/task benchmarks, not pure Turkish
  acquisition. English retention and TR→EN factual direction **NR/not studied as M2 sibling
  contrast**.
- **M2 lesson/non-copyable difference:** Keep CPT separate from SFT/merge and audit vngrs
  provenance. Qwen2.5-7B, 25.33B web dose, SFT synthetic data, LoRA and merge cannot be copied
  into the 1B full-CPT M2-A/M2-B causal estimand.

### 8.4 VBART — exact recipe extraction

Birincil kaynak: [paper](https://arxiv.org/abs/2403.01308) ve [PDF, §§3.1–3.6,
pp. 1–3, 5–6](https://arxiv.org/pdf/2403.01308), erişim 2026-08-07.

- **Paper/model/stage:** VBART-Large (387.6M) ve VBART-XLarge (740M), Turkish sequence-to-
  sequence BART/mBART-style models trained from scratch; decoder-only causal CPT değildir.
  XLarge, Large weights'inden genişletilerek ayrıca pretrain edilir.
- **Revision/checkpoint/exposure:** Exact release revision/checkpoint ID **NR** in reviewed
  paper. From-scratch model olduğu için source Turkish exposure applicable değildir.
- **Corpus/bytes/tokens:** Turkish OSCAR-2201 + mC4; cleaned corpus **50.3M pages, 135.7 GB
  on disk, 25.33B subword tokens**. Paper ayrıca Large'ın **708B token**, XLarge'ın **84B token**
  exposure'ını raporlar; raw/uncompressed bytes **NR**.
- **LID/quality/dedup:** Chain of rules/heuristics cleaning, ancak exact LID, exact/near-dedup,
  PII veya benchmark contamination manifesti paperda **NR**.
- **Tokenizer/objective:** SentencePiece Unigram tokenizer, 10 GB OSCAR/OPUS/Wikipedia sample;
  vocab **32,000**. Sentence permutation + span masking, 30% tokens masked, Poisson λ=3.5;
  no tokenizer change after tokenizer training.
- **Hyperparameters:** 8×A100-80GB, 2.7M steps, batch 256, context 1024 (encoder 800 during
  pretraining), Adam β1=.9, β2=.98, ε=1e-6, 20k warmup scheduler; dropout .1 for first 2.33M,
  .05 for next 165K, 0 for final 205K. Effective token batch and exact checkpoint selection
  **NR**.
- **Capability/forgetting/factual:** Summarization, title generation, paraphrase, question
  generation/answering; tokenizer fertility/efficiency. English retention and TR→EN factual
  access **NR/not studied**.
- **Lesson/difference:** Turkish tokenizer fertility must be measured, but encoder-decoder
  from-scratch objective and downstream generation scores are not evidence for the M2-A/M2-B
  decoder-only factual estimand.

### 8.5 TURNA — exact recipe extraction

Birincil kaynak: [paper](https://aclanthology.org/2024.findings-acl.600/) ve [PDF, §§3–5,
pp. 2–5, Appendix A](https://aclanthology.org/2024.findings-acl.600.pdf), erişim 2026-08-07.

- **Paper/model/stage:** TURNA Large36L, 1.1B Turkish encoder-decoder UL2 model; from-scratch
  monolingual pretraining, not decoder-only CPT. Exact released checkpoint revision **NR**.
- **Corpus/exposure:** Web, DergiPark scientific, YÖKTez, books, Bilkent creative writings and
  ParlaMintTR. Table 1: 50,336,214 web docs/25.33B tokens; DergiPark 1.78B; YÖKTez 15.24B;
  books .61B; creative .01B; ParlaMint .07B. Total pretraining exposure **42.7B tokens**;
  raw/compressed bytes **NR**.
- **Quality/LID/dedup:** Scientific PDF extraction uses Apache Tika, line/document filtering;
  book and creative-text heuristics; ParlaMint no special cleaning. Exact LID, exact/near-dedup,
  PII and benchmark-contamination manifest **NR** in §§3.1–3.5/Appendix A.
- **Tokenizer/objective:** SentencePiece Unigram trained on 10 GB OSCAR/OPUS/2021-09-17
  Wikipedia sample; vocab 32,000 + 128 sentinel tokens = 32,128. UL2 MoD: R/S/X denoising
  40%/20%/40%; no source replay because from scratch.
- **Hyperparameters:** 1.74M steps, batch 48, source/target seq length 512, single TPU v3-8;
  dropout off in pretraining. Pretraining optimizer/LR/scheduler and exact checkpoint-selection
  criterion **NR** in reviewed implementation section; fine-tuning uses Adafactor LR 1e-3 for
  TURNA/mT5 without scheduler, which is not the pretraining recipe.
- **Capability/forgetting/factual:** Three generation + five understanding tasks across 13
  datasets; no English retention, target-language forgetting or TR→EN factual direction.
- **Lesson/difference:** Diverse-domain Turkish coverage and language diagnostics are useful;
  UL2, encoder-decoder, from-scratch and 42.7B-token exposure are not copyable to M2-A/M2-B.

### 8.6 LlamaTurk — newly added required extraction

Birincil kaynak: [ACL page](https://aclanthology.org/2024.mrl-1.3/) ve [PDF, §§3.1–3.5,
pp. 2–4; §§4–7, pp. 4–8](https://aclanthology.org/2024.mrl-1.3.pdf), erişim 2026-08-07.

- **Paper/model/source:** *Adapting Open-Source Generative LLMs for Low-Resource Languages: A
  Case Study for Turkish*; Llama-7B (`huggyllama/llama-7b`) English-dominant source and MaLA
  multilingual comparison. Main continual-training arm is **LlamaTurk-7b-c**; instruction,
  task-specific and vocabulary-extension arms are separate.
- **Revision/exposure:** Exact source checkpoint revision **NR** in §§3.1–3.5; source model's
  exact Turkish pretraining share **NR**, so unseen is not claimed.
- **Corpus/bytes/tokens:** Raw Turkish Wikipedia dump from November 2023, **534,988 articles**;
  Table 1 reports **273.9M tokens** for continual training. Raw/compressed bytes, document byte
  manifest and exact dump hash **NR**.
- **LID/quality/dedup:** “Raw Wikipedia” is used; exact LID, quality filters, exact/near-dedup,
  PII and benchmark contamination **NR** in §3.1.
- **Tokenizer:** Continual-training arm keeps the Llama tokenizer. Separate vocabulary-extension
  arm uses a Turkish BPE tokenizer with **28,600 tokens**; merge yields **59,773 vocabulary**,
  **827 overlaps**, and about **228M new embedding parameters**. This is not the main CPT arm.
- **Objective/trainable scope:** Continual training is raw-text LM. Due to compute budget, only
  Llama-7B is run with 8-bit quantization and LoRA; **R=8, alpha=16, dropout=.05**. The paper
  does not provide a pretraining optimizer name, so optimizer **NR**.
- **Hyperparameters:** Sequence length **512**, batch **128 instances**, gradient accumulation
  **32**, 100 linear warmup steps, LR **3e-4**, one epoch; ~206 hours on four RTX A4000 for the
  reported setup. Effective token batch, exact optimizer/scheduler beyond linear warmup, and
  checkpoint selection **NR**.
- **Instruction/task data:** Separate translated Alpaca 52K instruction data and 5K sentiment
  task data; do not put them in unlabeled M2 corpus. Table 1 also reports 13.3M and 1.3M tokens
  for those stages.
- **Capability/forgetting/factual:** Continual training reduces PPL on evaluated xquad/dbricks
  sets; vocabulary extension has poor PPL/downstream results at this small dose; task-specific
  tuning can hurt PPL. No English retention or TR→EN factual direction.
- **M2 lesson/difference:** Wikipedia-only CPT can improve PPL but is narrow; fertility and
  tokenizer extension must be separate. LoRA/8-bit, Llama-7B, 273.9M-token Wikipedia and SFT
  combinations are not the proposed 1B full-CPT sibling design.

### 8.7 Ebrahimi & Kann — 1600-language adaptation

Birincil kaynak: [paper](https://aclanthology.org/2021.acl-long.351/) ve [PDF, §§2–4,
pp. 1–5](https://aclanthology.org/2021.acl-long.351.pdf), erişim 2026-08-07.

- **Source/stage:** XLM-R base; 30 evaluation languages are unseen in XLM-R's pretraining
  vocabulary/coverage claim in the paper's setup. Target data is New Testament; roughly 8,000
  verses total and average approximately 402K subword tokens per language; JHUBC 1611-language
  coverage is a separate source.
- **Corpus/bytes/tokenizer:** New Testament and JHUBC; raw/compressed bytes, exact document
  manifest and exact tokenizer-specific token counts beyond reported averages **NR**. XLM-R
  tokenizer is retained for the main methods; vocabulary extension is a separate method.
- **Methods/trainable scope:** Continued MLM, TLM and M|TLM; vocabulary extension with target
  SentencePiece max 30K, duplicate removal, random new embeddings; MAD-X language/invertible/task
  adapters. MLM/TLM 40 epochs, mixed 20; POS 80/40; final task fine-tuning 5 epochs, batch 32,
  LR 2e-5; adapter LR 1e-4; sequence length 256. Exact optimizer, warmup/scheduler, effective
  tokens and checkpoint hash **NR**.
- **Filtering/dedup/mix:** Exact/near-dedup and LID details **NR**; mixed objectives are not an
  English replay protocol. Checkpoint/epoch search chooses from {10,20,40,80} by average
  development performance across languages.
- **Capability/forgetting/factual:** POS and NER with English labeled data transferred; no LM
  PPL, English retention curve or factual direction. Main lesson is a clean full-CPT baseline
  before complex PEFT, but New Testament domain and encoder task setup are not copyable.

### 8.8 Arabic Stable LM — exact recipe extraction

Birincil kaynak: [paper](https://arxiv.org/abs/2412.04277) ve [PDF, §§3–6, pp. 2–8](https://arxiv.org/pdf/2412.04277),
erişim 2026-08-07.

- **Source/stage:** Stable LM 2 1.6B multilingual checkpoint → Arabic Stable LM 1.6B base;
  separate synthetic-data instruction-tuned chat model. Base model's listed languages include
  English, German, French, Italian, Dutch, Spanish and Portuguese; Arabic source exposure before
  adaptation is limited, not proven zero.
- **Corpus/bytes/tokens:** English 619B and Arabic 115B StableLM-token sampling totals, 84%/16%
  token share and 18%/82% sampling share; Arabic before/after cleaning: CulturaX 158.1B→114.1B
  tokens, 74.0M→49.9M docs; SANAD 145.1M→140.7M, 134.5K→128.7K; E-Book 280.3M→171.0M,
  1.7K→1.4K. Raw/compressed bytes **NR**.
- **Filtering/LID/dedup:** Safety, ads, line, character, Gopher and document cleaning are
  reported; Arabic Unicode remapping is applied. CulturaX is described as deduplicated in the
  fertility setup, but an exact/near-dedup manifest, benchmark overlap, PII and sample-level LID
  details are **NR** in §§3.2–3.3.
- **Tokenizer/objective:** StableLM Arcade100k tokenizer retained; fertility is explicitly
  measured. No vocabulary change is reported. Base fine-tuning is causal LM; full trainable scope
  is implied by “fine-tune checkpoint”, but trainable-parameter mask **NR**.
- **Hyperparameters:** 500K steps, 10K warmup, cosine + inverse-square-root to 300K then linear
  cooldown for 200K; max LR 5e-4, min LR 2.5e-6; two nodes × eight H100, micro-batch 6/GPU,
  global batch 96 sequences / ~400K tokens, ~197B total tokens. Optimizer is inherited from
  StableLM-2 original paper; exact name/betas and checkpoint selection **NR** in this reviewed
  paper.
- **Capability/forgetting/factual:** ArabicMMLU/CIDAR/ACVA and related Arabic benchmarks; cloze
  format is preferred over multiple-choice letters. Synthetic Qwen2-7B-Instruct rephrasing creates
  ~183K filtered conversations for chat. No English retention curve or cross-lingual factual
  direction.
- **M2 lesson/difference:** Separate base/chat, fertility and cloze likelihood are useful; Arabic
  734B mix, H100 scale, synthetic chat data and inherited scheduler cannot be copied into the
  Turkish base-CPT causal gate.

### 8.9 Sherkala-Chat — exact recipe extraction

Birincil kaynak: [COLM/OpenReview record](https://openreview.net/forum?id=wRcTCcb0H5) ve
[official arXiv PDF, §§2.1–3.3, pp. 2–5](https://arxiv.org/pdf/2503.01493), erişim 2026-08-07.

- **Source/stage:** Llama-3.1-8B base → Sherkala continual pretraining → multilingual instruction
  tuning/safety alignment. Exact base revision and selected CPT checkpoint **NR** in reviewed
  paper.
- **Corpus/exposure:** 45.3B CPT tokens: **19.45B Kazakh, 19.45B English, 6.4B Russian and
  Turkish**. Corpus byte size, exact file manifest and exact source-language LID/dedup counts
  **NR**.
- **Tokenizer/quality:** Separate Kazakh, Russian and Turkish BPE tokenizers; non-overlapping
  frequent tokens added; vocab 128,256→159,766 (+25%). Turkish fertility 2.23→1.82. Quality
  filtering/cleaning is described broadly, but exact/near-dedup, PII and benchmark overlap
  manifest **NR**.
- **Objective/hyperparameters:** Full parameter CPT; AdamW, LR 1.5e-4, global batch 4M tokens,
  warmup 1%/110 steps, β1=.9, β2=.95, ε=1e-5, weight decay .1, grad clip 1.0, 10× cosine decay
  to step 11,433. The 3:1:3 Kazakh:(Russian+Turkish):English mixture is an ablation result,
  not a Turkish-only recipe. Exact epochs and checkpoint selection **NR**.
- **Capability/forgetting/factual:** Kazakh/Russian/English MMLU, reasoning, knowledge and
  misinformation; generation and safety. English/Russian competitiveness is reported, but no
  Turkish factual direction. Added Russian/Turkish reduced Kazakh in one ablation; 3:1:3 with
  English was best overall.
- **M2 lesson/difference:** Tokenizer fertility and replay/mix must be measured. 8B, 45.3B-token
  multilingual mixture, vocabulary expansion and instruction tuning are not the 1B Turkish
  sibling-arm causal treatment.

### 8.10 Breaking Language Barriers — scale/replay evidence

Birincil kaynak: [EMNLP paper](https://aclanthology.org/2024.emnlp-main.441/) ve [PDF,
§§2.2–5.2, pp. 2–8](https://aclanthology.org/2024.emnlp-main.441.pdf), erişim 2026-08-07.

- **Source/stage:** Scratch pretraining scaling and cross-lingual CPT across multiple model sizes;
  paper studies 40 model-size conditions (40M–5B range), not one Turkish model. Exact model,
  checkpoint revision, tokenizer and per-run corpus row must therefore be read per experiment;
  one universal source recipe is **NR**.
- **Corpus/mix/hyperparameters:** Target-language scaling and source-language replay are varied;
  paper's replay ablation includes English ratios 1%, 5%, 10%, 20%, 50% and 80%. Exact per-run
  bytes, token counts, LID/dedup, optimizer/LR/batch/sequence/steps/checkpoint selection **NR**
  at the family level in the reviewed sections.
- **Metric/finding:** Held-out cross-entropy and multilingual zero-shot benchmarks; CPT reaches
  lower loss faster and saves about 25–50% FLOPs. Without replay English validation loss example
  rises from 2.40 to 3.68; replay changes early-stage forgetting, while same-compute convergence
  can meet similar loss. No Turkish-specific factual direction.
- **M2 lesson/difference:** Replay is a retention regularizer, not the M2-B treatment. Any chosen
  replay fraction must be fixed before results and identical in A/B; paper-scale curves do not
  freeze a Turkish contract.

### 8.11 DIPLomA — replay and alignment separation

Birincil kaynak: [paper](https://aclanthology.org/2025.findings-emnlp.1355/) ve [PDF,
§§3–4, Appendix C/D, pp. 7–12](https://aclanthology.org/anthology-files/anthology-files/pdf/findings/2025.findings-emnlp.1355.pdf),
erişim 2026-08-07.

- **Source/stage:** Llama-3.1 foundational/instruction counterpart; target CPT for Basque, with
  Welsh and Swahili validation, then separate SFT/alignment/delta merge. Exact revision/checkpoint
  **NR** in reviewed source.
- **Corpus/mix:** Table 6 reports Basque 531M train/5M validation words, Welsh 389M/4M and
  Swahili 490M/5M. CPT uses **80:20 target:English replay**; tokenizer-specific token count,
  raw/compressed bytes and exact dedup/LID/PII/benchmark-overlap manifest **NR**.
- **Recipe:** CPT 4 epochs, sequence length 4096, effective batch 2M tokens, HF Transformers /
  DeepSpeed ZeRO / Accelerate on 8×A100-80GB. CPT optimizer/LR/scheduler follows Corral et al.
  and is **NR** in the reviewed appendix; SFT has its own 4096 sequence, effective batch 256,
  LR 7e-6 and early stopping on 100 NoRobotsEU examples.
- **Capability/forgetting/factual:** Linguistic proficiency, instruction following and safety;
  mixed pretraining mitigates English forgetting and target-only variant forgets more. No Turkish
  factual direction. Delta merge is not part of the base language acquisition estimand.
- **M2 lesson/difference:** Source replay can be a retention regularizer; SFT/delta merge must
  remain separate. 80:20 is literature evidence, not a frozen M2 ratio.

### 8.12 SambaLingo — exact recipe extraction

Birincil kaynak: [paper](https://aclanthology.org/2024.mrl-1.1/) ve [PDF, §§3–5, Appendix A/E,
pp. 2–6, 11, 18–19](https://aclanthology.org/2024.mrl-1.1.pdf), erişim 2026-08-07.

- **Source/stage:** Llama-2 7B for nine target languages including Turkish; Llama-2 70B only
  for Arabic, Thai and Hungarian. Continual adaptation, then optional SFT+DPO chat alignment;
  exact source revision/checkpoint **NR**.
- **Corpus/exposure:** CulturaX target and English web data; per-language raw/compressed bytes,
  document counts and tokenizer-specific target token exposure **NR** in reviewed paper. CPT mix
  is **1:3 English:target**, biased toward target language.
- **Tokenizer/change:** Add non-overlapping target tokens initialized from original subword
  embeddings; chose **25,000 added tokens** for all languages. Turkish fertility falls from 3.28
  (0 added) to 1.77 (25K); Table 3 also reports the 1K/4K ladder. No exact target LID, quality,
  exact/near-dedup, PII or benchmark-overlap manifest.
- **Objective/trainable scope/hyperparameters:** Full parameter CPT; max 4 epochs, LR 1e-4 with
  cosine decay, warm-up ratio .01, weight decay .1. Exact optimizer name, beta values, sequence
  length, effective token batch, total steps and checkpoint selection **NR** in Appendix A.
  SFT: global batch 512, max seq 2048, LR 2e-5, 10% warmup; DPO: global batch 32, 3 epochs,
  LR 5e-7, 10% warmup, β=.1.
- **Capability/forgetting/factual:** PPL on holdout, FLORES, SIB-200, Belebele, XNLI and related
  cross-lingual tasks; Turkish qualitative chat judged by GPT-4/Claude. No English retention
  curve isolated for the Turkish base CPT and no TR→EN factual direction.
- **Finding/difference:** Vocabulary extension reduces fertility and can improve throughput, but
  an ablation found no significant downstream accuracy impact. This supports separate fertility
  diagnostics, not automatic tokenizer extension in M2-A/B.

## 9. Revize edilmiş M2 consequence ve açık NR listesi

1. **Source claim:** Bridging supports an explicit dose ladder, exact LoRA recipe and BPC/English
   forgetting; LlamaTurk supports narrow Wikipedia CPT and reports negative small-dose vocabulary
   extension; MODA separates CPT from SFT/merge; DIPLomA and Breaking support replay as a retention
   regularizer; SambaLingo and Sherkala support fertility/tokenizer ablations.
2. **Project inference:** The new study should start with identical sibling arms, base-compatible
   Turkish LM/capability measures, English retention, and TR→EN as the primary factual outcome.
3. **Not frozen:** Full CPT preference, exact English replay ratio, model choice, corpus revision,
   tokenizer extension, checkpoint rule, benchmark subset and numeric thresholds remain contract
   decisions. They must not be selected after observing M2-A/M2-B results.
4. **Remaining primary-source NR fields:** Per-paper immutable revision hashes, raw uncompressed
   bytes, sample-level LID, exact/near-dedup, PII, benchmark contamination and complete
   checkpoint-selection metadata are absent in at least one reviewed source. This is now recorded
   explicitly rather than deferred as an extraction task.

## 10. External validation changelog

- **2026-08-07:** Added this append-only validation section; corrected Bridging model/dose/LoRA/
  optimizer/BPC details; added the previously missing LlamaTurk paper; expanded MODA, VBART,
  TURNA, Arabic Stable LM, Sherkala, Breaking Language Barriers, DIPLomA and SambaLingo to the
  common extraction schema; replaced ambiguous “not yet extracted” language with source-scoped
  NR; preserved the earlier literature synthesis and all historical project results.
