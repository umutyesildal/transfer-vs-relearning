# M2 OSCAR eval-v2 V1 preflight failure ve V1A repair hazırlığı

Tarih: 2026-09-03  
Durum: `V1 OPERATIONAL NOT-RUN / V1A FROZEN UNEXECUTED`

## V1 publication ve submission

Kullanıcı exact V1 contract ve commitini yetkilendirdi. Commit
`8a2529692a077a3662e46b2227de063330ea88d1` ordinary non-force push edildi; temiz HU checkout
`b2be734...` üzerinden preservation-check sonrası fast-forward edildi. Contract SHA-256
`582b6b6d5f066f96c9fdbc38b6d34eb9e4d83aa15a45d29e5cf07f1ec22331bd` HU'da doğrulandı.
HU focused+compatibility suite `22/22 PASS` oldu.

Storage preflight `121,547,870,175,232` available byte ve `2,283,845,942` available inode gösterdi.
Tek DAG preflight `483719`, array `483720`, finalizer `483721` olarak gönderildi.

## Fail-closed sonuç

CPU preflight `483719`, corpus satırı okunmadan ve held-out output yazılmadan durdu:
`ValueError: accepted shard metadata ledger drift`. Array `483720` hiç başlamadı ve
`DependencyNeverSatisfied`; finalizer `483721` dependency-pending kaldı. Model load, GPU inference,
evaluation ve scientific result sayısı sıfırdır.

V1 root `/vol/tmp2/yesildau/vnd_m2_oscar_eval_v2_execution_v1` tam dört dosya / 80,598 byte içerir.
Önemli SHA-256 değerleri:

- submission manifest: `c58ddd987494c3ca36ff6e1c1f0a527efaa415032747db725b597245f58260a1`;
- task matrix: `3b4bfdc0fdb4cfb423fb4f11bd5a7ee3155e08faae4d3a20a97f189722383fc8`;
- stderr: `39d74329de6ec150ad6f67546a59278d7926f7ae8ba51385f9f659201d179964`;
- stdout: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

## Kök neden ve V1A

V3 Parquet materialization manifesti doğru rootta ve exact hash ile mevcuttur. Accepted source
object ledger ise tasarım gereği ayrı immutable metadata root'undadır. Önceki başarılı
materializerlar `load_source_objects_v3(SOURCE_ROOT)` ve
`load_verified_parquet_documents_v3(SOURCE_V3_ROOT, ...)` ayrımını kullanmıştır; yeni adapter iki
root'u yanlışlıkla tek path kabul etmiştir.

V1A yalnız bu adapter bağını düzeltir. Metadata ledger SHA-256
`6c6f27651945043ec2dfbf1b26575f416b5d38a8783d0a22320f0ffbf83d3fa3` ve 32 satırdır. Yeni fresh
root `/vol/tmp2/yesildau/vnd_m2_oscar_eval_v2_execution_v1a` olarak dondurulmuştur. Bilimsel matrix,
63 task, modeller, checkpointler, ölçümler, bootstrap, A100 kaynakları ve no-retry kuralı değişmez.

Local focused+compatibility suite `23/23 PASS`; compile ve diff-check PASS. V1A contract SHA-256:
`e152dab3ecfb3b54540716b0fd0d7046276c0d8d930797757e66f05616786541`.

Bu hazırlık push, HU fast-forward, `483720/483721` iptali, Slurm/GPU veya evaluation yetkisi değildir.
Exact V1A contract ve exact commit için ayrı kullanıcı yetkisi gerekir.
