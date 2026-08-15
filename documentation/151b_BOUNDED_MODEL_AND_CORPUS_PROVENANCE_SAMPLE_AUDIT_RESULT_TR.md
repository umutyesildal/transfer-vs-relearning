# 151b — Bounded Model ve Corpus Provenance Sample Audit Result

**Tarih:** 2026-08-07 (Europe/Berlin)  
**İşçi:** LUNA-Worker 2  
**Durum:** Operationally blocked; partial public metadata only  
**Contract:** [151a](151a_BOUNDED_MODEL_AND_CORPUS_PROVENANCE_SAMPLE_AUDIT_CONTRACT_TR.md)  
**Combined verdict:** `blocked_by_operational_access`

## 1. Özet

151a'da önceden dondurulan bounded audit'in HU örnekleme aşaması güvenlik/onay katmanında
çalıştırılmadan reddedildi. Reddedilen komut yalnızca AGENTS.md'nin zorunlu `du`, `df -h`,
`df -i` ve `readlink -f` preflight'iydi; credential, parola veya secret çıktısı alınmadı ve HU'da
hiçbir komut çalışmadı. Bu nedenle aşağıdaki sonuçlar **ölçülmemiştir** ve sayı uydurulmamıştır:

- CulturaX/vngrs sample row'ları ve sample manifestleri;
- fastText LID dağılımı ve Turkish pass/low-confidence/non-Turkish/mixed yüzdeleri;
- sample kalite quantile'ları, exact/near dedup ve `trwiki` overlap;
- Relation V2 synthetic subject/object/fact contamination;
- benchmark contamination ve PII aggregate;
- OLMo/Falcon/Qwen tokenizer fertility ve projected token bütçeleri;
- HU storage/inode preflight ve post-run audit.

Bu belge yarım kalmış bir “quality pass” değildir. Public model/dataset metadata'sı ve yerel frozen
project evidence ayrı tutulmuş, operasyona bağlı kanıt eksikliği final verdict'e taşınmıştır.

## 2. Contract hash ve çalışma durumu

| Alan | Değer |
|---|---|
| 151a SHA-256 | `524c3202df94ec95123bedbd976fe972bc0c2b1baad3eb301356d0b962a10dd4` |
| Audit kökü | `/vol/tmp2/yesildau/luna_bounded_provenance_sample_audit_v1` |
| Beklenen alt dizinler | `samples/ metadata/ manifests/ reports/ cache/ logs/ tmp/` |
| Local sample output | Oluşturulmadı |
| HU sample/metadata/cache | Oluşturulmadı |
| LID model | İndirilmedi; resmi `lid.176.ftz` kaynağı ve yöntem 151a'da frozen |
| Seed | 42 (uygulanamadı) |
| Audit zamanı | 2026-08-07; HU komutu approval katmanında execution öncesi reddedildi |
| Cleanup/mutation | Yapılmadı |

## 3. Storage preflight ve operational failure

AGENTS.md'nin zorunlu preflight'i şu path'ler için planlandı:

```text
/vol/tmp2/yesildau/luna_bounded_provenance_sample_audit_v1
/vol/fob-vol6/mi25/yesildau/transfer-vs-relearning/runs
/vol/fob-vol6/mi25/yesildau/transfer-vs-relearning/artifacts
```

Ancak `ssh-client/scripts/hu_ssh_expect` üzerinden read-only çağrı, güvenlik approval katmanında
Document 146/AGENTS'in tarihsel HU yasağı ile yeni bounded audit talimatı arasındaki authority
çatışması gerekçesiyle reddedildi. Bu ret, remote `du/df/readlink` çıktısı alınmadan gerçekleşti.
Dolayısıyla home usage, scratch free bytes/inodes, resolved destinations, large-home-file listesi,
expected transfer budget veya post-run audit için **PASS/FAIL sonucu yoktur**. Operational blocker
olarak kaydedilmesinin nedeni tam olarak budur.

Local repo statusu denetimden önce read-only kontrol edildi; mevcut unrelated user outputs korunuyor.
151a sözleşmesinden sonra local model/corpus artifact'i, cache'i, sample'ı veya büyük veri dosyası
oluşturulmadı. HU home'a hiçbir şey yazılmadı.

## 4. Public model metadata (sample audit değildir)

| Model | Public olarak doğrulanabilen | Eksik kalan | Verdict |
|---|---|---|---|
| `allenai/OLMo-2-0425-1B` | Model card: base OLMo 2 1B; Apache-2.0; 4T training-token headline; 16 layers, hidden size 2048, context 4096. Main file listing yaklaşık 5.95 GB ve iki safetensors shardı gösteriyor. Frozen selector `stage1-step140000-tokens294B` kartta kullanım örneği olarak mevcut. | Selector'ın exact immutable commit SHA'sı, config/tokenizer local hash'i, weight manifest/LFS-OID'in read-only capture'ı ve runtime compatibility alınamadı. | `metadata_blocked` |
| `tiiuae/falcon-rw-1b` | Model card/repo: English-tagged Falcon-RW-1B, Apache-2.0; main history'deki frozen commit `e4b9872bb803165eb22f0a867d4e6a64d34fce19` sözleşme selector'ı ile eşleşiyor. | Config/tokenizer hash'i, complete remote weight file/LFS-OID manifesti ve tokenizer usability capture'ı alınamadı. | `metadata_conditional` |
| `Qwen/Qwen2.5-1.5B` | Public card: multilingual base, Apache-2.0; current file listing yaklaşık 3.1 GB, `model.safetensors` yaklaşık 3.09 GB ve tokenizer/config dosyaları var. Project Document 105/147'deki read-only resolution `8faed761d45a263340a0528343f099c05c9a4323` ile sözleşme eşleşiyor. | Bu bounded round'da remote manifest/config/tokenizer SHA capture ve runtime compatibility tekrarlanamadı. Türkçe exposure unseen olarak sınıflandırılmayacak. | `metadata_conditional` |

Bu tablo weight indirme veya model inference sonucu değildir. Public file sizes yalnız transfer
bütçesi ve full-download yasağının neden gerekli olduğunu gösterir; audit sırasında hiçbir weight
byte'ı alınmadı.

## 5. Corpus public metadata (sample manifesti yok)

| Kaynak | Public metadata | Bounded sample sonucu | Verdict |
|---|---|---|---|
| `uonlp/CulturaX`, Turkish `tr` | HF card 167 dil ve parquet formatını bildiriyor; Turkish satırında `94,207,460` doküman ve `64,292,787,164` upstream token raporlanıyor. Card toplam repo boyutunu `17.5 TB` gösteriyor; upstream mC4/OSCAR lisanslarına bağlı ve dosya erişimi contact-information koşulu istiyor. | Sample revision/row IDs/raw bytes/normalized hashes alınamadı; LID/quality/dedup/contamination/fertility çalışmadı. | `quality_blocked` |
| `vngrs-ai/vngrs-web-corpus` | HF card: Turkish, parquet, `cc-by-nc-sa-4.0`, yaklaşık `84.9 GB`, 12 commit history; card'ın görünen son README commit'i short `ee5c620`. | Exact full revision SHA, shard/file manifest, bounded rows/raw bytes/hashes alınamadı; LID/quality/dedup/contamination/fertility çalışmadı. | `quality_blocked` |
| `trwiki-20260601` control | Document 110: frozen Wikimedia source; 684,703 extracted, 505,016 deduplicated, 504,287 clean retained, 729 conservative removals, 494,253 train/10,034 validation; final corpus manifest SHA `108c72375bb253742831da3fafb9e4b4b7b736974cb3cf6ef13f9b0f167502f7`. | Historical frozen evidence mevcut; bu bounded round'ın aynı sample/LID/fertility protocol'ü çalışmadı. Bu sayıların web sample sonucu gibi yeniden kullanımı yoktur. | `quality_conditional` |

Public CulturaX card'ı ayrıca kişisel/hassas bilgi içerebileceği uyarısını açıkça taşır; bu, PII
aggregate denetiminin gerekliliğini doğrular fakat bounded sample için PII oranı değildir.

## 6. LID, quality, dedup, overlap ve contamination

| Paket | Sonuç |
|---|---|
| fastText `lid.176.ftz` | Model indirilmedi; SHA doğrulanmadı; hiçbir LID skoru yok. |
| Turkish pass/low-confidence/non-Turkish/mixed | **N/A — sample yok.** |
| Quality length/control/URL/HTML/repetition/diacritic | **N/A — sample yok.** Threshold'lar 151a'da frozen; sonuç sonrası yeni heuristic eklenmedi. |
| Exact dedup | **N/A — sample yok.** Frozen NFC+whitespace+SHA yöntemi uygulanmadı. |
| Near dedup | **N/A — sample yok.** Frozen char-5-gram, MinHash `num_perm=128`, seed 42, threshold .80 uygulanmadı. |
| Web ↔ `trwiki` overlap | **N/A — sample yok.** |
| Synthetic contamination | **N/A — sample yok.** Frozen Relation V2 counts/hash yalnız referans olarak 151a'da bağlı; yeni match count üretilmedi. |
| Benchmark contamination | **BLOCKED.** TurkishMMLU, Turkish EXAMS, TurBLiMP ve optional CETVEL/TurkBench için exact item/revision manifesti bu turda capture edilmedi; sayı icat edilmedi. |
| PII | **N/A — sample yok.** Raw PII hiçbir dokümana yazılmadı; legal safety iddiası yok. |

Document 110'un 0 verified retained synthetic full-name match sonucu bu yeni web sample'larına
aktarılmamıştır; yalnız frozen Wikipedia control evidence'i olarak korunmuştur.

## 7. Tokenizer fertility ve projected budget

OLMo/Falcon/Qwen tokenizerları için sample-level `tokens/document`, `tokens/word`, `tokens/char`,
`bytes/token`, quantile/outlier, unknown/special/byte-fallback, diacritic edge-case ve tokens/GiB
hesapları **yoktur**. Model weight indirilmedi; inference çalıştırılmadı. Bu nedenle true
`BPC/bits-per-byte` ve PPL de ölçülmedi. Public model file sizes token budget değildir.

## 8. Scientific interpretation ve verdict gerekçesi

Public metadata, 151a'daki model rollerini destekliyor: OLMo açık base/provenance yönünden en güçlü
aday olarak kalıyor, Falcon English provenance/headroom adayı, Qwen ise multilingual positive
control. Fakat exact commit/config/tokenizer/weight manifest kanıtı tamamlanmadığı için bu, model
seçim geçidi değildir.

Web corpus tarafında CulturaX'ın Türkçe ölçeği ve documented cleaning/dedup pipeline'i, vngrs'ın
Türkçe parquet release'i ve lisans bilgisi adaylık için yeterli context sağlar; ancak sample-level
Turkish LID, quality, near-dedup, synthetic/benchmark overlap, PII aggregate ve tokenizer fertility
olmadan `quality_pass` denemez. `trwiki-20260601` güçlü historical control olarak kalır; web
çeşitliliği yerine otomatik seçilemez.

Combined verdict `blocked_by_operational_access` seçilmiştir. Downstream blockers ayrıca
`blocked_by_corpus_evidence` ve `blocked_by_measurement_design` olarak devam eder; bunlar
ölçülmüş başarısızlık değil, eksik kanıttır.

## 9. SHA manifest ve post-run storage

Bu bounded attempt'te doğrulanabilen local SHA:

```text
524c3202df94ec95123bedbd976fe972bc0c2b1baad3eb301356d0b962a10dd4  151a_BOUNDED_MODEL_AND_CORPUS_PROVENANCE_SAMPLE_AUDIT_CONTRACT_TR.md
```

Sample/model/LID manifest SHA'sı yoktur; çünkü dosyalar oluşturulmadı. HU preflight ve post-run
storage audit'i execution öncesi approval ret nedeniyle yoktur. No cleanup/migration/overwrite
yapılmadı.

## 10. Kaynaklar

- [OLMo-2-0425-1B model card](https://huggingface.co/allenai/OLMo-2-0425-1B)
- [Falcon-RW-1B model card](https://huggingface.co/tiiuae/falcon-rw-1b)
- [Qwen2.5-1.5B model card](https://huggingface.co/Qwen/Qwen2.5-1.5B)
- [CulturaX dataset card](https://huggingface.co/datasets/uonlp/CulturaX)
- [vngrs-web-corpus dataset card](https://huggingface.co/datasets/vngrs-ai/vngrs-web-corpus)
- [fastText language-identification model page](https://fasttext.cc/docs/en/language-identification)
- [Document 110 — frozen Turkish Wikipedia control](110_TURKISH_BRIDGE_CORPUS_RESULT_AND_FREEZE.md)
- [151a — bounded audit contract](151a_BOUNDED_MODEL_AND_CORPUS_PROVENANCE_SAMPLE_AUDIT_CONTRACT_TR.md)

