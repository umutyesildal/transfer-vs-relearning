# 150 — Türkçe Capability ve Adaptation Manipulation-Check Planı

**Tarih:** 2026-08-07 (Europe/Berlin)  
**Durum:** WP4 external-validation revision; proposed/preselected measurement architecture; freeze pending  
**Kapsam:** M0→M1→M2-A/M2-B state'leri için Türkçe capability, PPL, tokenizer fertility,
retention ve factual yön ölçümleri. Bu belge evaluator implementasyonu, broad evaluation
submission veya training izni değildir.

## 1. Ana ilke ve state zinciri

TR→EN factual artışı tek başına “Türkçe adaptation çalıştı” kanıtı değildir. Aynı measurement
package her state'e uygulanmalıdır:

```text
M0: frozen pretrained base
  ↓ English factual M1 acquisition
M1: selected English factual checkpoint
  ├── M2-A: general Turkish CPT, target facts yok
  └── M2-B: aynı Turkish CPT + matched Turkish target-fact re-exposure
```

Eski Qwen pilotunda M1, M2-clean ve M3-fact için mevcut yönler korunur; yeni literatür-first
çalışmada isimler M2-A/M2-B sibling-arm standardına çevrilir. M2-B'ye ekstra total token/update
verilmez; factual rows eşleşen neutral Turkish rows'un yerine geçer.

## 2. Ölçüm katmanları

### 2.1 Tokenizer fertility: maliyet ve erişilebilirlik tanısı

Aynı küçük, preselected Turkish+English sample (exact IDs/hash freeze pending) her modelin kendi
tokenizer'ıyla ölçülür:

- token/document;
- token/word;
- character/token;
- Turkish/English fertility ratio;
- agglutinative/morphologically long word parçalanma örnekleri;
- byte-fallback, unknown/special-token ve whitespace davranışı;
- projected tokens per dose, update ve sequence.

Fertility bir model kalite skoru değildir. Farklı tokenizer kullanan modellerin raw PPL veya raw
token count'u doğrudan rank-ordering için karşılaştırılmayacaktır. Aynı modelde pre/post delta,
aynı tokenizerla raporlanır.

### 2.2 Held-out PPL ve source retention

İki text split gerekir; exact contents ve hashes freeze pending'dir:

1. **Turkish held-out split:** Training corpus, contamination inventory, capability benchmark ve
   factual target rows dışında; source/domain ve length strata'sı manifestte korunmuş.
2. **English retention split:** M1 general-language/PPL protocol'üyle aynı hash ve evaluation
   chain; training/factual rows dışında.

Her M0, M1, M2-A, M2-B state'inde:

- token-level NLL ve PPL;
- document-level PPL dağılımı;
- Turkish pre/post delta;
- English PPL delta ve M1 EN→EN factual retention;
- source/domain stratified confidence interval

raporlanır. Uncertainty için document-level bootstrap veya predeclared paired resampling
kullanılır. Threshold sonuç görüldükten sonra seçilmez.

### 2.3 BPC / bits-per-byte: cross-model LM karşılaştırması

Raw PPL yalnızca aynı model ailesi ve aynı tokenizer zinciri içinde güvenli bir within-model
karşılaştırmadır. Farklı tokenizer/model ailelerinde Turkish LM karşılaştırması için primary
normalized metric **BPC (bits per character)** veya önceden seçilmiş tek bir UTF-8 **bits-per-byte**
ölçüsüdür. Bridging'in Appendix F yaklaşımı BPC kullanır; `trnews-64` test seti 5,000 örnektir.

- Aynı state/model/tokenizer zincirinde PPL ve PPL delta korunur.
- Modeller arasında Turkish held-out NLL, BPC; byte-normalized raporlama seçilirse UTF-8
  encoding ve byte boundary kuralı sabitlenerek bits-per-byte verilir.
- PPL, BPC ve bits-per-byte birbirinin yerine sonuçtan sonra seçilmeyecek; contract tek primary
  normalize metric ve tek secondary metric'i belirleyecektir.
- Tokenizer fertility ayrı bir maliyet/erişilebilirlik tanısıdır; fertility'i BPC ile birleştirip
  tek kalite skoru üretmek yoktur.

Bu düzeltme, farklı Turkish tokenizer kullanan model adaylarının raw PPL ile sıralanması riskini
kapatır; Turkish capability sonucu için LM katmanı artık “within-model PPL + cross-model BPC /
bits-per-byte” olarak raporlanacaktır.

### 2.4 Base-compatible Turkish capability

Ana manipulation check mümkünse instruction-following gerektirmeyen likelihood/MCQ/cloze
ölçümlerinden oluşur. Generation-only, judge-based veya chat benchmark ana kapı değildir.

| Kaynak | Kaynaklı kapsam | Önerilen kullanım | Ana risk |
|---|---|---|---|
| [TurBLiMP](https://arxiv.org/abs/2506.13487) | Turkish linguistic minimal-pair / grammar diagnostic. **A** | **Primary independent linguistic diagnostic candidate**, likelihood-based; yalnız exact release/license, contamination ve floor/ceiling audit'i geçerse. | Exact release/item revision, license, overlap ve small-model floor/ceiling. |
| [CETVEL](https://aclanthology.org/2026.eacl-long.46/) / [TurkBench](https://arxiv.org/abs/2601.07020) | Grammar, language understanding, knowledge, reasoning ve instruction karışımı. **A** | Yalnız base-compatible morphology/grammar/MCQ alt seti; TurBLiMP release'i kullanılamazsa secondary/robustness diagnostic. | Instruction/chat/generative/judge bölümleri causal LM ana gate'ine uygun değil. |
| [TurkishMMLU](https://arxiv.org/abs/2407.12402) | 10,000+ native Turkish, curriculum-expert MCQ; 9 subject. **A** | **Balanced likelihood subset**, broad Turkish knowledge capability. | Public overlap, subject floor/ceiling, prompt/choice formatting. Pure language acquisition değildir; okul bilgisi, reasoning ve kültürel bilgiyi ölçer. |
| [EXAMS](https://arxiv.org/abs/2011.03080) | 24,000+ high-school exam sorusu, 16 dil; Turkish subset. **A** | Turkish MCQ likelihood secondary/broader capability. | Translation/source provenance, contamination, multilingual format. Pure language acquisition değildir; school knowledge/reasoning ölçer. |
| [TrClaim-19](https://aclanthology.org/2020.conll-1.31/) | 2,287 Türkçe tweet; check-worthy labels/rationales. **A** | Optional small classification diagnostic; main gate değil. | Topic leakage, low sample variance, classification confound. |

TurkishMMLU ve EXAMS bu nedenle “Türkçe öğrenme”nin saf ölçüsü olarak değil, **geniş Turkish
knowledge/school/reasoning/cultural capability** olarak etiketlenecektir. Turkish LM/BPC ve
TurBLiMP grammar diagnostic ayrı tutulacaktır.

## 3. Ön-seçimli capability paketi (freeze pending)

Final benchmark revision/license/overlap audit'i tamamlanmadan sample materialize edilmeyecek;
ancak ölçüm mantığı şu sırada ön-seçilmiştir:

1. **Primary LM manipulation check:** Aynı modelde Turkish held-out PPL delta; model aileleri
   arasında BPC/bits-per-byte ile normalize edilmiş Turkish LM sonucu.
2. **Primary independent linguistic diagnostic candidate:** TurBLiMP; ancak exact release,
   license, item IDs/revision, overlap ve floor/ceiling audit'i geçerse.
3. **Optional base-compatible grammar alternative:** CETVEL/TurkBench içinden morphology/grammar
   alt seti; yalnız exact release ve base-compatible scoring geçerse TurBLiMP'ye alternatif.
4. **Broader capability:** TurkishMMLU balanced likelihood subset; Turkish school knowledge,
   reasoning ve cultural content olarak etiketlenir.
5. **Broader secondary capability:** EXAMS Turkish MCQ likelihood subset; school/reasoning olarak
   etiketlenir.
6. **Optional task diagnostic:** TrClaim-19; ana language-acquisition gate değil.
7. **Broad context only:** CETVEL/TurkBench'in generative/instruction/chat bölümleri sonuç raporunda
   auxiliary olabilir, manipulation-check kapısını açmaz.

Bu paket selection protocol'ünü sabitler; exact item IDs, split hashes, prompt template, answer
choice ordering, license ve contamination report sonraki bounded measurement contract'ında
dondurulmalıdır. Aynı item set M0/M1/M2-A/M2-B'ye uygulanır.

## 4. Capability scoring

### 4.1 MCQ/likelihood

- Her seçenek aynı prompt prefix ve aynı answer boundary ile tokenize edilir.
- Seçenek log-likelihood length normalization ile ve normalization'sız raporlanır.
- Accuracy primary, mean normalized log-prob secondary.
- Prompt order, answer labels, Turkish diacritics ve whitespace exact freeze edilir.
- Instruction template veya chain-of-thought eklenmez.

### 4.2 Cloze/minimal pair

- Correct/incorrect completion aynı context ve same-length control ile paired scored edilir.
- Morphological minimal pair varsa lexical frequency ve sentence length strata'ları raporlanır.
- Generation sampling, temperature veya judge kullanılmaz.

### 4.3 Classification diagnostic

TrClaim-19 gibi task'larda label verbalization kullanılırsa label tokens ve prompt formatı önce
frozen edilir. Bu skor Turkish fluency ile factual knowledge'ı aynı şey saymaz; yalnız destekleyici
diagnostic olur.

## 5. Factual yönler ve kontrol matrisi

| Yön | Rol | Ölçüm |
|---|---|---|
| EN→EN | M1 storage/source retention guardrail | M2-A ve M2-B'nin M1'e göre retention; factual re-exposure'ın English knowledge'ı bozup bozmadığı |
| TR→EN | **Primary causal outcome** | Turkish-side target fact exposure'ın English answer access'e etkisi; **paired sibling-arm treatment contrast** `TR→EN(M2-B) − TR→EN(M2-A)` |
| TR→TR | Secondary outcome | Turkish lexicalization + access; Türkçe capability ile birlikte yorumlanır |
| EN→TR | Exploratory | Türkçe cevap üretimi; ana başarı metric'i veya gate değildir |

Her factual direction'da:

- Forms A–D ve scaffold balance;
- relation binding ve same-subject relation swap;
- canonical answer/alias freeze;
- no-answer, empty/repetition, short-output diagnostics;
- target fact contamination ve source corpus overlap;
- paired bootstrap CI

raporlanır. M2-A ve M2-B aynı evaluation package'i kullanır.

## 6. Manipulation-check açılma kuralı

Sayısal threshold bu belgede uydurulmayacaktır; Document 148 literature matrix, bounded model
baseline ve benchmark floor/ceiling audit'i görüldükten sonra, factual treatment sonucu görülmeden
dondurulmalıdır. Yapısal açılma kuralı:

1. **Turkish LM:** M2-A ve M2-B, M1'e göre önceden tanımlı yönde within-model PPL iyileşmesi
   göstermeli; modeller arası karşılaştırma BPC/bits-per-byte ile yapılmalı; yalnız PPL düşüşü tek
   başına yeterli değil.
2. **Independent linguistic capability:** TurBLiMP veya audit'i geçmiş base-compatible grammar
   alt seti beklenen yönde değişmeli veya baseline floor/ceiling ve predeclared equivalence/no-harm
   gerekçesi kaydedilmelidir.
3. **Broader capability:** TurkishMMLU/EXAMS sonucu, saf language acquisition değil, Turkish
   knowledge/school/reasoning destekleyici manipulation check olarak raporlanmalıdır.
4. **English retention:** English PPL ve EN→EN retention önceden belirlenen guardrail içinde
   kalmalıdır.
5. **Factual separation:** Bu maddeler factual TR→EN treatment sonucu görülmeden seçilmiş olmalı;
   başarısız manipulation check varsa M2-B factual gain'i “Turkish adaptation” diye etiketlenmez.

### 6.1 Direction of interpretation

- PPL iyileşir, capability değişmezse: fluency/likelihood kazanımı sınırlı veya benchmark
  insensitive; factual sonuç tek başına language acquisition değildir.
- Capability iyileşir, TR→EN iyileşmezse: Turkish adaptation var, cross-lingual factual transfer
  yok/ölçüm gücü yetersiz olabilir.
- TR→EN iyileşir, Turkish PPL/capability iyileşmezse: factual memorization, prompt artifact,
  contamination veya answer-language effect şüphesi doğar.
- EN retention bozulursa: transfer–relearning trade-off ve forgetting ayrı raporlanır; olumlu
  TR→EN sonucu “unconditional success” değildir.

## 7. Kontaminasyon ve split kuralları

Measurement package için ayrı frozen manifest tutulur:

- Turkish training corpusundan document-level exclusion;
- 5,000 subject/25,000 fact/713 object-surface/65,717 pattern inventory taraması;
- factual evaluation prompt/answer/alias overlap;
- M1 English factual data overlap;
- benchmark source train/dev/test overlap;
- public benchmark release revision, license ve hash;
- random seed, item IDs ve evaluator version.

Target facts, capability items ve held-out PPL text birbirinden ayrıdır. Capability benchmark
items'in training corpusunda bulunma ihtimali raporlanmadan skorlar “genuine capability” olarak
sunulmaz.

## 8. Base vs instruction ve CPT vs SFT kararı

- Ana manipulation check **base model / causal LM** için tasarlanır.
- Turkish-SFT, Kara-Kumru, MODA'nın PEFT/SFT sonucu ve DIPLomA delta merge'i ana package'a
  karıştırılmaz.
- Instruction benchmark skorları ancak ayrı bir alignment extension'da, base CPT sonucundan sonra
  raporlanabilir.
- M2-A/M2-B'ye translated instruction data, synthetic dialogue veya chat template eklenmez.

## 9. Aynı paket için minimum rapor tablosu

Her state için en az şu satırlar üretilmelidir:

| State | Turkish PPL + BPC/bits-per-byte | English PPL | TurBLiMP / grammar | TurkishMMLU likelihood | EXAMS likelihood | EN→EN | TR→EN | TR→TR | EN→TR exploratory |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| M0 | frozen | frozen | frozen | frozen | frozen | frozen | baseline | baseline | baseline |
| M1 | delta | delta | delta | delta | delta | retention | delta | delta | delta |
| M2-A | delta | delta | delta | delta | delta | guardrail | primary control | secondary | exploratory |
| M2-B | delta | delta | delta | delta | delta | guardrail | primary treatment | secondary | exploratory |

Her hücrede point estimate + uncertainty + evaluator/data hash bulunur. Global average, minimum
relation/task cell ve robust intersection ayrı raporlanır; bir global ortalama zayıf relation veya
task cell'i gizleyemez.

## 10. Günlük çalışma günlüğü

| Alan | Kayıt |
|---|---|
| Tarih/saat | 2026-08-07, Europe/Berlin |
| İş paketi | WP4 Turkish capability ve manipulation-check planı |
| Okunan kaynaklar | Document 146; CETVEL, TurkBench, TurkishMMLU, EXAMS, TrClaim-19 ve TurBLiMP birincil sayfaları; Documents 110, 136, 138, 145 |
| Doğrulanan iddialar | Native/MCQ benchmark kapsamları; instruction vs base uyumsuzlukları; factual direction rolleri |
| Çelişkiler | Benchmark büyüklüğü/alt görevlerinin farklı sürümleri olabilir; exact item revision/license henüz frozen değil |
| Üretilen dosya | `documentation/150_TURKISH_CAPABILITY_AND_ADAPTATION_MANIPULATION_CHECK_PLAN_TR.md` |
| Açık sorular | Exact subset, hashes, overlap, floor/ceiling ve numeric thresholds |
| Yetki sınırı | HU erişimi yok; training/evaluation yok; broad submission yok; büyük indirme yok; artifact silme/taşıma yok |

## 11. Dış kaynaklar

- [CETVEL](https://aclanthology.org/2026.eacl-long.46/) — **A**
- [TurkBench](https://arxiv.org/abs/2601.07020) — **A**
- [TurkBench online space](https://huggingface.co/turkbench) — **A**
- [TurkishMMLU](https://arxiv.org/abs/2407.12402) — **A**
- [EXAMS](https://arxiv.org/abs/2011.03080) — **A**
- [TrClaim-19](https://aclanthology.org/2020.conll-1.31/) — **A**
- [TurBLiMP](https://arxiv.org/abs/2506.13487) — **A**

## 12. External validation revision — 2026-08-07

- Aynı M0/M1/M2-A/M2-B measurement package, English retention, `TR→EN` primary, `TR→TR`
  secondary ve `EN→TR` exploratory rolleri korunmuştur.
- Raw PPL'nin cross-tokenizer model sıralaması için kullanılması düzeltilmiş; BPC/bits-per-byte
  cross-model normalizasyonu eklenmiş, fertility ayrı tutulmuştur.
- TurBLiMP, exact release/license/contamination/floor-ceiling koşullu primary independent
  linguistic diagnostic adayı yapılmış; TurkishMMLU ve EXAMS geniş knowledge/school/reasoning/
  cultural capability olarak yeniden sınıflandırılmıştır.
- Eski `M2-B − M2-A interaction` terminolojisi kaldırılmış; mevcut sibling-arm tasarımı için estimand
  `TR→EN(M2-B) − TR→EN(M2-A)` paired treatment contrast olarak düzeltilmiştir. Interaction/DID
  ancak ayrıca repeated/unrepeated factual subgroup faktörü dondurulursa kullanılabilir.
- Paket **frozen değildir**: exact benchmark revisions, item IDs/hashes, licenses, overlap,
  floor/ceiling ve numeric thresholds hâlâ freeze pending'dir. Önceki Qwen pilot sonuçları
  değişmemiştir.
