# 180 — eval-v1 bilimsel girdi ve protokol freeze

**Tarih:** 2026-08-16, Europe/Berlin  
**Durum:** `EVAL-V1 FROZEN — EXECUTION NOT AUTHORIZED`

## 1. Hüküm

Document 179'daki OLMo qualification/parity PASS sonrasında açık kalan eval-v1 tasarım girdileri
kapatıldı. Aynı `eval-v1` ölçüm semantiği M0, M1, M2-A ve M2-B için kullanılacaktır. Task, metric,
denominator, cadence, probe, threshold veya confidence kuralındaki bilimsel değişiklik `eval-v2`
gerektirir.

Bu freeze bilimsel M0 evaluation, HU/Slurm/GPU, training, corpus materialization, push, cleanup veya
deletion yetkisi vermez. Model/checkpoint/output/route binding'i olan ayrı bir execution contract ve
ayrı kullanıcı yetkisi gerekir.

## 2. Final LM Evaluation Harness seti

Harness v0.4.12 commit `6d642546f4688648fced259eb3302efd36ece5af` altında final sekiz task
ID'si şunlardır:

```text
wikitext
pile_10k
blimp
hellaswag
winogender_female
winogender_male
winogender_neutral
turblimp_core
```

TurkishMMLU dataset kartı erişim için yazarlarla iletişim gerektirdiğinden exact erişilebilir
revision freeze edilemedi ve eval-v1'den çıkarıldı. XCOPA-TR reserve durumundan freeze öncesi
promote edilmedi. İkisinin sonradan eklenmesi eval-v1 uyumlu sayılmaz.

## 3. Exact environment ve dataset identity

Qualification'da çalışan environment bilimsel environment olarak değişmeden bağlandı:

- root: `/vol/tmp2/yesildau/eval_v1_envs/lm_eval_v0_4_12_torch260_cu124_v3`;
- lock SHA-256: `f9238f731fe3286aa0f5e5934f2b559a4202794d43cea4b9b00b2960b37ee942`;
- identity SHA-256: `9061cbc59d021676ca6b768f7688eb7da10e5460bf4919b963c9931eefcc7d71`;
- Python 3.11.15, Torch 2.6.0+cu124, Transformers 5.13.0, Datasets 5.0.0,
  Accelerate 1.14.0.

Scientific execution yalnız offline/read-only cache kullanır:

- cache root: `/vol/tmp2/yesildau/eval_v1_m0_olmo_qualification_v8/cache`;
- `HF_HOME`: aynı root altında `huggingface`; datasets cache: `huggingface_datasets`;
- content manifest: 404 dosya / 413,883,554 bayt;
- manifest SHA-256: `0bd32f84bcf94b8208b35a32cdb9a0e311e7ba005392a7557f80c316d0dfd7fb`;
- offline reload: PASS.

Frozen dataset revisions:

| Task family | Repository | Revision |
|---|---|---|
| WikiText | `EleutherAI/wikitext_document_level` | `647234772b9554e208af6c826f23b99e3cac88c8` |
| Pile-10k | `NeelNanda/pile-10k` | `127bfedcd5047750df5ccf3a12979a47bfa0bafa` |
| BLiMP | `nyu-mll/blimp` | `877fba0801ffb7cbd8c39c1ff314a46f053f6036` |
| HellaSwag | `Rowan/hellaswag` | `218ec52e09a7e7462a5400043bb9a69a41d06b76` |
| WinoGender | `oskarvanderwal/winogender` | `d1cdb5b708800c151d09c5d8817290d3f6ced9f4` |
| TurBLiMP | `juletxara/turblimp` | `cce94ca73ac04a0fabd9fbd7a56068261e6348ad` |

## 4. PPL ve cadence kararı

WikiText BPB her parent/epoch-end dense checkpointte primary English retention ölçümüdür. Pile-10k
all 10,000 rows ile entry/midpoint/endpoint full cadence'dedir; `--limit` scientific subset olarak
kullanılmaz. Frozen Pile identity 10,000 non-empty row, 61,074,719 UTF-8 bayt, 9,114,313
whitespace word ve dataset fingerprint `174215cc54146878` içerir.

Türkçe için exact frozen cross-domain control:

- `trwiki-20260601` validation: 10,034 doküman / 37,385,118 bayt;
- SHA-256: `15480c1f543acf6df7aac1b2a2ee15fdcb3a544814f0063a181bd7a9cb0ca4f8`;
- corpus manifest SHA-256:
  `108c72375bb253742831da3fafb9e4b4b7b736974cb3cf6ef13f9b0f167502f7`.

Bu control ana in-domain Türkçe split değildir. Primary in-domain split, M2 corpus contract'ında
exact path/hash/document manifest ile outcome görülmeden bağlanır. Bu binding eval semantiğini
değiştirmez; binding ve M1 baseline yoksa M2 primary manipulation summary açık kalır.

## 5. Factual registry freeze

Eski 4,000-row English registry kaybolmadı; EN→EN projection audit kaynağı olarak korunur. Yeni
bilimsel full registry 500 fact × 3 direction × 4 form × 2 scaffold = 12,000 probe içerir. Dense
panel her fact ve direction için tam bir probe seçer: 1,500 probe. Selection relation/branch içinde
deterministik olarak 8 form/scaffold hücresine 6/7 dağılımla counterbalance edilir.

| Artifact | Satır | SHA-256 |
|---|---:|---|
| English source audit | 4,000 | `54bf2968bcffecee8f0438b0ac489a6ab5fd0150dca2c459a4a1ad9efe50796b` |
| Full bilingual | 12,000 | `5125850a2db24c6b570971a58e9ba8a8586cabdec9084eb0e99bbd639691d93f` |
| Cheap bilingual | 1,500 | `9619339d5d0373036d26d39c88f36976bd4a9248f64ed346241a6ce54e658fc2` |
| Registry manifest | — | `e041515e0d040608c52901acb1656f0c19590be971bc50500b8a8f03c6642885` |

Generator iki kez aynı byte hashlerini üretti; tests source EN projection'ı, denominator'ları,
unique ID'leri, üç direction'ı ve hücre dengesini doğrular. Full checkpointte dense sonuç full
satırların alt kümesinden türetilir ve aynı probe ikinci kez score edilmez.

## 6. Frozen numeric rules

- M1 exact-prefix ≥ 0.90;
- trained A/B ve held-out C/D EN→EN top-1 global ve her relation için ≥ 0.80;
- sekiz-cell robust fact intersection global ve her relation için ≥ 0.70;
- WikiText ve Pile-10k `ΔBPB ≤ log2(1.25) = 0.32192809488736235`;
- BLiMP/HellaSwag absolute drop ≤ 0.05; WinoGender diagnostic;
- M2 primary Turkish byte PPL ratio ≤ 0.95, eşdeğer `ΔBPB ≤ -0.07400058144377693`;
- TurBLiMP absolute drop ≤ 0.05;
- M2 EN→EN top-1 ve robust-intersection drop ≤ 0.05;
- transfer M2-A−M1 ve relearning M2-B−M2-A TR→EN gain ≥ 0.05 ve paired-subject 95% bootstrap
  lower bound > 0;
- bootstrap 10,000 draw, seed 42; required her seed aynı rule'u ayrı geçer;
- selection ilk precommitted checkpointte bütün gerekli gate'lerin geçmesidir.

Retention score `100 / PPL ratio` yalnız görselleştirme alanıdır ve scientific gate değildir.

## 7. Checkpoint binding

eval-v1 cadence semantiği sabittir; update sayısı training recipe'ye göre değişebilir. Her training
contract outcome öncesinde:

1. her epoch'u exact integer update ve checkpoint hashine;
2. normalized progress 0.5'i bir exact integer update'a;
3. parent, entry ve endpoint'i exact model manifestlerine

bağlar. Interpolation veya sonuç gördükten sonra midpoint/checkpoint seçimi yasaktır.

## 8. Local frozen artifact identities

- `eval_v1_registry.yaml` SHA-256:
  `71d6f76e91f7891f32f9a1fffbc7493e3f85373b4c0737c9a734de9ec2d67d37`;
- `eval_v1_scientific_inputs_v1.yaml` SHA-256:
  `845cb891c9a74c98becb4c50e397124c8ab1f47aefdf91dfdd5548b4dcd3b62f`;
- `eval-v1.md` SHA-256:
  `72403598d7f9c8ba35bdfcc3e4791d097d41c6ef8f4e79c55cf9a6f34a37479e`;
- registry generator module SHA-256:
  `061ef34e3e82722e6ef0226027caca87a8be9c881522af90efc46f4eab6d731a`;
- operator SHA-256:
  `45253b6c3016b787feab7e20025bb37470fd491698aa2fd132cdd4c6d99cd4cd`.

Bu hashler Document 180 yazılmadan önceki frozen payload'lardır; Document 180 kendi kendisini hash
zincirine dahil etmez.

## 9. Sonraki exact boundary

R2 tamamlandı. Sonraki iş R3 kapsamında üç model için ayrı bilimsel M0 config/manifest üretmek,
fail-closed preflight çalıştırmak ve yalnız yeni explicit authorization ile OLMo/Qwen/SmolLM M0
evaluation wave'ini submit etmektir. M1/M2 training hâlâ yetkisiz ve corpus/training contractlarına
bağlıdır.
