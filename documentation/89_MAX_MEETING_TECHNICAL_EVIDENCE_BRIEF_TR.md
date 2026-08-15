# Max Görüşmesi İçin Teknik Kanıt ve Savunma Notu

**Tarih:** 14 Temmuz 2026  
**Kapsam:** Max'in M1 training setup, hyperparameter, loss, prompt ayrışması,
degeneration ve dataset sorularına sözlü olarak doğru cevap verebilmek.

Bu belge bir e-posta taslağı değildir. Amaç, görüşmede kısa cevap verebilmek ve takip sorusu
geldiğinde cevabın arkasındaki deneysel kanıtı gösterebilmektir.

## 1. Otuz Saniyelik Ana Anlatı

İlk deneylerde training ve validation loss düşüyordu fakat bu, held-out sorularda fact
retrieval'a dönüşmüyordu. Bu yüzden yalnızca loss'a bakmayı bıraktık ve exact-prefix,
held-out direct ve held-out QA olmak üzere üç ayrı retrieval görünümü tanımladık.

Daha sonra problemin üç ayrı bileşeni olduğunu gördük:

1. training formatında fact'i depolamak;
2. farklı prompt biçiminde doğru fact'e erişmek;
3. aynı subject'e ait fact'i doğru relation'a bağlamak.

Direct-aware answer-only recipe küçük ölçekte başarılı oldu. SmolLM2-360M, 500 Relation V2
fact'inin tamamını exact formatta depoladı fakat yalnız 329/500 fact iki held-out promptta
birden doğruydu. Aynı data ve optimization budget ile yalnız model kapasitesini 1.7B'ye
çıkardığımızda robust overlap iki bağımsız data order'ında 497/500 ve 499/500 oldu.

Bu nedenle güncel kanıt, 500-fact koşulundaki eski ayrışmanın yalnızca düşük loss veya daha
fazla exposure problemi olmadığını; büyük ölçüde prompt-robust binding/access kapasitesi
problemi olduğunu gösteriyor.

## 2. Max'in Soruları ve Kanıt Durumu

| Max'in sorusu | Şu anki cevap | Kanıt durumu |
|---|---|---|
| "Increasing training intensity" ne demek? | Bu ifade fazla belirsizdi. Tarihsel olarak daha fazla epoch/exposure ve farklı recipe'leri kastetti; tek bir kontrollü değişken değildi. | Tam cevaplanıyor. |
| Güncel hyperparameter'lar ne? | 1.7B, LR 1e-4, 36 epoch, effective batch 500, 252 update, %2 warmup, constant schedule, weight decay 0. | Config ile tam doğrulanıyor. |
| Farklı LR'lar denendi mi? | 2e-5, 5e-5 ve 1e-4 farklı tarihsel recipe'lerde denendi. Bunlar aynı setup üzerinde sistematik LR sweep değildir. Final 1.7B recipe'de 1e-4 kullanıldı. 2e-4 denenmedi. | Tam ve dürüst cevap. |
| Loss curve nasıl? | Başarılı 1.7B run'da validation loss yaklaşık 0.84'ten 0.007'ye düştü; retrieval checkpoint 50'de gate'i geçti ve 75'ten sonra stabilize oldu. | Mevcut raporlarla cevaplanıyor. |
| Promptlar neden ayrışıyordu? | 360M exact storage yapabiliyor fakat held-out relation/prompt üzerinden binding'e erişemiyordu. 1.7B aynı setup ile ayrışmayı neredeyse kapattı. | İki seed ile güçlü kanıt. |
| Model genel sorgulara hâlâ cevap verebiliyor mu? | Evet; genel narrative, explanation, procedure ve QA continuation'ları üretebiliyor. Ancak yanıtlar belirgin biçimde kısaldı. | Base-vs-M1 kontrolü tamamlandı. |
| Model dejenere olmuş olabilir mi? | Broad/fact-only collapse yok; fakat generic PPL %17--19 arttı ve 30/30 çıktı EOS ile erken bitti. Sonuç: measurable drift ve short-answer bias. | İki bağımsız M1 koşusu ve erken checkpoint'lerle ölçüldü. |
| V1 biographies zaten fact'leri birlikte içermiyor muydu? | Evet, her biography subject'in beş V1 fact'ini içeriyordu. Ancak V1'de field_of_study yoktu. | Dataset dosyalarıyla doğrulanıyor. |
| Neden dataset değişti? | studied_at ve works_at candidate collapse gösterdi. V2 bunları field_of_study ve works_in_industry ile değiştirdi. | V1/V2 kontrollü karşılaştırması var. |
| Relation başına accuracy raporlanıyor mu? | Evet. Tüm beş relation aynı run'da birlikte train ediliyor ve exact/direct/QA/overlap ayrı raporlanıyor. | Tam cevaplanıyor. |

## 3. "Increasing Training Intensity" İçin Doğru Açıklama

Bu ifade görüşmede savunulmamalı; düzeltilmelidir:

> "I used that phrase too loosely. I meant that we tried longer exposure and stronger
> acquisition recipes, but those experiments did not change only one variable. The important
> point is that lower loss and more exposure did not reliably improve held-out retrieval."

### 3.1. İlgili tarihsel LR/epoch denemeleri

| Model/recipe | LR | Epoch | Ana sonuç |
|---|---:|---:|---|
| GPT-2 plain CLM | 5e-5 | 1 | Loss düştü; robust overlap zayıf kaldı. |
| GPT-2 plain CLM | 1e-4 | 1 | Eval loss 2.002; en iyi overlap 5/500. |
| GPT-2 plain CLM | 5e-5 | 3 | Eval loss 1.830; en iyi overlap 3/500. |
| SmolLM2-360M plain CLM | 5e-5 | 1 | En iyi overlap 3/500. |
| SmolLM2-360M plain CLM high-exposure | 2e-5 | 5 | En iyi overlap 2/500; daha uzun exposure çözmedi. |
| SmolLM2-1.7B QA-mix | 5e-5 | 1 | Düşük loss'a rağmen overlap 1/500. |
| Direct-aware answer-only recipe | 1e-4 | 36 | Küçük ölçekte başarılı; 500-fact sonucu model kapasitesine duyarlı. |

### 3.2. Söylenmemesi gereken ifade

```text
We systematically swept 2e-5, 5e-5 and 1e-4.
```

Bu doğru değildir. LR değerleri farklı model, dataset ve objective aşamalarında kullanıldı.
Dolayısıyla LR etkisini diğer değişkenlerden ayıran temiz bir sweep değildir.

### 3.3. Doğru ifade

```text
We used 2e-5, 5e-5 and 1e-4 in different recipe stages, but not as a clean LR sweep on the
final setup. The final capacity-control experiment fixed the LR at 1e-4. We have not tested
2e-4 on that setup.
```

## 4. Güncel Başarılı Training Setup

### 4.1. Data

- 100 synthetic subject;
- subject başına 5 fact;
- toplam 500 fact;
- relation başına 100 fact;
- relation'lar:
  - `profession`;
  - `born_in`;
  - `lives_in`;
  - `field_of_study`;
  - `works_in_industry`;
- fact başına 7 training satırı;
- toplam 3.500 training satırı;
- satır bileşimi: 3 declarative, 2 QA ve 2 scaffold-free direct;
- held-out direct ve held-out QA probe'ları training satırlarıyla aynı değildir.

### 4.2. Model ve optimization

| Alan | Değer |
|---|---|
| Base model | `HuggingFaceTB/SmolLM2-1.7B` |
| Objective | Answer-only causal LM loss |
| Block size | 128 |
| Learning rate | `1e-4` |
| Epoch | 36 |
| Micro-batch | 10 |
| Gradient accumulation | 50 |
| Effective batch | 500 |
| Optimizer update | 252 |
| Scheduler | `constant_with_warmup` |
| Warmup | %2 |
| Weight decay | `0.0` |
| Max gradient norm | 1.0 |
| Precision | BF16 |
| Gradient checkpointing | Açık |
| Seed-42 split/training | 42 / 42 |
| Geçerli replication | split 42, training 43, data order 43 |

### 4.3. Neden effective batch 500?

3.500 satır / 500 effective batch = epoch başına 7 optimizer update eder. 36 epoch sonunda:

```text
7 update/epoch x 36 epoch = 252 optimizer update
```

Bu aynı zamanda her training satırının 36 kez görülmesi anlamına gelir. 360M ve 1.7B
capacity-control karşılaştırmasında effective batch ve toplam update sayısı sabit tutuldu.
1.7B'nin A100'e sığması için yalnız micro-batch decomposition `50 x 10` yerine `10 x 50`
olarak değiştirildi.

## 5. Loss Curve'ü Nasıl Açıklamalıyım?

### 5.1. Güncel 1.7B seed-42 run

- aggregate training loss: `0.2784`;
- ilk checkpoint sınırındaki validation loss: yaklaşık `0.8397`;
- sonlara doğru validation loss: `0.006978`;
- final epoch validation loss: `0.007413`;
- 36 epoch ve 252 update tamamlandı;
- factual gate ilk kez checkpoint 50'de geçti;
- checkpoint 75'ten sonra factual retrieval neredeyse doygun ve stabildi.

### 5.2. Geçerli seed-43/data-seed-43 replication

- final validation loss: `0.005654`;
- loss trajectory seed 42'den farklıydı;
- factual gate yine checkpoint 50'de geçti;
- checkpoint 75'ten 252'ye kadar seçili factual metrikler değişmedi.

### 5.3. Loss hakkında doğru yorum

> Loss curve sağlıklı optimization gösteriyor. Fakat tezde acquisition kararı loss ile değil,
> held-out factual retrieval ile veriliyor. Önceki deneylerde daha düşük loss'un daha iyi
> retrieval anlamına gelmediğini doğrudan gördük.

`aggregate training loss` tüm run boyunca raporlanan ortalamadır; son minibatch loss'u gibi
yorumlanmamalıdır. Ayrıca farklı dataset/objective run'ları arasında tek başına loss kıyaslamak
anlamlı değildir.

## 6. "Different Phrases" Ayrışması Ne Anlama Geliyordu?

Evaluator üç görünüm kullanır:

1. **Exact-prefix:** Training scaffold'una en yakın completion; storage sinyali.
2. **Held-out direct:** Training'de aynen bulunmayan scaffold-free soru.
3. **Held-out QA:** Held-out soru, `Question: ... Answer:` formatında.

Ana robust metric:

```text
direct rank 1 AND QA rank 1
```

Triple metric buna exact-prefix rank 1 koşulunu da ekler.

### 6.1. 360M'deki ayrışma

| Model | Exact | Direct | QA | Direct/QA overlap |
|---|---:|---:|---:|---:|
| SmolLM2-360M Relation V2 | 500/500 | 378/500 | 377/500 | 329/500 |

Exact 500/500 olduğu için model fact'leri training-benzeri formatta depolamıştı. Sorun, yeni
prompt ve relation üzerinden doğru object binding'ine erişmekti.

### 6.2. 1.7B capacity-control sonucu

| Run | Exact | Direct | QA | Direct/QA overlap | Triple |
|---|---:|---:|---:|---:|---:|
| Seed 42, checkpoint 200 | 500 | 499 | 498 | 497 | 497 |
| Seed 43/data 43, checkpoint 75 | 500 | 500 | 499 | 499 | 499 |

Aynı dataset, objective, LR, epoch, effective batch, optimizer-step budget ve evaluator
kullanıldı. Bilimsel ana değişken model kapasitesiydi: 360M -> 1.7B.

Bu, eski prompt ayrışmasının 500-fact koşulunda model kapasitesiyle neredeyse tamamen
kapanabildiğini gösterir. Ancak tek başına modelin genel dil kabiliyetinin korunduğunu göstermez.

## 7. Degeneration Sorusu

### 7.1. Kontrolün sonucu

Frozen WikiText-2 raw test kontrolünde aynı 596 blok ve 304.243 scored token kullanıldı:

| Model | PPL | Base'e oran | Değişim | Factual overlap |
|---|---:|---:|---:|---:|
| Base | 15.924 | 1.000 | - | - |
| Seed 42, checkpoint 50 | 18.757 | 1.178 | +%17,79 | 490/500 |
| Seed 42, checkpoint 75 | 18.899 | 1.187 | +%18,68 | 496/500 |
| Seed 42, checkpoint 200 | 19.018 | 1.194 | +%19,43 | 497/500 |
| Seed 43/data 43, checkpoint 75 | 18.681 | 1.173 | +%17,31 | 499/500 |

Precommitted sınıflandırmaya göre bu **measurable drift**tir; `%25` material-degradation
eşiğinin altındadır. Erken seed-42 checkpoint'leri drift'i ortadan kaldırmıyor.

### 7.2. Open generation ne gösterdi?

- Common-knowledge candidate ranking bütün modellerde 30/30 kaldı.
- M1 modelleri genel narrative, explanation, procedure ve QA promptlarına anlamlı cevaplar verdi.
- Unrelated promptlarda synthetic subject-name intrusion 0/30 oldu.
- Base 30 promptun hiçbirinde EOS üretmezken iki seçili M1 modelinde 30/30 çıktı EOS ile bitti.
- M1 çıktıları ortalama yaklaşık 7--8 content token'a düştü; 2--3 prompt near-empty kaldı.
- Training tokenizer her kısa cevabın sonuna EOS ekliyor ve EOS'u supervised label olarak
  kullanıyor. Dolayısıyla short-answer/EOS bias için doğrudan recipe-level mekanizma var.

Sonuç broad semantic collapse veya fact-only responder değildir. Fakat "model hiç dejenere
olmadı" demek de doğru değildir: generic distribution ve stopping behavior ölçülebilir biçimde
değişmiştir.

### 7.3. Görüşmede verilecek doğru cevap

> "I ran a base-versus-M1 control. I would not call it a broad collapse: the models still give
> meaningful general continuations, retain 30 out of 30 common-knowledge rankings, and do not
> inject synthetic facts into unrelated prompts. But there is measurable drift. Generic
> perplexity increases by about 17 to 19 percent in both independent runs, and all 30 open
> continuations end in EOS. That short-answer bias is consistent with our objective, because we
> supervise EOS after every answer. Earlier checkpoints only reduce the loss shift slightly."

## 8. V1 Biography ve Relation V2 Farkı

### 8.1. Max'in haklı olduğu nokta

V1 biography satırları bir subject'in beş fact'ini birlikte içeriyordu. Örneğin yapı olarak:

```text
SUBJECT works as PROFESSION. SUBJECT was born in BIRTHPLACE, now lives in RESIDENCE,
studied at UNIVERSITY, and works at EMPLOYER.
```

Dolayısıyla V1 biography eğitimi yalnız bir relation'ı izole şekilde göstermiyordu.

### 8.2. Düzeltilmesi gereken nokta

V1'in beş relation'ı şunlardı:

```text
profession
born_in
lives_in
studied_at
works_at
```

V1'de ayrıca `field_of_study` yoktu.

Relation V2 değişikliği:

```text
studied_at -> field_of_study
works_at   -> works_in_industry
```

Güncel Relation V2 seti yine beş relation içerir; relation sayısı artırılmadı.

### 8.3. Neden replacement yapıldı?

V1 500-fact audit'inde hata tahminleri özellikle iki proper-name-heavy relation'da birkaç
candidate'a yığılıyordu:

- `studied_at`: özellikle `19 Mayis Universitesi`;
- `works_at`: özellikle `3M`.

Bu, subject-specific binding yerine relation-level candidate prior/collapse davranışına işaret
ediyordu. `field_of_study` ve `works_in_industry`, aynı education/work semantiğini daha dengeli
candidate inventory ile test etmek için seçildi.

### 8.4. Değişiklik fayda sağladı mı?

SmolLM2-360M, 500-fact karşılaştırması:

| Dataset | Exact | Direct | QA | Overlap |
|---|---:|---:|---:|---:|
| Historical V1 | 451 | 317 | 349 | 277 |
| Relation V2 | 500 | 378 | 377 | 329 |
| Fark | +49 | +61 | +28 | +52 |

V2 strict gate'i 360M ile yine geçmedi; dolayısıyla replacement tek başına bütün problemi
çözmedi. Ancak V1'e göre kontrollü ve ölçülebilir iyileşme sağladı.

### 8.5. Güncel run biography mi kullanıyor?

Hayır. Güncel başarılı run full-subject biography satırları yerine fact başına yedi
relation-specific direct-aware satır kullanıyor. Buna rağmen beş relation aynı training run'ında
birlikte bulunuyor ve sonuçlar relation başına raporlanıyor.

## 9. Relation Başına Güncel Sonuç

### 9.1. Seed 42, checkpoint 200

Üç non-triple fact'in tamamı `lives_in` relation'ındadır. Bundan relation tablosu doğrudan
şöyle türetilir:

| Relation | Exact | Direct | QA | Overlap/Triple |
|---|---:|---:|---:|---:|
| `profession` | 100/100 | 100/100 | 100/100 | 100/100 |
| `born_in` | 100/100 | 100/100 | 100/100 | 100/100 |
| `lives_in` | 100/100 | 99/100 | 98/100 | 97/100 |
| `field_of_study` | 100/100 | 100/100 | 100/100 | 100/100 |
| `works_in_industry` | 100/100 | 100/100 | 100/100 | 100/100 |

### 9.2. Seed 43/data seed 43, checkpoint 75

Tek non-triple fact `lives_in` relation'ındadır:

| Relation | Exact | Direct | QA | Overlap/Triple |
|---|---:|---:|---:|---:|
| `profession` | 100/100 | 100/100 | 100/100 | 100/100 |
| `born_in` | 100/100 | 100/100 | 100/100 | 100/100 |
| `lives_in` | 100/100 | 100/100 | 99/100 | 99/100 |
| `field_of_study` | 100/100 | 100/100 | 100/100 | 100/100 |
| `works_in_industry` | 100/100 | 100/100 | 100/100 | 100/100 |

`lives_in` hatasının tekrarlanması relation'ı kaldırma gerekçesi değildir. `born_in` ve
`lives_in` aynı city candidate inventory'sini bilinçli olarak paylaşır; bu, subject'in iki
şehrini doğru relation'a bağlayıp bağlayamadığını test eden zor bir kontroldür.

## 10. Ölçek Sonucu Neden Önemli?

360M Relation V2 ile:

| Ölçek | Exact | Direct | QA | Overlap |
|---|---:|---:|---:|---:|
| 500 fact | 500/500 | 378/500 | 377/500 | 329/500 |
| 2.500 fact | 2.498/2.500 | 1.249/2.500 | 1.293/2.500 | 958/2.500 |

Normalized overlap `%65,8`den `%38,3`e düşerken exact storage yaklaşık `%100` kaldı. Ayrıca
2.500-fact modelin içindeki aynı nested ilk 500 fact'in overlap'i 329'dan 188'e düştü.

Bu, "model fact'leri hiç öğrenmedi" açıklamasından farklıdır. Fact'ler exact formatta hâlâ
erişilebilir; fakat daha fazla binding eklendikçe prompt/relation üzerinden retrieval
interference artmaktadır.

## 11. Görüşmede Kullanılabilecek Kısa Cevaplar

### "What did you mean by increasing training intensity?"

> I used that phrase too loosely. I meant more epochs, more exposure and stronger acquisition
> formats across several experiments. It was not one clean variable. The key result was that
> lower loss and longer exposure alone did not improve held-out retrieval.

### "What is the current setup?"

> The current validated setup is SmolLM2-1.7B on 500 facts from 100 subjects. I use seven English
> rows per fact, answer-only loss, LR 1e-4, 36 epochs, effective batch 500, 252 updates, 2% warmup,
> a constant schedule and zero weight decay.

### "Did you test the learning rates I suggested?"

> I used 2e-5, 5e-5 and 1e-4 in different earlier recipe stages, but that was not a controlled
> LR sweep on the final setup. I have not tested 2e-4. The final 1.7B capacity comparison kept
> 1e-4 fixed and passed in two independent data orders.

### "What does the loss curve look like?"

> In the first successful 1.7B run, validation loss fell from about 0.84 at the first checkpoint
> boundary to about 0.007 at the end. The factual gate passed at checkpoint 50 and retrieval was
> almost saturated from checkpoint 75 onwards. The replication ended at 0.0057 and showed the
> same factual plateau.

### "Why was there such a disconnect between phrases?"

> With 360M, exact retrieval was 500 out of 500 but the overlap across two held-out prompts was
> only 329. So storage and prompt-robust access were different. With the same data and update
> budget, the 1.7B runs reached 497 and 499 overlap. That makes a capacity-limited binding/access
> explanation much more likely for the 500-fact setting.

### "Has the model degenerated?"

> Not into a fact-only responder, but it has measurably drifted. Generic perplexity is 17 to 19
> percent worse in both M1 runs, and every open continuation ends in EOS. At the same time,
> common-knowledge ranking stays 30 out of 30 and the model still produces meaningful general
> continuations. I therefore call this general-language and stopping-behavior drift, not broad
> semantic collapse.

### "Didn't V1 already include the relations together?"

> Yes, each V1 biography included all five V1 facts. But V1 contained studied_at and works_at;
> it did not additionally contain field_of_study. V2 replaced studied_at with field_of_study and
> works_at with works_in_industry. The current run trains all five V2 relations jointly and reports
> accuracy per relation.

## 12. Kaçınılması Gereken İddialar

- "Lower loss proves the facts were learned." Yanlış; geçmiş deneyler tersini gösterdi.
- "We completed a clean LR sweep." Yanlış; LR'lar farklı recipe'lerde kullanıldı.
- "The model did not degenerate." Fazla güçlü; genel PPL ve stopping behavior ölçülebilir değişti.
- "The model broadly collapsed." Yanlış; genel continuation ve common-knowledge ranking korunuyor.
- "V1 already had field_of_study." Yanlış.
- "V2 solved the entire problem." Yanlış; V2 360M sonucu hâlâ gate altında kaldı.
- "1.7B proves the method scales to 25,000 facts." Yanlış; güçlü sonuç kontrollü 500-fact koşuluna ait.
- "Candidate ranking is the same as open-generation quality." Yanlış.
- "360M could not store the facts." Yanlış; exact storage 500/500 idi.
- "Changing only the seed produced an independent replication." İlk seed-43 girişiminde data order değişmediği için deterministik reproduction oluştu. Geçerli replication training ve data seed 43 kullanır.

## 13. Görüşmede Gelebilecek Takip Soruları

### Neden checkpoint 200 seçildi, final checkpoint 252 değil?

Checkpoint seçim sırası önceden overlap, triple, direct, QA ve daha erken checkpoint olarak
tanımlandı. Checkpoint 200 en iyi plateau'ya ulaştı ve tie-break ile seçildi; final checkpoint
olduğu için otomatik seçilmedi.

### Neden seed-43 checkpoint 75 seçildi?

Checkpoint 75, 499 overlap/triple plateau'suna ilk ulaşan checkpointti. 100-252 aynı sonucu
verdiği için predeclared earlier-checkpoint tie-break uygulandı.

### Neden 36 epoch çok yüksek değil mi?

Dataset küçük ve controlled acquisition amacı taşıyor. Effective batch 500 nedeniyle epoch
başına yalnız 7 optimizer update var; 36 epoch toplam 252 update ediyor. Yine de bunun genel
dil yeteneğine etkisi ayrıca ölçülmelidir.

### Neden open generation yerine candidate ranking?

Candidate ranking spelling, punctuation ve answer length gibi generation confound'larını
azaltarak doğru canonical object'in rakipler arasındaki rank'ini ölçer. Ancak bunun karşılığında
genel generation kalitesini ölçmez; bu nedenle degeneration kontrolü ayrı yapılmalıdır.

### Neden `born_in` ve `lives_in` aynı city inventory'yi paylaşıyor?

Bu bilinçli relation-binding kontrolüdür. Modelin subject'e ait herhangi bir şehri değil, doğru
relation'ın şehrini seçmesi gerekir. Birthplace-residence swap'ları bu nedenle ayrıca raporlanır.

## 14. Ana Kanıt Kaynakları

- Final 1.7B config:
  `transfer-vs-relearning/configs/training/m1_smollm2_1_7b_relation_v2_100_subjects_500_facts_direct_lr1e-4_ep36.yaml`
- 1.7B capacity-control:
  `documentation/85_M1_RELATION_V2_1_7B_CAPACITY_CONTROL_EVALUATION_REPORT.md`
- Seed-43/data-43 replication:
  `documentation/87_M1_RELATION_V2_1_7B_SEED43_REPLICATION_EVALUATION_REPORT.md`
- Relation V2 500-fact 360M sonucu:
  `documentation/75_M1_RELATION_V2_500_FACT_EVALUATION_REPORT.md`
- Relation V2 2.500-fact exploratory sonuç:
  `documentation/77_M1_RELATION_V2_2500_FACT_EXPLORATORY_EVALUATION_REPORT.md`
- Historical V1 500-fact direct-aware sonuç:
  `documentation/59_M1_500_FACT_DIRECT_SUPERVISION_INTERIM_REPORT.md`
- İlk LR/epoch pilotları:
  `documentation/08_M1_PILOT_LR5E-5_EP1_RUN_REPORT.md`,
  `documentation/10_M1_PILOT_LR1E-4_EP1_RUN_REPORT.md`,
  `documentation/11_M1_PILOT_LR5E-5_EP3_RUN_REPORT.md`
- High-exposure 2e-5/5-epoch kontrolü:
  `documentation/34_M1_RETURN_TO_BASELINE_HIGH_EXPOSURE_EVALUATION_REPORT.md`
- V2 dataset contract:
  `documentation/74_M1_RELATION_V2_500_FACT_SCALE_PLAN.md`
- General-capability pre-run plan ve sonuç raporu:
  `documentation/90_M1_GENERAL_CAPABILITY_DEGENERATION_PLAN.md`,
  `documentation/91_M1_GENERAL_CAPABILITY_DEGENERATION_EVALUATION_REPORT.md`
