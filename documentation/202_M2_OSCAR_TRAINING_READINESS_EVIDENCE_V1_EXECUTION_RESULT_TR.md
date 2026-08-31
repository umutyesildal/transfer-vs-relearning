# 202 — M2 OSCAR training-readiness evidence v1 execution sonucu

**Tarih:** 2026-08-31  
**Durum:** `EXECUTED ONCE / TERMINAL BLOCKED / NO RETRY AUTHORIZED`

## Sonuç

Exact contract SHA-256
`071252e2c1477f4fbc5e7d132a2bc0f418f2e51ee57120641f7de57bbcec1168` ve commit
`e6be7bf824a119f969d7490c293197908ba36015` kullanıcı tarafından yetkilendirildi. Commit ordinary
non-force push edildi; HU checkout temiz preservation-check sonrasında exact commite fast-forward
edildi. HU focused suite `67/67` ve exit 0 geçti.

`482034` yalnız Slurm test-only tahminidir. Tek gerçek iş `482035` idi. İş 2.21 saniyede exit 1 ile
fail-closed durdu. GPU, optimizer smoke, training veya evaluation çalışmadı.

## Exact hata

```text
ValueError: olmo: parent manifest has no file hash registry
```

Kök neden veri eksikliği değildir. Üretim `epoch-036.json` model manifestleri compact bağlardır;
`checkpoint_sha256`, exact `local_path_absolute` ve training identity taşırlar, fakat
`file_hashes` alanı taşımazlar. Exact `{path, bytes, sha256}` dosya registry'si bağlı
`epoch-036/snapshot_manifest.json` içindedir. V1 runner yanlış şema katmanından okumuştur.

## Terminal root

```text
/vol/tmp2/yesildau/vngrs_m2_oscar_training_readiness_evidence_v1
```

- 5 dosya / 14,971 byte;
- `control/slurm_exit.json`: `BLOCKED`, exit 1;
- parent registry, storage estimate, configs, review packet/HTML, evidence manifest ve final audit
  üretilmedi;
- stderr SHA-256:
  `e31ebce25931b74eda597610a6dfb65bf8879c78dff3e59713adfa49ec2cd118`;
- slurm-exit SHA-256:
  `29f49bf6beb885d0990dbdfe041d945b4f2eaad6149d85d2e978f6e772b6bdcd`.

Root immutable/read-only terminal evidence olarak korunur. Yetkili wave tüketilmiştir; automatic
retry yoktur.

## Kapı

`ready_to_train=false` kalır. Yeni deneme yalnız compact model-manifest ile snapshot-manifest
arasındaki checkpoint identity'sini doğrulayıp exact dosya registry'sini snapshot manifestten
okuyan, fresh root kullanan ayrı SHA-bound repair contract ile mümkündür.
