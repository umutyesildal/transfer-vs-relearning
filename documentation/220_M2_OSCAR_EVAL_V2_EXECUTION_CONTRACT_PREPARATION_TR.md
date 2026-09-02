# M2 OSCAR eval-v2 execution contract hazırlığı

Tarih: 2026-09-02  
Durum: `LOCAL PREPARATION PASS / FROZEN UNEXECUTED / EXACT AUTHORIZATION REQUIRED`

## Başlangıç kanıtı

Document 219 ile üç model × iki sibling arm training family `6/6`, checkpoint binding `60/60` ve
evaluation preparation matrix `PASS` oldu. Matrix SHA-256 değeri
`82373090047b8e52b064fd443cd007af20656d863e246905cebf6fa86a7ae7a9` ve bilimsel durum sayısı
63'tür. Bu hazırlık hiçbir HU, Slurm, GPU, model load, inference veya scoring çalıştırmadı.

## Yakalanan measurement-design düzeltmesi

İlk preparation matrix üç M1 parent'ı yeniden score etmeden projekte ediyordu. Fakat primary
in-domain kapı, M2-A OSCAR-held-out BPB'nin M1'e göre en az `0.07400058144377693` azalmasını ister;
M1 eval-v2 evidence'ında daha önce OSCAR held-out ölçülmemiştir. Bu nedenle yalnız eksik metriği
tamamlayan üç dar M1-parent OSCAR-BPB taskı eklendi. Eski factual, WikiText, trwiki ve capability
metrikleri yeniden score edilmez. Bilimsel state evreni değişmez: üç M1 parent + 60 M2 checkpoint
= 63; GPU task sayısı 60'tan 63'e çıkar.

## Frozen wave

- CPU preflight: 4 CPU/64G, exact 10.000 OSCAR held-out raw-text reconstruction;
- GPU array: `0-62%6`, her task için bir A100-80GB, automatic retry yok;
- M2 checkpointleri: 60, her birinde dense bundle;
- full checkpointler: update 381 ve 762, toplam 12 state;
- M1 completion taskları: yalnız OSCAR-held-out BPB, toplam 3;
- afterany finalizer: completeness ledger; yalnız 63/63 complete ise scientific analysis;
- analysis: Transfer=`M2-A−M1`, Relearning=`M2-B−M2-A`, `tr_to_en`, paired subject bootstrap
  10.000 draw/seed 42.

Her M2 checkpointte factual cheap, exact-prefix, WikiText/OSCAR/trwiki BPB ve generation integrity;
full state'lerde 12.000 factual probe ile English/Turkish capability paketi ölçülür. Cross-tokenizer
ana dil metriği BPB'dir.

## Operational ve authority gate

Fresh proposed root:
`/vol/tmp2/yesildau/vnd_m2_oscar_eval_v2_execution_v1`.
Kaynak corpus/split, M1 evidence, M1 parent modelleri, M2 checkpointleri ve training/finalizer
root'ları read-only'dir. Network, training, optimizer update, checkpoint yazma, cleanup, silme,
fallback, ikinci wave ve otomatik retry yoktur.

Offline focused suite `7/7 PASS`, Python compile ve `git diff --check` PASS olmuştur. Bu belge ve
contract hazırlanması publication, HU fast-forward veya execution yetkisi değildir. Final contract
SHA-256 değeri `582b6b6d5f066f96c9fdbc38b6d34eb9e4d83aa15a45d29e5cf07f1ec22331bd`'dir;
exact commit ile birlikte ayrı kullanıcı yetkisine sunulacaktır.
