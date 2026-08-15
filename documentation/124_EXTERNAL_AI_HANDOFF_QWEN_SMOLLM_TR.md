# External AI Handoff — Qwen Scale Probe and SmolLM Binding Pilot

**Tarih:** 28 Temmuz 2026  
**Amaç:** Bu belge, projeye yeni katılan bir AI/araştırma yardımcısının mevcut karar noktasını hızlı ve doğru anlaması için hazırlanmış Türkçe handoff'tur. Kronolojik bilimsel kayıtların özeti niteliğindedir; kaynak kayıtlar Doküman 100, 121, 122 ve 123'tür.

## 1. Tek cümlelik durum

Qwen2.5-1.5B, clean-English replay ile 2.500 synthetic fact üzerinde seed-42'de çok güçlü factual retrieval ve düşük erken-checkpoint PPL drift'i gösterdi; SmolLM2-1.7B için prompt-invariant binding'i hedefleyen contrastive objective teknik smoke'u geçti ve full seed-42 eğitimi A100 kuyruğunda.

## 2. Tezin ana sorusu ve M1'in rolü

Tezin ana sorusu şudur: **Türkçe factual adaptasyondan sonra modelde transfer mi görülür, yoksa hedef bilgilerin yeniden öğrenilmesi mi gerekir?** M1, bu ana sorunun kendisi değil; sonraki M2/M3 karşılaştırmalarının güvenilir olabilmesi için gereken İngilizce factual-adaptation temelidir.

Bu temel aşamada iki şeyi aynı anda koruyup koruyamadığımızı ölçüyoruz:

1. Fact'lerin exact ve prompt-robust biçimde geri çağrılması/binding'i.
2. Modelin genel İngilizce yeteneğinin bozulmaması.

Önemli ayrım: exact storage tek başına yeterli değildir. Held-out prompt biçimlerinde ve aynı subject içindeki relation ayrımında doğru cevaba erişim ayrıca ölçülür.

## 3. Geçmişteki ana problem

Önceki küçük ölçek Qwen denemelerinde factual retrieval çok güçlüydü; ancak generic WikiText-2 PPL oranı çoğu recipe'de frozen gate'i geçemeyecek kadar artıyordu. SmolLM2-1.7B ise PPL retention açısından daha temiz, fakat unseen/crossed promptlarda binding açısından zayıftı. Bu nedenle final M1/M2/M3 kararı daha önce HOLD durumundaydı.

## 4. Şu anki Qwen sonucu — seed-42 exploratory scale probe

### Dondurulmuş kontrat

- Model: `Qwen/Qwen2.5-1.5B`.
- Popülasyon: 500 subject × 5 relation = 2.500 fact.
- Eğitim: fact başına 3 canonical declarative + Form A direct/QA + Form B direct/QA; toplam 17.500 train row.
- Objective: answer-only factual LM + clean-English next-token replay (`coefficient=0.5`).
- Budget: 36 epoch, physical batch 50, accumulation 50, 252 optimizer update.
- Held-out evaluator: 2.500 exact probe; A/B/C/D × direct/QA altında 20.000 hard probe; WikiText-2 test PPL.
- Seed: 42. Bu bir discovery/scale probe'dur, final recipe replikasyonu değildir.

### Tam checkpoint eğrisi

Qwen frozen base PPL referansı 14.699'dur. Aşağıdaki hard top-1 tüm 20.000 probe'un global toplamıdır; cell-level robust intersection ile eş anlamlı değildir.

| Step | Hard top-1 | Exact primary | Paired relation binding | PPL | PPL/base |
|---:|---:|---:|---:|---:|---:|
| 25 | 14.67% | 13.84% | 8.2% | 13.413 | 0.912 |
| 50 | 98.40% | 99.64% | 99.2% | 15.200 | 1.034 |
| 75 | **99.29%** | **99.96%** | **100.0%** | **15.909** | **1.082** |
| 100 | 99.33% | 100.00% | 100.0% | 22.303 | 1.517 |
| 125 | 99.25% | 100.00% | 100.0% | 37.006 | 2.518 |
| 150 | 99.45% | 100.00% | 100.0% | 97.393 | 6.626 |
| 175 | 99.54% | 100.00% | 100.0% | 155.656 | 10.590 |
| 200 | 99.50% | 100.00% | 100.0% | 268.777 | 18.285 |
| 225 | 99.54% | 99.96% | 100.0% | 328.864 | 22.373 |
| 250 | 99.50% | 100.00% | 100.0% | 411.975 | 28.027 |
| 252 | 99.48% | 100.00% | 100.0% | 411.501 | 27.995 |

### Qwen yorumu

Step 75 güçlü provisional adaydır. Step 50'ye göre factual/binding sonuçları daha iyidir ve PPL ratio 1.082 ile hem hard `≤1.25` hem preferred `<1.10` bandındadır. Step 100 sonrası factual kazanım marjinal iken PPL maliyeti çok büyüktür; bu checkpointler frozen PPL gate'ini geçemez.

Ancak step-75'in **nihai seçimi**, sonuçlara bakıldıktan sonra “en iyi görünen checkpoint” seçilerek yapılamaz. Seed-43 başlamadan önce selection rule yazılı olarak dondurulmalıdır: örneğin önce tüm hard/robust/PPL gate'lerini geçen checkpointleri belirlemek, sonra bu küme içinden önceden tanımlı birincil metrik ve açık tie-break ile checkpoint seçmek. Aynı kural seed-42'ye geriye dönük exploratory analiz olarak, seed-43'e ise doğrulayıcı biçimde uygulanmalıdır.

Fakat şu iki nedenle “stabil M1 çözüldü” denemez:

1. Per-cell A/B/C/D ve eight-cell robust-intersection özeti henüz tamamlanmadı. Global %99.29 hard top-1 bu gate'in yerine kullanılamaz.
2. Sadece seed-42 var. Bağımsız seed-43 replikasyonu gerekir.

## 5. SmolLM contrastive-binding pilotu

### Müdahale

SmolLM'in retention yerine prompt-invariant binding sorunu hedefleniyor:

```text
L_total = L_answer_only_LM + 0.10 × L_relation_matched_candidate_ranking
```

- Model: SmolLM2-1.7B.
- Popülasyon: 100 subject / 500 fact.
- Train forms: canonical + A/B; C/D tamamen held-out.
- Candidate set: doğru cevap + deterministic relation-matched 15 negatif; city relation'larında paired karşı-city zorunlu negatif.
- Budget: 252 update, seed 42. Seed 43 yalnız seed-42 gate'leri geçerse açılacak.
- Zorunlu kontrol: aynı veri, update/factual-exposure bütçesi ve evaluator ile `λ=0` matched control çalıştırılmalıdır. Böylece olası kazanç contrastive terime atfedilebilir.
- Zorunlu loglar: canonical LM loss ile ranking loss ayrı kaydedilmeli; değerlendirmede C/D, eight-cell robust intersection, relation-level ranking margin ve PPL birlikte raporlanmalıdır.

### Güncel teknik durum

- İlk smoke Relation V2 column-schema uyumsuzluğunu gerçek trainer başlamadan yakaladı; düzeltildi.
- Sonraki smoke'lar A100 queue beklerken stale preflight guard'a takıldı; preflight artık GPU tahsisi anında çalışacak biçimde düzeltildi.
- Son smoke (`426979`) A100-80GB üzerinde başarıyla tamamlandı: fresh storage/path preflight PASS, 3.500/500 dataset, one optimizer update, finite train/eval loss, scratch-only checkpoint/final-model üretildi.
- Smoke runtime: 182.99 saniye/update. Bu nedenle full training için 16 saatlik operational wall limit kullanıldı; bilimsel recipe değişmedi.
- Full seed-42 training: Slurm job `429991`, A100 priority kuyruğunda. Bilimsel SmolLM metrikleri henüz yok.

## 6. Altyapı ve storage kuralları

- HU home (`/vol/fob-vol6/mi25/yesildau`) experiment artifact store olarak kullanılmaz.
- Checkpoint/model/cache/log/evaluation yalnız `/vol/tmp/yesildau` veya `/vol/tmp2/yesildau` altına yazılır.
- Son audit: home 7.91 GiB; project checkout 16.6 MiB; project altında checkpoint/optimizer/model dosyası yok; `runs` ve `artifacts` scratch'e resolve oluyor.
- Qwen scratch tree: `/vol/tmp2/yesildau/qwen_scale_probe_v3` (yaklaşık 99 GiB, cleanup henüz yapılmadı).
- SmolLM scratch tree: `/vol/tmp2/yesildau/smollm_contrastive_binding_v1`.

## 7. Arkadaş AI'dan beklenen kritik yardım

Lütfen aşağıdaki sorulara evidence-first yaklaşımıyla cevap ver:

1. Qwen step-75 için per-cell A/B/C/D ve robust-intersection özeti olmadan hangi iddialar meşru, hangileri erken olur?
2. Step-75'in PPL/factual Pareto seçimi metodolojik olarak doğru mu? Erken checkpoint seçimi için hangi ek leakage/selection riskleri var?
3. Qwen seed-43 replication planı nasıl olmalı? Önerilen kural: seed dışında veri, recipe, replay, batch, eşikler, evaluator ve checkpoint-selection kuralında hiçbir şey değiştirmemek. Bu yeterli mi?
4. SmolLM contrastive pilotu için `λ=0` matched control, ayrı LM/ranking-loss logları, C/D, robust intersection, relation-level margin ve PPL seti yeterli mi; ek zorunlu diagnostic var mı?
5. Eğer Qwen seed-43 geçmezse ve SmolLM seed-42 geçerse, iki aday arasında fair model-selection nasıl yapılmalı?

## 8. Kesinlikle yapılmaması gerekenler

- Sonuç görüldükten sonra threshold, lambda, negative count, data exposure veya checkpoint seçme kuralını değiştirmek.
- M1 validasyon hedefini tezin asıl transfer-vs-relearning sorusuyla karıştırmak; M1 yalnız sonraki Türkçe adaptasyon karşılaştırmasının güvenilir başlangıç noktasıdır.
- Qwen'in global hard top-1 sonucunu cell-level robust intersection yerine geçirmek.
- Seed-42 sonucunu final M1 olarak sunmak.
- SmolLM'i 2.500 fact'e doğrudan scale etmek; önce seed-42 ve seed-43 500-fact binding gate'leri geçmelidir.
- Büyük artifactleri HU home'a taşımak veya Qwen checkpointlerini selection/checksum öncesi silmek.

## 9. Kaynak dokümanlar

- `100_MASTER_PROJECT_STATUS_AND_EXECUTION_PLAN.md` — mevcut operasyonel master handoff.
- `121_PLAN_EXECUTION_AUDIT_98_TO_120_TR.md` — geçmiş plan/uygulama audit'i.
- `122_QWEN_SCALE_AND_SMOLLM_CONTRASTIVE_FEASIBILITY_PLAN.md` — frozen exploratory plan.
- `123_QWEN_SCALE_PROBE_RESULT_AND_SMOLLM_PILOT_STATUS.md` — job ID, failure/retry, storage audit ve tüm ayrıntılı güncel kayıt.
