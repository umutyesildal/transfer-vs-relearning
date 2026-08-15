# M1 Tamamlanma Güncellemesi

**Supervisor bilgilendirme notu**  
**Tarih:** 13 Temmuz 2026  
**Proje:** Transfer vs. Relearning in Cross-Lingual Factual Adaptation

Merhaba Max,

Bu notu projenin M1, yani İngilizce factual acquisition aşamasında ulaştığımız önemli sonucu
özetlemek için hazırladım. Uzun süredir çözmeye çalıştığımız temel problem, modelin sentetik
fact'leri yalnızca training formatında ezberlemesi fakat yeni İngilizce soru biçimlerinde güvenilir
şekilde geri çağıramamasıydı. Son kontrollü deneyler bu problemi 500-fact geliştirme koşulunda
neredeyse tamamen çözdü.

Kısa sonuç şu:

> SmolLM2-1.7B, 500 bağımsız sentetik fact'i İngilizce olarak öğrendi ve bunları hem training'e
> yakın exact-prefix formatında hem de iki farklı held-out soru formatında iki bağımsız training
> order'ında %99'un üzerinde robust başarıyla geri çağırdı. Önceden belirlenen M1 gate iki koşuda
> da büyük marjla geçti. Bu nedenle 500-fact Relation V2 çerçevesinde M1'i tamamlanmış kabul ediyor
> ve M2/M3 Türkçe adaptasyon deneylerine geçmeye hazırız.

## 1. Tezde M1 Neden Kritik?

Tezin ana sorusu, İngilizce öğrenilmiş bir fact'in Türkçe adaptasyon sonrasında Türkçe olarak
erişilebilir hale gelmesinin gerçek bir cross-lingual transfer mı, yoksa Türkçe veriden relearning
mi olduğudur.

Bu soruyu cevaplayabilmek için önce şu koşulun sağlanması gerekir:

> M2 ve M3 başlamadan önce fact'in İngilizce olarak gerçekten öğrenilmiş ve farklı İngilizce prompt
> biçimlerinde güvenilir şekilde erişilebilir olması gerekir.

M1'de öğrenilmemiş bir fact'in M2 sonrasında Türkçe cevaplanamaması transfer hakkında anlamlı bir
negatif kanıt üretmez. Bu nedenle M1 yalnızca bir hazırlık aşaması değil, sonraki nedensel analizin
geçerlilik koşuludur.

## 2. Deney Koşulu

Güncel Relation V2 geliştirme seti şu yapıdadır:

- 100 sentetik subject;
- subject başına 5 fact;
- toplam 500 fact;
- 5 relation: `profession`, `born_in`, `lives_in`, `field_of_study` ve `works_in_industry`;
- fact başına 7 İngilizce acquisition satırı;
- toplam 3.500 training satırı;
- bağımsız ve dengeli subject-relation-object atamaları;
- target fact'lerin base modelde önceden bilinmediğini destekleyen chance-level M0 sonucu.

`field_of_study` ve `works_in_industry`, eski proper-name-heavy `studied_at` ve `works_at`
relation'larının yerine kullanıldı. Bu değişiklik, modelin birkaç baskın kurum adına çökmesini
azaltırken tezin subject-relation-object binding sorusunu korudu.

## 3. Başarıyı Nasıl Ölçüyoruz?

Modeli open generation ile değil, relation'a özel dondurulmuş candidate inventory üzerinden
değerlendiriyoruz. Her candidate aynı prompt altında skorlanıyor ve doğru object'in rank'i
hesaplanıyor.

Üç ayrı görünüm kullanılıyor:

1. **Exact-prefix:** Training scaffold'una en yakın tamamlama. Fact'in depolanıp depolanmadığını
   güçlü biçimde test eder.
2. **Held-out direct:** Training'de aynen bulunmayan doğrudan İngilizce soru.
3. **Held-out QA-matched:** Aynı held-out soru, `Question: ... Answer:` scaffold'u içinde.

Ana robust metric:

```text
direct rank 1 AND QA rank 1
```

`Triple` metric buna exact-prefix rank 1 koşulunu da ekler.

Sonuçları görmeden önce belirlenen M1 gate şuydu:

| Metric | Gate |
|---|---:|
| Exact | en az 450/500 |
| Direct | en az 400/500 |
| QA | en az 400/500 |
| Direct/QA overlap | en az 350/500 |

Bu eşikler sonuç görüldükten sonra değiştirilmedi.

## 4. Önceki Darboğaz

SmolLM2-360M ile Relation V2 500-fact deneyinde exact storage kusursuzdu, fakat held-out retrieval
gate'i dar biçimde kaçırdı:

| Model | Exact | Direct | QA | Overlap |
|---|---:|---:|---:|---:|
| SmolLM2-360M | 500 | 378 | 377 | 329 |

Bu sonuç önemliydi: model fact'leri kaybetmiyor, fakat relation ve yeni prompt üzerinden doğru
object'e erişmekte zorlanıyordu.

Exploratory 2.500-fact deneyinde exact storage %99,92 seviyesinde kalırken overlap %38,32'ye
düştü. Aynı nested ilk 500 fact'in overlap'i 329'dan 188'e geriledi. Bu bulgu storage kapasitesi ile
prompt-robust retrieval/binding kapasitesinin ayrı olduğunu gösterdi.

## 5. Kontrollü Kapasite Deneyi

Yeni deneyde yalnızca model kapasitesini artırdık:

```text
SmolLM2-360M -> SmolLM2-1.7B
```

Aşağıdaki bilimsel değişkenler sabit tutuldu:

- aynı 500 fact ve aynı 3.500 satır;
- aynı answer-only objective;
- aynı learning rate: `1e-4`;
- aynı 36 epoch;
- aynı effective batch: 500;
- aynı 252 optimizer update;
- aynı scheduler, warmup ve weight decay;
- aynı exact/direct/QA evaluator;
- aynı precommitted gate.

1.7B modelin A100'e sığması için yalnızca operasyonel batch decomposition değişti: micro-batch 10
ve gradient accumulation 50 kullanıldı. Effective batch ve optimizer-step budget değişmedi.

## 6. Ana Sonuç: Seed 42

İlk geçerli 1.7B koşusunda en iyi checkpoint 200 oldu:

| Metric | Sonuç | Oran |
|---|---:|---:|
| Exact | 500/500 | %100,0 |
| Direct | 499/500 | %99,8 |
| QA | 498/500 | %99,6 |
| Direct/QA overlap | 497/500 | %99,4 |
| Triple | 497/500 | %99,4 |

Checkpoint 50'den itibaren precommitted gate geçti. Checkpoint 75 sonrasında performans neredeyse
tamamen doygun ve kararlı kaldı.

360M referansına göre mutlak değişim:

| Metric | 360M | 1.7B | Değişim |
|---|---:|---:|---:|
| Exact | 500 | 500 | 0 |
| Direct | 378 | 499 | +121 |
| QA | 377 | 498 | +121 |
| Overlap | 329 | 497 | +168 |

Exact storage zaten 360M modelde doygundu. Dolayısıyla 1.7B modelin temel katkısı daha fazla fact
ezberlemek değil, depolanmış subject-relation-object binding'lerine held-out promptlar üzerinden
erişebilmek oldu.

## 7. Bağımsız Training-Order Replication

Sonucun tek bir data order'a bağlı olmadığını test etmek için ikinci bir koşu yaptık. Train ve
validation dosyaları değişmedi; split seed 42'de kaldı. Training seed ve data-order seed 43'e
alındı.

Bu noktada önemli bir metodolojik kontrol yaptık. İlk seed-43 denemesinde training seed değişmişti,
ancak data-order seed hâlâ 42 idi. SmolLM2-1.7B'de attention dropout sıfır olduğu için bu koşu
deterministik olarak seed-42 ağırlıklarını yeniden üretti. Bunu loss eğrisi ve checkpoint byte
karşılaştırmasıyla fark ettik. Bu koşulu bağımsız replication olarak raporlamadık; yalnızca
reproducibility control olarak kaydettik.

Ardından training koduna split seed'den bağımsız `data_seed` desteği ekledik ve test ettik. Geçerli
replication'da split seed 42, training seed 43 ve data seed 43 kullanıldı. Loss eğrisi seed-42'den
ayrıştı ve gerçek bağımsız training path oluştu.

Seed-43 için seçilen checkpoint 75 sonucu:

| Metric | Sonuç | Oran |
|---|---:|---:|
| Exact | 500/500 | %100,0 |
| Direct | 500/500 | %100,0 |
| QA | 499/500 | %99,8 |
| Direct/QA overlap | 499/500 | %99,8 |
| Triple | 499/500 | %99,8 |

## 8. İki Koşunun Birlikte Sonucu

| Koşu | Seçilen checkpoint | Exact | Direct | QA | Overlap | Triple |
|---|---:|---:|---:|---:|---:|---:|
| Seed 42 | 200 | 500 | 499 | 498 | 497 | 497 |
| Seed 43 / data seed 43 | 75 | 500 | 500 | 499 | 499 | 499 |
| İki koşu ortalaması | - | 500,0 | 499,5 | 498,5 | 498,0 | 498,0 |

Robust overlap:

```text
360M reference:  %65,8
1.7B seed 42:    %99,4
1.7B seed 43:    %99,8
```

Bu nedenle ana kapasite sonucu tek bir checkpoint veya data order'a bağlı değildir.

## 9. Kalan Tekrarlanabilir Hata

Seed-43 seçilmiş checkpointte yalnızca bir non-triple fact vardır:

```text
Meggy Melvin -> lives_in -> Omaha
```

- exact-prefix: doğru, Omaha rank 1;
- held-out direct: doğru, Omaha rank 1;
- QA-matched: Gaziantep rank 1, Omaha rank 2.

Aynı fact seed-42 checkpointteki üç hatadan biridir. Bu durum broad stochastic instability yerine
dar ve tekrarlanabilir bir QA prompt-binding hard case'e işaret ediyor. `lives_in` relation'ını
çıkarmayı gerektiren bir neden değildir; relation bilimsel olarak özellikle değerlidir çünkü
`born_in` ile aynı city inventory'yi paylaşır.

## 10. Bilimsel Yorum

Bu sonuç şu iddiayı güçlü biçimde destekliyor:

> 360M modelde gördüğümüz 500-fact retrieval plateau'su, Relation V2 verisinin veya answer-only
> acquisition objective'inin temel bir başarısızlığı değildi. Darboğaz büyük ölçüde modelin
> depolanmış binding'lere farklı promptlar üzerinden erişme kapasitesiydi. 1.7B model aynı veri ve
> aynı optimization budget ile bu açığı neredeyse tamamen kapattı.

Bu sonuç aynı zamanda önceki 2.500-fact bulgusunu geçersiz kılmaz. Tam tersine yeni bir araştırma
sorusu açar: 1.7B model 500 fact'te çözdüğü binding/retrieval problemini daha yüksek fact
yoğunluğunda ne ölçüde koruyabilir? Ancak bu scale sorusu M2/M3'e geçişi geciktirmemelidir.

## 11. M1 Tamamlandı mı?

Evet, fakat kapsamı doğru ifade etmek önemlidir:

> M1, Relation V2 500-fact ve SmolLM2-1.7B koşulu için tamamlandı.

Tamamlanma kriterleri:

- exact storage gate geçti;
- iki held-out English retrieval gate'i geçti;
- robust overlap gate geçti;
- sonuç bağımsız data-order replication ile tekrarlandı;
- selected checkpointler model-only artifact olarak donduruldu;
- model manifestleri ve SHA-256 hashleri üretildi;
- büyük artifactler shared student home yerine scratch storage'da tutuluyor.

Dondurulan modeller:

- canonical primary trajectory: seed-42 checkpoint 200;
- replication/control trajectory: seed-43 checkpoint 75.

## 12. Bu Sonuç Ne Anlama Gelmiyor?

Bu sonucu gereğinden fazla geniş yorumlamamak önemli:

- Henüz İngilizce fact'lerin Türkçeye transfer olduğunu göstermedik.
- Henüz M2 generic Turkish adaptation sonrasında English retention ölçmedik.
- Henüz M3 Branch-B Turkish repetition etkisini ölçmedik.
- Sonuç kontrollü sentetik 500-fact koşulu için geçerlidir; doğrudan 25.000 fact'e genellenemez.
- Candidate-ranking başarısı open-generation dil kalitesiyle aynı şey değildir.
- Şimdilik yalnızca SmolLM2 ailesi üzerinde güçlü kanıtımız vardır.

Dolayısıyla bu sonuç tezin nihai cevabı değil, nihai nedensel deneyi artık güvenilir biçimde
başlatabilmemizi sağlayan kritik M1 kapanışıdır.

## 13. Sıradaki Aşama: M2 ve M3

Önerilen sonraki yol:

### M2 - Generic Turkish adaptation

- canonical M1 seed-42 checkpoint 200'den başlamak;
- contamination kontrolünden geçmiş genel Türkçe corpus kullanmak;
- target synthetic fact'leri Türkçe adaptasyon verisinde göstermemek;
- adaptasyon sonrası English exact/direct/QA retention ölçmek;
- aynı fact'ler için Turkish direct/QA access ölçmek.

M2 sonrasında Türkçe retrieval artışı, target fact'ler Türkçe corpus'ta bulunmadığı için
cross-lingual access/transfer lehine kanıt oluşturabilir.

### M3 - Turkish repetition / relearning condition

- aynı frozen M1 checkpointinden bağımsız olarak başlamak;
- M2 ile token ve optimizer budget'ını eşlemek;
- kontrollü tek fark olarak Branch-B fact'lerin Türkçe tekrarlarını eklemek;
- Branch A'yı transfer-only, Branch B'yi transfer-plus-relearning koşulu olarak karşılaştırmak.

Ana analiz:

```text
(M3 - M2 değişimi, Branch B) - (M3 - M2 değişimi, Branch A)
```

Seed-43 checkpoint 75, primary M2/M3 trajektorisine paralel replication/control kolu olarak
kullanılabilir. Compute maliyetini yönetmek için önce canonical seed-42 M2/M3 pilotu, ardından
gerekli checkpointlerde seed-43 replication öneriyorum.

## 14. Reproducibility ve Operasyonel Not

İki selected model için aşağıdaki materyaller oluşturuldu:

- model-only `model.safetensors` kopyası;
- config;
- local model manifest;
- source training run ve checkpoint metadata'sı;
- SHA-256 hash dosyası.

Ayrıca training/evaluation artifactlerinin yanlışlıkla shared student home fileserver'da birikmesi
sonrasında storage lifecycle düzeltildi. Home kullanımı 474 GB'tan 7,88 GiB'a indirildi; runs,
models, datasets, caches ve evaluation çıktıları `/vol/tmp` veya `/vol/tmp2` üzerinde tutuluyor ve
repo içindeki eski yollar symlink ile korunuyor. Bundan sonra scale-up öncesi ve sonrası storage
audit zorunlu olacak.

## 15. Supervisor ile Tartışmak İstediğim Kararlar

1. M2/M3 primary trajectory için canonical seed-42 checkpoint 200 seçimimizi onaylıyor muyuz?
2. İlk M2 pilotunda mevcut 500-fact frozen membership'in tamamını mı, yoksa ayrıca
   relation-stratified bir sensitivity subset'i mi raporlamalıyız?
3. Seed-43 replication kolunu her M2/M3 checkpointinde mi, yoksa yalnızca seçilmiş final
   checkpointlerde mi çalıştırmalıyız?
4. 1.7B modelin 2.500-fact scale kontrolü M2/M3'ten önce mi, yoksa ana cross-lingual deneyden sonra
   ikincil kapasite analizi olarak mı yapılmalı?
5. Tez anlatısında 360M storage-vs-retrieval ayrımını ve 1.7B capacity resolution sonucunu ayrı bir
   ana bulgu olarak ne kadar öne çıkarmalıyız?

## 16. Tek Paragraflık Özet

Bu projede önce sentetik fact'lerin depolanabildiğini fakat yeni prompt biçimlerinde güvenilir
şekilde geri çağrılamadığını gördük. Relation V2 ve direct-aware answer-only acquisition ile 360M
model 500 fact'in tamamını exact olarak depoladı, ancak robust overlap %65,8'de kaldı. Veri,
objective, exposure ve evaluator sabit tutularak yalnızca model 1.7B'ye çıkarıldığında overlap
seed-42'de %99,4'e, bağımsız data-order replication'da %99,8'e yükseldi. Her iki koşu da önceden
belirlenen M1 gate'i büyük marjla geçti ve selected modeller manifest/hash ile donduruldu. Bu nedenle
Relation V2 500-fact koşulunda M1 tamamlandı; proje artık generic Turkish adaptation M2 ile Turkish
repetition/relearning M3 arasındaki nedensel cross-lingual karşılaştırmaya geçmeye hazır.

Bu sonucu sonunda paylaşabilmek gerçekten sevindirici. Uzun negatif deney zinciri boşa gitmedi;
tam tersine, hangi failure mode'u ölçtüğümüzü netleştirdi ve bugünkü pozitif sonucun neden güvenilir
olduğunu gösteren kontrol yapısını oluşturdu.
