# 152a — Üç-Model 500-Fact M1 Screen: Model-Native Repair ve Execution Planı

**Tarih:** 2026-08-11 (Europe/Berlin)  
**Durum:** `READY_FOR_EXACT_USER_AUTHORIZATION — UNEXECUTED`  
**Kapsam:** `OLMo-2-0425-1B`, `Pythia-1.4B` ve `Falcon-RW-1B` üzerinde aynı donmuş
100-subject/500-fact İngilizce M1 acquisition screen'i ve base/endpoint evaluation  
**Supersession sınırı:** Bu belge Document 152'nin tarihsel `NATIVE ASSET GATE` sonucunu silmez.
Yalnız sonraki, yeni-root execution için düzeltilmiş model-native kontratı tanımlar.

## 1. Amaç ve tezdeki rol

Bu screen'in amacı üç farklı küçük, açık base model ailesinin aynı 500 sentetik İngilizce fact'i
aynı önceden dondurulmuş training recipe'si altında edinme ve prompt değişimlerine karşı geri
çağırma davranışını ölçmektir. Her aday ayrı bir bilimsel screening sonucu üretir. Negatif sonuç,
gate failure veya model-spesifik compatibility block kronolojik olarak korunur; sonuç görüldükten
sonra model, revision, learning rate, epoch, endpoint veya prompt paketi değiştirilmez.

Bu çalışma:

- model seçimi için tek başına final kanıt değildir;
- pozitif bir aday için seed-43 replication yetkisi vermez;
- Türkçe corpus, M2-A/M2-B, dose ladder veya 2.500/25.000-fact ölçeğini açmaz;
- mevcut `blocked_by_measurement_design` global kararını değiştirmez;
- üç yeni, karşılaştırılabilir M1 screening sonucu üretmeyi hedefler.

## 2. Frozen aday paneli

| Index | Label | Model | Exact Hugging Face revision | Rol |
|---:|---|---|---|---|
| 0 | `olmo` | `allenai/OLMo-2-0425-1B` | `a1847dff35000b4271fa70afc5db10fd29fedbdf` | açık provenance odaklı English-dominant aday |
| 1 | `pythia` | `EleutherAI/pythia-1.4b` | `0da31d8fb309463877ed8c40e54a8f911dced3ec` | kontrollü/open training-suite adayı |
| 2 | `falcon` | `tiiuae/falcon-rw-1b` | `e4b9872bb803165eb22f0a867d4e6a64d34fce19` | RefinedWeb tabanlı English comparator |

Model kimlikleri veya revision'lar execution sırasında değiştirilemez. Bir revision erişilemezse
o aday `NOT RUN — ACCESS/REVISION GATE` olur; başka revision'a sessiz geçiş yapılmaz. “English-only”
veya “English-dominant” ifadeleri, sıfır Türkçe exposure kanıtı olarak yorumlanmaz.

Literatür dayanakları:

- OLMo: Groeneveld et al., *OLMo: Accelerating the Science of Language Models*, 2024.
- Pythia: Biderman et al., *Pythia: A Suite for Analyzing Large Language Models Across Training
  and Scaling*, ICML 2023.
- Falcon/RefinedWeb: Penedo et al., *The RefinedWeb Dataset for Falcon LLM*, 2023.
- Factual acquisition yorumu: Zucchet et al., *How do language models learn facts? Dynamics,
  curricula and hallucinations*, 2025.

## 3. Frozen veri ve training recipe

Canonical dataset read-only olarak yeniden kullanılır:

```text
/vol/tmp2/yesildau/m1_canonical_form_diversity_v1/datasets
```

Zorunlu identity:

| Artifact | Beklenen |
|---|---|
| `dataset_manifest.json` | SHA-256 `c11f779229af14b196f2063ecdeb956e34444a30bf4086c331168f5cb11d6a26` |
| `train.jsonl` | 3.500 row; SHA-256 `8eb65505b22f5c7f8e67f2d1877efad7503489dd8bdf2608cad08791f7d05a67` |
| `validation.jsonl` | 500 row; SHA-256 `495cdcda9049b372159ef167f3da866e4cb82caf1977796efbb3baa9e07973e7` |
| Population | 100 subject / 500 semantic fact / 5 Relation V2 relation |
| Training representations | fact başına donmuş 7 English representation |

Training koşulları:

| Alan | Frozen değer |
|---|---:|
| Seed / data seed | `42 / 42` |
| Epoch | `36` |
| Effective factual batch | `500 rows` |
| Optimizer update | tam `252` |
| Learning rate | `5e-5` |
| Scheduler | `constant_with_warmup` |
| Warmup ratio | `0.02` |
| Weight decay | `0.0` |
| Loss | `answer_only` |
| EOS supervision | `false` |
| Block size | `128` |
| Max gradient norm | `1.0` |
| Primary endpoint | yalnız update `252` |

Candidate-native tokenization nedeniyle gerçek input ve supervised-token sayıları farklı olabilir.
Bilimsel eşleme 3.500 aynı row, 36 epoch, 500-row effective batch ve 252 update üzerinden yapılır.
Her aday için gerçek input token, supervised token, fertility, maksimum sequence length ve truncation
sayısı ayrıca raporlanır. Hiçbir row sessizce truncate edilemez.

### 3.1 Endpoint-only checkpoint düzeltmesi

Document 152'deki 11 checkpoint/candidate ve yaklaşık 709 GiB tahmini bu endpoint-only screen için
gereksizdir. Yeni koşu:

- yalnız update-252 resumable checkpoint ve doğrulanmış model-only final endpoint üretir;
- ara bilimsel checkpoint sweep'i yapmaz;
- `checkpoint_fractions: [1.0]` kullanır;
- checkpoint yazımı bilimsel recipe'yi veya endpoint seçimini değiştirmez;
- training öncesi acquisition manifestlerinden hesaplanan gerçek model/optimizer/cache boyutlarıyla
  combined reserve yeniden hesaplanır;
- ilk planlama rezervi en fazla 180 GiB'dir; live `df`/inode ve exact hesap bunu değiştirmeden
  training açılamaz.

## 4. Model-native tokenizer ve loader gate'i

Document 152'nin bütün modellerden aynı filename set'ini istemesi supersede edilir. `tokenizer.model`,
`tokenizer.json`, `vocab.json` veya `merges.txt` tek başına evrensel zorunlu dosya değildir.

Her aday ayrı olarak şu gate'i geçmelidir:

1. Resolved repository SHA, frozen requested revision ile birebir eşleşir.
2. Snapshot içindeki bütün dosyalar path+byte+SHA-256 manifestine bağlanır.
3. `AutoConfig`, `AutoTokenizer` ve `AutoModelForCausalLM` exact local snapshot'tan offline yüklenir.
4. Yüklenen tokenizer class, fast/slow türü, vocab size, special-token IDs ve model max length
   kaydedilir.
5. Answer-only offset masking için tokenizer'ın gerçek offset mapping desteği doğrulanır. Offset
   mapping yoksa aday `NOT RUN — MASKING COMPATIBILITY GATE` olur; farklı loss'a geçilmez.
6. Tokenizer scratch içindeki izole round-trip klasörüne `save_pretrained` ile yazılır, yeniden
   offline yüklenir ve sabit probe setinde şu değerler birebir eşleşir:
   - token IDs;
   - attention mask;
   - offsets;
   - decoded text;
   - EOS/PAD/UNK/BOS IDs;
   - vocabulary length.
7. Dataset'in bütün 4.000 hard prompt'u ve 3.500 training row'u tokenize edilir; sequence length
   `<=128`, supervised-token count `>0`, truncation `0` olmalıdır.
8. Token ID üst sınırı model input-embedding kapasitesini aşamaz.
9. Bir gerçek forward/backward optimizer-step smoke'u finite loss, finite gradient, non-zero
   gradients ve checkpoint save/reload ile geçer.
10. Model-specific pinned remote code ancak registry'de önceden açıkça `allowed=true` ise ve exact
    snapshot hash manifestine dahilse kullanılabilir. Koşu sırasında dinamik kod/fallback indirilemez.

Bir adayın bu gate'i geçememesi diğer iki adayın acquisition, training veya evaluation zincirini
durdurmaz.

## 5. Candidate-independent execution DAG

Eski all-or-none array dependency kaldırılır. Her adayın kendi zinciri vardır:

```text
family read-only preflight
├── olmo:   acquire → audit/tokenizer → smoke → train → base+endpoint eval
├── pythia: acquire → audit/tokenizer → smoke → train → base+endpoint eval
└── falcon: acquire → audit/tokenizer → smoke → train → base+endpoint eval
                                      ↓
                         afterany family assembly/gate
```

Kurallar:

- ortak family preflight storage/path/inode/queue/dataset identity için bir kez çalışır;
- üç zincir ayrı Slurm job ID ve ayrı dependency chain kullanır;
- bir adayın `FAILED`, `BLOCKED` veya `NOT RUN` olması diğer adaylara dependency oluşturmaz;
- family assembler, üç zincirin terminal durumunu `afterany` ile toplar;
- başarısız task yalnız teknik sebep açık ve recipe değişmeden düzeltilebiliyorsa, ayrı kullanıcı
  yetkisiyle yalnız o aday için yeni-root retry alabilir;
- duplicate submission ve aynı candidate namespace'inde eşzamanlı ikinci job fail-closed olur.

## 6. Fresh root ve prior-root koruması

Yeni root:

```text
/vol/tmp2/yesildau/m1_provenance_screen_v3
```

Şu tarihsel root'lar immutable/read-only kalır:

```text
/vol/tmp2/yesildau/m1_provenance_screen_v1
/vol/tmp2/yesildau/m1_provenance_screen_retry_v1
/vol/tmp2/yesildau/m1_provenance_screen_retry_v2
```

Yeni root altındaki her candidate için ayrı `models/`, `training/`, `evaluations/`, `manifests/`,
`logs/`, `cache/` ve `tmp/` namespace'i bulunur. Model, cache, checkpoint, evaluation ve logların
hiçbiri HU home'a yazamaz. Preflight `readlink -f`, `df -h`, `df -i`, home-usage ve `>500 MiB`
home-file audit'ini AGENTS.md kurallarına göre kaydeder.

## 7. Evaluation matrisi

Her candidate için iki state değerlendirilir:

- `M0/base` exact pinned model;
- `M1/update252` trained endpoint.

Her state için mümkün olan aynı frozen evaluator kullanılır:

1. 500 canonical exact-prefix probe;
2. 4.000 A/B/C/D × direct/QA hard probe;
3. eight-cell robust intersection;
4. relation-level cells;
5. relation-swapped ve same-subject binding control;
6. frozen WikiText-2 PPL;
7. 30 generic prompt/completion integrity control;
8. empty output, EOS-ending, synthetic-subject intrusion ve relation-collapse diagnostics.

Primary bilimsel rapor endpoint absolute metrics'i ve `M1 − M0` delta'larını birlikte verir.
Base factual evaluation, sentetik isimlerde beklenmeyen önbilgi/collision veya evaluator floor'unu
tespit etmek için zorunludur.

## 8. Frozen gate'ler ve sonuç sınıfları

Document 152 gate'leri değişmez:

| Gate | Requirement |
|---|---:|
| Exact prefix | `>=90%` |
| Trained A/B cell | global ve her relation `>=80%` |
| Held-out C/D cell | global ve her relation `>=80%` |
| Eight-cell robust | global ve her relation `>=70%` |
| Generic PPL ratio | `M1/M0 <=1.25` |
| Integrity | leakage, empty collapse, relation collapse ve synthetic intrusion yok |

Her candidate yalnız şu sınıflardan birini alır:

- `COMPLETED_PASS`;
- `COMPLETED_FAIL_<SCIENTIFIC_GATE>`;
- `NOT_RUN_<ACCESS_OR_COMPATIBILITY_GATE>`;
- `INVALID_INFRASTRUCTURE_RUN`.

Üç adaydan biri bile tamamlanırsa sonucu raporlanır; ancak family hedefi üç terminal ve
yorumlanabilir candidate kaydıdır. Tek seed sonucu screening'dir. Final model seçimi veya güçlü
genellenebilirlik iddiası için pozitif adayın ayrı seed-43 replication'ı gerekir.

## 9. Implementation değişiklikleri

Execution authorization öncesi local code review ve test ile şu dar değişiklikler hazırlanacaktır:

1. Yeni `m1_provenance_screen_v3` registry ve fresh-root config.
2. Universal-filename validator yerine model-native offline save/reload/encode round-trip validator.
3. Per-candidate independent submitter/DAG; shared all-or-none dependency kaldırılması.
4. Endpoint-only checkpoint config ve gerçek family-size estimator.
5. Base hard-suite/exact evaluator preparation.
6. Family terminal-state assembler, gate report ve artifact inventory.
7. Candidate-specific manifestlerde revision, transformers/tokenizers versions, tokenizer class,
   actual token counts, dtype, GPU ve exact config hash'leri.
8. Tests:
   - GPT-2 BPE-style tokenizer fixture;
   - tokenizer-json-only fixture;
   - missing/invalid tokenizer negative fixture;
   - independent DAG failure isolation;
   - 252-update invariant;
   - endpoint-only checkpoint invariant;
   - base/trained evaluation registry completeness;
   - prior-root immutability ve scratch-path validation.

Yerel Mac Python ortamında PyYAML bulunmadığı için mevcut targeted pytest collection'ı
`ModuleNotFoundError: yaml` ile durmuştur. Dependency kurulmayacak veya sistem ortamı
değiştirilmeyecektir. Authoritative suite HU'daki donmuş `xfer-relearn` environment'ında, source
access/training submission öncesi çalıştırılır; collection failure scientific test PASS sayılmaz.

## 10. HU publication ve preflight sırası

Execution ancak exact kullanıcı authorization'ından sonra şu sırayla ilerler:

1. Local diff/status review; unrelated untracked kullanıcı artifact'ları korunur.
2. Dar commit; exact commit SHA kaydedilir.
3. Kullanıcı tarafından ayrıca yetkilendirilen ordinary non-force push.
4. HU'da status blob ve incoming-path overlap kontrolü.
5. Yalnız overlap sıfırsa `git pull --ff-only origin corpus-update`.
6. Mandatory family storage/path/inode/home/root-absence/dataset-hash/queue preflight.
7. Üç candidate acquisition chain'inin tek submission dalgasında açılması.
8. Acquisition manifest ve tokenizer gate review.
9. Gate-passing candidate training submission'ları.
10. Base ve endpoint evaluation.
11. Family assembly, metric/gate report, SHA-256 artifact inventory ve post-run storage audit.

Gizli `.env` hiçbir loga veya belgeye alınmaz. `ssh-client/scripts/hu_ssh_expect` yalnız
`ssh-client` working directory'sinden, incelenmiş bounded command ile kullanılabilir.

## 11. Stop conditions

Aşağıdakilerde execution durur ve kullanıcıya dönülür:

- exact revision farklı resolve olursa;
- HU dirty paths ile incoming commit yolları çakışırsa;
- yeni root önceden mevcutsa;
- output/cache/tmp/log path'lerinden biri HU home'a resolve olursa;
- home usage açıklanamaz veya 30 GiB sınırına ulaşırsa;
- combined scratch kapasitesi/inode rezervi yeterli değilse;
- dataset hash/count/Relation V2 invariant'ı değişirse;
- candidate tokenizer offset veya round-trip gate'i geçmezse;
- smoke loss/gradient/checkpoint reload finite ve tutarlı değilse;
- 252 update veya effective batch 500 korunamazsa;
- evaluator registry base+trained state'leri eksikse;
- frozen bilimsel recipe'yi değiştirmeyi gerektiren bir hata çıkarsa.

## 12. Beklenen teslimatlar

Başarılı execution sonunda:

- **Document 153:** append-only execution result; job IDs, configs, manifests, base/endpoint metrics,
  candidate failures ve storage audit;
- **Document 154:** üç-model karşılaştırmalı scientific gate ve sonraki seed/corpus kararı;
- üç update-252 model-only endpoint manifesti (yalnız tamamlanan adaylar);
- exact model/tokenizer/config/evaluation SHA-256 kayıtları;
- tek karşılaştırma tablosu ve machine-readable family gate JSON'u;
- no-cleanup state; herhangi bir cleanup veya seçilmiş model durability kopyası ayrı review ister.

## 13. Exact next authorization request

Bu belge planlama ve contract hazırlığıdır; henüz HU/SSH, push, model download, Slurm, GPU,
training veya evaluation yapmamıştır.

Bir sonraki authorization tek cümlede şu kapsamı açıkça vermelidir:

> Document 152a'nın exact SHA-256'sına bağlı local implementation/test düzeltmesini, dar ordinary
> non-force push'u, preservation-checked HU fast-forward'u, mandatory preflight'i ve
> `/vol/tmp2/yesildau/m1_provenance_screen_v3` altında üç bağımsız candidate acquisition → smoke
> → training → base/endpoint evaluation zincirinin bir kez yürütülmesini yetkilendiriyorum.

Bu authorization corpus çalışmasını, seed-43'ü, M2-A/M2-B'yi, cleanup/deletion'ı veya HU-home model
kopyasını açmaz.
