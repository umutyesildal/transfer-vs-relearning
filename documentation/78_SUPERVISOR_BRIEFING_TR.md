# 78 - Supervisor Bilgilendirme Dokumani

Son guncelleme: 2026-07-12

## 1. Bu Dokumanin Amaci

Bu dokuman, tez projesinin baslangicindan bugune kadar yapilan calismalari supervisor'a
anlatilabilecek bir butunluk icinde ozetlemek icin hazirlanmistir. Yalnizca basarili sonuclari
degil, denenen ve basarisiz olan yollari, bu basarisizliklardan cikarilan dersleri, deney
tasariminda yapilan kontrollu degisiklikleri ve projenin bugunku bilimsel durumunu da kapsar.

Dokumanin ana mesaji sudur:

> Proje henuz Turkce adaptasyon asamasina gecmemistir; cunku once Ingilizce tarafinda hangi
> sentetik gerceklerin gercekten ogrenildigini guvenilir bicimde belirlemek zorundayiz. Son
> deneyler, modelin binlerce gercegi exact egitim baglaminda depolayabildigini, fakat bu
> bilgileri yeni soru bicimlerinde relation'a uygun olarak geri cagirmakta zorlandigini
> gostermistir. Dolayisiyla mevcut temel problem kapasite veya salt ezberleme degil,
> prompt-robust retrieval ve relation binding problemidir.

## 2. Tezin Temel Arastirma Sorusu

Tezin temel sorusu sudur:

> Bir dil modeli Turkceye adapte edildikten sonra daha once Ingilizce olarak ogrendigi bir
> gercegi Turkce sorular uzerinden cevaplayabiliyorsa, bu basari Ingilizcede edinilmis bilginin
> diller arasi transferi midir, yoksa model ayni gercegi Turkce adaptasyon verisinden yeniden mi
> ogrenmistir?

Bu ayrim onemlidir. Bir modelin Turkce factual retrieval performansinin artmasi tek basina
cross-lingual transfer kaniti degildir. Adaptasyon corpus'unda ayni gercek veya onu ele veren
bir ifade bulunuyorsa model bilgiyi Turkce tarafta yeniden ogrenmis olabilir. Bu nedenle tez,
bilginin nerede ve ne zaman goruldugunun kontrol edilebildigi sentetik bir deney sistemi kurar.

### 2.1. Ana hipotezler

1. Model once sentetik gercekleri yalnizca Ingilizce olarak ogrenebilir.
2. Bu gerceklerden bazilari Turkce adaptasyon sirasinda hic tekrar edilmeden Turkce olarak
   erisilebilir hale gelebilir. Bu durum transfer lehine kanit olusturur.
3. Turkce adaptasyon sirasinda tekrar edilen gerceklerin Turkce retrieval performansi daha fazla
   artabilir. Bu ek artis reaffirmation veya relearning etkisini gosterir.
4. Turkce adaptasyon, Turkce erisimi iyilestirirken Ingilizce erisimi zayiflatabilir. Bu nedenle
   English retention ve catastrophic forgetting de olculmelidir.

## 3. Neden Sentetik Gercekler Kullaniliyor?

Gercek dunyaya ait bilgilerle bu soruyu temiz bicimde cevaplamak zordur. Ornegin model “Ankara
Turkiye'nin baskentidir” bilgisini orijinal pretraining sirasinda Ingilizce, Turkce veya baska bir
dilde gormus olabilir. Bu durumda adaptasyon sonrasindaki dogru cevap icin bilgi kaynagi kesin
olarak belirlenemez.

Bu projede bu nedenle sentetik kisiler ve kontrollu subject-relation-object eslesmeleri
kullanilmaktadir. Bir fact su bicimdedir:

```text
subject -> relation -> object
```

Ornek:

```text
Sureyya Cinpolat -> born_in -> Van
```

Kisi-gercek eslesmesi yapay olarak uretildigi icin modelin bu baglantiyi onceden bilmesi
beklenmez. M0 sonucunun chance seviyesinde olmasi da bu beklentiyi desteklemistir.

Sentetik sistemin diger avantajlari sunlardir:

- her fact'in egitimde kac kez goruldugu bilinir;
- hangi dilde goruldugu kontrol edilir;
- Branch A ve Branch B dagilimi dengelenebilir;
- relation, name type ve frequency gibi alt gruplar ayrica incelenebilir;
- train ve evaluation ifadeleri ayrilabilir;
- corpus contamination sistematik olarak taranabilir;
- deney artifact'lari hash ve manifestlerle yeniden uretilebilir.

## 4. Deneyin Genel Mimarisi: M0, M1, M2 ve M3

### 4.1. M0 - Base model baseline

M0'da model sentetik fact'lerle egitilmeden once degerlendirilir. Amac iki seyi kontrol etmektir:

1. Model sentetik baglantilari zaten biliyor mu?
2. Evaluator ve prompt bicimleri yanlislikla yuksek skor uretiyor mu?

M0 direct ve QA-matched sonuclari primary top-1 icin yaklasik `0.006` olmustur. Bu deger relation
aday listelerinin chance seviyesine yakindir. Dolayisiyla sentetik fact'lerin base modelde
erisilebilir olmadigi ve QA scaffold'un sahte bilgi avantaji yaratmadigi gorulmustur.

### 4.2. M1 - English fact acquisition

M1'de tum hedef fact'ler Ingilizce olarak ogretilir. M1'in sonunda hangi fact'lerin Ingilizcede
gercekten ogrenildigi dondurulmalidir. Daha sonraki cross-lingual analiz yalnizca bu guvenilir
M1 fact alt kumesi uzerinde yapilacaktir.

Bu kosul nedensel yorum icin kritiktir. M1'de ogrenilmemis bir fact'in M2 sonrasinda Turkce
cevaplanamamasi cross-lingual transfer hakkinda bir sey soylemez; cunku aktarilacak Ingilizce
bilgi basta olusmamistir.

### 4.3. M2 - Generic Turkish adaptation, target fact tekrari yok

M2, dondurulmus M1 checkpoint'inden baslar ve contamination kontrolunden gecmis genel Turkce
corpus ile devam eder. Hedef sentetik fact'ler bu corpus'ta bulunmaz.

M2 sonrasinda Turkce retrieval artarsa, model fact'i Turkce corpus'tan yeniden ogrenmedigi icin
bu artis cross-lingual access/transfer lehine yorumlanabilir. Ayni zamanda Ingilizce retention
olculerek Turkce adaptasyonun unutma etkisi incelenir.

### 4.4. M3 - Turkish repetition / relearning condition

M3 de ayni M1 checkpoint'inden baslar. M2 ile toplam token, optimizer step, batch size ve learning
rate schedule acisindan budget-matched olmalidir. Tek kontrollu fark, Branch B fact'lerinin Turkce
ifadelerinin adaptasyon verisine eklenmesidir.

- Branch A: Turkce tarafta hedef fact tekrari yoktur; transfer-only kosuludur.
- Branch B: hedef fact Turkce olarak tekrar edilir; reaffirmation/relearning kosuludur.

Ana analiz difference-in-differences mantigina dayanir:

```text
(M3 Turkce retrieval - M2 Turkce retrieval) Branch B
eksi
(M3 Turkce retrieval - M2 Turkce retrieval) Branch A
```

## 5. Veri Setinin Evrimi

### 5.1. Ilk tasarimdan tam veri setine

Eski Notion notlarinda once 24 subject ve iki relation'li bir pilot, daha sonra 5.000 subject ve
dort relation'li 20.000 fact tasarimi bulunmaktadir. Bunlar projenin tasarim tarihidir; guncel
source of truth degildir.

Tam `synthetic_v1` veri seti su hale gelmistir:

- 5.000 sentetik subject;
- subject basina bes fact;
- toplam 25.000 fact;
- relation'lar: `profession`, `born_in`, `lives_in`, `studied_at`, `works_at`;
- kontrollu Branch A/B, frequency ve name-type metadata'si.

### 5.2. Relation V2 degisikligi

500-fact V1 audit'inde `studied_at` ve `works_at` relation'larinda yogun candidate collapse
gorulmustur. Yanlis tahminler rastgele dagilmamis, cok buyuk oranda iki baskin adaya yonelmistir:

- `studied_at` hatalarinda `19 Mayis Universitesi`;
- `works_at` hatalarinda `3M`.

Bu nedenle relation sayisini azaltmak yerine iki proper-name-heavy relation kontrollu olarak
degistirilmistir:

```text
studied_at -> field_of_study
works_at   -> works_in_industry
```

Guncel Relation V2 seti:

1. `profession`
2. `born_in`
3. `lives_in`
4. `field_of_study`
5. `works_in_industry`

Bu degisiklik arastirma sorusunu degistirmez. Amac, modelin subject-relation-object binding
yetenegini olcmek; tokenizer veya relation-level prior nedeniyle az sayida proper noun'a cokmesi
degildir.

### 5.3. V2 candidate ve assignment audit'i

Yeni field ve industry adaylari resmi siniflandirma/taksonomilerden uyarlanmis, sonra sentetik
atamalar dengeli ve bagimsiz uretilmistir.

- 50 field adayi ve 50 industry adayi vardir.
- Her aday globalde tam 100 kez gorulur.
- Her aday her 100-subject blokta iki kez gorulur.
- 2.500 olasi field-industry cifti de veri setinde temsil edilir.
- Pair cell count'lari 1 ile 3 arasindadir.
- Profession-field NMI: `0.00337`, Cramer's V: `0.03056`.
- Profession-industry NMI: `0.00396`, Cramer's V: `0.03374`.
- Field-industry NMI: `0.00225`, Cramer's V: `0.01852`.

Bu dusuk bagimlilik degerleri, modelin “doktor ise healthcare sektorundedir” gibi kolay
istatistiksel kestirmeler kullanmasini onlemeye yoneliktir. Modelden relation object'ini tahmin
etmesi degil, o subject icin atanmis sentetik binding'i ogrenmesi beklenmektedir.

Tam V2 release su buyukluktedir:

- 5.000 profil;
- 25.000 fact;
- 120.500 Ingilizce satir;
- Branch B icin 60.235 Turkce repetition satiri.

## 6. Degerlendirme Sistemi

### 6.1. Neden open generation yerine candidate ranking?

Modelden serbest metin uretmesini istemek spelling, punctuation, tokenization ve ayni cevabin
farkli yazimlari gibi ek belirsizlikler getirir. Bu nedenle her relation icin dondurulmus candidate
inventory kullanilir. Model ayni prompt altinda tum adaylara skor verir; dogru cevabin sirasi
hesaplanir.

Primary skor, answer token'larinin ortalama log probability'sidir. Total log probability ikincil
sensitivity metriğidir. Ortalama kullanmak, uzun cevaplarin yalnizca daha fazla token icerdigi
icin sistematik olarak cezalandirilmasini azaltir.

**Somut ornek:** `Vittoria Houston -> born_in -> San Francisco` fact'i icin evaluator su
held-out soruyu kullanabilir:

```text
What city was Vittoria Houston born in?
```

Model serbestce bir cumle uretmez. Ayni city inventory'deki her aday sorunun sonuna ayri ayri
eklenir ve yalnizca aday cevabin token'lari skorlanir. Asagidaki sayilar yontemi gostermek icin
temsili bir ornektir:

| Candidate | Mean answer-token log probability | Rank |
|---|---:|---:|
| `San Francisco` | -0,42 | 1 |
| `Chicago` | -1,18 | 2 |
| `Adana` | -2,05 | 3 |

Bu durumda prediction `San Francisco`, correct rank `1` ve fact top-1 basarilidir. Open
generation kullanilsaydi modelin `She was born in San Francisco.` gibi daha uzun bir ifade
uretmesi, canonical cevap dogru olsa bile ek string-normalization kararlarini gerektirecekti.

### 6.2. Uc retrieval gorunumu

M1'de bir fact'in yalnizca egitim cumlesini tamamlayabilmesi yeterli kabul edilmez. Uc ayri gorunum
kullanilir:

1. **Exact-prefix:** Egitim scaffold'una en yakin tamamlamadir. Depolama icin guclu bir testtir.
2. **Held-out direct:** Egitimde kullanilmayan dogrudan soru paraphrase'idir.
3. **Held-out QA-matched:** Question/Answer scaffold'unda, yine held-out bir probe'dur.

Bir fact'in en guclu learned-fact tanimi `triple robust` olmasidir:

```text
exact top-1 AND direct top-1 AND QA top-1
```

`Direct/QA overlap` ise iki held-out probe'da ayni anda top-1 olmasidir. Top-5, MRR, mean rank ve
margin de raporlanir; ancak ana learned-fact membership top-1 kesisimine dayanir.

**Uc yontemin ayni fact uzerindeki ornegi:** Yine
`Vittoria Houston -> born_in -> San Francisco` fact'ini ele alalim.

1. **Exact-prefix:** Training scaffold'una yakin prefix verilir.

   ```text
   Vittoria Houston was born in
   ```

   City adaylari bu prefix'in ardinda skorlanir. `San Francisco` rank 1 ise exact basarilidir.

2. **Held-out direct:** Training'de aynen bulunmayan, `Question:` / `Answer:` scaffold'u olmayan
   soru verilir.

   ```text
   What city was Vittoria Houston born in?
   ```

   `San Francisco` rank 1 ise direct basarilidir. Bu gorunum, bilginin yalnizca egitim cumlesini
   tamamlamaktan daha farkli bir soru bicimine tasinip tasinmadigini olcer.

3. **Held-out QA-matched:** Ayni held-out soru QA scaffold'u ile verilir.

   ```text
   Question: What city was Vittoria Houston born in?
   Answer:
   ```

   `San Francisco` rank 1 ise QA basarilidir.

**Triple robust ornegi:** Bir fact icin sonuc `exact rank = 1`, `direct rank = 1` ve
`QA rank = 1` ise fact triple robust listeye girer. Ornegin uc gorunumde de `San Francisco`
birinciyse `S00634_born_in` triple robust'tur. Sonuc `1 / 2 / 1` olsaydi fact depolanmis ve QA'de
erisilebilir olsa bile direct top-1 olmadigi icin triple robust sayilmazdi. Direct/QA overlap de
ancak son iki rank'in ikisi de 1 ise sayilir.

### 6.3. Relation binding

`born_in` ve `lives_in` ayni city candidate inventory'sini paylasir. Bu bilincli bir zorluktur.
Modelin bir subject ile iki sehri iliskilendirmesi yetmez; hangi sehrin dogum, hangisinin ikamet
relation'ina ait oldugunu ayirmasi gerekir.

Bu iki relation kaldirilmamali veya birlestirilmemelidir. Aksi halde tezin en degerli binding
kontrollerinden biri kaybolur. Birthplace-residence swap rate bu nedenle ayrica raporlanir.

**Somut binding ve swap ornegi:** `Doğan Uluba` icin iki ayri city fact'i vardir:

```text
Doğan Uluba -> born_in -> Adana
Doğan Uluba -> lives_in -> Istanbul
```

`What city does Doğan Uluba currently live in?` sorusunda model `Istanbul` yerine `Adana`
adayini rank 1 yaparsa subject'i ve subject'e ait gercek bir sehri hatirlamistir; fakat sehri
yanlis relation'a baglamistir. Bu bir residence-to-birthplace swap'tir. Tersine, dogum yeri
sorusunda `Istanbul` secilmesi birthplace-to-residence swap olur.

## 7. M1'de Denenen Ilk Yaklasimlar ve Neden Basarisiz Oldular

Projenin ilk M1 doneminde cok sayida genis olcekli recipe denendi. Bunlarin ortak sonucu,
training loss'un dusmesine ragmen held-out retrieval'in chance seviyesinin az uzerinde kalmasiydi.

**Sorunun sayisal ornegi:** Iki asamali Stage B2'nin `checkpoint-478` sonucunda answer-only
objective training loss'u belirgin bicimde iyilestirmesine ragmen direct top-1 yalnizca `6/500`,
QA top-1 `6/500` ve iki gorunumde ortak basarili fact sayisi `2/500` olmustur. Yani model egitim
dizilerindeki cevap token'larini daha iyi tahmin etmeyi ogrenmis, fakat held-out soruda dogru
adayi rakiplerinden ayirma yetenegi ayni oranda artmamistir. Bu nedenle dusuk loss tek basina
"500 fact ogrenildi" anlamina gelmez.

### 7.1. GPT-2 plain continued pretraining

Farkli learning rate ve epoch kombinasyonlari denendi:

- `5e-5`, 1 epoch;
- `1e-4`, 1 epoch;
- `5e-5`, 3 epoch.

En iyi direct ve QA sonuclari yaklasik yuzde 2 civarinda, robust overlap ise en fazla `5/500`
duzeyinde kaldi. Daha fazla epoch performansi iyilestirmedi; bazi checkpoint'lerde geriletti.

### 7.2. SmolLM2-360M ve SmolLM2-1.7B

Model ailesi ve kapasite degistirildi. SmolLM2-360M ilk pilotu ve daha buyuk 1.7B model de robust
retrieval tavanini kiramadi. 1.7B model direct tarafta bir miktar toparlanirken QA ve overlap
bozuldu. Bu, problemin yalnizca parametre sayisi olmadigina dair ilk guclu sinyaldi.

### 7.3. Daha cok repetition ve QA mix

Fact'ler daha sik gosterildi, QA satirlari pretraining mix'ine eklendi ve epoch sayisi artirildi.
R1-R4 ailesinde en iyi robust overlap yine `5/500` civarinda kaldi. Salt exposure artisi veya
generic QA eklemek yeterli olmadi.

### 7.4. BIO + QA mixed pretraining

Kisa fact cumleleri yerine daha zengin biography metinleri ve QA karisimi kullanildi. Bunun
gerekcesi, fact'leri daha dogal ve cok baglamli bicimde sunmakti. Ancak direct, QA ve overlap
sonuclari onceki iyi baseline'i gecmedi.

**Somut BIO + QA ornegi:** Bir subject icin kullanilan zengin biography satirlarindan biri
soyledir:

```text
Mada Granger works as a Customer service representative. Mada Granger was born in Istanbul,
now lives in Mugla, studied at Bezm-i Alem Vakif Universitesi, and works at Tofas.
```

Buna `Question: Where was Mada Granger born? Answer: Istanbul` gibi QA satirlari da eklendi.
Fakat en iyi checkpoint'te 500 fact icinde direct `8/500`, QA `11/500` ve robust direct/QA
overlap yalnizca `3/500` oldu. Ornek biography tum object'leri acikca icerse de modelin held-out
soruda ilgili relation object'ini top-1 secmesini garanti etmedi.

### 7.5. Iki asamali acquire-then-extract sistemi

Once biography'lerle acquisition, sonra QA fine-tuning ile extraction denenmistir. Answer-only
loss kullanan Stage B2 dahil olmak uzere bu kol da robust learned-fact gate'ini gecemedi. Loss'un
dusmesi factual candidate discrimination'in otomatik olarak arttigi anlamina gelmedi.

**Somut iki-asamali ornek:** `Mada Granger -> born_in -> Istanbul` fact'i icin Stage A'da model
subject-merkezli biography ile karsilasir:

```text
Mada Granger was born in Istanbul ... now lives in Mugla ...
```

Stage B, Stage A checkpoint'inden devam ederek ayni bilgiyi soru-cevap biciminde cikarmaya calisir:

```text
Question: Where was Mada Granger born?
Answer: Istanbul
```

Hipotez, Stage A'nin bilgiyi depolamasi ve Stage B'nin bu bilgiyi soru altinda cikarmayi
ogretmesiydi. Ancak answer-only Stage B2'nin en iyi noktasinda direct `6/500`, QA `6/500` ve
robust overlap `2/500` kaldi. Dolayisiyla acquire ve extract asamalarini sirayla uygulamak bu
recipe'de yeterli olmadi.

### 7.6. High-exposure baseline ve ranking objective

Daha uzun ve dusuk learning rate'li baseline ile candidate-ranking objective kollari denendi.
Ilk ranking deneyi bazi metriklerde kucuk bir toparlanma gosterse de tekrar edilebilir ve kalici
bir iyilesme uretmedi. Follow-up run geriledi.

### 7.7. Binding-mix synthetic redesign

Multi-view biography, farkli QA bicimleri ve relation-contrastive satirlar iceren daha zengin bir
veri ailesi olusturuldu. Training loss basarili bicimde dustu; fakat en iyi direct `7/500`, QA
`11/500`, robust overlap `3/500` oldu. Bu deney, zengin veri + plain full-sequence CLM'in tek
basina problemi cozmedigini gosterdi.

**Somut binding-mix ornegi:** Ayni `Mada Granger` profili farkli biography gorunumleriyle verildi
ve relation'a ozel rakipler iceren su tip bir satir eklendi:

```text
Question: What is the birthplace of Mada Granger?
Options:
A. Mugla
B. San Jose
C. Irving
D. Istanbul
Answer: D. Istanbul
```

Burada `Mugla`, ayni subject'in dogru sehri fakat yanlis relation object'idir; bu nedenle guclu
bir binding rakibidir. Buna ragmen en iyi binding-mix sonuclari direct `7/500`, QA `11/500` ve
robust overlap `3/500` olarak kaldi. Zengin gorunum ve contrastive secenek, plain full-sequence
CLM altinda held-out retrieval'e yeterince genellenmedi.

### 7.8. Bu donemin temel metodolojik hatasi

Bu denemelerin en onemli ortak problemi, temel acquisition feasibility sorusu kucuk olcekte
cozulmeden 25.000 fact uzerinde recipe aramaya calisilmasiydi. Eski deployment planinda kucuk
pilot ongorulmesine ragmen, uygulamada full fact corpus ile training yapilip yalnizca 100-subject
alt kumesi evaluate edilmisti.

Dolayisiyla “model sentetik fact ogrenemiyor” sonucu erken ve fazla geneldi. Once su sorularin
ayrilmasi gerekiyordu:

1. Model tek bir fact'i depolayabiliyor mu?
2. Egitim scaffold'unda geri cagirabiliyor mu?
3. Held-out direct soruya transfer edebiliyor mu?
4. Ayni recipe birden cok relation ve daha fazla binding altinda olcekleniyor mu?

## 8. Donum Noktasi: Acquisition Ladder ve Direct Supervision

### 8.1. Ilk 10-subject acquisition ladder

10 subject, 50 fact ile yapilan ilk kucuk deney de basarisiz oldu:

- exact: `12/50`;
- direct: `1/50`;
- QA: `11/50`;
- direct/QA overlap: `1/50`.

Bu sonuc scale probleminden once format problemini incelememiz gerektigini gosterdi.

**Sonucun nasil okunduguna dair ornek:** Ayni 50-fact setindeki
`Augusta Rodriquez -> born_in -> Van` fact'i daha sonra tek basina izole edildiginde exact ve QA
gorunumlerinde `Van` rank 1, direct gorunumde rank 4 oldu. Bu tek fact, aggregate tablodaki
deseni somutlastirir: model egitim prefix'ine yakin bicimde cevabi saklayabilir ve QA scaffold'u
altinda bulabilir; fakat scaffold-free soruda ayni cevabi top-1'e tasiyamayabilir. Bu nedenle
`12/50 exact` ile `1/50 direct` arasindaki fark yalnizca fact sayisi degil, format transferi
sorunudur.

### 8.2. Single-fact diagnostic

Tek bir fact secildi:

```text
Augusta Rodriquez -> born_in -> Van
```

Model exact-prefix ve QA-matched probe'da `Van` cevabini rank 1 yapti; fakat scaffold-free direct
prompt'ta cevap rank 4'te kaldi. Bu deney cok onemliydi:

- model fact'i depolayabiliyordu;
- QA scaffold'unda erisebiliyordu;
- sorun fact'in yoklugu degil, direct prompt formatina transferdi.

### 8.3. Direct-aware supervision

Ayni fact icin iki scaffold-free direct training paraphrase'i eklendi. Toplam optimizer-step
budget'i onceki kontrolle eslestirildi ve evaluation direct prompt'u held-out tutuldu.

Sonuc: ilk kaydedilen checkpoint'ten itibaren exact, held-out direct ve held-out QA'nin ucu de
rank 1 oldu. Bu, direct retrieval'in ogretilebilir oldugunu ve onceki temel eksigin prompt-format
coverage oldugunu kanitladi.

**Training ve held-out ayrimi ornegi:** `Van` cevabi icin training'e su iki scaffold-free form
eklendi:

```text
Where was Augusta Rodriquez born? Van
Which place is recorded as Augusta Rodriquez's birthplace? Van
```

Evaluation'da ise ayni cumleler tekrar kullanilmadi; su ucuncu paraphrase held-out tutuldu:

```text
What is the birthplace of Augusta Rodriquez?
```

Direct-aware run'in ilk kaydedilen `checkpoint-25` sonucunda `Van` exact, bu held-out direct ve
held-out QA gorunumlerinin her birinde rank 1 oldu. Direct margin onceki kontrolun `-1,513`
degerinden `+3,566` degerine cikti. Boylece sonuc exact prompt kopyalamaya degil, yeni bir direct
paraphrase'e genellemeye dayandi.

### 8.4. 10 `born_in` fact

Ayni direct-aware recipe on farkli birthplace binding'ine genisletildi. Checkpoint 50'den itibaren:

- exact: `10/10`;
- direct: `10/10`;
- QA: `10/10`;
- overlap: `10/10`.

**On farkli binding'den ornekler:** Bu run tek bir cevabi tekrar etmek yerine ayni relation icinde
farkli subject-city eslesmelerini birlikte ogrenmek zorundaydi:

```text
Vittoria Houston -> born_in -> San Francisco
Doğan Uluba -> born_in -> Adana
Leyla Demirtaş -> born_in -> Omaha
Augusta Rodriquez -> born_in -> Van
Mildred Parks -> born_in -> El Paso
```

Checkpoint 25'te yalnizca `7/10` exact, `6/10` direct ve `6/10` QA top-1 iken checkpoint 50'de
listedeki ve diger bes binding'in tamami uc gorunumde de rank 1 oldu. Ornegin `What city was
Doğan Uluba born in?` sorusunda `Adana`, `What is the birthplace of Augusta Rodriquez?` sorusunda
`Van` tum diger city adaylarini gecti.

### 8.5. Bes relation, 50 fact

Recipe bes relation'in tamamina, 10 subject ve 50 fact'e genisletildi. Checkpoint 75 sonucu:

- exact: `50/50`;
- direct: `48/50`;
- QA: `49/50`;
- direct/QA overlap: `48/50`.

Bu sonuc projenin ilk gercek acquisition basarisidir. SmolLM2-360M modelinin dogru veri ve
supervision bicimiyle sentetik fact'leri hem depolayabildigi hem de held-out prompt'larda buyuk
oranda geri cagirabildigi gosterilmistir.

**Bes relation'in tek subject uzerindeki ornegi:** `Vittoria Houston` profili bes ayri binding
iceriyordu:

```text
profession -> Event planner
born_in    -> San Francisco
lives_in   -> Chicago
studied_at -> Erciyes Universitesi
works_at   -> Domino's Pizza
```

Evaluator relation'a gore farkli aday inventory'sini kullandi: profession sorusunda meslekleri,
dogum ve ikamet sorularinda ortak city listesini, egitim sorusunda universiteleri, is sorusunda
ise kurumlari karsilastirdi. Checkpoint 75'te global `50/50` exact sonucu tum fact'lerin training
prefix'inde saklandigini; `48/50` direct/QA overlap ise bunlarin 48'inin iki held-out soru
gorunumunde de top-1 oldugunu gosterdi. Relation bazinda profession, `born_in` ve `works_at`
`10/10`; `lives_in` ile `studied_at` `9/10` overlap verdi. Yani toplam basari, bir relation'in
adaylarini baska relation'in adaylariyla karistiran tek bir toplu siniflandirma degildir.

### 8.6. Basarili recipe

Temel direct-aware recipe:

- fact basina 3 declarative satir;
- fact basina 2 QA satiri;
- fact basina 2 direct soru satiri;
- toplam 7 satir/fact;
- answer-only loss;
- base SmolLM2-360M;
- learning rate `1e-4`;
- 36 epoch;
- constant-with-warmup scheduler;
- weight decay yok;
- olcekler arasinda 252 optimizer update ve efektif exposure mantigi korunuyor.

Burada “36 epoch coktur” seklinde tek basina yorum yapmak yaniltici olur. Kucuk datasetlerde
epoch sayisi, sabit 252 update ve fact basina kontrollu exposure saglamak icin kullanilmistir.

## 9. V1 500-Fact Sonucu ve Relation Collapse

Direct-aware recipe 100 subject / 500 fact'e ciktiginda checkpoint 250'de:

- exact: `451/500` (%90,2);
- direct: `317/500` (%63,4);
- QA: `349/500` (%69,8);
- direct/QA overlap: `277/500` (%55,4);
- triple robust: `265/500` (%53,0).

Relation bazinda triple robust dagilim cok dengesizdi:

| Relation | Triple robust |
|---|---:|
| profession | 85/100 |
| lives_in | 74/100 |
| born_in | 53/100 |
| studied_at | 29/100 |
| works_at | 24/100 |

Branch A/B ve English-like/Turkish-like name dengesinde onemli bir sapma yoktu. Esas sorun
relation-specific candidate collapse idi. Bu bulgu Relation V2 degisikliginin gerekcesidir.

Checkpoint 250 uzerinde balanced-negative ranking continuation da denenmis, fakat en iyi sonuc
triple robust `264/500` ile baseline'i gecememistir. Bu nedenle devam checkpoint'i reddedilmistir.

## 10. Relation V2 Sonuclari

### 10.1. V2 10-subject / 50-fact gate

Checkpoint 125'te:

- exact: `50/50`;
- direct: `45/50`;
- QA: `46/50`;
- overlap: `45/50`;
- triple robust: `45/50`.

Relation bazinda:

| Relation | Triple robust |
|---|---:|
| profession | 10/10 |
| born_in | 10/10 |
| lives_in | 5/10 |
| field_of_study | 10/10 |
| works_in_industry | 10/10 |

Yeni iki relation'in `10/10` olmasi redesign'in amacina ulastigini gosterdi. Kalan bes hatanin
dordu residence sorusunda ayni subject'in birthplace'inin secilmesiydi. Yani kalan ana problem
city-relation binding idi.

### 10.2. Paired-city CLM kontrolu

`born_in` ve `lives_in` fact'leri icin iki sehri ayni training ifadesinde karsilastiran simetrik
satirlar eklendi. Beklenti modelin iki relation'i ayirmasiydi. Sonuc iyilesmedi:

- global triple `45/50`den `44/50`ye dustu;
- `lives_in` triple `5/10` olarak kaldi;
- unique city swap sayisi dortten bese cikti;
- ters yonde yeni bir hata olustu.

Yorum: Iki sehri birlikte gostermek relation ayrimini ogretmek yerine subject-city association'ini
iki sehir icin de guclendirdi.

**Somut paired-city ornegi:** `Doğan Uluba` icin canonical eslesmeler `born_in -> Adana` ve
`lives_in -> Istanbul` idi. Kontrol training'inde iki relation'i ayni satirda acikca karsilastiran
su tip ifadeler kullanildi:

```text
Although Doğan Uluba currently lives in Istanbul, Doğan Uluba was born in Adana.
Question: Doğan Uluba was born in Adana. Where does Doğan Uluba currently live instead?
Answer: Istanbul
```

Beklenti, `Adana` ile `Istanbul`un relation rollerinin bu acik karsitlik sayesinde ayrilmasiydi.
Fakat held-out residence sorusunda model yine `Adana`yi secebildi. Daha genis hata listesinde
`Vittoria Houston` icin `Chicago` yerine `San Francisco` ve `Umut Üçer` icin `Chicago` yerine
`Santa Ana` secildi. Ayrica ters yonde yeni bir hata olustu: `Mildred Parks`in dogum yeri
`El Paso` sorulunca QA gorunumunde ikamet sehri `Tucson` secildi. Tum bu fact'ler exact-prefix'te
rank 1 kaldigi icin paired-city kontrolu storage'i bozmadi; iki subject-city association'ini
guclendirip relation ayrimini held-out prompt'a tasiyamadi.

### 10.3. City hard-negative ranking kontrolu

Clean V2 checkpoint 125'ten baslayarak, dogru city ile ayni subject'in diger relation'daki city'sini
karsilastiran dusuk learning rate'li ranking continuation uygulandi. 35 update boyunca tum
checkpoint'ler tamamen ayni sonucu verdi: `50/45/46/45/45`.

Training prompt'larinda pairwise loss zaten cok dusuktu. Bu nedenle model seen prompt'ta dogru
sehri yanlis sehirden ayirabiliyor, fakat bu ayrimi held-out prompt'a tasiyamiyordu. Bu da yeniden
prompt transfer problemine isaret etti.

### 10.4. V2 500-fact sonucu

Clean V2 recipe 100 subject / 500 fact ile calistirildi. En iyi checkpoint 250 sonucu:

| Metric | Sonuc | Precommitted gate |
|---|---:|---:|
| Exact | 500/500 | 450/500 |
| Direct | 378/500 | 400/500 |
| QA | 377/500 | 400/500 |
| Overlap / triple | 329/500 | 350/500 |

Exact storage kusursuzdur. Gate direct icin 22, QA icin 23 ve overlap icin 21 fact ile dar bicimde
kacirilmistir.

V1 checkpoint 250 ile kontrollu karsilastirma:

```text
exact   +49
direct  +61
QA      +28
overlap +52
```

Dolayisiyla V2 bilimsel ve muhendislik acisindan acik bir iyilesmedir; fakat precommitted gate
sonuc goruldukten sonra degistirilmemistir. Bu, olumlu sonucu abartmamak icin onemlidir.

### 10.5. Exploratory V2 2.500-fact sonucu

500-fact gate resmi olarak gecmemesine ragmen, kullanici onayi ile 2.500-fact run exploratory
override olarak yapildi. Bu run gate'i geriye donuk olarak gecmis saymaz.

Checkpoint 252 sonucu:

- exact: `2.498/2.500` (%99,92);
- direct: `1.249/2.500` (%49,96);
- QA: `1.293/2.500` (%51,72);
- overlap: `958/2.500` (%38,32);
- triple robust: `957/2.500` (%38,28).

Exploratory gate `2.250/2.000/2.000/1.750` idi ve prompt-robust metriklerde acik bicimde
gecilemedi.

En onemli scale karsilastirmasi:

| Scale | Exact orani | Overlap orani |
|---|---:|---:|
| 500 fact | 100,0% | 65,8% |
| 2.500 fact | 99,92% | 38,3% |

Ayrica 2.500-fact modelinin icindeki ayni nested ilk 500 fact:

- exact `498/500`;
- direct `236/500`;
- QA `264/500`;
- overlap `188/500`;
- triple `187/500`.

Ayni 500 fact izole run'da `500/378/377/329/329` idi. Iki bin ek binding eklendiginde ayni
fact'lerin exact storage'i korunurken held-out retrieval'i ciddi bicimde dusmustur.

Bu sonuc, bugune kadarki en guclu bilimsel bulgudur:

> Modelin fact depolama kapasitesi mevcut olcekte ana darboğaz degildir. Fact yogunlugu arttikca
> subject-relation-object baglantilarini yeni prompt bicimlerinde secme yetenegi bozulmakta;
> retrieval/binding interference artmaktadir.

## 11. Sonuclari Nasil Yorumlamaliyiz?

### 11.1. “Model fact'leri ogrenemiyor” demek artik dogru degil

Tek fact, 10 fact, 50 fact, 500 fact ve 2.500 fact sonuclari modelin sentetik bilgiyi depoladigini
gostermektedir. Ozellikle 500 fact'te `500/500`, 2.500 fact'te `2.498/2.500` exact sonucu bu konuda
gucludur.

Dogru ifade sudur:

> Model fact'leri depoluyor; ancak depolanan bilgiyi farkli soru scaffold'larinda ve relation'a
> uygun aday secimiyle istikrarli bicimde geri cagirmiyor.

### 11.2. Training loss yeterli bir basari olcutu degil

Birden fazla basarisiz run'da training ve validation loss dustu, fakat candidate-ranking
accuracy artmadi. CLM objective dil dizisini tahmin etmeyi optimize eder; bizim bilimsel hedefimiz
ise subject ve relation kosulu altinda dogru object'i rakiplerden ayirmaktir. Loss ve retrieval
metrikleri bu nedenle birlikte raporlanmalidir.

### 11.3. Model buyutmek tek basina cozum degil

1.7B model denemesi kucuk modeldeki temel failure mode'u ortadan kaldirmadi. Daha buyuk model
gelecekte ayri bir kapasite branch'i olabilir; ancak mevcut kanitlar veri/objective/prompt coverage
problemini model boyutuyla maskelemenin iyi ilk adim olmadigini gosterir.

### 11.4. Tokenization tek basina ana neden degil

Proper-name-heavy relation'lar candidate prior ve tokenization acisindan problemliydi; V2 ile
buyuk iyilesme saglandi. Fakat V2'de bile scale arttikca retrieval dustu. Demek ki tokenization
onemli bir etken olsa da genel sorunu tek basina aciklamaz.

### 11.5. `born_in` ve `lives_in` karisikligi degerli bir negatif sonuc

Bu iki relation'in karismasi veri setinin bozuk oldugunu gostermek zorunda degildir. Ayni subject
icin iki city object'i ve ortak candidate inventory, modelin relation semantics'i ne kadar iyi
bagladigini olcer. Paired CLM ve hard-negative kontrollerinin basarisizligi, basit contrastive
exposure'un held-out prompt transferini otomatik olarak cozmedigini gosteren yorumlanabilir bir
bulgudur.

## 12. Su Anda Ne Kanitlandi, Ne Kanitlanmadi?

### Kanitlanan veya guclu bicimde desteklenen noktalar

- Base model sentetik fact baglantilarini chance seviyesinin uzerinde bilmiyor.
- SmolLM2-360M, direct-aware answer-only recipe ile sentetik fact depolayabiliyor.
- Prompt-format coverage held-out retrieval icin kritik.
- Exact storage ile robust retrieval birbirinden ayrilmasi gereken iki farkli yetenek.
- V2 relation redesign'i V1'e gore kontrollu ve buyuk bir iyilesme sagladi.
- 500'den 2.500 fact'e cikarken storage sabit kalirken retrieval ciddi bicimde bozuldu.
- Relation binding ve fact-density interference bugunku ana M1 darboğazidir.

### Henuz kanitlanmayan noktalar

- Ingilizce fact'lerin Turkceye transfer olup olmadigi henuz test edilmedi.
- Branch A ve Branch B arasindaki reaffirmation/relearning farki henuz olculmedi.
- Turkish adaptation'in English retention uzerindeki etkisi henuz olculmedi.
- 25.000 fact'lik full M1 recipe henuz bilimsel olarak hazir degil.
- Daha buyuk modelin ayni kontrollu recipe ile scale interference'i azaltip azaltmayacagi bilinmiyor.

Bu nedenle mevcut calisma “tez basarisiz oldu” degil, ana nedensel deneye gecmeden once M1
olcum kosullarini kuran ve onemli bir storage-retrieval ayrimi bulan bir feasibility ve diagnostic
asamasidir.

## 13. Turkce Corpus ve Contamination Hatti

M2/M3 icin Turkce Wikipedia tabanli versioned corpus pipeline'i tasarlanmistir. Temel prensip,
sentetik target fact'lerin generic Turkish adaptation corpus'una sizmasini engellemektir.

Planlanan/uygulanan pipeline bileşenleri:

1. Resmi Wikimedia dump metadata'sini resolve etme.
2. Resmi SHA-1 checksum ile download dogrulama.
3. Streaming XML extraction (`mwxml`, `mwparserfromhell`).
4. Unicode NFC ve Turkce karakterleri koruyan normalization.
5. Audit-first filtering; threshold'lari veriyi gormeden keyfi secmeme.
6. SHA-256 ve SQLite tabanli exact deduplication.
7. Exact, Unicode casefold ve Turkish-lowercase kanallarinda contamination scan.
8. Subject name, fact ID, training sentence ve subject-own-object eslesmelerinde removal.
9. Tek basina yaygin object adlarini remove etmek yerine flag-only olarak raporlama.
10. Deterministic document-level train/validation split.
11. Manifest, hash, provenance ve stage-state kaydi.

Planlanan corpus token budget'lari nested olacaktir:

```text
10M token < 25M token < 50M token
```

Bu sayede Turkish adaptation strength arttikca transfer, forgetting ve Turkish perplexity
degisimi incelenebilir. Ancak M1 learned-fact membership dondurulmadan M2/M3'e gecmek nedensel
yorumu zayiflatir.

## 14. Reproducibility ve Deney Disiplini

Projede her run icin asagidaki unsurlar kaydedilmektedir:

- Git commit'leri;
- dataset ve artifact SHA-256 hash'leri;
- model/checkpoint kimligi;
- training config;
- Slurm job ID;
- runtime ve GPU bilgisi;
- train/validation loss;
- exact/direct/QA sonuclari;
- relation ve subgroup breakdown;
- precommitted gate ve son karar.

Gate'ler sonucu gordukten sonra kolaylastirilmamaktadir. Ornegin V2 500-fact sonucu guclu ve gate'e
yakin olmasina ragmen resmi olarak pass sayilmamistir. 2.500-fact run ise acikca “exploratory
override” olarak etiketlenmistir. Bu ayrim tez yaziminda korunmalidir.

## 15. Mevcut Sinirlamalar ve Validity Threat'leri

### 15.1. Prompt dependence

Direct-aware satirlar olmasaydi model direct probe'a transfer edemiyordu. Bu, evaluation prompt
ailesinin training data tasarimini etkiledigini gosterir. Held-out paraphrase kullanilsa da tamamen
prompt-independent bir factual representation iddiasi kurulamaz.

### 15.2. Candidate-ranking evaluation

Candidate ranking temiz ve kontrol edilebilir bir olcumdur; ancak open-ended generation ile ayni
sey degildir. Tez iddialari “adaylar arasinda factual access” olarak dikkatli sinirlandirilmalidir.

### 15.3. Sentetik veri ekolojik gecerliligi

Sentetik fact'ler nedensel kontrol saglar, fakat gercek dunyadaki bilgi ediniminin tum karmasikligini
temsil etmez. Sonuclar kontrollu sentetik factual bindings icin gecerlidir.

### 15.4. Tek model ailesi

Ana pozitif sonuclar SmolLM2-360M uzerindedir. Genelleme icin ileride ayni frozen protocol'un baska
bir model boyutunda tekrari yararli olabilir. Ancak model degisimi yeni bir deney branch'i olarak
raporlanmalidir.

### 15.5. Relation dengesizligi

Relation'lar aday seti, token uzunlugu ve anlamsal benzerlik acisindan ayni zorlukta degildir.
Global accuracy tek basina yeterli degildir; relation-level sonuclar her zaman verilmelidir.

### 15.6. Scale ve update budget

Olcekler arasinda 252 optimizer update korunmustur. Bu kontrollu karsilastirma saglar; ancak daha
buyuk veri setinin optimum training budget'inin daha yuksek olabilecegi ihtimalini tamamen elemez.
Yine de 2.500 fact'te exact storage'in neredeyse kusursuz olmasi, salt undertraining aciklamasini
zayiflatir.

## 16. Onerilen Sonraki Bilimsel Yol

Mevcut dokumantasyona gore en savunulabilir yol sudur:

### Adim 1 - Canonical development scale'i dondur

- Relation V2 500-fact checkpoint 250'yi ana development checkpoint'i olarak tut.
- 2.500-fact checkpoint 252'yi scale-interference analysis checkpoint'i olarak koru.
- Tum bes relation'i, ozellikle `born_in` ve `lives_in` hard pair'ini koru.
- Full 25.000-fact run'i mevcut recipe ile baslatma.

### Adim 2 - Relation-conditioned retrieval objective gelistir

Yeni calisma 500 fact'te, fact veya candidate inventory degistirmeden yapilmalidir. Amac exact
storage'i yeniden ogretmek degil, held-out direct/QA prompt'larinda relation-conditioned object
secimini guclendirmektir.

Bu kol su kontrolleri korumalidir:

- held-out evaluation prompt leakage olmamasi;
- base veya frozen checkpoint baslangicinin acik belirtilmesi;
- exact retrieval'in bozulmamasi;
- relation-level ve city-swap metriklerinin raporlanmasi;
- ayni precommitted gate;
- birden fazla random seed ile tekrar edilebilirlik.

### Adim 3 - Basarili M1 membership'i dondur

M1 icin tum 25.000 fact'in robust olmasi zorunlu degildir. Ancak final M1 analysis subset'i
onceden tanimli ve yeterince buyuk olmalidir. Exact, direct ve QA'de top-1 olan fact'ler hash'li
bir liste olarak dondurulmalidir. Branch, relation, frequency ve name-type dengesi audit edilmelidir.

### Adim 4 - M2/M3'e ayni checkpoint ve budget ile gec

M1 dondurulduktan sonra:

- M2: generic, contamination-free Turkish corpus;
- M3: ayni toplam budget, Branch B Turkish fact repetition;
- her iki kol ayni M1 checkpoint'inden;
- English ve Turkish parallel probes;
- Branch A/B difference-in-differences;
- English retention ve city binding raporu.

### Adim 5 - Model-size replication'i ikincil deney yap

Compute uygun oldugunda ayni 500-fact frozen protocol daha buyuk bir modelde tekrarlanabilir. Bu,
360M modeldeki retrieval interference'in kapasiteye bagli olup olmadigini test eder. Fakat ana
protocol degismeden yalnizca model boyutu degismelidir.

## 17. Supervisor'a Sunulabilecek Kisa Anlatim

Asagidaki anlatim toplantinin ilk 3-5 dakikasinda kullanilabilir:

> Tezde, bir model Turkceye adapte edildikten sonra Turkce factual retrieval artiyorsa bunun
> Ingilizcede edinilmis bilginin transferi mi, yoksa Turkce veriden yeniden ogrenme mi oldugunu
> ayirmaya calisiyorum. Bunun icin onceden bilinmesi mumkun olmayan sentetik subject-relation-object
> fact'leri uretiyorum. Once bunlari Ingilizce ogretiyorum; sonra ayni M1 checkpoint'inden iki
> budget-matched Turkce adaptasyon kolu acacagim. Birinde hedef fact'ler Turkce corpus'ta hic yok,
> digerinde yalnizca Branch B fact'leri Turkce tekrar ediliyor.
>
> M2 ve M3'e gecmeden once M1 fact'lerinin gercekten ogrenildigini garanti etmem gerekiyordu.
> Ilk genis olcekli denemeler cok kotu sonuclar verdi; robust overlap 500 fact'te 3-5 civarinda
> kaliyor, daha fazla epoch ve daha buyuk model de bunu cozmuyordu. Tek-fact diagnostic yaptigimda
> modelin fact'i exact ve QA formatinda depoladigini, fakat direct soruya aktaramadigini gordum.
> Training'e held-out probe'dan farkli direct paraphrase'ler ekleyince tek fact, 10 fact ve 50
> fact'te neredeyse kusursuz sonuc aldim. Bu, ana eksigin prompt-format coverage oldugunu gosterdi.
>
> 500 fact'e ciktigimda eski university ve employer relation'larinda belirli adaylara collapse
> oldu. Bunlari balanced ve bagimsiz atanan field-of-study ve industry relation'lariyla degistirdim.
> Yeni V2 veri seti 500 fact'te exact 500/500, direct 378/500, QA 377/500 ve robust 329/500 verdi.
> Bu eski V1'e gore buyuk iyilesme ama precommitted gate'i dar farkla gecmiyor.
>
> Exploratory olarak 2.500 fact'e ciktigimda exact storage 2.498/2.500 kaldi; fakat robust overlap
> yuzde 65,8'den yuzde 38,3'e dustu. Dolayisiyla model bilgiyi depoluyor, ama fact yogunlugu arttikca
> relation-conditioned retrieval bozuluyor. Su an ana bilimsel sonucum storage ile retrieval'in
> ayrismasi; sonraki adimim 500-fact kontrollu olcekte retrieval objective'ini iyilestirip M1
> learned-fact subset'ini dondurmak, sonra M2/M3 transfer-relearning deneyine gecmek.

## 18. Supervisor ile Tartisilmasi Gereken Kararlar

1. M1 icin full 25.000 fact yerine dengeli ve yeterli buyuklukte frozen robust subset kullanmak
   ana tez sorusu icin kabul edilebilir mi?
2. Candidate-ranking ana metrik olarak yeterli mi, yoksa daha kucuk bir open-generation secondary
   evaluation eklenmeli mi?
3. Relation-conditioned extraction objective M1 acquisition'in parcasi mi, yoksa ayri bir
   task-specific remediation olarak mi raporlanmali?
4. 500->2.500 scale interference sonucu tezin yardimci arastirma bulgusu olarak ne kadar merkezde
   yer almali?
5. M2/M3 icin 10M, 25M ve 50M Turkish token seviyelerinin tumu gerekli mi, yoksa once tek bir
   orta budget ile feasibility run daha mi savunulabilir?
6. Ana deneyden sonra daha buyuk model replication'i zorunlu mu, yoksa compute varsa extension mi?
7. Branch C, yani yalnizca Turkce tanitilan yeni fact'ler, ana kapsamda mi kalmali yoksa opsiyonel
   extension olarak mi birakilmali?

## 19. Toplantida Yanlis Anlasilmamasi Gereken Noktalar

- M0'un dusuk olmasi hata degil, sentetik fact kontrolunun calistigini gosteren beklenen sonuctur.
- Ilk M1 basarisizliklari modelin hicbir fact ogrenemedigini kanitlamamistir; diagnostic ladder bu
  yorumu duzeltmistir.
- Exact `500/500`, robust `329/500` ile celismez. Birincisi depolama/scaffold completion, ikincisi
  held-out prompt retrieval'dir.
- V2 500-fact sonucu iyi olsa da resmi gate gecmemistir.
- 2.500-fact run precommitted progression degil, acikca exploratory override'dir.
- Proje henuz cross-lingual transfer sonucu uretmemistir; su ana kadarki sonuclar M1 feasibility ve
  methodology sonucudur.
- Negative run'lar bosuna degildir; undertraining, model size, generic repetition, biography mix,
  two-stage QA ve basit ranking gibi aciklamalari kontrollu bicimde elemislerdir.

## 20. Kisa Terimler Sozlugu

- **Fact:** Bir subject-relation-object uclusu.
- **Acquisition:** Modelin yeni fact'i egitimden edinmesi.
- **Storage:** Fact'in egitim scaffold'una yakin bicimde modelde erisilebilir olmasi.
- **Retrieval:** Fact'in bir probe altinda dogru aday olarak geri cagrilmasi.
- **Binding:** Dogru subject, relation ve object'in birbirine baglanmasi.
- **Candidate collapse:** Modelin bir relation'da cok sayida subject icin ayni baskin adayi secmesi.
- **Exact-prefix:** Egitim ifadesine yakin completion testi.
- **Held-out direct:** Egitimde gorulmeyen dogrudan soru bicimi.
- **QA-matched:** Question/Answer scaffold'unda held-out probe.
- **Triple robust:** Exact, direct ve QA gorunumlerinin ucunde de top-1 olan fact.
- **Branch A:** Turkce adaptasyonda hedef fact tekrari olmayan transfer-only kosulu.
- **Branch B:** Turkce adaptasyonda hedef fact'in tekrar edildigi reaffirmation/relearning kosulu.
- **M0:** Base model factual baseline.
- **M1:** Ingilizce fact acquisition.
- **M2:** Target fact tekrari olmayan generic Turkish adaptation.
- **M3:** Branch B fact repetition iceren budget-matched Turkish adaptation.
- **Precommitted gate:** Sonuclar gorulmeden once belirlenen ilerleme esigi.
- **Exploratory override:** Resmi gate gecmeden, analiz amaciyla acikca etiketlenmis ek deney.

## 21. Tek Cumlelik Guncel Durum

Model sentetik Ingilizce fact'leri exact olarak neredeyse kusursuz depolayabiliyor; ancak fact
yogunlugu arttikca held-out prompt'larda relation-conditioned retrieval belirgin bicimde bozuluyor,
bu nedenle full M1 ve Turkce M2/M3 deneylerinden once 500-fact kontrollu olcekte robust retrieval
problemini cozmemiz ve dondurulmus bir learned-fact subset'i olusturmamiz gerekiyor.
