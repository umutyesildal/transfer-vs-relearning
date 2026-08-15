# 154 — Üç-Model 500-Fact M1 Screen v3 Post-Execution Gate

**Tarih:** 2026-08-11 (Europe/Berlin)  
**Durum:** `BLOCKED_BY_OPERATIONAL_PREFLIGHT`  
**Sonuç otoritesi:** Document 153

## 1. Gate kararı

Document 152a execution wave'i üç modelden herhangi biri için bilimsel sonuç üretmeden zorunlu
HU-home exact-byte usage kontrolünde durmuştur. Dar gate:

```text
blocked_by_operational_preflight
```

Şu ifadelerin hiçbiri desteklenmez:

- OLMo/Pythia/Falcon access veya tokenizer uyumsuzdur;
- modeller 500 fact'i öğrenemedi;
- modeller gate'i geçti;
- üç-model karşılaştırması tamamlandı.

## 2. Readiness

| Karar alanı | Değer |
|---|---|
| `ready_to_submit_m1_v3` | `false` |
| `ready_to_train_m1_v3` | `false` |
| `m1_v3_scientific_result_available` | `false` |
| `ready_for_seed43` | `false` |
| `ready_for_m2_m3` | `false` |
| `ready_for_corpus_stage_from_152a` | `false` |

Global `blocked_by_measurement_design` kararı değişmez. vngrs corpus çalışması kullanıcının çalışma
sırasında belirttiği sıraya göre üç-model ekranından sonra ele alınacaktır; 152a/153/154 corpus
execution yetkisi vermez.

## 3. Tek dürüst sonraki adım

Yeni model dalgasından önce storage preflight davranışı ayrı ve dar biçimde çözülmelidir. Yeni
kontrat en azından:

1. 120 saniyelik exact-byte `du` timeout'unu korunmuş kanıtla sınıflandırmalı;
2. home kullanımını 30 GiB sınırına karşı kanıtlayan bounded alternatif/önceden dondurulmuş yöntemi
   tanımlamalı veya timeout politikasını açıkça değiştirmeli;
3. fresh root'un hâlâ absent olduğunu ve `m1-pv3-*` job sayısının sıfır olduğunu yeniden bağlamalı;
4. aynı `a0eeed3` implementation commitini ve Document 152a bilimsel recipe'sini değiştirmemeli;
5. exact yeni kullanıcı authorization'ı istemelidir.

Bu düzeltme yalnız operasyonel preflight'i ele almalıdır; model/revision/dataset/LR/epoch/seed/gate
değerlerini sonuç görülmeden değiştiremez. Mevcut yetkiyle otomatik retry yapılmayacaktır.
