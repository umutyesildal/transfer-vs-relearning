# Frozen execution contract — `vngrs-m2-oscar-scientific-training-v1`

Tarih: 2026-09-01
Durum: `FROZEN / UNEXECUTED / EXACT USER AUTHORIZATION REQUIRED`

## 1. Tek amaç

Bu sözleşme, aynı exact M1 epoch-036 parent'larından başlayan altı sibling M2 koşusunu tek
fail-closed wave olarak sınırlar:

```text
OLMo   × [M2-A, M2-B]
Qwen   × [M2-A, M2-B]
SmolLM × [M2-A, M2-B]
```

`M2-A`, temiz Türkçe OSCAR continual-pretraining koludur. `M2-B`, aynı token/update bütçesi ve
aynı generic block ailesi içinde yalnız frozen Branch-B Türkçe fact re-exposure taşır. M2-B,
M2-A'nın devamı değildir; iki kol aynı parent'tan bağımsız başlar. Üç model de zorunludur ve bu
wave tek primary model seçmez.

## 2. Değiştirilemez bilimsel reçete

Her koşu için:

- exact `97,536` × `512` = `49,938,432` model-native token;
- `762` optimizer update;
- microbatch `4` × gradient accumulation `32` = `128` block/update;
- update başına `65,536` token;
- full-sequence causal LM;
- LR `1e-5`, constant-with-warmup, `15` warmup step;
- AdamW, `foreach=false`, betas `0.9/0.999`, epsilon `1e-8`, weight decay `0`;
- BF16, gradient checkpointing, gradient clip `1.0`;
- training/data seed `42`;
- tokenizer extension ve English replay yoktur.

Exact checkpoint update'leri:

```text
76, 152, 229, 305, 381, 457, 533, 610, 686, 762
```

Outcome görüldükten sonra LR, seed, checkpoint, block, fact, threshold, arm veya model değişikliği
yasaktır.

## 3. Exact input zinciri

| Input | SHA-256 |
|---|---|
| readiness final audit | `d8cd44eae03ec1c5b5eea334bf94506417730c30f44dfbfbf6df2bf60a144fc8` |
| epoch-036 parent registry | `b9ada6b7280270d987077b8e1721106ed6a6a0ac78c133dc4150500aaad87823` |
| storage estimate | `51d6ac33db1527c509889964fc61a3af33cbaaf9075beb38c54ee0c0528737e8` |
| corrected block-family manifest | `96f9867c857b08bfd784660331d1a354be7d7c6bc39250091f427fdfaa3c6486` |
| corrected block final audit | `fc2075cbce7f4d51c8013b7977ec64630d2181c8c9ebf30a64f5cab61514e54d` |
| corrected 250-fact human-review validation | `a5e4f04a567de98f85674e8c58e13effe85753738d5de931704e41a153ec20b1` |

Preflight human review için exact `250/250 usable`, unique fact ID ve
`M2_FACT_REVIEW_PASS` alanlarını yeniden doğrular. Corrected manifestteki M2-A/shared-validation
referansları ve corrected M2-B dosyaları yeniden hashlenmeden config üretilemez.

## 4. Önceden tamamlanmış GPU smoke bağları

Yeni smoke çalıştırılmaz. Aşağıdaki immutable PASS raporları read-only doğrulanır:

| Rol | Rapor SHA-256 |
|---|---|
| OLMo | `1ba84c61dccdbf7d6a85d3b96d03435180d7afa4f04100a625030079c801327d` |
| Qwen | `c0b33e389aa9a8544f3354c65a1ba0b4bda206be718d3b3ad09b7d4eb1936009` |
| SmolLM | `05faf4999fe04de49e9bc9ce30f5734584cba63e1ba3043c1dc1453fe1ab1732` |

Her rapor `OPTIMIZER_SMOKE_PASS`, bir optimizer step, `128` block, `65,536` token,
`scientific_training=false`, `checkpoint_written=false` ve exact corrected-family manifest SHA
taşımak zorundadır.

## 5. Fresh root ve storage kapısı

Tek output root:

```text
/vol/tmp2/yesildau/vnd_m2_oscar_scientific_training_v1
```

Root submission öncesi absent olmalıdır. HU home'a output/cache/tmp/checkpoint yazılamaz. Fresh
preflight en az `386,596,220,128` free byte ve `8,192` free inode ister. Tahmin 60 model-only
checkpoint için `190,043,787,340` byte içerir; ayrıca preserved smoke, en fazla üç concurrent
active optimizer state ve headroom uygulanmıştır. Gate geçmezse hiçbir GPU training task'i
başlayamaz.

## 6. Tek izin verilebilir DAG

```text
test-only: preflight + training array + finalizer
  ↓
1 × CPU preflight
  ↓ afterok
1 × A100-80GB array 0-5%3
  ↓ afterok (altı task de PASS)
1 × CPU checkpoint-family finalizer + execution-disabled eval-v2 matrix builder
```

Array sırası lexicographic olarak:

```text
0 olmo/M2-A     1 olmo/M2-B
2 qwen/M2-A     3 qwen/M2-B
4 smollm/M2-A   5 smollm/M2-B
```

Her task tek `gpu:a10080gb:1`, 8 CPU, 64G RAM ve 24 saat sınırındadır; throttle `%3`'tür. GPU
başlangıcında allocated device üzerinde sıfır compute process ve en az 61,440 MiB free VRAM
zorunludur. Bir task fail olursa finalizer açılmaz. Otomatik retry, fallback veya ikinci wave yoktur.

## 7. Measurement precommit ve evaluation sınırı

Training sırasında her exact checkpoint'te validation loss/training trace kaydedilir. Başlangıç
M1 state'i mevcut hash-closed eval-v2 evidence'tan outcome görmeden projekte edilir. Dense ölçüm
paketi tüm on update'te; full paket update `381` ve `762`'de precommit edilmiştir.

Finalizer yalnız altı run ve 60 checkpoint exact kapanırsa:

1. model-only checkpoint manifestlerini üretir;
2. exact `60` dense / `12` full / `3` projected-parent, toplam `63` scientific-state eval-v2
   matrix'ini üretir;
3. matrix'i `execution_adapter_registered=false`, `evaluation_authorized=false` ve
   `ready_to_evaluate=false` bırakır.

Bu sözleşme inference/scoring çalıştırmaz ve evaluation GPU job'u yetkilendirmez. Bunun nedeni
OSCAR held-out BPB ile paired M2-A−M1 / M2-B−M2-A final analyzer'ının checkpoint çıktılarıyla ayrı
hash-bound evaluation sözleşmesinde kapanacak olmasıdır. Ölçüm isimleri, update'leri ve eşikleri
bu arada değiştirilemez. Pile-10k kesinlikle yasaktır.

## 8. Implementation identity

| Dosya | SHA-256 |
|---|---|
| scientific plan | `2c8d3aae2a631dc8e1eb7c8bcaccb4dcb300ad3a84d62875520fd62facc94494` |
| preparation v4 | `716461f75b028540ccdfc584d6307e25300d0d15da571e46c4463342e6670c90` |
| execution config | `5ed389b9afba97d567d6145b88db79dada3d29b18af9af80503ce06b7ecb3b93` |
| preflight operator | `2c00e27cb218e284d2e16bd5b73dd4e6303b1817b5f932b95253331ae81b0e66` |
| config generator | `fb00ca7ff7a498b930db7d91034c7d1dc3e4506b110c84c60c84e4ba14d22f98` |
| config validator | `9190bfb25220cd8c951efdcb30d68219e67acbf68a5e65c032a05e7cc4b1d36c` |
| submitter | `5d160cf3347a9bccf40ef7721f1f07be231143394df4d73acb972a87d409bec0` |
| training-output finalizer | `925cfc51d0c5266e14101e230eb94725343b993981c38eb33dddeea9b32c94e7` |
| output binding library | `9948c88cd149a4f0b21d99747f97f5a555539a842f231c17aec4fd2694294492` |
| eval matrix builder | `c5039f6f6a7f4f0153d47c6562f89d9eaf4405a12f7aadb99fe0dd661ae35ade` |
| eval matrix preparation | `c18fc30ca8afa998bc4db6096e34a80e1afe1e54707ffa70ab24558f79592d05` |
| preflight Slurm | `e52e7a2d8942ecf36ce56246f581c01eb99b9c617b13939457e6a6b36ddc1d69` |
| training Slurm | `253bcf5a4910402fd23eb7907cd6d8cbed736a6445f15c69d667130d2cc98678` |
| finalizer Slurm | `44692ad1c11f7805a882d3d03031b30bc225081cd82262d068a1280e247112cd` |

İlgili training/block/output/measurement suite bu freeze sırasında `57 passed` vermiştir. Bash
syntax ve Python compilation ayrıca PASS'tir.

## 9. Yetki sınırı

Bu belgenin hazırlanması; push, HU fast-forward, HU/SSH, Slurm, GPU, model-weight erişimi,
scientific training, checkpoint oluşturma, inference, evaluation, cleanup veya deletion yetkisi
vermez.

Gelecekteki tek execution yetkisi bu belgenin exact SHA-256'sına ve publication commit'ine açıkça
bağlanmalıdır. Yetki yalnız ordinary non-force push + preservation-check sonrası HU fast-forward,
tek fresh-root preflight, tek `0-5%3` A100 training array ve tek afterok CPU finalizer/matrix-builder
wave'ini kapsayabilir. Evaluation/scoring, cleanup, retry ve fallback ayrıca yasak kalır.
