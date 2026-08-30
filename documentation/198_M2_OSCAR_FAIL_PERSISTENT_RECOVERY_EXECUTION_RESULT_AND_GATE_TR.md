# 198 — M2 OSCAR fail-persistent recovery execution sonucu ve kapısı

**Tarih:** 2026-08-31  
**Durum:** `TERMINAL BLOCKED / EXACT ADAPTER INTERFACE FAILURE / NO RELOCATION OR RETRY`

## Sonuç

Yetkili CPU recovery job `482007`, 00:30 kontrolünden önce çalışmış ve terminal `BLOCKED` duruma
gelmiştir. Bu nedenle pending-only Document 197 relocation koşulu artık sağlanmaz; job hold/cancel,
HU fast-forward veya 4-CPU submission yapılmamıştır.

Fail-persistent düzeltme amacına ulaşmış ve exact failure ilk kez kalıcılaştırılmıştır:

```text
exception_type: AttributeError
message: 'FrozenTokenizerAdapter' object has no attribute 'eos_token_id'
stage: stream_train_blocks
role: olmo
node: gruenau4
exit_code: 1
```

`FrozenTokenizerAdapter` tokenizer'ı `.tokenizer` alanında taşır ve `encode()` metodunu proxy eder,
fakat adapter üzerinde doğrudan `eos_token_id` property bulunmaz. Yeni streaming helper adapter'ı
tokenizer-benzeri kabul edip doğrudan bu eksik property'yi okuduğu için OLMo train-block stream'i
başlamadan durmuştur. Bu bir corpus, tokenizer asset, model veya bilimsel recipe sonucu değildir.

## Kaynak ölçümü

Persistent `/usr/bin/time -v` ve progress kayıtları:

- elapsed wall time: `14:23.19`;
- maximum RSS: `32,807,744 KiB` (yaklaşık `31.29 GiB`);
- average allocated-CPU utilization: `%47` of the 8-CPU allocation;
- user CPU: `359.66 s`;
- system CPU: `52.27 s`;
- swap: `0`.

Bu kanıt job `482007` için 128G RAM'in fazlasıyla yeterli olduğunu ve OOM yaşanmadığını kapatır.
Yaklaşık 3.8 CPU eşdeğeri ortalama kullanım, gelecekteki separately contracted 4-CPU route'un
makul olduğunu destekler; tek başına execution yetkisi vermez.

## Terminal artifact closure

Root: `/vol/tmp2/yesildau/vngrs_m2_oscar_exact_blocks_recovery_v1`

- files: `8`;
- total root bytes: `123,392`;
- fact registry: 250 rows / 105,994 bytes / SHA-256
  `784f78a5a182c329b4b995ee1a97c580da994059a18b1f9702ec657569ccbfec`;
- block files: `0`;
- terminal family manifest: absent;
- progress SHA-256: `2badd02ca329ea7ce4ef5808981746fbd3e85bc88d29a4f01f15b1b24d69af38`;
- failure SHA-256: `1ce489502583f900a039e1776e67d4d2992d945405d49cfac3bf385a93c799d7`;
- shell-exit SHA-256: `e427d45ca3e911b5c11b5a77b703e8ffdfa2f4192095e63a180155a3b0bbf914`;
- stderr SHA-256: `0e48d7e87d46078a5b8acc91e4e55a349dda2b1ecc0b1578a8d1df5e420de821`.

## Gate

- Job `482007` authorization is consumed.
- Document 197 pending-only relocation is now ineligible and remains unexecuted.
- Both recovery roots are immutable/read-only terminal evidence; cleanup/deletion is forbidden.
- `ready_to_train=false`; no model weights, GPU, optimizer smoke, training or evaluation ran.
- Any adapter-interface repair requires a fresh root, regression test, separately frozen contract
  and new exact SHA-bound user authorization.

Job `481990` remains historically unresolved because it did not persist its exception. The matching
durable boundary makes this adapter defect a plausible explanation, but Document 195 is not
retrospectively rewritten to claim evidence that did not exist there.
