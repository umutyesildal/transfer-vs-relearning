# 200 — M2 OSCAR exact-block adapter repair execution sonucu ve kapısı

**Tarih:** 2026-08-31  
**Durum:** `EXECUTED ONCE / PASS / EXACT THREE-MODEL BLOCKS MATERIALIZED`

## Sonuç

Kullanıcı, SHA-256'sı
`711deae9853287f9eeea62f35cc397a27a9c3ae3c3f8bbf2f65a8637d647508f` olan
`vngrs-m2-oscar-exact-block-materialization-adapter-repair-v1` sözleşmesini ve exact commit
`b1ec082d0d5f567f76925a251ead67a6bad09118` için ordinary non-force push,
preservation-checked HU fast-forward ve tek fresh-root 4-CPU/64G CPU wave'ini yetkilendirdi.

Commit origin'e ordinary non-force push edildi. HU checkout'unun branch'i, eski HEAD'i
`6c8c7fa039b7c352e7c9be9236b2a6b9db71fd79`, temizliği ve fast-forward ilişkisi doğrulandı;
checkout yalnız `git merge --ff-only` ile exact commite ilerletildi. HU focused suite `12/12`
geçti. Tek gerçek Slurm işi `482027` idi; `482026` yalnız `sbatch --test-only` tahmin kimliğidir.

Job `482027`, `gruenau3` üzerinde `longrun` partition'ında exit 0 ile tamamlandı. Frozen istek
`CPUs/Task=4`, `ReqTRES=cpu=4,mem=64G` idi; Slurm node-granularity nedeniyle `AllocTRES=cpu=8`
ayırdı. Bu ikinci bir iş veya recipe değişikliği değildir.

## Terminal kapanış

Fresh root:

```text
/vol/tmp2/yesildau/vngrs_m2_oscar_exact_blocks_adapter_repair_v1
```

- dosya sayısı: `21`;
- root boyutu (`du -sb`): `2,736,458,613` byte;
- wall time: `16:53.50`;
- peak RSS: `32,820,872` KiB (yaklaşık 31.30 GiB);
- swap: `0`;
- process exit: `0`;
- final status: `EXACT_THREE_MODEL_M2_BLOCKS_MATERIALIZED`;
- `training_opened=false`, `ready_to_train=false`, `model_weights_accessed=false`;
- failure artifact: yok;
- predecessor root mutation: false.

`manifest.json` SHA-256'sı
`68dd7ca18d794c09ce3e1b1aa8b2b4b9f6ddb175195959b24b0103c7ea65dd63` olup
`control/final_audit.json` içindeki exact manifest bağıyla eşleşir. Üç role ait audit hashleri de
manifestteki bağlarla yeniden doğrulandı (`CHAIN=PASS`).

## Bilimsel invariantlar

Üç rolün her biri `TOKENIZER_COMPATIBILITY_PASS` ve `EXACT_MATCHED_BLOCKS_PASS` verdi:

| Rol | train block/arm | token/arm | validation block | replacement block | factual token share |
|---|---:|---:|---:|---:|---:|
| OLMo | 97,536 | 49,938,432 | 2,048 | 976 | 0.0099173118 |
| Qwen | 97,536 | 49,938,432 | 2,048 | 976 | 0.0098721362 |
| SmolLM | 97,536 | 49,938,432 | 2,048 | 976 | 0.0098152461 |

Her rolde M2-A/M2-B block ve token bütçeleri eşittir. Branch-A factual exposure sıfırdır. Exact
250 Branch-B Turkish fact registry hash'i
`784f78a5a182c329b4b995ee1a97c580da994059a18b1f9702ec657569ccbfec` olarak korunmuştur. Split
344,482 train / 10,000 held-out dokümandır ve overlap sıfırdır.

## Terminal hash zinciri

```text
olmo/audit                    20477ee4395f3b11daf6048e1dad141cf6d7107a282af03155a7d6aadbd4ea62
olmo/m2_a_train               f5683fe5414d7079f9df28542068f60f179e1559b403176604d874fa367d665d
olmo/m2_b_train               b7564aec4bd2f676c75174cfd19910ab5ffdcb09c52a484dc2a7ccd59e26b325
olmo/shared_validation        834669c2e936534fc51370577cbf3be107de228591102197face570f1ffa4f54
qwen/audit                    89693e9b01dbe582254116ad227fa154cdd2b596f6fb2b6e2cfd4b9bd64139f7
qwen/m2_a_train               3fc29808b5f1b5b046cddb12c28011e8169067551fd4fe7a1abe1f105cb0360c
qwen/m2_b_train               abe71a0cbecf499ae03e19e06026f5d1f14dbe1a388707ba10d2fbe483b08423
qwen/shared_validation        8b5a973b529ad11a11702534c4d2a27c4cd328c57349c7a9a6cb382967fe7234
smollm/audit                  48726a0106116aadb7042d7508d0f849b0a6edecd0df049bca4a6badc4bd5619
smollm/m2_a_train             a9844e64dfa68872b4f168e654410d0a74e26258fcf58f66c6784e65e9a12688
smollm/m2_b_train             31408f29270bcb28bd7ca85be0b0744fe3fa5e709a413b627717d3299adae193
smollm/shared_validation      598522d808f7e262bfa32f0fd36385585f19d2d73aeb7813ff0eb5a844285835
control/final_audit           7475686c16d8aff55acfa18154cd5b6e686ee7aa1083547e28b6657f1c1b70a6
control/progress              fa34ed83cb5d0a5414203f442d4f3590f99772bdbc64568afd121adfa13196cd
control/slurm stderr          7fc5887a8930651f182b553b020bcd39149c378fde339fe76b32454330f5b540
control/slurm stdout          e2b54f9fa37349f39b51f9ac742c337d85ebd70c3c359b76b155b2b1e7943eb5
control/slurm_exit            0a3e591ede0ea4808313286cd8557b01c74a7ed814cf0a0e3c78b97549e96c10
control/submission_result     2ddd47cfd63489dab1681b3e2cab181d73f813532ec8d95d94c94646a76ce844
control/submission_state      801f406d5edde23c9a3454be45294e5d3e085f34459bd341d63bfa4d03c15b63
facts registry                784f78a5a182c329b4b995ee1a97c580da994059a18b1f9702ec657569ccbfec
manifest                      68dd7ca18d794c09ce3e1b1aa8b2b4b9f6ddb175195959b24b0103c7ea65dd63
```

Stderr'deki tokenizer maximum-length uyarısı model inference/training değildir; tokenization
streami üzerindeki bir library uyarısıdır. Exit 0, tüm role auditleri ve terminal hash zinciri
PASS olduğu için sonucu geçersizleştirmez.

## Kapı

Exact block materialization tamamlandı, fakat bu sözleşme M2 eğitimini açmaz. `ready_to_train`
bilinçli olarak false kalır. Sonraki aşama exact epoch-036 parent weight/config hashlerinin,
memory/optimizer smoke tasarımının ve M1 ile aynı epoch-level measurement matrisinin tek frozen
M2-A/M2-B training/evaluation contract'ında bağlanmasıdır. GPU, model-weight access, optimizer
smoke, training, evaluation, cleanup, deletion ve otomatik retry için yeni exact SHA-bound kullanıcı
yetkisi gerekir.
