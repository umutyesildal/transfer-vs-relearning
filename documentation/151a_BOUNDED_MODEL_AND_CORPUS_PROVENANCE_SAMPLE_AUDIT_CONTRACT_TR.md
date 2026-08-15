# 151a — Bounded Model ve Corpus Provenance Sample Audit Contract

**Tarih:** 2026-08-07 (Europe/Berlin)  
**İşçi:** LUNA-Worker 2  
**Durum:** Sonuçlardan önce donduruldu; yalnızca read-only provenance/sample audit'i  
**Kapsam:** Documents 147–151'in kullanıcı tarafından açıkça yetkilendirilen sınırlı devamı

## 1. Yetki ve kapsam sınırı

Bu sözleşme yalnızca aşağıdaki kanıt paketini üretmeye izin verir:

1. üç model reposu için exact revision, lisans/erişim, config/tokenizer metaverisi ve uzaktaki
   weight dosyalarının isim/boyut/LFS-OID metaverisi;
2. Turkish CulturaX ve `vngrs-ai/vngrs-web-corpus` için bounded, deterministik, streaming/sample
   provenance ve kalite denetimi;
3. frozen `trwiki-20260601` için aynı audit şemasında kontrol karşılaştırması;
4. CPU üzerinde LID, kalite, exact/near-dedup, synthetic contamination, PII aggregate ve
   tokenizer fertility hesapları;
5. scratch üzerinde manifest, rapor ve SHA-256 kanıtları.

Bu sözleşme training/fine-tuning, factual training, M2-A/M2-B training, GPU evaluation, tam model
 ağırlığı indirme, tam corpus indirme/materialization, 25.000 fact üretimi, checkpoint/optimizer
 oluşturma, frozen artifact mutation/cleanup veya `ready_to_train` iddiası vermez. Documents
 152–154 oluşturulmayacaktır.

Sonuçlar yalnızca `151b` ve `151c` içinde, bu sözleşmede önceden sabitlenen yöntem ve eşiklerle
raporlanabilir. Sonuç görüldükten sonra aday, seed, sample sınırı, metrik, eşik, dedup parametresi
veya verdict yolu değiştirilemez. Çözülemeyen bir alan adayın/sourcenun blocked veya conditional
olarak raporlanmasına yol açar; ikame aday seçilmez.

## 2. Dondurulmuş modeller ve roller

| Rol | Repo | Sözleşmedeki revision seçicisi | Protokol rolü |
|---|---|---|---|
| Yeni birincil aday | `allenai/OLMo-2-0425-1B` | `stage1-step140000-tokens294B` | Açık provenance/base adayı; selector'ın immutable commit SHA'sı audit başlangıcında kaydedilecek; çözülemezse blocked. |
| Yeni ikinci aday | `tiiuae/falcon-rw-1b` | `e4b9872bb803165eb22f0a867d4e6a64d34fce19` | English-only provenance sinyali ve tokenizer headroom adayı; bu sinyal sıfır Türkçe exposure kanıtı sayılmayacak. |
| Multilingual kontrol | `Qwen/Qwen2.5-1.5B` | `8faed761d45a263340a0528343f099c05c9a4323` | Mevcut frozen M1 ve Türkçe pilot zincirinin positive control'ü; “Turkish unseen” olarak sınıflandırılmayacak. |

Model revision çözümü için yalnızca read-only metadata/API çağrısı ve küçük config/card/tokenizer
dosyaları kullanılabilir. Her model için audit sonucu en az `resolved_revision`, repo/card URL,
lisans, base/stage, architecture/context, tokenizer dosya hash'leri, config hash'i, uzak weight
dosyalarının ad/boyut/LFS-OID listesi ve erişim hatalarını içerecektir. Weight içerikleri
indirilmeyecek. OLMo selector'ı exact commit'e çözülemezse OLMo sonucu `blocked_by_model_provenance`
gerekçesine yazılır; `main` veya başka bir checkpoint'e sessizce geçilmez.

`Pythia`, `StableLM`, `Gemma`, `Llama`, `SmolLM` ve başka model bu bounded round'a dahil değildir.
Sonuçlara göre yeni model eklenmeyecek.

## 3. Dondurulmuş corpus kaynakları ve örnekleme

### 3.1 Kaynaklar

| Rol | Kaynak | Revision politikası |
|---|---|---|
| Web aday 1 | `uonlp/CulturaX`, yalnız Turkish split | Dataset `main` ref'i audit başlangıcında immutable commit/snapshot SHA'ya çözülecek; çözüm yoksa blocked. Başka dil split'i eklenmeyecek. |
| Web aday 2 | `vngrs-ai/vngrs-web-corpus` | Dataset `main` ref'i audit başlangıcında immutable commit/snapshot SHA'ya çözülecek; çözüm yoksa blocked. VBART paper/card'daki 84.9 GB/25.33B ve 135 GB iddiaları birleştirilmeyecek. |
| Control | `trwiki-20260601` | Document 110'da frozen Wikimedia dump ve final manifest; yeni indirme/materialization yapılmadan mevcut manifest/hash ve scratch metadata kullanılacak. |

Web kaynaklarının her biri için hard stop:

- en fazla **10.000 doküman**; veya
- compressed/transferred source bytes için **1 GiB**;

hangisi önce gerçekleşirse örnekleme durur. Streaming/range erişim tercih edilir. Tam shard veya
tam dataset indirilmez; decompressed sample da yalnız audit scratch'inde tutulur. Deterministic
seed **42**'dir. Sample manifest her kayıt için `source_repo`, immutable `revision`, split/shard,
row/document ID, seed, sample index, raw transferred/compressed byte count, normalized-text
SHA-256 ve UTC retrieval timestamp alanlarını taşır. Kaynak bu sınırları güvenilir biçimde
uygulayamıyorsa sample `blocked_by_operational_access` olarak raporlanır.

Stratification yalnız kaynak metaverisinde mevcut alanlar üzerinden yapılır: shard/source/domain,
document-length quantile, page title/URL host ve varsa time bucket. Sonuç gördükten sonra strata
eklenmez. Row ID veya shard metadata yoksa eksik alan açıkça `NR` yazılır.

## 4. Storage, erişim ve audit kökü

Tüm scratch çıktısı için sabit kök:

```text
/vol/tmp2/yesildau/luna_bounded_provenance_sample_audit_v1
```

Sabit alt dizinler:

```text
samples/ metadata/ manifests/ reports/ cache/ logs/ tmp/
```

HU üzerinde örnek/metadata/cache/model dosyası `/vol/fob-vol6/mi25/yesildau` altına yazılamaz.
Launcher veya komutlar aşağıdaki değişkenleri köke yönlendirecektir:

```text
HF_HOME=$ROOT/cache/huggingface
TRANSFORMERS_CACHE=$ROOT/cache/huggingface
HF_DATASETS_CACHE=$ROOT/cache/huggingface-datasets
XDG_CACHE_HOME=$ROOT/cache
TORCH_HOME=$ROOT/cache/torch
TMPDIR=$ROOT/tmp
```

HU üzerinde ilk download/sample işleminden hemen önce ve tamamlandıktan sonra AGENTS preflight/audit
çalıştırılır:

```bash
HOME_ROOT=/vol/fob-vol6/mi25/yesildau
du -xsh "$HOME_ROOT"
df -h "$HOME_ROOT" /vol/tmp /vol/tmp2
df -i "$HOME_ROOT" /vol/tmp /vol/tmp2
find "$HOME_ROOT" -xdev -type f -size +500M -printf '%s %p\n' | sort -nr
```

Ayrıca her hedef için `readlink -f` ile sonuç yolu doğrulanır. Preflight; home 30 GiB'e yaklaşırsa,
home artışı açıklanamazsa, scratch/inode kapasitesi yetersizse, hedef home'a çözülürse, kaynak
revision/lisansı doğrulanamazsa veya transfer/sample bütçesi tahmin edilemezse işlemi durdurur.
Beklenen bounded üst bütçe sample transferi için kaynak başına 1 GiB, scratch geçici/metadata/cache
payı için 2 GiB ve model küçük metadata için 1 GiB'dir; gerçek kullanım ve yollar sonuç raporunda
ayrıca verilecektir. Bu bütçe tam corpus/model ağırlığı için değildir.

## 5. LID protokolü ve frozen eşikler

Primary LID, resmi fastText **`lid.176.ftz`** modelidir. Kaynak URL, exact model SHA-256, fastText
runtime sürümü ve preprocessing manifestte kaydedilecektir. SHA çözülemiyor veya model erişilemiyorsa
LID sonucu `blocked_by_operational_access` olur; farklı LID modeliyle ikame yapılmaz.

Preprocessing sabittir: Unicode NFC; ham kaydın yanında audit için whitespace runs tek space'e
indirgenmiş metin; boş kayıt atılmaz; doküman metni en fazla ilk 65.536 Unicode karakter üzerinden
LID'e verilir. Satır bazlı mixed-language kontrolü, normalize metnin non-empty satırlarında en
fazla 64 satırla yapılır.

Doküman sınıfları mutually exclusive ve şu önceliktedir:

1. **mixed:** en az 5 non-empty satır varsa ve satırların en az %10'u top-1 non-`tr`, en az %10'u
   top-1 `tr` ve `p(tr) >= 0.80` ise;
2. **Turkish pass:** mixed değil, top-1 `tr` ve `p(tr) >= 0.80`;
3. **low-confidence:** mixed değil, top-1 `tr` ve `0.50 <= p(tr) < 0.80`;
4. **non-Turkish:** yukarıdakilerin dışındaki tüm kayıtlar.

Rapor: `p(tr)` dağılımı, pass %, low-confidence %, non-Turkish %, mixed %, top-1 label dağılımı,
source/shard/domain kırılımları ve deterministic manual review için örnek ID'leri. Threshold'lar
sonuçtan sonra değiştirilemez.

## 6. Dondurulmuş kalite ve kalite raporu

Her source/sample için aşağıdaki ham ve aggregate alanlar hesaplanacaktır; yeni heuristic eklenmeyecek:

- UTF-8 byte, Unicode karakter, whitespace-token ve model-token uzunlukları;
- empty (`normalized_chars == 0`) ve short (`normalized_chars < 50`);
- Unicode replacement (`U+FFFD`) ve izin verilen `\\t/\\n/\\r` dışı control-character sayısı;
- URL count/density, HTML-tag count, code/table marker count;
- repeated-line oranı ve normalized character 5-gram repetition summary;
- alphabetic, Turkish diacritic (`çğıöşüÇĞİÖŞÜ`), punctuation ve digit oranları;
- source/shard/domain ve length quantile'ları;
- PII için yalnız aggregate pattern hit counts ve pattern category; ham PII dokümana veya sonuca
  yazılmaz.

`URL density > 0.20`, repeated-line ratio `>= 0.50`, HTML-tag presence, `normalized_chars < 50`,
replacement/control presence gibi eşikler yalnız diagnostic flag'dir; tek bir global “quality score”
üretilmez. Boilerplate, spam/adult/zararlı içerik ve PII için yalnız frozen pattern/aggregate
kanıt raporlanır; hukuki güvenlik veya training suitability iddia edilmez.

## 7. Exact/near dedup ve overlap

Exact dedup anahtarı:

```text
NFC(text) -> every Unicode whitespace run to one ASCII space -> strip -> UTF-8 SHA-256
```

Near dedup yöntemi sonuçtan önce sabittir: normalized **character 5-gram**, MinHash/LSH,
`num_perm=128`, `seed=42`, estimated Jaccard threshold `>= 0.80`. Uygulanan library/runtime ve
hash seed manifestte kaydedilecektir. Şüpheli yakın çiftlerin aggregate oranı ve source/shard/
domain kırılımı raporlanır; raw pair text sonuca alınmaz.

Karşılaştırmalar zorunludur:

1. CulturaX kendi içinde;
2. vngrs kendi içinde;
3. CulturaX–vngrs cross-source;
4. her web sample–`trwiki-20260601`;
5. mümkünse sample içi train/validation ayrımı ve source shard arası.

## 8. Synthetic ve benchmark contamination

Synthetic scan, mevcut frozen Relation V2 release'e bağlanacaktır: 5.000 subject, 25.000 fact,
713 canonical-object surface, 65.717 pattern ve 20.000 declared training sentence. Yerel
manifest evidence: release commit `ec2b96a`, release manifest SHA-256
`94df56dba548c81d39b03b7b7fe4f9a59d9555997e984fd7aed5cabd0a113425`; derived inventory hash'i
audit scratch'inde yeniden üretilip kaydedilecektir. Bu scan mevcut fact population'ı değiştirmez
ve yeni fact üretmez.

Eşleşmeler ayrı raporlanacaktır: `subject-only`, `object-only`, `subject+object/full-name`,
`probable alias/fuzzy`, `verified target-fact`, `false-positive/manual-adjudicated`. Object-only
ve common-name hit'leri hedef fact sonucu değildir; tüm match count'lar hedef fact sayısı gibi
yorumlanmayacaktır. Raw names/PII son docs'a yazılmaz.

Benchmark contamination için bu turda yalnız exact revision/item-set/hash erişilebilen kaynaklar
raporlanabilir. TurkishMMLU, Turkish EXAMS, TurBLiMP ve opsiyonel CETVEL/TurkBench için exact
revision veya item manifesti çözülemiyorsa sonuç **blokerdir**; sayı uydurulmayacak ve “clean” iddiası
kurulmayacaktır.

## 9. Tokenizer fertility ve BPC sınırı

Aynı frozen sample üzerinde OLMo, Falcon ve Qwen tokenizerlarıyla yalnız metadata/small tokenizer
dosyalarından şu ölçüler alınacaktır: tokens/document, tokens/word, tokens/character, bytes/token,
quantiles/outliers, unknown/special/byte-fallback oranları, Turkish diacritic edge cases ve
estimated tokens/GiB. Tokenizer revision ve tokenizer-file SHA her model için yazılır. Full model
weights olmadan tokenizer yüklenemezse fertility o model için blocked olur; sample başka modelle
yeniden seçilmez.

Bu turda model inference/likelihood yapılmadığı için **true BPC/bits-per-byte/PPL ölçülmeyecektir**.
Fertility yalnız compute/accessibility diagnostic'tir. 151c, evidence ve evaluator compatibility
varsa ileride true BPC/bpb ölçümünü önerebilir; raw PPL ile cross-tokenizer model sıralaması veya
true BPC sonucu iddia edilemez.

## 10. Dondurulmuş sonuç/verdict sözlüğü

Model başına `metadata_pass`, `metadata_conditional` veya `metadata_blocked`; corpus başına
`quality_pass`, `quality_conditional` veya `quality_blocked` kullanılır. Combined 151c final verdict
yalnızca aşağıdakilerden biri olabilir:

```text
ready_to_freeze_bounded_m1_screen_contract
ready_to_freeze_fact_free_turkish_dose_contract_using_existing_qwen
ready_to_freeze_both_bounded_contracts
blocked_by_model_provenance
blocked_by_corpus_evidence
blocked_by_measurement_design
blocked_by_operational_access
```

`ready_to_*` ifadeleri yalnız bir sonraki bounded contract'ın hazırlanabilirliğini ifade eder;
training readiness veya `ready_to_train` değildir. Exact measurement revision/hash/overlap/floor-
ceiling/threshold eksikse en az `blocked_by_measurement_design` korunur. Web sample evidence
tamamlanmadan corpus seçiminde automatic pass yoktur.

## 11. Dondurulmuş çıktı şeması ve kapanış

`151b` şu bölümleri içerecektir: summary, bu contract'ın SHA-256 hash'i, storage preflight, exact
paths, model metadata table, corpus sample manifests, LID, quality, exact/near dedup, trwiki
overlap, synthetic contamination, benchmark contamination, PII aggregate, fertility, projected
budgets, operational failures, scientific interpretation, model/corpus verdicts, SHA manifest,
post-run storage audit ve “no cleanup”.

`151c` şu kararları verecektir: OLMo–Falcon arasındaki primary M1 aday ve diğer aday; Qwen'in
positive-control rolü; CulturaX–vngrs seçimi ve Wikipedia control; corpus pass/conditional/blocked;
measurement blockers; BPC/bpb önerisi; Documents 152/153'ün yalnız hazırlanabilir olup olmadığı.
152/153 dosyaları bu sözleşmede oluşturulmayacaktır.

No cleanup kuralı: sample veya metadata audit'inin sonunda seçilmiş/frozen/unique artifact, dataset,
canonical manifest veya scientific result silinmeyecek/overwrite edilmeyecektir. Scratch sample
ham içeriği yalnız bu sözleşmenin yetkili bounded audit kökünde kalır; herhangi bir cleanup kararı
ayrı kullanıcı yetkisi gerektirir.

## 12. Sözleşme bütünlüğü

Bu belge oluşturulduktan sonra immutable contract olarak ele alınır. Dosyanın SHA-256'sı, oluşturma
UTC zamanı, git çalışma ağacı durumu ve kullanılan attachment/prompt referansı audit başlangıcında
`151b` içinde kaydedilecektir. Bu belgedeki hash veya seçimler sonuçtan sonra değiştirilemez; bir
düzeltme gerekirse yeni append-only belge gerekir ve mevcut contract korunur.

