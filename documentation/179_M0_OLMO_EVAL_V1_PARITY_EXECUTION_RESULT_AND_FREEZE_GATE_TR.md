# 179 — M0 OLMo eval-v1 parity execution result and freeze gate

**Tarih:** 2026-08-16, Europe/Berlin  
**Durum:** `PARITY PASS — QUALIFICATION COMPLETE — EVAL-V1 FREEZE STILL OPEN`

## 1. Hüküm

OLMo test-only qualification paketi için açık kalan iki parity kapısı kapandı:

| Kapı | Sonuç |
|---|---|
| `wikitext_count_result_and_heading_parity` | PASS |
| `turblimp_16_subtask_macro_parity` | PASS |

Bu sonuç OLMo qualification sürecini `qualified_for_eval_v1_freeze_review` durumuna getirir. Bilimsel
M0 evaluation yapılmadı; bu sayılar scientific model karşılaştırmasına veya tez sonuç tablosuna
giremez. eval-v1 de henüz frozen değildir.

## 2. Korunan ilk v1 girişimi

İlk parity root'u, GPU route probe ve `sbatch` çağrısından önce structural validator'da durdu.
WikiText PASS olurken, validator TurBLiMP `acc_norm` denominator'ını yanlış biçimde UTF-8 bayt
uzunluğu olarak yorumladı ve `0.34375` hesapladı. Pinned lm-eval v0.4.12 `api/task.py` ise:

- `acc_norm` için Python `len(choice)` Unicode string uzunluğunu;
- ayrı `acc_bytes` için UTF-8 bayt uzunluğunu

kullanır. TurBLiMP task'ı `acc_norm` yayınlar, `acc_bytes` yayınlamaz. Bu nedenle ilk fark model
sonucu değil validator hatasıdır.

Korunan v1 kanıtı:

- root: `/vol/tmp2/yesildau/eval_v1_m0_olmo_qualification_parity_v1`;
- dosya/bayt: 406 / 413,897,338;
- Slurm job: 0;
- structural SHA-256:
  `8bf52585239d6bd61f076ba09a4a8814755d78a46e74fed598081a7a4273e370`;
- plan SHA-256:
  `d9bee3dda03942767dd12bc567a21e4712207bed45b133839abbe39a6e6a6554`.

V1 root değiştirilmeyecek ve yeniden kullanılmayacaktır.

## 3. Dondurulmuş v2 düzeltmesi

V2 yalnız upstream denominator semantiğini geri yükledi, `task.py` hash'ini input identity'ye
ekledi ve byte-normalized değeri açıkça descriptive sensitivity olarak ayırdı.

- implementation commit: `cb48fddadcbaa1e6ef145d6be7d7568359723573`;
- operator SHA-256:
  `bfe2832517f214059539f5cb97763a92407ad9efe62cad98e4ea640f349b9380`;
- parity module SHA-256:
  `a7d66c49224828ed997a29f0e8caeefd0cce93c3ad97351a8188d30fffdcbda0`;
- corrected config SHA-256:
  `b855225f13355989877e988e90f8049df790ce0e244348417b42fb31054920b5`;
- upstream `api/task.py` SHA-256:
  `310d5e10c44a3e66683db374a4be955bee8b697ab9675a47a12bd8330e085784`;
- root: `/vol/tmp2/yesildau/eval_v1_m0_olmo_qualification_parity_v2`.

Local tam suite 461/461, HU hedefli suite 16/16 geçti. Exact HU preflight'ın bütün blocker listesi
boştu.

## 4. Execution ledger

| İş | Job | Route | Sonuç |
|---|---:|---|---|
| WikiText heading sensitivity | `461668` | `gruenau1`, V100-32GB | complete, return code 0 |
| afterany finalizer | `461669` | `std` | parity PASS |

Runtime free-memory guard 17,179,869,184 bayt minimuma karşı 33,740,357,632 bayt gözledi. Heading
job süresi 84.92 saniyeydi. `sacct` son kontrol sırasında çıktı vermedi; tamamlanma durumu immutable
run/finalizer artifact'larından doğrulandı.

## 5. WikiText canonical parity

Aynı iki doküman için upstream target detokenization, raw-page word/byte denominator'ları,
log-likelihood toplamı, sample count ve result aggregation yeniden hesaplandı.

| Alan | Recomputed | Harness | Fark |
|---|---:|---:|---:|
| word count | 5,844 | 5,844 | 0 |
| byte count | 30,207 | 30,207 | 0 |
| log-likelihood sum | -15,134.0 | -15,134.0 | 0 |
| word PPL | 13.325301724411347 | 13.325301724411347 | 0 |
| byte PPL | 1.6503868248492586 | 1.6503868248492586 | 0 |
| BPB | 0.722804209249961 | 0.722804209249961 | 0 |

Mutlak parity tolerance `1e-12` idi.

## 6. Heading sensitivity

Canonical `= heading =` satırları, aynı depth'i koruyan Markdown başlıklarına dönüştürüldü. İki
dokümanda sırasıyla 8 ve 13 heading satırı değişti; doc identity, transform, denominator ve result
aggregation kontrollerinin tümü geçti.

| Metric | Canonical | Markdown | Markdown − canonical |
|---|---:|---:|---:|
| word PPL | 13.325301724411347 | 21.499387361604374 | 8.174085637193027 |
| byte PPL | 1.6503868248492586 | 1.6814614213798644 | 0.031074596530605847 |
| BPB | 0.722804209249961 | 0.7497156787619479 | 0.026911469511986863 |

Bu fark için sayısal PASS/FAIL eşiği yoktur. Canonical upstream WikiText primary kalır; Markdown
varyantı yalnız formatting sensitivity'dir.

## 7. TurBLiMP parity

Exact 16 subtask sırası ve her subtask için iki sample yeniden hesaplandı. Upstream YAML'daki iki
`aggregate_metric_list` anahtarı gözlendi; YAML'nin effective son anahtarı yalnız `acc_norm`dur.

- recomputed Unicode-length-normalized 16-subtask macro `acc_norm`: `0.40625`;
- Harness reported macro `acc_norm`: `0.40625`;
- descriptive UTF-8-byte-normalized macro sensitivity: `0.34375`;
- group sample count: 32;
- absolute parity difference: 0.

Bu ayrım gelecekte normalizer'ın `acc_norm` ile byte sensitivity'yi karıştırmasını engeller.

## 8. Frozen artifact identities

- `parity_result.json`:
  `b50b5d2282464fa5890a11297550502753daaf39708b9ed9eff5e1a269ae266e`;
- `parity_results.jsonl`:
  `378a2ef869831e1a9368f310343459fc31324c6339ecf0b9e8c4adca4aea02e1`;
- `structural_parity.json`:
  `6e426841d43c3484ff53cb50a099cac7491c7fd4df0e0c257bd357b88e7a1667`;
- `heading_sensitivity.json`:
  `267007f163c7267345b9fe812a7e6dfd6fccbfefb253e340060df02fddce5ae3`;
- `parity_manifest.json`:
  `7f6396e3b41fe63127915fd5622373fe9545c545caf77689f6a3f921bb00ae55`;
- `submission_manifest.json`:
  `80469138c9d9893abdf61bfaae6aebc0d7805cad1590f42c08777060b069dcff`;
- `final_inventory.json`:
  `683f5bd5158a28bf23b0d23bfa0d6710fe3e0d4373c60bc35bd884d7138a4c20`;
- final inventory: 422 files / 414,036,276 bytes.

## 9. Current gate

Qualification parity is complete. eval-v1 freeze still requires, at minimum:

1. exact scientific dataset revisions/content manifests;
2. final scientific environment binding;
3. Pile-10k runtime/cadence decision;
4. TurkishMMLU include/exclude decision;
5. frozen cheap factual panel IDs/hash;
6. precommitted numeric acquisition/retention/manipulation/non-inferiority margins; and
7. per-training-contract checkpoint binding rule.

No scientific M0 config, three-model M0 run, M1/M2 training, corpus materialization, retry, cleanup
or deletion follows automatically from this PASS.
