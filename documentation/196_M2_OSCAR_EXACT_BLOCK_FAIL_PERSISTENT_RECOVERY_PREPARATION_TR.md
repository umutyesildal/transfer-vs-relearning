# 196 — M2 OSCAR exact block fail-persistent recovery hazırlığı

**Tarih:** 2026-08-30  
**Durum:** `LOCALLY IMPLEMENTED / TESTED / FROZEN / EXECUTION NOT AUTHORIZED`

## Sonuç

Job `481990` tarafından bırakılan terminal partial root korunarak ayrı bir fresh-root recovery
hazırlandı. Yeni çalışma bilimsel M2 tasarımını değiştirmez: aynı OSCAR train/held-out split'i,
aynı epoch-036 OLMo/Qwen/SmolLM tokenizer'ları, aynı 49,938,432 token/arm, aynı 976 replacement ve
aynı seed-42 document order kullanılır.

Yeni recovery'nin iki operasyonel düzeltmesi vardır:

1. Parquet doğrulaması bittikten sonra 5.3 milyon mC4/non-OSCAR belge nesnesi tokenizer aşamasından
   önce bellekten bırakılır.
2. Yaklaşık 50 milyon tokenlık M2-A/M2-B aileleri bellekte çoğaltılmak yerine atomik JSONL
   writer'lara block-by-block stream edilir.

Fixture eşdeğerlik testi yeni streaming writer'ın eski frozen in-memory algoritmayla M2-A,
M2-B, validation, consumed-prefix ve factual-matching audit içeriklerini birebir ürettiğini
doğruladı. Bu bir token-budget veya dose değişikliği değildir.

## Failure persistence

Yeni launcher ve runner aşağıdaki kanıtları fresh root altında kalıcılaştırır:

- submission-prepared ve submission-result kayıtları;
- gerçek Slurm stdout/stderr;
- `/usr/bin/time -v` resource raporu;
- atomik stage/progress kaydı ve Python max-RSS/CPU snapshot'ları;
- Python exception type, message ve bounded traceback;
- shell exit code/job/node audit'i;
- incomplete durumda publish edilmeyen fakat silinmeyen `*.tmp` block evidence.

Bu nedenle Python exception, signal veya role-level failure tekrar oluşursa exact failure boundary
job `481990`'daki gibi sessizce kaybolmayacaktır. Kernel-level hard kill durumunda bile son atomic
progress stage ve Slurm logları korunur. Recovery halen fail-closed ve tek-attempt'tir.

## Doğrulama

- focused compatible suite: `20 passed`;
- streaming M2-A/M2-B equivalence: PASS;
- streaming validation equivalence: PASS;
- insufficient-source atomic non-publication: PASS;
- CPU-only / offline / persistent-log launcher assertions: PASS;
- Python compile, Bash syntax ve `git diff --check`: PASS.

Geniş `tests/test_m2*.py` toplaması local system Python'da `PyYAML` bulunmadığı için dört eski test
modülünde collection aşamasında durdu; dependency mutation yapılmadı. Recovery'nin doğrudan ilgili
20-test compatible set'i ve bağımsız YAML parse doğrulaması tamamlandı.

## Frozen contract

```text
documentation/contracts/corpora/vngrs-m2-oscar-exact-block-materialization-recovery-v1.md
```

Final SHA-256:

```text
d49a221a7b1f8b02682330b4d46762cc57140023a5426f0f5ad77b4d10f8e0d9
```

## Kapı

Hazırlık HU/SSH, push, Slurm veya recovery execution yetkisi vermez. GPU, model weights,
optimizer smoke, M2-A/M2-B training, evaluation, cleanup ve automatic retry kapalıdır. Ayrı exact
SHA-bound kullanıcı yetkisi olmadan fresh root oluşturulamaz ve job gönderilemez.

Recovery PASS verse bile `ready_to_train=false` kalır; fact-registry review, parent weight/config
binding, optimizer smoke ve training/evaluation contract daha sonra ayrı kapılardır.
