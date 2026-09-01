# Frozen execution contract — `vngrs-m2-oscar-scientific-training-recovery-1gpu-relocation-v1`

Tarih: 2026-09-01
Durum: `FROZEN / UNEXECUTED / EXACT USER AUTHORIZATION REQUIRED`

## Amaç ve exact trigger

Recovery preflight `482224` PASS olmasına rağmen training array `482225_[0-5%1]`, her task aynı
node'da üç A100 istediği için `PENDING(Resources)` kalmış ve Slurm 6 Eylül tahmini vermiştir.
Read-only node ledger'ı gruenau10 ve gruenau9 üzerinde üç karttan ikisinin Slurm-allocated,
birinin Slurm-free olduğunu doğrulamıştır. gruenau10'daki free kartın canlı görünümü
`78,342 MiB free / 2,811 MiB used` olup frozen güvenlik sınırını geçmektedir.

Bu sözleşme yalnız hiç başlamamış `482225` ve dependency-pending `482226` job'larını exact
`PENDING`, runtime `00:00:00` ve zero scientific artifact kontrolünden sonra iptal edip tek fresh
root altında bir-GPU relocation açabilir. Eski recovery root'u read-only kalır.

## Değişmeyen bilim

V1/recovery ile exact aynı input, parent, corrected block, optimizer-smoke, training ve measurement
alanları korunur: üç model × M2-A/M2-B, her arm `49,938,432` token, `762` update, microbatch `4`,
accumulation `32`, BF16 AdamW, LR `1e-5`, seed `42`, aynı on checkpoint ve aynı 63-state
execution-disabled evaluation matrix precommit. Recipe/threshold/outcome-aware değişiklik yoktur.

## Tek operasyonel değişiklik

Fresh root:

```text
/vol/tmp2/yesildau/vnd_m2_oscar_scientific_training_recovery_1gpu_relocation_v1
```

Tek DAG: CPU preflight → serial `0-5%1` array → afterok CPU finalizer. Her task exact
`--nodelist=gruenau10`, `gpu:a10080gb:1`, 8 CPU, 64G ve 24h ister. Mevcut atomik selector/audit
korunur; allocated tek GPU ancak `free >= 61,440 MiB` ve `used <= 20,480 MiB` ise kullanılır.
Geçmezse model load öncesi persistent failure audit ile durur. Automatic retry/fallback yoktur.

## Cancellation ve synchronization sırası

1. `482225` ve `482226` exact pending/never-started ve eski root'ta training artifact sıfırdır;
2. yalnız bu iki job iptal edilir;
3. HU checkout `a8978b1` üzerinde clean doğrulanır;
4. publication commit'e preservation-check sonrası fast-forward yapılır;
5. HU tests ve üç `sbatch --test-only` PASS olursa tek fresh-root DAG gönderilir.

Bir assertion saparsa yeni submission yoktur. Foreign process müdahalesi, cleanup ve deletion yoktur.

## Implementation identity

| Dosya | SHA-256 |
|---|---|
| preparation v6 | `298a63655c19a2f220bc08375cab45943045fa527cac5183f313472c87d897fd` |
| relocation config | `ea59deb8d5e2a6794d4bd50ce380e08dc94b41cca40cfe967eb34e2f4a9b09ff` |
| selector | `286e1e419ceb6ba613013a046cbb9c5df8cd18881ea8958279257046e54e1515` |
| task audit | `a0a51b0312c2cca57066e7b2f22b94b0ffd7dbd76bf17514d8026c0fdd62e6a2` |
| submitter | `87c9a0063debea3fd196ef47dea7c56366a7a6438dff7242782cb6f6faef46ea` |
| preflight Slurm | `bf1d62495ed493eeda7c6cbfe6bb956cc1732ef76ce03cf34e1325e42808ea58` |
| training Slurm | `c23d4cfc228b556ed8d4dbae79764c8272f5f080e24b8e517598e8cfe07431dd` |
| finalizer Slurm | `8a0b2a7bcc784d75ba7d3de9192231c54fedda6d5f7a320616e4c458d8b53b0e` |
| focused tests | `bf23483e7e066c0c503a61a3623f546daf42d3230773cfb9911f7d6d39b75c2a` |

Focused relocation/recovery suite `5/5 PASS`; Bash syntax, Python compilation ve science-field
equivalence PASS'tir.

## Yetki sınırı

Hazırlık push, HU fast-forward, job cancellation, Slurm/GPU, model access, training veya checkpoint
yetkisi vermez. Exact contract SHA ve publication commit'e bağlı yeni kullanıcı yetkisi gerekir.
Evaluation/scoring, cleanup, deletion, ikinci relocation, fallback ve automatic retry yasaktır.
