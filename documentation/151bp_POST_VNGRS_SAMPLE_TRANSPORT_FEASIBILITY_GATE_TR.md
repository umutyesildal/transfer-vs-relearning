# Document 151bp — Post-vngrs Sample Transport Feasibility Gate (TR)

**Tarih:** 2026-08-13, Europe/Berlin  
**Related result:** Document 151bo  
**Gate:** `BLOCKED — CURRENT SYSTEMATIC MIDPOINT SAMPLE HAS NO BOUNDED TRANSPORT ROUTE`

## 1. Decision

Document 151bn projection package bütün integrity gate'lerini geçti. Ancak bilimsel/operasyonel
karar PASS değildir:

```text
projection integrity                = PASS
100-request /rows feasibility       = FAIL by pre-existing 373-window minimum
Parquet row-group transport         = 5,664 / 5,696 groups
compressed coverage                 = 9,455,428,874 / 9,468,474,036 bytes
bounded sample transport readiness  = false
corpus selection/materialization    = BLOCKED
global gate                         = blocked_by_measurement_design
ready_to_measure                    = false
ready_to_train                      = false
```

## 2. Scientific implication

10.000 exact systematic midpoint kaydı shard boyunca yaymak temsili kapsama sağlar; fakat
Parquet row-group depolama düzeninde neredeyse full selected-shard taşıması gerektirir. Limitleri
sonuç gördükten sonra büyütmek veya bu işi sample diye adlandırmak kabul edilmez.

## 3. Next design gate

Sonraki corpus adımı ayrı exact contract altında şu iki seçenekten birini önceden seçmelidir:

1. Exact systematic estimand korunur; `/rows` için en az 373 successful window ve gerçek response
   byte budget'ı yeniden dondurulur. Bu seçenek source/path binding problemini ayrıca çözmelidir.
2. Bounded transport öncelenir; shard başına az sayıda önceden dondurulmuş clustered windows ile
   yeni bir cluster-sampling estimand, inclusion weights ve uncertainty/coverage sınırları tanımlanır.

İki seçenek aynı wave içinde response'a bakılarak değiştirilemez. Full selected shards veya
yaklaşık 9.46 GB retrieval otomatik olarak açılmaz.

Bu belge network, corpus row/full shard, sample calibration, LID/quality, materialization,
model/tokenizer, GPU/Slurm, training, cleanup veya deletion yetkisi vermez.
