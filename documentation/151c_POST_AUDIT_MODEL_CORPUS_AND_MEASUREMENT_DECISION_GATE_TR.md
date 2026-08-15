# 151c — Post-Audit Model, Corpus ve Measurement Decision Gate

**Tarih:** 2026-08-07 (Europe/Berlin)  
**İşçi:** LUNA-Worker 2  
**Girdi:** [151a contract](151a_BOUNDED_MODEL_AND_CORPUS_PROVENANCE_SAMPLE_AUDIT_CONTRACT_TR.md), [151b result](151b_BOUNDED_MODEL_AND_CORPUS_PROVENANCE_SAMPLE_AUDIT_RESULT_TR.md)  
**Final verdict:** `blocked_by_operational_access`

## 1. Karar özeti

Bounded audit'in HU preflight/sample adımı güvenlik approval katmanında execution öncesi
reddedildi. Bu nedenle model/corpus selection veya measurement opening kararı verilemez. Public
metadata, aday rollerini değiştirmiyor; ancak sample evidence yokluğu pass üretmiyor.

## 2. Model kararı

- **Primary M1 candidate önerisi:** OLMo-2 1B, açık base/provenance ve yayımlanmış training
  artefact/recipe çizgisi nedeniyle; fakat exact selector-to-commit, config/tokenizer hash ve
  remote weight manifest tamamlanana kadar `metadata_blocked`.
- **Secondary candidate:** Falcon-RW-1B; English provenance sinyali ve headroom sorusu için
  uygun, fakat tokenizer/config/weight manifest eksikliği nedeniyle `metadata_conditional`.
- **Positive control:** Qwen/Qwen2.5-1.5B; mevcut frozen M1 ve multilingual continuity için
  tutulur. Türkçe unseen adayı değildir; bounded metadata refresh tamamlanmadığı için
  `metadata_conditional`.
- **Pythia:** Bu bounded round'a dahil edilmedi; sonuçlara göre sonradan eklenmeyecek.

Bu sıralama bir eğitim izni veya yeni model seçimi değildir. Exact immutable revision, license,
base/stage, tokenizer usability ve remote file/LFS-OID manifesti tamamlanmadan OLMo–Falcon
karşılaştırması `ready_to_freeze_bounded_m1_screen_contract` açmaz.

## 3. Corpus kararı

- **Control:** `trwiki-20260601` historical frozen control olarak korunur. Kalite/provenance
  evidence'i güçlüdür, fakat bu bounded round'ın aynı LID/fertility sample'ı çalışmadığı için
  `quality_conditional`.
- **CulturaX:** Public card ölçek, Turkish row count ve documented cleaning/dedup pipeline'i
  gösterir; contact-information erişim koşulu ve sample evidence eksikliği nedeniyle
  `quality_blocked`.
- **vngrs-web-corpus:** Public card Turkish/parquet/CC-BY-NC-SA-4.0 ve yaklaşık 84.9 GB metadata
  gösterir; exact full revision, file manifest ve sample evidence eksikliği nedeniyle
  `quality_blocked`.
- **Web corpus selection:** CulturaX veya vngrs arasında seçim yapılmadı. `trwiki` web adayı
  yerine otomatik terfi ettirilmedi; Kumru 500 GB/300B ile vngrs 84.9 GB/25.33B iddiaları hâlâ
  aynı release olarak uzlaştırılmadı.

## 4. Measurement kararı

Measurement package frozen değildir. Açık blocker'lar:

1. model-independent Turkish held-out split ve English retention split hash'leri;
2. TurBLiMP veya CETVEL/TurkBench grammar alt seti için exact revision/item IDs/license/overlap;
3. TurkishMMLU ve EXAMS Turkish subset için exact item manifesti, scoring ve overlap;
4. fastText `lid.176.ftz` exact SHA ve sample LID output;
5. frozen exact/near-dedup ve Relation V2 contamination manifestleri;
6. OLMo/Falcon/Qwen fertility and projected token budgets;
7. BPC/bits-per-byte evaluator compatibility, UTF-8 byte rule, baseline floor/ceiling ve
   predeclared numeric thresholds.

Bu nedenle true BPC/bpb sonucu yoktur. İleride farklı tokenizer/model ailelerini karşılaştıran
ölçüm açılırsa, UTF-8 bytes üzerinden normalize edilmiş tek bir primary metric (BPC veya bpb)
önceden seçilmelidir; raw cross-tokenizer PPL ranking yapılmamalıdır. Bu turda en savunulabilir
öneri, evaluator compatibility kanıtlanırsa UTF-8 **bits-per-byte**'ı primary normalized metric,
within-model PPL'yi secondary diagnostic ve fertility'i ayrı compute/accessibility diagnostic
olarak önceden dondurmaktır. Bu yalnız öneridir, frozen contract değildir.

## 5. 152/153 hazırlık durumu

Documents 152 veya 153 oluşturulamaz ve “hazırlanabilir” sayılmaz. Exact model provenance,
sample-level corpus evidence, contamination/benchmark status, fertility budget ve measurement
freeze tamamlanmadan:

- bounded M1 screen execution contract açılmaz;
- existing Qwen ile facts-free Turkish dose contract açılmaz;
- 25.000-fact veya M2-A/M2-B training planı açılmaz.

Bu iki dosya intentionally oluşturulmadı; yalnız bu gate belgesi ve 151a/151b append-only kanıtı
vardır.

## 6. Yasaklanan/uygulanmayan işlemler

Bu turda training, fine-tuning, factual training, GPU evaluation, Slurm job, full model-weight
download, full corpus download/materialization, checkpoint/optimizer creation, artifact mutation,
cleanup veya migration yapılmadı. HU home'a yazım yoktur. Approval ret nedeniyle storage preflight
ve post-run audit ölçümleri de yoktur; bunlar yokmuş gibi PASS raporlanmamıştır.

## 7. Tek sonraki hareket

Kullanıcıdan bounded audit için HU read-only preflight/sample komutuna açık approval sağlanması
veya aynı sınırlı işlemleri çalıştıracak onaylı bir bağlantı yüzeyi sağlanması gerekir. Bu yetki
sağlanmadan hiçbir alternatif SSH/credential yolu denenmeyecek. Yetki geldikten sonra tek wave'de
151a'daki değişmez seed/limit/eşiklerle yeniden başlanır; sonuç görülünce aday veya yöntem
değiştirilemez.

