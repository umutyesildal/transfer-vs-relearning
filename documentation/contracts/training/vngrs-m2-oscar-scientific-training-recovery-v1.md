# Frozen execution contract — `vngrs-m2-oscar-scientific-training-recovery-v1`

Tarih: 2026-09-01
Durum: `FROZEN / UNEXECUTED / EXACT USER AUTHORIZATION REQUIRED`

## 1. Tek amaç ve predecessor sınırı

Bu sözleşme, v1 array `482207_[0-5]` görevlerinin model load öncesinde shared-node
zero-process guard'ında durmasından sonra aynı altı bilimsel koşuyu tek fresh-root recovery wave'i
olarak sınırlar. V1 root'u ve tüm kanıtları read-only kalır. V1 sonucu bilimsel negatif değil,
`OPERATIONAL_NOT_RUN_GPU_ZERO_PROCESS_GUARD` sınıfıdır.

Dependency-dead finalizer `482208` yalnız exact `PENDING`, `DependencyNeverSatisfied`, runtime
`00:00:00`, never-started ve failed `482207` dependency'sine bağlı olduğu yeniden doğrulanırsa
iptal edilebilir. Bu exact doğrulamalardan biri tutmazsa submission fail-closed durur. Başka hiçbir
job iptal edilemez.

## 2. Değişmeyen bilimsel reçete

OLMo, Qwen ve SmolLM'nin M2-A/M2-B sibling arm'ları yine exact M1 epoch-036 seed-42 parent'ından
bağımsız başlar. V1 ile birebir aynı olarak her koşu:

- `97,536 × 512 = 49,938,432` model-native token;
- `762` optimizer update;
- microbatch `4 × 32` accumulation = `128` block/update = `65,536` token/update;
- LR `1e-5`, constant-with-warmup, 15 warmup step;
- BF16 AdamW, `foreach=false`, weight decay `0`, gradient checkpointing/clip `1.0`;
- seed/data seed `42`;
- checkpoint `76,152,229,305,381,457,533,610,686,762` kullanır.

Corrected block-family, 250/250 human review, exact parents, üç optimizer-smoke PASS raporu,
storage gate ve tüm measurement precommit alanları v1 ile aynıdır. Outcome-aware recipe,
measurement, threshold, LR, seed, fact, arm veya model değişikliği yasaktır.

## 3. Fresh root ve yeni dar GPU isolation politikası

Tek yeni root:

```text
/vol/tmp2/yesildau/vnd_m2_oscar_scientific_training_recovery_v1
```

Her array task tek allocation içinde exact `gpu:a10080gb:3` ister, fakat scientific training için
yalnız bir GPU seçer. Array `0-5%1` olduğundan altı koşu seridir. Selector:

1. Slurm tarafından allocation'a verilen üç token/UUID'yi ve unique UUID sayısını doğrular;
2. üçünün de total/used/free VRAM ve compute-process ledger'ını atomik JSON'a yazar;
3. `free >= 61,440 MiB` ve `used <= 20,480 MiB` koşulunu geçenler arasından en yüksek free VRAM'i,
   eşitlikte lexicographic en küçük UUID'yi seçer;
4. hiç aday yoksa model load öncesinde exact failure reason ve full ledger ile fail-closed durur.

Foreign process'lere müdahale edilmez. Sıfır-process şartı kaldırılmıştır; yalnız bounded VRAM
şartları geçerli olur. Seçilmeyen GPU'larda training yapılmaz. Bu operasyonel değişiklik,
microbatch/effective batch/precision/optimizer veya bilimsel reçeteyi değiştirmez.

## 4. Kalıcı task audit'i

Her task, selector öncesinde `TRAINING_TASK_LAUNCH`, terminal başarıda `TRAINING_TASK_PASS`, her
non-zero exit'te shell `EXIT` trap üzerinden `TRAINING_TASK_FAIL` kaydını atomik olarak yazar.
Kayıt rol/arm/config/output root, Slurm job/array/task ID, selected GPU, selector-audit SHA ve exit
code taşır. Böylece önceki wave'deki zero-byte stdout/stderr belirsizliği tekrarlanamaz.

## 5. Tek izin verilebilir DAG

```text
exact old-finalizer verification
  -> test-only: preflight + recovery array + finalizer
  -> cancel only never-started 482208
  -> 1 × CPU preflight
  -> afterok 1 × A100 array 0-5%1, each task requests 3 A100 and trains on 1 selected GPU
  -> afterok 1 × CPU checkpoint finalizer + execution-disabled eval-v2 matrix builder
```

Preflight yine en az `386,596,220,128` free byte ve `8,192` free inode ister. Altı run ve 60
checkpoint kapanmazsa finalizer açılmaz. Finalizer yalnız binding manifest ve evaluation-disabled
63-state matrix üretir; inference/scoring çalıştırmaz.

## 6. Implementation identity

| Dosya | SHA-256 |
|---|---|
| scientific plan | `2c8d3aae2a631dc8e1eb7c8bcaccb4dcb300ad3a84d62875520fd62facc94494` |
| preparation v5 | `848fabdddf308e8f5a22156fa431001ebee0f4d4cd2ce7372bc1015e474270a2` |
| recovery config | `055be13c0cafc9fb5aff9b90a6665155c0806033d61a8f96e470c2413f06e046` |
| preflight operator | `2c00e27cb218e284d2e16bd5b73dd4e6303b1817b5f932b95253331ae81b0e66` |
| config generator | `fb00ca7ff7a498b930db7d91034c7d1dc3e4506b110c84c60c84e4ba14d22f98` |
| config validator | `9190bfb25220cd8c951efdcb30d68219e67acbf68a5e65c032a05e7cc4b1d36c` |
| GPU selector | `286e1e419ceb6ba613013a046cbb9c5df8cd18881ea8958279257046e54e1515` |
| task-audit writer | `a0a51b0312c2cca57066e7b2f22b94b0ffd7dbd76bf17514d8026c0fdd62e6a2` |
| submitter | `152722a485d4db58133e87c81fad12fee90726ecea6ab9ce43cbe8d5c41e1a79` |
| preflight Slurm | `51f935b1be254c931efa515cc98c7b0d99bc120ceded4c0ce91437d584f028b9` |
| training Slurm | `4e5f96e4280cccdc18b5a7ff367a0cce02f8a7059c630914325ebd7e5c2598d9` |
| finalizer Slurm | `cbb46d933f0f8e17c04b04db2b7522366e3d8abee47ef25ee50affbd34e73fd7` |
| recovery tests | `927685fc2fe7e205d1870cd5245dc4417dd859ff1a7d55142590f06326a9081f` |

Compatible M2 suite `60/60 PASS`; Python compilation ve Bash syntax PASS'tir.

## 7. Yetki sınırı

Bu hazırlık; push, HU fast-forward, HU/SSH, `482208` iptali, Slurm/GPU, model-weight erişimi,
scientific training, checkpoint, evaluation/scoring, cleanup, deletion, fallback veya automatic
retry yetkisi vermez.

Gelecekte execution için bu belgenin exact SHA-256'sına ve publication commit'ine bağlı açık
kullanıcı yetkisi gerekir. Yetki yalnız ordinary non-force push, preservation-check sonrası HU
fast-forward, koşullu `482208` iptali ve yukarıdaki tek fresh-root DAG'ı kapsayabilir. İkinci wave,
otomatik retry, fallback, evaluation/scoring, cleanup ve deletion yetkisiz kalır.
