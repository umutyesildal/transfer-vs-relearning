# Frozen execution contract — `vngrs-m2-oscar-finalizer-numeric-order-repair-v1`

Tarih: 2026-09-02  
Durum: `FROZEN / UNEXECUTED / EXACT USER AUTHORIZATION REQUIRED`

## Amaç ve bilimsel durum

Bir-GPU relocation array'i `482232_[0-5%1]` altı scientific training task'ini de tamamladı.
Altı `training_manifest.json` kaydı `complete`, altı task audit'i `TRAINING_TASK_PASS`, toplam
checkpoint dizini sayısı 60'tır. Eğitim sonucu veya checkpoint kaybı yoktur.

Afterok CPU finalizer `482233`, trainer'ın `checkpoint_dirs` alanını lexicographic sırada yazması
nedeniyle fail-closed durdu. Örneğin `checkpoint-76`, lexicographic listede `checkpoint-686` ile
`checkpoint-762` arasındadır; finalizer ise numerik precommit sırasını bekliyordu. Altı manifestin
her biri exact aynı on checkpoint yolunu içerir ve her yol gerçek dizindir. Bu sözleşme yalnız bu
order-only validator uyuşmazlığını düzeltir.

## Immutable source evidence

Kaynak root salt okunurdur:

```text
/vol/tmp2/yesildau/vnd_m2_oscar_scientific_training_recovery_1gpu_relocation_v1
```

Wave başlamadan önce config manifest, preflight, submission result, failed-finalizer stderr, altı
training manifest ve altı task audit dosyası
`configs/training/m2_oscar_finalizer_numeric_order_repair_v1.yaml` içindeki exact SHA-256
değerlerine göre doğrulanır. Ayrıca:

- kaynak `bindings/` dizini var ve tamamen boş olmalıdır;
- kaynak `evaluation/` namespace'i yok olmalıdır;
- 60 checkpoint dizininin tamamı var olmalıdır;
- job `482232` ve `482233` Slurm kuyruğunda aktif olmamalıdır;
- hiçbir kaynak artifact yazılmaz, taşınmaz veya silinmez.

## Exact repair semantics

Validator önce manifest listesinin uzunluğunu, exact path-set üyeliğini ve her path'in dizin
olduğunu doğrular. Ancak bu üç kontrol geçtikten sonra liste frozen numeric sıraya normalize edilir:

```text
76, 152, 229, 305, 381, 457, 533, 610, 686, 762
```

Yeni çıktı root'u:

```text
/vol/tmp2/yesildau/vnd_m2_oscar_finalizer_numeric_order_repair_v1
```

Tek `std`, 4-CPU, 16G, 8h job şu çıktıları fresh root altında üretir:

1. altı run / 60 checkpoint model-only binding family;
2. 60 task / 12 full task / 63 unique scientific-state eval-v2 matrix;
3. hash-closed terminal `control/final_audit.json`.

Evaluation matrix yalnız hazırlık artifact'idir. Terminal koşul
`evaluation_authorized=false` ve `ready_to_evaluate=false` olmalıdır. Checkpoint model dosyaları
yalnız model-only manifest SHA-256 değerlerini hesaplamak için read-only byte stream olarak okunur;
parent model okunmaz, hiçbir model load/inference/scoring yapılmaz, GPU istenmez ve scientific
training yeniden çalıştırılmaz.

## Implementation identity

| Dosya | SHA-256 |
|---|---|
| repair config | `c3212c1d683dd32cd5349ccf49126bdcfc2b5997237c039a7ec64ae9b344450f` |
| numeric-order validator | `8d58a3b69c36add587e8dd9d1d78082ffdc690f36ba2e6d24f8b4c08ddd4c30c` |
| bounded runner | `712bfca0c6190086c65364f254ef13753e14ce66727fdb3c46de6db0d56a005c` |
| submitter | `953e0bebeeb8dbc1c9699afe5148dbb8c5745b50331180cd0a29da9edae3a3c7` |
| Slurm launcher | `4bdf5e78951562f6b442c03b9de53a724f118a54581f9434690518782b392ad3` |
| output regression tests | `371266c350f08792f78dd9237093578e084d46104c90092a5a01a18b5ac9cff7` |
| contract tests | `10ca4448b995515f69fb1e84717e14c8f1b5d83e70928395f4e0423cc7d1e08e` |

Focused tests `6/6 PASS`; compatible `tests/test_m2_*.py` suite `66/66 PASS`; both Bash files pass
`bash -n`.

## Fail-closed ve yetki sınırı

Contract/config/commit/hash, clean checkout, source evidence, checkpoint membership, old empty
namespace, fresh-root ve duplicate-job kontrollerinden biri saparsa real `sbatch` yoktur. Bir kez
submission yapıldıktan sonra ikinci job, automatic retry veya fallback yoktur.

Bu hazırlık push, HU fast-forward veya Slurm yetkisi vermez. Exact contract SHA-256 ve publication
commit'e bağlı ayrı kullanıcı yetkisi gerekir. GPU, parent-model access, model load/inference,
training, evaluation, scoring, cleanup, deletion ve automatic retry yetkili değildir. Yalnız
tamamlanmış checkpoint dosyalarının binding hash'leri için read-only erişim contract kapsamındadır.
