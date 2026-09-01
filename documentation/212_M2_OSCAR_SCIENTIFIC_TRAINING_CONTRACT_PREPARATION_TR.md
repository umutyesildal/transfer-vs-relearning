# 212 — M2 OSCAR scientific training sözleşmesi hazırlığı

Tarih: 2026-09-01
Durum: `FROZEN / UNEXECUTED / READY FOR EXACT AUTHORIZATION`

## Sonuç

OLMo, Qwen ve SmolLM'nin M2-A/M2-B sibling kollarını kapsayan altı-run scientific training wave'i
yerel olarak tamamlandı ve fail-closed bir execution sözleşmesinde donduruldu:

```text
documentation/contracts/training/vngrs-m2-oscar-scientific-training-v1.md
SHA-256: 748e2aae5c7e3ec95acaf639e4536e6024686e5a854ad09dc6013feb47490222
```

Bu preparation hiçbir HU/Slurm/GPU işi çalıştırmadı ve model ağırlıklarına erişmedi.

## Kapanan boşluklar

- Eski readiness config'lerinin superseded M2-B bloklarına bağlı olması düzeltilmiştir. Fresh CPU
  preflight, exact corrected manifestten altı config'i yeniden deterministik üretir.
- Corrected `250/250 usable` insan kararı, corrected block manifest/final audit, exact epoch-036
  parent registry ve üç immutable optimizer-smoke PASS raporu training öncesi yeniden doğrulanır.
- Altı task exact `49,938,432` token, `762` update, BF16, AdamW, seed 42 ve aynı effective batch
  reçetesine bağlıdır.
- Checkpointler `76,152,229,305,381,457,533,610,686,762` update'lerinde zorunludur.
- Tek fresh scratch root, en az `386,596,220,128` free byte / `8,192` inode ve no-home-write
  kuralları dondurulmuştur.
- Tek DAG: CPU preflight → `0-5%3` A100-80GB training array → afterok CPU finalizer.
- Finalizer altı run/60 checkpoint'i hash-kapatır ve precommitted `60 dense / 12 full / 3 parent`
  olmak üzere 63-state eval-v2 matrix'i üretir.
- Otomatik retry, fallback, second wave, cleanup ve outcome-aware recipe/measurement değişikliği
  yoktur.

## Evaluation sınırı

Metrik isimleri, dense/full update'leri ve eşikler training öncesi dondurulmuştur. Buna rağmen bu
contract inference/scoring çalıştırmaz. Üretilen matrix `execution_adapter_registered=false` ve
`evaluation_authorized=false` kalır. OSCAR held-out BPB ve paired sibling analyzer'ı, training
çıktıları mevcut olduktan sonra ayrı SHA-bound evaluation sözleşmesinde kapanacaktır. Böylece
measurement design outcome'a göre değiştirilemez, fakat training yetkisi evaluation yetkisine
sessizce genişlemez.

## Yerel doğrulama

- ilgili M2 training, output, eval-matrix ve checkpoint suite: `57 passed`;
- genişletilmiş compatible `tests/test_m2_*.py + test_training_core.py` suite: `105 passed`;
- yeni Python preflight: compilation PASS;
- submitter ve üç Slurm dosyası: `bash -n` PASS;
- `git diff --check`: PASS.

## Sonraki tek karar

Sözleşme artık exact authorization için hazırdır. Execution öncesi bu local implementation
ordinary non-force push edilmeli, HU checkout preservation-check sonrası exact commit'e
fast-forward edilmeli ve yalnız sözleşmedeki tek fresh-root wave açıkça yetkilendirilmelidir.
Hazırlık tek başına push, HU, Slurm, GPU, training, checkpoint veya evaluation yetkisi değildir.
