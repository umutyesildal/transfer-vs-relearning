# M2 OSCAR finalizer numeric-order repair sonucu ve evaluation gate

Tarih: 2026-09-02  
Durum: `PASS / TRAINING FAMILY BOUND / EVALUATION NOT AUTHORIZED`

## Yetki ve publication

Kullanıcı, SHA-256'sı
`c30efe60dc76e2701434c0f87ba2cb269d8deeda1ccd3f6f84b7c5194b17054e` olan
`vngrs-m2-oscar-finalizer-numeric-order-repair-v1` sözleşmesini ve
`b2be734b72829c4dc6d695ff43b4a9bf81796d8d` commitini exact olarak yetkilendirdi. Commit ordinary
non-force push edildi; HU checkout temiz ve fast-forwardable doğrulandıktan sonra
`c15c1232e7dfd2317455abadbd635f136a320b92` üzerinden `b2be734...` commitine fast-forward edildi.
HU checkout execution sonunda da temiz kaldı.

HU `tests/test_m2_*.py` suite'i cache yazmadan `66/66 PASS` verdi.

İlk launcher çağrısı, operatorün contract path'inde `vngrs` yerine `vnd` yazması nedeniyle SHA
kontrolünün ilk satırında durdu. Fresh root ve Slurm job oluşmadığı exact kontrol edildi. Bu olay
scientific/Slurm retry değildir. Doğru exact path ile aynı yetkili single wave bir kez gönderildi.

## Job

- gerçek Slurm job: `483682`;
- route: CPU `longrun`, 4 CPU, 16G;
- node: `gruenau9`;
- gözlenen süre: yaklaşık 13 dakika;
- stderr byte: `0`;
- terminalde `squeue` satırı: `0`;
- `sacct` bu HU oturumunda satır döndürmedi; bu eksik accounting metadata'sıdır, artifact sonucu
  değildir.

`sbatch --test-only` scheduler tahmini `483681` kimliğini yazdı; bu real submitted job değildir.

## Terminal artifact'ler

Fresh root:

```text
/vol/tmp2/yesildau/vnd_m2_oscar_finalizer_numeric_order_repair_v1
```

| Artifact | SHA-256 |
|---|---|
| `control/final_audit.json` | `f33605456a5dcc5521a3da2f307f820b38711de0ab3e753ed3b80b6e4e1253f1` |
| `bindings/family_manifest.json` | `5c8aba3220f03f9ccdd5e14aad6fff98d11cfcb75ffda53ce16db42a7ddcfaa1` |
| `evaluation/eval_v2_matrix.json` | `82373090047b8e52b064fd443cd007af20656d863e246905cebf6fa86a7ae7a9` |
| stderr | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

Terminal kontroller:

- final audit: `M2_FINALIZER_NUMERIC_ORDER_REPAIR_PASS`;
- family: `M2_TRAINING_FAMILY_BINDING_PASS`;
- run sayısı: `6`;
- checkpoint/model-manifest sayısı: `60`;
- per-run checkpoint manifest: `6`;
- matrix: `M2_EVAL_V2_MATRIX_PREPARED_NOT_AUTHORIZED`;
- dense task: `60`;
- full task: `12`;
- unique scientific state: `63`;
- `evaluation_authorized=false`;
- `ready_to_evaluate=false`;
- `source_mutated=false`.

Kaynak training root'taki eski `bindings/` hâlâ boş, `evaluation/` hâlâ yoktur. Training artifact,
checkpoint, parent model veya historical root değiştirilmedi. Cleanup/silme yapılmadı.

## Bilimsel gate

M2 scientific training family artık operasyonel olarak da kapalıdır:

1. OLMo/Qwen/SmolLM × M2-A/M2-B: `6/6 training complete`;
2. precommitted checkpointler: `60/60`;
3. model-only binding family: `PASS`;
4. evaluation task matrix: hazırlanmış fakat execution-disabled.

Bu wave hiçbir inference veya scoring üretmedi. Loss değerleri de tek başına M2-A/M2-B bilimsel
sonucu değildir. Bir sonraki aşama eval-v2 execution adapter/contract'ının frozen 63-state matrixe
bağlanması, offline test edilmesi ve ayrı exact kullanıcı yetkisine sunulmasıdır. Yeni GPU job,
evaluation/scoring, training retry, cleanup veya otomatik retry bu sonuç tarafından açılmaz.
