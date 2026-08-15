# Document 169 — M1 Dose/Pareto Falcon Exclusive Recovery Execution Result (TR)

**Tarih:** 2026-08-13, Europe/Berlin  
**Contract:** Document 168 SHA-256
`6e57f90897db8202bcb338a84b6a3b99abb2bf3a887e1a2cdaefacdde08021c8`  
**Sonuç:** `NOT RUN — EXCLUSIVE ALLOCATION EXPOSED FOUR GPUs — FAMILY REMAINS 15/18`

## 1. Preflight ve submission

Fresh preflight PASS verdi:

```text
path = /vol/tmp2/yesildau/m1_provenance_screen_v4_dose_pareto_v1/
       preflight/falcon_rtxa6000_exclusive_recovery_6589f6a.json
SHA-256 = b1119e82f69a954dcc11fdef7986cfb3cfd8f8a8cf40d13d1e5233025a872707
family rows = 15/18
missing = Falcon {126,210,252}
route = gruenau8|gpu|up|idle|gpu:rtxa6000:4,mps:rtxa6000:400
```

Document 165'in dependency-dead summary job'u `456415` contract kapsamında iptal edildi.
`sbatch --test-only` PASS ile scheduler test job ID `456465` ve immediate-start tahmini verdi.
Exactly one real array ve one afterok summary submit edildi:

```text
evaluation array = 456466_[2,4,5%1]
summary          = 456467
dependency       = afterok:456466
```

## 2. Runtime fail-closed result

`--exclusive` node allocation her task'a requested one GPU yerine Slurm accounting'de bütün dört
RTX A6000'ü verdi:

```text
ReqTRES   = gres/gpu=1, gres/gpu:rtxa6000=1
AllocTRES = gres/gpu=4, gres/gpu:rtxa6000=4
CPUs      = 72 allocated
node      = gruenau8
```

Runtime validator ilk CUDA gate'inde `torch.cuda.device_count() != 1` gördü ve şu exact hata ile
evaluator hazırlığından önce durdu:

```text
ValueError: Exactly one allocated CUDA device is required
```

Task ledger:

| Step/task | Slurm JobId | State | Elapsed | Exit |
|---|---:|---|---:|---:|
| 126 / `_2` | `456468` | FAILED | 00:00:15 | 1:0 |
| 210 / `_4` | `456469` | FAILED | 00:00:05 | 1:0 |
| 252 / `_5` | `456466` | FAILED | 00:00:05 | 1:0 |

Üç stdout da 0 byte ve SHA-256
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`; üç stderr de 421 byte
ve SHA-256 `a5adab8df62780f9b71544e35bad540399c458dc6e2a026ea2e57a4b782e1ece`'dir.

## 3. Artifact ve dependency closure

Device-count gate, `nvidia-smi` process evidence ve runtime manifest yazımından önce çalıştı. Üç
runtime manifest ve evaluation root absent kaldı; model load, inference, exact/PPL/hard evaluation
başlamadı. Family cheap-gate inventory `15/18` kaldı.

Summary job `456467`:

```text
state  = PENDING
reason = DependencyNeverSatisfied
root   = absent
```

Document 168 yalnız eski `456415` cancellation'ını yetkilendirdi; yeni dead summary'ye müdahale
edilmedi. İkinci array/retry submit edilmedi.

## 4. Preservation

```text
HU HEAD/status = 6589f6a / 49 entries / preserved SHA-256
family root    = 168,515,673,816 bytes (`du -sb`)
/vol/tmp2 free = 123,657,891,348,480 bytes
/vol/tmp2 inode use = 3%
cleanup/deletion = none
```

Bu operasyonel NOT-RUN sonucudur; Falcon scientific score değildir.
