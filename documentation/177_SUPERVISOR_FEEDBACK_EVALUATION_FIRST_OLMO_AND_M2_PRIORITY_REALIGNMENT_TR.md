# Document 177 — Supervisor Feedback: Evaluation-First OLMo and M2 Priority Realignment (TR)

**Tarih:** 2026-08-14, Europe/Berlin  
**Kaynak:** Max ile 14 Ağustos 2026 tarihli supervisor görüşmesi  
**Durum:** `SUPERVISOR FEEDBACK CAPTURED — IMPLEMENTATION CONTRACT NOT YET FROZEN`  
**Önceki otoriteler:** Documents 145, 158, 159, 160, 176

## 1. Kısa hüküm

Yeni yön, vngrs üzerinde uzun bir provenance/quality araştırmasına devam etmek değil; OLMo üzerinde
ölçüm sistemini sağlamlaştırmak, eğitimin başından sonuna fact access ile retention davranışını
izlemek ve projenin en büyük zaman payını `M2-A` / `M2-B` ana karşılaştırmasına ayırmaktır.

Öncelik sırası artık şöyledir:

1. mevcut PPL hesabını ve eğitim ayarlarını Max'e açıklanabilir hale getirmek;
2. LM Evaluation Harness tabanlı, çok-metrikli ve checkpoint/epoch boyunca çalışan değerlendirme
   sistemini kurmak;
3. OLMo'nun gerçekten retention problemi yaşayıp yaşamadığını bu sistemle yeniden ölçmek;
4. vngrs'i yalnız hafif ve hedefli kontrollerden sonra doğrudan Türkçe adaptation corpus'u olarak
   kullanmak;
5. ana zamanı sentetik İngilizce facts → factsiz Türkçe corpus → sentetik Türkçe factual
   re-exposure sırasındaki `M2-A` / `M2-B` deneyine vermek.

Bu belge yeni training/evaluation yürütmez ve HU/Slurm yetkisi vermez. Bir sonraki adım, burada
tanımlanan evaluation ve training-trace kontratının exact model/dataset/commit/task adlarıyla
dondurulmasıdır.

## 2. Supervisor notlarının düzenlenmiş özeti

### 2.1 Eğitim sürecini baştan sona izleme

Sadece base ve endpoint sonucu yeterli değildir. Epoch 0/base dahil, eğitimin tüm aşamalarında fact
access ve retention birlikte izlenmelidir. İdeal teslimat tek bir uzunlamasına tablo ve ona bağlı
Pareto/trajectory grafiğidir:

| Alan | Her ölçüm noktasında kaydedilecek değer |
|---|---|
| Kimlik | model revision, run ID, seed, epoch, update, checkpoint hash |
| Dose | cumulative examples, fact exposures, supervised tokens, total tokens |
| Optimization | LR, train loss, microbatch, gradient accumulation, effective batch |
| Sequence | max sequence length, gerçek non-pad token ortalaması, truncation count/rate |
| Fact access | exact accuracy, aggregate hard-suite accuracy, relation/form minima |
| English retention | WikiText harness word PPL, byte PPL, bits/byte; Pile-10k sonucu |
| English capability | BLiMP, HellaSwag ve uygun pronoun/coreference görevi |
| Turkish capability | TurBLiMP, TurkishMMLU, XNLI-TR; karşılaştırma için XNLI-EN |

Tam 4.000-probe hard suite'i her epoch çalıştırmak pahalıysa iki katman kullanılabilir:

- her epoch/update grid'inde frozen cheap fact-access paneli + retention paneli;
- önceden dondurulmuş milestone'larda tam hard suite.

Bu ayrım sonuç görüldükten sonra değiştirilmemeli; ölçüm grid'i eğitimden önce dondurulmalıdır.

### 2.2 Corpus yönü

vngrs'in OSCAR ve mC4 gibi farklı web stillerini karıştırması olumlu kabul edilmiştir. Derin ve
uzun bir corpus audit'i artık ana öncelik değildir. Minimum yeterli kontrol:

1. exact dataset revision ve shard/hash freeze;
2. `text`, `corpus`, `original_id` şema doğrulaması;
3. OSCAR/mC4 oranları ve çok küçük stratified human sample;
4. hafif regex tabanlı encoding/boilerplate/SEO-betting/legal-jurisdiction benzeri pattern sayımları;
5. sentetik fact subject/alias'larına karşı dar contamination kontrolü.

Supervisor notundaki “jurisdict” ifadesi tam görev adı olarak açık değildir. Şimdilik bu ifade,
web metnindeki hukuk/jurisdiction boilerplate'ini ölçen hafif regex kontrolleri şeklinde yorumlanır;
implementasyondan önce Max'ten gerekirse netleştirilmelidir. Ağır classifier eğitimi veya kapsamlı
manual labeling planlanmaz.

## 3. PPL tam olarak nedir?

Bir token dizisi için ortalama negatif log-likelihood:

```text
NLL_token = -(1/N) * sum_t log p(x_t | x_<t)
token_PPL = exp(NLL_token)
```

Mevcut projede kullanılan retention oranı:

```text
PPL_ratio(checkpoint) = PPL_checkpoint / PPL_base
```

`1.0` değişim yok, `>1.0` kötüleşme, `<1.0` iyileşme anlamına gelir. Ancak raw token PPL,
tokenizer ve segmentasyon değiştiğinde modeller arasında doğrudan karşılaştırılmamalıdır. Aynı
modelin base/checkpoint oranı daha anlamlıdır çünkü tokenizer sabittir; yine de corpus formatting,
heading/detokenization, context window ve stride sonucu ciddi biçimde etkileyebilir.

LM Evaluation Harness'ın current metric implementasyonu perplexity'yi log-likelihood ortalamasının
negatif üssü olarak hesaplar; weighted perplexity ve bits-per-byte da sunar. Resmî WikiText task'ı
`loglikelihood_rolling` kullanır ve `word_perplexity`, `byte_perplexity`, `bits_per_byte` raporlar.
Bu nedenle yeni ölçümde tek bir raw PPL yerine üçü birlikte saklanmalıdır:

- word perplexity;
- byte perplexity;
- bits per byte (BPB).

Kaynaklar:

- [LM Evaluation Harness task guide](https://github.com/EleutherAI/lm-evaluation-harness/blob/main/docs/task_guide.md)
- [LM Evaluation Harness metrics implementation](https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/api/metrics.py)
- [Official WikiText task](https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/wikitext/wikitext.yaml)

## 4. “Retention score” düzeltmesi

Max görüşmesinde gösterilen slayttaki `retention score` standart literatür veya LM Evaluation
Harness metriği değildir. Yalnız görselleştirme için şu dönüşüm kullanılmıştır:

```text
retention_score = 100 / PPL_ratio
```

Bu skor:

- yalnız “higher is better” grafik üretmek için kullanıldı;
- scientific gate değildir;
- model seçimi için tek başına kullanılmamalıdır;
- tezde primary metric olarak raporlanmamalıdır.

Bilimsel kayıtta base PPL, checkpoint PPL, PPL ratio, word/byte PPL ve BPB gösterilmelidir. Grafik
gerekiyorsa retention score ikincil ve açıkça “derived visualization” diye etiketlenmelidir.

## 5. WikiText formatting ve heading kontrolü

Resmî harness WikiText görevi `EleutherAI/wikitext_document_level`,
`wikitext-2-raw-v1`, `loglikelihood_rolling` ve kendi `wikitext_detokenizer` fonksiyonunu kullanır.
Mevcut özel evaluator ile bu task arasında şu farklar exact olarak denetlenmelidir:

- article heading'leri ham `= Heading =` biçiminde mi kalıyor;
- heading'leri Markdown `# Heading` biçimine çevirmek sonucu değiştiriyor mu;
- whitespace/newline ve detokenization aynı mı;
- document boundaries, BOS/EOS, stride ve context overlap nasıl uygulanıyor;
- son token dışında her token yalnız bir kez mi skorlanıyor;
- toplam scored token/word/byte sayıları aynı mı.

Heading-to-Markdown dönüşümü outcome görüldükten sonra primary evaluator'a eklenmemelidir. Önce
canonical harness sonucu primary reference olarak dondurulmalı; raw/detokenized/Markdown varyantı
yalnız bounded sensitivity analysis olarak raporlanmalıdır.

## 6. Pile-10k rolü

[NeelNanda/pile-10k](https://huggingface.co/datasets/NeelNanda/pile-10k) 10.000 örnek içerir;
alanları `text` ve `meta.pile_set_name` olarak kayıtlıdır. Bu veri:

- WikiText'e ek olarak geniş-domain English retention kontrolü olabilir;
- farklı Pile alt-kümeleri için breakdown sağlayabilir;
- corpus-perplexity görevi olarak harness'a custom YAML/task ile eklenebilir.

Pile-10k mevcut resmî task kataloğunda hazır bir task olarak varsayılmamalıdır. Exact dataset
revision, split, preprocessing, document joining, stride/context ve metric aggregation kontratta
dondurulmalıdır. Ayrıca training corpus overlap/decontamination riski not edilmelidir; bu nedenle
WikiText'i tamamen değiştiren tek primary retention seti değil, tamamlayıcı kontrol olarak başlamak
daha güvenlidir.

## 7. LM Evaluation Harness task matrisi

Current upstream katalog doğrulamasına göre:

| Task/aile | Dil | Upstream durum | Projedeki rol |
|---|---|---|---|
| `wikitext` | EN | mevcut | canonical rolling word/byte PPL ve BPB |
| `blimp` | EN | mevcut | grammatical minimal-pair likelihood |
| `hellaswag` | EN | mevcut | commonsense continuation accuracy |
| `winogender` | EN | mevcut | pronoun/coreference diagnostic |
| `turblimp_core` | TR | mevcut | Türkçe grammatical minimal pairs |
| `turkishmmlu` | TR | mevcut; dataset access e-posta gerektirebilir | Türkçe knowledge/reasoning capability |
| `xnli` family | EN/TR dahil | mevcut | matched NLI: `TR` manipulation, `EN` retention |
| `xquad` | TR dahil | mevcut | isteğe bağlı reading comprehension |
| `xcopa` | TR dahil | mevcut | isteğe bağlı causal commonsense |
| EWOK | — | current main task README'de bulunmadı | external/custom task veya Max'ten exact source beklenir |
| Turkish HellaSwag | — | current standard catalogda bulunmadı | varsa external source doğrulanmalı; otomatik çeviri primary yapılmamalı |

Exact CLI task adları, prompt templates, few-shot sayısı ve metric'ler upstream commit pinlendikten
sonra `lm-eval ls tasks` ve `lm-eval validate` çıktısıyla dondurulmalıdır. Özellikle XNLI için
`xnli_tr` / `xnli_en` adları doğrulanmadan kontrata literal yazılmamalıdır.

Upstream kaynaklar:

- [LM Evaluation Harness repository](https://github.com/EleutherAI/lm-evaluation-harness)
- [Task catalog](https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks)
- [TurkishMMLU task README](https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/turkishmmlu/README.md)

## 8. OLMo için önerilen evaluation-first akış

Yeni OLMo işi doğrudan başka bir outcome-aware training rerun ile başlamamalıdır:

### Phase E0 — evaluator parity

- exact LM Evaluation Harness commit'ini pinle;
- base OLMo üzerinde resmî `wikitext` task'ını çalıştır;
- mevcut custom WikiText sonucu ile scored text/token/word/byte ve final metric düzeyinde karşılaştır;
- Pile-10k custom task'ını validate et;
- Turkish/English task listesini base modelde smoke-run et.

### Phase E1 — historical checkpoint backfill

Mevcut OLMo checkpoint `0/42/84/126/168/210/252` için:

- harness WikiText word/byte PPL ve BPB;
- Pile-10k;
- cheap English capability paneli;
- mevcut fact-access sonuçları

tek tabloda birleştirilir. Bu, yeni training yapmadan önce Max'in istediği başlangıçtan sona
trajectory'nin büyük bölümünü üretir.

### Phase E2 — gerekirse yeni high-frequency trace

Historical checkpoint yoğunluğu yetersizse, yeni bir run ancak frozen grid ile açılır. Her epoch
veya sabit update interval'ında aynı cheap panel çalışır; tam hard suite yalnız precommitted
milestone'larda çalışır.

## 9. Training setup incelemesi

Mevcut OLMo run'ı Document 160'a göre:

```text
model                 = allenai/OLMo-2-0425-1B
epochs / updates      = 36 / 252
checkpoint grid       = 42,84,126,168,210,252
microbatch            = 5
gradient accumulation = 100
effective batch       = 500 rows
```

Max'e gönderilecek paket bunlara ek olarak exact training config'den şunları çıkarmalıdır:

- maximum sequence length / block size;
- padding/truncation tarafı ve gerçek supervised-token oranı;
- tokens per microbatch, optimizer step ve epoch;
- LR, scheduler, warmup, weight decay, optimizer, precision;
- model başına memory-safe microbatch ve accumulation;
- effective examples/update yanında effective tokens/update.

Batch size önemlidir: küçük modeller için microbatch düşürülebilir ve HU'da gradient accumulation
ile hedef effective batch korunabilir. Ancak `effective batch = 500 rows` tek başına yeterli
karşılaştırma değildir; sequence length ve padding farklıysa gerçek token budget değişir. Yeni
kontrat model başına hem row-batch'i hem effective tokens/update'ı raporlamalıdır.

Sequence length de outcome'u etkileyebilir. Çok kısa block:

- WikiText/Pile long-context retention ölçümüne uymayabilir;
- corpus adaptation sırasında document context'ini kesebilir;
- synthetic fact promptlarında truncation üretmese bile genel LM davranışını farklı etkileyebilir.

Bu nedenle block size değişikliği gerekiyorsa ayrı ablation'dır; mevcut run'larla sessizce
karıştırılmamalıdır.

## 10. M2-A / M2-B için zaman ve deney sırası

Supervisor yönüne göre projenin kalan zamanının en büyük kısmı ana causal comparison'a ayrılır:

```text
M1 / initial state
    synthetic English facts

M2-A
    fact-free Turkish vngrs adaptation

M2-B
    same Turkish adaptation budget
    + controlled synthetic Turkish factual re-exposure
```

İki arm aynı M1 checkpoint'inden başlayan paralel siblings olmalıdır; M2-B, M2-A'nın continuation'ı
olmamalıdır. Token budget, optimizer, sequence length, sampling ve checkpoint grid matched olmalı;
tek kontrollü fark Turkish factual re-exposure'dır.

Manipulation check:

- Turkish: TurBLiMP, TurkishMMLU, XNLI-TR ve Turkish held-out corpus metric'leri;
- English retention: WikiText harness, Pile-10k, BLiMP/HellaSwag/XNLI-EN;
- factual transfer/relearning: frozen bilingual hard suite ve branch contrast.

## 11. Revize edilmiş zaman dağılımı

| İş paketi | Kalan efordaki önerilen pay |
|---|---:|
| Evaluator parity + OLMo historical trajectory | %20 |
| vngrs minimum checks + materialization | %10 |
| M2-A / M2-B training ve checkpoint evaluation | %45 |
| Statistical analysis, figures, artifact freeze | %15 |
| Thesis writing ve Max feedback cycle | %10 |

Bu oranlar takvim değil öncelik oranıdır. Corpus audit'in büyüyerek ana deneyi tekrar geciktirmesi
engellenmelidir.

## 12. Repo'ya alınabilecek somut evaluation çıktısı

Evaluation altyapısı güvenilir biçimde tamamlanırsa repo'ya şu dar paket eklenebilir:

- pinned harness commit + lock/environment manifest;
- custom Pile-10k task YAML/adapter;
- frozen task bundle (`wikitext`, BLiMP, HellaSwag, TurBLiMP, XNLI, TurkishMMLU);
- checkpoint trajectory runner;
- one-row-per-checkpoint normalized result schema;
- tests: task validation, token/count reconciliation, base/checkpoint identity, resume safety;
- reproducible command examples ve metric-definition README.

Raw model weights, large dataset caches ve generated evaluation outputs repo'ya pushlanmamalıdır;
bunlar scratch/artifact manifestlerinde tutulmalıdır.

## 13. Max'e gönderilecek kısa teknik paket

Görüşme takibi için iki sayfalık/tek mesajlık paket hazırlanmalıdır:

1. **PPL açıklaması:** formül, current custom evaluator, harness WikiText farkları, ratio ve
   derived retention-score ayrımı.
2. **Training setup:** effective batch, microbatch/accumulation, sequence length, token budget,
   LR/scheduler/precision ve checkpoint grid.
3. **Trajectory örneği:** OLMo `0/42/84/126/168/210/252` fact access + word PPL + byte PPL + BPB.
4. **Yeni eval listesi:** EN ve TR task'ları, metric, few-shot ve expected runtime.

## 14. Açık sorular

1. Max'in göndereceği ek task'ların exact repository/dataset/revision'ları nedir?
2. “EWOK” ile kastedilen exact benchmark hangisidir ve LM Eval adaptörü var mıdır?
3. “jurisdict” notunun exact corpus regex/pattern beklentisi nedir?
4. TurkishMMLU dataset erişimi mevcut mudur; değilse e-posta/izin süresi ne kadardır?
5. XNLI-TR/XNLI-EN için upstream exact task adları ve prompt eşliği nedir?
6. Her epoch full hard suite gerçekten isteniyor mu, yoksa cheap panel + milestone full suite yeterli
   midir?
7. WikiText heading Markdown varyantı yalnız sensitivity analysis olarak mı tutulmalıdır?

## 15. Tek sonraki planlama adımı

Bir sonraki belge, **OLMo LM-Eval parity, historical checkpoint trajectory and M2 evaluation
contract** olmalıdır. Exact harness commit, task registry, dataset revisions, preprocessing,
metrics, checkpoint grid, batch/sequence reporting ve artifact schema dondurulmadan yeni OLMo
training veya M2-A/M2-B training açılmamalıdır.

