# 122 - Qwen Scale ve SmolLM Contrastive-Binding Feasibility Planı

**Tarih:** 25 Temmuz 2026  
**Durum:** Uygulama ve HU submission öncesinde dondurulmuş exploratory plan  
**Otorite:** Kullanıcının açık kararı; Doküman 100, 117--121'deki HOLD ve artefact kuralları geçerliliğini korur.

## 1. Kapsam ve sınır

İki kontrollü discovery/feasibility deneyi açılmıştır:

1. Qwen2.5-1.5B'nin clean-English replay ile 500 subject / 2,500 fact scale probe'u.
2. SmolLM2-1.7B'nin 100 subject / 500 fact canonical-plus-A/B müfredatında relation-matched contrastive candidate-ranking müdahalesi.

Bunlar final M1 değildir. Deney A, seed-43'te başarısız olan Qwen replay recipe'ini passing
recipe olarak sınıflandırmaz; sadece ölçek davranışını ölçer. Deney B tek bir binding mekanizmasını
sınar. M2, M3, 1,000 subject, 5,000 subject, final M1 freeze ve DID analizi yetkili değildir.

Yeni config/launcher, yerel test, HU Git sync ve scratch preflight geçmeden hiçbir job submit
edilemez. Geçmiş launcher'lar doğrudan tekrar kullanılmaz.

## 2. Ortak değişmezler

- Relation V2'nin beş relation'ı, candidate inventory'leri, Branch A/B ataması ve metadata'sı değişmez.
- Held-out Forms C/D training row, ranking prompt veya negative seçimine girmez.
- Checkpoint seçimi: kendi frozen kapılarından geçen en erken optimizer update.
- Büyük dosyalar yalnız `/vol/tmp2/yesildau` altında yazılır; HU home artifact store değildir.
- Passing discovery sonucu, bağımsız seed replikasyonu olmadan final model seçimi vermez.

## 3. Deney A — Qwen 2,500-fact exploratory scale probe

### 3.1 Soru

Qwen'in 500 fact'teki yüksek factual robustness'ı 2,500 fact'te korunuyor mu? Fact sayısı
binding/interference veya generic-English PPL driftini artırıyor mu? Yeterli büyüklükte frozen
eligible-fact havuzu oluşuyor mu?

### 3.2 Dondurulmuş eğitim kontratı

| Öğe | Değer |
|---|---|
| Model | Frozen `Qwen/Qwen2.5-1.5B` local base manifest |
| Popülasyon | 500 subject × 5 relation = 2,500 fact; nested 100-subject subset zorunlu raporlanır |
| Müfredat | Fact başına 3 byte-identical canonical declarative + Form A direct/QA + Form B direct/QA |
| Factual rows | 17,500 train / 2,500 validation; answer-only, `supervise_eos: false` |
| Retention | Aynı optimizer adımında clean-English next-token replay, coefficient `0.5`, en çok 64 Qwen token |
| Anchor | WikiText-2 raw train/validation; 17,500/2,500 hizalı row, subject-surface exclusion, test split ile sıfır örtüşme |
| LR / scheduler | `5e-5`, constant-with-warmup, warmup ratio `0.02`, weight decay `0`, max grad norm `1.0` |
| Epoch / effective batch | 36 epoch / 2,500 factual row |
| Optimizer budget | 7 update/epoch × 36 = **252 update** |
| Physical schedule | batch `50`, accumulation `50`; A100-80GB smoke bunu geçmelidir |
| Seed / checkpoints | model/data seed `42/42`; step 25,50,75,100,125,150,175,200,225,250,252 + final |

Bu, Doküman 76'nın 500-subject eşleşmesiyle aynıdır: 36 epoch olmasına rağmen 1,260 değil
252 update vardır. Batch-50 smoke OOM veya güvenli bellek kapısını geçmezse full run submit edilmez;
farklı batch/accumulation planı append-only plan revizyonu gerektirir.

### 3.3 Değerlendirme ve karar

Her checkpointte 2,500 exact-prefix probe, A/B/C/D × direct/QA altında 20,000 hard probe,
eight-cell intersection, relation/Branch/subgroup/nested-100 sonuçları, WikiText-2 test PPL,
generic completion, lexical-empty ve synthetic-subject intrusion raporlanır. Ayrıca eligible
subject (held-out ailelerde ≥4/5 fact) ve strict 5/5 sayısı verilir.

Yorum kapıları Doküman 117'nin 500-subject minimumlarıdır: exact ≥90%, her relation/form/scaffold
cell ≥80%, robust global ve relation başına ≥70%, PPL ratio ≤1.25, sıfır lexical-empty/intrusion.
Bu sonuç resmi final scale pass değildir. İyi sonuç aynı 2,500-fact kontratın bağımsız replikasyonunu
önerir; kötü sonuç Qwen için negatif scale/retention kanıtıdır. Üçüncü seed veya coefficient sweep
otomatik açılmaz.

Scratch root ve başlangıç rezervi:

```text
/vol/tmp2/yesildau/qwen_scale_probe_v1
300 GiB = en az 250 GiB training + 50 GiB compact evaluation
```

## 4. Deney B — SmolLM2-1.7B contrastive-binding remediation

### 4.1 Soru ve tek müdahale

SmolLM2'nin sorun alanı retention değil unseen/crossed prompt altında factual binding'dir. Bu nedenle
yalnız aşağıdaki loss eklenir; LM eğitimi veya held-out evaluator değiştirilmez:

```text
L_total = L_answer_only_LM + 0.10 × L_relation_matched_candidate_ranking
```

Candidate-ranking loss, doğru cevabın index 0 olduğu 16'lı relation-matched candidate setinde mean
answer-token log-probability skorlarından cross entropy olarak hesaplanır. Set başına 15 negatif,
önceki prompt-consistency çalışmasıyla uyumlu deterministic `balanced_cycle` ve seed 42 ile seçilir.
City relation'larında subject'in karşı-city değeri candidate setine zorunlu olarak dahil edilir.

`λ=0.10` ana objective'i canonical LM olarak tutan, tek ve outcome-blind dondurulmuş değerdir.
λ sweep, post-hoc reweighting veya negative-count değişimi bu planın dışında kalır.

### 4.2 Dondurulmuş eğitim kontratı

| Öğe | Değer |
|---|---|
| Model | Frozen SmolLM2-1.7B base manifest |
| Popülasyon | 100 subject / 500 fact, Relation V2 |
| Control | Doküman 104 canonical-plus-A/B hybrid seed-42 endpoint'i; yeniden eğitilmez |
| Intervention data | Dok. 104 ile byte-identical 3,500 train / 500 validation; 7 row/fact |
| Training forms | 3 canonical declarative + Form A direct/QA + Form B direct/QA; C/D sıfır training exposure |
| Optimizer | `5e-5`, 36 epoch, batch `10`, accumulation `50`, effective batch `500`, **252 update** |
| Loss | Answer-only LM + sadece yukarıdaki contrastive ranking loss; EOS kapalı |
| Seed / checkpoints | model/data seed `42/42`; step 25,50,75,100,125,150,175,200,225,250,252 + final |

Yeni trainer iki loss'u aynı forward/backward optimize adımında hesaplar. Önce LM sonra ranking
fine-tune veya C/D data exposure bu planın dışındadır.

### 4.3 Kapılar ve karar

Doküman 103/104 kapıları değişmez: exact-prefix ≥90%, tüm A/B/C/D relation-form-scaffold cell'leri
≥80%, eight-cell robust global ve relation başına ≥70%, PPL ratio ≤1.25 ve generic integrity pass.
Seed-42 intervention tümünü geçerse aynı kontratla seed/data-seed 43 replikasyonu açılır. İki seed
geçerse ancak o zaman SmolLM için ayrı 2,500-fact scale planı yazılır.

Scratch root ve başlangıç rezervi:

```text
/vol/tmp2/yesildau/smollm_contrastive_binding_v1
275 GiB = training + compact evaluation başlangıç rezervi
```

Two-loss trainer için local CPU unit tests ve A100-80GB single-batch smoke; finite loss/gradient ve
scratch-only write kapıları geçmeden full training submit edilmez.

## 5. Uygulama ve submission sırası

1. 500-subject hybrid builder, Qwen anchor/evaluation registry ve Slurm chain yazılır.
2. SmolLM two-loss trainer, deterministic candidate builder, loss/gradient tests ve launcher yazılır.
3. Yerel tests/config-manifest integrity/syntax check geçer.
4. Dar commit/push, HU exact sync ve remote targeted tests yapılır.
5. Tek coordinated family preflight home/capacity/inodes, resolved scratch paths, queue, checkpoint
   bytes/count, toplam rezerv, model/dataset/probe hashes ve output absence'i kaydeder.
6. Capacity smoke'lar geçerse training, checkpoint evaluation, frozen summary ve post-run audit
   dependency-gated olarak bir kez submit edilir.

Qwen ve SmolLM ancak combined 575 GiB reserve ile preflight geçerse paralel koşabilir; aksi halde
ayrı preflight dalgalarıyla çalışır. Bu bilimsel kontratı değiştirmez.

## 6. Stop conditions ve çıktı

- Qwen batch-50 smoke geçmezse Qwen full training yoktur.
- Dataset/nesting/anchor alignment/C-D holdout/candidate audit başarısızsa ilgili job yoktur.
- Herhangi output/cache/log/tmp HU home'a çözülürse işlem durur.
- Sonuçtan sonra λ, negative sampling, batch budget, gate veya checkpoint seçimi değiştirilemez.

Implementation/preflight/launch güncellemeleri bu dokümana append edilir. Sonuçlar ayrı Doküman
123'te yazılır. Doküman 100 yalnız sonuçlar tamamlanınca güncellenir; geçmiş negatif kanıt
değiştirilmez.

## 7. V1 preparation kapasite düzeltmesi

Qwen V1 preflight `418361` geçti; ancak dependent preparation `418362`, 500 synthetic subject
surface exclusion sonrası resmi WikiText-2 validation splitinde yalnız 2,301 benzersiz temiz row
bulduğunu gösterdi. İstenen 2,500 anchor row'a ulaşamadığı için job training öncesinde güvenli
biçimde durdu; `418363` training başlamadı ve checkpoint/model oluşturulmadı.

Bu bir outcome veya retention sonucu değildir. Append-only V2 kontratı, factual training rows'u
17,500 ve 2,500-fact exact/hard evaluator denominatorlarını değiştirmez. Sadece Trainer'ın
monitoring validation splitini, aynı 2,301 temiz WikiText validation anchor ile bire bir hizalanan
deterministik 2,301 factual validation row'a indirir. Anchor duplicate edilmez, train/test split
karışmaz ve C/D holdout değişmez. Yeni scratch root `qwen_scale_probe_v2` olduğundan V1 evidence
üzerine yazılmaz; V2 için yeni preflight zorunludur.

## 8. Execution pointer — 26 July 2026

Qwen seed-42 scale probe completed all 252 updates and all eleven checkpoint evaluations. Its
append-only results, failure/retry record, storage audit, and provisional interpretation are in
Document 123. SmolLM contrastive seed-42 remains active only at the smoke-recovery stage; it has
no scientific result yet. Document 100 is not updated by this pointer because the independent
replication and the remaining frozen Qwen gate aggregation are still outstanding.
