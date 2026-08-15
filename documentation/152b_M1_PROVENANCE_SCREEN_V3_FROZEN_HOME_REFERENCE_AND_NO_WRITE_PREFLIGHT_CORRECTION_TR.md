# 152b — M1 Provenance Screen v3: Frozen Home Reference ve No-Write Preflight Düzeltmesi

**Tarih:** 2026-08-11 (Europe/Berlin)  
**Durum:** `FROZEN — LOCAL IMPLEMENTATION PREPARED — EXECUTION UNAUTHORIZED`  
**Kapsam:** yalnız Document 152a/153/154 üç-model v3 dalgasının HU-home storage preflight'i  
**Bilimsel recipe:** değişmedi

## 1. Neden gerekli?

Document 153 dalgası model erişiminden önce, HU home ağacında zorunlu tutulan recursive
`du -x -B1 -s` kontrolü 120 saniyede tamamlanmadığı için fail-closed oldu. Bu timeout home'un
30 GiB sınırını aştığını göstermedi; yalnız ağaç dolaşımının o çağrıda bounded süreye sığmadığını
gösterdi. Aynı recursive tarama dış wrapper'a ek olarak acquisition, training ve evaluation
preflight'larında da tekrar ediliyordu. Bu tekrarlar bilimsel güvence üretmeden operasyonel
blokaj yaratıyordu.

Bu belge yalnız v3 için Document 151ax'tan miras alınmış “her stage canlı recursive du” kuralını
supersede eder. Document 151ax'ın tarihsel corpus wave'leri veya başka deney aileleri yeniden
yorumlanmaz.

## 2. Tek seferlik exact referans ölçümü

Kullanıcının açık isteğiyle HU home bir kez salt-okunur ve 600 saniye bound ile ölçüldü:

```text
command: timeout 600s /usr/bin/time -f ... du -x -B1 -s /vol/fob-vol6/mi25/yesildau
started_at: 2026-08-11T07:30:52+02:00
finished_at: 2026-08-11T07:32:29+02:00
command_rc: 0
home_usage_bytes: 14689423360
elapsed_seconds: 96.99
max_rss_kib: 3456
limit_bytes: 32212254720
below_30_GiB: true
```

`14,689,423,360` byte yaklaşık `13.68 GiB`'dir. 30 GiB sınırına göre yaklaşık `16.32 GiB`
headroom vardır. Bu ölçüm v3 continuation'ın frozen başlangıç referansıdır; başka deney ailelerine
veya belirsiz gelecekteki dalgalara otomatik yetki/evidence sağlamaz.

## 3. Yeni v3 storage güvenlik modeli

Sonraki ayrı yetkili v3 continuation'da recursive home `du` submission veya per-stage blocker
olmayacaktır. Güvenlik şu birlikte zorunlu kontrollerle sağlanır:

1. Registry'deki exact frozen reference byte değeri bu belgedeki değerle eşleşir ve `<30 GiB`'dir.
2. `home_write_allowed=false` fail-closed registry invariant'ıdır.
3. `runs`, `artifacts`, family root ve candidate output namespace'leri yalnız
   `/vol/tmp/yesildau/` veya `/vol/tmp2/yesildau/` altında resolve edilir.
4. Aşağıdaki yüksek hacimli/cache/temp environment yollarının tamamı scratch altında bulunur:
   `HF_HOME`, `TRANSFORMERS_CACHE`, `HF_DATASETS_CACHE`, `XDG_CACHE_HOME`, `TORCH_HOME`, `TMPDIR`.
5. Ek cache yolları da scratch'a sabitlenir: `TRITON_CACHE_DIR`, `CUDA_CACHE_PATH`, `MPLCONFIGDIR`,
   `NUMBA_CACHE_DIR`, `WANDB_DIR`; `WANDB_MODE=disabled` ve `PYTHONDONTWRITEBYTECODE=1` kullanılır.
6. Frozen v3 root execution öncesi absent; prior v1/retry root'ları immutable/read-only olmalıdır.
7. `df -hP` ve `df -iP` ile home filesystem ve scratch kapasite/inode görünümü alınır; family'nin
   149 GiB planlama rezervi scratch free-space ve inode sayısına sığmalıdır.
8. Dataset hash/count, commit, dirty-path overlap ve duplicate `m1-pv3-*` job kontrolleri değişmez.
9. Candidate model/tokenizer/download/checkpoint/evaluation yollarından herhangi biri HU home'a
   resolve olursa stage fail-closed olur.

Tam recursive `du` ve tam recursive `>500 MiB find` v3'ün her-stage kapısından çıkarılır. Bunlar
submission öncesi veya candidate stage'lerinde tekrar çalıştırılmaz. Bu değişiklik home'a yazma
izni değildir; pahalı global tarama yerine v3 process'lerinin bütün yazma hedeflerini önceden
sınırlar ve doğrular.

## 4. Uygulama düzeltmeleri

Local implementation şunları hazırlar:

- `m1_provenance_screen_v3.yaml` içine frozen home-reference/no-write policy;
- registry validation'da exact reference `< limit`, no per-stage du ve no-home-write invariant'ı;
- `m1_cross_family_preflight.py` içinde v3 için live recursive du yerine frozen evidence kaydı;
- legacy aileler için mevcut live `du -xsk` davranışının korunması;
- v3 preflight manifestinde reference command/timestamp/bytes/limit/evidence mode;
- bütün acquisition/training/evaluation/preflight Slurm job'larında scratch cache/tmp environment;
- dış submit wrapper'da recursive `du` ve recursive large-file scan yerine frozen-reference eşliği,
  `df`, inode, resolved path, root absence, dataset ve queue kontrolleri;
- targeted registry/preflight testlerinde exact `14,689,423,360` byte, 30 GiB limit,
  `recursive_du_executed_for_this_stage=false` ve `home_write_allowed=false` assertions.

Local Mac environment'ında PyYAML bulunmadığı için dependency kurulmaz. `py_compile`, `bash -n` ve
diff checks local çalışır; authoritative targeted pytest, sonraki yetkili HU continuation'da model
erişimi ve `sbatch` öncesinde çalışmalıdır. Test collection/failure durumunda root/job submission
açılmaz.

## 5. Değişmeyen bilimsel ve operasyonel sınırlar

Aşağıdakiler Document 152a'daki exact halleriyle değişmez:

- OLMo/Pythia/Falcon model ID ve revision'ları;
- 100 subject / 500 fact dataset ve üç SHA-256 kimliği;
- seed 42, 36 epoch, effective batch 500, 252 update, LR `5e-5`;
- answer-only, EOS false, block 128 ve update-252-only endpoint;
- model-native tokenizer round-trip/masking/smoke gate'i;
- base + endpoint exact/hard/binding/PPL evaluation;
- üç bağımsız candidate DAG ve fresh root
  `/vol/tmp2/yesildau/m1_provenance_screen_v3`;
- no cleanup/deletion, no corpus, no seed-43, no M2-A/M2-B.

## 6. Stop conditions

Continuation şu durumlarda model erişiminden veya ilgili candidate stage'inden önce durur:

- frozen reference registry/document eşleşmez veya reference `>=30 GiB` ise;
- `home_write_allowed` true olur veya per-stage recursive du yeniden etkinleştirilirse;
- zorunlu cache/tmp/output path'lerinden biri scratch dışında/HU home altında resolve olursa;
- root önceden varsa, prior-root write tespit edilirse veya dirty incoming-path overlap varsa;
- scratch free space/inode 149 GiB family rezervini karşılamazsa;
- HU targeted pytest PASS vermezse;
- dataset/commit/config/launcher hashleri veya scientific recipe değişirse;
- duplicate v3 job varsa.

## 7. Yetki durumu ve sonraki exact istek

Bu belge tek seferlik ölçümü ve local correction'ı kaydeder; push, HU fast-forward, model access,
Slurm/GPU, training veya evaluation yetkisi vermez. Yeni execution için kullanıcı şu kapsama denk
ayrı bir explicit authorization vermelidir:

> Document 152b'nin exact SHA-256'sına bağlı local implementation/test düzeltmesini, dar ordinary
> non-force push'u, preservation-checked HU fast-forward'u, frozen-reference/no-home-write
> preflight'ini ve `/vol/tmp2/yesildau/m1_provenance_screen_v3` altında Document 152a'daki üç
> bağımsız candidate acquisition → smoke → training → base/endpoint evaluation zincirinin bir kez
> yürütülmesini yetkilendiriyorum.

Başarılı submission veya training, seed-43/corpus/M2-M3/cleanup yetkisi üretmez.
