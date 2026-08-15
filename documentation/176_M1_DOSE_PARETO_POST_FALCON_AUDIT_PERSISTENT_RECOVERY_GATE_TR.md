# Document 176 — M1 Dose/Pareto Post-Falcon Audit-Persistent Recovery Gate (TR)

**Tarih:** 2026-08-13, Europe/Berlin  
**Related result:** Document 175  
**Gate:** `BLOCKED — FOREIGN FOUR-GPU VLLM OCCUPANCY; FAMILY 15/18`

## 1. Recovery decision

```text
preflight                         = PASS
test-only                         = PASS
exclusive four-GPU allocation    = PASS
failure audit persistence        = PASS
clean candidate                  = none
deterministic UUID selection     = not available
runtime/model/evaluation         = NOT RUN
recovery wave                    = consumed
```

Document 174'ün metodolojik düzeltmesi başarılıdır: no-candidate sonucu artık exact dört-device
ledger ile açıklanabilir. Dört A6000 aynı foreign VLLM tensor-parallel workload tarafından yaklaşık
45.25 GiB/device kullanıldığı için clean predicate'i karşılamadı. Slurm `idle`/exclusive allocation
bu cluster'da Slurm dışı veya allocation accounting'ine yansımayan GPU process temizliği anlamına
gelmemektedir.

## 2. Family/project gate

```text
required rows               = 18
available rows              = 15
missing                     = Falcon {126,210,252}
summary                     = not generated
selected English-centric M1 = none
automatic promotion         = false
ready_to_train              = false
```

## 3. Next operational gate

Bir sonraki continuation aynı `gruenau8 --exclusive` yolunu körlemesine tekrar etmemelidir. Exact
ledger, bunun deterministic code bug değil external capacity/ownership problemi olduğunu gösterir.
İlerleme için önce cluster yöneticisi/iş sahibi tarafından VLLM workload'un meşru yaşam döngüsü ve
gerçek temiz-capacity penceresi doğrulanmalı veya ayrı bir kontratta gerçekten erişilebilir temiz
bir GPU route'u dondurulmalıdır. Foreign PID sonlandırmak, workload'a müdahale etmek veya mevcut
threshold'u gevşetmek yasaktır.

Mevcut Falcon training ve 15 cheap row tekrar edilmemelidir. Summary `456595` dependency-dead
kalmıştır; cancellation ayrı authority gerektirir. Bu belge retry, job cancellation, GPU reroute,
seed-43, precision/LR/threshold/recipe change, Turkish dose ladder, M2-A/M2-B, cleanup veya deletion
yetkisi vermez.
