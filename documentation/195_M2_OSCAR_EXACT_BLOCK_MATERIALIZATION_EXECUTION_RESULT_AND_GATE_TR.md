# 195 — M2 OSCAR exact block materialization execution sonucu ve kapısı

**Tarih:** 2026-08-30  
**Durum:** `TERMINAL PARTIAL / BLOCKED BEFORE TOKEN BLOCK PUBLICATION / NO RETRY AUTHORIZED`

## Sonuç

SHA-256'sı
`f8abbd417e7dd82f524c3691872bb40c4efb9a1988f1920ad363bd1c6cd4dc1c` olan
`vngrs-m2-oscar-exact-block-materialization-v1` sözleşmesinin kullanıcı tarafından yetkilendirilen
tek CPU wave'i bir kez tüketildi. Commit
`9cdf149a88a822df123f8af890b489b62a0d1953` ordinary non-force push edildi; HU aktif checkout'u
temiz preservation-check sonrasında aynı commit'e fast-forward edildi.

Submitter'ın frozen input hash, clean checkout, duplicate-job, kapasite/inode ve Slurm test-only
kapıları geçti. Test-only çıktısındaki `481989` yalnız scheduler tahmin kimliğidir; gerçek tek iş
`481990`'dır. Scheduler işi altı saatlik time limit nedeniyle `longrun` partition'ına yönlendirdi.
İş 2026-08-30 16:01:06 CEST'te `gruenau3` üzerinde `RUNNING` olarak doğrulandı.

İlk heartbeat kontrolünde iş artık `squeue` içinde değildi ve sorgu `Invalid job id specified`
döndürdü. `sacct` terminal metadata sorgusu HU'nun mevcut Munge/SlurmDBD authentication arızası
nedeniyle yine kullanılamadı. Buna rağmen scratch çıktısı işin PASS olmadığını kesin olarak
gösterir:

- output root: `/vol/tmp2/yesildau/vngrs_m2_oscar_exact_blocks_v1`;
- toplam dosya: `1`;
- root toplam boyutu: `114,186` byte (`du -sb`);
- üretilen tek dosya: `facts/branch_b_turkish_facts.jsonl`;
- fact satırı: `250`;
- fact dosyası: `105,994` byte;
- fact SHA-256: `784f78a5a182c329b4b995ee1a97c580da994059a18b1f9702ec657569ccbfec`;
- block dosyası: `0`;
- model-role audit'i: `0`;
- terminal `manifest.json`: **yok**.

Dolayısıyla hiçbir OLMo/Qwen/SmolLM M2-A, M2-B veya shared-validation token block'u yayımlanmadı.
Bu wave `EXACT_THREE_MODEL_M2_BLOCKS_MATERIALIZED` PASS'i değildir ve `ready_to_train=false`
kalır.

## Fail-closed yorum

Runner, fact registry'yi tokenizer döngüsünden hemen önce atomik olarak yazar. Tek kalıcı dosyanın
bu registry olması, son dayanıklı sınırın source/split/fact kontrollerinden sonra fakat ilk
model-role block/audit publication'ından önce olduğunu gösterir. Slurm stdout/stderr submitter
tarafından `/dev/null`'a yönlendirildiği ve `sacct` kullanılamadığı için exact exception veya
terminal state kanıtı mevcut değildir. OOM, tokenizer load veya packing hatası gibi bir neden
kanıt olmadan atanamaz; trigger **unresolved operational failure** olarak kaydedilir.

## Mevcut kapı

- Tek yetkili wave tüketildi; otomatik veya manuel retry yetkisi yoktur.
- Partial root immutable/read-only terminal evidence olarak korunacaktır; cleanup/silme yoktur.
- GPU, model ağırlığı, optimizer smoke, M2-A/M2-B training ve evaluation açılmadı.
- Training preparation ve eval-v2 matrix local/non-executable hazırlık olarak kalır.
- Yeni bir deneme ancak fresh root kullanan, terminal exception/log ve atomic failure audit'i
  kalıcılaştıran ayrı SHA-bound recovery contract'ı ve yeni kullanıcı yetkisiyle yapılabilir.

## Bilimsel sınıflandırma

Bu sonuç bir model veya corpus kalite sonucu değildir. Token-block materialization tamamlanmadığı
için M2 eğitimi hakkında bilimsel çıkarım üretmez. Sınıf:
`OPERATIONAL_TERMINAL_PARTIAL_BEFORE_BLOCK_PUBLICATION`.
