# 156 — Pythia-1.4B Resmî Tokenizer Repair ve Tek Execution Kontratı

**Tarih:** 2026-08-11 (Europe/Berlin)  
**Durum:** `FROZEN — READY_FOR_EXACT_USER_AUTHORIZATION — UNEXECUTED`  
**Kapsam:** yalnız `EleutherAI/pythia-1.4b` için resmî GPT-NeoX-20B tokenizer bağlama,
tokenizer/masking audit, V100 FP16 smoke, donmuş 500-fact M1 training ve base/endpoint evaluation

## 1. Gerekçe ve tarihsel sonucu koruma

Document 155'teki Pythia acquisition, exact model revision'ını indirdi; fakat snapshot tokenizer
vocabulary byte'larını içermedi. `AutoTokenizer` iki-token bir nesne üretti ve dört non-empty
probe için boş ID/mask/offset/decode döndürdü. Eski validator empty-to-empty round-trip'i yanlış
PASS saydı. Pythia training/evaluation GPU başlamadan iptal edildi ve terminal sınıfı doğru olarak:

```text
NOT_RUN_MASKING_COMPATIBILITY_GATE
```

Bu kayıt değiştirilmez. Bu kontrat yeni bir bilimsel recipe veya weight revision fallback'i değil;
aynı dondurulmuş ağırlıkları Pythia'nın kendi resmî eğitim tokenizerına bağlayan ayrı ve açıkça
etiketli bir compatibility repair'dir.

## 2. Değişmeyecek model ve korunan kanıt

| Alan | Frozen değer |
|---|---|
| Model | `EleutherAI/pythia-1.4b` |
| Requested/resolved revision | `0da31d8fb309463877ed8c40e54a8f911dced3ec` |
| Input embedding row | `50,304` |
| Preserved model root | `/vol/tmp2/yesildau/m1_provenance_screen_v3/models/EleutherAI__pythia-1.4b` |
| Preserved snapshot | aynı root altında `0da31d8fb309463877ed8c40e54a8f911dced3ec` |
| Preserved manifest | aynı model root altında `model_manifest.json` |

Preserved snapshot, manifest, false-positive access record ve eski Pythia subtree'lerine hiçbir
byte yazılamaz. Repair yalnız yeni root'ta çalışır:

```text
/vol/tmp2/yesildau/m1_provenance_screen_v3_pythia_repair_v1
```

OLMo/Falcon aktif veya tamamlanmış zincirleri bağımsızdır; iptal, duplicate submission veya artifact
değişikliği bu kontratın dışındadır.

## 3. Resmî tokenizer kaynağı

Pythia'nın resmî deposu bütün Pythia modellerinin GPT-NeoX-20B tokenizerını kullandığını ve
training reproduction için `utils/20B_tokenizer.json` dosyasının kullanılmasını belirtir:

- [EleutherAI/Pythia resmî deposu](https://github.com/EleutherAI/pythia)
- [Resmî tokenizer geçmişi](https://github.com/EleutherAI/pythia/commits/main/utils/20B_tokenizer.json)
- [Pythia paper](https://arxiv.org/abs/2304.01373)

Frozen source identity:

| Alan | Frozen değer |
|---|---|
| Repository | `EleutherAI/pythia` |
| Commit | `1e2365516a3284f18a68c13dbd4ca19fcae59a4b` |
| Path | `utils/20B_tokenizer.json` |
| Immutable URL | `https://raw.githubusercontent.com/EleutherAI/pythia/1e2365516a3284f18a68c13dbd4ca19fcae59a4b/utils/20B_tokenizer.json` |
| Exact bytes | `2,467,981` |
| SHA-256 | `56ac4821e129d2c520fdaba60abd920fa852ada51b45c0dd52bbb6bd8c985ade` |
| Download ceiling | `3,145,728` bytes |
| Expected vocabulary length | `50,277` |
| BOS/EOS/UNK | `<|endoftext|>` |
| PAD | source'ta yok; runtime batching sırasında EOS'a eşlenir ve kaydedilir |

Yalnız bu tek URL ve tek response indirilebilir. Redirect, non-200, byte/hash/size farkı veya ceiling
aşımı fail-closed'dur. Community tokenizer, Pythia-v0 fallback'i, başka model revision'ı ya da
Hugging Face `main` üzerinde hareketli kaynak kullanılamaz.

## 4. Composite manifest ve provenance

Repair executor:

1. preserved model manifestteki model ID ve requested/resolved revision'ı doğrular;
2. manifestte listelenen bütün preserved model dosyalarının SHA-256 değerlerini yeniden doğrular;
3. resmî tokenizer byte'larını yeni root'a yazar ve SHA-256/byte/route evidence üretir;
4. `GPTNeoXTokenizerFast` ile resmî byte'lardan tokenizer oluşturur;
5. yeni root'ta offline save/reload round-trip yapar;
6. preserved weight path/hash'leri ile yeni `tokenizer_source_path_absolute` alanını birleştiren
   ayrı composite `model_manifest.json` üretir.

Tokenizerın gerçekten yüklendiği save-pretrained klasöründeki bütün dosyalar exact relative-path
+ SHA-256 inventory'sine bağlanır. Tokenization audit, smoke, training ve base/endpoint evaluation
bu inventory'yi her yüklemeden önce yeniden doğrular; eksik, ek veya hash'i değişmiş dosya
fail-closed'dur. Raw source SHA-256 tek başına loaded-tokenizer integrity kanıtı sayılmaz.

Original manifest yeniden yazılmaz. Training/evaluation model ağırlıklarını preserved exact
snapshot'tan, tokenizerı yalnız yeni repair root'undan offline yükler.

## 5. Zorunlu tokenizer ve masking gate'leri

Training açılmadan önce bütün gate'ler geçmelidir:

1. Tokenizer fast olmalı ve offset mapping desteklemelidir.
2. Vocabulary `50,277` olmalı; `>2` ve `<=50,304` şartları ayrıca doğrulanmalıdır.
3. Her non-empty frozen probe için input IDs, attention mask, offsets ve decoded text non-empty
   olmalı; üç dizinin uzunlukları eşit olmalıdır.
4. Token ID üst sınırı model embedding row sınırının altında olmalıdır.
5. Save/reload öncesi ve sonrası ID, mask, offset, decode, vocabulary ve special-token ID'leri
   birebir aynı olmalıdır.
6. Donmuş 3.500 training row ve 500 validation row'un tamamı audit edilir: length `<=128`,
   supervised-token count `>0`, truncation `0`.
7. Frozen 4.000 A/B/C/D × direct/QA hard probe ayrıca tokenizer/length gate'inden geçirilir.
8. Gerçek V100 forward/backward/AdamW step'i finite loss, finite/non-zero gradient, FP16
   GradScaler ve checkpoint save/reload ile geçmelidir.

Shared validator ayrıca boş tokenizerın tekrar PASS olmasını engellemek üzere bütün adaylar için
non-empty probe ve meaningful-vocabulary kontrolü kazanır.

## 6. Frozen training recipe ve V100 compatibility

Bilimsel recipe Document 152a ile aynıdır:

| Alan | Değer |
|---|---:|
| Dataset | 100 subject / 500 semantic fact / 3.500 English training row |
| Seed / data seed | `42 / 42` |
| Epoch | `36` |
| Microbatch × accumulation | `10 × 50 = 500` |
| Optimizer update | `252` |
| LR | `5e-5` |
| Scheduler | `constant_with_warmup`, warmup ratio `0.02` |
| Loss | answer-only |
| EOS supervision | `false` |
| Block size | `128` |
| Checkpoint | yalnız update 252 endpoint |

Pythia-1.4B V100 üzerinde FP16 + GradScaler ile çalıştırılır. Bu değişiklik açık compatibility
koşuludur; dataset, effective batch, update, LR, epoch, loss veya endpoint değişikliği değildir.
Yalnız daha önce actual V100 üzerinde doğrulanmış scratch runtime kullanılır:

```text
/vol/tmp2/yesildau/m1_provenance_screen_v3/compat_envs/torch260_cu124_v1/bin/python
```

Runtime `sm_70`, CUDA availability, V100 compute capability ve finite FP16 probe'u yeniden
doğrulanmadan Pythia smoke/training başlamaz.
Dedicated Pythia training/evaluation launcherları exact Python executable, Torch
`2.6.0+cu124`, GPU adı `Tesla V100-PCIE-32GB`, capability `7.0`, compiled `sm_70` ve finite FP16
forward/backward koşullarını fail-closed doğrular; generic A100 default'una sessiz düşüş yasaktır.

## 7. Tek execution zinciri

Exact authorization sonrası sıra:

```text
local tests + narrow commit/push
  → preservation-checked HU ff-only
  → frozen-reference/no-home-write + scratch/path/inode/capacity/queue preflight
  → official tokenizer retrieval + composite manifest
  → full tokenizer/dataset/hard-probe audit
  → V100 FP16 optimizer smoke
  → 252-update Pythia training
  → base + endpoint evaluation
  → artifact/hash/storage audit
  → Document 157 result + Document 158 gate
```

Tek bir Pythia zinciri submit edilir. Aynı namespace'te mevcut Pythia job/root varsa, checkout
dirty overlap varsa, source/preserved hash değişirse, yeni root mevcutsa, scratch/env HU home'a
resolve olursa veya duplicate job bulunursa durulur.

Shared HU checkout'ta eski commit'e bağlı OLMo/Falcon downstream preflight/evaluation job'ı queued
veya running iken fast-forward yapılamaz. Önce bu job'lar terminal ve artifact durumları doğrulanır;
bu kontrat aktif sibling zincirini bozma pahasına publication yapmaz. Ayrı checkout/worktree bu
kontratın otomatik fallback'i değildir.

Home ağacı tekrar recursive `du` ile taranmaz. Document 152b'nin `14,689,423,360` byte frozen
referansı ve no-home-write politikası kullanılır; `df`, inode, resolved path, root absence ve
post-run audit yine zorunludur.

## 8. Evaluation ve sonuç sınıfı

Base ve update-252 endpoint için aynı frozen matrix çalışır: 500 exact, 4.000 hard suite,
eight-cell robust/relation/binding kontrolleri, WikiText-2 PPL ve generic integrity. Document
152a'nın eşikleri değişmez. Terminal sınıf yalnız şunlardan biri olabilir:

- `COMPLETED_PASS`;
- `COMPLETED_FAIL_<SCIENTIFIC_GATE>`;
- `NOT_RUN_<ACCESS_OR_COMPATIBILITY_GATE>`;
- `INVALID_INFRASTRUCTURE_RUN`.

Başarılı repair, eski `NOT_RUN` kaydını silmez; onu yeni ve provenance-açık bir execution sonucu
ile tamamlar. Tek seed screening sonucu otomatik model seçimi veya seed-43 yetkisi vermez.

## 9. Çıktılar ve kapsam dışı işler

Zorunlu çıktılar: tokenizer source/route/hash evidence, composite manifest, tokenization audit,
smoke manifest, training manifest/update-252 model-only endpoint, base/endpoint evaluation,
machine-readable gate ve artifact inventory. Cleanup yoktur.

Kapsam dışı: OLMo/Falcon iptali veya retry'ı, eski root yazısı, corpus işi, seed-43, 2.500/25.000
fact, M2-A/M2-B, publication, cleanup/deletion ve HU-home durability copy.

## 10. Exact next authorization request

Bu kontratın hazırlanması Pythia repair execution'ını henüz başlatmaz. Bir sonraki kullanıcı
yetkisi Document 156'nın exact SHA-256'sına bağlı olarak şu kapsamı vermelidir:

> Document 156'nın exact SHA-256'sı kapsamındaki local implementation/test'i, dar ordinary
> non-force push'u, preservation-checked HU fast-forward'u, yeni scratch root'a bounded resmî
> tokenizer retrieval'ını, frozen-reference/no-home-write preflight'ini ve exactly one Pythia
> tokenizer audit → V100 FP16 smoke → 500-fact training → base/endpoint evaluation zincirini;
> ayrıca append-only result/post-gate dokümantasyonunu yürütmeni yetkilendiriyorum.
