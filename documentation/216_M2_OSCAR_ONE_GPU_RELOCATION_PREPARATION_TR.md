# 216 — M2 OSCAR tek-A100 relocation hazırlığı

Tarih: 2026-09-01
Durum: `LOCAL PREPARATION COMPLETE / FROZEN / UNEXECUTED`

Üç-A100 request'inin 5 günlük tahmini kuyruğu incelendi. Her iki A100 node'unda exact iki Slurm GPU
allocated, bir GPU free olduğundan üçlü co-allocation darboğazdır. gruenau10'daki Slurm-free GPU'nun
canlı VRAM'i frozen selector sınırını geçmektedir.

Bilimsel alanları değiştirmeyen fresh-root, gruenau10-bound tek-A100 serial relocation hazırlandı.
Mevcut pending chain yeni exact authorization gelene kadar korunmuştur; iptal/submission yapılmadı.
Focused suite `5/5 PASS`; config science equivalence, Bash syntax ve Python compilation PASS'tir.

Frozen contract SHA-256:

```text
ffea82ac9f9d0bbd9228c13cff7eec9d87c16fd381b92ab35021345413c83792
```
