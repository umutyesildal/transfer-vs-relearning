# Document 151aw — Literature, Model, Corpus and M2-A/M2-B Roadmap Alignment (TR)

**Tarih:** 2026-08-09, Europe/Berlin  
**Durum:** `DOCUMENTATION ALIGNMENT COMPLETE — NO EXECUTION AUTHORITY`  
**Kapsam:** Literatür haritası, tarihsel roadmap, güncel bilimsel rota ve 151at operasyonel
durumunun tek bir tutarlı karar zincirinde uzlaştırılması

## 1. Amaç

Bu belge aşağıdaki dört kaynağın rollerini ve aralarındaki sınırları netleştirir:

1. `THESIS_RELEVANT_PAPERS_MASTER_MAP_TR.md`: yaşayan literatür sentezi;
2. Document 60: tarihsel M1→M3 yürütme kaydı ve güncel rotaya yönlendirme;
3. Document 145: supervisor realignment sonrasındaki aktif bilimsel plan;
4. Document 151at: yalnız vngrs metadata/footer rotası için dondurulmuş, çalıştırılmamış
   operasyonel düzeltme kontratı.

Bu belge yeni model veya corpus seçmez; indirme, HU/SSH, evaluation, training, Slurm, corpus
materialization ya da 151at execution yetkisi vermez. Tamamlanmış Qwen M2/M3 sonuçlarını veya
151an–151as kronolojik kanıtını değiştirmez.

## 2. Otorite sırası

Çelişki durumunda aşağıdaki sıra kullanılmalıdır:

1. **Tamamlanmış deney sonucu:** Documents 136, 138, 140a, 142 ve 143.
2. **Supervisor realignment:** Document 144.
3. **Aktif bilimsel plan:** Document 145 ve bu uyum belgesi.
4. **Literatür gerekçesi:** `THESIS_RELEVANT_PAPERS_MASTER_MAP_TR.md`.
5. **Operasyonel bounded contract/result zinciri:** Documents 151ag–151at.
6. **Tarihsel plan:** Document 60'ın 2026-08-09 öncesindeki fazları.

Document 60'ın eski SmolLM/Qwen fazları tarihsel kanıttır. Document 145, yeni training'i otomatik
olarak açan bir kontrat değildir. Document 151at ise bütün roadmap'in değil, yalnızca vngrs
metadata/footer route-feasibility alt probleminin kontratıdır.

## 3. Değişmeyen bilimsel sonuç

Tamamlanan Qwen Wikipedia-only pilotunun frozen kararı:

```text
primary_success_criterion_not_met
```

Bu sonuç:

- teknik olarak geçerli bir negative/inconclusive pilot sonucudur;
- Qwen M1'in başarısını veya dört endpoint artifact'inin geçerliliğini iptal etmez;
- Wikipedia-only yaklaşık 1M-token Turkish adaptation'ın gerçek Turkish capability
  manipulation'ı oluşturduğunu kanıtlamaz;
- yeni M2-A/M2-B ailesini otomatik açmaz.

Yeni çalışma eski artifact'leri yeniden adlandırmamalıdır. Tarihsel `M2-clean` ve `M3-fact`, aynı
M1'den başlayan kardeş kollardı; fakat yeni tasarımın daha güçlü corpus, manipulation check ve
matched-replacement koşullarını karşılamadıkları için yeni `M2-A/M2-B` ana deneyiyle eşit
sayılmamalıdır.

## 4. Model rollerinin dondurulmuş yorumu

| Model | Güncel rol | Kesinlikle söylenmemesi gereken |
|---|---|---|
| OLMo-2-0425-1B | Açık provenance nedeniyle öncelikli English-centric aday | Seçilmiş ana model; kesinlikle sıfır Türkçe gördü |
| Pythia-1.4B | Reproducible data-order/checkpoint kontrol adayı | Türkçe exposure'ı adli düzeyde sıfır |
| Falcon-RW-1B | En güçlü açık English-only dokümantasyon sinyaline sahip karşılaştırma adayı | Tokenizer ve Turkish floor denetlenmeden hazır ana model |
| Qwen2.5-1.5B | Tamamlanmış güçlü M1 ve multilingual positive control | Turkish-unseen causal source model |
| StableLM2-1.6B | Yalnız gerekçelendirilirse ikinci-seviye sınırlı aday | Yeni ana model-fishing dalı |
| SmolLM2-1.7B | Değerli negatif karşılaştırma | Yeni ana optimizasyon hattı |
| Gemma-2-2B / Llama-3.2-1B | Tarihsel model-recipe sonuçları | Değişikliksiz recipe ile yeniden açılmış aday |

OLMo, Pythia ve Falcon kısa listedir; hiçbiri seçilmiş değildir. Qwen bu üçüyle aynı causal rolü
oynamaz. Model seçimi ancak exact revision/stage/license, Turkish baseline headroom, tokenizer
davranışı, M1 usability ve önceden dondurulmuş Pareto kuralı birlikte değerlendirildikten sonra
yapılabilir.

## 5. Corpus rollerinin dondurulmuş yorumu

| Corpus/kaynak | Güncel statü | Roadmap rolü |
|---|---|---|
| `vngrs-web-corpus` | `conditional primary materialization candidate` | En çok yerel operational evidence bulunan aday; quality-pass veya selected değil |
| `trwiki-20260601` | frozen cross-domain control | Ana in-domain corpus değil; küçük-doz/domain kontrolü |
| CulturaX | `excluded_access_blocked` | Literatür precedent'i; mevcut projede karşılaştırmalı seçim girdisi değil |
| Turkish OSCAR / mC4 | literature/provenance candidates | Küçük/orta Türkçe model precedent'lerini ve mixed-web seçeneğini denetleme |
| HPLT Turkish / FineWeb2 Turkish | public pipeline/data candidates | Modern provenance, filtreleme ve dedup hatlarını değerlendirme |
| Bella Turca | literature candidate | Exact data/license/access kanıtı çözülmeden yalnız tasarım precedent'i |
| Kumru/MODA/VBART/TURNA/cosmosGPT/SindBERT | model/corpus recipe precedents | Bugünkü exact training corpus'u veya doğrudan materialization adayı oldukları varsayılmaz |

Bu adayların aynı tabloda bulunması, aynı kanıt seviyesinde oldukları anlamına gelmez. Önce exact
identity, lisans, erişim, LID, kalite, dedup, PII, synthetic contamination, benchmark overlap ve
model-tokenizer yield kanıtı gerekir.

## 6. 151at'ın roadmap içindeki sınırlı yeri

Document 151at SHA-256:

```text
d846b3636aa4d55b4fdf95eebf00241ed6c85e6243b3c6a54dbd99bc546576fa
```

151at, ilk direct immutable vngrs route'unun HTTP 302 dönmesi üzerine zero-or-one-hop Hugging Face
CDN/Xet protokolünü dondurur. Yerel implementation commit'i:

```text
de4a14e3370326173bdf04ce33356aae7826ddda
```

Bu commit yerelde doğrulanmış fakat henüz push/publish edilmemiştir. Dolayısıyla gelecekteki tek
bounded execution authorization, doğrudan HU execution ile başlayamaz. Önce aşağıdaki operasyonel
zinciri açıkça kapsamalıdır:

1. local ve remote base kimliklerinin yeniden doğrulanması;
2. yalnız `de4a14e...` commit'inin ordinary non-force push ile yayımlanması;
3. HU'daki korunmuş dirty status blob'unun yeniden hash/path-overlap denetimi;
4. yalnız koşullar değişmemişse `merge --ff-only` ile senkronizasyon;
5. zorunlu storage/path/inode ve independent-writer preflight;
6. 151at semantiğiyle tek bounded metadata/footer execution;
7. sonuç/gate belgeleri olarak yalnız rezerve 151au/151av'ın oluşturulması.

Bu zincir ayrıca ve açıkça yetkilendirilmeden hiçbir adım çalıştırılmaz. Başarılı olması yalnız
vngrs route/footer feasibility alt kapısını kapatabilir; corpus selection, sample quality,
measurement design veya training readiness üretmez.

## 7. Güncel bilimsel yürütme sırası

### R0 — Literatür ve provenance reconciliation

- OLMo/Pythia/Falcon/Qwen exact model ve tokenizer revision kayıtları;
- model stage, lisans ve yalnız kaynağın desteklediği dil-exposure ifadeleri;
- corpus adayları için “training precedent”, “public data candidate” ve “control” ayrımı.

### R1 — Ölçüm tasarımını dondurma

- held-out Turkish BPB/PPL split'i;
- base-compatible Turkish linguistic/capability paketi;
- benchmark revision/item hash/license/overlap ve floor/ceiling kuralları;
- EN PPL ve M1 EN→EN retention guardrail'leri.

### R2 — Sınırlı M1 usability screen

- en fazla üç English-centric aday ve Qwen control;
- aynı 500-fact population ve evaluator;
- en fazla iki literatür-gerekçeli recipe;
- sonuç görülmeden dondurulmuş endpoint/threshold/Pareto kararı;
- seçilen English-centric model için ikinci-seed doğrulaması.

### R3 — Corpus seçimi ve facts-free dose ladder

- en az bir corpus'un exact snapshot/quality/contamination kapılarını geçmesi;
- yalnız M2-A-benzeri, hedef factsiz Turkish CPT;
- Turkish BPB/PPL + bağımsız capability gain + English/M1 retention ile en küçük etkili dozu
  seçme;
- factual TR→EN sonucu doz seçiminde kullanılmaz.

### R4 — Ana M2-A/M2-B kardeş ailesi

Her M1 seed'i için:

```text
aynı frozen M1
├── M2-A: general Turkish corpus, target facts yok
└── M2-B: aynı toplam bütçe; matched neutral Turkish rows yerine target-fact rows
```

İki kol aynı tokenizer, corpus base pool/order, seed, optimizer, scheduler, sequence length,
toplam token, update, endpoint-selection rule ve evaluation paketini kullanır.

Birincil estimand'ler:

```text
Transfer   = TR→EN(M2-A) - TR→EN(M1)
Relearning = TR→EN(M2-B) - TR→EN(M2-A)
```

EN→EN retention zorunlu guardrail; TR→TR ikincil lexicalization; EN→TR yalnız exploratory'dir.

### R5 — Ölçek kararı

25.000 fact veya ikinci tam model zinciri ancak 2.500-fact ana aile yorumlanabilir bir estimand
üretirse ve ölçek değişiminin yanıtlayacağı soru önceden yazılırsa açılır.

## 8. Güncel kapılar

```text
vngrs route operational gate = blocked_by_operational_access
global scientific gate       = blocked_by_measurement_design
corpus contribution          = blocked_by_corpus_selection_or_materialization
ready_to_measure             = false
ready_to_train               = false
```

Henüz seçilmiş English-centric ana model, seçilmiş/materialize edilmiş ana Turkish corpus,
tamamlanmış benchmark measurement freeze veya yetkili training family yoktur.

## 9. Son karar

Roadmap'in doğru okunması şudur:

- tamamlanan Qwen pilotu korunur ve negatif/inconclusive sonuç olarak raporlanır;
- OLMo/Pythia/Falcon kanıt düzeyleri farklı adaylardır; Qwen ayrı bir positive control'dür;
- corpus havuzu genişletilmiştir, fakat yalnız vngrs koşullu materialization adayı statüsündedir;
- 151at operasyonel bir alt problemi düzeltir, bilimsel tasarımı tamamlamaz;
- gerçek sonraki ana deney, manipulation check'ten sonra aynı M1'den başlayan eş bütçeli
  M2-A/M2-B kardeş kollarıdır;
- mevcut durumda hiçbir training başlatılmamalıdır.
