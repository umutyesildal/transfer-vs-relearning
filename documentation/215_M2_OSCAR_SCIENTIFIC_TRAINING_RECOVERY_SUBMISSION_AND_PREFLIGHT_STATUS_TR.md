# 215 — M2 OSCAR scientific training recovery submission ve preflight durumu

Tarih: 2026-09-01
Durum: `AUTHORIZED / SUBMITTED ONCE / PREFLIGHT PASS / TRAINING PENDING RESOURCES`

## Yetki ve publication

Kullanıcı exact SHA-256
`c6f07cdc69003406d2ea44d8bb2c71b9c89ffd4694e224fd708460fb7374da13` olan
`vngrs-m2-oscar-scientific-training-recovery-v1` sözleşmesini ve commit
`a8978b189740449ca3a696753b9dd6a6e7801f3f` için ordinary non-force push, HU preservation-check
sonrası fast-forward, koşullu eski-finalizer iptali ve tek recovery DAG'ını açıkça yetkilendirdi.

Branch ordinary non-force push edildi. HU checkout temiz predecessor
`71fb16a7287120964d9d6e1c1c7ec8602de39f1a` üzerinden yalnız fast-forward ile exact yetkili
commite ilerledi; contract SHA ve clean status yeniden doğrulandı. HU compatible M2 suite
`60/60 PASS` verdi.

İlk preservation komutu, HU fetch refspec'inin remote-tracking ref'i güncellememesi nedeniyle
`origin/...` assertion'ında fail-closed durdu; HEAD ve worktree değişmedi. Read-only teşhis bunu
doğruladı. Düzeltilmiş pass exact `FETCH_HEAD` identity'sini doğrulayıp fast-forward yaptı.

## Eski finalizer ve yeni job kimlikleri

Eski job `482208`; exact `PENDING`, `DependencyNeverSatisfied`, `RunTime=00:00:00`, never-started
ve failed `482207` dependency bağları PASS olduktan, ayrıca üç yeni launcher `sbatch --test-only`
kontrolünü geçtikten sonra iptal edildi. Başka job iptal edilmedi.

- test-only scheduler tahminleri: `482221`, `482222`, `482223`;
- CPU preflight: `482224`;
- serial scientific training array: `482225_[0-5%1]`;
- afterok finalizer/matrix builder: `482226`.

Submission manifest SHA-256:

```text
b58ee935ba04832568b10f18d2f95e8c9f29def87e80472c904c6df4658b6e98
```

## Preflight PASS

Job `482224` terminal PASS üretti. Exact kanıt:

| Artifact | SHA-256 |
|---|---|
| preflight result | `463bd848b362bea8749d8fc2bffae4ee499d0200ef4fbf84400320d7dc281489` |
| config validation | `aaddd1a3c9300f0913cec444717b0f7a27fee621632548b313574afc32f5ae5b` |
| six-config manifest | `8eccf41ee692b6f4d7088d3adb8d2257ca3ba3989ad268326af7060ae09729af` |

Preflight status `M2_SCIENTIFIC_TRAINING_PREFLIGHT_PASS`; canlı scratch
`122,148,408,524,800` free byte ve `2,283,847,062` free inode idi. Corrected block family, exact
parents, üç optimizer-smoke PASS raporu, contract/config identity ve altı regenerated config
kapandı. `training_started=false` preflight için doğrudur.

## Güncel scheduler durumu

İlk preflight-sonrası gözlemde array `482225_[0-5%1]` `PENDING(Resources)` durumundadır. Slurm
backfill tahmini `2026-09-06 13:16:07` başlangıç göstermiştir; bu rezervasyon garantisi değildir ve
kaynak erken boşalırsa task daha erken başlayabilir. Her task aynı node üzerinde üç A100-80GB ister
ve yalnız selector'ın seçtiği bir GPU'da training yapar. Finalizer `482226` dependency-pending'dir.

Henüz model load, scientific token consumption, optimizer update, checkpoint, GPU selector/task
audit veya evaluation matrix yoktur. Wave bir kez gönderildi; duplicate submission, fallback,
ikinci wave ve automatic retry yetkisizdir. Evaluation/scoring, cleanup ve deletion da yetkisizdir.
