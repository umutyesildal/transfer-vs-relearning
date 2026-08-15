# 156a — Pythia Resmî Tokenizer PAD-Default Düzeltmesi ve Tek Retry Kontratı

**Tarih:** 2026-08-11 (Europe/Berlin)  
**Durum:** `FROZEN — READY_FOR_EXACT_USER_AUTHORIZATION — UNEXECUTED RETRY`  
**Önceki kontrat:** Document 156 SHA-256
`0e48ec4882768d92d2a88e75e8d54a7d505d95a1605b015692e31b3b9e5c8985`

## 1. İlk yetkili wave sonucu

Document 156 için verilen exact authorization altında:

- implementation commit `da5715d3f20498b14148cd28d9c069b226cbc537` ordinary non-force push edildi;
- HU checkout, 42 dirty path ve status blob'u değiştirmeden, incoming overlap `[]` ile aynı
  commit'e fast-forward edildi;
- HU targeted test paketi exit `0` ile geçti;
- acquisition preflight job `452542` PASS oldu;
- official-tokenizer acquisition job `452543`, exact immutable source byte'ını indirdi ve preserved
  model hash kontrolünü yürüttü;
- training preflight job `452544`, yanlış V100 GRES selector'ına bağlanmadan önce pending durumda
  iptal edildi.

Job `452543` resmî source veya vocabulary gate'inde değil, tokenizer constructor sonrası şu dar
assertion'da fail-closed oldu:

```text
ValueError: Official Pythia tokenizer unexpectedly defines a PAD token
```

İlk root korunur ve yeniden kullanılmaz:

```text
/vol/tmp2/yesildau/m1_provenance_screen_v3_pythia_repair_v1
```

Bu root'ta yalnız preflight/log/tmp/cache ve exact 2,467,981-byte resmî
`source/20B_tokenizer.json` kanıtı oluştu; composite manifest, tokenizer round-trip PASS, smoke,
training, checkpoint veya evaluation oluşmadı. Cleanup/deletion yoktur.

## 2. Kök nedenin allocated olmayan salt-okunur doğrulaması

HU'nun frozen Transformers `5.13.0` ortamında aynı exact source byte üzerinde üç constructor
varyantı salt-okunur denendi:

| Constructor | Vocab | BOS/EOS/UNK | PAD |
|---|---:|---|---|
| framework default | `50,277` | `0/0/0` | `<|padding|>` / `1` |
| explicit `pad_token=None` | `50,277` | `0/0/0` | `None` |
| `pad_token=None` + explicit BOS/EOS/UNK | `50,277` | `0/0/0` | `None` |

Dolayısıyla source yanlış değildir. Transformers 5.13 sınıf default'u PAD tokenını ID `1` olarak
eklemektedir. `pad_token=None` explicit construction, Document 156'nın frozen beklentisini aynen
sağlar. Training/smoke runtime'ı daha sonra batching için PAD'i EOS'a bellekte eşler; loss labels
üzerindeki padding yine `-100` olur.

## 3. Dar implementation düzeltmeleri

Retry implementationı yalnız şunları değiştirir:

1. `GPTNeoXTokenizerFast(..., pad_token=None)` explicit olur.
2. HU'nun kanıtlanmış Slurm GRES adı kullanılır:

```text
gpu:v10032gb:1
```

3. Dedicated launchers, yeni retry root/registry değerlerini environment override ile alabilir;
   eski root ve ilk-wave logları değiştirilmez.

Model revision, official source commit/URL/bytes/SHA-256, vocabulary, BOS/EOS/UNK, dataset,
training recipe, FP16/GradScaler, V100 runtime identity, gate'ler ve evaluation matrisi değişmez.

## 4. Fresh retry root ve frozen identity

Yeni tek retry root:

```text
/vol/tmp2/yesildau/m1_provenance_screen_v3_pythia_repair_retry_v1
```

Preserved model:

```text
EleutherAI/pythia-1.4b@0da31d8fb309463877ed8c40e54a8f911dced3ec
```

Official tokenizer:

```text
EleutherAI/pythia@1e2365516a3284f18a68c13dbd4ca19fcae59a4b
utils/20B_tokenizer.json
bytes: 2467981
sha256: 56ac4821e129d2c520fdaba60abd920fa852ada51b45c0dd52bbb6bd8c985ade
vocab: 50277
```

Document 156'nın tokenizer file-inventory hash, non-empty probe, offset, full 3.500+500 row,
4.000 hard probe, embedding bound, runtime identity, optimizer smoke ve evaluation gate'lerinin
tamamı değişmeden zorunludur.

## 5. Tek retry zinciri

Exact authorization sonrası yalnız şu yeni-root DAG bir kez submit edilir:

```text
acquisition preflight
  → official tokenizer + composite manifest
  → training preflight
  → V100 FP16 runtime + tokenization + optimizer smoke + 252-update training
  → evaluation preflight
  → base/endpoint evaluation
  → Documents 157/158
```

Her stage `afterok` dependency ile bağlıdır. Her preflight target launcher SHA'sını ve checkout
commitini yeniden bağlar. İlk root salt-okunur kalır; job `452543` resume edilmez. Aynı yeni root
ve job namespace'i için duplicate submission fail-closed'dur.

## 6. Kapsam dışı

Eski root cleanup/deletion, model/source/revision değişimi, scientific recipe remediation,
seed-43, corpus, M2-A/M2-B, OLMo/Falcon retry ve HU-home yazısı kapsam dışıdır. OLMo/Falcon
tamamlanan sonuçları bilimsel gate olarak raporlanır; negatif sonuçları düzeltmek için outcome-aware
recipe değişikliği yapılmaz.

## 7. Exact next authorization request

> Document 156a'nın exact SHA-256'sı kapsamındaki `pad_token=None` ve `v10032gb` local
> implementation/test düzeltmesini, dar ordinary non-force push'u, preservation-checked HU
> fast-forward'u ve fresh retry root altında exactly one acquisition preflight → official
> tokenizer/composite manifest → V100 FP16 smoke/500-fact training → base/endpoint evaluation
> retry zincirini; ayrıca Documents 157/158 result/gate dokümantasyonunu yürütmeni
> yetkilendiriyorum.

