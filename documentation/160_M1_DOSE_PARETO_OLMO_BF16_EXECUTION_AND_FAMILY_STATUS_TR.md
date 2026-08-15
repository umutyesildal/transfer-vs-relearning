# Document 160 — M1 Dose/Pareto OLMo BF16 Execution Result and Family Status (TR)

**Tarih:** 2026-08-12, Europe/Berlin  
**Authority:** Documents 159, 159a ve exact authorized Document 159b  
**159b SHA-256:** `6bbd299645ca36463b3fd3fdb9f90288e8ec3f4f6ba2312bd4ce704ccd225984`  
**Sonuç:** `OLMo COMPLETE SCIENTIFIC NEGATIVE; THREE-MODEL FAMILY INCOMPLETE`

## 1. Execution reconciliation

Kullanıcının exact 159b authorization'ı verildiğinde read-only HU inspection, authorized OLMo
zincirinin başka bir aktif worker tarafından zaten tamamlandığını gösterdi:

```text
HU commit             = 4083158e06f95d38c07d0449f934cbeb73fa4096
training job          = 454283
evaluation array      = 454284_[0-5]
training namespace    = present, one run
OLMo checkpoint gates = 6/6 present
active m1-v4 jobs     = 0
```

Bu nedenle duplicate submission yapılmadı. Document 159b'deki eski dependent jobs `453514/453515`
canlı queue'da yoktu; state-checked cancellation için hedef kalmadığından cancellation çağrısı
yapılmadı. `sacct` Munge/SlurmDBD authentication failure nedeniyle sonuç döndürmedi; bu eksik
accounting metadata'sıdır. Completion aşağıdaki manifest/log/evaluation artifact'lerinden
doğrulanmıştır.

## 2. BF16 compatibility ve smoke sonucu

Append-only preflight:

```text
/vol/tmp2/yesildau/m1_provenance_screen_v4_dose_pareto_v1/preflight/olmo_bf16_4083158.json
SHA-256 = e3211986f07dcd9903f503ab729bad76a4bb92abcc5c76fc684116c9eab44c0b
status  = PASS
```

Runtime manifest:

```text
GPU                   = NVIDIA GeForce RTX 3090
free bytes            = 25,003,687,936
total bytes           = 25,296,044,032
compute capability    = 8.6
Torch/CUDA            = 2.6.0+cu124 / 12.4
AMP dtype             = bfloat16
SHA-256               = 30cf86bf555f053d8ad80a911a6e367836821dca45cd7ac5579ac70ff4e84db3
```

Smoke manifest:

```text
status                   = passed
parameter dtype          = torch.bfloat16
gradient dtype           = torch.bfloat16
AdamW exp_avg/exp_avg_sq = torch.bfloat16
GradScaler               = disabled
optimizer_foreach        = false
microbatch/accumulation  = 5 / 100
effective batch          = 500
optimizer steps          = 1
finite loss              = 8.661642074584961
peak allocated bytes     = 13,052,446,208
smoke checkpoint         = save/reload PASS, preserved
smoke SHA-256            = 886ccaf484334be64426cf54571c94c7244c82989d8c81c8d8b3e2d5cbc1c0b3
```

Bu kanıt 159b'nin explicit BF16 parameter/gradient/optimizer-state repair'ının runtime gate'ini
geçtiğini gösterir. FP16 historical endpoint ile bitwise eşitlik iddiası yapılmaz.

## 3. OLMo scientific training

Run:

```text
/vol/tmp2/yesildau/m1_provenance_screen_v4_dose_pareto_v1/training/olmo/
  20260812T043539Z_m1_provenance_screen_v4_dose_pareto_v1_olmo_seed42_43bab681
```

Kimlik ve sonuç:

```text
model                  = allenai/OLMo-2-0425-1B
revision               = a1847dff35000b4271fa70afc5db10fd29fedbdf
parameters             = 1,484,916,736
seed/data seed          = 42 / 42
dataset rows            = 3,500 train / 500 validation
dataset SHA             = frozen 159 registry values
learning rate           = 5e-5
epochs/updates          = 36 / 252
checkpoint grid         = 42,84,126,168,210,252
train runtime           = 4,855.4297 seconds
train loss              = 0.31161744197200436
final eval loss         = 0.0007769028889015317
status                  = COMPLETE
```

Manifest SHA-256:

```text
training_manifest = 63b8713ae46a309844098b7674f01098d87a0f5600a508b79f1956041bcb3826
train_metrics     = 05f3b07e1a41c112041eebeaccb0ae8580bf57af0b30595a8737e166d6cc9ad6
eval_metrics      = e9640ff121b4d25ebf55ff07207ae5933048082c67a1dfbfd8b9048132ae9568
```

Checkpoint model SHA-256 ledger:

| Step | `model.safetensors` SHA-256 |
|---:|---|
| 42 | `e53dc9c8aa32cc2048e7187af09c1278d26d4b9c4c31ae0ca1f5a7b8da0fb7de` |
| 84 | `9127898cd832fd89936f28e313dd8a5e24d9b6ade5b6ed3425bf8db78544fab7` |
| 126 | `c2de8e856ab65d20d52ecec16282fa8af7927ad302103ce3853ec10024a763c8` |
| 168 | `5b5d51b94c62d6da519c6320c48569b3563bb30456af8f0d4ee4e859dc21e013` |
| 210 | `cc4983f0dc800874ece39f2b9565924bc2d68014787a8579e42850e707a258ec` |
| 252 | `dc01cfeb4d0d3346f796eac0989e515d305eb4498e2c490f46a6a3650c344fd6` |

Final model SHA-256, checkpoint-252 ile aynıdır:
`dc01cfeb4d0d3346f796eac0989e515d305eb4498e2c490f46a6a3650c344fd6`.

Training/evaluation logs'da traceback, OOM, CUDA error, NaN veya RuntimeError signature'ı yoktur.

## 4. OLMo six-checkpoint cascade result

| Step | Exact | PPL | PPL ratio | Integrity | Hard stage |
|---:|---:|---:|---:|---|---|
| 42 | 1.000 | 23.2970 | 1.38543 | PASS | closed |
| 84 | 1.000 | 23.6972 | 1.40923 | PASS | closed |
| 126 | 1.000 | 23.8303 | 1.41714 | PASS | closed |
| 168 | 1.000 | 23.9097 | 1.42186 | PASS | closed |
| 210 | 1.000 | 23.9742 | 1.42570 | PASS | closed |
| 252 | 1.000 | 24.0234 | 1.42862 | PASS | closed |

Base PPL `16.8157879211`, frozen maximum ratio `1.25`'tir. Altı checkpoint'in tamamı exact
acquisition'ı geçse de retention gate'ini kaçırır. Precommitted cascade gereği hard suite hiçbir
checkpoint için açılmaz. OLMo'nun en iyi observed retention noktası step 42'dir, fakat
`1.38543 > 1.25`; eligible OLMo nominee yoktur.

Cheap-gate SHA-256 ledger:

```text
step42  ae6f73abbf9a5d08e0b73fb056c8854d1ecf4cc94094e83e29fa83a6c2cff783
step84  521cb5ad904a02b69fafc3c700f2fff995d5b25f937cc4bcd7910dfbb0cd3df6
step126 ad8c5eecf25ef762cda59e45e518e00e95b74d8df1c1094b80984dd8fded19a4
step168 7c69de7e474ffe8aac1cc0913173a0e60400d3d4a6f1275428e67e400e532587
step210 6c6cc2ca0b16ed23f28ec10e4c01e5b53444867d1d595170f426f3661e4a90f4
step252 432a8a5805521f8214173adad2cf4df07da843ccd1e3ccfe58b1216e59b4a837
```

## 5. Three-model family reconciliation

| Model | Training | Cheap gates | Observed result | Family status |
|---|---|---:|---|---|
| OLMo | COMPLETE | 6/6 | exact 100%; PPL ratio 1.385–1.429; no hard stage | valid scientific negative |
| Pythia | COMPLETE | 6/6 | exact 100%; PPL ratio 16.100–17.730; no hard stage | valid scientific negative |
| Falcon | COMPLETE | 3/6 | exact 100%; observed PPL ratio 9.568–9.994; no hard stage | incomplete evaluation |

Falcon missing tasks are checkpoint 126, 210 and 252 (`453302_2/_4/_5`). Her üçü de scientific
evaluation başlamadan runtime gate'te aynı kanıtla durmuştu:

```text
ValueError: Insufficient free VRAM: 12083855360
```

Üç error log'unun SHA-256 değeri aynıdır:
`efb943105c772b3cae949331176868fec0ead6a4b59ef25876149a20ef6ecd22`.

159b Falcon re-evaluation retry'sini authorize etmez; Falcon/Pythia korunmuştur. Bu nedenle 18-row
three-model summary üretilmedi. Mevcut eksik checkpoint'ler outcome olarak doldurulmadı ve sonraki
Falcon davranışı önceki üç PPL değerinden tahmin edilmedi.

## 6. Post-run storage/preservation

```text
family root bytes       = 168,515,628,105
/vol/tmp2 available     = approximately 113 TiB
/vol/tmp2 inode use     = 3%
HU home large files     = unchanged known five files
HU checkout status      = 42 entries / 6,989 bytes
HU status SHA-256       = 71a2e3b1d03a5c73ab3fb16c02e59910b7ec35f553956b079edcf71f3a3c59e9
cleanup/deletion        = none
```

## 7. Honest result

```text
159b OLMo execution          = COMPLETE
OLMo scientific decision    = NEGATIVE / NO ELIGIBLE CHECKPOINT
three-model family           = INCOMPLETE_FALCON_EVALUATION
three-model summary          = NOT GENERATED
automatic primary selection = false
seed43                      = not authorized
M2-A/M2-B                   = not authorized
```

