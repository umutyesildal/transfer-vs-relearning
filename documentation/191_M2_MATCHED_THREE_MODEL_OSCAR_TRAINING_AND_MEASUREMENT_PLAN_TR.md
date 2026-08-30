# 191 — M2 matched three-model OSCAR training and measurement plan

**Tarih:** 2026-08-30  
**Durum:** `DESIGN FROZEN / NON-EXECUTABLE / TRAINING NOT AUTHORIZED`

## 1. Kısa karar

Phase-2 V1A kanıtı tamamlandığı için sonraki deney tasarımı OLMo, Qwen ve SmolLM'nin üçünde de
aynı nedensel yapıyı kullanacaktır:

```text
aynı modelin exact M1 epoch-036 parent'ı
├── M2-A: factsiz Türkçe OSCAR continual pretraining
└── M2-B: aynı bütçe + Branch-B Türkçe factual re-exposure
```

Üç model de zorunludur; tek primary model seçilmez. M2-B, M2-A'nın devamı değildir. Her modelde
iki kol bağımsız olarak aynı M1 ağırlığından başlar.

## 2. Neden tokenizer toplamlarını modelden modele eşitlemiyoruz?

Aynı OSCAR train split'i üç tokenizer altında farklı uzunluktadır:

| Model | Full train token |
|---|---:|
| Qwen | 450,578,318 |
| OLMo | 527,542,206 |
| SmolLM | 688,976,056 |

Bu fark veri kalitesi veya model kalitesi değildir; tokenizer segmentasyonu farkıdır. Ana causal
karşılaştırma model içinde M2-B−M2-A olduğu için zorunlu eşleme her modelin iki kolu arasındadır.
Modeller arası sonuç yalnız secondary heterogeneity analysis olacaktır.

Bu plan yine de compute dozunu karşılaştırılabilir tutar: her model ve arm için exact
`97,536 × 512 = 49,938,432` model-native token. Aynı seed-42 stable-document sırası kullanılır;
tokenizer fertility nedeniyle bu hedefe ulaşmak için tüketilen OSCAR doküman sayısı model bazında
farklı olabilir ve ayrıca raporlanır.

Bu yaklaşık 50M-token doz, eski 1M-token Qwen Wikipedia pilotundan yaklaşık 50 kat büyüktür ve
Document 145'te sonuç görülmeden önce önerilen ilk anlamlı doz basamağıyla uyumludur. 250M/1B dose
ladder veya full-corpus epoch bu aile tarafından otomatik açılmaz.

## 3. M1 parent bağları

Her model seed 42 M1 `epoch-036` model-only snapshot'ından başlar. Mevcut eval-v2 kanıtı bu exact
snapshot'ları 111/111 tamamlanmış aile içinde değerlendirmiştir. Proposed yollar config'e
işlenmiştir; training contract açılmadan önce direct read-only manifest, config, tokenizer ve
weight SHA-256 değerleri ayrıca yakalanıp birebir bağlanmalıdır.

Bu endpoint seçimi treatment sonucuna göre yapılmamıştır. M2-A ve M2-B için ara checkpoint seçimi
yoktur; birincil endpoint update `762`'dir. Ara noktalar trajectory evidence'tır.

## 4. Training reçetesi

Ana mantıksal reçete bütün modellerde ve kollarda aynıdır:

- full-sequence causal language modeling;
- tokenizer değişikliği/extension yok;
- English replay yok;
- sequence length `512`;
- `97,536` tam block / `49,938,432` token;
- effective batch `128` block = `65,536` token/update;
- `762` optimizer update;
- LR `1e-5`, constant-with-warmup, warmup `%2`;
- AdamW, weight decay `0`, betas `0.9/0.999`, epsilon `1e-8`;
- BF16, gradient checkpointing, gradient clipping `1.0`;
- training/data seed `42`.

Microbatch ve gradient accumulation model/GPU belleğine göre farklı parçalanabilir; ancak çarpımları
exact `128` block/update kalmalıdır. Bu yalnız memory decomposition'dır, bilimsel bütçe değişikliği
değildir. Her model için optimizer smoke geçmeden training açılamaz.

## 5. M2-B factual replacement

Relation V2 100-subject/500-fact populationındaki Branch B, yaklaşık 50 subject / 250 fact içerir.
Branch A facts hiç Türkçe training exposure almaz ve transfer-only control olarak kalır.

M2-B için:

1. her Branch-B fact için tek canonical Türkçe declarative statement dondurulur;
2. alias ve relation template'leri evaluator ile aynı registry'ye bağlanır;
3. exact duplicate fact ID, yanlış branch, boş/çok uzun encoding ve alias drift fail-closed olur;
4. fact stream complete-cycle biçiminde dengeli tekrar edilir;
5. `976` evenly spaced generic block içindeki prefix, complete fact boundaries korunarak fact
   tokenlarıyla değiştirilir; kalan block tail'i M2-A'daki generic tokenlarla aynı kalır;
6. toplam block/token/update sayısı M2-A ile birebir aynı kalır.

Hedef replacement alanı yaklaşık `%1`'dir. Tokenizer farkı nedeniyle exact factual token ve her
fact'in exposure adedi materialization raporunda hesaplanıp training öncesi dondurulacaktır;
relation/fact exposure farkı en fazla bir complete cycle olmalıdır. M2-A'da target synthetic
subject/binding hit sayısı `0` olmak zorundadır.

## 6. Ölçüm sıklığı — “her epoch” meselesi

M1'in veri seti küçüktü ve 36 gerçek epoch vardı. M2 corpusu çok büyük olduğundan 50M token dozu
tam OSCAR train split'inin yalnız bir bölümüdür; burada “36 epoch”u mekanik olarak kopyalamak doğru
değildir. Bunun yerine daha güçlü bir dose trajectory kullanılır:

```text
update: 0, 76, 152, 229, 305, 381, 457, 533, 610, 686, 762
```

Yani başlangıç ve yaklaşık her `%10` token dozunda model-only snapshot + dense ölçüm vardır. Bu,
bu koşudaki tek endpoint'i ölçmekten çok daha sıkıdır. Full pahalı paket başlangıç, midpoint
(`381`) ve endpoint'te (`762`) çalışır.

Dense paket:

- training trace, loss, LR, gerçek token ve truncation/padding sayıları;
- cheap factual access;
- 500 exact-prefix paneli;
- WikiText word/byte PPL ve BPB;
- held-out OSCAR Turkish word/byte PPL ve BPB;
- trwiki cross-domain control;
- cheap generation-integrity.

Full paket:

- 12,000-probe factual hard suite ve relation/form/scaffold minima;
- eval-v2 BLiMP, HellaSwag, WinoGender;
- TurBLiMP;
- full generation-integrity.

Pile-10k emekli edilmiştir ve M2'ye geri eklenmez. TurkishMMLU/XNLI, mevcut frozen eval-v2'nin
aktif task setinde olmadığı için sessizce primary pakete eklenmez; yeni bir amendment olmadan
çalıştırılmaz.

## 7. Önceden donmuş başarı ve koruma kuralları

- M2-A held-out Turkish BPB: M1'e göre en az `0.07400058` düşüş, byte-PPL ratio en fazla `0.95`.
- M2 English retention: WikiText `ΔBPB ≤ 0.32192809`; BLiMP/HellaSwag düşüşü en fazla `0.05`.
- M2 EN→EN factual/robust düşüşü: M1'e göre en fazla `0.05`.
- Transfer: `TR→EN(M2-A) − TR→EN(M1)`.
- Relearning: `TR→EN(M2-B) − TR→EN(M2-A)`.
- Birincil relearning kapısı: point gain en az `0.05` ve 10,000-draw seed-42 paired-subject
  bootstrap `%95` alt sınırı strict `>0`.

Sonuç negatif olsa bile deney geçerlidir. Endpoint veya threshold treatment sonucu görüldükten
sonra değiştirilemez.

## 8. Bilimsel sıralama ve DAG

```text
CPU evidence/materialization
  ├── exact three M1 parent manifests
  ├── Turkish Branch-B fact registry + review
  ├── 3 × (M2-A/M2-B) packed block manifests
  └── exact storage/runtime estimate
          ↓
per-model optimizer smoke
          ↓
3 models × 2 sibling training arms
          ↓
dense checkpoint evaluation + full 0/50/100% evaluation
          ↓
paired M2-A−M1 and M2-B−M2-A analysis
```

Training joblarının aynı anda koşması bilimsel zorunluluk değildir; cluster kapasitesine göre
sıralanabilirler. Ancak bir modelin iki arm'ı aynı frozen input/recipe'yi kullanmalı ve bir arm'ın
sonucu diğer arm'ın recipe'sini değiştirememelidir.

## 9. Training açılmadan önce kalan işler

1. M1 epoch-036 parent ağırlık/config/tokenizer manifest hash'lerini read-only yakala.
2. Branch-B 250-fact Turkish declarative registry'yi üret, hash-kapat ve bounded insan incelemesi
   yap.
3. Her tokenizer için deterministic 97,536-block M2-A/M2-B pair materialize et; text veya raw token
   listelerini Git'e koymadan compact manifest/hashes üret.
4. Exact per-model fact exposure, consumed-document, discarded-tail ve packing audit'ini doğrula.
5. Model-specific microbatch×accumulation route ve optimizer smoke'u dondur.
6. Checkpoint başına model-only storage, active optimizer state, toplam scratch ve runtime
   tahminini dondur.
7. Training/evaluation DAG'ını implement edip offline fixture ve fail-closed testlerini geçir.
8. Exact implementation/config hash'li ayrı execution contract hazırla ve kullanıcıdan açık yetki
   al.

## 10. Yetki sınırı

Machine-readable plan:

```text
configs/training/m2_matched_three_model_oscar_plan_v1.yaml
```

Bu belge ve config yalnız local design freeze'dir. Push, HU/SSH, model-weight erişimi, corpus/block
materialization, Slurm, GPU, training, evaluation, cleanup, deletion veya automatic retry yetkisi
vermez. `ready_to_train=false` kalır.
