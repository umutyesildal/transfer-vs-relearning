# Document 164 — M1 Dose/Pareto Post-Falcon-Recovery Gate (TR)

**Tarih:** 2026-08-12, Europe/Berlin  
**Related result:** Document 163  
**Gate:** `BLOCKED — GUPPI5 PARTITION ACCESS; FAMILY STILL 15/18`

## 1. Recovery gate

Document 162 preflight'leri scientific/artifact inventory bakımından geçti. Ancak frozen
`guppi5` target'ı current scheduler'da `wbimlgpu` partition'ında ve kullanıcı grubu bu partition'a
job gönderme yetkisine sahip değil. İlk partition mismatch'i dar implementation correction ile
giderilmiş olsa da corrected submission allocation öncesi authorization gate'inde reddedildi.

```text
preflight validity        = PASS
scheduler target identity = PASS, guppi5 exposes RTX3090
partition group access    = FAIL
evaluation array created  = no
summary job created       = no
scientific result         = NOT RUN
recovery classification  = OPERATIONAL BLOCK
```

## 2. Family gate

OLMo ve Pythia'nın altışar, Falcon'ın yalnız üç cheap gate'i korunmuştur. Missing Falcon
checkpoint `126/210/252` değerlendirmeleri yoktur ve summary root absent'tir.

```text
required checkpoint rows = 18
available checkpoint rows = 15
missing rows              = falcon {126,210,252}
summary readiness         = false
family decision           = BLOCKED_INCOMPLETE_FALCON_EVALUATION
```

Bu blocker Falcon modelinin scientific negative sonucu değildir. Existing Falcon 42/84/168
PPL trendi missing row'lara taşınmaz ve imputation yapılmaz.

## 3. Current project decision

```text
selected English-centric M1 model = none
automatic primary promotion       = false
seed43 replication                = CLOSED / NOT AUTHORIZED
Turkish dose ladder               = CLOSED / NOT AUTHORIZED
M2-A/M2-B                         = CLOSED / NOT AUTHORIZED
ready_to_train                    = false
```

Corpus hattındaki measurement-design ve materialization blocker'ları bu sonuçla değişmez.

## 4. Sonraki gate

Document 162'nin bounded wave'i kapanmıştır; automatic retry yoktur. Gelecekte family completion
ancak yeni frozen contract ve exact SHA-bound kullanıcı yetkisi altında şu iki seçenekten biriyle
açılabilir:

1. `guppi5/wbimlgpu` için gerçek scheduler group access sağlanıp execution-time erişim preflight'i
   dondurulur; veya
2. outcome-blind, clean ve kullanıcı tarafından erişilebilir başka RTX3090 node/partition route'u
   exact olarak dondurulur.

Her iki durumda da yalnız missing `126/210/252` task'ları çalıştırılmalı; existing 15 row,
training, model/data/LR/seed/threshold ve summary `afterok` semantiği değişmemelidir.

Bu belge yeni Slurm submission'ı, node/partition relocation, evaluation, summary, seed-43,
M2-A/M2-B, cleanup veya deletion yetkisi vermez.
