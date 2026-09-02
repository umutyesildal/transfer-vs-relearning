# M2 OSCAR altı-run eğitim tamamlanması, finalizer sıra hatası ve repair hazırlığı

Tarih: 2026-09-02  
Durum: `TRAINING COMPLETE / FINALIZER OPERATIONAL FAILURE / REPAIR FROZEN UNEXECUTED`

## Sonuç

Bir-GPU relocation wave'inin altı scientific training task'i tamamlanmıştır. OLMo, Qwen ve
SmolLM için M2-A ve M2-B sibling arm'larının altısı da `complete`; task audit'lerinin altısı da
`TRAINING_TASK_PASS / exit_code=0` durumundadır. Her run exact on precommitted checkpoint içerir;
toplam 60 checkpoint dizini vardır. Bu nedenle M2-A/M2-B scientific training bitmiştir.

Finalizer job `482233` ise bilimsel eğitimden sonra CPU üzerinde fail-closed olmuştur. Hata:

```text
ValueError: M2 run does not contain exactly the ten precommitted checkpoints
```

Read-only inceleme bunun missing checkpoint olmadığını doğruladı. Trainer path listesini
lexicographic sıraladığı için `checkpoint-76`, numeric listenin ilk elemanı yerine
`checkpoint-686` ile `checkpoint-762` arasında yer almaktadır. Altı manifestin hepsinde exact aynı
on path-set bulunmakta ve her path gerçek dizine karşılık gelmektedir.

## Tamamlanan altı run

| Model | Arm | final train loss | final held-out eval loss | training manifest SHA-256 |
|---|---:|---:|---:|---|
| OLMo | M2-A | 3.080 | 2.940 | `4176bdd6399ba5428ce6847419c6d4e7c2e6a1d36e445eef9cd88e01dd37c632` |
| OLMo | M2-B | 3.062 | 2.940 | `d1d081ff4e28d54451bd1fb6d7ae548ad2f8b051c30309a3282bcc7524b69e59` |
| Qwen | M2-A | 2.852 | 2.774 | `0104cf26fa9fac850054e48421cc6b032df5437abba95f5e72274c495d93b20b` |
| Qwen | M2-B | 2.834 | 2.775 | `ea71fc8c931ea5f3fe605f52f5d11d5b40eef1d5fb1b82cf8b10b39383b3445e` |
| SmolLM | M2-A | 2.205 | 2.149 | `a8a770190ad53736535c72952e3b270644d4551fd6b118cd6a6060fb1874e4c0` |
| SmolLM | M2-B | 2.199 | 2.149 | `649356349de719045b9bf9172119a4f5d69a8e72e4a701c62d06c6e9b49f36e1` |

Bu loss değerleri run bütünlüğü/progress evidence'ıdır; tek başına thesis sonucu veya M2-A/M2-B
karşılaştırma hükmü değildir. Henüz inference/eval-v2 scoring yapılmamıştır.

## Failure sonrası artifact durumu

- training root korunmuş ve read-only kabul edilmiştir;
- `60/60` checkpoint dizini vardır;
- eski `bindings/` dizini vardır fakat tamamen boştur;
- eski `evaluation/` namespace'i yoktur;
- failed finalizer stderr SHA-256:
  `45919ace28181402b4b12c5466fa292b9e75994de1b51a93bb65af6e97a9a2e8`;
- cleanup, deletion, training retry veya evaluation yapılmamıştır.

## Frozen CPU-only repair

Sözleşme:
`documentation/contracts/training/vngrs-m2-oscar-finalizer-numeric-order-repair-v1.md`  
SHA-256: `c30efe60dc76e2701434c0f87ba2cb269d8deeda1ccd3f6f84b7c5194b17054e`

Repair exact path üyeliğini ve tüm dizinleri kontrol ettikten sonra yalnız sıralamayı numeric
precommit sırasına normalize eder. Tek 4-CPU/16G job fresh root altında 6-run/60-checkpoint binding
family ve `60 dense / 12 full / 63 unique scientific state` execution-disabled evaluation matrix
hazırlar. Source training root'a yazmaz; checkpoint model dosyalarını yalnız binding SHA-256 için
read-only tarar ve GPU/model load/training/inference/scoring yapmaz.

Focused suite `6/6`, tüm uyumlu M2 suite'i `66/66` PASS'tir.

## Gate

Scientific training: `COMPLETE (6/6)`.  
Binding/evaluation-matrix finalization: `BLOCKED BY ORDER-ONLY OPERATIONAL VALIDATOR BUG`.  
Repair: `FROZEN / UNEXECUTED`.  
Evaluation/scoring: `NOT AUTHORIZED / NOT STARTED`.

Bir sonraki exact sınır, contract SHA ve publication commit'e bağlı tek CPU finalizer-repair
wave'idir. Bu wave PASS olmadan evaluation execution sözleşmesi açılamaz. Repair PASS olsa bile
evaluation/scoring ayrıca tasarlanmalı, freeze edilmeli ve kullanıcı tarafından yetkilendirilmelidir.
