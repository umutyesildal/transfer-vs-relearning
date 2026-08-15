# Document 151bg — Post-vngrs Single Metadata/Footer Retry Gate (TR)

**Tarih:** 2026-08-12, Europe/Berlin  
**Related result:** Document 151bf  
**Gate:** `BLOCKED — LICENSE REDIRECT SEMANTICS`

## 1. Decision

Document 151be'nin tek authorized invocation'ı connectivity, preservation, prewarm, internal
storage preflight, independent PyArrow writer/parser ve 32-shard metadata/footer request
progression'ını final license request'ine kadar geçti. Immutable README/license route'u frozen
151at vocabulary'sindeki `302` yerine `HTTP 307` döndürdü. Executor doğru biçimde fail-closed
durdu ve ikinci invocation çalıştırılmadı.

```text
decision                  = BLOCKED
operational gate          = blocked_by_operational_access
narrow blocker            = license_route_http_307_not_in_frozen_redirect_vocabulary
global scientific gate    = blocked_by_measurement_design
corpus contributing gate  = blocked_by_corpus_selection_or_materialization
ready_to_measure          = false
ready_to_train            = false
```

## 2. Gate ledger

| Gate | Sonuç |
|---|---|
| Exact 151be authorization | PASS |
| HU connectivity sentinel | PASS |
| Live HEAD/status preservation | PASS |
| Frozen vngrs worktree SHA manifest | PASS, 13/13 |
| Scratch root absence/path | PASS |
| Read-only home/cache prewarm | PASS, 14,691,028,992 bytes |
| Internal 151ax preflight | PASS |
| Independent writer/parser | PASS, PyArrow 24.0.0 |
| Shard request progression | reached all 96 shard HEAD/trailer/footer requests |
| License request | BLOCKED, HTTP 307 |
| Complete artifact package/final audit | NOT REACHED |
| Executor invocation count | exactly 1; consumed |
| Post-run root/storage/home reconciliation | PASS; root absent, 0 files/bytes |

## 3. Bilimsel anlam

Bu sonuç vngrs source veya seçili shardların unavailable olduğunu göstermez. Ayrıca 32 shardın
exact accepted registry'sini, corpus quality PASS'i, sample calibration'ı veya materialization
readiness'i de göstermez. In-memory partial route/footer ilerlemesi complete, self-audited package
yerine kullanılamaz.

vngrs statüsü yalnız `conditional_primary_materialization_candidate` olarak kalır. `trwiki` frozen
cross-domain control, CulturaX `excluded_access_blocked` olarak değişmez.

## 4. Sonraki gate

151be tamamlanmış ve tüketilmiştir; automatic retry yoktur. Gelecekteki herhangi bir retry önce
license/README route'u için immutable identity, method preservation, secret-safe persistence,
logical-attempt/hop/byte accounting ve terminal 307 semantiğini ayrı append-only contract/code/test
düzeltmesinde dondurmalıdır. Sonra yeni exact SHA-bound user authorization gerekir.

Bu belge 151ak sample calibration, 151ah acquisition/materialization, corpus row/full-shard,
model/tokenizer, scoring/evaluation, GPU/Slurm, training, cleanup/deletion veya ikinci executor
invocation yetkisi vermez.
