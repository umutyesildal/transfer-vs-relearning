# 213 — M2 OSCAR scientific training v1 operational NOT_RUN sonucu

Tarih: 2026-09-01
Durum: `EXECUTED ONCE / PREFLIGHT PASS / TRAINING NOT_RUN / GPU GUARD BLOCKED`

## Yetki ve publication

Kullanıcı SHA-256 değeri
`748e2aae5c7e3ec95acaf639e4536e6024686e5a854ad09dc6013feb47490222` olan
`vngrs-m2-oscar-scientific-training-v1` sözleşmesini ve commit
`71fb16a7287120964d9d6e1c1c7ec8602de39f1a` için ordinary non-force push, HU
preservation-check sonrası fast-forward ve tek preflight/training-array/finalizer wave'ini açıkça
yetkilendirdi.

Commit origin'e ordinary non-force push edildi. HU checkout temiz
`86d9b253995013d31b62944e80708d665bf84e46` predecessor'ından exact yetkili commite yalnız
fast-forward ilerledi; branch, clean status ve contract SHA yeniden doğrulandı. HU compatible M2
suite `105/105 PASS` verdi.

## Job kimlikleri

- test-only scheduler tahminleri: `482203`, `482204`, `482205`;
- gerçek CPU preflight: `482206`;
- gerçek six-task A100 array: `482207_[0-5]`;
- afterok CPU finalizer/matrix builder: `482208`.

## Preflight sonucu

Job `482206` PASS tamamlandı ve training dependency'sini açtı. Exact kanıt:

| Artifact | SHA-256 |
|---|---|
| submission result | `14b2caae35a3033bb0e47c456b8e68bfea3a50997c31b2b6b7185e70679f906b` |
| config validation | `9b0b81e38f0a600361bcbec96859317fe13e7c8d5f9b5a2f53b51e71c10aea87` |
| preflight result | `f62323690347bb1a75885ea357149d8d7e7de4733725aa23256dfe55ca7e8211` |
| six-config manifest | `af5ab14d709b177088261584ba934c56dc228695641a9d676e77e30ee61a4b9f` |

Preflight terminal status `M2_SCIENTIFIC_TRAINING_PREFLIGHT_PASS` oldu. Corrected 250-fact human
review, corrected block family, exact parents, üç smoke PASS raporu ve altı corrected-family config
doğrulandı. Canlı scratch gözlemi `122,148,408,524,800` free byte ve `2,283,847,145` free inode idi.

## Training array terminal sonucu

Altı task'in tamamı `gruenau10` üzerinde model yüklemeden önce terminal oldu:

| Task | Rol/arm | Runtime | Slurm state | Exit |
|---:|---|---:|---|---|
| 0 | OLMo/M2-A | 4 s | `FAILED / NonZeroExitCode` | `1:0` |
| 1 | OLMo/M2-B | 3 s | `FAILED / NonZeroExitCode` | `1:0` |
| 2 | Qwen/M2-A | 3 s | `FAILED / NonZeroExitCode` | `1:0` |
| 3 | Qwen/M2-B | 3 s | `FAILED / NonZeroExitCode` | `1:0` |
| 4 | SmolLM/M2-A | 3 s | `FAILED / NonZeroExitCode` | `1:0` |
| 5 | SmolLM/M2-B | 3 s | `FAILED / NonZeroExitCode` | `1:0` |

Her task'in stdout ve stderr dosyası `0` byte'tır. Yalnız task-local `tmp/train_*` dizinleri
oluşmuştur; training run directory, model load, optimizer update, checkpoint, training manifest,
binding veya evaluation matrix yoktur. Finalizer `482208`, `afterok:482207_*(failed)` nedeniyle
`DependencyNeverSatisfied` kaldı ve ayrıca yetki olmadığı için iptal edilmedi.

## Exact operational trigger

2026-09-01 18:12 Europe/Berlin read-only `nvidia-smi` ledger'ında gruenau10'daki üç A100'ün
tamamında Slurm dışı foreign compute process vardı:

| GPU | Used MiB | Free MiB | Foreign process durumu |
|---:|---:|---:|---|
| 0 | 13,891 | 67,262 | 4 process |
| 1 | 25,158 | 55,995 | 3 process |
| 2 | 2,815 | 78,338 | 1 process |

Sözleşme allocated GPU üzerinde exact sıfır compute process ve en az 61,440 MiB free VRAM
zorunlu tutuyordu. Bu nedenle GPU0 ve GPU2 free-memory eşiğini geçse de zero-process guard'ında;
GPU1 hem zero-process hem free-memory guard'ında fail-closed durdu. Altı görevin de aynı guard
öncesi noktada sessiz `test` exit'i vermesi controller timing, boş loglar, oluşmuş tmp dizinleri ve
node ledger ile uyumludur.

## Korunan root ve bilimsel sınıflandırma

Fresh root:

```text
/vol/tmp2/yesildau/vnd_m2_oscar_scientific_training_v1
```

Terminal root `24` dosya / `73,256` byte'tır. Cleanup veya deletion yapılmadı.

Bu sonuç bilimsel negatif değildir. Exact sınıf:

```text
OPERATIONAL_NOT_RUN_GPU_ZERO_PROCESS_GUARD
```

Scientific M2-A/M2-B training başlamadı; token tüketimi, optimizer update, checkpoint ve evaluation
sıfırdır. Contract'ın tek wave yetkisi tüketilmiştir. Otomatik retry, fallback, ikinci wave,
threshold gevşetme veya foreign process müdahalesi yetkili değildir. Yeni girişim; failure ledger'ı
atomik persist eden ve GPU isolation/selection politikasını açıkça yeniden donduran ayrı contract ve
exact kullanıcı yetkisi gerektirir.
