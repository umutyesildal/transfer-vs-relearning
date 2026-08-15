# 156b — Pythia V100 Kuyruğundan RTX 3090'a Dar Relocation Kontratı

**Tarih:** 2026-08-11 (Europe/Berlin)  
**Durum:** `FROZEN — READY_FOR_EXACT_USER_AUTHORIZATION — UNEXECUTED RELOCATION`

## 1. Gerekçe ve korunacak kanıt

Document 156a'nın yetkili retry zincirinde acquisition preflight `452895`, resmî tokenizer işi
`452896` ve training preflight `452897` PASS oldu. Exact tokenizer source, `pad_token=None`
round-trip, 50.277 vocabulary ve composite model manifest yeni retry root altında oluştu:

```text
/vol/tmp2/yesildau/m1_provenance_screen_v3_pythia_repair_retry_v1
```

V100 training `452898` bilimsel training başlamadan `PENDING(Resources)` kaldı. Ona bağlı
`452899` ve `452900` da başlamadı. `gruenau1` üzerindeki üç V100 başka kullanıcının işleriyle
dolu ve Slurm tahmini `2026-08-13T15:09:23+02:00` oldu. Buna karşılık `guppi5`, `guppi6` ve
`guppi7` üzerinde toplam dokuz `rtx3090` kartı aynı salt-okunur taramada idle görüldü.

İlk iki Pythia repair root'u, completed tokenizer/preflight kanıtı ve historical job/log
artifactleri append-only korunur. Relocation acquisition/tokenizerı tekrar etmez.

## 2. Değişmeyen bilimsel kontrat

Aşağıdakiler aynen korunur:

- model: `EleutherAI/pythia-1.4b@0da31d8fb309463877ed8c40e54a8f911dced3ec`;
- resmî tokenizer source commit/path/bytes/SHA-256 ve composite manifest;
- dataset hash/count'ları: 3.500 train + 500 validation, 500 subject/fact;
- seed `42`, 36 epoch, effective batch `500`, 252 optimizer update;
- LR `5e-5`, answer-only loss, `supervise_eos:false`, block size `128`;
- FP16 + GradScaler, gradient checkpointing ve endpoint-only checkpoint;
- tokenization, optimizer smoke, hard-suite, exact-prefix ve general-capability gate'leri;
- base/endpoint evaluator, thresholds ve artifact-retention kuralları.

Yalnız allocated GPU sınıfı ve ona bağlı fail-closed runtime identity değişir. Bu bir scientific
recipe remediation veya outcome-aware retry değildir; V100 training hiç başlamadığı için yalnız
operasyonel relocation'dır.

## 3. Frozen RTX 3090 runtime

Scheduler selector:

```text
gpu:rtx3090:1
```

Runtime identity:

```text
python: /vol/tmp2/yesildau/m1_provenance_screen_v3/compat_envs/torch260_cu124_v1/bin/python
torch: 2.6.0+cu124
expected_gpu: NVIDIA GeForce RTX 3090
expected_compute_capability: 8.6
expected_compiled_arch: sm_86
precision: FP16 + GradScaler
```

Training ve evaluation launcherlar allocation içinde exact GPU name, capability, compiled arch,
Torch/Python identity ve finite FP16 forward/backward kontrolünde fail-closed kalır. 24 GiB kartta
optimizer smoke veya gerçek training OOM olursa bu bilimsel sonuç sayılmaz ve otomatik başka
recipe/retry açılmaz.

## 4. Tek relocation prosedürü

Exact authorization sonrası:

1. `452898`, `452899`, `452900` hâlâ training başlamadan pending/dependency durumundaysa yalnız bu
   üç job cancel edilir; başka job'a dokunulmaz.
2. Retry root'ta training checkpoint/run/evaluation namespace'lerinin absent olduğu, composite
   manifestin hash-bound PASS olduğu ve checkout/dirty-state'in korunduğu doğrulanır.
3. Dar registry/test commit'i ordinary non-force push edilir ve HU preservation-checked
   fast-forward yapılır.
4. Yeni `training_rtx3090.json` preflight'i submit edilir; sonra `afterok` ile exactly one RTX3090
   training job bağlanır.
5. Training sonrasında yeni `evaluation_rtx3090.json` preflight'i ve exactly one RTX3090
   base/endpoint evaluation job'u `afterok` ile bağlanır.
6. Allocation `guppi5/6/7` idle havuzundan scheduler tarafından seçilir; başka kullanıcının işi
   iptal edilmez, node'a pin veya exclusive allocation yapılmaz.
7. Result ve gate Documents 157/158'e append-only yazılır; storage/no-home-write audit kapanmadan
   operational completion iddiası yapılmaz.

İlk root'lar, job logları, manifestler, model/dataset, corpus, OLMo/Falcon artifactleri ve HU home
salt-okunur kalır. Cleanup/deletion yoktur.

## 5. Kapsam dışı

Pythia seed-43, recipe/LR/epoch değişimi, OLMo/Falcon remediation training, corpus çalışması,
M2-A/M2-B, A100/V100/RTX6000 fallback, checkpoint seçimi ve sonuç sonrası ek retry kapsam dışıdır.

## 6. Exact authorization request

> Document 156b'nin exact SHA-256'sı kapsamındaki dar RTX3090 registry/test düzeltmesini, ordinary
> non-force push'u, preservation-checked HU fast-forward'u; henüz başlamamış `452898/452899/452900`
> joblarının durum/namespace korumasından sonra yalnız bu üç jobın cancellation'ını ve mevcut
> verified tokenizer/composite-manifest kanıtını yeniden kullanarak exactly one RTX3090 training
> preflight → FP16 smoke/500-fact training → evaluation preflight → base/endpoint evaluation
> relocation zincirini; ayrıca Documents 157/158 result/gate dokümantasyonunu yürütmeni
> yetkilendiriyorum.
