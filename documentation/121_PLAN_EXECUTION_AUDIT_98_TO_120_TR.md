# 121 - Plan Uygulama Denetimi: Doküman 98'den 120'ye (TR)

**Tarih:** 25 Temmuz 2026  
**Durum:** Başka bir AI ajanı için güncel durum, plan-uygulama farkı ve sonraki karar noktaları  
**Operasyonel otorite:** Güncel çalışma durumu için `100_MASTER_PROJECT_STATUS_AND_EXECUTION_PLAN.md`; bu doküman onun yerine geçmez.  
**Kapsam:** `00_DOCUMENTATION_INDEX.md`, `98_PRE_M2_FINAL_DECISION.md` ve `100`--`120` numaralı tüm Markdown kayıtları.

## 1. Kısa hüküm

Projenin ana mantığı korunmuştur: Türkçe M2/M3 etkisini yorumlamadan önce İngilizce M1 bilgisinin hem prompt-robust hem de genel dil yeteneğini koruyan şekilde edinildiği gösterilmelidir. Ancak bu ön koşul henüz **bağımsız iki seed ile geçilememiştir**.

En güncel ve bağlayıcı sonuç şudur:

> Qwen temiz-İngilizce replay müdahalesi seed 42'de yalnızca keşif niteliğinde bir geçiş noktası üretmiştir (adjudicated step 50). Aynı sabit kontrat seed 43'te tekrar üretilememiştir. Bu nedenle 500-subject / 2,500-fact ölçek kapısı, final M1, M2-clean ve M3 kolları **HOLD** durumundadır.

Bu, altyapı veya depolama kaynaklı açık bir başarısızlık değildir. Seed-43 eğitim ve 11-checkpoint değerlendirme tamamlanmış; sorun, retention ile özellikle `profession` Form-C prompt genellemesinin aynı checkpoint'te birleşmemesidir.

## 2. Sayısal, ama ağırlıksız ilerleme özeti

Bu yüzdeler deney ağırlığı veya tez tamamlanma oranı değildir; yalnızca 98 ve 100'deki sıralı karar kapılarının durumu için hızlı yön bulma aracıdır.

| Plan zinciri | Tamamlanan / yürütülen | Geçen | Bloklanan veya hiç açılmayan |
|---|---:|---:|---:|
| Doküman 98, Stage 1--6 | 1/6 doğrudan aşama denendi; Stage 1 altında birden fazla remediation yapıldı | 0/6 | Stage 2--6 açılmadı; M2/M3 dahil |
| Doküman 100, Phases 1, 2, 2B, 2C | 4/4 yürütüldü | 0/4 | Her biri frozen gate'te başarısız |
| Doküman 109 bridge hazırlığı ve pilotu | corpus, Contract V2, iki model eğitimi ve iki model değerlendirmesi tamamlandı | hazırlık/operasyon kapıları geçti | iki model de bridge promotion gate'ini geçemedi |
| Doküman 117 retention dalı | seed-42 control+replay ve bütün checkpoint değerlendirmesi; adjudication; seed-43 replikasyonu tamamlandı | yalnızca seed-42 keşif/adjudication adımı | seed-43 geçemedi; 500-subject kapısı kapalı |
| Final nedensel zincir (seçilmiş ölçek M1 → M2 → M3 → DID analiz) | 0 ana deney | 0 | tamamı HOLD |

## 3. Doküman 98 planı: madde madde denetim

| 98 plan maddesi | Gerçekte yapılan iş | Durum | Sonuç / neden ilerlemedi |
|---|---|---|---|
| Stage 1: 100 subject/500 fact form-balanced remediation | Dok. 101--104 ile iki SmolLM2 müfredat denendi; Dok. 105--108 ile cross-family/Qwen checkpoint tanısı yapıldı; Dok. 117--120 ile Qwen replay müdahalesi ve seed-43 replikasyonu yapıldı | **Tamamlandı, ancak geçmedi** | Hiçbir doğrulanmış iki-seed çözüm tüm exact + held-out form + robust + PPL kapılarını birlikte geçmedi |
| Stage 2: Başarılı müfredatla joint relation control | Yeni passing curriculum oluşmadığı için çalıştırılmadı | **Doğru biçimde açılmadı** | Ön koşul başarısız; tarihsel WP3 sonucu geçerli ama yeni recipe için yeterli değil |
| Stage 3: 1.7B, 500 subject/2,500 fact scale validation | Çalıştırılmadı | **HOLD** | 100-subject recipe iki seed ile geçmedi |
| Stage 4: 5,000 subject/25,000 fact canonical M1 | Çalıştırılmadı | **HOLD** | 500-subject ara kapı geçmeden büyük ölçek bilimsel olarak açılmıyor |
| Stage 5: final M1 artifact / learned-fact freeze / pre-M2 audit | Çalıştırılmadı | **HOLD** | Seçilmiş passing M1 checkpoint yok |
| Stage 6: M2-clean ve M3 Branch A/B deneyleri | Çalıştırılmadı | **HOLD** | M1 ön koşulu sağlanmadı |

## 4. Doküman 100 yürütme planı: ne kadar yapıldı?

### Tamamlanan ancak gate'i geçmeyen M1 çözüm aramaları

1. **Phase 1 / Dok. 101--102 — Form A+B question-only remediation:** tamamlandı ve başarısız oldu. Trained A/B erişimi %100 iken held-out C/D %46.6--62.4, exact-prefix %9.4 ve eight-cell robust intersection %11.8 kaldı. PPL ratio 1.041 idi; sorun retention değil prompt-generalization idi.
2. **Phase 2 / Dok. 103--104 — Canonical + A/B hybrid:** tamamlandı ve başarısız oldu. Exact-prefix 500/500, A/B 2,000/2,000 ve PPL ratio 1.080 geçti; fakat held-out C/D 1,501/2,000 (%75.05) ve robust 198/500 (%39.6) kaldı. Sorun yeniden exact storage değil, prompt-invariant access idi.
3. **Phase 2B / Dok. 105--106 — Cross-family screen:** tamamlandı ve başarısız oldu. Qwen factual/robustness açısından neredeyse tam geçti (exact %100, robust global/min %99.6/%99) fakat PPL ratio yaklaşık 1.461 ile retention kapısını ihlal etti. StableLM, Gemma ve Llama da tüm kapıları birlikte geçmedi.
4. **Phase 2C / Dok. 107--108 — Qwen early-checkpoint Pareto tanısı:** tamamlandı ve başarısız oldu. Update 50 factual kapıları geçerken PPL ratio 1.455 idi; update 25 bile PPL 1.409'daydı ve factual kapıları geçmiyordu. Erken durdurma çözüm değildir.

### 109 planının hazırlanıp sonuçlanan kısmı

5. **Phase 109A corpus ve kontrat:** başarıyla tamamlandı. Temiz, hash'lenmiş Türkçe Wikipedia corpus (504,287 clean belge), contamination audit, Contract V2, localized candidates, eligible setler ve low/full dozlar donduruldu (Dok. 110--112). Bu operasyonel bir başarıdır; M2 yetkisi değildir.
6. **Bridge training:** Qwen ve SmolLM2 scratch üzerinde başarıyla eğitildi; node/GPU kontaminasyonları GPU-guard ile güvenli biçimde atlatıldı (Dok. 113--114).
7. **Frozen bridge evaluation:** tamamlandı. SmolLM2'de Türkçe PPL iyileşti fakat TR→EN access açılmadı/iyileşmedi. Qwen M1'de yüksek TR→EN access ile başladı, fakat genel Türkçe adaptasyon bu erişimi anlamlı biçimde düşürdü. İki aile de `not_viable_under_frozen_pilot` oldu (Dok. 115--116).

### Sonraki explicit pivot: retention remediation

8. **Dok. 117 seed-42 Qwen replay:** control ve `w=0.5` clean-English replay eğitimleri ile 22 checkpoint taraması tamamlandı. Replay step 50 exact, held-out robustness ve PPL ratio 1.24684 kapılarını geçti. İlk literal karar, doğru `navigation` + EOS yanıtını yalnızca iki token diye empty sayan integrity heuristic nedeniyle başarısızlıktı.
9. **Dok. 118 adjudication:** orijinal strict sonucu değiştirmeden, lexical-content tabanlı ayrı bir adjudicated özet üretildi. Bu post-outcome keşif düzeltmesinde replay step 50 tek geçiş noktası oldu; bu nedenle bağımsız seed-43 zorunlu replikasyonu açıldı.
10. **Dok. 119--120 seed-43 replikasyonu:** eksiksiz tamamlandı ve gerçek bilimsel gate'te başarısız oldu. Step 50 PPL ratio 1.1869 ile retention'ı geçti; ancak held-out minimum C/D yalnızca %72 idi. Step 75'te factual/robustness geçti fakat PPL ratio 2.755'e yükseldi. Dolayısıyla ortak passing checkpoint yoktur.

## 5. Yapılmış, korunması gereken varlıklar ve negatif kanıt

- Relation V2 canonical popülasyon, Branch A/B ataması ve 10/100/500-subject dataset paketleri mevcuttur.
- Türkçe clean corpus, contamination envanteri, deterministic split ve hash'ler dondurulmuştur (Dok. 110).
- Qwen/SmolLM bridge kontratları, eğitim endpointleri ve frozen bridge evaluation kanıtı vardır (Dok. 112--116).
- Seed-42 retention denemesinin hem **orijinal** hem **adjudicated** özetleri korunmalıdır; adjudication geçmiş sonucu overwrite etmemiştir (Dok. 118).
- Seed-43 Qwen replay checkpoint/evaluation kanıtı korunmalıdır. Bu, seed-42 bulgusunun replikasyon başarısızlığıdır; "denenmemiş" veya altyapı hatası değildir (Dok. 120).
- HU home storage kuralı başarıyla korunmuştur: büyük ağaçlar scratch'tedir, home yaklaşık 7.91--8.0 GiB düzeyinde kalmıştır. Bu durum yeni deneyde de değişmez bir zorunluluktur.

## 6. Önerilen kontrollü feasibility planı (25 Temmuz 2026)

### 6.1 Karar ve sınır

Bu bölüm, güncel audit sonrasında kullanıcıyla paylaşılan dış değerlendirme önerisini kaydeder.
Öneri, Doküman 100/117'deki sıradan farklı olarak Qwen için 500-subject denemesini, iki-seed
100-subject recipe doğrulaması olmadan **keşif amaçlı bir scale diagnostic** olarak açmayı önerir.
Bu nedenle iki deney de aşağıdaki gibi sınıflandırılmalıdır:

- **final M1 değildir;**
- M2, M3, 1,000-subject veya 5,000-subject çalışmasını yetkilendirmez;
- passing sonuç, recipe'in doğrulandığı veya seçildiği anlamına gelmez;
- sonuç ne olursa olsun final seçimin öncesinde bağımsız seed doğrulaması gerekir;
- kodlama, HU submission veya scale-up için ayrıca sürümlenmiş numbered plan, frozen config/gate,
  test ve zorunlu scratch preflight gerekir.

Bu değişiklik, Doküman 120'nin otomatik üçüncü seed/coefficient sweep yasağını kaldırmaz. Qwen
deneyi, seed-43'te başarısız olan 100-subject replay recipe'ini "passing final recipe" gibi
sunmamalıdır; yalnızca ölçek davranışını ölçen yeni, açıkça exploratory bir koşudur.

### 6.2 Deney A — Qwen 500-subject / 2,500-fact exploratory scale probe

**Amaç:** Qwen'in 500 fact'teki çok yüksek factual robustness'ının 2,500 fact'te korunup
korunmadığını; binding/interference ve generic-English PPL davranışının ölçekle nasıl değiştiğini
ölçmek.

| Öğe | Frozen plan taslağı |
|---|---|
| Model | `Qwen/Qwen2.5-1.5B`, mevcut frozen base snapshot |
| Popülasyon | 500 subject × 5 Relation V2 relation = 2,500 fact; Branch A/B ve metadata dengesi korunur |
| Recipe | Canonical + Form A + Form B factual curriculum; clean-English replay (`w=0.5`); tarihsel Dok. 76 ölçek eşlemesiyle 36 epoch ve effective factual batch 2,500 |
| Update bütçesi | 7 optimizer update/epoch × 36 epoch = **252 update**; 2,500 fact için 1,260 update kullanılmaz |
| Seed | Seed/data-seed 42, **tek discovery seed** |
| Selection | Düzenli retained checkpoint evaluation; endpoint seçimi sonuç görülmeden frozen edilir |
| Zorunlu metrikler | Exact-prefix, A/B, held-out C/D, eight-cell robust intersection, per-relation/per-branch sonuçlar, WikiText-2 PPL ratio, integrity/generation kontrolleri |
| Ana karşılaştırma | Dok. 117--120'daki Qwen 100-subject/500-fact sonuçlarıyla aynı evaluator ve denominator kuralları altında doğrudan karşılaştırma |
| Bilimsel sorular | Robustness ölçekle korunuyor mu? Interference hangi relation/subgroup'ta oluşuyor? PPL drift sabit mi büyüyor mu? Yeterli büyüklükte frozen eligible-fact havuzu oluşuyor mu? |

Bu deney 500-subject kapısını resmi olarak **geçmiş** saymak için kullanılamaz; çünkü kullanılan
recipe seed-43'te 100-subject düzeyinde doğrulanmamıştır. Ancak iyi sonuç, aynı ölçek kontratının
bağımsız seed'de replikasyonunu gerektirir; kötü sonuç Qwen'in ölçek/retention sınırlamasını
doğrudan kanıtlar.

### 6.3 Deney B — SmolLM2 prompt-binding remediation (önce 100 subject)

**Amaç:** SmolLM2-1.7B'nin retention avantajını korurken, başarısız olduğu prompt-invariant
subject--relation--object binding mekanizmasını doğrudan hedeflemek.

Tek müdahale, mevcut canonical-plus-A/B hybrid factual objective'e relation-matched contrastive
candidate-ranking kaybı eklemektir:

```text
L_total = L_canonical_factual_LM + λ × L_correct-versus-relation-matched-distractors
```

Her factual örnekte doğru cevap, **aynı relation** içinden güçlü yanlış adaylarla karşılaştırılır.
Örneğin `profession` relation'ında doğru `physicist` için `architect`, `biologist`, `historian`,
`chemist` relation-matched negative adaylarıdır. Bu tasarımın hedefi yalnız doğru cevabı üretmek
değil, doğru subject--relation binding'in olasılığını aynı relation'daki rakiplerinden açıkça üstün
kılmaktır.

| Öğe | Frozen plan taslağı |
|---|---|
| Model | SmolLM2-1.7B |
| İlk ölçek | 100 subject / 500 fact |
| Control | Dok. 104 canonical + Form A/B hybrid recipe; mevcut frozen sonuç yeniden eğitilmez, integrity reference olarak kullanılır |
| Intervention | Aynı hybrid curriculum, factual row/answer-token exposure/update bütçesi ve tek ek değişken olarak contrastive ranking loss |
| Negatifler | Relation-matched; candidate inventory, sayı, sampling ve `λ` sonuç görülmeden dondurulur |
| Holdout koruması | Forms C/D **kesinlikle training'e girmez**; aynı frozen held-out evaluator korunur |
| Seed akışı | Seed 42 discovery → tüm kapılar geçerse değişmemiş kontratla seed/data-seed 43 replication → iki seed geçerse 2,500-fact scale |
| Zorunlu kapılar | Exact, A/B, C/D, eight-cell robust global + per relation, PPL ratio, generic behavior/integrity; mevcut frozen eşikler zayıflatılmaz |

Bu deney doğrudan 2,500 fact'te başlatılmamalıdır. SmolLM için ilk soru ölçek değil, 500 fact'te
crossed/held-out form probleminin tek müdahale ile çözülüp çözülmediğidir.

### 6.4 Paralel karar sırası

```text
A. Qwen: 2,500-fact exploratory scale probe (seed 42)
B. SmolLM: 500-fact hybrid + contrastive-binding discovery (seed 42)
       |
       +-- başarısızsa: scale-up yok; yeni analiz/plan gerekir
       |
       +-- geçerse: aynı SmolLM kontratıyla seed 43 replication
                         |
                         +-- iki seed geçerse: SmolLM 2,500-fact scale control

Qwen ve SmolLM scale/feasibility sonuçları
       -> karşılaştırmalı model/recipe seçimi
       -> seçilen koşulun bağımsız doğrulaması
       -> ancak sonra final-M1 adayına ilişkin yeni karar
```

İki deney aynı anda planlanabilir; fakat her birinin kendi kontrol, evaluator, scratch namespace,
checkpoint seçme kuralı, storage estimate ve post-run audit'i olmalıdır. Sonuçlar görülmeden
Qwen ile SmolLM arasında kazanan ilan edilmez.

## 7. Açık kalan işler: önerilen planla güncellenmiş bağımlılık sırası

```text
Dok. 122 ile formalize edilmiş Qwen scale probe ve SmolLM contrastive-binding planları
  -> Qwen: exploratory 2,500-fact sonucu + gerekirse bağımsız replikasyon
  -> SmolLM: 500-fact seed-42 → seed-43 → ancak sonra 2,500-fact scale gate
  -> karşılaştırmalı model/recipe seçimi ve bağımsız doğrulama
  -> selected-scale M1 eğitimi, evaluated learned-fact membership ve artifact freeze
  -> M2-clean
  -> M3-lexical ve M3-fact (aynı frozen M1'den bağımsız)
  -> English retention + Turkish transfer + precommitted DID analizi
```

Şu anda yalnız ilk iki feasibility oku ayrıntılı, outcome-blind planlama aşamasına açıktır. Onların
ötesindeki hiçbir kutu yetkili değildir.

## 8. Bir sonraki AI ajanı için önerilen çalışma çerçevesi

1. Önce `AGENTS.md`, sonra Dok. 100, 117--120 ve bu raporu okuyun. Güncel otorite Dok. 100'dür; Dok. 121 yalnızca denetim/sentezdir.
2. Seed-43 sonucunu "biraz daha eğitim" veya "üçüncü seed" ile otomatik çözmeye çalışmayın. Dok. 120 bunu açıkça yasaklar.
3. Yeni planları **post-outcome exploratory** olarak etiketleyin. Qwen scale probe'unun, frozen iki-seed M1 scale gate'iyle aynı şey olmadığını açıkça yazın.
4. Qwen planında replay coefficient, checkpoint seçme kuralı, 500-subject curriculum/anchor budget ve evaluator sonuç görülmeden dondurulmalıdır. Seed-43'teki `profession` / Form-C zaafı için açıklama henüz hipotezdir.
5. SmolLM planında yalnız contrastive-ranking objective değişmelidir. Negatif sampling, `λ`, candidate inventory, update/factual exposure ve Forms C/D holdout durumu sonuçtan önce hash'lenmelidir.
6. Bridge sonucu ile M1 retention sonucunu karıştırmayın: bridge pilotu geçmedi; bu feasibility planı M2/M3 veya final M1 için izin değildir.
7. HU'da yeni iş başlatılacaksa `ssh-client/README.md` okunmadan, family-level storage/path/inode preflight yapılmadan veya resolved output path scratch değilken hiçbir iş submit edilmemelidir.

## 9. Mevcut karar tablosu

| Konu | Mevcut karar |
|---|---|
| 100-subject SmolLM form remediation | Tamamlandı, geçmedi; yeniden scale edilmez |
| Cross-family screen | Tamamlandı, hiçbir aday geçmedi |
| Qwen early stopping | Tanısal olarak elendi |
| Turkish bridge pilot | Tamamlandı, iki aile de frozen promotion gate'i geçmedi |
| Qwen seed-42 replay | Keşif/adjudication aşamasında umut verici, bağımsız doğrulama değildir |
| Qwen seed-43 replay | Tamamlandı, geçmedi |
| Qwen 500 subject / 2,500 fact | Planlama aşamasında exploratory feasibility probe; final scale gate değildir |
| SmolLM contrastive-binding, 100 subject / 500 fact | Planlama aşamasında exploratory remediation |
| 500 subject / 2,500 fact resmi M1 scale gate | HOLD; passing/replicated recipe gerektirir |
| 1,000 veya 5,000 subject M1 | HOLD |
| Final M1 artifact freeze | HOLD |
| M2-clean, M3-lexical, M3-fact | HOLD |
| Final difference-in-differences analizi | HOLD |

## 10. Kaynak haritası

- Başlangıç HOLD ve ilk altı aşama: Dok. 98.
- Güncel otorite, kapsam değişiklikleri ve operasyonel kayıt: Dok. 100.
- Form remediation ve model-family/early-stop tanıları: Dok. 101--108.
- Türkçe corpus, bridge kontratı, eğitim ve bridge sonuçları: Dok. 109--116.
- Kullanıcı kararlı bounded retention remediation, integrity adjudication ve replikasyon sonucu: Dok. 117--120.
- Bu audit'e eklenen Qwen scale probe ve SmolLM contrastive-binding feasibility önerisi: Bölüm 6 ve Dok. 122.
- İndeksin güncel okuma sırası: Dok. 00.

Bu rapor hiçbir başarısızlığı silmez veya başarısız bir recipe'i seçilmiş final M1 olarak sınıflandırmaz.
