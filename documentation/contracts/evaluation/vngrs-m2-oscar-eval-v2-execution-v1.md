# vngrs-m2-oscar-eval-v2-execution-v1

Status: `FROZEN / UNEXECUTED / SEPARATE EXACT AUTHORIZATION REQUIRED`

## Amaç

Tamamlanmış üç-model OSCAR M2 training family için dondurulmuş eval-v2 ölçümünü tek dalga halinde
çalıştırmak. Bilimsel evren 60 M2 checkpoint durumu ve üç M1 parent durumundan oluşan exact 63
durumdur. M1 parent'ın mevcut factual/WikiText/trwiki/capability metrikleri hash-closed evidence'dan
yeniden score edilmeden projekte edilir; daha önce ölçülmemiş OSCAR held-out BPB ise her parent için
bir kez tamamlanır. Bu dar completion, M1'e göre primary OSCAR-BPB kapısını hesaplayabilmek için
zorunludur. Bu sözleşme training değildir.

## Immutable girdiler

- finalizer matrix:
  `/vol/tmp2/yesildau/vnd_m2_oscar_finalizer_numeric_order_repair_v1/evaluation/eval_v2_matrix.json`,
  SHA-256 `82373090047b8e52b064fd443cd007af20656d863e246905cebf6fa86a7ae7a9`;
- M1 parent evidence:
  `artifacts/evaluations/m1_three_model_v1/dump/m1_metrics.json`, SHA-256
  `41c2f2c6b722fc25ac48af278f1b318acc5e743b3c48d649fe26259848080462`;
- OSCAR V3 materialization manifest SHA-256
  `bb413e9acafd0d891ea9c4461abc77acea1c737489560650db56dacf781dbd10`;
- held-out ID registry SHA-256
  `dc30629fe76ca722745fcd0148021de6c042218ed2994281d52d13c06011dc91`;
- eval-v2 runtime lock SHA-256
  `f9238f731fe3286aa0f5e5934f2b559a4202794d43cea4b9b00b2960b37ee942`.
- execution config SHA-256
  `54dedde78dda88f99d4cec80606c63b03657b04cb6545f816ff4979ed0b0567d`;
- adapter SHA-256
  `4bd68c27b486ea6b928a7ed21ef9171182fa01d1c9f6f9cb907cb8f254540ca9`;
- entrypoint SHA-256
  `141faf323ee85a4407525b51f6f757afdb749b3ac00b168cd6a8963fcfc5b215`.

Tüm parent model, checkpoint, corpus, split ve eski sonuç kökleri read-only'dir.

## Tek wave DAG

1. Tek 4-CPU/64G `longrun` preflight 32 verified Parquet objesini read-only doğrular, exact 10.000
   held-out stable ID'yi seçer ve yalnız fresh evaluation root altında raw-text JSONL üretir. Aynı
   preflight, üç immutable M1 epoch-036 full-factual summary hash'ini doğrular ve 12.000 satırlık
   per-probe baseline dosyalarının SHA-256 ledger'ını M2 scoring başlamadan önce dondurur.
2. `afterok` tek `0-62%6` A100-80GB array'i 60 M2 checkpointi ve üç dar M1-parent OSCAR baseline
   taskını tam bir kez score eder. Otomatik retry veya failed task yeniden çalıştırması yoktur.
3. `afterany` tek CPU finalizer 63 taskın completeness/hash ledger'ını yazar. Eksik veya failed bir
   task varsa sonuç `INCOMPLETE` kalır; sonucu uydurmaz ve retry açmaz.
4. Yalnız 63/63 complete ise aynı finalizer `tr_to_en` üzerinde 10.000-draw, seed-42 paired-subject
   bootstrap ile Transfer=`M2-A−M1` ve Relearning=`M2-B−M2-A` estimandlarını ve dondurulmuş
   OSCAR/WikiText/English-retention kapılarını yazar.

## Ölçümler

Her checkpointte cheap factual 1.500, exact-prefix 500, WikiText-2 + OSCAR held-out + trwiki
token-PPL/byte-PPL/BPB ve generation integrity ölçülür. Update 381 ve 762'de ayrıca full factual
12.000, BLiMP, HellaSwag, Winogender ve Turkish capability paketi ölçülür. Cross-tokenizer ana dil
metriği BPB'dir. M2-A genel Türkçe adaptasyonu, M2-B kontrollü factual re-exposure sibling arm'ıdır.

## Fail-closed sınırlar

Fresh root:
`/vol/tmp2/yesildau/vnd_m2_oscar_eval_v2_execution_v1`.
Network kapalıdır. Training, optimizer update, checkpoint yazma, source/root mutation, cleanup,
silme, fallback route, ikinci wave ve otomatik retry yasaktır. Scheduler test-only kontrollerinden
biri geçmezse hiçbir real job gönderilmez. Evaluation inference/scoring ve HU publication ancak
bu frozen dosyanın final SHA-256'sına ve exact commit'e bağlı ayrı kullanıcı yetkisiyle açılabilir.
Launcher hem exact contract SHA-256'yı hem exact commit'i hem de
`exact_sha_bound_user_authorization_received` acknowledgement değerini iki kez fail-closed doğrular.
