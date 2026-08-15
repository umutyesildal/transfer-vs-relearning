# Document 167 — M1 Dose/Pareto Post-Falcon RTX A6000 Relocation Gate (TR)

**Tarih:** 2026-08-13, Europe/Berlin  
**Related result:** Document 166  
**Gate:** `BLOCKED — ALLOCATION-TIME GPU CONTAMINATION/LOW FREE VRAM; FAMILY 15/18`

## 1. Recovery gate

Document 165 route preflight ve scheduler `--test-only` gate'leri geçti. Real array exact
`gruenau8/gpu:rtxa6000` allocations aldı; ancak her allocated device 40 GiB minimuma karşı yalnız
3.14 GB free VRAM gösterdi. Runtime guard doğru biçimde evaluator namespace yaratılmadan durdu.

```text
preflight validity          = PASS
scheduler test-only         = PASS
node/GRES allocation        = PASS
allocation free-VRAM gate   = FAIL, 3,142,844,416 < 42,949,672,960
scientific evaluations      = NOT RUN
summary                     = dependency closed / not run
recovery classification     = OPERATIONAL BLOCK
```

## 2. Family gate

```text
required checkpoint rows = 18
available checkpoint rows = 15
missing rows              = falcon {126,210,252}
summary readiness         = false
family decision           = BLOCKED_INCOMPLETE_FALCON_EVALUATION
```

Existing 15 rows ve SHA identities korunmuştur. Falcon trendinden missing PPL/accuracy impute
edilmez.

## 3. Current project decision

```text
selected English-centric M1 model = none
automatic primary promotion       = false
seed43 replication                = CLOSED / NOT AUTHORIZED
Turkish dose ladder               = CLOSED / NOT AUTHORIZED
M2-A/M2-B                         = CLOSED / NOT AUTHORIZED
ready_to_train                    = false
```

Corpus hattında metadata/footer feasibility artık PASS olsa da sample/quality/materialization ve
global measurement-design gate'leri kapalıdır.

## 4. Sonraki gate

Document 165 wave'i tüketilmiştir; automatic retry yoktur. Gelecekte Falcon family completion
ancak yeni exact contract altında, allocation içindeki gerçek per-device process/memory evidence
ile temizliği kanıtlanmış erişilebilir GPU route'u veya scheduler-level exclusive temiz GPU
allocation semantiği dondurularak açılabilir. Sadece missing `126/210/252` task'ları çalışmalı;
training ve existing 15 evaluation tekrar edilmemelidir.

Summary job `456415` dependency-never-satisfied durumundadır. Herhangi bir cancellation/cleanup
ayrı authority gerektirir.

Bu belge yeni retry, job cancellation, GPU relocation, seed-43, M2-A/M2-B, cleanup veya deletion
yetkisi vermez.
