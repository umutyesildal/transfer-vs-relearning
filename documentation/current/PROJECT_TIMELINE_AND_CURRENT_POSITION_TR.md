# Proje timeline'ı ve güncel konum

**Son doğrulama:** 2026-08-20T07:59:47Z

**Bilimsel faz:** eval-v1 donduruldu; üç modelli M0 wave terminal `partial_invalid`

**Training readiness:** `ready_to_train=false`

**Seçili primary model:** yok

> Bu dosya projenin tek insan-okunur kronolojik durum özetidir. Bilimsel sözleşme veya execution
> yetkisi değildir. Kesin canlı alanlar
> [`PROJECT_STATE.yaml`](PROJECT_STATE.yaml), değişmez kurallar
> [`eval-v1`](../contracts/evaluation/eval-v1.md) ve gerçekleşen olaylar ilgili record/numbered
> belgelerindedir.

## 1. En kısa cevap: pipeline başladı mı?

**Evet, bilimsel M0 evaluation pipeline'ı 16 Ağustos 2026'da başlatıldı.** OLMo, Qwen ve SmolLM
için 24 GPU lane tek wave olarak submit edildi. 20 Ağustos'taki salt-okunur doğrulamada bütün
job'lar Slurm kuyruğundan çıkmış, 24 lane'in tamamı terminal duruma gelmiş ve family finalizer
artefaktını üretmişti.

Ancak **tam M0→M1→M2-A/M2-B pipeline henüz başlamadı.** M0 wave sonucu:

```text
24 required lane
├── 17 complete raw lane
└── 7 failed_pre_scoring / partial_invalid lane

normalization_allowed = false
cross-model scientific summary = yok
M1 training = başlamadı ve yetkili değil
```

Bu nedenle ikinci bir M0 submit yapılmadı ve M1'e otomatik geçilmedi. Mevcut wave'i yeniden
başlatmak duplicate/outcome-aware rerun olurdu. Sıradaki bilimsel karar, tam olarak eksik yedi lane
için semantiği değiştirmeyen ayrı bir recovery contract hazırlayıp hazırlamamak.

## 2. Şu an tam olarak neredeyiz?

```mermaid
flowchart LR
    A["Repository ve documentation migration"] --> B["Evaluation inventory"]
    B --> C["LM Eval qualification + parity"]
    C --> D["eval-v1 freeze"]
    D --> E["3-model M0 preflight"]
    E --> F["24-lane M0 submit"]
    F --> G["17 complete + 7 partial_invalid"]
    G --> H["Eksik 7 lane recovery kararı"]
    H --> I["Canonical normalization + M0 gate"]
    I --> J["M1 recipe + training"]
    J --> K["M2-A / M2-B sibling training"]

    style G fill:#ffd8a8,stroke:#d9480f
    style H fill:#fff3bf,stroke:#e67700
    style I fill:#e9ecef,stroke:#495057
    style J fill:#e9ecef,stroke:#495057
    style K fill:#e9ecef,stroke:#495057
```

Güncel konum **G ile H arasındadır**. M0 GPU işleri terminaldir; fakat bilimsel M0 ailesi complete
değildir. Normalization ve model karşılaştırması fail-closed tutulmuştur.

## 3. Kronolojik timeline

### Tarihsel bilimsel temel — 2026-08-03

Qwen M1→M2-clean/M3-fact pilot ailesi tamamlandı. Bu çalışma proje için gerçek ve korunmuş ilk
controlled transfer/re-exposure kanıtını üretti; fakat yeni ana deney tasarımının yerine geçmedi.
Pilotun bilimsel yorumu
[`Document 138`](../138_QWEN_M2_M3_COMPLETED_MILESTONE_AND_SCIENTIFIC_INTERPRETATION_EN.md)
içinde donduruldu.

**Çıktı:** mevcut kod, evaluator, corpus ve sonuçların çöpe atılmaması gerektiğini gösteren tarihsel
pilot; yeni deney için doğrudan primary başarı iddiası değil.

### Supervisor bilimsel realignment — 2026-08-06

Max'in geri bildirimiyle hedef “en yüksek skoru üretmek”ten yorumlanabilir karşılaştırma kurmaya
çevrildi. M2 koşulları ardışık aşamalar olmaktan çıkarılıp aynı M1 parent'ından başlayan kardeş
kollar olarak tanımlandı:

```text
M1
├── M2-A: matched fact-free Turkish adaptation
└── M2-B: matched Turkish adaptation + controlled factual re-exposure
```

**Çıktı:** `M2-B−M2-A` relearning etkisinin ana causal contrast'ı oldu. Kaynak:
[`Document 144`](../144_SUPERVISOR_FEEDBACK_AND_SCIENTIFIC_REALIGNMENT_TR.md).

### Evidence, model ve corpus audit dönemi — 2026-08-07…2026-08-10

151-serisi evidence-integrity, benchmark/model metadata, corpus inventory ve measurement-design
audit'leri yürütüldü. Birçok operasyonel ve provenance boşluğu fail-closed biçimde kaydedildi.
vngrs conditional candidate kaldı; `trwiki-20260601` cross-domain control rolünde tutuldu;
CulturaX access-blocked kaldı.

**Çıktı:** corpus seçimi ve materialization'ın chat varsayımıyla yapılamayacağı, exact contract
gerektirdiği netleşti.

### Üç modelli 500-fact M1 ekranı — 2026-08-11

OLMo-2-0425-1B, Falcon-RW-1B ve Pythia-1.4B için üç geçerli bilimsel negatif sonuç kapatıldı.
Üç model de exact acquisition'da çok güçlüydü; fakat robust held-out form ve/veya generic
retention gate'lerini geçmedi.

| Model | Exact trained | Worst robust cell | PPL ratio | Gate |
|---|---:|---:|---:|---|
| OLMo | 100% | profession 59% | 1.510× | FAIL |
| Falcon | 100% | profession 37% | 10.952× | FAIL |
| Pythia | 100% | profession 65% | 16.149× | FAIL |

**Çıktı:** “küçük modeller fact öğrenemiyor” sonucu değil; dondurulmuş recipe exact storage
sağlarken robustness/retention dengesini geçemedi. Otomatik primary model seçilmedi. Kaynak:
[`Document 158`](../158_PYTHIA_REPAIR_POST_EXECUTION_AND_THREE_MODEL_GATE_TR.md).

### Dose/Pareto trajectory denemesi — 2026-08-12…2026-08-13

Acquisition ile retention'ın epoch/checkpoint boyunca birlikte izlenmesi için OLMo/Falcon/Pythia
dose family çalışması yapıldı. OLMo ve Pythia cheap checkpoint gate'leri tamamlandı; Falcon'ın
126/210/252 evaluation satırları GPU temizliği sorunları nedeniyle eksik kaldı.

```text
required cheap rows = 18
available rows      = 15
missing             = Falcon {126, 210, 252}
selected model      = none
```

Son recovery wave'i dört A6000'ün foreign VLLM süreçleriyle dolu olduğunu audit ederek doğru
biçimde `NOT RUN` kapandı. Kaynaklar:
[`Document 161`](../161_M1_DOSE_PARETO_POST_EXECUTION_GATE_TR.md) ve
[`Document 176`](../176_M1_DOSE_PARETO_POST_FALCON_AUDIT_PERSISTENT_RECOVERY_GATE_TR.md).

### Evaluation-first yön — 2026-08-14

Max'in ikinci ana geri bildirimiyle öncelik açık biçimde şu sıraya taşındı:

1. PPL/BPB hesabını açıklanabilir hale getirmek;
2. LM Evaluation Harness tabanlı multi-metric evaluation sistemini kurmak;
3. fact access ve retention'ı baştan sona, her epoch izlemek;
4. ana zamanı M2-A/M2-B karşılaştırmasına ayırmak.

**Çıktı:** endpoint-only test yaklaşımı bırakıldı; dense/full cadence ve trajectory tabloları zorunlu
hale geldi. Kaynak: [`Document 177`](../177_SUPERVISOR_FEEDBACK_EVALUATION_FIRST_OLMO_AND_M2_PRIORITY_REALIGNMENT_TR.md).

### End-to-end deney tasarımı — 2026-08-14…2026-08-15

M0→M1→M2-A/M2-B planı tek bir bilimsel çerçevede birleştirildi. Acquisition, transfer, relearning
ve retention estimand'ları ayrıldı; missingness, uncertainty, parent comparison ve checkpoint
kuralları tanımlandı.

**Çıktı:** 15-stage single-model lifecycle ve üç modelli 27-node cohort planı. Kaynak:
[`Document 178`](../178_END_TO_END_EXPERIMENTAL_PLAN_AND_EVALUATION_PROTOCOL_EN.md).

### Repository ve documentation migration — 2026-08-15…2026-08-16

Kod, synthetic-data tooling, papers, paper source, scripts, Slurm launchers, study notes,
presentations ve kronolojik bilimsel kayıtlar tek monorepo altında kayıpsız birleştirildi.

- 35,598 source regular file ve 13 symlink preservation doğrulandı;
- synthetic Git history içindeki sekiz büyük generated blob private bundle yedeği alındıktan sonra
  published history'den çıkarıldı;
- remote main'de 10 MiB ve üzeri reachable blob sayısı sıfırlandı;
- 129 script ve 135 Slurm file rolüne göre gruplandı;
- root `AGENTS.md` küçültüldü, current/contracts/records/evaluation katmanları kuruldu;
- Luna task packet'ları küçük context ile çalışacak şekilde oluşturuldu.

**Çıktı:** mevcut uygulama korunarak tek canonical repository ve daha küçük ajan context'i.
Kaynaklar: [`migration record`](../migration/REPOSITORY_MIGRATION_V1.md) ve
[`entrypoint layout`](../migration/ENTRYPOINT_LAYOUT_V2.md).

### OLMo qualification ve parity — 2026-08-16

Birden fazla fail-closed qualification denemesi runtime/controller/task sorunlarını ortaya çıkardı;
hiçbiri sessizce başarılı sayılmadı. XNLI eval-v1'den tamamen çıkarıldı. V8 + single-lane recovery
7/7 test-only qualification bundle üretti. WikiText ve TurBLiMP parity ayrıca doğrulandı.

**Çıktı:** Harness v0.4.12 semantiği, official WikiText PPL/BPB ve 16-subtask TurBLiMP macro parity
PASS. Kaynak: [`Document 179`](../179_M0_OLMO_EVAL_V1_PARITY_EXECUTION_RESULT_AND_FREEZE_GATE_TR.md).

### Eval-v1 freeze — 2026-08-16

Aynı evaluation sistemi M0, M1, M2-A ve M2-B için donduruldu. Semantic değişiklik artık eval-v2
gerektiriyor.

Frozen bileşenler:

- LM Eval Harness v0.4.12 exact commit/environment;
- WikiText, Pile-10k, BLiMP, HellaSwag, WinoGender ve TurBLiMP;
- trwiki cross-domain BPB control;
- 12,000-row full ve 1,500-row cheap factual registry;
- top-1, robust intersection, relation swap ve paired bootstrap;
- BPB/ΔBPB/PPL-ratio retention;
- dense/full checkpoint cadence;
- numeric gates ve missing-result semantics.

**Çıktı:** evaluation metodunun sonuç görüldükten sonra değiştirilemeyeceği ölçüm sınırı. Kaynak:
[`Document 180`](../180_EVAL_V1_SCIENTIFIC_INPUT_AND_PROTOCOL_FREEZE_TR.md).

### Üç modelli M0 preflight ve authorization — 2026-08-16

Exact OLMo, Qwen2.5-1.5B ve SmolLM2-1.7B revision'ları sekiz lane'e bağlandı. HU read-only identity
preflight geçti; 30 GiB HU-home gate doğrulandı.

```text
HU home measured = 14,545,990,549 bytes
hard limit       = 32,212,254,720 bytes
headroom         = 17,666,264,171 bytes
```

Contract SHA-256 `013f6f638176cbfd15fbe65c7d07a9dbb8d0029879e217f65e4e69bbeef765d9`
ve pre-authorization manifest SHA-256
`264525095a3f67b5899771069ad227a41ed431de14fd98c38168690787d2bf5d` için yalnız bir wave
yetkilendirildi.

**Çıktı:** ikinci wave/retry/M1/M2 yetkisi vermeyen, tek kullanımlık scientific M0 authorization.

### 24-lane bilimsel M0 submission — 2026-08-16

Üç CPU/data preflight ve 24 GPU lane submit edildi:

| Model | Preflight | GPU lane'ler | Finalizer |
|---|---:|---|---:|
| OLMo | `461860` | `461861`–`461868` | `461869` |
| Qwen | `461874` | `461875`–`461882` | `461883` |
| SmolLM | `461888` | `461889`–`461896` | `461897` |

Family finalizer `461898` idi. CPU/data preflight'ların tamamı 8/8 task resolution ve dondurulmuş
offline cache kimliğiyle geçti.

**Çıktı:** pipeline gerçekten başladı; submit'ten sonra controller/ajan beklemeden çıktı.

### M0 terminal raw-bundle durumu — 2026-08-16 22:23 Europe/Berlin

Son factual lane `461895`, 2026-08-16T20:22:58Z'de tamamlandı. Family raw bundle
2026-08-16 22:23:14 Europe/Berlin'de yazıldı.

| Model | Complete | Partial invalid | Model bundle |
|---|---:|---:|---|
| OLMo | 5/8 | 3/8 | `partial_invalid` |
| Qwen | 5/8 | 3/8 | `partial_invalid` |
| SmolLM | 7/8 | 1/8 | `partial_invalid` |
| **Aile** | **17/24** | **7/24** | `partial_invalid_no_cross_model_summary` |

Tamamlanan önemli son lane'ler:

- OLMo factual access `461867`: complete;
- Qwen factual access `461881`: complete;
- SmolLM factual access `461895`: complete;
- SmolLM generation integrity `461896`: complete.

Eksik yedi lane:

| Job | Model | Lane | Neden |
|---:|---|---|---|
| `461864` | OLMo | English capability | foreign-process RTX6000 OOM |
| `461865` | OLMo | TurBLiMP | foreign-process RTX6000 OOM |
| `461866` | OLMo | trwiki BPB | foreign-process RTX6000 OOM |
| `461876` | Qwen | Pile-10k | V100 attention allocation OOM |
| `461879` | Qwen | TurBLiMP | foreign-process RTX6000 OOM |
| `461880` | Qwen | trwiki BPB | foreign-process RTX6000 OOM |
| `461892` | SmolLM | English capability | foreign-process RTX6000 OOM |

Bu yedi satır `0` skor değildir. Geçerli final metrikleri yoktur. Raw family finalizer bilinçli
olarak cross-model PASS/FAIL hesaplamadı ve `normalization_allowed=false` yazdı.

Terminal family artefaktı:

```text
/vol/tmp2/yesildau/eval_v1_m0_scientific_three_model_v1/three_model_m0_raw_bundle.json
SHA-256: 75fcd7cf1e388eb5a4e883264c6aa14db83797b2e7832a4bbc8e40bb38865db1
```

Family JSON içindeki `scientific_work_started=false` alanı lane gerçeğini temsil etmez; partial
model bundle'larında expected evaluation-manifest referansları açılmadığı için raw family
finalizer'ın fail-closed sınıflandırmasıdır. 24 `lane_result.json`, Slurm job kimlikleri ve 17 raw
artefakt seti bilimsel GPU işinin gerçekten başladığını kanıtlar. Bu alan model sonucu olarak
yorumlanmamalıdır.

### Salt-okunur terminal doğrulama — 2026-08-20

Tüm 31 ilgili Slurm/control job'u aktif kuyruktan çıkmıştı. 24/24 lane result dosyası, üç
`bundle_status.json`, üç `scientific_bundle_result.json`, üç final inventory ve family raw bundle
mevcuttu. `sacct`, HU Munge/SlurmDBD authentication hatası nedeniyle accounting geçmişi veremedi;
bu missing accounting metadata'sıdır, lane çalışmasının başarısızlığı değildir.

**Çıktı:** yeni submit gerekmediği kesinleşti. Wave terminal fakat incomplete'dir.

## 4. Pipeline stage durumu

| Stage | Durum | Açıklama |
|---|---|---|
| Repository/documentation migration | COMPLETE | Canonical monorepo ve küçük context control plane hazır |
| eval-v1 design | COMPLETE/FROZEN | Semantic değişiklik eval-v2 gerektirir |
| M0 qualification/parity | COMPLETE | Test-only qualification PASS |
| Three-model M0 submission | COMPLETE | Tek authorization tüketildi |
| Three-model M0 raw execution | TERMINAL/PARTIAL | 17/24 complete, 7/24 partial invalid |
| M0 recovery | NOT AUTHORIZED | Eksik yedi lane için ayrı contract gerekli |
| M0 canonical normalization | BLOCKED | Required raw bundle complete değil |
| Cross-model M0 scientific comparison | BLOCKED | Normalize complete table yok |
| M1 recipe/corpus freeze | NOT FROZEN | Model-specific exact recipe yok |
| M1 training | NOT STARTED/NOT AUTHORIZED | M0 ve training contract kapıları açık değil |
| M1 evaluation/trajectory | PLANNED ONLY | Dense/full evaluator planı var |
| M2 corpus contract | NOT FROZEN | Primary in-domain Türkçe binding yok |
| M2-A/M2-B training | NOT STARTED/NOT AUTHORIZED | Sibling matched-budget recipe yok |
| Paired transfer/relearning analysis | PLANNED ONLY | M2 result olmadan açılamaz |
| Presentation bundle | PLANNED ONLY | Canonical long tables bekleniyor |

## 5. Sıradaki doğru sıra

### Adım 1 — Eksik yedi M0 lane için recovery contract

Recovery yalnızca şu yedi lane'i hedeflemeli; tamamlanmış 17 lane'i yeniden çalıştırmamalı.

Gerekli tasarım sınırları:

- aynı eval-v1 task/prompt/metric/dataset/model revision;
- mevcut raw root'lar immutable/read-only;
- fresh recovery namespace;
- temiz GPU/free-VRAM preflight;
- OLMo/Qwen/SmolLM için duplicate lane yasağı;
- Qwen Pile OOM için scientific semantiği değiştirmeyen memory-safe runtime decomposition;
- exact source/recovery hash merge manifesti;
- tek separately authorized recovery wave;
- missing veya yeni hata yine `0` sayılmadan fail closed.

Bu adım 20 Ağustos'ta yerel olarak hazırlandı ve donduruldu; henüz çalıştırılmadı:

- contract:
  [`m0-three-model-seven-lane-recovery-v1.md`](../contracts/evaluation/m0-three-model-seven-lane-recovery-v1.md);
- contract SHA-256:
  `1ee7c8d9d1da092cd1e4a64dbffa4594e041ebf2b4d56eb62f345a6aaa8c25c4`;
- config SHA-256:
  `4a603719dd43a65dd9b36a36786407993afe84cf8d1d48f6245656d235c6bfeb`;
- exact DAG: yedi GPU lane + üç model finalizer + bir family finalizer;
- exact SHA-bound kullanıcı yetkisi 20 Ağustos'ta verildi;
- authorization record:
  [`m0-three-model-seven-lane-recovery-v1-authorization-2026-08-20.md`](../contracts/evaluation/m0-three-model-seven-lane-recovery-v1-authorization-2026-08-20.md);
- pre-authorization config SHA-256 `4a603719...` korunarak execution overlay açıldı;
- execution durumu: HU fast-forward ve fail-closed preflight sonrası tek submission bekliyor.

### Adım 2 — Complete raw bundle ve canonical normalization

Yedi recovery lane geçerli biçimde tamamlanırsa 17 source + 7 recovery artefaktı hash doğrulamalı
bir composite M0 bundle'a bağlanır. Ardından eval-v1 normalizer:

- checkpoint registry;
- metric observations;
- factual probe results;
- model/family gate tabloları;
- uncertainty ve diagnostic tabloları

üretir. Ancak o noktada M0 bilimsel model karşılaştırması yapılabilir.

### Adım 3 — M1 training contract

M0 sonucu görüldükten sonra outcome-aware recipe aramak yerine önceden yazılı seçim kuralıyla exact
M1 model/data/LR/batch/sequence/checkpoint/seed contract'ı dondurulur. Bu contract ayrı kullanıcı
yetkisi olmadan training başlatmaz.

### Adım 4 — M1 trajectory

M1 parent ve her epoch snapshot'ında fact access + Wiki/Pile BPB birlikte ölçülür. Entry/midpoint/
endpoint'te full factual/capability/generation paneli uygulanır. Earliest precommitted all-gates-pass
checkpoint seçilir.

### Adım 5 — M2-A/M2-B siblings

Aynı exact M1 checkpoint'ından, aynı token/sequence/update bütçesiyle iki kol açılır. Ana kontrastlar:

```text
transfer   = M2-A − M1
relearning = M2-B − M2-A
retention  = child − exact parent
```

## 6. Bugünkü execution sınırı

Şu anda yeni training başlatmak doğru adım değildir. Doğru tek execution yolu authorize edilmiştir:

> Mevcut 17 geçerli M0 lane'i immutable biçimde koruyan ve yalnızca eksik yedi lane'i tamamlayan
> frozen recovery contract'ın exact SHA-256 değerine bağlı yalnızca tek recovery DAG'ını
> çalıştırmak ve terminal durumunu beklemek.

Bu wave dışında:

- mevcut 24 lane yeniden submit edilmez;
- başarılı 17 lane tekrar skorlanmaz;
- partial lane'lere sıfır yazılmaz;
- M1/M2 training açılmaz;
- eşikler veya task seti değiştirilmez;
- HU artefaktları temizlenmez.

## 7. Hızlı kaynaklar

- Derin metric/pipeline açıklaması:
  [`EVAL_V1_AND_END_TO_END_PIPELINE_DEEP_DIVE_TR.md`](../evaluation/EVAL_V1_AND_END_TO_END_PIPELINE_DEEP_DIVE_TR.md)
- Machine current state: [`PROJECT_STATE.yaml`](PROJECT_STATE.yaml)
- Current roadmap: [`ROADMAP.md`](ROADMAP.md)
- Frozen evaluation: [`eval-v1.md`](../contracts/evaluation/eval-v1.md)
- Scientific M0 contract:
  [`m0-three-model-scientific-v1.md`](../contracts/evaluation/m0-three-model-scientific-v1.md)
- Single-wave authorization:
  [`m0-three-model-scientific-v1-authorization-2026-08-16.md`](../contracts/evaluation/m0-three-model-scientific-v1-authorization-2026-08-16.md)
- Submission record:
  [`M0_THREE_MODEL_SCIENTIFIC_SUBMISSION_2026-08-16.md`](../records/evaluation/M0_THREE_MODEL_SCIENTIFIC_SUBMISSION_2026-08-16.md)

## 8. Tek satırlık güncel hüküm

**Pipeline başlatıldı; M0 execution terminalde 17/24 geçerli ham lane ile fail-closed duruyor;
eksik yedi lane için recovery contract donduruldu ve exact SHA-bound tek wave authorize edildi;
sıradaki adım yalnız bu DAG'ın execution ve terminal doğrulamasıdır.**
