# 144 — Supervisor Geri Bildirimi ve Bilimsel Yeniden Hizalama

**Tarih:** 2026-08-06  
**Durum:** Toplantı notları kayda geçirildi; yorum düzeltmesi yapıldı; yeni eğitim henüz yetkili değil  
**Kapsam:** M1 model seçimi, Türkçe dil adaptasyonu, Exposé ile M2-A/M2-B tasarımının uzlaştırılması

## 1. Bu belgenin amacı

Bu belge, Max ile yapılan son görüşmede alınan notları bilimsel kararlar hâline getirir ve mevcut
deney kaydını geriye dönük olarak değiştirmeden projenin yönünü düzeltir. İki şeyi birbirinden
ayırır:

1. Ağustos 2026'da tamamlanan Qwen `M2-clean/M3-fact` ailesinin **gerçek ve korunacak pilot
   sonucu**;
2. tez sorusunu daha güçlü biçimde sınamak için bundan sonra izlenecek **literatür-öncelikli yeni
   deney tasarımı**.

Bu belge yeni bir HU eğitimi başlatma izni değildir. Uygulanabilir rota ve açılma kapıları
Doküman 145'te tanımlanmıştır.

## 2. Max'ten alınan ana geri bildirimler

Toplantı notlarından çıkarılan bilimsel mesajlar şunlardır:

### 2.1 Amaç en yüksek skoru üretmek değil, anlamlı bir karşılaştırma kurmaktır

Projede daha önce özellikle M1'i her donmuş kapıdan geçirebilmek için çok sayıda mimari, recipe,
checkpoint ve probing varyantı denenmiştir. Bu çalışmalar önemli kanıt üretmiştir; ancak yeni
aşamada sonsuz recipe optimizasyonu yapmak tez katkısını güçlendirmeyebilir.

Yeni ilke:

> Modeli veya müdahaleyi mümkün olan en iyi skora zorlamak yerine, literatürde gerekçesi bulunan,
> değişkenleri açık ve sonucu yorumlanabilir bir deney kurulmalıdır.

Başarılı, negatif veya karışık sonuçların üçü de değerlidir; temel şart deneyin doğru manipülasyonu
uygulaması ve ölçmesidir.

### 2.2 Kaynak modelin Türkçe geçmişi deneyin nedensel yorumunu belirler

Cross-lingual adaptation iddiası için seçilen başlangıç modelinin:

- instruction-tuned değil, uygun eğitim aşamasındaki **base/pretrained** varyant olması;
- ağırlıklı olarak İngilizceyle eğitilmiş veya Türkçeyi hiç/hemen hemen hiç görmemiş olduğuna dair
  belgelenebilir kanıt sunması;
- adaptasyon öncesinde Türkçe için gelişmeye açık yeterli `headroom` bırakması;
- yine de M1'de İngilizce sentetik olguları öğrenebilecek kapasitede olması

gerekir.

Qwen2.5-1.5B base güçlü bir M1 sonucu verdiği için korunacaktır; fakat model kartı 29'dan fazla dil
desteği bildirdiğinden “Türkçe görmemiş temiz kaynak model” olarak kullanılamaz. Yeni model
taramasında Qwen bir **güçlü çokdilli pozitif kontrol** olarak kalmalı, tek varsayılan ana model
olmamalıdır.

### 2.3 Türkçe adaptasyonun gerçekten çalıştığı doğrudan gösterilmelidir

Yalnızca sentetik olgu sorularına bakmak, modelin Türkçe dil modellemesinin gelişip gelişmediğini
kanıtlamaz. Adaptasyon müdahalesi için ayrıca:

- donmuş ve eğitimden ayrı Türkçe metinde PPL;
- base modele uygun bir Türkçe yetenek ölçümü;
- tokenizer verimliliği/fragmentation betimlemesi;
- İngilizce PPL veya eşdeğer bir kaynak-dil koruma ölçümü

gereklidir.

Türkçe yetenek kazanımı gözlenmezse, olgu transferindeki sıfır sonuç “bilgi transferi yok” diye
yorumlanamaz; önce dil köprüsünün kurulmadığı düşünülmelidir.

### 2.4 Türkçe dışındaki dil adaptasyonu literatürü de tasarıma dâhil edilmelidir

Araştırma yalnızca Türkçe modellerle sınırlı kalmamalıdır. Arapça, Kazakça ve pretraining sırasında
görülmemiş/düşük kaynaklı dillere adaptasyon çalışmaları şu tasarım kararları için doğrudan kanıt
sağlar:

- base mi instruction model mi kullanılmalı;
- tam continual pretraining mi, LoRA/adapters mı kullanılmalı;
- hedef dil verisi tek başına mı, İngilizce replay ile mi kullanılmalı;
- tokenizer genişletmesi gerekli mi;
- ne büyüklükte veri dozu anlamlıdır;
- catastrophic forgetting nasıl ölçülür.

## 3. Exposé düzeltmesi: M2 ve M3 ardışık aşamalar değildir

`documentation/Expose.pdf` sayfa 6'daki çekirdek karşılaştırmanın doğru operasyonel karşılığı iki
**paralel kardeş adaptasyon koludur**:

```text
aynı donmuş M1
├── M2-A: Türkçe genel korpus, hedef sentetik olgular yok
└── M2-B: aynı Türkçe korpus + önceden belirlenmiş Türkçe sentetik olgu tekrarları
```

M2-B, M2-A'dan başlatılmaz. İki kol da aynı M1 checkpoint'inden başlar. Bundan sonra yeni tasarımda
ana adlandırma `M2-A / M2-B` olacaktır. Böylece “M3 daha sonraki bir eğitim aşamasıdır” izlenimi
ortadan kalkar.

Birincil bilimsel karşılaştırma:

```text
M2-B − M2-A
```

olmalıdır. Bu fark, aynı Türkçe dil adaptasyonu altında hedef olguların Türkçe olarak yeniden
görülmesinin ek etkisini ölçer.

## 4. Tamamlanan Qwen pilotunun bu düzeltmeyle ilişkisi

Eski belgeler veya artifact adları geriye dönük olarak değiştirilmeyecektir. Çapraz okuma için:

| Tarihsel ad | Yeni kavramsal karşılık | Başlangıç |
|---|---|---|
| `M2-clean` | `M2-A` benzeri, hedef olgusuz Türkçe adaptasyon kolu | donmuş Qwen M1 |
| `M3-fact` | `M2-B` benzeri, Türkçe olgu tekrarına sahip kardeş kol | aynı donmuş Qwen M1 |

Dolayısıyla tamamlanan koşu teknik olarak M2'den M3'e ardışık eğitim yapmadı; doğru biçimde iki
kardeş kol kullandı. “M2/M3'ü tamamen yanlış çalıştırdık” sonucu doğru değildir. Yanlış veya zayıf
olan noktalar daha çok **adlandırma, motivasyon ve adaptasyon dozunun yeterliliği** ile ilgilidir.

Pilotun korunan sonucu:

- iki seed ve dört `checkpoint-128` endpoint tamamlandı;
- 96/96 aynı değerlendirme slice'ı iki kola da uygulandı;
- EN→EN koruma kapısı geçti;
- M1 TR→EN yaklaşık `%52` iken olgusuz Türkçe kol yaklaşık `%33`, olgu tekrarlı kol yaklaşık
  `%35` verdi;
- M2-B-benzeri kolun M2-A-benzeri kola göre betimsel faydası yaklaşık `+1.9` puandı;
- donmuş birincil interaction ölçütü iki seed'in ikisinde de geçmediği için sonuç
  `primary_success_criterion_not_met` olarak kaldı.

Bu bir altyapı hatası değildir. Ancak aşağıdaki sınırlamalar nedeniyle tez sorusuna son cevap da
değildir:

- adaptasyon her kol için yalnızca `1,048,576` tokenlık saf Türkçe Wikipedia verisiydi;
- Wikipedia dil ve alan çeşitliliği açısından dar bir korpustur;
- endpoint M2-A/M2-B modellerinde Türkçe PPL ve bağımsız Türkçe yetenek ölçümü ana sonuç paketinin
  parçası olarak tamamlanmadı;
- Qwen başlangıçtan itibaren çokdillidir ve Türkçe exposure miktarı kesin olarak bilinmemektedir;
- bu nedenle düşük factual sonuç, “Türkçe öğrenildi ama bilgi transfer olmadı” ile “Türkçe köprü
  yeterince kurulmadı” açıklamalarını temiz biçimde ayıramaz.

Bu koşu bundan sonra **Qwen Wikipedia-only, 1M-token pilotu** olarak anılmalıdır.

## 5. Base ve instruction-tuned aşaması hakkındaki karar

Tezin çekirdek sorusu dil bilgisi adaptasyonu ve factual erişim olduğundan ana deney için şimdilik
önerilen aşama **base/pretrained causal LM** aşamasıdır. Gerekçeler:

- causal language-model continual pretraining ile aynı eğitim hedefini kullanır;
- chat template ve instruction-following davranışı factual erişim ölçümüne ek karıştırıcı getirmez;
- M1 sentetik olgu edinimi ve M2-A/M2-B dil adaptasyonu aynı temel modelleme aşamasında kalır;
- MODA da dil edinimi ile sonraki task alignment aşamasını açıkça ayırır.

Instruction-tuned bir model ancak literatür taraması tez sorusunun yaygın uygulama koşulunu bunun
daha iyi temsil ettiğini gösterirse ayrı bir extension/control olarak düşünülmelidir. Base ve
instruction model sonuçları tek deney gibi birleştirilmemelidir.

## 6. Yeni bilimsel çerçeve

Güncellenmiş ana soru:

> Ağırlıklı olarak İngilizceyle eğitilmiş bir base dil modeli, İngilizce olarak öğrendiği sentetik
> olgulara yalnızca genel Türkçe continual pretraining sonrasında Türkçe sorgular üzerinden
> erişebilir mi; aynı olguların Türkçe tekrar edilmesi bu erişime ne kadar ek katkı sağlar?

Bu soru üç ayrı olguyu ölçer:

1. **M1 acquisition:** Model İngilizce sentetik olguyu gerçekten öğrendi mi?
2. **Language adaptation:** Genel Türkçe korpus modelin Türkçe dil yeteneğini gerçekten geliştirdi
   mi?
3. **Transfer vs. relearning:** Türkçe olgu exposure'ı olmayan M2-A ile olgu tekrarlı M2-B
   arasındaki fark nedir?

## 7. Değişmeyen bilimsel ve operasyonel ilkeler

- Tamamlanmış negatif sonuçlar saklanacak ve tezde raporlanacaktır.
- Checkpoint, threshold veya metric sonuç görüldükten sonra değiştirilirse açıkça exploratory olarak
  etiketlenecektir.
- M2-A ve M2-B aynı M1, seed, genel korpus sırası ve toplam token/update bütçesini kullanacaktır.
- M2-B'ye sentetik olgu satırları **ekstra token olarak eklenmeyecek**; eşleşmiş nötr Türkçe
  tokenların yerine konacaktır.
- İki kol da aynı donmuş testlerin tamamına girecektir.
- Eğitim verisi ile Türkçe değerlendirme verisi ve sentetik subject/object alias'ları arasında
  contamination taraması yapılacaktır.
- HU home depolama kuralları ve scratch preflight zorunlulukları değişmemiştir.

## 8. Bu geri bildirimden doğan somut iş paketleri

1. İngilizce-ağırlıklı/Türkçe-görmemiş base model adaylarının belgeli provenance denetimi.
2. Adayların mevcut M1 kanıtıyla ve sınırlı, önceden donmuş yeni M1 ekranıyla karşılaştırılması.
3. Türkçe model ve korpus literatürünün kaynak, temizlik, lisans, token sayısı ve eğitim dozu
   açısından çıkarılması.
4. Wikipedia-only korpusun `CulturaX`, `mC4 + OSCAR` ve `vngrs-web-corpus` seçenekleriyle
   karşılaştırılması.
5. M2-A açılmadan önce Türkçe PPL/yetenek manipulation-check paketinin dondurulması.
6. Daha sonra aynı M1'den çıkan eş-bütçeli M2-A/M2-B ana karşılaştırmasının yapılması.

Bu işlerin sırası, seçim kapıları ve durdurma koşulları Doküman 145'te verilmiştir.

## 9. Kaynaklar ve kanıt izi

- Proje tasarımı: [`Expose.pdf`](./Expose.pdf), özellikle sayfa 6.
- Tamamlanan pilot: [`136_QWEN_M2_M3_ENDPOINT_EVALUATION_GPU_ALLOCATION_STATUS.md`](./136_QWEN_M2_M3_ENDPOINT_EVALUATION_GPU_ALLOCATION_STATUS.md).
- Bilimsel yorum: [`138_QWEN_M2_M3_COMPLETED_MILESTONE_AND_SCIENTIFIC_INTERPRETATION_EN.md`](./138_QWEN_M2_M3_COMPLETED_MILESTONE_AND_SCIENTIFIC_INTERPRETATION_EN.md).
- Exploratory mekanizma analizi: [`142_QWEN_M2_M3_EXPLORATORY_MECHANISM_ANALYSIS_RESULT_EN.md`](./142_QWEN_M2_M3_EXPLORATORY_MECHANISM_ANALYSIS_RESULT_EN.md).
- Son artifact freeze: [`143_QWEN_M2_M3_ARTIFACT_RETENTION_FREEZE_AND_STORAGE_AUDIT_EN.md`](./143_QWEN_M2_M3_ARTIFACT_RETENTION_FREEZE_AND_STORAGE_AUDIT_EN.md).
- Max görüşme notları: 2026-08-06 tarihinde kullanıcı tarafından aktarılan sözlü toplantı notları;
  doğrudan alıntı değil, bu belgede yapılandırılmış yorumdur.

