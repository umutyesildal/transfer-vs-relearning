# Document 170 — M1 Dose/Pareto Post-Falcon Exclusive Recovery Gate (TR)

**Tarih:** 2026-08-13, Europe/Berlin  
**Related result:** Document 169  
**Gate:** `BLOCKED — SLURM EXCLUSIVE EXPANDS GPU VISIBILITY; FAMILY 15/18`

## 1. Recovery decision

```text
preflight                         = PASS
test-only                         = PASS
exclusive allocation             = received
exactly-one-visible-CUDA-device   = FAIL
clean-process/free-VRAM evidence  = NOT REACHED
scientific evaluation            = NOT RUN
recovery wave                     = consumed
```

`--exclusive` foreign Slurm allocation'ı önledi; fakat bu cluster/GRES semantiğinde requested
single A6000 yerine dört A6000'ü allocation/visibility kapsamına aldı. Tek-device scientific
runtime binding'i bozulduğu için validator'ın durması doğrudur. Dört cihazdan keyfî birini seçmek
Document 168'i ihlal ederdi.

## 2. Family/project gate

```text
required rows               = 18
available rows              = 15
missing                     = Falcon {126,210,252}
summary                     = not generated
selected English-centric M1 = none
automatic promotion         = false
ready_to_train              = false
```

## 3. Next operational gate

Gelecekteki bir Falcon continuation ancak yeni exact contract ile yapılabilir. Contract,
node-exclusive allocation yerine single-GPU visibility'yi kesin biçimde sağlamalıdır; örneğin
allocation sonrası dört görünür GPU arasından temizliği kanıtlanmış tek UUID'yi precommitted
deterministic kuralla bağlamak veya cluster yöneticisinden gerçek single-GPU isolation semantiği
almak gerekir. Bu seçim job içinde dört GPU'nun UUID/process/free-memory ledger'ı yazıldıktan sonra,
model load öncesinde yapılmalıdır. Existing 15 evaluation ve training tekrar edilmemelidir.

Summary `456467` dependency-dead kalmıştır; cancellation ayrı authority gerektirir. Bu belge retry,
job cancellation, GPU selection/relocation, seed-43, threshold/recipe change, Turkish dose ladder,
M2-A/M2-B, cleanup veya deletion yetkisi vermez.
