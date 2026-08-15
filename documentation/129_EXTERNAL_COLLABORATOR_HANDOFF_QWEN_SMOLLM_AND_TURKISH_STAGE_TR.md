# 129 — Dış Kolaboratör Handoff: Qwen, SmolLM ve Türkçe Aşama Kararı

**Tarih:** 30 Temmuz 2026  
**Durum:** Güncel bilimsel/operasyonel handoff; yeni iş açmaz, mevcut kanıtı ve karar eşiğini netleştirir  
**Okuma önceliği:** `AGENTS.md` → Doküman 100 → bu doküman  
**Kapsam:** Doküman 98 sonrası tüm karar zinciri, özellikle Dokümanlar 100--128

## 1. Bu dokümanın tek cümlelik sonucu

Projede şu an eldeki en güçlü sonuç, **Qwen2.5-1.5B'nin 500 subject / 2.500 synthetic fact
ölçeğinde, aynı frozen recipe ile iki bağımsız seed'de prompt-robust İngilizce factual acquisition
(ara-ölçek M1) gate'lerini geçmesidir.** Buna karşılık SmolLM2-1.7B'nin hem ilk contrastive
ailesi hem de son 500-fact prompt-consistency remediation'ı held-out C/D retrieval gate'ini
geçememiştir.

Bu, **“M1'in ara-ölçek Qwen kanıtı güçlü”** demektir; **“tez tamamlandı”**, **“nihai 5.000-subject
M1 tamamlandı”** veya **“Türkçe adaptasyon transfer üretir”** demek değildir. M2 ve M3 Türkçe
nedensel aşamaları henüz açılmamıştır. Bir sonraki doğru bilimsel iş, eski ve olumsuz bridge
pilotunu otomatik tekrar etmek değil, yeni replikeli Qwen M1 artifact'leri için açıkça frozen yeni
bir Türkçe-stage/bridge kontratı yazmaktır.

Bu handoff, dışarıdaki bir araştırmacının/AI ajanın aşağıdaki iki soruya sağlıklı biçimde yardım
edebilmesi için hazırlanmıştır:

1. Qwen ara-ölçek M1 kanıtı ile Türkçe aşamaya geçişi metodolojik olarak nasıl tasarlamalıyız?
2. SmolLM'yi ikinci model olarak ne ölçüde korumak anlamlıdır; hangi noktada yeni bir SmolLM
   deneyi sadece düşük değerli bir tekrar olur?

## 2. Asıl tez sorusu ve deney mimarisi

Tezin asıl sorusu bir modelin İngilizce synthetic fact'leri ezberleyip ezberlemediği değildir.
Asıl nedensel soru şudur:

> Model Türkçe adaptasyondan sonra İngilizce öğrenilmiş olgulara Türkçe istemlerle erişiyorsa,
> bu erişim İngilizce factual memory'nin çapraz-dilli temsili/transferi midir; yoksa Türkçe fact
> eğitimiyle sonradan yeniden öğrenme midir?

Bu ayrım için durumlar aşağıdaki gibi tasarlanmıştır.

| Durum | İçerik | Nedensel rol |
|---|---|---|
| M0 | Base model | Synthetic fact öncesi negatif/baseline durum |
| M1 | İngilizce synthetic factual acquisition | İngilizce factual memory'yi kurar |
| M2 | Yalnız temiz genel Türkçe adaptasyonu | İngilizce memory'nin Türkçe'ye **transfer** olup olmadığını test eder |
| M3 | Temiz Türkçe + kontrollü Türkçe factual exposure | Türkçe factual exposure ile **relearning** etkisini ayırır |

Dolayısıyla M1'in görevi yalnız yüksek exact recall değildir. M1 artifact'i farklı istem
formlarında, özellikle eğitimde görülmeyen C/D formunda, subject--relation--object binding'i
koruyacak kadar sağlam olmalıdır. Aksi halde M2'de görülen kayıp/başarı dil transferi yerine
İngilizce istem kırılganlığı olabilir.

## 3. Bugünkü karar özeti

| İş kolu | Mevcut karar | Kanıt | Sonraki izinli adım |
|---|---|---|---|
| Qwen, 2.500 fact İngilizce M1 | İki seed'de replikeli ara-ölçek başarı | Seed-42 ve seed-43 tüm frozen gate'leri geçti | Yeni frozen Türkçe bridge/M2 kontratı tasarlamak |
| Qwen, nihai canonical 5.000 subject / 25.000 fact | Henüz çalıştırılmadı | Ara-ölçek sonucu ölçeklenebilirlik için güçlü ama nihai ölçek kanıtı değil | Türkçe-stage tasarımından sonra bilinçli scale kararı |
| Eski Qwen Türkçe bridge pilotu | Geçerli negatif feasibility bulgusu; yeni Qwen M1'e otomatik taşınamaz | Eski M1 recipe altında generic TR adaptation bridge access'i bozdu | Yeni M1 checkpoint'leriyle yeniden-baseline şart |
| SmolLM ilk ranking ailesi | Kapalı | En iyi robust intersection %52,2; frozen %70 eşiğinin altında | Replikasyon/2.500-fact scale yok |
| SmolLM prompt-consistency V2 | Kapalı | En iyi robust intersection %55,8; min relation %38 | Ancak yeni, önceden güçlü gerekçelendirilmiş farklı bir araştırma sorusu varsa yeniden açılabilir |
| M2/M3 ana tez koşulları | HOLD | Qwen M1 hazır, fakat yeni Türkçe kontratı frozen değil | Kontrat, preflight ve yeni M1-bridge baseline sonrası açılabilir |

Şu anda aktif Slurm işi yoktur. Tamamlanan son SmolLM değerlendirmesinin sonuçları Doküman 128'e
işlenmiş, terminal durumu ve storage audit'i kayda geçirilmiştir.

## 4. Neden Doküman 98 veya eski pilotlar tek başına okunmamalı?

Doküman 98, o tarihteki doğru HOLD kararını ve M2 öncesi eksikleri kaydeder. Fakat daha sonra
M1 form-generalization remediation'ları, cross-family screening, Qwen replay düzeltmeleri,
2.500-fact scale probe, bağımsız Qwen seed-43 replikasyonu ve iki SmolLM remediation dalı
gerçekleşmiştir. Bu nedenle eski bir rapordaki “Qwen başarısız”, “SmolLM umut verici” veya
“M1/M2 kapalı” ifadesi, tarihsel bağlamı olmadan güncel karar gibi okunmamalıdır.

Yetki sırası şöyledir:

1. `AGENTS.md`: storage, Slurm, artifact ve bilimsel kayıt kuralları.
2. Doküman 100: operasyonel ana kaynak; son düzeltmelerle birlikte güncel durum.
3. Dokümanlar 122--129: Qwen-scale ve SmolLM karşılaştırmasının son kanıt zinciri.
4. Dokümanlar 98--121: neden önceki recipe'lerin yeterli olmadığına dair korunmuş tarihsel kanıt.

Eski başarısızlıklar silinmedi veya yeniden yazılmadı. Bu önemlidir: yeni Qwen sonucunun değeri,
önceki yanlış/eksik recipe'lerden sonra frozen evaluator ile yeniden sınanmış olmasından gelir.

## 5. Kronolojik bilimsel hikâye

### 5.1. Erken M1 problemi: exact storage, robust binding değildir

Dokümanlar 94--98, M1'in yalnız canonical exact formda yüksek görünmesinin yeterli olmadığını
gösterdi. A/B eğitim formuna yakın istemlerde başarı, held-out veya crossed C/D formunda aynı
başarıyı garanti etmedi. Bu nedenle proje şu korumaları dondurdu:

- factual storage ile prompt-robust retrieval ayrı raporlanır;
- A/B/C/D form ailesi ve direct/QA hücreleri ayrı değerlendirilir;
- eight-cell robust intersection yalnız bütün hücrelerde doğru olan fact'i sayar;
- relation-level minimum ve tek hücre minimumu ayrıca gate'tir;
- generic integrity, synthetic intrusion ve WikiText-2 PPL retention kontrol edilir;
- checkpoint seçimi sonuç görüldükten sonra en iyi sayıyı almakla değil, önceden tanımlanmış
  “tüm gate'leri geçen en erken checkpoint” kuralıyla yapılır.

Bu kurallar sonraki Qwen değerlendirmesinin güçlü görünmesinin temelidir.

### 5.2. M1 remediation ve model screening

Dokümanlar 101--108, canonical form çeşitliliği ve farklı model ailelerinin test edilmesini
kaydetti. İlk SmolLM hybrid deneyleri 500-fact düzeyinde canonical/direct/QA başarıda çok iyi
göründü; buna rağmen unseen/crossed formlarda çöküş yaşadı. Bu, SmolLM sorununun salt retention
değil **prompt-invariant binding** olduğunu düşündürdü.

Qwen tarafında early cross-family sonucu robust retrieval açısından çok güçlüydü, ancak İngilizce
PPL maliyeti kabul edilemez derecede yüksekti. Sonraki workstream bu iki kusuru ayrı ele aldı:

- Qwen için clean-English replay ile factual retention ve generic-English retention arasında
  denge arandı.
- SmolLM için doğru cevap--relation-matched distractor ayrımını güçlendiren contrastive ranking
  objektifi test edildi.

### 5.3. Türkçe bridge pilotlarının uyarısı

Dokümanlar 109--116'daki pilotlar, “İngilizce M1 iyi görünüyorsa Türkçe adaptasyon otomatik
çalışır” varsayımının doğru olmadığını gösterdi.

- SmolLM pilotunda Türkçe PPL iyileşirken bridge access beklenen biçimde artmadı.
- Eski Qwen M1 pilotunda Türkçe erişim pre-adaptation aşamasında gözlenebildi; fakat generic
  Türkçe adaptation sonrasında bu erişim kötüleşti.

Bu sonuçlar önemli negatif feasibility kanıtıdır; ancak güncel Qwen M1 artifact'leri farklı
recipe, farklı scale ve replikeli seçimle üretildiği için yeni checkpoint'ler için doğrudan nihai
hüküm değildir. Yeni M2/M3 kontratı önce güncel Qwen M1'de İngilizce ve Türkçe erişim baseline'ını
tekrar ölçmek zorundadır.

### 5.4. Qwen replay düzeltmesi ve 2.500-fact scale

Dokümanlar 117--124, replay recipe'in seed stabilitesi ve değerlendirme/integrity tanımlarını
düzeltti. Eski seed-43 sonucu bazı gate'leri tekrar etmeyince recipe otomatik “final M1” ilan
edilmedi. Bunun yerine 2.500-fact scale koşusu açıkça **exploratory scale diagnostic** olarak
tanımlandı; ardından değişmeyen recipe ile bağımsız seed-43 doğrulaması planlandı.

Bu disiplin, aşağıdaki Qwen sonucunun post-hoc bir checkpoint seçimi veya tek-seed tesadüfü
olma riskini azaltır.

## 6. Qwen ara-ölçek M1 sonucu: en güçlü mevcut pozitif kanıt

### 6.1. Sabit tutulanlar ve değişenler

Qwen2.5-1.5B için iki koşuda 500 subject / 2.500 fact Relation V2 popülasyonu kullanıldı. Aynı:

- fact popülasyonu, dataset ve clean-English replay anchor'ları;
- model ailesi, objective, replay coefficient'i, batch/update bütçesi;
- evaluator, held-out A/B/C/D form seti, gate eşikleri ve checkpoint-selection kuralı;
- output/artifact prosedürü

kullanıldı. Seed-43'te yalnız run identity, model/data seed değiştirildi. Bu nedenle iki koşu,
aynı deneyin bağımsız replikasyonlarıdır; iki farklı recipe'in karşılaştırması değildir.

Seçim kuralı eğitimden/evaluatordan önce dondurulmuştur:

> Bütün frozen global, cell, relation, integrity ve PPL gate'lerini geçen **en erken checkpoint**
> seçilir.

Seed-42'de step 50 en zayıf hücre eşiğini (%80) %78,6 ile kaçırdı. Step 75 tüm gate'leri geçen
ilk checkpoint olduğu için seçildi. Seed-43'te ilk tam geçiş step 50'dir; step 75 de iyi olsa bile
seçilmemiştir. Bu yaklaşım “sonuca bakıp en iyi checkpoint'i seçme”yi engeller.

### 6.2. Seçilmiş checkpoint sonuçları

| Metrik | Qwen seed-42, step 75 | Qwen seed-43, step 50 | Yorumu |
|---|---:|---:|---|
| Canonical exact | %99,96 | %99,68 | İngilizce factual storage neredeyse tam |
| Hard aggregate | 19.858/20.000 = %99,29 | 19.845/20.000 = %99,225 | Tek form dışında da yüksek erişim |
| Eight-cell robust intersection | 2.402/2.500 = **%96,08** | 2.405/2.500 = **%96,20** | Aynı fact'in tüm A/B/C/D × direct/QA hücrelerinde doğru olması |
| En düşük relation | profession: %88,2 | profession: %90,2 | Relation bazlı taban güçlü |
| En zayıf hücre | profession / C / direct: %88,4 | Frozen gate'i geçti | Seed-42'nin asıl sınırlayıcı hücresi |
| Forced-choice binding | 7.961/8.000 = %99,51 | 7.965/8.000 = %99,56 | Doğru nesne, aynı relation'daki kuvvetli distractor'lardan ayrılıyor |
| WikiText-2 PPL | 14,699 → 15,909 | 14,699 → 15,169 | PPL oranı sırasıyla **1,082** ve **1,032** |
| Generic integrity | 29/30; zero synthetic intrusion | 29/30; zero synthetic intrusion | English retention/intrusion kontrolü geçti |

Seed-42'de yalnız iki lexical-but-not-empty sensitivity output gözlenmiştir; integrity kuralı
düzeltildikten sonra bunlar “boş yanıt” gibi yanlış sınıflandırılmamış ve frozen kontrol geçmiştir.
Bu açıklama kayıtlıdır; sonuç sonradan eşik oynatılarak geçirilmemiştir.

### 6.3. Artifact ve reproducibility durumu

Seçilmiş model-only artifact'ler HU scratch'ta manifest ve SHA-256 ile dondurulmuştur:

- Seed-42 step 75:
  `/vol/tmp2/yesildau/qwen_scale_selected_v1/seed42_step75/selected_artifact_manifest.json`
  (manifest SHA-256: `aed52ff8...`)
- Seed-43 step 50:
  `/vol/tmp2/yesildau/qwen_scale_selected_v1/seed43_step50/selected_artifact_manifest.json`
  (manifest SHA-256: `af3569...`)

Tam hash değerleri ve job/config ledger'ı Dokümanlar 126--127'de bulunur. Büyük checkpoint,
cache ve raw evaluation ağaçları HU home'a yazılmamıştır; scratch retention ve post-run audit
kayıtlıdır.

### 6.4. Qwen için yapılabilecek ve yapılamayacak iddia

**Savunulabilir iddia:** Bu recipe, bu model, bu 2.500-fact population ve bu frozen evaluator için
iki seed'de robust İngilizce factual acquisition göstermiştir. Qwen, Türkçe-stage tasarımı için
haklı bir ana adaydır.

**Henüz savunulamaz iddia:**

- 5.000 subject / 25.000 fact canonical final scale aynı performansı korur.
- Türkçe clean adaptation factual memory'yi korur veya Türkçe retrieval üretir.
- M2'de görülecek erişim transferdir; bunun için M3 karşılaştırması gerekir.
- Qwen tüm relation/istem gruplarında kusursuzdur; profession en zayıf relation olmaya devam eder.

## 7. SmolLM karşılaştırması: neden dal kapatıldı?

SmolLM2-1.7B ikinci model olarak değerliydi, çünkü daha küçük bir modelde clean factual storage,
PPL ve robust binding arasındaki trade-off'u karşılaştırma imkânı veriyordu. Ancak model seçimi
“en az iki model kullanılmış olsun” diye değil, her model aynı güvenlik/robustness eşiğini
geçtiğinde yapılmalıdır. Aksi halde M2/M3'te yorumlanacak şey dil transferi değil, önceden var olan
İngilizce retrieval kırılganlığı olur.

### 7.1. İlk contrastive objective ailesi

100 subject / 500 fact koşusunda canonical answer-only LM loss'a relation-matched
correct-versus-distractor ranking eklendi. Lambda=0 control, lambda=.10 treatment ve exploratory
lambda=.25 karşılaştırıldı. Kısa sonuç:

| Koşul | Exact | Hard aggregate | Eight-cell robust | En düşük relation | Forced choice | PPL |
|---|---:|---:|---:|---:|---:|---:|
| λ=0 matched control | %100 | %87,525 | %39,6 | %21 | %89,4 | 17,198 |
| λ=0,10 | %100 | %91,0 | **%52,2** | %34 | %93,1 | 17,5234 |
| λ=0,25 exploratory | %100 | %90,975 | %50,4 | %32 | %94,1 | 17,5521 |

Ranking loss doğru yönde bir fark yaratmıştır: λ=.10 robust intersection'ı %39,6'dan %52,2'ye
çıkarmıştır. Fakat frozen global gate %70'tir. Dolayısıyla bu bir mekanizma ipucu, M1 geçişi veya
M2/M3 izni değildir. λ=.25'in daha iyi olmaması da “lambda artırılırsa sorun çözülür” şeklinde
basit bir devamı desteklemez.

### 7.2. Son bounded remediation: A/B dağılım tutarlılığı

Kullanıcının yetkilendirdiği son SmolLM deneyi, aynı .10 ranking bileşenini koruyup yalnız bir
mekanizma ekledi:

```text
L = L_canonical_answer_only_LM
  + 0.10 × L_relation_matched_ranking
  + 0.10 × L_Form-A/Form-B_candidate_distribution_consistency
```

Form C/D eğitimde tutulmadı; yani C/D sonucu gerçek held-out generalization ölçümüdür. 100
subject / 500 fact, seed-42, aynı population ve aynı bütçeyle 252 update tamamlandı. Eğitim
logları final factual LM loss `0,772060`, ranking loss `0,653131`, consistency loss `0,045811`
ve 18.000 consistency group kaydeder.

Checkpoint sweep sonucu aşağıdadır. PPL base değeri 15,9242'dir.

| Step | Exact | Hard aggregate | Robust intersection | Min. relation | Forced choice | PPL ratio |
|---:|---:|---:|---:|---:|---:|---:|
| 25 | %5,6 | %4,70 | %1,0 | %0 | %50,75 | 1,011 |
| 50 | %35,4 | %34,48 | %7,4 | %3 | %55,56 | 1,031 |
| 75 | %85,2 | %74,50 | %23,6 | %14 | %75,31 | 1,055 |
| 100 | %100 | %86,45 | %38,4 | %23 | %89,69 | 1,071 |
| 125 | %100 | %89,28 | %46,6 | %28 | %92,81 | 1,082 |
| 150 | %100 | %90,65 | %51,0 | %30 | %93,38 | 1,089 |
| 175 | %100 | %90,88 | %51,4 | %32 | %93,75 | 1,091 |
| 200 | %100 | %91,15 | %53,4 | %36 | %94,00 | 1,096 |
| 225 | %100 | %91,62 | %55,0 | %38 | %94,06 | 1,098 |
| 250 | %100 | **%91,67** | **%55,8** | **%38** | %94,00 | 1,099 |
| 252/final | %100 | %91,60 | %55,2 | %38 | %94,12 | 1,100 |

Her checkpoint generic integrity kontrollerini geçti: generic top-1 30/30, lexical-empty 0 ve
synthetic intrusion 0. Buna rağmen seçilebilir checkpoint yoktur. En iyi exploratory nokta olan
step 250 bile global robust gate'i 14,2 puan; min-relation gate'ini 32 puan kaçırmaktadır.
En zayıf hücreler profession/Form-C/QA (%44), profession/Form-C/direct (%51) ve
works_industry/Form-D/direct (%49)'dir.

Bu sonuç önemli bir ayrım gösterir: model %100 exact canonical storage ve %91,67 hard aggregate
görebilir; yine de bir fact'i sekiz hücrenin tamamında güvenilir biçimde retrieve edemeyebilir.
SmolLM V2, önceki en iyi %52,2'nin az üzerinde %55,8'e çıkmıştır; fakat bu fark frozen eşiği
geçmeye yaklaşan bir sonuç değildir. Bu nedenle seed-43 replication veya 2.500-fact scale-up
bilimsel olarak yetkilendirilmemiştir.

## 8. Şu anki güçlü yanlar ve sınırlamalar

### Güçlü yanlar

- Qwen iki seed'de aynı frozen 2.500-fact protocolü geçti; bu tek seed discovery sonucundan
  belirgin biçimde daha güçlüdür.
- Qwen değerlendirmesi exact, per-cell direct/QA, eight-cell intersection, relation floor,
  forced-choice binding, integrity ve PPL'i birlikte kapsar.
- Checkpoint kuralı önceden donduruldu; seed-42 step 75'in seçimi post-hoc değildir.
- SmolLM kontrol/treatment deneyleri aynı population ve comparable budget ile yapıldı; failure
  “rastgele kötü koşul” olarak gizlenmedi.
- Çıktılar scratch'a yönlendirildi, seçilmiş artifact manifest/hash ile donduruldu ve HU home
  storage incident'ının tekrarlanmaması için post-run audit yapıldı.

### Sınırlamalar ve açık riskler

- Qwen'in kanıtı 2.500 fact'tedir; canonical nihai tasarım 5.000 subject / 25.000 fact'tir.
- Seed sayısı iki olsa da M2/M3'nin her bir seed için nasıl koşturulacağı henüz frozen değildir.
- Qwen'in güncel M1 artifact'i üzerinde Türkçe bridge baseline'ı yoktur. Eski bridge pilotu yeni
  artifact için nihai cevap sayılmaz.
- Profession relationı Qwen'de de en zayıf relationdır; Türkçe stage raporlarında relation-level
  tablo zorunlu olmalıdır.
- SmolLM V2'nin mekanik training-loss ayrıştırması vardır; ancak önceki completed treatment eski
  logging ile LM/ranking bileşenlerini ayrı kaydetmemişti. Bu, önceki sonuç farkının training
  dynamics yorumunu sınırlar; outcome değerlendirmesini geçersiz kılmaz.
- Synthetic facts kontrollü benchmarktır. Doğal dünya factuality veya genel Türkçe yetkinlik
  iddiasına tek başına genişletilmemelidir.

## 9. Bir sonraki karar için önerilen, kontrollü sıra

Bu bölüm doğrudan çalıştırma emri değildir. Dış kolaboratörden beklenen, bu sıra ve kontratın
bilimsel tasarımını eleştirmesi/iyileştirmesidir.

### Adım 1 — Yeni Qwen Türkçe-stage kontratını *önce* dondur

Doküman 100'ün HOLD prensibini koruyarak aşağıdakiler eğitime başlamadan yazılmalıdır:

1. Hangi Qwen M1 seed/checkpoint'lerinin downstream başlangıcı olacağı ve iki seed'in bağımsız
   causal replicate olarak nasıl kullanılacağı.
2. Temiz Türkçe corpus'un kaynak, lisans, filtre, token bütçesi, data hash ve train/validation
   ayrımı.
3. M2'nin yalnız clean Turkish olduğunu garanti eden contamination denetimi.
4. M3'teki Türkçe factual exposure'ın M2 ile aynı clean Turkish bütçesini koruyup hangi tek
   factual değişkeni ekleyeceği.
5. EN prompt ve TR prompt evaluator setleri; A/B/C/D × direct/QA tabloları; relation floor;
   exact/hard/robust tanımları.
6. Türkçe PPL/generic retention, English PPL/generic integrity, intrusion ve bilingual
   lexicalization kontrolleri.
7. Checkpoint-selection kuralı, primary outcome, secondary outcomes ve başarı/failure gate'leri.

Bu kontrat olmadan doğrudan generic Turkish adaptation başlatmak, eski bridge pilotunun
belirsizliğini yeni artifact'e taşımak olur.

### Adım 2 — M1 üzerinde yeniden bridge baseline ölç

Her seçili güncel Qwen M1 artifact'i için Türkçe eğitimden **önce** şunlar ölçülmelidir:

- İngilizce A/B/C/D direct ve QA retrieval (M1 gate'in downstream başlangıçta korunması);
- Türkçe karşılık promptlarında direct ve QA retrieval;
- relation/cell bazlı bridge tablosu;
- forced-choice binding ve answer-language policy;
- English ve Turkish generic/PPL baseline'ları.

Bu basamakta Türkçe erişim yoksa M2'de olası erişim daha dikkatli yorumlanır. Varsa da bu,
adaptasyon sonrası korunup korunmadığı ölçülmeden transfer kanıtı değildir.

### Adım 3 — M2 ve M3'ü aynı nedensel aile içinde karşılaştır

Ancak Adım 1--2 sonrasında M2/M3 açılmalıdır. Temel karşılaştırma:

```text
M1 → M2: English facts + clean Turkish only
M1 → M3: English facts + same clean Turkish + controlled Turkish factual exposure
```

M2'deki Türkçe retrieval, clean adaptation altında erişimin ne ölçüde dönüştüğünü gösterir.
M3'ün M2 üzerindeki ek farkı ise Türkçe factual re-learning katkısını izole eder. Her sonuç aynı
frozen evaluator, aynı checkpoint kuralı ve M1 seed replikasyonu altında raporlanmalıdır.

### Adım 4 — 25.000-fact canonical scale kararını bilinçli ver

Qwen 2.500 fact'te ölçeklenebilirliğe dair güçlü kanıt vermiştir, ama 25.000 fact için otomatik
garanti vermez. Final scale kararı iki makul biçimde ele alınabilir:

- **Önce bridge feasibility:** Yeni Qwen artifact'inde M1→M2/M3 mekanizmasının çalışıp
  çalışmadığını orta ölçekte netleştir; olumluysa canonical scale'ı final doğrulama olarak yap.
- **Önce canonical M1 scale:** Türkçe aşama öncesi final population'da M1'in tekrar geçmesini
  iste; bunun maliyeti yüksek fakat downstream family'yi nihai ölçeğe doğrudan bağlar.

Bu tercih bilimsel güç, hesaplama bütçesi ve tez takvimiyle birlikte açıkça gerekçelendirilmelidir.
Hangi sıra seçilirse seçilsin, 2.500-fact sonucu “25.000 fact sonucu zaten biliniyor” diye
sunulmamalıdır.

## 10. SmolLM için gerçekçi kullanım kararı

SmolLM'yi tezde tutmak mümkündür; ancak rolü **başarılı ikinci M1/M2/M3 ana modeli** değil,
kontrollü karşı-model / failure-boundary evidence olarak tanımlanmalıdır. Bu, negatif sonuçları
değersizleştirmez. Tam tersine, aynı canonical storage seviyesinde model ailelerinin robust binding
bakımından ayrışabildiğini gösterir.

Yeni SmolLM job'u ancak şu üç koşuldan biri açıkça sağlanırsa haklıdır:

1. Yeni objektifin, profession C/D ve relation--prompt binding hatasını neden doğrudan çözeceğine
   dair önceden yazılmış mekanik hipotez vardır.
2. Sadece “lambda/epoch/batch denemek” değil, kontrolü olan tek değişkenli yeni bir intervention
   tasarlanmıştır.
3. Sonuç, Qwen ana causal line'ını geciktirmeden ayrı bir comparative research question'ı
   cevaplayacaktır.

Bu koşullar yoksa SmolLM seed-43 veya 2.500-fact scale çalıştırmak kaynak tüketir fakat tezdeki
ana transfer-vs-relearning sorusunu daha iyi cevaplamaz.

## 11. Dış kolaboratörden istenen somut değerlendirme

Lütfen aşağıdaki sorulara mevcut kanıta dayanarak cevap verin:

1. Qwen'in iki-seed 2.500-fact M1 sonucu, yeni bir orta-ölçek M1→M2/M3 bridge feasibility
   çalışması başlatmak için yeterince güçlü mü? Değilse, minimal ek gate nedir?
2. M2/M3 için iki Qwen M1 seed'i nasıl kullanılmalı: her iki seed'den ayrı full causal chain mi,
   yoksa bir discovery chain + bağımsız confirmatory chain mi? Hangi checkpoint/run selection
   kuralı önceden yazılmalı?
3. Türkçe promptlarda doğru cevabın English object, Turkish object veya kabul edilen bilingual
   eşdeğer olması nasıl tanımlanmalı? Bu karar factual access ile lexical translation'ı
   karıştırmadan nasıl değerlendirilmeli?
4. Eski Qwen bridge negatif sonucu varken, yeni bridge baseline'da hangi failure pattern'leri
   “M2'yi başlatma” stop condition'ı yapmalıdır?
5. 2.500→25.000 scale sırası için bridge-first mi, canonical-M1-first mi daha uygundur? Kararın
   power, maliyet ve tez iddiasına etkisi nedir?
6. SmolLM'yi ikinci ana deneysel model olarak sürdürmek mi, yoksa iyi belgelenmiş comparative
   negative result olarak kapatmak mı daha dürüst ve güçlü bir tez anlatısı üretir?

Kolaboratörden yeni bir job/recipe önermeden önce şu disipline uyması beklenir: primary endpoint,
held-out evaluator, checkpoint rule, seed plan, control arm, storage estimate ve stop condition
önceden yazılmalıdır. Post-hoc “en iyi görünen” checkpoint veya yalnız exact-recall metriği
kullanılmamalıdır.

## 12. Kaynak haritası

| Belge(ler) | Bu handoff'taki rolü |
|---|---|
| 84 | HU home storage incident ve artifact lifecycle; operasyonel güvenlik sınırı |
| 94--98 | M1'in neden robust/crossed-form gate gerektirdiği; ilk HOLD kararı |
| 100 | Güncel ana operasyonel karar ve M1--M3 yürütme mantığı |
| 101--108 | Form remediation ve cross-family screening'in deneysel geçmişi |
| 109--116 | Türkçe bridge/adaptation pilotları ve negatif feasibility bulguları |
| 117--121 | Replay düzeltmeleri, M1 değerlendirme dersi ve eski planların gerçekleştirme denetimi |
| 122--125 | Qwen 2.500-fact scale probe ve SmolLM controlled comparison planları |
| 126 | Qwen seed-43 ve SmolLM training completion ledger |
| 127 | Qwen replikeli M1 sonucu ve ilk SmolLM contrastive sonuçları |
| 128 | SmolLM prompt-consistency V2 contract, eğitim ve nihai checkpoint sweep |
| 129 (bu belge) | Dış değerlendirme için güncel sentez ve karar soruları |

## 13. Son net hüküm

Qwen, şu anda projedeki **tek replikeli ve prompt-robust ara-ölçek İngilizce M1 çözümüdür**.
SmolLM, canonical memory'nin robust factual binding ile aynı şey olmadığını gösteren değerli fakat
gate'i geçmemiş karşı örnektir. Tezin ana sorusu hâlâ açıktır: yeni Qwen M1 artifact'i altında
clean Turkish adaptation transfer üretir mi, ve controlled Turkish factual exposure bundan ne
kadar ayrışır?

Bu nedenle en doğru ilerleme “M1 tamamlandı, hemen sonuç yazalım” veya “SmolLM'i tekrar tekrar
deneyelim” değildir. En doğru ilerleme, güncel Qwen artifact'leri için sıkı bir bilingual bridge
kontratı dondurmak; ardından M2 ve M3'ü kontrollü, replikeli bir nedensel karşılaştırma olarak
yürütmektir.
