# 151e — Resumed Audit Sonrası Model, Corpus ve Measurement Decision Gate

**Tarih:** 2026-08-07 (Europe/Berlin)  
**İşçi:** LUNA-Worker 2  
**Girdi:** 151a immutable contract + 151d resumed bounded audit result  
**151a SHA-256:** `524c3202df94ec95123bedbd976fe972bc0c2b1baad3eb301356d0b962a10dd4`  
**Final gate:** `blocked_by_measurement_design`

## 1. Gate sonucu

Resumed audit, model/corpus adaylarını daraltacak kanıt üretti; ancak yeni execution contract'ı hazırlamaya yetecek ölçüm bütünlüğü oluşmadı. Bu nedenle hiçbir aday için `ready_to_freeze_*` ve hiçbir aşama için `ready_to_train` sonucu verilmez.

Final verdict, 151a'nın izin verdiği sözlükten aynen seçilmiştir:

```text
blocked_by_measurement_design
```

Bu karar model veya corpus erişiminin tümüyle başarısız olduğu anlamına gelmez. Bounded kanıtın bir bölümü tamamlanmış, fakat aşağıdaki ölçüm kapıları açık kalmıştır.

## 2. Model gate

| Aday | Gate verdict | Rol ve gerekçe | Açık kapı |
|---|---|---|---|
| `allenai/OLMo-2-0425-1B` at `stage1-step140000-tokens294B` | `metadata_conditional` | `a priori preferred candidate` olarak korunur. Exact Hub snapshot `905c75e...` ve config/tokenizer/weight metadata çözüldü; küçük tokenizer çalıştı. | Exact revision API'sinde license/cardData yok; exact revision lisans/provenance kanıtı tamamlanmadan selected primary model ilan edilemez. |
| `tiiuae/falcon-rw-1b` at `e4b9872bb803165eb22f0a867d4e6a64d34fce19` | `metadata_conditional` | Secondary English-only provenance comparator; Turkish exposure yok varsayımı yapılmaz. Apache-2.0 card, exact revision, config ve safe tokenizer kanıtlandı. | Custom remote runtime kodu çalıştırılmadı; full model compatibility ve revision-level runtime davranışı koşullu. |
| `Qwen/Qwen2.5-1.5B` at `8faed761d45a263340a0528343f099c05c9a4323` | `metadata_pass` | Mevcut frozen Qwen zincirinin multilingual/Turkish positive control'ü. Yeni bir “Turkish unseen” baseline değildir. | Bu audit sonucu Qwen ile yeni training yetkisi doğmaz; mevcut scientific role korunur. |

### Model seçimi

Bir sonraki tasarım açısından çalışma sırası değişmeden kalır: OLMo `a priori preferred candidate`, Falcon secondary comparator, Qwen positive control. Fakat bu sıralama `metadata_conditional` ve `metadata_pass` statüleridir; M1 screening contract'ı veya training readiness değildir. OLMo lisans/provenance kapısı ve Falcon runtime koşulu kapanmadan model tarafı tamamlanmış sayılmaz.

## 3. Corpus gate

| Corpus | Gate verdict | Kullanılabilir bilimsel rol | Açık kapı |
|---|---|---|---|
| `vngrs-ai/vngrs-web-corpus` | `quality_conditional` | Bounded sample'da %98.29 Turkish ve ölçülebilir quality/LID/fertility sonucu verdiği için web adayları içinde mevcut en güçlü gözlenen adaydır. | Sample 3,400 dokümanda 66 HTTP 429 ile kesildi; full shard/coverage, benchmark contamination ve synthetic inventory reconciliation yok. |
| `uonlp/CulturaX` Turkish | `quality_conditional` with `blocked_by_access_condition` substatus | Card metadata'sında Turkish config var; sayısal kalite sonucu verilmedi. | `gated=auto`/access condition ve rows probe HTTP 429 nedeniyle sample yok; exact Turkish shard manifesti ve sample olmadan selection yapılamaz. |
| frozen `trwiki-20260601` | `quality_conditional` | Frozen Wikipedia control; seed-42 sample, LID, quality ve bounded dedup ile karşılaştırma kontrolü. | Mixed-language sample ve contamination/benchmark measurement kapıları açık; yeni web corpus adayı gibi yorumlanamaz. |

### Corpus seçimi

`vngrs` conditional web shortlist olarak, `trwiki-20260601` frozen control olarak korunur. CulturaX erişim/sample kanıtı oluşmadan CulturaX–vngrs arasında seçim yapılmaz. Bu tur M2-A (genel Türkçe corpus) veya M2-B (controlled factual re-exposure) için corpus freeze etmez; iki arm da sonraki ayrı execution contract'ına bırakılır.

## 4. Measurement gate

| Measurement gate | Durum | Karar etkisi |
|---|---|---|
| Model exact revision/config/tokenizer/weight metadata | Kısmen tamamlandı | Qwen pass; OLMo/Falcon conditional. |
| CulturaX Turkish bounded sample | Tamamlanmadı; access/429 | CulturaX quality pass ve corpus selection yasak. |
| vngrs/trwiki bounded LID ve quality | Tamamlandı | Yalnız conditional diagnostic; full-source purity/quality iddiası yok. |
| Exact/near dedup | Bounded tamamlandı | MinHash doc başına 512 feature cap; full clean-overlap iddiası yok. |
| Web cross-source overlap | Kısmen tamamlandı | vngrs–trwiki ölçüldü; CulturaX yok. |
| Synthetic inventory | Bloklu/uyuşmaz | Declared 25,000 fact / 713 object ile erişilebilir 50,000 bilingual fact-row / 829 surface ayrıştırılamadı; 65,717 pattern ve alias listesi materialize değil. |
| Benchmark contamination | Bloklu | Exact revision + item-set + hash yok; clean claim yasak. |
| True BPC/bpb/PPL | Bu kapsamda yok | Fertility yalnız budget diagnostic; inference/evaluator sonucu değil. |
| Turkish capability baseline | Bu kapsamda yok | Model weights/training/evaluation yapılmadı; source provenance ile capability improvement karıştırılamaz. |

Synthetic sayım uyuşmazlığı ve benchmark hash eksikliği, audit'in yalnız operational access ile çözülebilecek bir eksik olmadığını; measurement design'ın yeniden dondurulması gerektiğini gösterir. Bu nedenle final gate `blocked_by_measurement_design` olarak korunur.

## 5. 152/153 yetkilendirme kararı

Bu gate altında:

- Document 152 oluşturulmadı.
- Document 153 oluşturulmadı.
- Document 154 oluşturulmadı.
- 152/153 için “hazırlanabilir” veya “execution-ready” iddiası verilmedi.

152/153 ancak şu kanıtlar yeni, açık bir kullanıcı yetkisi ve ayrı frozen contract ile tamamlandıktan sonra değerlendirilebilir:

1. OLMo exact revision lisans/provenance kanıtı ve Falcon runtime compatibility koşulu;
2. CulturaX Turkish sample + immutable shard manifesti veya erişim blokajının bilimsel tasarımda açıkça kabul edilmesi;
3. synthetic inventory'nin 151a declared counts ile yeniden üretilebilir şekilde uzlaştırılması; 65,717 pattern ve alias/fuzzy listelerinin exact manifesti;
4. benchmark item-set/revision/hash registry;
5. near-dedup/overlap kapsamının sonraki measurement contract'ında açıkça full veya bounded olarak dondurulması;
6. M2-A ve M2-B'nin source-model Turkish provenance, capability baseline ve factual re-exposure ölçümlerinin ayrı precommit gate'leri.

Bu koşullar tamamlanmadan yeni factual training family, model download, corpus materialization, GPU evaluation veya HU/Slurm execution başlatılamaz.

## 6. Bilimsel yorum

Bu audit'in güvenli sonucu “en iyi corpus/model bulundu” değil, hangi adayların hangi koşullarda ilerleyebileceğinin ayrıştırılmasıdır. Vngrs örneği yüksek Türkçe LID oranı gösterirken web quality ve contamination kanıtı henüz bounded/conditional'dır. Trwiki control'de yüksek mixed oranı, source provenance ile sample purity'nin aynı kavram olmadığını gösterir. Qwen positive control olarak Turkish capability zincirini sabitler; OLMo ve Falcon için kaynak-model Turkish provenance sorusu açık kalır. Fertility budget'ı Falcon'un daha yüksek token maliyetini, Qwen/OLMo'nun ise sample üzerinde daha düşük token/word değerlerini gösterir; bunlar model kalite veya transfer iddiasına çevrilemez.

Dolayısıyla sonuç paketi bilimsel olarak kapatılmış bir model/corpus freeze değil, sonraki contract'ın ölçüm önkoşullarını donduran bir audit kapanışıdır. No cleanup uygulandı; 151a, 151b, 151c ve scratch evidence korunmaktadır.
