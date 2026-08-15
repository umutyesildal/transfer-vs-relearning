# 159b — OLMo RTX3090 Explicit BF16 Parameter/Optimizer-State Repair Contract

**Tarih:** 2026-08-11 (Europe/Berlin)  
**Durum:** `FROZEN — UNEXECUTED — EXACT SHA-BOUND AUTHORIZATION REQUIRED`

## 1. Fail-closed evidence

Document 159a relocation üç kez bilimsel training başlamadan fail-closed olmuştur:

- `453386`: FP16, microbatch 4, accumulation 125; AdamW optimizer smoke OOM;
- `453479`: precommitted microbatch 2, accumulation 250 fallback; aynı optimizer-state OOM;
- `453513`: aynı fallback + `optimizer_foreach:false`; tek-tensor AdamW sqrt aşamasında
  784 MiB allocation için yalnız 553 MiB kaldığından OOM.

Üçünde de OLMo v4 training/evaluation namespace'i absent, optimizer training update/checkpoint ve
bilimsel sonuç sıfırdır. Runtime guard ayrıca guppi7'de bir kirli ve iki temiz RTX3090 UUID'sini
ayırmıştır; yabancı process'e dokunulmamıştır.

## 2. Dar repair

OLMo yalnız aşağıdaki explicit low-memory BF16 moduna geçer:

- `model_load_dtype: bfloat16`;
- `bf16: true`, `fp16: false`, GradScaler disabled;
- parameter, gradient ve AdamW `exp_avg/exp_avg_sq` state dtype'ları BF16;
- microbatch 5, accumulation 100, effective batch 500;
- `optimizer_foreach:false`.

Smoke; BF16 parameter/gradient/optimizer-state dtype inventory'sini, finite loss/gradient,
checkpoint save/reload ve peak VRAM'i fail-closed doğrular. Explicit BF16 dtype gate geçmeden
training başlamaz. Bu, Falcon/Pythia için doğrulanmış RTX3090 BF16 mekanizmasıyla aynıdır.

## 3. Korunan bilimsel alanlar

Model/revision, dataset/hash, seed/data-seed, LR `5e-5`, answer-only loss, EOS=false, scheduler,
weight decay, effective batch 500, 252 update, checkpoint grid `42/84/126/168/210/252`, frozen
evaluation cascade, PPL `<=1.25` ve bütün robustness eşikleri değişmez. Outcome-aware checkpoint,
threshold/LR değişimi, replay, seed43, corpus, M2/M3 ve cleanup yoktur.

FP16→explicit BF16 parameter-state değişimi maddi runtime precision repair'ıdır ve Documents
160/161'de limitation olarak raporlanır. OLMo v4 sonucu önceki FP16 endpoint ile tam bitwise
karşılaştırma sayılmaz; precommitted dose/gate analizi geçerli kalır.

## 4. GPU placement ve tek zincir

`guppi6` yasaktır. guppi7 probe ledger'ında kirli UUID
`GPU-9ef665e6-fafe-8760-cae6-33c3cfaf8a5d` quarantine allocation ile ayrılır; yalnız 24.11 GB
free gösteren temiz UUID üzerinde smoke/training açılır. Quarantine OLMo allocation aldıktan sonra
kapatılır. Evaluation öncesi aynı clean-device guard tekrarlanır.

Başlamamış dependent jobs `453514/453515` state-checked iptal edilebilir. Exactly one explicit-BF16
OLMo smoke → six-checkpoint training → frozen cascade evaluation zinciri ve güncel üç-model
summary submit edilir. Falcon/Pythia/yabancı işler korunur.

## 5. Implementation ve yetki sınırı

Dar implementation template/registry/runtime/launcher/test ve append-only BF16 repair preflight
ile sınırlıdır. Local/HU tests, ordinary non-force push ve 42-entry preservation-checked HU
fast-forward zorunludur. Historical logs/preflight/artifacts korunur; silme/cleanup yoktur.

## 6. Exact next authorization request

Bir sonraki yetki Document 159b'nin exact SHA-256'sına bağlı olarak local implementation/test,
dar ordinary non-force push, preservation-checked HU fast-forward, append-only BF16 repair
preflight, başlamamış `453514/453515` için state-checked cancellation, clean-guppi7 quarantine ve
exactly one OLMo RTX3090 explicit-BF16 parameter/optimizer-state smoke → six-checkpoint training →
frozen cascade evaluation ile güncel summary ve Documents 160/161'i açıkça kapsamalıdır.
