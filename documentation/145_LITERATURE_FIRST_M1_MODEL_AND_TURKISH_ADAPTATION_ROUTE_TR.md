# 145 — Literatür-Öncelikli M1 Model, Türkçe Korpus ve M2-A/M2-B Deney Rotası

**Tarih:** 2026-08-09 (roadmap güncellemesi)  
**Durum:** Literatür/korpus aday denetim rotası; yeni training ailesi henüz açılmadı  
**Önkoşul:** Doküman 144 ve `Expose.pdf` sayfa 6  
**Ana karar:** Önce kaynak model ile Türkçe adaptasyonun geçerliliğini kanıtla; sonra eşleşmiş
M2-A/M2-B factual karşılaştırmasını çalıştır

**2026-08-09 güncelleme notu:** Türkçe corpus adımı artık yalnızca CulturaX ve vngrs arasında
seçim olarak tanımlanmamaktadır. Küçük/orta Türkçe model çalışmalarında kullanılan OSCAR, mC4,
Wikipedia ve karma web/book/scientific kaynaklar; ayrıca HPLT, FineWeb2 ve Bella Turca gibi yeni
adaylar paper-backed bir karşılaştırma havuzuna alınmıştır. Bu havuz henüz seçim, indirme,
materialization veya training yetkisi vermez. Güncel operasyonel durum `ready_to_measure=false`,
`ready_to_train=false` ve ana gate `blocked_by_measurement_design` olarak korunur.

**Authority alignment:** Bu belgenin güncel rol/model/corpus statüleri
[`151aw_LITERATURE_MODEL_CORPUS_AND_M2A_M2B_ROADMAP_ALIGNMENT_TR.md`](./151aw_LITERATURE_MODEL_CORPUS_AND_M2A_M2B_ROADMAP_ALIGNMENT_TR.md)
ile uzlaştırılmıştır. Özellikle OLMo/Pythia/Falcon birer adaydır, Qwen ayrı bir multilingual
positive control'dür; vngrs koşullu materialization adayı, trwiki kontrol, CulturaX ise
`excluded_access_blocked` durumundadır. Diğer corpus adları literatür/provenance adaylarıdır ve
seçilmiş corpus gibi yorumlanmamalıdır.

## 1. Yönetici özeti

Yeni rota altı aşamadan oluşur:

1. **Model provenance denetimi:** Türkçe exposure'ı en düşük ve eğitim verisi en iyi belgelenmiş
   base modelleri belirle.
2. **Sınırlı M1 yeniden ekranı:** Önceki yüzlerce recipe'i tekrarlamadan, en fazla birkaç
   literatür-gerekçeli koşulla hangi İngilizce-ağırlıklı modellerin kullanılabilir M1 ürettiğini
   ölç.
3. **Korpus denetimi:** Wikipedia-only pilot yerine paper-backed aday havuzunu — `vngrs-web-corpus`,
   Turkish OSCAR/mC4, HPLT Turkish, FineWeb2 Turkish, CulturaX-tabanlı derlemeler ve Bella Turca —
   kaynak, lisans, temizlik, tekrar, domain ve contamination açısından karşılaştır; hiçbir adayı
   audit tamamlanmadan seçilmiş sayma.
4. **Adaptasyon manipulation check:** Hedef olgu eklemeden önce Türkçe PPL ve donmuş Türkçe yetenek
   ölçümünün gerçekten iyileştiği veri dozunu bul.
5. **Ana paralel deney:** Aynı M1'den M2-A=`Türkçe genel korpus` ve M2-B=`aynı korpus + Türkçe
   olgu tekrarları` kollarını eşit bütçeyle eğit.
6. **Yalnız kanıt haklı çıkarırsa ölçekle:** 2.500 fact sonucu anlaşılır ve seed'lerde tutarlıysa
   25.000 fact veya ikinci bir model ailesi aç.

Bu rota Qwen sonucunu iptal etmez. Qwen, güçlü çokdilli kontrol; tamamlanan Wikipedia koşusu ise
zayıf-dozlu pilot kanıtıdır.

## 2. Güncellenmiş estimand ve deney şeması

### 2.1 Model durumları

```text
M0: İngilizce-ağırlıklı, base/pretrained başlangıç modeli
M1: M0 + İngilizce sentetik factual acquisition

aynı donmuş M1
├── M2-A: genel Türkçe continual pretraining; hedef fact yok
└── M2-B: aynı genel Türkçe continual pretraining + Türkçe hedef fact tekrarları
```

### 2.2 Ana ölçümler

- **Transfer:** M2-A'nın TR→EN factual başarısı ile M1'in TR→EN başarısı arasındaki değişim.
- **Relearning katkısı:** M2-B − M2-A, birincil olarak TR→EN yönünde.
- **Kaynak bilgi koruma:** M1/M2-A/M2-B EN→EN factual başarısı.
- **Türkçe lexicalization:** TR→TR ayrı ve ikincil ölçüm.
- **Dil adaptasyonu manipulation check:** held-out Türkçe PPL ve base modele uygun Türkçe yetenek
  ölçümü.

`EN→TR` ana başarı ölçütü değildir. İngilizce soruya Türkçe cevap beklemek tezin çekirdek
mekanizması değildir; kullanılırsa yalnızca exploratory yön/lexicalization tanısı olarak raporlanır.

### 2.3 Eşit-bütçe kuralı

M2-B'nin factual satırları M2-A'ya göre ek training tokenı yaratmayacaktır. M2-B'deki factual
tokenlar, aynı konumlardaki eşleşmiş nötr Türkçe tokenların yerini almalıdır. İki kol için:

- aynı M1 checkpoint;
- aynı seed;
- aynı toplam token ve optimizer update sayısı;
- aynı genel korpus havuzu ve mümkün olduğunca aynı sıra;
- aynı checkpoint/endpoint seçimi;
- aynı evaluation paketi

kullanılacaktır. Sonuca göre ayrı checkpoint seçilmeyecektir.

## 3. M1 model taraması: mevcut kanıt ve yeni adaylar

### 3.1 “Türkçe görmemiş” ne kadar kesin söylenebilir?

Web verisiyle eğitilmiş bir model için adli düzeyde sıfır Türkçe contamination kanıtlamak çoğu
zaman mümkün değildir. Bu nedenle iddialar üç kanıt düzeyinde tutulmalıdır:

1. **Güçlü belge:** Model kartı/eğitim verisi açıkça English-only der ve veri kaynakları
   izlenebilir.
2. **Orta belge:** Çokdilli diller listelenir ve Türkçe listede yoktur; yine de web contamination
   ihtimali vardır.
3. **Zayıf belge:** Geniş çokdilli eğitim bildirilir veya dil dağılımı açıklanmaz.

Tezde “hiç Türkçe görmedi” yerine kaynağın desteklediği doğru ifade kullanılmalıdır:
`documented English-only`, `Turkish not listed`, veya `Turkish exposure unknown`.

### 3.2 Aday matrisi

| Model | Aşama ve dil provenance'ı | Mevcut M1 kanıtımız | Önerilen rol |
|---|---|---|---|
| **OLMo-2-0425-1B** | Base; açık ve English-dominant provenance; 4T token; kod, checkpoint ve loglar açık; sıfır Türkçe exposure kanıtlanmış değil | Henüz test edilmedi | Birinci seviye aday; provenance ve tekrarlanabilirlik güçlü |
| **Pythia-1.4B** | Base; The Pile ve aynı veri sırası boyunca 154 checkpoint; English-language tasarım sinyali güçlü, fakat adli düzeyde sıfır Türkçe exposure iddia edilmez | Henüz test edilmedi | Birinci seviye bilimsel kontrol; temiz stage ve güçlü reproducibility |
| **Falcon-RW-1B** | Base; kart açıkça English-only der; 350B RefinedWeb tokenı; web-kaynaklı artık contamination olasılığı ayrıca dürüstçe korunur | Henüz test edilmedi | En açık dil ayrımı; tokenizer/yaş/kapasite riski ölçülmeli |
| **StableLM2-1.6B** | Base; yedi dil listeleniyor, Türkçe listelenmiyor; 2T token | 500 fact: robust `%93.8`, min relation `%69`, PPL ratio `1.477` | İkinci seviye aday; eski sonucu nedeniyle sınırlı tek yeniden test haklı olabilir |
| **SmolLM2-1.7B** | Base; English-centric FineWeb-Edu/DCLM/code/math karışımı; mutlak sıfır Türkçe kanıtı yok | Robust `%39.6`; remediation `%52.2` ve `%55.8`, gate altında | Negatif karşılaştırma; yeni ana optimizasyon dalı açılmamalı |
| **Qwen2.5-1.5B** | Base; 29+ dil desteği; Türkçe miktarı açıklanmıyor | 2.500 fact, seed 42/43 robust `%96.08/%96.20`; PPL ratio `1.082/1.032` | Güçlü çokdilli pozitif kontrol ve mevcut başarılı M1 |
| **Gemma-2-2B** | Base; tam Türkçe exposure ayrımı bu proje kaydında yok | Robust `%78`, min relation `%7`, PPL ratio `704.873` | Yeniden açma; eski model-recipe kombinasyonu açıkça zayıf |
| **Llama-3.2-1B** | Base; multilingual kabiliyet, training dağılımı tam açık değil | Robust `%81.4`, min relation `%7`, PPL ratio `3.862` | Yeniden açma; causal provenance ve M1 sonucu zayıf |

Birincil kaynaklar:

- [OLMo-2-0425-1B model card](https://huggingface.co/allenai/OLMo-2-0425-1B)
- [Pythia-1.4B model card](https://huggingface.co/EleutherAI/pythia-1.4b)
- [Falcon-RW-1B model card](https://huggingface.co/tiiuae/falcon-rw-1b)
- [StableLM2-1.6B model card](https://huggingface.co/stabilityai/stablelm-2-1_6b)
- [SmolLM2-1.7B model card](https://huggingface.co/HuggingFaceTB/SmolLM2-1.7B)
- [Qwen2.5-1.5B model card](https://huggingface.co/Qwen/Qwen2.5-1.5B)
- Yerel M1 karşılaştırması: [`106_M1_CROSS_FAMILY_MODEL_SCREENING_RESULT.md`](./106_M1_CROSS_FAMILY_MODEL_SCREENING_RESULT.md)
- Replike Qwen sonucu: [`127_QWEN_SCALE_REPLICATION_RESULT_AND_SMOLLM_LAMBDA025_STATUS.md`](./127_QWEN_SCALE_REPLICATION_RESULT_AND_SMOLLM_LAMBDA025_STATUS.md)

### 3.3 Önerilen kısa liste — seçim değildir

İlk read-only/ucuz denetim sırası:

1. OLMo-2-1B;
2. Pythia-1.4B;
3. Falcon-RW-1B;
4. mevcut Qwen2.5-1.5B pozitif kontrolü;
5. yalnız gerekirse StableLM2-1.6B.

İlk üç modelin hepsini büyük ölçekte eğitmek gerekmemektedir. Amaç “kazanan modeli bulana kadar
aramak” değil, provenance ile M1 kullanılabilirliği arasındaki trade-off'u önceden tanımlanmış
sınırlı bir ekranda görmek olmalıdır.

Bu sıra bir model-selection sonucu değildir. Exact revision/stage/license, Turkish baseline
headroom, tokenizer davranışı ve M1 usability aynı pre-frozen karar tablosuna girmeden hiçbir aday
`selected primary model` olarak adlandırılmaz.

## 4. M1 yeniden değerlendirme protokolü

### Faz M1-0 — Training olmadan model kartı ve baseline denetimi

Her aday için şunlar dondurulur:

- tam Hugging Face repo ve revision/commit;
- base/instruct durumu;
- lisans;
- parametre sayısı ve context length;
- bildirilen pretraining dilleri/veri kaynakları;
- tokenizer revision ve Türkçe tokenization fertility;
- M0 English ve Turkish held-out PPL;
- aynı küçük Türkçe capability paketindeki M0 skorları;
- HU/Transformers uyumluluğu ve tahmini bellek.

Tokenizer fertility örneği:

```text
"Evlerimizden ayrıldığımızda yağmur yağıyordu."
```

Her model için token sayısı, karakter/token ve kelime/token oranı raporlanır. Bu değer tek başına
model seçmez; Türkçe adaptasyon maliyetini ve tokenizer dezavantajını açıklar.

### Faz M1-1 — Sınırlı 500-fact acquisition ekranı

- Aynı 100 subject / 500 fact population kullanılabilir.
- En fazla iki önceden gerekçelendirilmiş recipe denenmelidir: basit factual CPT baseline ve
  mevcut Qwen'de çalışan retention/replay recipe'inin model-uyumlu sürümü.
- Her aday aynı factual Forms A–D, relation binding ve generic-retention ölçümlerine girer.
- Checkpoint kuralı sonuç görülmeden dondurulur.
- Recipe veya threshold model başına post-hoc değiştirilmez.

Buradaki amaç her modeli `%100` yapmak değildir. Ana deney için kullanılabilir model şu üç koşulu
birlikte sağlamalıdır:

1. İngilizce M1 olgularını prompt-robust biçimde öğrenmesi;
2. genel İngilizce modellemesini kullanılamaz hâle getirmemesi;
3. Türkçe adaptasyon için ölçülebilir headroom ve makul tokenizer davranışı bırakması.

Kesin sayısal geçiş eşiği, yeni sonuçlara bakılmadan önce literatür ve eski frozen gate'lerle
uzlaştırılarak ayrı execution contract'ta dondurulmalıdır.

### Faz M1-2 — Seçim ve replikasyon

- En fazla bir English-centric ana model seçilir.
- Qwen kontrol olarak korunur; her yeni modelin bütün Qwen zincirini tekrar etmesi zorunlu değildir.
- Seçilen modelin M1 sonucu ikinci seed'de doğrulanmadan ana M2-A/M2-B ailesi açılmaz.
- Seçim yalnız en yüksek skora değil; provenance, M1 kullanılabilirliği, Türkçe headroom, maliyet ve
  reproducibility'nin önceden tanımlı Pareto kararına dayanır.

## 5. Türkçe korpus araştırması

### 5.1 Mevcut Wikipedia-only pilotu

Mevcut `trwiki-20260601` korpusu:

- tarihli ve hash'li;
- temizleme/dedup ve sentetik contamination denetiminden geçmiş;
- yüksek provenance ve düşük belirsizliğe sahip

olduğu için iyi bir **kontrol korpusu**dur. Ancak tamamlanan ana kollarda yalnızca 2.048 × 512 =
`1,048,576` training tokenı kullanılmıştır. Bu doz ve tek-domain yapı, literatürdeki Türkçe CPT
ölçeklerinden çok küçüktür. Bundan sonra Wikipedia tek başına varsayılan ana adaptasyon korpusu
değil, karışım bileşeni veya küçük-doz kontrolü olarak değerlendirilmelidir.

### 5.2 CulturaX Türkçe

*Bridging the Bosphorus* Türkçe CulturaX splitini kullanır. Bu split, mC4 ve farklı OSCAR
sürümlerinin temizlenip deduplicate edilmiş birleşimidir. Makale yaklaşık `179.2 GB` ve `130B`
training tokenı bildirir; continual-pretraining deneylerinde veri dozunu kademeli büyütür.

Bilimsel değeri:

- Wikipedia'dan daha geniş domain çeşitliliği;
- Türkçe adaptation literatüründe doğrudan kullanım;
- doz ölçekleme için published precedent.

Riskleri:

- web kaynaklı kalite/PII/telif ve domain imbalance;
- indirilen exact revision'ın ve filtre durumunun yerelde yeniden dondurulması gereği;
- sentetik subject/object contamination taraması.

Kaynak: [Bridging the Bosphorus, MRL 2024](https://aclanthology.org/2024.mrl-1.21/).

### 5.3 `vngrs-ai/vngrs-web-corpus`

Dataset card'a göre bu korpus:

- OSCAR-2201 ve mC4'ün temizlenmiş Türkçe bölümlerini birleştirir;
- `50.3M` sayfa ve VBART tokenizer ile `25.33B` token içerir;
- indirilebilir dosya boyutu yaklaşık `84.9 GB`dır;
- VBART için oluşturulmuş, TURNA ve daha sonra MODA gibi çalışmalarda kullanılmıştır;
- lisansı `CC BY-NC-SA 4.0` olarak listelenir.

Ancak MODA makalesi önemli sınırlamalar kaydeder:

- temizlik rule/heuristic tabanlıdır, semantic filtering yoktur;
- ek language identification yöntemi belgeli değildir;
- CPT öncesi MinHash near-dedup uygulanmamıştır;
- kaynak/domain dağılımı güvenilir biçimde raporlanmamıştır.

Bu nedenle korpus “başkaları kullandı, doğrudan kopyalayalım” şeklinde değil, **yeniden audit
edilecek güçlü aday** olarak ele alınmalıdır.

Kaynaklar:

- [`vngrs-web-corpus` dataset card](https://huggingface.co/datasets/vngrs-ai/vngrs-web-corpus)
- [MODA, SIGTURK 2026](https://aclanthology.org/2026.sigturk-1.17/)

### 5.4 Paper-backed diğer Türkçe corpus adayları

vngrs güçlü ve doğrudan kullanılabilir görünen bir adaydır; fakat Türkçe model literatüründeki
tek precedent değildir. Yeni rota, aşağıdaki adayları aynı seçim matrisi içinde tutar. Buradaki
“paper-backed” ifadesi, adayın literatürde kullanıldığını veya yönteminin yayınlandığını gösterir;
bugünkü exact snapshot'ın lisans, revision, erişim, kalite ve contamination koşullarını otomatik
olarak doğrulamaz.

| Aday | Küçük/orta model veya corpus precedent'i | Roadmap'teki rol | Henüz çözülmemiş nokta |
|---|---|---|---|
| **Turkish OSCAR** | [Tiny–Medium Turkish BERT](https://arxiv.org/abs/2307.14134) ve [Turkish tokenizer çalışması](https://arxiv.org/abs/2204.08832) | Doğrudan Türkçe model pretraining precedent'i; tokenizer/fertility karşılaştırması | Exact OSCAR snapshot'ı, filtre/dedup, LID, lisans ve target-fact overlap |
| **Turkish mC4** | [mC4/T5](https://arxiv.org/abs/1910.10683) veri ailesi ve [SindBERT](https://aclanthology.org/2026.sigturk-1.1/) | Büyük karma web-corpus precedent'i; OSCAR ile karışım etkisini inceleme | Exact Türkçe shard/revision, karma kaynak kalitesi, lisans ve tekrar oranı |
| **cosmosGPT Türkçe** | [cosmosGPT](https://arxiv.org/abs/2404.17336) | Monolingual Türkçe GPT pretraining'in doğrudan model precedent'i | Exact corpus bileşimi, tekrar/epoch hesabı, tokenizer ve yeniden üretilebilirlik |
| **HPLT Turkish** | [HPLT veri/boru hattı çalışması](https://aclanthology.org/2024.eamt-2.27/), [resmî v1.2 release](https://hplt-project.org/datasets/v1.2) | Metadata-rich, yeni ve denetlenebilir public corpus adayı | Exact Türkçe release kimliği, erişim/route, sample quality ve target overlap |
| **FineWeb2 Turkish** | [FineWeb2](https://arxiv.org/abs/2506.20920), [resmî pipeline](https://github.com/huggingface/fineweb-2) | Dil-özel filtreleme ve dedup yöntemi için modern corpus adayı | Exact Türkçe split, ham veri provenance'ı, lisans, route ve küçük-model training precedent'i |
| **CulturaX-tabanlı temiz Türkçe corpus** | [CulturaX](https://aclanthology.org/2024.lrec-main.377/) ve [Türkçe temizleme çalışması](https://doi.org/10.1109/icmi65310.2025.11141276) | CulturaX erişimi mümkün olursa karşılaştırmalı geniş-data adayı | Projede CulturaX erişimi `excluded_access_blocked`; paper'daki corpus ile current snapshot eşit sayılamaz |
| **Bella Turca** | [Bella Turca / TSD 2024 kaydı](https://doi.org/10.1007/978-3-031-70563-2_16) | Çeşitli kaynaklardan Türkçe corpus tasarımı için literatür adayı | Full paper/data erişimi, exact materialization, lisans ve kalite kanıtı |

Bu tablo karar sırası da verir: OSCAR/mC4/cosmosGPT doğrudan **“daha önce küçük/orta Türkçe
model eğitildi mi?”** sorusuna; HPLT/FineWeb2/CulturaX/Bella Turca ise **“hangi veri üretim ve
temizlik hattı bugün denetlenebilir?”** sorusuna cevap aratır. `trwiki-20260601` cross-domain
control olarak kalır; vngrs ise mevcut C1 kararı gereği yalnız conditional primary materialization
candidate'dir. Aday havuzuna eklenmeleri seçildikleri veya eğitim için hazır oldukları anlamına
gelmez.

Yöntemsel arka plan için [Quality at a Glance](https://arxiv.org/abs/2103.12028) ve [Turkish NLP
resources survey](https://doi.org/10.1007/s10579-022-09605-4) okunmalıdır. Bu çalışmalar aday
corpus'ları seçmez; kalite, kapsam ve kaynak iddialarını karşılaştırırken kullanılacak audit
başlıklarını gerekçelendirir.

### 5.5 Kumru bize ne öğretiyor?

[Kumru-2B-Base](https://huggingface.co/vngrs-ai/Kumru-2B-Base) base/pretrained modeldir;
[Kumru-2B](https://huggingface.co/vngrs-ai/Kumru-2B) ise instruction-fine-tuned varyanttır. Model
kartı Türkçe için sıfırdan eğitim, temiz/dedup edilmiş yaklaşık `500 GB`, `300B` pretraining tokenı
ve instruct model için `1M` SFT örneği bildirir.

Bu iddia ile yayımlanmış `vngrs-web-corpus` kartındaki `84.9 GB / 25.33B token` sayıları aynı şey
değildir. Muhtemel açıklamalar farklı corpus versionları, tekrar epoch'ları, ek veri veya farklı
tokenizer sayımıdır; fakat varsayım yapılmamalıdır. Kullanmadan önce:

- Kumru'nun exact pretraining corpus listesi;
- 500 GB ile 84.9 GB arasındaki fark;
- 300B tokenın unique token mı yoksa epoch-toplam exposure mı olduğu;
- uygulanan dedup/language/quality filtreleri;
- base model ile instruct model aşamalarının ayrımı

doğrulanmalıdır.

Kumru'nun ana katkısı bize hazır bir recipe vermekten çok, **Türkçe tokenizer + büyük ve çeşitli
Türkçe pretraining verisi + ayrı base/SFT aşaması** kombinasyonunun önemli olduğunu göstermesidir.

### 5.6 Alican Kiraz çalışmaları nasıl kullanılmalı?

[Kara-Kumru-v1.0-2B](https://huggingface.co/AlicanKiraz0/Kara-Kumru-v1.0-2B), Kumru-2B instruct
üzerinde full fine-tuning yapılmış bir Türkçe task modelidir. CETVEL üzerinde QA, summarization ve
TR→EN translation kazanımları; bazı NLI/classification/GEC görevlerinde ise gerilemeler raporlar.
Bu, yalnızca ortalama skor yerine **görev bazlı kazanım ve gerileme** raporlamamız gerektiğini
destekler.

Fakat mevcut Kara-Kumru model kartı training datasetinin tam kimliğini, learning rate'i, epoch ve
örnek sayısını vermemektedir. Bu nedenle Kara-Kumru kartı M2 continual-pretraining corpus recipe'i
olarak kopyalanamaz.

Alican Kiraz'ın yayımladığı
[Turkish-SFT-Dataset-v1.0](https://huggingface.co/datasets/AlicanKiraz0/Turkish-SFT-Dataset-v1.0)
yaklaşık 5.58K uzun sentetik instruction örneği ve 20M+ token bildirir. Bu veri SFT/task alignment
içindir; genel Türkçe M2 continual pretraining korpusunun yerine geçmez. Ana tez deneyinde SFT
verisi ile unlabeled CPT verisi karıştırılmamalıdır.

## 6. Korpus kabul denetimi

Ana korpus seçilmeden önce her aday için aynı rapor üretilmelidir:

| Denetim | Zorunlu çıktı |
|---|---|
| Kimlik | dataset repo, revision/commit, indirme tarihi, dosya listesi ve SHA-256 |
| Lisans | dataset ve kaynak lisansları; tez/araştırma kullanım uygunluğu |
| Boyut | byte, document, character ve **seçilen model tokenizerıyla** token sayısı |
| Dil | fastText/CLD benzeri language-ID dağılımı ve Türkçe confidence örneklemi |
| Kalite | boilerplate, çok kısa/uzun, spam, code, adult/harmful ve encoding oranları |
| Tekrar | exact duplicate ve MinHash/near-duplicate oranı |
| Domain | wiki, news, forum, blog, government, education vb. tahmini dağılım |
| Literatür precedent'i | Kullanıldığı küçük/orta model veya paper, model stage'i, corpus bileşimi, tokenizer ve bildirilen ölçek |
| Contamination | sentetik subject/object/alias exact ve fuzzy taraması |
| Evaluation ayrımı | held-out PPL ve benchmark metinleriyle overlap denetimi |
| Örnek denetimi | sabit random seed ile insan tarafından okunacak stratified sample |

Korpus “Türkçe etiketi var” veya “bir paper'da kullanılmış” diye kabul edilmez. Paper'daki
corpus ile bugünkü exact snapshot ayrıştırılır; audit geçmeyen veri ana deneyde kullanılmaz.

## 7. Adaptasyon dozunu seçme rotası

Eski `1M-token` Wikipedia dozu ana deneyi açmak için yeterli kanıt üretmedi. Yeni doz factual
sonuçlara bakılarak seçilmemelidir. Öneri:

1. Sadece M2-A-benzeri, **factsiz** Türkçe CPT pilotu çalıştır.
2. Literatürdeki ölçeğe yaklaşan önceden belirlenmiş küçük bir dose ladder kullan; ilk makul
   basamaklar örneğin `50M`, `250M` ve kaynak yeterliyse `1B` target-language token olabilir.
3. Her dozda Türkçe held-out PPL, donmuş capability ölçümü, EN PPL ve M1 EN→EN retention ölç.
4. En küçük açıkça etkili ve retention guardrail içinde kalan dozu önceden tanımlı kural ile seç.
5. Ancak bu doz seçildikten sonra factual M2-A/M2-B ana kollarını üret.

Rakamlar nihai contract değildir; korpus tokenization audit'i ve HU runtime tahmininden sonra
dondurulmalıdır. Önemli fark, dose seçiminin TR→EN factual treatment sonucundan önce yapılmasıdır.

## 8. Türkçe adaptasyonun değerlendirme paketi

### 8.1 Her state aynı testlere girmelidir

Değerlendirilecek durumlar:

```text
M0, M1, M2-A, M2-B
```

İki seed varsa bütün state'ler seed zinciri içinde eşleştirilir. M2-A ve M2-B kesinlikle aynı test
paketine girer.

### 8.2 Birincil manipulation check

1. **Held-out Turkish PPL:** Adaptasyon verisinden ayrı, hash'li ve contamination-audited split.
2. **Turkish capability delta:** Base causal modele uygun, instruction-following gerektirmeyen
   en az bir donmuş likelihood/multiple-choice/cloze ölçümü.
3. **English retention:** Held-out English PPL ve M1 EN→EN factual retention.

PPL yalnız aynı tokenizer/model zinciri içinde karşılaştırılır. Farklı tokenizer kullanan iki
modelin ham PPL değerleri doğrudan model sıralaması olarak kullanılmaz.

### 8.3 Türkçe benchmark adayları

- **CETVEL:** geniş görev taksonomisi; ancak her alt görev base model için uygun değildir.
- **TurkBench:** daha geniş Türkçe değerlendirme perspektifi için literatür ve uygulama denetimi.
- **TurkishMMLU / EXAMS-TR / TRCLAIM-19:** MODA'da kullanılmıştır; base-model prompt formatı,
  contamination ve lisans ayrıca incelenmelidir.
- Morphology/grammar için küçük, likelihood-temelli bir diagnostic set hazırlanabilir; bu set
  ana benchmark yerine geçmez ve creation sonrası dondurulur.

İlk ana paket, compute ve base-model uygunluğu için birkaç önceden seçilmiş alt görevle sınırlı
kalmalıdır. Bütün CETVEL skorunu optimize etmek bu tezin hedefi değildir.

### 8.4 Factual yönler ve örnekler

Sentetik örnek fact:

```text
English M1 statement: "Neral Voss was born in Talmera."
```

| Yön | Örnek prompt | Beklenen cevap | Yorum |
|---|---|---|---|
| EN→EN | `Where was Neral Voss born?` | `Talmera` | İngilizce M1 storage/retention |
| TR→EN | `Neral Voss nerede doğdu?` | `Talmera` | Birincil cross-lingual access; object alias değişmez |
| TR→TR | `Neral Voss nerede doğdu?` | önceden dondurulmuş Türkçe alias | Access + Türkçe lexicalization |
| EN→TR | İngilizce soru | Türkçe alias | Ana sonuç değil; yalnız exploratory diagnostic |

Özel isim objectleri dil değişiminden daha az etkilendiği için birincil TR→EN yorumunu
sadeleştirir. Çevrilebilir common-noun objectler için İngilizce ve Türkçe alias listeleri eğitimden
önce dondurulmalıdır.

## 9. Literatürden tasarıma taşınan dersler

| Kaynak | İlgili bulgu | Projeye etkisi |
|---|---|---|
| [Bridging the Bosphorus](https://aclanthology.org/2024.mrl-1.21/) | İngilizce modelleri Türkçeye CPT; CulturaX; kademeli veri dozu; LoRA ve from-scratch karşılaştırması | Wikipedia-only yerine geniş web korpusu ve dose ladder |
| [MODA](https://aclanthology.org/2026.sigturk-1.17/) | Dil edinimini task alignment'dan ayırır; `vngrs-web-corpus`; causal LM CPT | Base/CPT aşamasını SFT'den ayrı tut |
| [Tiny–Medium Turkish BERT](https://arxiv.org/abs/2307.14134) | Küçük ve orta Türkçe encoder'ların Türkçe corpus ile eğitilebildiğini gösteren doğrudan precedent | M2 corpus seçimi “teknik olarak mümkün mü?” yerine veri bileşimi, tokenizer ve recipe karşılaştırmasına dayanmalı |
| [Impact of Tokenization for Turkish](https://arxiv.org/abs/2204.08832) | Türkçe tokenizer seçiminin fertility ve model maliyetiyle ilişkisini inceler | Her M1 adayı için tokenizer fertility ve Türkçe headroom birlikte raporlanmalı |
| [cosmosGPT](https://arxiv.org/abs/2404.17336) | Monolingual Türkçe GPT pretraining örneği | Türkçe-only model precedent'i var; ancak paper corpus'u current candidate snapshot ile eşitlenmemeli |
| [SindBERT](https://aclanthology.org/2026.sigturk-1.1/) | mC4/OSCAR/Wikipedia gibi kaynakların karma kullanımını ve büyük Türkçe pretraining ölçeğini örnekler | Mixed-source adaylar için kaynak ağırlıkları, dedup ve domain dağılımı ayrı dondurulmalı |
| [HPLT](https://aclanthology.org/2024.eamt-2.27/) / [FineWeb2](https://arxiv.org/abs/2506.20920) | Metadata, language-specific filtering ve corpus construction açısından daha yeni public hatlar | Sadece corpus büyüklüğü değil, reproducible provenance ve quality evidence karşılaştırılmalı |
| [Bella Turca](https://doi.org/10.1007/978-3-031-70563-2_16) ve [CulturaX-tabanlı Türkçe temizleme](https://doi.org/10.1109/icmi65310.2025.11141276) | Çeşitli kaynakları ve temizleme tasarımını öne çıkaran ek Türkçe corpus precedent'leri | Candidate pool genişler; erişim, exact data identity ve lisans çözülmeden seçim yapılmaz |
| [How to Adapt ... 1600 Languages](https://aclanthology.org/2021.acl-long.351/) | Çok düşük kaynakta basit continued pretraining güçlü baseline olabilir | Karmaşık yöntemden önce temiz CPT baseline |
| [Breaking Language Barriers](https://aclanthology.org/2024.emnlp-main.441/) | CPT daha hızlı yakınsar; transfer ölçek ve dil özelliklerinden etkilenir; replay forgetting'i azaltabilir | Veri/model ölçeğini ve EN replay'i kontrollü faktör olarak ele al |
| [Arabic Stable LM](https://arxiv.org/abs/2412.04277) | Türkçe listelenmeyen StableLM2'yi yeni bir dile adapte eder | StableLM2'nin sınırlı karşılaştırma adayı olmasına dayanak |
| [Sherkala-Chat](https://openreview.net/forum?id=wRcTCcb0H5) | Kazakça CPT'de dil karışımı ve tokenizer genişletmesi önemlidir | Tokenizer fertility ve mix kararını sonuçtan önce denetle |
| [DIPLomA](https://aclanthology.org/2025.findings-emnlp.1355/) | Dil CPT'si ile instruction davranışını ayrı aşamalar/delta merging ile ele alır | Base vs instruction aşamasını karıştırma; alignment extension olarak kalsın |

Bu tablo başlangıç sentezidir. Nihai execution contract'tan önce her çalışmanın exact model stage,
tokenizer, veri dozu, objective, replay oranı ve evaluation ölçümü ayrı literature matrix'e
çıkarılmalıdır.

## 10. Aşamalı yürütme planı

151at'ın vngrs redirect düzeltmesi bu bilimsel aşamaların yerine geçmez. Commit
`de4a14e3370326173bdf04ce33356aae7826ddda` yerelde doğrulanmış fakat yayımlanmamıştır. Gelecekteki
ayrı bir vngrs route-feasibility yetkisi; ordinary non-force push, korunmuş HU dirty-state
yeniden doğrulaması, güvenli `merge --ff-only`, preflight ve tek bounded execution zincirini açıkça
kapsamalıdır. Bu operasyonel alt kapı geçse bile aşağıdaki model, corpus-quality ve measurement
kapıları ayrıca geçilmeden training açılamaz.

### Aşama 0 — Literatür ve provenance paketi

**İşler**

- Yukarıdaki model kartlarını revision bazında kaydet.
- Turkish/Arabic/Kazakh/unseen-language CPT çalışmalarından karşılaştırmalı recipe tablosu çıkar.
- Tiny–Medium Turkish BERT, Turkish tokenizer, cosmosGPT ve SindBERT çalışmalarından model stage,
  corpus bileşimi, tokenizer, objective, doz ve ölçüm bilgilerini ayrı satırlarda çıkar.
- HPLT, FineWeb2, CulturaX-tabanlı Türkçe çalışma ve Bella Turca için “public candidate” ile
  “doğrudan küçük-model precedent'i” ayrımını açıkça işaretle.
- Kumru `500 GB / 300B` ile yayımlanmış korpus `84.9 GB / 25.33B` farkını kaynak üzerinden çöz.
- Alican Kiraz modelleri ve datasetlerini CPT, SFT, evaluation olarak ayrı sınıflandır.

**Çıkış kapısı**

- En fazla üç English-centric base aday;
- bir Qwen pozitif kontrol;
- her biri için doğrulanmış stage, lisans, data-language iddiası.

### Aşama 1 — Read-only/ucuz model ve korpus audit'i

**İşler**

- Tokenizer fertility ve M0 EN/TR PPL.
- Küçük Turkish capability baseline.
- `vngrs-web-corpus`, Turkish OSCAR/mC4, HPLT ve erişilebilirse CulturaX-tabanlı adaylar için
  metadata, lisans ve küçük stratified sample denetimi; FineWeb2/Bella Turca için önce metadata
  ve erişim feasibility kontrolü.
- Her adayın paper'daki corpus kimliği ile bugünkü exact revision/snapshot'ını ayrı kaydet.
- Sentetik subject/object contamination scanner tasarımı.

**Çıkış kapısı**

- En az bir modelde Türkçe headroom var;
- en az bir korpus lisans/provenance/kalite bakımından uygulanabilir;
- train/eval overlap kontrol edilebilir.

### Aşama 2 — Sınırlı M1 ekranı

**İşler**

- 500 fact, aynı donmuş population/evaluator.
- En fazla iki recipe.
- Factual robustness + EN retention + Türkçe başlangıç headroom'u birlikte raporla.

**Çıkış kapısı**

- Bir English-centric base model seçilir ve ikinci seed ile doğrulanır.
- Hiçbiri kullanılabilir M1 üretmezse model fishing yapılmaz; Qwen ana kontrol olarak kalır ve tez
  sorusunun “multilingual initialization” koşulu açıkça kabul edilir.

### Aşama 3 — Factsiz Türkçe dose pilotu

**İşler**

- Seçilen M1 üzerinde yalnız M2-A koşulları.
- Önceden dondurulmuş dose ladder.
- Türkçe PPL/capability ve EN PPL/factual retention.

**Çıkış kapısı**

- Türkçe PPL açıkça iyileşmeli;
- en az bir bağımsız Türkçe yetenek ölçümünde gelişme olmalı veya sıfır sonucun neden güvenilir
  olduğu önceden tanımlanmalı;
- İngilizce/M1 retention guardrail içinde kalmalı.

Bu kapı geçmezse M2-B başlatılmaz; önce corpus, tokenizer, objective veya dose tasarımı literatüre
göre yeniden değerlendirilir.

### Aşama 4 — Donmuş 2.500-fact M2-A/M2-B ana ailesi

**İşler**

- İki replike M1 seed zinciri.
- Her seed için aynı M1'den kardeş M2-A ve M2-B.
- Eşit token/update ve tek sabit endpoint.
- Her state'te aynı PPL, Turkish capability ve factual evaluation.

**Birincil sonuç**

- TR→EN M2-B − M2-A paired farkı ve önceden dondurulmuş belirsizlik ölçümü.

**İkincil sonuçlar**

- M2-A transfer değişimi;
- TR→TR;
- EN→EN retention;
- Türkçe PPL/capability kazanımı;
- relation/form bazlı robustness.

### Aşama 5 — Ölçek veya ikinci model kararı

25.000 fact ancak şu sorulardan birini yanıtlayacaksa açılır:

- 2.500 factteki etki fact sayısıyla ölçekleniyor mu?
- pozitif/negatif sonuç daha geniş subject havuzunda korunuyor mu?
- model ailesi sonucu değiştiriyor mu?

Mekanizma kurulmadan 25.000 fact çalıştırmak identifiability sorununu çözmez ve öncelik değildir.

## 11. Açık kararlar — sonuç görülmeden önce dondurulmalı

1. Ana English-centric model: OLMo, Pythia veya Falcon?
2. Qwen yalnız kontrol mü, ikinci tam zincir mi?
3. Ana korpus: audit edilmiş `vngrs-web-corpus`, Turkish OSCAR/mC4, HPLT, FineWeb2,
   CulturaX-tabanlı corpus, Bella Turca veya bunlardan kontrollü bir karışım mı?
4. Wikipedia karışımdaki payı ne olmalı?
5. Full-weight CPT, LoRA veya karşılaştırmalı tek bir adaptation yöntemi mi?
6. Tokenizer değişmeden mi kalacak; extension bilimsel değişken olacak mı?
7. English replay kullanılacak mı; kullanılırsa iki M2 kolunda aynı oran mı?
8. Dose ladder ve seçme kuralı tam olarak nedir?
9. Türkçe capability paketindeki base-compatible görevler hangileridir?
10. M2-B'de bütün 2.500 fact mi yoksa önceden belirlenmiş subset mi tekrar edilecek?
11. Primary threshold/CI ve seed-level replication kararı nedir?

Bu kararlar factual M2-A/M2-B sonuçları görülmeden ayrı bir frozen execution document'ta
kilitlenmelidir.

## 12. Şu anda yapılacak ilk yedi iş

1. OLMo-2-1B, Pythia-1.4B, Falcon-RW-1B ve Qwen için revision-level model provenance manifesti.
2. Bu dört tokenizer üzerinde aynı Türkçe/İngilizce sample ile fertility raporu.
3. CETVEL/TurkBench/TurkishMMLU içinden base-model uygun küçük manipulation-check paketi seçimi.
4. `vngrs-web-corpus`, Turkish OSCAR/mC4, HPLT, FineWeb2, CulturaX-tabanlı corpus ve Bella Turca
   için lisans, revision, dosya, language-ID, dedup, domain ve paper-precedent audit matriksi.
5. Kumru/MODA/VBART/TURNA ile Tiny–Medium BERT, cosmosGPT, SindBERT ve
   Arabic Stable LM/Sherkala/DIPLomA recipe matrix'i.
6. En fazla üç yeni aday için eşit-bütçeli 500-fact M1 screening contract'ı.
7. M1 adayı seçildikten sonra, factsiz Türkçe dose pilotunun frozen contract'ı.

İlk beş iş training gerektirmez. Altıncı ve yedinci işler ancak audit çıktılarıyla ayrı ayrı
yetkilendirilmelidir.

## 13. Durdurma koşulları

Yeni training başlatma, eğer:

- modelin base/instruct stage'i veya revision'ı belirsizse;
- “English-only/Turkish unseen” iddiası kaynakla desteklenemiyorsa;
- corpus lisansı, revision'ı, hash'i veya evaluation overlap'i çözülmemişse;
- target fact contamination bulunuyorsa;
- M2-A/M2-B token ve update bütçeleri eşleşmiyorsa;
- Türkçe capability/PPL manipulation check önceden dondurulmamışsa;
- output/cache/log pathleri HU home'a çözülüyorsa;
- checkpoint selection factual treatment sonuçlarına göre yapılacaksa.

## 14. Başarı tanımı

Yeni rota “en yüksek benchmark skoru” ile değil, aşağıdaki kanıt zinciriyle başarılı sayılır:

1. Kaynak modelin training stage'i ve dil provenance'ı dürüstçe belgelenmiştir.
2. M1 İngilizce olguları yeterince öğrenmiştir.
3. M2-A Türkçe dil modellemesini gerçekten geliştirmiştir.
4. M2-A ve M2-B arasındaki tek ana fark factual re-exposure'dır.
5. İki kola aynı testler uygulanmıştır.
6. Sonuç pozitif, negatif veya sıfır olsa da transfer ile relearning hakkında tanımlı bir estimand
   verir.
7. Seçilen corpus yalnızca paper-backed olmakla kalmaz; exact snapshot, lisans, kalite,
   contamination ve evaluation ayrımı reproducible biçimde belgelenmiştir.

Bu şartlar sağlanırsa, sonuç “süper iyi” olmak zorunda değildir; bilimsel olarak yorumlanabilir
olması yeterlidir.
