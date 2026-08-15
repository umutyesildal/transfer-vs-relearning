# 159 — Üç-Model M1 Dose/Pareto Remediation Execution Contract

**Tarih:** 2026-08-11 (Europe/Berlin)  
**Durum:** `FROZEN — UNEXECUTED — EXACT AUTHORIZATION REQUIRED`

## 1. Amaç ve bilimsel sınıflandırma

Documents 157/158'de OLMo-2-0425-1B, Falcon-RW-1B ve Pythia-1.4B aynı 500-fact endpoint
screen'inde exact acquisition'ı geçti, fakat en kötü `profession` robustness ve/veya generic
retention gate'lerini geçmedi. Bu kontrat o negatif sonuçları değiştirmez. Yeni aile
`EXPLORATORY / PRE-REGISTERED REMEDIATION`dır ve şu tek soruyu sorar:

> Aynı model, veri, seed, LR ve optimization recipe korunurken daha düşük factual dose/erken
> checkpoint, exact acquisition + prompt robustness + generic retention gate'lerini birlikte
> geçiren bir Pareto noktası üretiyor mu?

Sonuçlardan sonra eşik yükseltmek, prompt eklemek, replay/KL eklemek veya checkpoint seçmek
yasaktır. Hiçbir model geçmezse sonuç `VALID_NEGATIVE_REMEDIATION_RESULT` olur.

## 2. Değişmez girdiler

| Alan | Frozen değer |
|---|---|
| Dataset root | `/vol/tmp2/yesildau/m1_canonical_form_diversity_v1/datasets` |
| Dataset manifest SHA-256 | `c11f779229af14b196f2063ecdeb956e34444a30bf4086c331168f5cb11d6a26` |
| Train | 3,500 row; `8eb65505b22f5c7f8e67f2d1877efad7503489dd8bdf2608cad08791f7d05a67` |
| Validation | 500 row; `495cdcda9049b372159ef167f3da866e4cb82caf1977796efbb3baa9e07973e7` |
| Population | 100 subject / 500 semantic fact / 5 Relation V2 relation |
| Seed / data seed | `42 / 42` |
| LR | `5e-5` |
| Effective batch | 500 rows |
| Loss | answer-only |
| EOS supervision | false |
| Block size | 128 |
| Scheduler | constant-with-warmup; warmup ratio 0.02 |
| Weight decay | 0 |
| Maximum updates | 252 / 36 epoch |

Model identities:

| Label | Model / immutable revision | Frozen runtime identity |
|---|---|---|
| OLMo | `allenai/OLMo-2-0425-1B@a1847dff35000b4271fa70afc5db10fd29fedbdf` | completed v3 V100 FP16 runtime; same microbatch/accumulation and optimizer semantics |
| Falcon | `tiiuae/falcon-rw-1b@e4b9872bb803165eb22f0a867d4e6a64d34fce19` | completed v3 RTX3090 BF16 runtime |
| Pythia | `EleutherAI/pythia-1.4b@0da31d8fb309463877ed8c40e54a8f911dced3ec` | completed 156c RTX3090 BF16 runtime and verified official tokenizer/composite manifest |

Base weights, model/tokenizer manifests and dataset are read-only reused. No network retrieval or
model/corpus download is allowed. Historical v3 and Pythia repair roots remain immutable.

## 3. Tek training dalgası ve checkpoint grid'i

Her model tam olarak bir seed-42 training run alır. Training maksimum update 252'ye kadar sürer ve
exact checkpoint'ler şunlardır:

```text
42, 84, 126, 168, 210, 252
```

Bunlar sırasıyla 6, 12, 18, 24, 30 ve 36 epoch'tur. Implementation `save_steps: 42` ve en az altı
retained resumable checkpoint ile fail-closed çalışmalıdır. Bir run erken iyi görünürse training
durdurulmaz; bütün grid tamamlanır. Böylece model aileleri aynı dose ekseninde karşılaştırılır.

Bu wave'deki tek bilimsel değişken endpoint yerine precommitted factual dose/checkpoint'tir.
OLMo/Falcon/Pythia'nın daha önce doğrulanmış zorunlu hardware precision farkları yeni treatment
değildir; her aile kendi tamamlanmış v3 runtime'ını aynen korur.

## 4. Frozen evaluation cascade

Eski base evaluation artifact'ları SHA-256 ile doğrulanıp yeniden kullanılır; base inference
tekrarlanmaz. Her trained checkpoint için sıralama outcome-blind ve fail-closed'dur:

1. exact-prefix evaluation;
2. frozen WikiText-2 PPL ve 30-prompt generic capability/integrity evaluation;
3. yalnız `exact >=90%` **ve** `PPL ratio <=1.25` olan checkpoint'lerde 4,000-probe hard-suite,
   relation-swap ve eight-prompt robust intersection.

İlk iki kapıdan geçmeyen checkpoint'in hard-suite'ini atlamak başarı üretmez; checkpoint otomatik
FAIL olur. Bütün checkpoint'ler için cheap-stage metrikleri, skip nedeni ve artifact hash'i
raporlanır. Hard-stage'e giren her checkpoint için full per-probe CSV ve compact summary korunur.

## 5. Değişmez gate ve seçim kuralı

| Gate | Eşik |
|---|---:|
| Exact prefix | `>=90%` |
| Trained A/B cells | global ve her relation `>=80%` |
| Held-out C/D cells | global ve her relation `>=80%` |
| Eight-prompt robust intersection | global ve her relation `>=70%` |
| Generic PPL ratio | `<=1.25` |
| Integrity | no empty/relation collapse, no synthetic intrusion |

Model içi nominee, bütün gate'leri geçen **en erken update**'tir. Birden fazla model geçerse mevcut
Document 105 tie-break sırası uygulanır: global robust, minimum-relation robust, held-out C/D,
daha düşük PPL ratio, sonra maliyet. Seed-42 nominee yalnız `REMEDIATION_NOMINEE` olur; primary
promotion için ayrı frozen seed-43 replication kontratı gerekir.

PPL `1.25` sonucu görmek için yükseltilmez. Continuous PPL, completion ve degeneration metrikleri
ayrıca raporlanır; gelecekte farklı eşik tartışması bu wave'in sonucunu geriye dönük değiştiremez.

## 6. Scratch, storage ve korunacak kanıt

Fresh root:

```text
/vol/tmp2/yesildau/m1_provenance_screen_v4_dose_pareto_v1
```

Root execution öncesi absent olmalıdır. Bütün cache/tmp/log/checkpoint/evaluation çıktıları bu root
altında olmalı; HU home'a yazı yasaktır. Historical roots read-only kalır. Worst-case altı
resumable checkpoint x üç model için 600 GiB reserve ve en az 10,000 inode önceden doğrulanır.

Kullanıcının no-delete şartı nedeniyle cleanup yoktur. Altı checkpoint, optimizer/scheduler/RNG
state, model-only freeze, tokenizer/config, manifests, logs ve evaluation evidence korunur.
Execution sonrası exact bytes/inodes, file inventory ve compact SHA-256 ledger Document 160'a
yazılır.

## 7. Implementation ve preflight kapıları

Execution öncesi local implementation/tests şunları fail-closed bağlar:

- yeni registry/config/launcher'lar ve fresh root;
- exact model revision, historical manifest ve dataset hash doğrulaması;
- `save_steps=42`, exact six-checkpoint inventory ve `save_total_limit>=6`;
- model-specific known-good runtime/GPU/precision/template identity;
- OLMo için V100 `sm_70` runtime, Falcon/Pythia için RTX3090 `sm_86` ve clean/free-VRAM gate;
- `guppi6` exclusion, başka kullanıcı process'ine dokunmama ve duplicate-job rejection;
- frozen base-summary hash'leri ve evaluator/template hash'leri;
- no-home-write, resolved paths, `df -h`, `df -i`, reserve ve root-absence checks;
- cascade evaluator'ın cheap-stage FAIL'i hard-stage PASS olarak yorumlayamaması;
- exact earliest-all-gates selection ve tie-break tests.

Local changes dar ordinary non-force push ile yayınlanır. HU checkout ancak dirty-state blob ve
incoming-path intersection korunarak `git pull --ff-only` ile ilerletilebilir.

## 8. Execution sırası ve durma koşulları

1. local implementation + targeted/compatible tests;
2. narrow review, commit ve ordinary non-force push;
3. preservation-checked HU fast-forward;
4. one shared storage/path/inode/no-duplicate preflight;
5. three independent runtime/tokenization/optimizer smokes;
6. exactly one training run per model;
7. six-checkpoint frozen cascade evaluation per completed model;
8. result assembly, hash/storage audit ve Documents 160/161.

Yanlış GPU/runtime, non-finite loss/gradient, dataset/hash drift, zero supervision, unexpected root,
insufficient storage, duplicate namespace veya artifact overwrite riski yalnız ilgili modeli
fail-closed durdurur. Sibling model iptal edilmez. Hiçbir yabancı job/process iptal edilmez.

## 9. Scope dışı

- `2e-5` veya `1e-5` LR training;
- replay, KL/weight anchoring veya generic-data mixing;
- prompt augmentation/rebalancing;
- seed 43;
- Türkçe corpus, dose ladder veya M2-A/M2-B;
- threshold change;
- cleanup/deletion;
- historical artifact mutation.

Bu wave hiçbir modelde all-gates nominee üretmezse, Document 161 ancak ayrı bir LR-ladder
kontratını önerebilir. Onu otomatik çalıştıramaz.

## 10. Exact next authorization request

Document 159'un final SHA-256'sına bağlı ayrı kullanıcı yetkisi; local implementation/tests, dar
ordinary non-force push, preservation-checked HU fast-forward, frozen-reference/no-home-write
preflight, exactly one OLMo + one Falcon + one Pythia six-checkpoint training chain, frozen cascade
evaluation ve Documents 160/161 result/gate dokümantasyonunu açıkça kapsamalıdır.
