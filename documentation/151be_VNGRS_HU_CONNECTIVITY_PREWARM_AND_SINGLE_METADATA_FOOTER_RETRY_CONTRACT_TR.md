# Document 151be — vngrs HU Connectivity, Prewarm and Single Metadata/Footer Retry Contract (TR)

**Tarih:** 2026-08-12, Europe/Berlin  
**Durum:** `FROZEN — UNEXECUTED — EXACT SHA-BOUND AUTHORIZATION REQUIRED`  
**Reserved result/gate:** Documents 151bf/151bg  

## 1. Amaç ve değişmeyen bilimsel durum

Bu belge, Documents 151bc/151bd'de HU read-only bağlantısı remote sonuç döndürmeden kapanan
prewarmed retry'dan sonra hazırlanmış tek, minimal operational retry contract'ıdır. Yalnızca
Documents 151an/151at/151ax ile zaten dondurulmuş vngrs metadata/footer feasibility wave'ini bir
kez çalıştırmayı hedefler.

Bu retry:

- corpus row'u veya full shard indirmez;
- 151ak sample calibration veya 151ah materialization çalıştırmaz;
- model/tokenizer erişimi, scoring, evaluation, GPU/Slurm veya training yapmaz;
- HU home'a yazmaz;
- prior evidence root'larını değiştirmez;
- local/remote Git branch'ine push/fetch/merge/reset/checkout/stash/clean yapmaz;
- mevcut HU dirty/untracked owner state'ini değiştirmez.

Bilimsel kapılar değişmez:

```text
vngrs_status      = conditional_primary_materialization_candidate
quality_pass      = false
selected_corpus   = false
primary_gate      = blocked_by_measurement_design
contributing_gate = blocked_by_corpus_selection_or_materialization
ready_to_measure  = false
ready_to_train    = false
```

## 2. Korunan authority ve exact kimlikler

| Authority | SHA-256 |
|---|---|
| Document 151an | `937ec22c4b0f32d6c15a43ef872e497a0c62266383d46d2e74fca9069f952b79` |
| Document 151at | `d846b3636aa4d55b4fdf95eebf00241ed6c85e6243b3c6a54dbd99bc546576fa` |
| Document 151ax | `b32550966e29f3398239e7be778cb20e3344e427bbec6f664fdda062c0e9eaff` |
| Document 151bc | `376c5e380ba1fa22262626b66b531d19f9333e168a2ffe3c86017b1218726edc` |
| Document 151bd | `c9544bbe410c2d4353ef6b1f1c4c72debd269bb3122d0c0de559b46680d61683` |

Frozen source identity değişmez:

```text
repository         = vngrs-ai/vngrs-web-corpus
immutable_revision = ee5c6201ee84457a18182bfc483a7d8a7f3655ba
split              = train
schema             = text / corpus / original_id
selected_paths     = exact 32-path systematic midpoint set from 151an
selection_sha256   = dbb9714347970634386ff62366384fcae12cf5f12f1df1df676cb9af3ae25686
route_kind         = parquet_footer_range
scratch_root       = /vol/tmp2/yesildau/luna_vngrs_metadata_footer_feasibility_v1
```

## 3. Neden Git synchronization yapılmayacak

Document 151bc'deki son kabul edilmiş HU execution-code hedefi
`92460a00ec136dd885b4940184bee9d954da9106` idi. Local/remote branch daha sonra M1-only
commit'lerle ilerlemiştir. Read-only local karşılaştırmada `92460a...` ile mevcut
`4083158...` arasında aşağıdaki vngrs source/test path setinde diff sıfırdır. Bu nedenle bu retry
HEAD eşitliği veya yeni fast-forward istemez; canlı HU worktree dosyalarının exact SHA-256
manifestini doğrular. Bir byte bile farklıysa executor çalışmaz.

Frozen worktree byte manifest:

```text
a8f6abededf94010e7b28c69501a5abf0cb7c6e76ef513436f0eeae841a52068  src/transfer_vs_relearning/corpora/vngrs/__init__.py
c71742ee18da20aadffad111dae2f3c2774cac9dab329c8dfa4296875df6d297  src/transfer_vs_relearning/corpora/vngrs/contamination.py
eb7fe85852d7b58e9bc673236f731314560949f1a05610a2689901c6ad770b7a  src/transfer_vs_relearning/corpora/vngrs/dedup.py
daff73cc32b6de34bf993f6f30a088b4962081c721b873d530bd514baca9b00c  src/transfer_vs_relearning/corpora/vngrs/manifest.py
e350abaa5bbe79fef77faf2014f42a47636f769158878b1001165e7eaba55720  src/transfer_vs_relearning/corpora/vngrs/metadata.py
89cd24854e52fa7c71bef92f337e3a16509c6cae15aaf1b2b84944e02da40d6e  src/transfer_vs_relearning/corpora/vngrs/metadata_executor.py
35f43ef5c0a9ab46f9bf01582446f129c462ffbb53946f2e9f065f3afb014504  src/transfer_vs_relearning/corpora/vngrs/outputs.py
9ff77c98bac062d6002b892420fad212fe9753d63387785e7b6d36566923fdba  src/transfer_vs_relearning/corpora/vngrs/pipeline.py
4f87deb3279bd8ef4e9d1348a6e38e093d41dc9997ab4175479da95090b40d49  src/transfer_vs_relearning/corpora/vngrs/quality.py
c9ab8dac7f5b77ece1f1371d54b4a8cdab8186ff0f7adadd707846172a871277  src/transfer_vs_relearning/corpora/vngrs/records.py
8c347ece3d02301ab7abf686e2558cf652e38b6faf0e9692d0b2ddb740cc7618  src/transfer_vs_relearning/corpora/vngrs/sampling.py
efd4884c88747dfea72e2da2663773005404bc35ace149664444f40c331a24d1  src/transfer_vs_relearning/corpora/vngrs/split.py
3562185ba5d2828a9bc6531fa386617835396b7df3a804830cd0665651384de7  tests/test_vngrs_preparation.py
```

`metadata.py` ayrıca runtime'da şu literal değerleri taşımaya devam etmelidir:

```text
METADATA_FOOTER_CONTRACT_SHA256 = 937ec22c4b0f32d6c15a43ef872e497a0c62266383d46d2e74fca9069f952b79
METADATA_FOOTER_SCRATCH_ROOT     = /vol/tmp2/yesildau/luna_vngrs_metadata_footer_feasibility_v1
METADATA_FOOTER_MAX_RETRIES      = 24
```

## 4. Tek execution sırası

### 4.1 Bounded connectivity gate

`ssh-client` çalışma dizininden yalnız documented `scripts/hu_ssh_expect` helper'ı kullanılır.
İlk remote komut yalnız `printf HU_READONLY_OK` çalıştırır. Credential içeriği, `.env`, shell trace
veya signed CDN URL hiçbir output'a alınmaz.

Remote sentinel dönmezse veya helper hata verirse:

```text
status       = BLOCKED
phase        = hu_read_only_connectivity
source_calls = 0
```

Yeni helper, fallback host veya ikinci connection route denenmez.

### 4.2 Canlı preservation ve identity gate

Aynı documented route üzerinden birleşik read-only kontrol şunları doğrular:

1. HU repository path'i `/vol/fob-vol6/mi25/yesildau/transfer-vs-relearning`;
2. current HEAD ve branch yalnız evidence olarak kaydedilir; belirli yeni HEAD'e geçiş yapılmaz;
3. canonical `git status --porcelain=v2` byte count, SHA-256 ve entry classes kaydedilir;
4. frozen 13-path manifestinin worktree SHA-256 değerleri Section 3 ile exact eşleşir;
5. bu 13 path status blob'unda dirty/untracked değildir;
6. frozen scratch root execution öncesi absent'tir;
7. resolved root `/vol/tmp2/yesildau` altında, HU home dışında kalır;
8. `df -h` ve `df -i` kontrolleri başarılıdır;
9. HU home write policy `false` olarak kalır.

Bir kontrol eksik, timeout veya mismatch ise prewarm/executor çalışmaz.

### 4.3 Read-only cache prewarm

Önceki 151ba preflight exact-byte `du` timeout verirken hemen sonraki post-run aynı ölçümü
başarıyla tamamlamıştır. Bu retry bu gözlemi execution sonucu olarak değil, yalnız read-only cache
prewarm gerekçesi olarak kullanır.

Executor öncesinde aşağıdaki iki read-only komut bir kez çalıştırılır:

```text
du -x -B1 -s /vol/fob-vol6/mi25/yesildau
find /vol/fob-vol6/mi25/yesildau -xdev -type f -size +500M -printf '%s %p\n'
```

Her biri en fazla 240 saniye ile bounded'dır. Exact-byte `du` tek satır parse edilmeli ve değer
`30 * 1024^3` byte altında olmalıdır. Large-file satırları `{bytes,path}` olarak parse edilir ve
canonical sorted manifest SHA-256 üretilir. Timeout, non-zero exit, parse failure veya home sınırı
ihlali `BLOCKED` üretir. Prewarm sonucu executor'ın kendi 151ax preflight'ının yerine geçmez.

### 4.4 Exactly one executor invocation

Section 4.1–4.3 PASS ise mevcut HU environment ile tam bir kez şu module çalıştırılır:

```text
/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python
  -m transfer_vs_relearning.corpora.vngrs.metadata_executor
  --root /vol/tmp2/yesildau/luna_vngrs_metadata_footer_feasibility_v1
```

Çalışma dizini HU repository root'u, `PYTHONPATH=src` olmalıdır. Executor tekrar kendi exact-byte
120-second `du`, capacity/inode/path/root/large-file preflight'ını ve independent PyArrow
writer/parser self-check'ini çalıştırır. Source erişimi yalnız bu internal preflight ve writer
check PASS sonrasında başlayabilir.

Invocation sayısı sonuçtan bağımsız olarak birdir. BLOCKED veya partial result ikinci invocation,
resume veya replacement path yetkisi vermez.

### 4.5 Post-run evidence

Executor'ın kendi post-run audit sonucu aynen korunur. Ardından yalnız read-only olarak:

- HEAD/status digest;
- frozen 13-path SHA manifesti;
- root file/inode/byte inventory;
- `df -h`/`df -i`;
- prewarm/post large-home-file manifest reconciliation

kaydedilir. Result Document 151bf ve gate Document 151bg append-only oluşturulur. Source-stage PASS
olsa bile post-run audit PASS değilse top-level PASS verilemez.

## 5. Değişmeyen executor sınırları

```text
selected_shards               = exactly 32
base logical requests         = 97
max logical attempts          = 121
max physical HTTP hops        = 242
max retries                   = 24
max total response bytes      = 64 MiB
max single response bytes     = 4 MiB
max output files/new inodes   = 128 / 128
max wall clock                = 7,200 seconds
redirects                     = zero or one validated HTTPS 302 CDN hop
allowed CDN suffixes          = xethub.hf.co / cdn.hf.co
rows/full-shard retrieval     = forbidden
```

Raw signed CDN URL, query values, credentials ve cookies persist edilmez. Cross-host hop'ta
Authorization/Cookie header'ları taşınmaz. Path/revision/route replacement yasaktır.

## 6. PASS/BLOCKED yorumu

`PASS` yalnız bütün 32 shard için exact route/object/footer/byte/license evidence package'i ve
post-run audit geçerse verilir. Bu PASS yalnız metadata/footer feasibility'yi kapatır.

`BLOCKED` bağlantı, preservation, SHA manifest, prewarm, internal preflight, writer check,
route/redirect, byte/retry/file/inode/time bound, parser, evidence graph veya post-run audit
failure'ında verilir. Eksik sonuçlar success olarak tamamlanmaz.

Her iki durumda da:

```text
151ak sample calibration = NOT AUTHORIZED
151ah materialization    = NOT AUTHORIZED
ready_to_measure         = false
ready_to_train           = false
```

### 6.1 Yerel preparation doğrulaması

Hazırlık sırasında `92460a00ec136dd885b4940184bee9d954da9106..4083158` aralığında frozen vngrs
source/test path seti için `git diff --exit-code` PASS vermiştir. Focused vngrs suite:

```text
PYTHONPATH=src python3 -m pytest -o addopts='' -q tests/test_vngrs_preparation.py
82 passed, 2 skipped in 11.27s
```

Local Python environment'da `yaml` bulunmadığı için bütün `tests` collection'ı üç M1 dosyasında
beklenen environment-only import error ile durmuştur. Bu üç dosya exact olarak hariç tutularak
compatible suite sonucu:

```text
PYTHONPATH=src python3 -m pytest -o addopts='' -q tests \
  --ignore=tests/test_m1_cross_family.py \
  --ignore=tests/test_m1_dose_pareto.py \
  --ignore=tests/test_m1_smoke_hash_verification.py
332 passed, 9 skipped in 28.60s
```

Bu local PASS değerleri HU connectivity, prewarm, route veya source evidence değildir ve execution
yetkisi vermez.

## 7. Exact next authorization request

Bir sonraki yetki Document 151be'nin final SHA-256'sına bağlı olarak şunları açıkça kapsamalıdır:

1. documented helper ile bir bounded HU read-only connectivity probe;
2. zero-mutation live HEAD/status/path/hash/root/capacity/inode preservation gate;
3. iki bounded read-only prewarm komutu;
4. yalnız bütün preconditions PASS ise existing exact-byte-verified HU executor'ın tam bir kez
   çalıştırılması;
5. mandatory post-run audit ve yalnız Documents 151bf/151bg'nin append-only hazırlanması.

Bu yetki push/fetch/merge, HU checkout movement, corpus row/full-shard erişimi, sample calibration,
materialization, model/tokenizer, scoring/evaluation, GPU/Slurm, training, cleanup/deletion veya
başka retry yetkisi vermez.
