# 146 — LUNA-Worker 2 Ayrıntılı Araştırma ve Denetim Handoff'u

**Tarih:** 2026-08-07  
**Önerilen ajan adı:** `LUNA-Worker 2 — Model, Corpus & Literature Audit`  
**Durum:** Yürütülebilir read-only araştırma/dokümantasyon handoff'u  
**Yetki sınırı:** Literatür, model provenance, yerel kanıt ve korpus metadata/kalite planı denetimi;
yeni training, HU bağlantısı, Slurm submission, büyük model/korpus indirme veya artifact silme yok

## 1. Görev tanımı

LUNA-Worker 2'nin görevi yeni bir model eğitmek değildir. Görevi, tezdeki bir sonraki deneyin
yanlış motivasyon, belirsiz kaynak model veya etkisiz Türkçe adaptasyon yüzünden yeniden
yorumlanamaz hâle gelmesini önleyecek **karar paketini** hazırlamaktır.

Ana araştırma sorusu:

> Ağırlıklı olarak İngilizceyle eğitilmiş bir base model İngilizce M1 aşamasında öğrendiği sentetik
> olgulara, hedef olguları Türkçe görmeden yalnız genel Türkçe continual pretraining sonrasında
> erişebilir mi; aynı olguların Türkçe yeniden gösterilmesi ne kadar ek fayda sağlar?

Bu soruyu çalıştırılabilir hâle getirmek için ajan beş şeyi kanıtlamalıdır:

1. Hangi base model adaylarının Türkçe exposure'ı düşük olduğuna dair güvenilir kanıt vardır?
2. Bu adaylardan hangileri önceki M1 kanıtımıza göre sentetik fact öğrenmeye uygundur?
3. Hangi Türkçe korpus gerçekten dil adaptasyonu için yeterince geniş, temiz ve belgelenmiştir?
4. Türkçe adaptasyonun gerçekten çalıştığını hangi test paketi gösterecektir?
5. Hangi koşullar sağlanırsa sınırlı M1 screen veya daha sonra M2-A/M2-B eğitimi açılabilir?

## 2. Değiştirilemez güncel proje durumu

LUNA-Worker 2 aşağıdaki noktaları yeni baştan tartışılacak varsayımlar değil, korunacak kanıt olarak
ele almalıdır:

- Qwen2.5-1.5B, 2.500 fact M1'i iki seed'de geçmiştir.
- Seçili M1 checkpoint'leri seed 42 için step 75, seed 43 için step 50'dir.
- Sekiz-cell robust sonuçlar yaklaşık `%96.08` ve `%96.20`; PPL ratio'ları `1.082` ve `1.032`dir.
- SmolLM2-1.7B exact storage üretmiş fakat robust retrieval `%39.6`, `%52.2` ve son remediation ile
  `%55.8` seviyesinde kalmıştır; yeni ana SmolLM optimizasyon dalı kapalıdır.
- Eski cross-family 500-fact screen'de StableLM güçlü fakat tam geçmeyen sonuç; Gemma ve Llama ise
  ciddi robustness/PPL sorunları üretmiştir.
- Tamamlanan Qwen Türkçe ailesi teknik olarak geçerli iki kardeş koldan oluşmuştur; `M3-fact`,
  `M2-clean`den başlatılmamıştır.
- Bu eski aile artık **Qwen Wikipedia-only, yaklaşık 1M-token pilotu** olarak yorumlanmalıdır.
- Pilotun donmuş kararı `primary_success_criterion_not_met`tir; bu sonuç silinmeyecek, threshold
  değiştirilerek başarıya çevrilmeyecek ve altyapı hatası diye sunulmayacaktır.
- Yeni ana koşulların doğru kavramsal adı:

```text
aynı donmuş M1
├── M2-A: genel Türkçe korpus; hedef sentetik fact yok
└── M2-B: aynı Türkçe adaptasyon + kontrollü Türkçe target-fact re-exposure
```

- Yeni training ancak ayrı bir frozen execution contract ve açık kullanıcı yetkisiyle açılabilir.

## 3. Zorunlu okuma sırası

Belge adları ve numaraları özellikle verilmiştir. Ajan her belgeyi okumalı; yalnız dosya adına göre
sonuç çıkarmamalıdır.

### Katman A — Kurallar, ana tarih ve yeni bilimsel otorite

1. **`AGENTS.md` — Project Agent Instructions**
   - Depolama, HU, Git, artifact ve stop-condition kuralları.
2. **Doküman 00 — `00_DOCUMENTATION_INDEX.md`**
   - Belge otoritesi ve kronoloji.
3. **Doküman 100 — `100_MASTER_PROJECT_STATUS_AND_EXECUTION_PLAN.md`**
   - Tarihsel master synthesis ve 3/6 Ağustos append-only düzeltmeleri.
4. **`Expose.pdf`**
   - Tamamını oku; özellikle sayfa 6'daki paralel no-repetition/repetition tasarımını çıkar.
5. **Doküman 144 — `144_SUPERVISOR_FEEDBACK_AND_SCIENTIFIC_REALIGNMENT_TR.md`**
   - Max geri bildirimi, M2-A/M2-B düzeltmesi ve eski pilotun yeni yorumu.
6. **Doküman 145 — `145_LITERATURE_FIRST_M1_MODEL_AND_TURKISH_ADAPTATION_ROUTE_TR.md`**
   - Model, korpus, capability ve aşamalı rota.

Ayrıca **Doküman 84 — `84_HU_HOME_STORAGE_INCIDENT_AND_ARTIFACT_LIFECYCLE.md`** okunmalıdır.
LUNA-Worker 2 HU'ya bağlanmayacak olsa da sonraki planların neden model, dataset, cache ve output
pathlerini scratch'e yönlendirmesi gerektiğini ve seçili artifactlerin neden özel koruma altında
olduğunu bilmelidir.

Bu Katman A kaynakları okunmadan hiçbir yeni doküman yazılmamalıdır.

### Katman B — M1'in neden zor olduğu ve model ailesi kanıtı

7. **Doküman 94 — `94_PRE_M2_FROZEN_HARD_EVALUATION_REPORT.md`**
   - Donmuş hard evaluation ve factual binding ayrımı.
8. **Doküman 95 — `95_PRE_M2_PARAPHRASE_COUNTERBALANCE_REPORT.md`**
   - Form counterbalance ve crossed-form problemi.
9. **Doküman 96 — `96_PRE_M2_JOINT_RELATION_CONTROL_REPORT.md`**
   - Joint relation capture kontrolü.
10. **Doküman 97 — `97_PRE_M2_DRIFT_ABLATION_REPORT.md`**
    - Learning-rate/PPL drift ablation.
11. **Doküman 98 — `98_PRE_M2_FINAL_DECISION.md`**
    - Eski HOLD ve Max sorularına verilen kontrollü yanıt.
12. **Doküman 101 — `101_M1_FORM_GENERALIZATION_REMEDIATION_PLAN.md`**
    - İlk form-generalization müdahalesi.
13. **Doküman 102 — `102_M1_FORM_GENERALIZATION_REMEDIATION_RESULT.md`**
    - İlk remediation'ın negatif sonucu.
14. **Doküman 103 — `103_M1_CANONICAL_FORM_DIVERSITY_REMEDIATION_PLAN.md`**
    - Canonical-plus-form-diversity planı.
15. **Doküman 104 — `104_M1_CANONICAL_FORM_DIVERSITY_REMEDIATION_RESULT.md`**
    - SmolLM M1 storage/robustness ayrışması.
16. **Doküman 105 — `105_M1_CROSS_FAMILY_MODEL_SCREENING_PLAN.md`**
    - Qwen, Gemma, StableLM ve Llama için donmuş model-family screen.
17. **Doküman 106 — `106_M1_CROSS_FAMILY_MODEL_SCREENING_RESULT.md`**
    - Beş modelin exact, hard, Forms A-D, robust ve PPL sonuçları.
18. **Doküman 107 — `107_QWEN_CHECKPOINT_RETENTION_PARETO_DIAGNOSTIC_PLAN.md`**
    - Qwen retention/Pareto sorusu.
19. **Doküman 108 — `108_QWEN_CHECKPOINT_RETENTION_PARETO_DIAGNOSTIC_RESULT.md`**
    - Qwen'in factual başarı ile PPL trade-off'u.
20. **Doküman 117 — `117_M1_RETENTION_REMEDIATION_AND_500_SUBJECT_SCALE_GATE.md`**
    - Replay/retention recipe ve checkpoint kuralı.
21. **Doküman 118 — `118_M1_RETENTION_EVALUATION_RESULT_AND_INTEGRITY_ADJUDICATION.md`**
    - Qwen seed-42 result ve evaluator adjudication.
22. **Doküman 119 — `119_M1_QWEN_RETENTION_SEED43_REPLICATION_PLAN.md`**
    - Seed-43 replication contract.
23. **Doküman 120 — `120_M1_QWEN_RETENTION_SEED43_REPLICATION_RESULT.md`**
    - Seed-43 ilk replication kanıtı.
24. **Doküman 121 — `121_PLAN_EXECUTION_AUDIT_98_TO_120_TR.md`**
    - 98–120 arasındaki plan/sonuç audit'i.
25. **Doküman 122 — `122_QWEN_SCALE_AND_SMOLLM_CONTRASTIVE_FEASIBILITY_PLAN.md`**
    - Qwen scale ile SmolLM contrastive sorusunun ayrımı.
26. **Doküman 123 — `123_QWEN_SCALE_PROBE_RESULT_AND_SMOLLM_PILOT_STATUS.md`**
    - 2.500-fact Qwen probe ve SmolLM pilotu.
27. **Doküman 125 — `125_QWEN_CONFIRMATION_AND_SMOLLM_MATCHED_CONTROL_EXECUTION_PLAN.md`**
    - Matched control ve Qwen confirmation tasarımı.
28. **Doküman 126 — `126_QWEN_SEED43_AND_SMOLLM_TRAINING_COMPLETION_REPORT.md`**
    - İki dalın tamamlanma kaydı.
29. **Doküman 127 — `127_QWEN_SCALE_REPLICATION_RESULT_AND_SMOLLM_LAMBDA025_STATUS.md`**
    - Qwen iki-seed nihai M1 kanıtı ve SmolLM karşılaştırması.
30. **Doküman 128 — `128_SMOLLM_500_FACT_PROMPT_CONSISTENCY_REMEDIATION_PLAN.md`**
    - Son SmolLM remediation ve `%55.8` kapanış sonucu.
31. **Doküman 129 — `129_EXTERNAL_COLLABORATOR_HANDOFF_QWEN_SMOLLM_AND_TURKISH_STAGE_TR.md`**
    - Qwen/SmolLM/Türkçe aşaması için önceki ayrıntılı handoff.
32. **Doküman 130 TR — `130_COMPLETE_PROJECT_HISTORY_METHODS_RESULTS_AND_FORWARD_PLAN_TR.md`**
    - Supervisor/agent seviyesinde tam tarih, yöntem ve sonuç sentezi.

### Katman C — Eski Türkçe bridge ve korpus kanıtı

33. **Doküman 109 — `109_TURKISH_BRIDGE_RETENTION_AND_SCALE_DECISION_PLAN.md`**
    - İlk bridge, retention ve ölçek kararı.
34. **Doküman 110 — `110_TURKISH_BRIDGE_CORPUS_RESULT_AND_FREEZE.md`**
    - `trwiki-20260601` corpus kimliği, temizlik, contamination ve freeze.
35. **Doküman 111 — `111_TURKISH_BRIDGE_CONTRACT_V2_AND_EXECUTION_GATE.md`**
    - Türkçe bridge V2 contract.
36. **Doküman 112 — `112_TURKISH_BRIDGE_CONTRACT_V2_RESULT_AND_TRAINING_DECISION.md`**
    - Contract sonucu ve training kararı.
37. **Doküman 113 — `113_TURKISH_BRIDGE_PARALLEL_TRAINING_PLAN_AND_LAUNCH.md`**
    - Paralel bridge training planı.
38. **Doküman 114 — `114_QWEN_TURKISH_BRIDGE_CLEAN_GPU_RECOVERY_PLAN.md`**
    - GPU recovery; bilimsel sonuç sanılmaması gereken operasyonel hata kaydı.
39. **Doküman 115 — `115_TURKISH_BRIDGE_FROZEN_EVALUATION_PLAN.md`**
    - Frozen bridge evaluation.
40. **Doküman 116 — `116_QWEN_BRIDGE_TOKENIZER_RECOVERY_PLAN.md`**
    - Tokenizer recovery ve artifact bütünlüğü.
41. **Doküman 132 — `132_PRE_M2_QWEN_READINESS_AND_BASELINE_PLAN.md`**
    - Bilingual baseline, PPL ve pre-M2 readiness.

Bu katmanda özellikle şu ayrım çıkarılmalıdır:

- corpus teknik olarak temiz/provenance açısından güçlü müydü?
- corpus dozu ve domain çeşitliliği gerçek Türkçe adaptation için yeterli miydi?
- hangi state'lerde Türkçe PPL gerçekten ölçüldü, hangilerinde ölçülmedi?

### Katman D — Tamamlanan Qwen Türkçe pilotu ve kapanış

42. **Doküman 133 — `133_QWEN_2500_FACT_M2_M3_EXECUTION_HANDOFF_PLAN.md`**
    - Eski frozen scientific plan ve §14 execution closure.
43. **Doküman 134 — `134_QWEN_PRE_M2_GPU_BLOCKER_AND_OFFLINE_PREPARATION_STATUS.md`**
    - Bilingual M1 baseline ve operasyonel hazırlık.
44. **Doküman 135 — `135_QWEN_M2_M3_CONTRACT_AND_MATERIALIZATION_STATUS.md`**
    - Eşit `1,048,576` token kolları, materialization ve training ledger.
45. **Doküman 136 — `136_QWEN_M2_M3_ENDPOINT_EVALUATION_GPU_ALLOCATION_STATUS.md`**
    - 96/96 evaluation, metrics ve frozen gate; sonuç otoritesi.
46. **Doküman 137 — `137_QWEN_M2_M3_EXTERNAL_REVIEW_HANDOFF_PROMPT_EN.md`**
    - Dış review için kanıt beklentileri.
47. **Doküman 138 — `138_QWEN_M2_M3_COMPLETED_MILESTONE_AND_SCIENTIFIC_INTERPRETATION_EN.md`**
    - Negatif/inconclusive sonucun doğru bilimsel yorumu.
48. **Doküman 139 — `139_POST_M2_M3_INDEPENDENT_NEXT_ACTION_PLAN_EN.md`**
    - O dönemde izinli read-only sonraki işler.
49. **Doküman 140a — `140a_QWEN_M2_M3_INDEPENDENT_REVIEW_RESULT_EN.md`**
    - Bağımsız doğrulama ve `PASS WITH CONCERNS`.
50. **Doküman 141 — `141_QWEN_M2_M3_EXPLORATORY_MECHANISM_ANALYSIS_PLAN_EN.md`**
    - Exploratory analiz contract'ı.
51. **Doküman 142 — `142_QWEN_M2_M3_EXPLORATORY_MECHANISM_ANALYSIS_RESULT_EN.md`**
    - Geniş Türkçe-involving düşüş ve küçük factual recovery.
52. **Doküman 143 — `143_QWEN_M2_M3_ARTIFACT_RETENTION_FREEZE_AND_STORAGE_AUDIT_EN.md`**
    - Dört endpoint artifact'in model-only freeze ve hash doğrulaması.

## 4. Belge otoritesi ve çelişki çözümü

Çelişki görülürse aşağıdaki sıra kullanılmalıdır:

1. `AGENTS.md` güvenlik/operasyon kuralları.
2. Doküman 144–146 yeni bilimsel yön ve yetki sınırı.
3. Doküman 136 tamamlanan Qwen pilotunun sayısal/operasyonel sonucu.
4. Doküman 138 ve 142 bilimsel ve exploratory yorum.
5. Doküman 140a bağımsız review.
6. Doküman 143 artifact closure.
7. Doküman 100 tarihsel master ve dated append-only corrections.
8. Daha eski belgeler kendi zamanlarındaki kararların kanıtıdır; güncel durum için tek başına
   kullanılmaz.

Örnek: Doküman 98 veya 100'ün eski bölümünde `M2 HOLD` yazması, tamamlanmış Doküman 136 sonucunu
iptal etmez. Benzer şekilde Doküman 131'deki 25.000-fact planı, Doküman 144–146 sonrasında otomatik
olarak yürütülebilir değildir.

## 5. Çalışma yöntemi ve kanıt standardı

### 5.1 Kaynak önceliği

Her dış iddia için öncelik:

1. hakemli makale/ACL Anthology/OpenReview conference page;
2. resmi model veya dataset card;
3. resmi repository/config/training log;
4. resmi blog/technical report;
5. ikincil kaynak yalnız keşif için.

Bir model kartı “English-only” diyorsa bu güçlü belge olarak yazılabilir. Yalnız diller listesinde
Türkçe yoksa “Türkçe görmedi” denmemeli; `Turkish not listed` denmelidir. Training dağılımı
açıklanmıyorsa `Turkish exposure unknown` yazılmalıdır.

### 5.2 Her iddianın kayıt biçimi

Her tablo satırında mümkünse şunlar bulunmalıdır:

- iddia;
- kaynak URL/dosya;
- exact bölüm/sayfa/line veya model-card heading;
- erişim tarihi;
- kanıt düzeyi: `strong`, `moderate`, `weak`, `unknown`;
- doğrudan kaynak iddiası mı, ajan inference'ı mı;
- çözülmemiş soru.

### 5.3 Başarısız ve belirsiz bulgular

- Kaynak bulunamadıysa `not documented` yaz.
- Bir sayı iki kaynakta farklıysa ikisini de yaz, olası açıklamayı inference olarak etiketle.
- Eksik bilgiye dayanarak corpus veya model seçme.
- Sonucu güzelleştirmek için belirsizliği kaldırma.

## 6. İş paketi 0 — Proje-state doğrulaması

### Amaç

Yeni araştırmanın yanlış veya stale bir proje durumundan başlamamasını sağlamak.

### Adımlar

1. Zorunlu okuma zincirini tamamla.
2. Aşağıdaki state tablosunu kaynak belgelerden yeniden üret:
   - Qwen M1 seed/checkpoint/robust/PPL;
   - SmolLM üç ana robust sonucu;
   - StableLM/Gemma/Llama screen sonucu;
   - eski Qwen pilot M1/M2-clean/M3-fact EN→EN, TR→EN, TR→TR;
   - primary interaction verdict;
   - artifact freeze durumu.
3. Her sayı için belge numarası ve bölümünü yaz.
4. Eski `M2/M3` adları ile yeni `M2-A/M2-B` kavramsal crosswalk'ını yaz.
5. `verified`, `interpretive correction` ve `open question` alanlarını ayır.

### Çıktı

Bu tablo Doküman 147'nin ilk bölümü olmalıdır; ayrı result iddiası yaratmamalıdır.

### Tamamlanma kapısı

Doküman 106, 127, 136, 138, 142 ve 143 arasında açıklanamayan sayısal çelişki kalmamalıdır.

## 7. İş paketi 1 — Kaynak-model provenance audit'i

### Ana adaylar

- `allenai/OLMo-2-0425-1B`
- `EleutherAI/pythia-1.4b`
- `tiiuae/falcon-rw-1b`
- `Qwen/Qwen2.5-1.5B` — mevcut çokdilli pozitif kontrol
- `stabilityai/stablelm-2-1_6b` — yalnız ikinci seviye aday

SmolLM, Gemma ve Llama yeniden ana aday yapılmayacaktır; önceki negatif kanıtları comparison olarak
özetlenecektir.

### Her model için çıkarılacak alanlar

1. Tam repo adı ve pinned revision/commit bulunabiliyor mu?
2. Base/pretrained mi, SFT/instruct/chat mi?
3. Model size, architecture, context length, tokenizer ve vocabulary size.
4. Training token sayısı.
5. Training dataset adları ve erişilebilirlikleri.
6. Bildirilen diller ve Türkçe hakkında exact ifade.
7. Web contamination yüzünden sıfır-Türkçe iddiasının sınırı.
8. Lisans ve akademik kullanım uygunluğu.
9. Checkpoint/log/data order açıklığı.
10. Transformers/PyTorch ve tek-GPU uyumluluğuna ilişkin yalnız belgeli bilgi.
11. Mevcut proje M1 sonucu veya `not yet tested`.
12. Türkçe adaptation için beklenen headroom.
13. Bilimsel artı, bilimsel eksi, operasyonel risk.

### Model seçim tablosu

Her modele 0–2 ordinal puan verilebilir, fakat toplam puan otomatik seçim yapmamalıdır:

| Boyut | 0 | 1 | 2 |
|---|---|---|---|
| Turkish provenance | bilinmiyor/çokdilli | Türkçe listede yok | English-only açık belge |
| Stage clarity | belirsiz | base fakat recipe eksik | base ve tam stage açık |
| Reproducibility | az | kısmi | data/checkpoint/log güçlü |
| Existing M1 evidence | başarısız | sınırda/test edilmedi | kullanılabilir/geçmiş |
| Turkish headroom | ölçülemez | muhtemel | baseline ile ölçülebilir |
| Compute fit | uygunsuz | belirsiz | HU tek-GPU için makul |

Son karar skora göre değil, kaynaklı gerekçe ve Pareto değerlendirmesiyle yazılmalıdır.

### Çıktı

**Doküman 147:** `147_LUNA_MODEL_PROVENANCE_AND_M1_SHORTLIST_AUDIT_TR.md`

Zorunlu final verdict seçenekleri:

- `shortlist_ready_for_local_baseline_audit`
- `shortlist_blocked_by_provenance_gaps`
- `retain_qwen_only_until_better_evidence`

Bu verdict training izni değildir.

## 8. İş paketi 2 — Cross-lingual language-adaptation literatür matrisi

### Türkçe çekirdek kaynaklar

1. *Bridging the Bosphorus: Advancing Turkish Large Language Models...*
2. MODA — *Building a Turkish Large Language Model via Continual Pre-Training and
   Parameter-Efficient Adaptation*.
3. VBART.
4. TURNA.
5. Kumru model ve dataset cards.
6. CETVEL.
7. TurkBench.
8. Alican Kiraz'ın Kara-Kumru ve ilgili açık dataset/model cards.

### Türkçe dışı zorunlu örnekler

1. *How to Adapt Your Pretrained Multilingual Model to 1600 Languages*.
2. *Breaking Language Barriers: Cross-Lingual Continual Pre-Training at Scale*.
3. *Arabic Stable LM: Adapting Stable LM 2 1.6B to Arabic*.
4. Sherkala-Chat/Kazakça continual-pretraining çalışması.
5. DIPLomA.
6. Unseen-language adaptation veya language adapters üzerine en az bir güçlü karşılaştırmalı
   çalışma.

### Her makaleden çıkarılacak alanlar

- source model ve exact stage;
- hedef dil ve modelin o dili önceden görüp görmediği;
- tokenizer değişikliği;
- corpus adı, document/token/byte büyüklüğü;
- language/quality/dedup filtreleri;
- objective: full CPT, LoRA, adapters, SFT veya merge;
- target-language ve English/replay karışım oranı;
- LR, batch/effective tokens, sequence length, steps/epochs ve total target-language exposure;
- checkpoint selection;
- source-language forgetting ölçümü;
- target-language capability ölçümü;
- factual/cross-lingual ölçüm varsa yönü;
- pozitif, negatif ve sınırlı bulgular;
- bizim M2-A/M2-B tasarımına uygulanabilir ders;
- kopyalanmaması gereken fark.

### Çıktı

**Doküman 148:** `148_CROSS_LINGUAL_LANGUAGE_ADAPTATION_LITERATURE_MATRIX_TR.md`

Doküman sonunda en fazla üç literature-backed recipe family önerilmeli; “en iyi sonuç” değil,
deneysel sadelik ve yorumlanabilirlik öncelikli olmalıdır.

## 9. İş paketi 3 — Türkçe korpus provenance ve kalite audit'i

### Karşılaştırılacak corpus seçenekleri

1. Mevcut `trwiki-20260601`.
2. Turkish CulturaX.
3. `vngrs-ai/vngrs-web-corpus`.
4. Yalnız güçlü kaynak varsa Wikipedia + geniş web kontrollü karışımı.

SFT/instruction datasetleri bu tabloya genel CPT korpusu gibi eklenmemelidir. Alican Kiraz
`Turkish-SFT-Dataset-v1.0` ve benzeri veriler ayrı `SFT evidence` bölümünde tutulmalıdır.

### Her corpus için metadata

- canonical repo/source URL;
- exact revision/snapshot tarihi;
- lisans;
- dosya formatı ve yayınlanan toplam boyut;
- document/page sayısı;
- kaynak tokenizer ve raporlanan token sayısı;
- her aday tokenizerla token sayısının henüz ölçülüp ölçülmediği;
- kaynak bileşimi: Wikipedia, mC4, OSCAR, news, forum vb.;
- language identification yöntemi;
- exact ve near-dedup yöntemi;
- heuristic/semantic quality filtering;
- PII, zararlı içerik, boilerplate ve spam riskleri;
- domain dağılımı;
- benchmark overlap riski;
- sentetik subject/object contamination riski;
- akademik kullanım kısıtları.

### Kumru sayı uyuşmazlığı özel görevi

Aşağıdaki iki iddiayı aynı şeymiş gibi birleştirme:

- Kumru kartı: yaklaşık `500 GB`, `300B` pretraining tokenı;
- `vngrs-web-corpus` kartı: yaklaşık `84.9 GB`, `25.33B` VBART-tokenizer tokenı.

Şunları araştır:

1. 500 GB başka/ek bir unpublished corpus versionı mı?
2. 300B token epoch-toplam exposure mı?
3. Fark tokenizer kaynaklı mı?
4. Kumru başka kaynaklar da kullanıyor mu?
5. Resmî kaynak cevap vermiyorsa hangi kısım `not documented` kalmalıdır?

Kesin kaynak bulunmazsa uyuşmazlığı çözülmüş gösterme.

### Audit planı

Büyük corpus indirmeden önce uygulanacak planı yaz:

1. metadata ve file manifest;
2. küçük streaming/stratified sample;
3. language-ID distribution;
4. Unicode/encoding ve length istatistikleri;
5. boilerplate/spam/repetition örnekleri;
6. exact + MinHash near-duplicate tahmini;
7. source/domain stratification;
8. sentetik subject/object/alias exact + normalized + fuzzy contamination scan;
9. evaluation overlap kontrolü;
10. seçili tokenizerlarla fertility ve projected token bütçesi;
11. SHA-256 ve immutable manifest tasarımı.

### Çıktı

**Doküman 149:** `149_TURKISH_CORPUS_PROVENANCE_QUALITY_AND_CONTAMINATION_AUDIT_PLAN_TR.md`

Zorunlu verdict seçenekleri:

- `metadata_ready_for_bounded_sample_audit`
- `corpus_choice_blocked`
- `wikipedia_control_plus_web_candidate`

Bu doküman büyük download veya corpus materialization izni değildir.

## 10. İş paketi 4 — Türkçe capability ve manipulation-check tasarımı

### Temel ilke

Factual TR→EN başarısı tek başına “Türkçe adaptasyon çalıştı” kanıtı değildir. Model state'leri:

```text
M0 → M1 → M2-A / M2-B
```

aynı dil-adaptasyon ölçüm paketine girmelidir.

### Paket bileşenleri

#### A. Tokenizer fertility

- aynı Türkçe ve İngilizce sample;
- token/document, token/word, character/token;
- Türkçe/İngilizce fertility ratio;
- çok uzun parçalanan morfolojik kelime örnekleri;
- special-token veya byte-fallback oranı.

Tokenizer fertility bir model-kalite skoru değildir; maliyet ve erişilebilirlik tanısıdır.

#### B. Held-out PPL

- training corpusundan ayrı frozen Turkish split;
- English retention split;
- exact data identity ve hash;
- aynı model/tokenizer zinciri içinde pre/post delta;
- farklı tokenizerlı modeller arasında raw PPL sıralaması yapılmaması;
- bootstrap veya document-level uncertainty planı.

#### C. Base-model uyumlu Türkçe capability

Aşağıdaki kaynaklardan küçük, donmuş ve compute-bounded bir paket seç:

- CETVEL;
- TurkBench;
- TurkishMMLU;
- EXAMS-TR;
- TRCLAIM-19;
- gerekiyorsa açık morphology/grammar diagnostics.

Her görev için şu soruları yanıtla:

1. Base causal LM instruction-following olmadan adil ölçülebilir mi?
2. Scoring generation mı, likelihood/MCQ/cloze mu?
3. Prompt Türkçe mi ve answer language ne?
4. Metric nedir?
5. Training corpus overlap riski nedir?
6. Lisans ve indirme yolu nedir?
7. Küçük model için floor/ceiling problemi var mı?

Ana manipulation check mümkünse likelihood/MCQ/cloze temelli olmalıdır. Chat-quality benchmark ana
kapı yapılmamalıdır.

#### D. Factual directions

- EN→EN: M1 storage/retention.
- TR→EN: birincil cross-lingual factual access.
- TR→TR: ikincil access + Turkish lexicalization.
- EN→TR: yalnız exploratory; ana başarı metric'i değil.

#### E. Kontroller

- target fact contamination;
- alias freeze;
- Forms A–D ve scaffold eşitliği;
- relation binding;
- no-answer/empty/repetition diagnostics;
- aynı test paketinin M2-A ve M2-B'ye uygulanması.

### Manipulation-check açılma kuralı

Sayısal threshold henüz uydurulmayacaktır. Doküman 148 literatür matrisi ve benchmark baseline
özellikleri görülmeden kesin değer dondurulmaz. Ancak kural yapısı şu olmalıdır:

1. Turkish PPL pre/post iyileşmeli;
2. en az bir bağımsız base-compatible Turkish capability ölçümü beklenen yönde değişmeli veya
   önceden tanımlı equivalence/no-harm gerekçesi bulunmalı;
3. English PPL ve M1 EN→EN retention önceden belirlenen guardrail içinde kalmalı;
4. sonuç factual TR→EN treatment sonucu görülmeden seçilmelidir.

### Çıktı

**Doküman 150:** `150_TURKISH_CAPABILITY_AND_ADAPTATION_MANIPULATION_CHECK_PLAN_TR.md`

Bu belge evaluator implementasyonu veya broad evaluation submission izni değildir.

## 11. İş paketi 5 — Birleşik karar kapısı

Doküman 147–150 tamamlandıktan sonra çelişkileri çözerek tek karar belgesi üret.

### Çıktı

**Doküman 151:** `151_PRETRAINING_MODEL_CORPUS_AND_MEASUREMENT_DECISION_GATE_TR.md`

### Doküman 151'in zorunlu bölümleri

1. Yönetici özeti.
2. Doğrulanmış proje state'i.
3. Kaynak-model kısa listesi ve nedenleri.
4. Seçilmeyen modeller ve nedenleri.
5. Türkçe corpus kısa listesi.
6. Kumru/vngrs sayı uyuşmazlığı sonucu veya unresolved kaydı.
7. Literature-backed adaptation recipe seçenekleri.
8. Base vs instruction kararı.
9. Full CPT vs LoRA/adapters kararı veya açık kalan deney faktörü.
10. Tokenizer extension kararı.
11. English replay kararı.
12. Turkish capability package.
13. M1 bounded-screen için gerekli inputlar.
14. Factsiz dose pilotu için gerekli inputlar.
15. Risk register.
16. Tamamlanan, açık ve bloke işlerin tablosu.
17. Önerilen sonraki tek hareket.

### İzinli final verdictler

- `ready_to_freeze_bounded_m1_screen_contract`
- `ready_to_freeze_fact_free_turkish_dose_contract_using_existing_qwen`
- `blocked_by_model_provenance`
- `blocked_by_corpus_evidence`
- `blocked_by_measurement_design`

Doküman 151 `ready_to_train` veya eşdeğer bir verdict kullanmamalıdır. Execution contract ayrı
belgedir ve kullanıcı onayı gerektirir.

## 12. Bu handoff kapsamında oluşturulmaması gereken şeyler

- Yeni M1 training config'i.
- Yeni M2-A/M2-B materialized corpus.
- Slurm launcher veya job submission.
- HU üzerinde model/dataset download.
- 25.000-fact run.
- Yeni factual threshold.
- Sonuç görerek seçilmiş checkpoint kuralı.
- Eski Doküman 131'i yeniden etkinleştiren ifade.
- Qwen/SmolLM frozen artifactlerinde değişiklik veya cleanup.
- Eski dokümanları yeniden yazarak başarısızlıkları kaldırma.

## 13. Daha sonra, yalnız açık onayla hazırlanacak belgeler

Doküman 151 tamamlanıp kullanıcı karar verdikten sonra muhtemel sıra:

1. **Doküman 152 — Bounded M1 Screen Frozen Execution Contract**
   - adaylar, exact revisions, 500 fact population, en fazla iki recipe, seeds, checkpoints, gates,
     compute/storage tahmini.
2. **Doküman 153 — Fact-Free Turkish Dose Pilot Frozen Contract**
   - seçili M1, corpus revision, dose ladder, PPL/capability/retention gates.
3. **Doküman 154 — M2-A/M2-B Main Family Frozen Contract**
   - yalnız dose pilotu manipulation check'i geçerse.

Bu numaralar rezervasyon niyetidir; belgeler henüz varmış veya yetkiliymiş gibi gösterilmemelidir.

## 14. Paralelleştirilebilecek ve sıralı işler

Zorunlu bağımlılık:

```text
WP0 project-state verification
├── WP1 model provenance
├── WP2 literature matrix
├── WP3 corpus audit plan
└── WP4 capability design
          ↓
      WP5 decision gate
```

WP1–WP4, WP0 tamamlandıktan sonra içerik olarak paralel yürütülebilir. Tek ajan çalışıyorsa önerilen
sıra `WP1 → WP2 → WP3 → WP4 → WP5`tir. Birden çok ajan kullanılırsa her ajan ayrı çıktı belgesine
sahip olmalı; ortak Doküman 151 yalnız bütün kaynak belgeler tamamlandıktan sonra yazılmalıdır.

## 15. Günlük çalışma günlüğü biçimi

Her çalışma oturumunda kısa bir ledger tutulmalıdır:

| Alan | İçerik |
|---|---|
| Tarih/saat | Europe/Berlin |
| İş paketi | WP0–WP5 |
| Okunan kaynaklar | belge no/dosya veya URL |
| Doğrulanan iddialar | kısa liste |
| Çelişkiler | kaynak A vs kaynak B |
| Üretilen dosya | path |
| Açık sorular | sonraki adım |
| Yetki sınırı | training/HU yapılmadı teyidi |

Tam job ID günlüğü bu araştırma belgelerine eklenmez; çünkü bu handoff training veya HU işi
yetkilendirmez.

## 16. Kalite kontrol listesi

Her çıktı teslim edilmeden önce:

- [ ] Belge numarası ve dosya adı doğru.
- [ ] Tarih ve status alanı var.
- [ ] Kaynaklar birincil ve tıklanabilir.
- [ ] Kaynak iddiası ile inference ayrılmış.
- [ ] `English-only`, `Turkish not listed`, `unknown` ifadeleri karıştırılmamış.
- [ ] Base ve instruct varyantlar ayrılmış.
- [ ] CPT ve SFT corpusları ayrılmış.
- [ ] Token sayıları tokenizer/epoch bağlamıyla yazılmış.
- [ ] Eski Qwen pilotu geçersiz veya teknik failure diye yanlış sunulmamış.
- [ ] M2-A/M2-B sibling-arm yapısı doğru.
- [ ] M2-B'ye ekstra token eklenmemesi ilkesi korunmuş.
- [ ] TR→EN primary, TR→TR secondary, EN→TR exploratory olarak ayrılmış.
- [ ] Yeni training veya HU erişimi yapılmamış.
- [ ] Eski dosyalar geriye dönük değiştirilmemiş.
- [ ] Doküman 00 ve gerekirse AGENTS.md yalnız yeni çıktı gerçekten oluştuğunda güncellenmiş.

## 17. LUNA-Worker 2'nin kullanıcıya final raporu

Final cevap uzun tarih özeti olmamalıdır. Şunları vermelidir:

1. Oluşturulan Doküman 147–151 linkleri.
2. Model shortlist verdict'i.
3. Corpus shortlist/verdict'i.
4. Capability manipulation-check özeti.
5. Çözülemeyen en önemli üç belirsizlik.
6. Önerilen **tek** sonraki hareket.
7. `No HU access, no training, no large download, no artifact deletion` teyidi.

## 18. LUNA-Worker 2 için doğrudan kopyalanabilir başlangıç prompt'u

```text
Sen LUNA-Worker 2 — Model, Corpus & Literature Audit ajanısın.

Workspace:
/Users/umutyesildal/Desktop/UniDE/Semester6/Thesis/implementation

İlk olarak workspace kökündeki AGENTS.md'yi eksiksiz oku. Ardından Doküman 146'yı tamamen oku ve
orada verilen zorunlu okuma sırasını uygula. Özellikle Doküman 100, Expose.pdf, Dokümanlar 106,
110, 127, 136, 138, 140a, 142, 143, 144 ve 145 okunmadan sonuç üretme.

Görevin yeni training başlatmak değil; bir sonraki deneyden önce model provenance, M1 geçmiş
kanıtı, Türkçe corpus provenance/kalitesi, cross-lingual language-adaptation literatürü ve Türkçe
capability manipulation-check tasarımını doğrulamaktır.

Doküman 146'daki WP0–WP5 iş paketlerini sırayla tamamla ve şu append-only belgeleri üret:

147_LUNA_MODEL_PROVENANCE_AND_M1_SHORTLIST_AUDIT_TR.md
148_CROSS_LINGUAL_LANGUAGE_ADAPTATION_LITERATURE_MATRIX_TR.md
149_TURKISH_CORPUS_PROVENANCE_QUALITY_AND_CONTAMINATION_AUDIT_PLAN_TR.md
150_TURKISH_CAPABILITY_AND_ADAPTATION_MANIPULATION_CHECK_PLAN_TR.md
151_PRETRAINING_MODEL_CORPUS_AND_MEASUREMENT_DECISION_GATE_TR.md

Birincil kaynakları kullan; her dış iddiaya URL, erişim tarihi ve kanıt düzeyi ekle. Kaynak
iddiası ile kendi inference'ını ayır. Kumru'nun 500GB/300B iddiası ile vngrs-web-corpus'un
84.9GB/25.33B bilgisini kaynak olmadan uzlaştırma. Base ile instruct, CPT ile SFT verilerini
karıştırma.

Tamamlanan Qwen M2-clean/M3-fact ailesini geçersiz sayma. Onu, aynı M1'den çıkan kardeş kollara
sahip fakat yaklaşık 1M-token Wikipedia adaptasyonuyla sınırlı negatif/inconclusive pilot olarak
koru. Yeni ana tasarımı M2-A genel Türkçe corpus ve M2-B aynı corpus + kontrollü factual
re-exposure olarak ifade et. M2-B'ye ekstra total token verme.

HU'ya bağlanma. Slurm işi başlatma. Model veya büyük corpus indirme. Training/evaluation config'i
oluşturma. Artifact silme veya taşıma. 25.000-fact planını açma. Doküman 151 sonunda yalnız
Doküman 146'da izin verilen verdictlerden birini kullan ve kullanıcıdan sonraki adım için onay bekle.

Çalışırken eski belgeleri yeniden yazma; yeni bulguları yeni numbered docs olarak ekle. Yeni belge
gerçekten oluştuğunda Doküman 00 indeksini güncelle. Final cevapta oluşturduğun dosyaları, ana
verdictleri, açık belirsizlikleri, önerilen tek sonraki hareketi ve hiçbir training/HU/large-download
yapmadığını bildir.
```

## 19. İsim değerlendirmesi

`LUNA-Worker 2` kısa, hatırlanabilir ve önceki ajan zinciriyle uyumludur. Tek başına isim rolü
anlatmadığı için görev başlığında şu tam biçim önerilir:

> **LUNA-Worker 2 — Model, Corpus & Literature Audit**

Bu ad, ajanın deney çalıştıran bir executor değil, training öncesi bilimsel denetim ve karar paketi
hazırlayan worker olduğunu açık tutar.
