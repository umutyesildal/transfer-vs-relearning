# 159a — OLMo V100 Kuyruğundan RTX3090'a Bellek-Güvenli Relocation Kontratı

**Tarih:** 2026-08-11 (Europe/Berlin)  
**Durum:** `FROZEN — UNEXECUTED AMENDMENT — EXACT SHA-BOUND AUTHORIZATION REQUIRED`

## 1. Gerekçe ve outcome-blind sınıflandırma

Document 159 altında OLMo training job `453301`, üç `v10032gb` kartın tamamı yabancı işlerce
tahsis edildiği için `PENDING(Resources)` durumunda kalmış ve Slurm tahmini
`2026-08-13T15:08:31` olmuştur. OLMo v4 training namespace'i oluşmamıştır; optimizer update,
checkpoint veya v4 evaluation sonucu yoktur. Dolayısıyla bu düzeltme bir sonucu gördükten sonra
seçilmemiştir.

`2026-08-11T22:15:25+02:00` kaynak taraması şunları göstermiştir:

- `gruenau1`: üç V10032GB'nin üçü tahsisli;
- `gruenau9/10`: altı A10080GB'nin altısı Slurm tarafından tahsisli;
- `gruenau7/8`: RTX A6000 düğümleri `DOWN (MPS not quitting)`;
- `gruenau2`: üç RTX6000 tahsisli ve kart başına 24 GB;
- `guppi5/7`: kullanılabilir RTX3090 kapasitesi; `guppi6` yabancı-process riski nedeniyle yasak.

Bu append-only amendment yalnız OLMo'nun başlamamış runtime yerleşimini düzeltir. Falcon job
`453300`, Pythia job `453296` ve onların evaluation DAG'ları değiştirilmez.

## 2. Korunan bilimsel kontrat

Aşağıdakiler Document 159 ile byte/semantic düzeyde aynıdır:

- model/revision, tokenizer ve base manifest;
- 3,500 train / 500 validation row ve bütün dataset hash'leri;
- seed/data-seed `42/42`, LR `5e-5`, answer-only loss, EOS=false, block size 128;
- effective batch 500, 36 epoch, 252 optimizer update;
- checkpoint grid `42/84/126/168/210/252` ve altı resumable checkpoint;
- exact/PPL/generic → koşullu hard-suite cascade;
- PPL `<=1.25`, exact/robust/held-out eşikleri ve earliest-all-gates seçim kuralı;
- no-home-write, no-cleanup ve historical-root immutability.

PPL veya başarı eşiği değişmez. Yeni LR, replay, KL, prompt augmentation, seed43, corpus veya
M2/M3 açılmaz.

## 3. Tek maddi runtime değişikliği

OLMo için frozen relocation şöyledir:

| Alan | Document 159 | Document 159a |
|---|---:|---:|
| GPU | V10032GB / `sm_70` | RTX3090 / `sm_86` |
| Precision | FP16 autocast | FP16 autocast |
| Per-device microbatch | 10 | 4 |
| Gradient accumulation | 50 | 125 |
| Effective batch | 500 | 500 |
| Optimizer/update count | AdamW / 252 | AdamW / 252 |

FP16 parameter-loading davranışı değiştirilmez; mevcut OLMo template gibi explicit
`model_load_dtype` eklenmez. Microbatch/accumulation ayrıştırması floating-point toplama sırasını
değiştirebilir ve Document 160'ta limitation olarak raporlanır; fakat treatment dose, örnek sırası,
global effective batch ve optimizer-update ekseni korunur.

RTX3090 runtime fail-closed olarak exact Python, Torch `2.6.0+cu124`, GPU adı, compute capability
`8.6`, compiled `sm_86`, FP16 finite probe ve en az `20 GiB` pre-allocation free VRAM ister.
`guppi6` hard-excluded'dur. Başka kullanıcının process/job'ına dokunulmaz.

## 4. Önceden dondurulmuş bellek fallback'i

Birincil `4 x 125` smoke CUDA OOM ile **training namespace/optimizer training başlamadan önce**
fail ederse tek izinli fallback `2 x 250`'dir. Effective batch yine 500 ve update sayısı yine
252'dir. Bu fallback yalnız smoke bellek uyumluluğudur; loss/metric sonucu görüldükten sonra
seçilemez. `4 x 125` smoke geçerse fallback yasaktır.

Training başladıktan sonra OOM veya non-finite durumunda otomatik ikinci bilimsel run yoktur;
model fail-closed olur ve Document 160'a yazılır.

## 5. Evaluation relocation

OLMo'nun altı checkpoint evaluation array'i RTX3090'da çalışır. Scoring, prompt, model state ve
gate aynıdır. Yalnız outcome-invariant compute batching küçültülür:

- exact candidate batch: `32`;
- hard-suite candidate batch: `32`;
- general-capability ayarları Document 159 ile aynıdır.

Bir evaluation task'ı çıktı oluşturmadan CUDA OOM olursa yalnız aynı task ID, candidate batch
`16` ile bir kez retry edilebilir. Kısmi/geçerli sonuç overwrite edilmez.

## 6. İş ve namespace koruması

Yeni wave öncesi şu koşullar zorunludur:

1. `453301` ve dependent OLMo eval `453303` hâlâ başlamamış/PENDING olmalıdır;
2. OLMo v4 training/evaluation namespace'leri absent olmalıdır;
3. yalnız `453301`, `453303` ve eski bağımlılık grafiğine bağlı summary `453304` iptal edilebilir;
4. Falcon/Pythia jobları ve yabancı işler korunur;
5. append-only relocation preflight, Document 159 shared/retry preflight hash'lerine, yeni commit,
   registry/template/launcher hash'lerine ve scratch capacity/no-home-write kanıtına bağlanır;
6. exactly one OLMo compatibility smoke → scientific training → six-checkpoint evaluation chain
   submit edilir; yeni summary job üç güncel evaluation jobına bağlanır.

Cancellation öncesi ve sonrası job-state ledger korunur. Eski V100 jobları bilimsel run sayılmaz,
çünkü GPU allocation/training namespace/optimizer update sıfırdır.

## 7. Implementation ve test kapısı

Dar implementation şunları içermelidir:

- ayrı OLMo RTX3090 FP16 template ve dedicated train/eval launcher;
- registry'de Document 159a SHA, RTX3090 runtime ve `4 x 125` binding;
- `load_registry`, runtime, effective-batch/checkpoint ve launcher fail-closed testleri;
- OLMo exact/hard candidate batch `32` binding testi;
- append-only relocation preflight üreticisi;
- local/HU targeted compatible pytest, shell syntax ve Python compile;
- ordinary non-force push ve 42-entry dirty-state/sıfır-overlap korunarak HU fast-forward.

Document 159, ilk Falcon pre-optimizer smoke failure'ı ve onun append-only repair evidence'i
korunur; historical artifact veya log değiştirilmez/silinmez.

## 8. Sonuç ve dokümantasyon

OLMo tamamlanınca mevcut Falcon/Pythia zincirleriyle aynı frozen cascade'e girer. Documents
160/161 şunları ayrıca raporlar:

- V100 queue blocker ve 159a relocation;
- kullanılan microbatch/accumulation, GPU/node, observed free/peak VRAM;
- bütün job ID/state/exit code'ları;
- 18-checkpoint Pareto tablosu, artifact hash/storage audit ve no-cleanup durumu.

## 9. Exact next authorization request

Bir sonraki yetki Document 159a'nın exact SHA-256'sına bağlı olarak şunları açıkça kapsamalıdır:

- local implementation/test ve dar ordinary non-force push;
- preservation-checked HU fast-forward ve append-only relocation preflight;
- başlamamış `453301/453303` ile stale summary `453304` için state-checked cancellation;
- exactly one OLMo RTX3090 FP16 memory-safe smoke → 500-fact six-checkpoint training → frozen
  cascade evaluation relocation;
- güncel üç-model evaluation DAG'ına tek summary job ve Documents 160/161.

Bu yetki silme/cleanup, Falcon/Pythia/yabancı job cancellation, threshold/LR değişimi veya ikinci
bilimsel OLMo run yetkisi vermez.
