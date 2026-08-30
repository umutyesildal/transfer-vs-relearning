# 193 — M2 üç-model training hazırlığı implementasyonu

**Tarih:** 2026-08-30  
**Durum:** `LOCAL IMPLEMENTATION PASS / NON-EXECUTABLE / TRAINING NOT AUTHORIZED`

## Kısa sonuç

Exact OSCAR block materialization wave'i yetki beklerken, onun başarılı çıktısından sonra gereken
training hazırlık katmanı local olarak implement edildi. Bu katman:

- exact block family manifestini;
- exact OLMo/Qwen/SmolLM M1 epoch-036 parent registry'sini;
- frozen Document 191 bilimsel planını

birlikte doğrulamadan hiçbir training config üretmez.

Başarılı preparation tam altı config üretir:

```text
OLMo   × [M2-A, M2-B]
Qwen   × [M2-A, M2-B]
SmolLM × [M2-A, M2-B]
```

Her modelin iki arm'ı aynı parent manifest ve aynı validation block hash'ine, fakat farklı train
block hash'ine sahip olmak zorundadır. Altı config de `pretokenized=true`, full-sequence CLM,
512 token, LR `1e-5`, BF16, seed 42, 762 update ve exact effective batch 128 block kullanır.

## Exact checkpoint düzeltmesi

Document 191'in yaklaşık her %10 dose noktaları uniform değildir:

```text
76, 152, 229, 305, 381, 457, 533, 610, 686, 762
```

Dolayısıyla yalnız `save_steps=76` kullanmak yanlış scientific states üretirdi. CLM trainer'a
explicit `checkpoint_updates` callback'i eklendi. Callback yalnız frozen update kimliklerinde
save/eval açar; liste unique/ascending/positive olmalı, exact endpoint 762'yi içermeli ve
`save_total_limit` hiçbir precommitted state'i silememelidir.

## Memory route ve DAG sınırı

Local candidate decomposition her model için `microbatch=4 × accumulation=32 = 128 block/update`
olarak tutuldu. Bu bilimsel reçete değişikliği değildir ve yalnız A100-80GB optimizer smoke ile
doğrulanırsa kullanılabilir. OLMo/Qwen/SmolLM için üç teknik smoke görevi seri; bunlar PASS olursa
altı sibling training görevi en fazla üçlü paralellikle açılabilecek bir `afterok` DAG iskeletine
bağlandı.

Submitter ayrıca exact commit, clean checkout, config-manifest status, exact execution-contract
SHA-256 ve açık `M2_TRAINING_AUTHORIZATION_ACK` olmadan job göndermez. Launcher'lar scratch-only
log/cache/tmp kullanır. Herhangi bir fallback veya retry ayrı contract gerektirir.

## Local doğrulama

İlgili training/block/control-plane birleşik suite: `77 passed`.

Kapsam:

- üç model × iki arm identity matrix;
- exact sibling parent/validation eşliği ve ayrı train hash'leri;
- exact 762-update recipe ve 10 non-uniform checkpoint;
- effective batch 128;
- preparation/validator end-to-end fixture;
- unmaterialized block ve incomplete parent fail-closed kapıları;
- üç-model optimizer-smoke ve altı-run training launcher Bash syntax;
- exact contract/authorization guard;
- önceki exact block/fact invariants.

## Hâlâ tamamlanması gerekenler

Bu kayıt training readiness iddia etmez. Sırayla:

1. Document 192'nin exact block CPU wave'i ayrı kullanıcı yetkisiyle çalışmalı;
2. 250-row Turkish Branch-B registry bounded insan review'undan geçmeli;
3. exact M1 parent weight/config hashes read-only registry'de yakalanmalı;
4. output storage/runtime estimate dondurulmalı;
5. üç optimizer smoke gerçek GPU'da PASS olmalı;
6. eval-v2 dense/full checkpoint DAG adapter'ı exact materialized/training manifestlerine bağlanmalı;
7. bütün sonuçlar yeni SHA-bound M2 training contract'ında dondurulmalı;
8. ancak bundan sonra kullanıcı training'i ayrıca yetkilendirebilir.

Bu dosya, preparation config'i veya launcher'lar HU/SSH, GPU, model ağırlığı erişimi, training,
evaluation, cleanup ya da otomatik retry yetkisi vermez.
