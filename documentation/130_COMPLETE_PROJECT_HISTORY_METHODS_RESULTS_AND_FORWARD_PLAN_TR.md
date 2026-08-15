# 130 - Projenin Tam Tarihi, Yöntemler, Sonuçlar ve İleriye Dönük Plan

**Tarih:** 30 Temmuz 2026  
**Dil:** İngilizce ana belgenin Türkçe eşlik eden sürümü  
**Amaç:** Kişisel milestone değerlendirmesi, bütüncül bilimsel sentez ve bölüm bölüm supervisor sunumu  
**Durum:** Doküman 129 ve sonrasındaki dış değerlendirmeye kadar mevcut kanıtı ve geçici önerileri sentezler; yeni deney yetkilendirmez  
**Operasyonel otorite:** Tarihli düzeltmeleriyle birlikte `AGENTS.md` ve Doküman 100  

## 1. Amaç ve okuma rehberi

Bu belge, tez projesini ilk bilimsel motivasyondan en güncel Qwen ve SmolLM sonuçlarına kadar
yeniden kurar. Üç amaç taşır:

1. nelerin geliştirildiğini, denendiğini, öğrenildiğini, reddedildiğini ve korunduğunu milestone
   düzeyinde kaydetmek;
2. başarısız ve superseded sonuçları gizlemeden projenin bilimsel durumunu değerlendirmek;
3. supervisor'a birbirinden bağımsız bölümler halinde sunulabilecek bir kaynak oluşturmak.

Bu bir sentezdir; kronolojik kanıt kaydının yerine geçmez. Tam komutlar, Slurm dökümleri, artifact
yolları ve hash'ler numaralı raporlarda korunmaktadır. Ana İngilizce kaynak
`130_COMPLETE_PROJECT_HISTORY_METHODS_RESULTS_AND_FORWARD_PLAN_EN.md` dosyasıdır.

Kaynak önceliği şöyledir:

1. açık kullanıcı ve supervisor kararları;
2. `AGENTS.md` ve Doküman 100'ün son tarihli düzeltmeleri;
3. en yeni numaralı sonuç ve handoff belgeleri;
4. dondurulmuş manifestler ve repository kanıtı;
5. bilimsel çerçeve olarak Exposé;
6. tarihsel bağlam olarak eski Notion notları.

## 2. Yönetici özeti ve milestone değerlendirmesi

Tez, Türkçe adaptasyondan sonra Türkçe üzerinden erişilebilir hale gelen olgusal bilginin daha
önce İngilizcede edinilmiş bilgiye cross-lingual erişim mi, yoksa Türkçe adaptasyon verisindeki
tekrar nedeniyle reaffirmation/relearning mi olduğunu sorar.

Proje bu son nedensel soruyu henüz yanıtlamamıştır. Yeni seçilmiş Qwen artifact'leriyle M2 ve M3
çalıştırılmamıştır. Buna karşılık proje, sorunun yorumlanabilir biçimde sınanması için gereken
metodolojik ve ampirik zemini kurmuştur.

Ana milestone şudur:

> Qwen2.5-1.5B, aynı 500-subject/2.500-fact Relation V2 popülasyonunda frozen ara-ölçek İngilizce
> M1 acquisition kontratını iki bağımsız seed'de geçmiştir. Seçilen checkpoint'ler canonical
> acquisition, prompt-robust retrieval, relation binding, generic integrity ve WikiText-2 PPL
> retention'ı birlikte sağlamaktadır.

Eşlik eden negatif sonuç da aynı ölçüde önemlidir:

> SmolLM2-1.7B kusursuz canonical storage ve kabul edilebilir generic retention elde edebilmekte,
> fakat en iyi prompt-consistency remediation'ı %55,8 eight-cell robust retrieval'da kalmakta ve
> frozen %70 global/per-relation gate'ini geçememektedir.

Sonuç olarak:

- Qwen tek replikeli ara-ölçek İngilizce M1 adayıdır;
- SmolLM ikinci başarılı causal model olarak değil, değerli bir negatif karşılaştırma olarak
  korunmalıdır;
- eski Türkçe bridge pilotu geçerli negatif feasibility kanıtıdır, fakat eski M1 durumlarını
  kullandığından yeni Qwen artifact'lerinin sonucuna doğrudan taşınamaz;
- sonraki savunulabilir adım yeni bir bilingual Qwen kontratını dondurmak, pre-adaptation
  baseline'larını yeniden ölçmek ve ancak sonra kontrollü M2/M3 açmaktır;
- 2.500-fact causal bridge'in 25.000-fact canonical M1'den önce gelmesi şimdilik güçlü bir öneri,
  supervisor onayı alınmış kesin bir karar değildir.

## 3. Araştırma sorusu ve nedensel mantık

### 3.1 Temel soru

> Türkçeye adapte edilmiş bir model bir fact'i Türkçe üzerinden retrieve ettiğinde, İngilizcede
> önceden edinilmiş bilgiye mi erişmektedir, yoksa fact'i Türkçe exposure'dan yeniden mi
> öğrenmiştir?

Türkçe factual performance artışı tek başına transfer kanıtı değildir. Hedef fact Türkçe
adaptasyon verisinde bulunuyorsa doğru cevap relearning olabilir. Bu nedenle exposure geçmişi
denetlenebilen sentetik subject--relation--object binding'leri kullanılır.

### 3.2 Özgün M0--M3 tasarımı

| Durum | Müdahale | Bilimsel rol |
|---|---|---|
| M0 | Sentetik acquisition olmayan pinned base model | Target binding'lerin başlangıçta bulunmadığını doğrular |
| M1 | Yalnız İngilizce sentetik factual acquisition | İngilizce factual memory'yi kurar |
| M2 | Target fact tekrarı olmayan temiz generic Türkçe adaptasyon | Transfer/cross-lingual access değişimini ölçer |
| M3 | Branch B fact repetition içeren budget-matched Türkçe adaptasyon | Reaffirmation/relearning'in ek etkisini ölçer |

Tüm Türkçe kollar aynı frozen M1'den bağımsız başlamalıdır. M3, M2'nin devamı olamaz. Branch A ve
B M1'de aynı İngilizce acquisition'ı alır; branch etiketi yalnız daha sonraki Türkçe exposure'ı
belirler.

### 3.3 Rafine nedensel tasarım

Sonraki planlarda üçlü bir ayrım geliştirilmiştir:

- **M2-clean:** temiz generic Türkçe adaptasyon;
- **M3-lexical:** doğru binding olmadan Branch B entity ve label exposure'ı;
- **M3-fact:** doğru Branch B fact'lerinin exposure'ı.

Bu yapı generic adaptasyon, entity/lexical alignment ve gerçek factual re-exposure etkilerini
ayırabilir. Basit M2/M3 tasarımı da mümkündür; hangi tasarım seçilirse seçilsin training'den önce
dondurulmalıdır.

### 3.4 Cevap dili: korunan hedef ve açık metodolojik karar

Exposé, Türkçe prompt'a Türkçe object ile cevap verilmesini örnekler:

```text
TR prompt -> TR object
```

Bu, tezin doğal end-to-end çıktısıdır. Bridge çalışmaları ayrıca şunu ölçmüştür:

```text
TR prompt -> EN object
```

TR-to-EN, Türkçe lexicalization/translation yükünü azaltarak İngilizcede edinilmiş object'e erişimi
daha temiz test edebilir. Son dış görüş bu yönü primary access metriği, TR-to-TR'yi secondary
end-to-end metrik olarak önermektedir. Bu değerli bir öneridir fakat Exposé'yi değiştiren onaylı
karar değildir. Şimdilik iki sonuç ayrı tutulmalı, tek bir bilingual-correct skorda
birleştirilmemeli ve primary/secondary sırası Max'in görüşünden sonra dondurulmalıdır.

## 4. Veri tasarımı ve evrimi

### 4.1 Neden sentetik fact?

Gerçek dünya bilgilerinin hangi dilde ne zaman görüldüğü bilinmez. Sentetik binding'ler şunları
sağlar:

- exposure dili ve zamanının kontrolü;
- repetition frequency'nin bilinmesi;
- dengeli Branch A/B ataması;
- relation, name ve frequency alt-grup analizi;
- training/probe form ayrımı;
- contamination taraması;
- manifest ve hash ile reproducibility.

M0 direct ve QA top-1 yaklaşık 0,006 ile chance düzeyindedir. Bu, binding'lerin base modelde
erişilebilir olmadığını ve QA scaffold'un yapay baseline avantajı üretmediğini destekler.

### 4.2 Canonical popülasyon

- 5.000 sentetik subject;
- 2.500 Branch A ve 2.500 Branch B;
- subject başına beş fact;
- toplam 25.000 fact;
- branch başına 12.500 fact.

Relation'lar:

1. `profession`;
2. `born_in`;
3. `lives_in`;
4. `field_of_study`;
5. `works_in_industry`.

### 4.3 Relation V1'den V2'ye

V1'deki `studied_at` ve `works_at`, proper-name-heavy inventory'leri nedeniyle belirli adaylara
collapse üretti. Bunlar dengeli ve bağımsız atanmış `field_of_study` ve `works_in_industry` ile
değiştirildi. Elli field ve elli industry adayı global/blok dengesi ve düşük çapraz bağımlılıkla
atandı. Araştırma sorusu değişmedi; identifiability iyileşti.

### 4.4 Acquisition ladder

| Düzey | Subject | Fact | Amaç |
|---|---:|---:|---|
| Micro | 10 | 50 | Pipeline ve feasibility |
| Recipe pilot | 100 | 500 | Kontrollü diagnosis/ablation |
| Ara ölçek | 500 | 2.500 | Capacity, binding ve interference |
| Üst canonical | 5.000 | 25.000 | Tarihsel tam Branch A/B popülasyonu |

2.500 fact ile branch başına 2.500 subject aynı şey değildir ve her zaman açıkça etiketlenmelidir.

## 5. Değerlendirme metodolojisi

### 5.1 Candidate ranking

Evaluator, aynı prompt altında relation inventory'sindeki tüm adayları skorlar. Primary skor mean
answer-token log probability, total log probability sensitivity metriğidir. Böylece spelling ve
free-generation normalization sorunları azaltılır.

Candidate ranking open-ended generation ile aynı değildir. İddialar frozen candidate'lar
arasındaki factual access ile sınırlandırılmalı; generation ikincil integrity kontrolü olarak
kullanılmalıdır.

### 5.2 Storage ve retrieval ayrımı

- **Exact-prefix:** training'e yakın canonical completion;
- **Direct:** scaffold-free held-out soru;
- **QA:** held-out Question/Answer scaffold;
- **Triple robust:** aynı fact için exact, direct ve QA'nın tümünde top-1.

Son evaluator Forms A/B/C/D'yi direct ve QA altında test eder. En güçlü mevcut fact-level ölçüm,
aynı fact'in sekiz hücrenin tamamında doğru olmasını gerektiren **eight-cell robust intersection**
metriğidir.

### 5.3 Relation binding

`born_in` ve `lives_in` aynı city inventory'sini bilinçli olarak paylaşır. Model iki şehri
hatırlayıp yanlış relation'a bağlayabilir. Same-subject forced choice ve city-swap oranları bu
nedenle korunmalıdır.

### 5.4 Generic retention ve integrity

- WikiText-2 PPL ve trained/base ratio;
- common-knowledge ranking;
- generic completions;
- EOS/empty/repetition kontrolleri;
- synthetic-subject intrusion.

| PPL oranı | Yorum |
|---:|---|
| `<=1.10` | Bu kontrolde material degradation yok |
| `>1.10` ve `<=1.25` | Ölçülebilir drift; trade-off incelenmeli |
| `>1.25` | Material generic-loss degradation flag |

### 5.5 Checkpoint seçme disiplini

Kural “en iyi görünen checkpoint” değildir:

> Tüm frozen factual, cell, relation, integrity ve PPL gate'lerini geçen en erken checkpoint'i
> seç.

Qwen step-75/step-50 yorumunun güvenilirliği bu kurala dayanır. M2 ve M3 için de Türkçe factual
sonuçlara bakarak treatment-specific checkpoint seçilmemelidir.

## 6. Kronolojik deney tarihi

### 6.1 Phase 0: altyapı, evaluator ve M0

Ayrı data/training repository'leri, pinned model/dataset artifact'leri ve relation-aware candidate
scoring kuruldu. Negatif M0 sonucu, sonraki başarının pre-existing association olmadığını
doğruladı.

### 6.2 Phase 1: erken geniş M1 recipe araması

#### GPT-2 continued pretraining

`5e-5`/1 epoch, `1e-4`/1 epoch ve `5e-5`/3 epoch denendi. Direct/QA yaklaşık %2, en iyi overlap
yaklaşık 5/500 kaldı. Fazla epoch çözüm olmadı.

#### SmolLM, repetition ve QA mix

SmolLM2-360M, erken 1.7B denemesi, daha yüksek repetition, QA mix ve uzun exposure aynı tavanı
kıramadı. Salt model boyutu ve exposure yeterli değildi.

#### Biography + QA

Tüm fact'leri doğal biography bağlamında göstermek ve QA eklemek direct 8/500, QA 11/500,
overlap 3/500 verdi. Metinde bulunmak, relation sorusu altında robust retrieval demek değildi.

#### Two-stage acquire/extract

Biography acquisition ve QA extraction aşamaları ayrıldı. Answer-only Stage B2 loss'u düşürdü,
fakat direct 6/500, QA 6/500, overlap 2/500 kaldı.

#### High exposure, ranking ve binding mix

High-exposure baseline ilerleme sağlamadı. İlk ranking küçük sinyal verdi, follow-up geriledi.
Multi-view biography, QA ve relation-aware option'lar içeren binding mix bile direct 7/500,
QA 11/500, overlap 3/500'de kaldı.

#### Temel ders

Geniş recipe araması, tek-fact feasibility çözülmeden yapılmıştı. Düşük loss, daha fazla exposure,
zengin metin ve büyük model robust factual access için yeterli değildi.

### 6.3 Phase 2: acquisition ladder ve direct supervision

İlk 50-fact gate exact 12/50, direct 1/50, QA 11/50 ve overlap 1/50 verdi. Tek-fact diagnostic'te
`Augusta Rodriquez -> born_in -> Van`, exact ve QA'de rank 1, direct'te rank 4'tü. Fact tamamen
yok değildi; erişim yolu form-dependent idi.

İki direct training paraphrase'i eklenip üçüncü form held-out tutulunca exact/direct/QA ilk
checkpoint'ten itibaren rank 1 oldu. Direct margin -1,513'ten +3,566'ya çıktı.

Sonra:

- 10 `born_in` fact: 10/10 exact/direct/QA/overlap;
- 50 fact, beş relation: 50/50 exact, 48/50 direct, 49/50 QA, 48/50 overlap.

Bu ilk ikna edici acquisition başarısıydı. Prompt-format coverage ve answer-only supervision'ın
kritik olduğu gösterildi.

### 6.4 Phase 3: V1 scale, Relation V2 ve interference

#### V1, 500 fact

| Metrik | Sonuç |
|---|---:|
| Exact | 451/500 |
| Direct | 317/500 |
| QA | 349/500 |
| Overlap | 277/500 |
| Triple robust | 265/500 |

`studied_at` ve `works_at` yalnız 29/100 ve 24/100 robust verdi. Ranking continuation baseline'i
geçmedi.

#### V2 micro ve city kontrolleri

V2 50-fact gate 50/50 exact ve 45/50 robust verdi; iki yeni relation 10/10 oldu. Kalan hata
`lives_in` için birthplace seçilmesiydi. Paired-city CLM sonucu 45/50'den 44/50'ye düşürdü;
hard-negative continuation metric-neutral kaldı. Seen contrast, held-out relation rolüne
genellenmedi.

#### V2, 500 fact

| Metrik | Sonuç | Gate |
|---|---:|---:|
| Exact | 500/500 | 450/500 |
| Direct | 378/500 | 400/500 |
| QA | 377/500 | 400/500 |
| Overlap | 329/500 | 350/500 |

V1'e göre büyük iyileşme sağlandı fakat frozen gate geçilmedi.

#### Exploratory V2, 2.500 fact

- exact 2.498/2.500 (%99,92);
- direct 1.249/2.500 (%49,96);
- QA 1.293/2.500 (%51,72);
- overlap 958/2.500 (%38,32).

Exact sabit kalırken overlap 500 fact'teki %65,8'den %38,3'e düştü. Bu, storage ile robust
retrieval'ın ayrıldığını ve fact-density interference bulunduğunu gösterdi.

### 6.5 Phase 4: 1.7B capacity ve supervisor follow-up

SmolLM2-1.7B basit 500-fact direct/QA plateau'sunu büyük ölçüde çözdü:

| Run | Exact | Direct | QA | Robust |
|---|---:|---:|---:|---:|
| Seed 42 | 500 | 499 | 498 | 497 |
| Seed 43 | 500 | 500 | 499 | 499 |

Fakat PPL ratio 1,194 ve 1,173 oldu ve generic completions'da aşırı EOS davranışı görüldü.

Frozen hard evaluation A/B dört hücrede 466/500 ve 457/500 verdi. Form C daha zor, `lives_in`
swap'leri baskındı.

Counterbalance/swap deneyinde:

- seen form %100;
- crossed %39,0 ve %38,8;
- novel C %46,3 ve %47,8;
- dört-hücre robust %28,0 ve %28,4;
- gate %70.

Swap sonrası failure tekrarlandığından sorun subject split değil subject-specific form exposure idi.

Joint relation control %99,4 seen, %46,5 crossed, %68,4 novel, %32,5 robust ve %93,7 forced
choice verdi. Relation identity büyük ölçüde temsil ediliyor, fakat open-ended access wording'e
bağımlı kalıyordu.

LR/EOS ablation sonucu:

| Seed | EOS | Hard | Robust | Exact | PPL ratio | EOS ending |
|---:|---|---:|---:|---:|---:|---:|
| 42 | true | %74,1 | %46,9 | %100 | 1,077 | 27/30 |
| 42 | false | %77,9 | %52,4 | %100 | 1,082 | 0/30 |
| 43 | true | %73,1 | %44,5 | %100 | 1,076 | 27/30 |
| 43 | false | %76,2 | %50,1 | %100 | 1,084 | 0/30 |

EOS supervision stopping bias'ın replikeli nedeniydi. Seçilen Pareto recipe bu bias'ı giderdi,
fakat %70 robust gate'in altında kaldı; M2 HOLD kararı doğruydu.

### 6.6 Phase 5: form remediation ve model-family screen

Balanced A+B question-only müdahalesi trained hücreleri %100 yaptı; held-out C/D %46,6--62,4,
exact %9,4, robust %11,8 ve PPL ratio 1,041 kaldı.

Canonical+A/B hybrid %100 exact/A-B, %75,05 held-out C/D, %39,6 robust ve PPL ratio 1,080 verdi.
Storage ile retention birlikte çözüldü, unseen access çözülmedi.

| Model | Exact | Robust global/min | PPL ratio | Karar |
|---|---:|---:|---:|---|
| SmolLM2-1.7B | %100 | %39,6 / %21 | 1,080 | Robustness failure |
| Qwen2.5-1.5B | %100 | %99,6 / %99 | 1,461 | Yalnız retention failure |
| StableLM2-1.6B | %100 | %93,8 / %69 | 1,477 | Cell/relation/PPL failure |
| Gemma-2-2B | %97,8 | %78,0 / %7 | 704,873 | Bu recipe kombinasyonu başarısız |
| Llama-3.2-1B | %100 | %81,4 / %7 | 3,862 | Cell/relation/PPL failure |

Qwen robust retrieval'ın mümkün olduğunu gösterdi fakat PPL drift yüksekti. Early stopping çözüm
olmadı: update 25 PPL 1,409 iken factual gate'i kaçırdı; ilk factual-pass update 50'de PPL 1,455'ti.

### 6.7 Phase 6: Türkçe corpus ve ilk bridge pilotu

Haziran 2026 Türkçe Wikipedia dump'ı checksum-verified, normalize, deduplicate, contamination-scan,
split ve manual-review süreçlerinden geçirilip donduruldu:

- 505.016 deduplicated document;
- 504.287 clean retained;
- 729 conservative removal;
- 494.253 train ve 10.034 validation;
- sıfır retained synthetic full-name match.

Bridge M0/M1/low/full durumlarında EN-to-EN, TR-to-EN, TR-to-TR ve PPL ölçtü.

SmolLM'de EN-to-EN %96,66'dan %96,10'a yakın kaldı ve Türkçe PPL 10,778'den 9,426'ya iyileşti;
TR-to-EN %20,61'den %16,99'a düştü.

Eski Qwen'de EN-to-EN %100 kaldı ve Türkçe PPL 22,007'den 13,378'e iyileşti; fakat TR-to-EN
%66,20'den %46,48'e düştü.

Generic Türkçe adaptation gerçek bir language-model etkisi yarattı, fakat factual access'i
açmadı; hatta Qwen'de bozdu. Bu geçerli negatif feasibility kanıtıdır, yeni Qwen artifact'lerinin
nihai sonucu değildir.

### 6.8 Phase 7: Qwen clean-English replay ve seed-instability

Clean-English replay coefficient 0,5 ile Qwen retention hedeflendi. Seed-42 replay step 50:

- %99,8 exact;
- %98 global robust;
- %91 minimum relation;
- PPL ratio 1,24684.

`navigation` + EOS yanıtını <=2 token diye empty sayan heuristic literal failure üretti. Orijinal
sonuç korunarak lexical-content tabanlı ayrı adjudication yapıldı.

100-subject recipe seed 43'te tam replikasyon vermedi. Step 50 retention'ı geçti ama minimum C/D
%72 kaldı; step 75 factual gate'leri geçti fakat PPL ratio 2,755 oldu. Ortak passing checkpoint
yoktu ve bu gerçek scientific failure olarak korundu.

### 6.9 Phase 8: Qwen 2.500-fact scale ve bağımsız replikasyon

Exploratory scale diagnostic model, V2 popülasyon, hybrid curriculum, replay coefficient, 252
update, evaluator, gate ve selection rule'u sabit tuttu.

Seed-42'de step 50/75 factual başarı ve düşük PPL'i birleştirdi; step 100 sonrasında factual skorlar
yüksek kalırken PPL hızla bozuldu ve finalde yaklaşık 28 katına ulaştı.

Seed-43 aynı frozen kontratı geçti:

| Metrik | Seed 42, step 75 | Seed 43, step 50 |
|---|---:|---:|
| Exact | %99,96 | %99,68 |
| Hard | %99,29 | %99,225 |
| Eight-cell robust | %96,08 | %96,20 |
| Min robust relation | %88,2 | %90,2 |
| Forced choice | %99,51 | %99,56 |
| PPL/base | 1,082 | 1,032 |
| Generic top-1 | 29/30 | 29/30 |
| Synthetic intrusion | 0 | 0 |

İki artifact manifest ve SHA-256 ile scratch'ta donduruldu. Bu en güçlü pozitif sonuçtur; 25.000
fact scale veya Türkçe causal sonuç değildir.

### 6.10 Phase 9: SmolLM contrastive ve consistency karşılaştırması

| Koşul | Exact | Hard | Robust | Min relation | Forced | PPL |
|---|---:|---:|---:|---:|---:|---:|
| `lambda=0` | %100 | %87,525 | %39,6 | %21 | %89,4 | 17,1980 |
| `lambda=0.10` | %100 | %91,00 | %52,2 | %34 | %93,1 | 17,5234 |
| `lambda=0.25` | %100 | %90,975 | %50,4 | %32 | %94,1 | 17,5521 |

Relation-matched discrimination doğru yönde 12,6 puan robust artış sağladı; coefficient artırmak
çözüm olmadı.

Son A/B distribution-consistency müdahalesinin en iyi step-250 sonucu:

- exact %100;
- hard %91,67;
- robust %55,8;
- min relation %38;
- forced %94,0;
- PPL ratio 1,099;
- empty/intrusion 0.

Önceki %52,2'yi iyileştirdi fakat global gate'i 14,2, per-relation gate'i 32 puan kaçırdı.
SmolLM dalı seed-43 ve scale-up olmadan doğru biçimde kapatıldı.

## 7. Yöntemler arası karşılaştırma

| Yöntem | Hedeflenen mekanizma | Sonuç | Ders |
|---|---|---|---|
| Fazla epoch/LR/repetition | Exposure artırma | Robust artış yok | Exposure tek başına yetmez |
| QA/biography | Doğal context/extraction cue | Düşük held-out retrieval | Metinde bulunmak robust binding değildir |
| Two-stage | Storage ve querying'i ayırmak | Loss düştü, retrieval düşük | Loss factual access değildir |
| Direct-aware | Eksik prompt family'yi kapsamak | 1/10/50-fact ladder çözüldü | Prompt coverage kritik erken bottleneck idi |
| Relation V2 | Candidate collapse'ı azaltmak | Büyük iyileşme | Data identifiability önemlidir |
| City contrast/negative | Same-subject city rollerini ayırmak | Fail/neutral | Seen contrast role transfer değildir |
| 1.7B capacity | Interference azaltmak | Basit 500-fact retrieval çözüldü | Capacity önemli, hard forms yine gerekli |
| EOS removal | Short-answer bias'ı kaldırmak | Replikeli iyileşme | EOS supervision causal etkendi |
| Balanced A/B | Birden çok seen form öğretmek | Seen perfect, unseen weak | Coverage invariance değildir |
| Canonical+A/B | Storage ve form diversity | Storage/PPL pass, robust fail | Memory ve binding ayrıdır |
| Cross-family | Model-family Pareto farkı | Qwen robust/drift; Smol retained/fragile | Aile seçimi sonucu değiştirir |
| English replay | Qwen retention | Passing scale checkpoint'leri | Retention data ana Qwen kusurunu düzeltti |
| Contrastive ranking | Object discrimination | %39,6 -> %52,2 | Mekanizma doğru yönde, yetersiz |
| Distribution consistency | Seen prompt alignment | %55,8 | Seen consistency unseen invariance değildir |

## 8. Operasyonel ve reproducibility milestone'ları

### 8.1 HU home storage incident

13 Temmuz'da shared HU home üzerinde yaklaşık 474 GB artifact birikmiş ve servis kesintisine
katkıda bulunmuştu. Checkpoint, optimizer, cache ve evaluation tree'leri scratch'a taşındı; bilimsel
sonuç silinmeden home regular-file kullanımı 7,88 GiB'a indirildi.

Kalıcı kural:

- home yalnız source, küçük config, manifest, hash ve compact summary;
- büyük artifact'ler `/vol/tmp` veya `/vol/tmp2`;
- her family için pre/post capacity, inode, resolved-path ve retention audit'i;
- selected artifact için cleanup öncesi manifest ve SHA-256.

### 8.2 Operasyonel failure'ların doğru sınıflandırılması

GPU contamination, OOM, stale preflight, tokenizer boundary, V1 schema assumption, checksum URL,
duplicated pattern match explosion ve evaluator aggregation sorunları yaşandı. Scientific contract
korunarak altyapı düzeltildi ve yalnız eksik işler yeniden yürütüldü. Operasyonel failure model
failure sayılmadı; scientific failure altyapı sorunu diye gizlenmedi.

### 8.3 Precommitment ve append-only correction

- V2 500-fact near-pass failure olarak kaldı;
- ilk 2.500-fact Smol run exploratory etiketini korudu;
- Qwen integrity düzeltmesi orijinal summary'yi overwrite etmedi;
- Qwen checkpoint'leri earliest-all-gates kuralıyla seçildi;
- başarısız SmolLM koşulları korundu;
- corpus ve selected models append-only manifestlerle donduruldu.

## 9. Şu anda desteklenen bilimsel sonuçlar

1. Base model sentetik binding'leri acquisition öncesinde chance üstünde retrieve etmiyor.
2. Canonical storage ve prompt-robust retrieval farklı yeteneklerdir.
3. Training loss ve exact tek başına learned factual access değildir.
4. Prompt coverage gerekli olabilir; A/B coverage C/D invariance sağlamaz.
5. Candidate design ve bağımsız assignment identifiability'yi etkiler.
6. Fact-density, storage'ı silmeden retrieval interference yaratabilir.
7. `born_in`/`lives_in` same-subject binding değerli hard diagnostic'tir.
8. Supervised final EOS replikeli stopping bias nedenidir.
9. Model family'leri farklı robustness/retention Pareto noktalarındadır.
10. Clean-English replay Qwen robust acquisition ile düşük PPL drift'i birleştirebilir.
11. Qwen 2.500-fact M1 frozen evaluator altında iki seed'de replikedir.
12. SmolLM contrastive müdahaleleri binding'i iyileştirir fakat causal eligibility gate'ine ulaşmaz.
13. Türkçe PPL iyileşmesi factual transfer anlamına gelmez.

## 10. Henüz desteklenmeyen iddialar

Henüz şunlar söylenemez:

- yeni Qwen artifact'leri altında clean Turkish adaptation transfer üretir;
- Turkish fact repetition ölçülmüş relearning increment üretir;
- Branch A/B DID hesaplanmıştır;
- 2.500-fact Qwen sonucu otomatik 25.000 fact'e ölçeklenir;
- bütün fact'ler universal prompt-independent veya open-generation robust'tur;
- SmolLM ikinci başarılı M1/M2/M3 modelidir;
- answer-language hierarchy ve final M2/M3 checkpoint rule onaylanmıştır.

## 11. 30 Temmuz 2026 mevcut durum

| İş kolu | Kanıt | Karar |
|---|---|---|
| Qwen M1, 2.500 fact | İki seed pass, artifact'ler frozen | Ana ara-ölçek aday |
| Qwen M1, 25.000 fact | Çalıştırılmadı | Açık scale kararı |
| Eski Turkish bridge | Negatif feasibility tamam | Yeni artifact'te baseline yeniden ölçülmeli |
| SmolLM ranking | Mekanistik pozitif, gate fail | Ana dal kapalı |
| SmolLM consistency V2 | Best robust %55,8 | Replication/scale yok |
| Türkçe corpus | Frozen ve hash'li | Kontrat incelemesiyle kullanılabilir |
| Yeni Qwen bilingual contract | Frozen değil | Training öncesi zorunlu |
| Ana M2/M3 | Çalıştırılmadı | HOLD |
| Aktif Slurm | Yok | İzleme/duplicate gerekmez |

## 12. Son dış görüşün değerlendirilmesi

Dış değerlendirme mevcut kanıtla büyük ölçüde uyumludur ve değerlidir. Şunları önerir:

- ara-ölçek Qwen M1'i causal feasibility için yeterli saymak;
- SmolLM ana model optimizasyonunu kapatıp negatif karşılaştırma olarak korumak;
- iki Qwen seed'i sibling causal chains olarak kullanmak;
- M2/M3 token ve update bütçelerini tam eşlemek;
- treatment-specific factual checkpoint selection yapmamak;
- TR-to-EN ile TR-to-TR'yi ayrı raporlamak;
- 25.000-fact M1'den önce bridge-first 2.500-fact feasibility yapmak;
- Branch A/B DID'yi korumak;
- M3'e ek token vermeyip neutral filler'ı factual rows ile değiştirmek.

Bu görüş projeyi sonsuz M1 optimizasyonundan tez sorusuna yönelttiği için ikna edicidir. Fakat
henüz otorite değildir. Max ile kararlaştırılması gerekenler:

1. bridge-first veya canonical-M1-first;
2. iki full causal chain veya discovery+confirmatory staging;
3. TR-to-TR veya TR-to-EN primary outcome;
4. M3-lexical kolunun gerekliliği;
5. adaptation endpoint/checkpoint kuralı;
6. ilk Türkçe dose'un ölçeği.

## 13. Supervisor görüşmesi için geçici ileri plan

Bu bölüm öneridir, execution authorization değildir.

### Adım 0: Max ile hizalan

Mail/görüşmede şu noktalar sunulmalı:

- replikeli Qwen 2.500-fact sonucu;
- SmolLM ana dalının kapanması ve negatif kanıt değeri;
- eski bridge uyarısı ve yeni baseline gereği;
- bridge-first/25.000-fact sıralaması;
- cevap dili ve seed-chain seçenekleri.

### Adım 1: Yeni bilingual kontratı dondur

- iki Qwen artifact'in replicate rolü;
- exact Türkçe corpus subset/hash;
- contamination exclusions;
- English/Turkish alias-candidate registries;
- EN-to-EN, TR-to-EN, TR-to-TR probes;
- A/B/C/D direct/QA ve relation floors;
- English/Turkish PPL ve integrity;
- token/update budget ve neutral filler;
- endpoint rule, estimands, stop conditions;
- compute/storage/retention.

### Adım 2: Güncel M1 baseline'larını yeniden ölç

İki artifact reload edilerek English M1 gate, üç dil yönü, relation/cell, forced choice, PPL ve
manifest/contamination kontrolü doğrulanmalı.

Düşük pre-adaptation Turkish retrieval tek başına stop değildir; transfer için headroom sağlar.
Tavana yakın retrieval ise analizi gain yerine preservation/degradation'a kaydırır.

### Adım 3: Onaylanırsa matched 2.500-fact causal family

```text
Qwen M1 seed 42 -> sibling M2-42 ve M3-42
Qwen M1 seed 43 -> sibling M2-43 ve M3-43
```

Her seed family içinde Turkish document order, adaptation seed, token/update, optimizer ve
checkpoint schedule sabit; yalnız factual exposure farklı olmalı.

Minimum tasarım:

- M2 = clean Turkish + neutral matched filler;
- M3 = aynı clean Turkish, neutral filler yerine factual rows.

Daha kontrollü tasarım M3-lexical ve M3-fact'i ayırır. Branch A hiç Turkish fact repetition almaz.

### Adım 4: Frozen endpoint ve causal estimands

M2/M3 checkpoint'leri Türkçe factual sonuca göre ayrı seçilmemeli. Fixed update veya treatment-blind
rule önceden dondurulmalı.

Ayrı raporlanmalı:

- Branch A/B için M1-to-M2;
- Branch A/B için M1-to-M3;
- M3-M2 DID;
- varsa lexical-clean ve fact-lexical increments;
- English retention ve generic PPL;
- relation/form/branch/name/frequency uncertainty;
- birleştirilmeden TR-to-EN ve TR-to-TR.

### Adım 5: 25.000-fact kararını kanıttan ver

Bridge-first yaklaşımı tezin katkısını doğrudan test eder. Mekanizma 2.500 fact'te ayrışmıyorsa
önce M1 scale büyütmek maliyeti artırır. İki seed'de çalışırsa 25.000-fact run scale robustness
veya final validation olabilir.

Supervisor canonical population'ı causal claim öncesinde şart koşarsa canonical-M1-first de
savunulabilir. Bu durumda 2.500-fact sonuç garanti değil güçlü ara-ölçek kanıt olarak sunulmalıdır.

### Adım 6: SmolLM'yi negatif comparative result olarak koru

Yeni deney ancak profession/C-D binding failure'ını doğrudan hedefleyen yeni bir mekanizma ve
Qwen causal line'ını geciktirmeyen ayrı araştırma sorusu varsa açılmalıdır.

Mevcut güçlü SmolLM sonucu:

> Perfect canonical storage ve düşük PPL drift, prompt-robust factual binding için yeterli değildir;
> mechanism-aligned contrastive improvement bile downstream eligibility eşiğinin altında kalabilir.

## 14. Yeni Türkçe aşama için önerilen stop conditions

Şu durumlarda ana causal family başlamamalı/devam etmemeli:

- selected Qwen artifact reload sonrası frozen M1 metriğini üretmiyorsa;
- corpus/filler contamination audit'inden geçmiyorsa;
- M2/M3 budget eşit değilse;
- output/cache/log/checkpoint HU home'a resolve oluyorsa;
- alias/prompt contract belirsizse;
- checkpoint Türkçe factual sonucu gördükten sonra seçilebiliyorsa;
- smoke catastrophic English loss veya broken evaluator gösteriyorsa;
- iki seed family seed kimliği dışında farklılaşıyorsa.

Düşük M1 Turkish retrieval ve mevcut kapasiteye sığan ağır scratch kullanımı otomatik stop değildir.

## 15. Validity threats ve yorum sınırları

- **Synthetic data:** Source control sağlar, doğal-world factuality'nin tamamını temsil etmez.
- **Candidate ranking:** Kontrollüdür, open-ended recall değildir.
- **Prompt family:** C/D holdout leakage'i azaltır, universal invariance kanıtlamaz.
- **Model/seed:** Pozitif sonuç iki-seed Qwen'dir, universal model-family claim değildir.
- **Scale:** Pozitif kanıt 500 subject/2.500 fact'tir, 5.000 subject/25.000 fact değildir.
- **Adaptation attribution:** Turkish PPL gain transfer değildir; matched M2/M3 ve frozen estimand gerekir.

## 16. Supervisor'a sunulabilir modüller

1. Motivasyon ve causal question: Bölüm 2--3.
2. Synthetic data ve dataset evrimi: Bölüm 4.
3. Factual learning ölçümü: Bölüm 5.
4. Erken yöntemler neden başarısız oldu: Bölüm 6.2--6.4.
5. Storage-retrieval keşfi: Bölüm 6.3--6.4.
6. EOS, capacity ve prompt dependence: Bölüm 6.5.
7. Model-family trade-off ve bridge uyarısı: Bölüm 6.6--6.7.
8. Replikeli Qwen milestone: Bölüm 6.8--6.9.
9. SmolLM negatif sonucu: Bölüm 6.10.
10. Kanıtlanan/kanıtlanmayanlar: Bölüm 9--11.
11. Supervisor'dan beklenen kararlar: Bölüm 12--14.

## 17. Son milestone hükmü

Proje üç niteliksel aşamadan geçti. İlk aşama broad M1 recipe search idi ve training loss'un
yanıltıcı olduğu görüldü. İkinci aşama storage, prompt transfer, relation binding, capacity, EOS ve
retention'ı ayıran kontrollü diagnostic programdı. Üçüncü aşama iki seed'de replikeli Qwen
ara-ölçek M1 artifact'i ve iyi kontrol edilmiş SmolLM failure boundary üretti.

Başarısız deneyler final sonucun etrafındaki gürültü değildir; mevcut evaluator, gate, dataset,
checkpoint rule ve model seçiminin neden güvenilir olduğunu açıklar.

Proje artık açık uçlu M1 optimizasyonundan çıkmaya hazırdır, fakat transfer veya relearning sonucu
iddia etmeye hazır değildir. Sonraki milestone, supervisor-onaylı outcome-blind bilingual contract
ve matched/replikeli Turkish causal feasibility olmalıdır. Bu çalışma yorumlanabilir bir ayrışma
verirse 25.000-fact canonical validation'ın tez değerine bilinçli karar verilebilir.

## 18. Kanıt haritası

| Konu | Ana belgeler |
|---|---|
| Özgün tez sorusu | `Expose.pdf`, 00, 01 |
| Erken M0/M1 | 04--47 |
| Acquisition ladder/direct supervision | 48--64 |
| Relation V2/scale interference | 65--82 |
| HU storage incident | 84 |
| 1.7B capacity/generic drift | 83, 85--91 |
| Supervisor follow-up/HOLD | 93--98 |
| Master status | 100 |
| Form remediation/model screen | 101--108 |
| Turkish corpus/eski bridge | 109--116 |
| Qwen replay ve 100-subject replication failure | 117--121 |
| Qwen scale/SmolLM sonuçları | 122--128 |
| Son handoff | 129 |

