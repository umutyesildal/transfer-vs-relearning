# M2 OSCAR Corrected Optimizer Smoke — Sonuç ve Kapı

Tarih: 2026-09-01  
Durum: `PASS / SCIENTIFIC TRAINING NOT STARTED`

## Yetki ve kapsam

Bu kayıt, SHA-256'sı
`2f43dc86836bb9d030988fe7567c19245b1c7246c335f34353184e8b3c4103f1` olan
`vngrs-m2-oscar-corrected-optimizer-smoke-v1` sözleşmesinin kullanıcı tarafından yetkilendirilen
tek seri `0-2%1` A100-80GB optimizer-smoke array sonucunu kapatır. Model ağırlıklarına yalnız
read-only smoke erişimi kullanılmıştır. M2-A/M2-B bilimsel eğitimi, checkpoint, evaluation,
cleanup, fallback veya retry çalıştırılmamıştır.

## Slurm ve terminal kanıtı

- test-only job: `482102`
- gerçek array: `482103`, görevler `0`, `1`, `2`
- rol sırası: OLMo, Qwen, SmolLM
- 2026-09-01 17:09 Europe/Berlin kontrolünde `squeue` işi artık aktif tabloda bulmamıştır.
- `sacct`, bilinen Munge/SlurmDBD kimlik doğrulama problemi nedeniyle terminal accounting satırı
  döndürememiştir. Bu eksik accounting metadata'sıdır; rol raporları ve loglar terminal kanıttır.
- failure-audit dosyası yoktur; üç stderr yalnız Transformers `torch_dtype` deprecation uyarısı ve
  normal ağırlık yükleme ilerlemesi içerir.

## Rol sonuçları

| Rol | Durum | Loss aralığı | Gradient norm | Peak allocated | Rapor SHA-256 |
|---|---|---:|---:|---:|---|
| OLMo | `OPTIMIZER_SMOKE_PASS` | 3.541560–4.910563 | 27.0 | 13,335,054,848 B | `1ba84c61dccdbf7d6a85d3b96d03435180d7afa4f04100a625030079c801327d` |
| Qwen | `OPTIMIZER_SMOKE_PASS` | 2.801940–4.321830 | 10.125 | 14,165,686,784 B | `c0b33e389aa9a8544f3354c65a1ba0b4bda206be718d3b3ad09b7d4eb1936009` |
| SmolLM | `OPTIMIZER_SMOKE_PASS` | 1.763196–2.838634 | 2.96875 | 14,412,728,832 B | `05faf4999fe04de49e9bc9ce30f5734584cba63e1ba3043c1dc1453fe1ab1732` |

Her rol için:

- GPU: `NVIDIA A100 80GB PCIe`;
- parametre ve gradient dtype: BF16;
- AdamW moment dtype: BF16, step dtype: FP32;
- `batch_size=4`, `gradient_accumulation_steps=32`;
- 128 blok / 65,536 token tüketilerek tam bir optimizer adımı tamamlandı;
- `scientific_training=false`, `checkpoint_written=false`, `ready_to_train=false`;
- corrected block-family manifest SHA:
  `96f9867c857b08bfd784660331d1a354be7d7c6bc39250091f427fdfaa3c6486`.

## Bilimsel/operasyonel karar

Üç model de aynı frozen M2-A girdisi ve corrected M2-B aile bağlamı altında gerçek model yükleme,
forward/backward ve AdamW update yolunu başarıyla geçti. Dolayısıyla GPU bellek ve optimizer
uyumluluğu için mevcut smoke kapısı kapanmıştır.

Bu PASS kendi başına M2 eğitim yetkisi veya `ready_to_train=true` üretmez. Sonraki iş; altı
bilimsel koşulun (üç model × M2-A/M2-B) exact training/evaluation DAG'ını, checkpoint/epoch ölçüm
matrisini, storage/runtime sınırlarını ve fail-closed kuralları tek yeni hash-bound sözleşmede
dondurmaktır. Ayrı kullanıcı yetkisi gelmeden hiçbir bilimsel eğitim başlatılmayacaktır.
