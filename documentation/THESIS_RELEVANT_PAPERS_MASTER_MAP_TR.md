# Transfer mı, Yeniden Öğrenme mi? Tez İçin Kapsamlı Literatür Haritası

**Proje:** *Transfer vs. Relearning in Cross-Lingual Factual Adaptation*  
**Araştırmacı:** Umut Yunus Yesildal  
**Tarama ve sentez tarihi:** 9 Ağustos 2026  
**Dil:** Türkçe  
**Belge türü:** Yaşayan literatür haritası ve tez-yazım rehberi; deney yürütme yetkisi değildir  
**Ana yerel kaynak:** [Expose.pdf](Expose.pdf)

> [!IMPORTANT]
> Bu dosya literatürü ve mevcut proje kanıtını sentezler. Yeni model/corpus indirme, HU erişimi,
> değerlendirme, eğitim veya Slurm çalıştırma yetkisi vermez. Güncel operasyonel kapılar için
> [Document 151at](151at_BOUNDED_HUGGINGFACE_CDN_REDIRECT_SEMANTICS_CORRECTION_CONTRACT_TR.md)
> ve kronolojik proje kayıtları yetkilidir. Mevcut genel durum hâlâ
> `blocked_by_measurement_design`; `ready_to_measure=false` ve `ready_to_train=false`.

> [!NOTE]
> Geri yüklenen kapsamlı haritanın literatür içeriği korunmuştur; model/corpus adları bir seçim listesi değil,
> kanıt rolleri farklı bir araştırma havuzudur. Güncel rol ve otorite uzlaştırması için
> [Document 151aw](151aw_LITERATURE_MODEL_CORPUS_AND_M2A_M2B_ROADMAP_ALIGNMENT_TR.md) kullanılmalıdır.
> OLMo/Pythia/Falcon screening adayları, Qwen multilingual positive control; vngrs koşullu
> materialization adayı, trwiki kontrol ve CulturaX access-blocked literatür karşılaştırmasıdır.

## 1. Bir dakikalık sonuç

Tezin savunulabilir bilimsel sorusu şudur:

> İngilizce öğrenilmiş ve İngilizcede geri getirilebilir olduğu doğrulanmış sentetik olgular,
> hedef olguların Türkçe uyarlama verisinde hiç yer almadığı durumda yalnızca genel Türkçe
> dil uyarlaması sayesinde **TR→EN** yönünde daha erişilebilir hâle geliyor mu; yoksa gözlenen ek
> erişim aynı olguların Türkçe uyarlama sırasında kontrollü yeniden gösterilmesine, yani
> **reaffirmation/relearning** etkisine mi bağlı?

Literatürün ortak mesajı nettir:

1. Bir modelin bir olguyu bir dilde bilmesi, onu başka dilde güvenilir biçimde çağırabildiği
   anlamına gelmez. Bu sonuç farklı veri kümeleri, model aileleri ve ölçülerde tekrar eder
   [P01–P12].
2. Hedef dilde performans artışı tek başına bilgi transferi kanıtı değildir. Dil yeterliği,
   eğitim verisindeki aynı bilginin önceden bulunması, yüzeysel prompt ipuçları ve hedef dilde
   yeniden öğrenme aynı skoru üretebilir [P05, P10, P13–P17].
3. Continued pretraining (CPT) hedef dil yeterliğini artırabilir; fakat source-language unutma,
   zayıf cross-lingual conductivity ve tokenizer/corpus etkileri yaratabilir
   [P14–P20, P35–P46, P53–P58].
4. Olgu “depolama” ile çeşitli promptlardan “çıkarma” aynı şey değildir. Paraphrase çeşitliliği,
   relation binding, aday sıralaması ve eğitim frekansı kritik belirleyicilerdir [P24–P34].
5. 2025–2026 çalışmaları tezin yakın komşularını çoğaltmıştır: ECLeKTic ve LiveCLKTBench
   transferi daha temiz ölçmeye; Zhang et al. kültürel transferi CPT altında ayrıştırmaya;
   Zhao et al. domain adaptation sırasında edinim ve transfer dinamiklerini izlemeye çalışır
   [P10, P13, P15, P16]. Buna rağmen taranan çalışmalarda aşağıdaki bileşim bulunmamıştır:

   - İngilizce-only kontrollü M1 factual acquisition,
   - M1'de kaynak dil retrieval kapısı,
   - aynı M1 checkpoint'inden başlayan kardeş Türkçe CPT kolları,
   - aynı toplam token/update bütçesi,
   - yalnızca bir kolda neutral Türkçe satırların kontrollü hedef-olgu satırlarıyla değiştirilmesi,
   - `M2-A − M1` transfer kestirimi ile `M2-B − M2-A` relearning kestiriminin ayrılması,
   - English retention ve gerçek Türkçe capability manipulation check'in aynı pakette ölçülmesi.

Bu nedenle güçlü fakat temkinli özgünlük iddiası “cross-lingual factual transfer ilk kez
inceleniyor” değildir. Savunulabilir iddia, **Türkçe language adaptation altında transfer ile
hedef-dil factual re-exposure etkisini eş bütçeli kardeş kollarla ayıran kontrollü nedensel tasarım**
olmalıdır.

## 2. Kapsam ve araştırma yöntemi

### 2.1 İncelenen kaynaklar

Bu harita aşağıdaki kanıt katmanlarını birlikte kullanır:

- `documentation/Expose.pdf` dosyasının 10 sayfasının metinsel ve görsel incelemesi;
- projenin master handoff'u, tamamlanan Qwen M2/M3 sonucu, bağımsız inceleme, bilimsel
  realignment, model/corpus/measurement audit'leri ve en güncel gate belgeleri;
- workspace içindeki 21 paper PDF'i;
- ACL Anthology, OpenReview, arXiv, resmi model kartları ve resmi dataset kartlarındaki birincil
  kaynaklar;
- 9 Ağustos 2026'ya kadar yayımlanmış veya kamuya açık hâle gelmiş ilgili 2025–2026 çalışmaları.

### 2.2 Arama eksenleri

Aramalar şu kavram aileleriyle yapıldı:

- `cross-lingual factual knowledge`, `knowledge transfer`, `knowledge conductivity`,
  `multilingual factual consistency`;
- `language adaptation`, `continued pretraining`, `target language adaptation`,
  `catastrophic forgetting`;
- `synthetic facts`, `fictitious knowledge`, `knowledge acquisition`, `paraphrase robustness`;
- `Turkish LLM adaptation`, `Turkish corpus`, `Turkish benchmark`, `tokenizer fertility`;
- `cross-lingual knowledge editing`, `unlearning`, `fact injection`;
- `OLMo`, `Pythia`, `Falcon-RW`, `Qwen2.5` provenance ve training-data açıklığı.

### 2.3 Dahil etme ve öncelik ölçütü

| Sınıf | Anlamı | Tezde kullanım |
|---|---|---|
| **A — çekirdek** | Araştırma sorusunu, en yakın tasarımı veya ana ölçüm problemini doğrudan ele alır | Introduction, Related Work ve Discussion'da mutlaka |
| **B — yöntemsel** | CPT, factual acquisition, synthetic data, forgetting, Türkçe adaptation veya ölçüm tasarımını destekler | Methods ve Limitations'da seçici biçimde |
| **C — çevresel** | Editing, unlearning, cultural QA, genel cross-lingual task transfer gibi komşu fakat farklı müdahaleyi inceler | Kapsam sınırını açıklamak için |

Peer-reviewed proceedings makaleleri mümkün olduğunca tercih edildi. Yalnız arXiv/OpenReview'de
bulunan çalışmalar **preprint** veya ilgili venue statüsüyle etiketlendi. Model ve dataset kartları
“paper” gibi bilimsel sonuç kaynağı sayılmadı; provenance veya uygulama girdisi olarak ayrı tutuldu.

### 2.4 “Tüm paperlar” ifadesinin operasyonel anlamı

Hiçbir literatür taraması mutlak olarak tüm yayınları garanti edemez. Buradaki kapsam, tez sorusuna
doğrudan veya yöntemsel olarak yüksek değer taşıyan çalışmaların geniş bir haritasıdır. Genel
multilingual NLP, sıradan cross-lingual classification/NER transferi, machine translation ve RAG
çalışmaları yalnızca factual adaptation sorusuna somut bir bağlantı sunduklarında dahil edilmiştir.

## 3. Exposé ne söylüyor, proje bugün nerede?

### 3.1 Exposé'deki özgün tasarım

[Expose.pdf](Expose.pdf) şu yapıyı önerir:

- küçük/orta, İngilizce-merkezli bir base model;
- İngilizce sentetik subject–relation–object olgularıyla M1 bilgi edinimi;
- yalnız İngilizcede geri getirilebilen olguların transfer analizine alınması;
- **Branch A:** hedef olgular olmadan Türkçe adaptation;
- **Branch B:** aynı olguların Türkçe tekrarlandığı adaptation;
- opsiyonel **Branch C:** yalnız Türkçede tanıtılan yeni olgular;
- İngilizce ve Türkçe direct/paraphrase probing;
- accuracy, transfer gain, reaffirmation gain, English retention, frequency ve name analizleri.

Bu mantık hâlâ tezin özüdür. Güncel proje dili Branch A/B yerine sibling arms `M2-A` ve `M2-B`
kullanır; sonraki ana deneyde `M2-B`, ek token almak yerine `M2-A` bütçesindeki neutral Türkçe
satırların bir kısmını eşlenmiş Turkish target-fact satırlarıyla değiştirmelidir.

### 3.2 Tamamlanan Qwen pilotu

Qwen2.5-1.5B üzerinde tamamlanan Wikipedia-only pilotu, yöntemin çalıştırılabilirliğini gösteren
geçerli fakat negatif/inconclusive bir ön çalışmadır. Ayrıntılı otorite:
[Document 136](136_QWEN_M2_M3_ENDPOINT_EVALUATION_GPU_ALLOCATION_STATUS.md) ve
[Document 138](138_QWEN_M2_M3_COMPLETED_MILESTONE_AND_SCIENTIFIC_INTERPRETATION_EN.md).

| State | Seed | EN→EN (%) | TR→EN (%) | TR→TR (%) |
|---|---:|---:|---:|---:|
| M1 | 42 | 99.29 | 52.03 | 29.05 |
| M2-clean | 42 | 98.05 | 33.29 | 22.46 |
| M3-fact | 42 | 98.22 | 35.14 | 24.04 |
| M1 | 43 | 99.24 | 52.52 | 30.12 |
| M2-clean | 43 | 96.24 | 33.70 | 23.25 |
| M3-fact | 43 | 96.95 | 35.59 | 24.97 |

Pilotun doğru yorumu:

- genel Türkçe Wikipedia CPT'si TR→EN retrieval'ı iki seed'de yaklaşık 18.7–18.8 puan düşürdü;
- factual re-exposure kolu clean kola göre TR→EN'de +1.86 ve +1.89 puan toparlandı;
- pre-registered Branch interaction seed 42'de +0.25 puan, güven aralığı sıfırı içeriyor;
- seed 43'te +1.35 puan ve pozitif güven aralığı var;
- iki-seed ana başarı kapısı geçmedi: `primary_success_criterion_not_met`;
- bu sonuç transfer kanıtı veya tekrarlanmış relearning kanıtı değildir; Wikipedia-only düşük
  dozun Türkçe erişimi gerçekten artırdığı da gösterilmemiştir.

Bağımsız inceleme sonucu **PASS WITH CONCERNS**'dır
([Document 140a](140a_QWEN_M2_M3_INDEPENDENT_REVIEW_RESULT_EN.md)). Yani kanıt zinciri geçerli,
fakat iddia sınırı dar tutulmalıdır.

### 3.3 Güncel ana tasarım ve estimand'ler

Supervisor-driven realignment
([Document 144](144_SUPERVISOR_FEEDBACK_AND_SCIENTIFIC_REALIGNMENT_TR.md),
[Document 145](145_LITERATURE_FIRST_M1_MODEL_AND_TURKISH_ADAPTATION_ROUTE_TR.md)) şu bilimsel
mantığı dondurmayı amaçlar:

| Kestirim | Tanım | Yorum |
|---|---|---|
| **Transfer** | `TR→EN(M2-A) − TR→EN(M1)` | Hedef olgu Türkçe adaptation verisinde yokken genel Türkçe adaptation'ın mevcut İngilizce factual access'i değiştirip değiştirmediği |
| **Relearning / reaffirmation** | `TR→EN(M2-B) − TR→EN(M2-A)` | Aynı toplam bütçede Türkçe hedef-olgu re-exposure'ın ek etkisi |
| **Source retention** | `EN→EN(M2-*) − EN→EN(M1)` | İngilizce factual knowledge korunumu/unutturma |
| **Target lexicalization** | `TR→TR` | Türkçe cevap üretimi; ana transfer ölçüsü değil |
| **Reverse exploratory** | `EN→TR` | Cevap dilini Türkçe yapmanın ek bariyeri |

`TR→EN` birincildir; çünkü soruyu Türkçeleştirirken cevabı İngilizce tutarak target-language
comprehension/access değişimini Türkçe object lexicalization yükünden kısmen ayırır. Bu ayrım
özellikle [P09] ile güçlü biçimde desteklenir.

## 4. Çekirdek literatür matrisi

### 4.1 Multilingual factual recall, consistency ve transfer

| ID | Kaynak ve durum | En alakalı kısımlar | Ana bulgu | Bizim projeye bağlantı | Sınır / kopyalanmaması gereken çıkarım |
|---|---|---|---|---|---|
| **P01** | [LAMA: Language Models as Knowledge Bases?](https://aclanthology.org/D19-1250/) — EMNLP-IJCNLP 2019 | §3–5, probing setup ve results | Cloze promptlarla parametric factual knowledge probing'i kurar | Subject–relation–object probe geleneğinin başlangıç noktası | Tek prompt başarısı robust knowledge değildir |
| **P02** | [X-FACTR](https://aclanthology.org/2020.emnlp-main.479/) — EMNLP 2020 | Dataset/multilingual probing, multi-token decoding | Çokdilli factual recall dil ve decoding biçimine duyarlıdır | Türkçe ve İngilizce parallel probe gereğini destekler | Masked LM ve doğal Wikipedia facts; causal synthetic setup değil |
| **P03** | [mLAMA](https://aclanthology.org/2021.eacl-main.284/) — EACL 2021 | Multilingual LAMA construction, results | Çokdilli modellerde bilgi erişimi diller arasında eşit değildir | EN/TR sonuçlarını ayrı raporlama gerekçesi | Doğal facts ve pretraining contamination kontrolü zayıf |
| **P04** | [Factual Consistency / mParaRel](https://aclanthology.org/2022.findings-acl.240/) — Findings ACL 2022 | Dataset ve multilingual consistency experiments | Paraphrase inconsistency İngilizce dışı dillerde daha yüksektir | Direct + paraphrase ve robust-intersection kapısını destekler | Encoder/masked-LM sonuçları decoder-only modellere nicel taşınmaz |
| **P05** | [Cross-Lingual Consistency of Factual Knowledge](https://aclanthology.org/2023.emnlp-main.658/) — EMNLP 2023 | §3 RankC; §5–6; §7 editing case; Limitations | Model ölçeği accuracy'yi artırsa da consistency'yi garanti etmez; vocabulary overlap önemlidir | Tek dil accuracy yerine paired state, cross-language consistency ve uncertainty | Küçük editing case'i adaptation mekanizması kanıtı değildir |
| **P06** | [Polyglot or Not?](https://aclanthology.org/2023.emnlp-main.691/) — EMNLP 2023 | §3–6, özellikle dataset ve script/model analyses | 20 dilde 303K gerçek/counterfactual association; İngilizce-dışı factual açıklar ve script etkisi | Candidate-ranking ve model-family karşılaştırmalarını motive eder | Natural facts; exposure kaynağı bilinmiyor |
| **P07** | [Language Representation Projection](https://aclanthology.org/2023.emnlp-main.226/) — EMNLP 2023 | LRP2 yöntemi; X-FACTR/mLAMA experiments | İngilizce-benzeri temsil projeksiyonu bazı dillerde retrieval'ı artırır | Erişim bariyerinin temsil/arayüz bileşeni olabileceğini gösterir | İnference-time modül; CPT veya relearning değil |
| **P08** | [Tracing the Roots of Facts](https://aclanthology.org/2024.eacl-long.127/) — EACL 2024 | §3–4; §5 factual neurons; §6 roots-to-data; Limitations | Independent, shared ve transferred fact biçimleri; transfer var ama sınırlı | Fact provenance, source exposure ve “shared ≠ transferred” ayrımı | mBERT/mLAMA ve Wikipedia co-occurrence proxy'si |
| **P09** | [Lost in Multilinguality](https://aclanthology.org/2025.acl-long.253/) — ACL 2025 | §5 latent states/information flow; §6 cause; §7 linear shortcut | Kavram orta katmanlarda erişilebilirken son dil-output dönüşümünde kaybolabilir | `TR→EN` ile `TR→TR` ayrımının en güçlü mekanistik gerekçesi | Linear shortcut ana tez müdahalesi değildir |
| **P10** | [ECLeKTic](https://arxiv.org/abs/2502.21228) — 2025 preprint | Dataset construction; source/target metric; limitations | Tek-dilde Wikipedia varlığını exposure proxy'si yaparak source-known koşullu transfer ölçer | M1 source-retrievable filtresi ve conditional transfer metriğiyle doğrudan akraba | Wikipedia absence gerçek training absence kanıtı değildir; post-training arm yok |
| **P11** | [Language Models' Factuality Depends on the Language of Inquiry](https://arxiv.org/abs/2502.17955) — 2025 preprint | §3 dataset; §4.2 FRS/KTS/X-FaKT; §4.3–4.4 | 10K ülke olgusu ve 13 dilde factuality güçlü biçimde soru diline bağlıdır | Global average yerine dil-yönü ve fact-conditional ölçüm gereği | Country facts/templates; kontrollü acquisition yok |
| **P12** | [MultiLoKo](https://arxiv.org/abs/2504.10356) — 2025 preprint/OpenReview | Dataset partitions; human vs machine translation; transfer analysis | Yerel bilgi ve soru dili model sıralamalarını ciddi değiştirebilir | Human-validated EN/TR paralellik ve çeviri audit'i için uyarı | Local-cultural benchmark; adaptation müdahalesi yok |
| **P13** | [LiveCLKTBench](https://aclanthology.org/2026.acl-long.694/) — ACL 2026 | §1; §3.1–3.3; §4; Limitations | Model-cutoff sonrası gerçek belgelerle knowledge injection ve source-correct koşullu transfer; yön asimetrisi | Tezin en yakın güncel benchmark komşusu; source acquisition filtresini doğrular | Hedef-dil adaptation ve matched factual re-exposure kolu yok; sentetik olguya yönelik eleştirisi ayrıca ele alınmalı |

### 4.2 Adaptation altında knowledge transfer ve edinim: en yakın çalışmalar

| ID | Kaynak ve durum | En alakalı kısımlar | Ana bulgu | Bizim projeye bağlantı | Kritik fark |
|---|---|---|---|---|---|
| **P14** | [CLiKA: Multilingual Pretraining and Instruction Tuning Improve Cross-Lingual Knowledge Alignment, But Only Shallowly](https://aclanthology.org/2024.naacl-long.339/) — NAACL 2024 | §3 PF/CT/CD; §4; §5; §7 | Continued pretraining hedef dil performansını artırabilir ama diğer dilleri zedeleyebilir; deep conductivity zayıf kalır | “Türkçe skoru arttı = transfer” çıkarımını reddeder; capability ve conductivity ayrı ölçülmeli | Chinese/German case'leri ve farklı model/stage'ler |
| **P15** | [Cross-Lingual Transfer of Cultural Knowledge: An Asymmetric Phenomenon](https://aclanthology.org/2025.acl-short.13/) — ACL 2025 | §2 controlled CPT framework; §3 results; §4 frequency; §5 | From-scratch English base + non-English CPT; bridge/no-bridge farkıyla transfer; kaynak düzeyine göre asimetri | Şeffaf data, sibling-like control ve frequency hipotezi bakımından çok yakın | Manipüle edilen faktör bilingual bridge/co-occurrence; hedef fact re-exposure yok, Türkçe yok |
| **P16** | [Tracing Multilingual Knowledge Acquisition Dynamics in Domain Adaptation](https://aclanthology.org/2026.eacl-long.269/) — EACL 2026 | §2 AdaXEval; §3.2–3.3; §4; §5 | EN/JA biomedical CPT'de monolingual edinim güçlü, cross-lingual artış sınırlı; edinim–unutma trade-off'u ve loss shielding | Training data–evaluation coverage eşleşmesi, checkpoint dynamics ve paraphrase gereğini doğrular | Domain corpus aynı olguları doğal olarak içerir; no-fact vs fact-reexposure sibling estimand yok |
| **P17** | [Crosslingual Capabilities and Knowledge Barriers](https://openreview.net/forum?id=AwRFhS5grK) — COLM 2025 | §2; §3.1–3.2; §4.1–4.2; Appendix D/E | MT/embedding yeteneğine rağmen implicit knowledge barrier; mixed-language fine-tuning bariyeri azaltır | Capability manipulation check'in transfer kanıtı olmadığını, alignment sinyalinin ayrı olduğunu gösterir | Mixed-language FT, yalnız Türkçe general CPT kolundan farklı ve confounding müdahaledir |
| **P18** | [Analyzing the Evaluation of Cross-Lingual Knowledge Transfer](https://aclanthology.org/2024.eacl-long.177/) — EACL 2024 | Challenging setups; analyses; limitations | Yüksek zero-shot skorun task/surface artifact transferinden gelebileceğini gösterir | Relation controls, mixed-language traps ve form generalization kapılarını destekler | Factual CPT değil; genel evaluation critique |
| **P19** | [PreAlign](https://aclanthology.org/2024.emnlp-main.572/) — EMNLP 2024 | Synthetic English/English-clone setup; real-language experiments | Erken explicit alignment cross-lingual skill/knowledge application'ı iyileştirir | Dil arayüzü kurulmadan transferin zayıf kalabileceği hipotezi | Model pretraining mimarisi müdahalesi; mevcut frozen-base CPT karşılaştırması değil |
| **P20** | [Disentangling Continued Pre-Training](https://aclanthology.org/2026.findings-acl.1218/) — Findings ACL 2026 | §4 interface/semantic hub; §5 attention routing; §6 | CPT'de semantic hub korunurken interface katmanları token dağılımına uyarlanır; attention routing kritik | İleri mekanizma çalışması için layer/attention analizini motive eder | Factual transfer ana outcome değil; büyük modeller ve farklı diller |

### 4.3 Controlled factual acquisition, sentetik olgular ve robust retrieval

| ID | Kaynak | Alakalı kısımlar | Tez için alınacak ders | Sınır |
|---|---|---|---|---|
| **P21** | [LAMA](https://aclanthology.org/D19-1250/) | Probe construction/results | Triple tabanlı factual probe temelini sağlar | Robustness tek template ile ölçülemez |
| **P22** | [Are PLMs Symbolic Reasoners over Knowledge?](https://aclanthology.org/2020.conll-1.45/) | Controlled reasoning experiments | Relational bağın ve kompozisyonun ayrıca test edilmesi gerekir | Reasoning sorusu ana transfer estimand'i değil |
| **P23** | [Pre-training Language Models with Deterministic Factual Knowledge](https://aclanthology.org/2022.emnlp-main.764/) | Factual objectives; ParaRel/generalization | Training objective factual capture ve prompt consistency'yi değiştirebilir | Encoder-style pretraining; proje standard causal LM kullanır |
| **P24** | [Physics of Language Models 3.1: Knowledge Storage and Extraction](https://arxiv.org/abs/2309.14316) — preprint | §2; §3; §4; §5; §8 | Çeşitli biography/verbalization olmadan bilgi depolanabilir ama QA ile çıkarılamayabilir | Projenin M1 canonical-form diversity ve robust eight-cell gate'inin temel desteği | Sentetik biyografi ortamı doğal dil genellemesini tam temsil etmez |
| **P25** | [Physics of Language Models 3.2: Knowledge Manipulation](https://arxiv.org/abs/2309.14402) — preprint | §3 retrieval; §4 classification/comparison; §5 inverse search | Retrieval başarısı knowledge manipulation veya inverse query başarısı değildir | Primary outcome'u sade retrieval'da tutup relation controls'ü ayrı raporlamayı destekler | Manipulation görevleri ana tez sorusu değil |
| **P26** | [TOFU](https://arxiv.org/abs/2401.06121) — preprint | §2 fictitious authors; §2.2 metrics; §3–5 | Fictitious entities knowledge-source controlü ve contamination azaltımı sağlar | Synthetic inventory fikrinin yakın yöntemsel kaynağı | Unlearning benchmark; acquisition/transfer değil |
| **P27** | [Synthetic Knowledge Ingestion](https://aclanthology.org/2024.emnlp-main.1196/) — EMNLP 2024 | Synthetic representations; CPT/SFT/RAG experiments | Olgunun eğitimde nasıl verbalize edildiği ingestion başarısını etkiler | Injection yöntemlerini ve factual data formunu karıştırır |
| **P28** | [Instruction-tuned LMs are Better Knowledge Learners](https://aclanthology.org/2024.acl-long.296/) — ACL 2024 | Knowledge learning setup/results | Base ve instruction model factual acquisition davranışı aynı değildir | Ana tez base-CPT estimand'inde instruction tuning'i dışarıda tutmalı |
| **P29** | [How Do Language Models Learn Facts? Dynamics, Curricula and Hallucinations](https://arxiv.org/abs/2503.21676) — preprint | Training dynamics, curriculum, corruption | Fact acquisition plateau'ları ve distribution/frequency etkisi checkpoint eğrisi gerektirir | Farklı sentetik görev; cross-lingual değil |
| **P30** | [Enhancing LLM Knowledge Learning through Generalization](https://aclanthology.org/2025.findings-emnlp.469/) — Findings EMNLP 2025 | Paraphrase-based acquisition/generalization | Aynı answer token'ını çeşitli bağlamlardan tahmin etmek QA extraction'ı destekler | Tek dil ve farklı intervention |
| **P31** | [ParaRel](https://aclanthology.org/2021.tacl-1.60/) — TACL 2021 | §3–6; §8 | Meaning-preserving prompt değişimlerinde factual consistency düşüktür | Forms A–D ve direct/QA robust intersection'ı doğrudan destekler |
| **P32** | [mParaRel](https://aclanthology.org/2022.findings-acl.240/) — Findings ACL 2022 | Multilingual paraphrase results | Non-English paraphrase çeşitliliği ayrıca zorlayıcıdır | Masked LM; Türkçe causal decoding farklıdır |
| **P33** | [UniArk / ParaTrex](https://aclanthology.org/2024.naacl-long.388/) — NAACL 2024 | Debiasing; large paraphrase benchmark | Prompt prior ve object-frequency bias kontrolü gerekir | Projenin synthetic ranking evaluator'ı farklıdır |
| **P34** | [LiveCLKTBench](https://aclanthology.org/2026.acl-long.694/) — ACL 2026 | §1 synthetic-vs-live discussion; §3 | Sentetik olgular güçlü contamination controlü sağlar, fakat mevcut semantik ağla zayıf/çatışmalı bağlanabilir | Sentetik inventory'de relation binding, diverse forms ve M1 source-retrieval gate zorunlu |

### 4.4 Türkçe language adaptation, corpus ve model çalışmaları

| ID | Kaynak | En alakalı kısımlar / sayfalar | Proje açısından değeri | Doğrudan aktarılmaması gereken şey |
|---|---|---|---|---|
| **P35** | [Bridging the Bosphorus](https://aclanthology.org/2024.mrl-1.21/) — MRL 2024 | §§3.1–4.1; Appendix C/F | Türkçe CulturaX CPT dose ladder, BPC ve English forgetting gözlemi; küçük model adaptation örneği | LoRA ve benchmark gain'i transfer kanıtı değildir; English replay yok |
| **P36** | [LlamaTurk](https://aclanthology.org/2024.mrl-1.3/) — MRL 2024 | Continual training, tokenizer extension, evaluation | 273.9M-token Turkish Wikipedia CPT; küçük dozda tokenizer extension riskini gösterir | English retention ve TR→EN factual yön raporlanmaz |
| **P37** | [MODA](https://aclanthology.org/2026.sigturk-1.17/) — SIGTURK 2026 | CPT recipe; evaluation; SFT/merge ayrımı | Qwen2.5-7B üzerinde büyük ölçek Türkçe CPT; stage'leri ayırma dersi | CPT+SFT/merge sonuçları ana base-CPT causal estimand'ine karıştırılamaz |
| **P38** | [VBART](https://arxiv.org/abs/2403.01308) — preprint | Corpus, tokenizer, pretraining | Türkçe corpus ölçeği ve tokenizer fertility/efficiency | Encoder–decoder from-scratch sonuçları decoder-only CPT'ye nicel taşınmaz |
| **P39** | [TURNA](https://aclanthology.org/2024.findings-acl.600/) — Findings ACL 2024 | Data mixture, UL2 training, tasks | Diverse Turkish corpus ve geniş language diagnostics | From-scratch encoder–decoder; English retention/transfer yok |
| **P40** | [CulturaX](https://aclanthology.org/2024.lrec-main.377/) — LREC-COLING 2024 | Collection/filtering/dedup | Çokdilli corpus provenance ve kalite pipeline'ı | Projede erişim blocked; seçilmiş corpus sayılamaz |
| **P41** | [How to Adapt Your PMM to 1600 Languages](https://aclanthology.org/2021.acl-long.351/) — ACL 2021 | Adaptation methods/results | Küçük ve dar corpuslarda basit continued pretraining güçlü baseline olabilir | Encoder ve downstream POS/NER; factual retrieval değil |
| **P42** | [Breaking Language Barriers](https://aclanthology.org/2024.emnlp-main.441/) — EMNLP 2024 | Scaling/replay experiments | Replay'in forgetting regularizer'ı olabileceğini ve CPT ölçek ilişkisini gösterir | Replay oranı projeye aynen alınamaz; iki kolda sabitlenmesi gerekir |
| **P43** | [Arabic Stable LM](https://arxiv.org/abs/2412.04277) — preprint | Data mix, vocabulary, fertility, benchmarks | Büyük ölçek bilingual CPT ve tokenizer-fertility analizi | Arapça/İngilizce 7B ölçeği, 1B Türkçe çalışmaya recipe değildir |
| **P44** | [Sherkala](https://openreview.net/forum?id=wRcTCcb0H5) — OpenReview | Multilingual corpus mix; vocab extension; ablations | Türkçe dahil 45.3B-token mix ve fertility değişimi | Kazakh ana hedefli 8B model; Turkish factual estimand yok |
| **P45** | [DIPLomA](https://aclanthology.org/2025.findings-emnlp.1355/) — Findings EMNLP 2025 | 80:20 target/English CPT; delta merge | Mixed CPT'nin retention düzenleyicisi rolü | Alignment/merge ayrı müdahaledir |
| **P46** | [SambaLingo](https://aclanthology.org/2024.mrl-1.1/) — MRL 2024 | Vocab extension; 1:3 mix; ablations | Turkish fertility 3.28→1.77 örneği; vocab kazanımı task gain garantisi değil | 7B ve multilingual recipe; tokenizer değişimi causal treatment'e karıştırılmamalı |

### 4.5 Türkçe ölçüm ve benchmark literatürü

| ID | Kaynak | Ne ölçüyor? | Tezde önerilen rol | Ana risk |
|---|---|---|---|---|
| **P47** | [TurBLiMP](https://aclanthology.org/2025.emnlp-main.834/) — EMNLP 2025 | 16 fenomen × 1,000 Turkish minimal pair | Exact release/overlap/floor–ceiling audit'i geçerse primary bağımsız linguistic manipulation check | Factual transferi ölçmez; benchmark contamination ve small-model floor'u kontrol edilmeli |
| **P48** | [TurkishMMLU](https://arxiv.org/abs/2407.12402) — preprint | Native Turkish, 9 konu, 10K+ MCQ | Geniş knowledge/reasoning capability, likelihood scoring | Saf dil edinimi değildir; public overlap |
| **P49** | [EXAMS](https://arxiv.org/abs/2011.03080) — preprint | 16 dilde 24K+ lise sınav sorusu | Turkish MCQ secondary capability | Translation/source provenance ve contamination |
| **P50** | [CETVEL](https://aclanthology.org/2026.eacl-long.46/) — EACL 2026 | Turkish understanding, generation ve culture | Base-compatible grammar/morphology altkümeleri koşullu destek | Chat/judge/generation bölümleri base causal gate'e uygun değil |
| **P51** | [TurkBench](https://aclanthology.org/2026.sigturk-1.12/) — SIGTURK 2026 | 8,151 örnek, 21 alt görev, 6 kategori | Kapsam haritası ve koşullu base-compatible altkümeler | Knowledge, reasoning ve instruction etkilerini dil edinimiyle karıştırır |
| **P52** | [TrClaim-19](https://aclanthology.org/2020.conll-1.31/) — CoNLL 2020 | 2,287 Turkish tweet/check-worthiness | Opsiyonel küçük classification diagnostic | Topic ve task confound; ana kapı olmamalı |

Ana measurement sonucu: Türkçe öğrenildiğini yalnız PPL ile söylemek yeterli değildir. Aynı state
paketinde en az Turkish bits-per-byte/BPB, within-model PPL, tokenizer fertility, bağımsız Turkish
linguistic diagnostic, geniş Turkish capability, EN→EN retention ve factual yönler raporlanmalıdır.
Cross-tokenizer model sıralamasında raw PPL kullanılmamalı; fertility ayrı bir erişim/maliyet
tanısıdır.

### 4.6 Catastrophic forgetting ve source-language retention

| ID | Kaynak | Alakalı kısım | Bizim projeye bağlantı | Sınır |
|---|---|---|---|---|
| **P53** | [Don't Stop Pretraining](https://aclanthology.org/2020.acl-main.740/) — ACL 2020 | DAPT/TAPT setup; Tables 5–6 | Continued pretraining'in ayrı bir adaptation evresi olduğunu ve data distribution eşleşmesinin önemini kurar | Monolingual domain classification; language/factual transfer değil |
| **P54** | [Lifelong Pretraining](https://aclanthology.org/2022.bigscience-1.1/) — BigScience 2022 | Continual corpora; retention/transfer metrics | Yeni distribution'a adaptasyon ile eski performans korunmasını birlikte ölçme | Domain stream ve downstream FT; EN/TR synthetic facts değil |
| **P55** | [Overcoming Catastrophic Forgetting in Massively Multilingual Continual Learning](https://aclanthology.org/2023.findings-acl.48/) — Findings ACL 2023 | §2.2 LR Adjust; §3.3 CFT/CBT; §4 | Forward ve backward transferi ayrı ölçme, dil sırası ve LR etkisi | Classification/sequence labeling ve encoder modeller |
| **P56** | [Source-Shielded Updates](https://aclanthology.org/2026.acl-long.865/) — ACL 2026 | §3 SSU; §4–6; conclusion | Hedef dil adaptation'ında source degradation'ın ağır olabileceğini ve seçici güncellemenin koruma sağlayabildiğini gösterir | 7B/13B instruct modeller; SSU ana base full-CPT tasarımının yerine geçmez |
| **P57** | [Bridging the Bosphorus](https://aclanthology.org/2024.mrl-1.21/) — MRL 2024 | §5.3 / retention analysis | Türkçe adaptation sonrası English validation/performance düşüşünü doğrudan raporlar | LoRA ve farklı evaluation; factual EN→EN retention değil |
| **P58** | [Disentangling CPT](https://aclanthology.org/2026.findings-acl.1218/) — Findings ACL 2026 | §4–5 | “Semantic hub korundu” iddiasının state-level factual retention ile doğrulanması gerektiğini düşündürür | Representation mekanizması behavior-level retention garantisi değildir |

Proje için sonuç: `EN→EN` yalnız bir güvenlik metriği değil, estimand'in yorumlanması için zorunlu
bir state variable'dır. `TR→EN` artarken `EN→EN` düşüyorsa net transfer, yeniden yönlendirme ve
unutma birbirine karışabilir. English replay seçilecekse oran iki sibling arm'da aynı olmalı ve
sonuç görülmeden önce dondurulmalıdır.

### 4.7 Cross-lingual knowledge editing ve unlearning: yakın ama farklı müdahaleler

| ID | Kaynak | Alakalı kısımlar | Neden ilgili? | Neden ana emsal değil? |
|---|---|---|---|---|
| **P59** | [Cross-Lingual Knowledge Editing in LLMs](https://aclanthology.org/2024.acl-long.627/) — ACL 2024 | Method, multilingual propagation, locality | İngilizce fact update'in başka dillere yayılmasını doğrudan sınar | Noktasal edit; genel Turkish CPT değil |
| **P60** | [ReMaKE](https://aclanthology.org/2024.acl-long.21/) — ACL 2024 | Retrieval-enhanced multilingual editing | Dil bariyerinde external memory/retrieval'ın rolünü gösterir | Parametric transfer estimand'ini değiştirir |
| **P61** | [Cross-Lingual Multi-Hop Knowledge Editing](https://aclanthology.org/2024.findings-emnlp.701/) — Findings EMNLP 2024 | CroLin-MQuAKE; multi-hop results | Edit propagation ve multi-hop portability sorunlarını gösterir | Multi-hop reasoning + edit; M2 adaptation değil |
| **P62** | [MLaKE](https://aclanthology.org/2025.coling-main.301/) — COLING 2025 | Benchmark/results | Language-family ve parameter ayrışması nedeniyle edit transferi zayıf | Beş dil; Türkçe ve CPT yok |
| **P63** | [Language-Agnostic Factual Neurons](https://aclanthology.org/2025.coling-main.385/) — COLING 2025 | Neuron localization; LU-LAFNs | Aynı fact için paylaşılan neuron kümeleri olabileceğini gösterir | Editor başarısı doğal CPT transferi kanıtlamaz |
| **P64** | [BMIKE-53](https://aclanthology.org/2025.acl-long.798/) — ACL 2025 | 53-language IKE benchmark | Script, model scale ve demonstration alignment etkileri | In-context editing; weight-space acquisition değil |
| **P65** | [BabelEdits](https://aclanthology.org/2025.findings-acl.438/) — Findings ACL 2025 | Alias-aware benchmark; downstream collapse | Entity alias/translation doğruluğu ve model-collapse guardrail'i | Modular ReFT edit; CPT değil |
| **P66** | [Edit Once, Update Everywhere](https://aclanthology.org/2025.findings-acl.1196/) — Findings ACL 2025 | Synchronization framework | Bir dilde update'in çok dillere yayılması için explicit mekanizma gereğini gösterir | Ana tez spontaneous adaptation etkisini ölçer |
| **P67** | [Editing Across Languages: Survey](https://aclanthology.org/2025.emnlp-main.803/) — EMNLP 2025 | Taxonomy; benchmark/gap sections | Editing literatürünün hızlı kapsam haritası | Survey birincil deney kanıtı değildir |
| **P68** | [Evaluating Cross-Lingual Unlearning](https://arxiv.org/abs/2601.06675) — preprint | Benchmark, language-direction leakage | Bir dilde parametric değişimin diğer dillere asimetrik yayılabileceğini gösteren ters problem | Silme/unlearning, acquisition/relearning değil |

Editing ve unlearning literatürü tez için iki şekilde değerlidir: (i) dil yönüne bağlı parametric
yayılımın mümkün ama güvenilmez olduğunu gösterir, (ii) efficacy yanında locality/retention ve
alias robustness raporlamayı öğretir. Fakat bu çalışmalar hedef dilde geniş dağılımlı CPT'nin
nedensel etkisini doğrudan cevaplamaz.

### 4.8 Source model ve corpus provenance kaynakları

Bu kaynaklar factual transfer sonucu değil, deneysel yorumun geçerli olup olmadığını belirleyen
altyapı kanıtıdır.

| Kaynak | Resmî kaynak | Projedeki rol | Kritik uyarı |
|---|---|---|---|
| OLMo 2 | [OLMo 2 paper](https://arxiv.org/abs/2501.00656), [OLMo-2-0425-1B card](https://huggingface.co/allenai/OLMo-2-0425-1B) | Açık provenance'lı primary candidate | English-dominant, “sıfır Türkçe gördü” denemez; exact revision ve baseline headroom gerekir |
| Pythia | [Pythia paper](https://proceedings.mlr.press/v202/biderman23a.html), [1.4B card](https://huggingface.co/EleutherAI/pythia-1.4b) | Data-order/checkpoint reproducibility adayı | Turkish exposure niceliği açık değildir |
| Falcon-RW-1B | [Model card](https://huggingface.co/tiiuae/falcon-rw-1b), [RefinedWeb paper](https://proceedings.neurips.cc/paper_files/paper/2023/hash/fa3ed726cc5073b9c31e3e49a807789c-Abstract-Datasets_and_Benchmarks.html) | En güçlü “English-only” dokümantasyon sinyali | Tokenizer fertility ve Turkish floor riski yüksek olabilir |
| Qwen2.5-1.5B | [Model card](https://huggingface.co/Qwen/Qwen2.5-1.5B), [technical report](https://arxiv.org/abs/2412.15115) | Tamamlanan pilot ve multilingual positive control | 29+ language bilgisi nedeniyle “Turkish unseen” ana aday değildir |
| vngrs web corpus | [Dataset card](https://huggingface.co/datasets/vngrs-ai/vngrs-web-corpus), [MODA](https://aclanthology.org/2026.sigturk-1.17/) | Şimdilik yalnız conditional primary materialization candidate | Quality-pass, selected veya training-frozen değildir |
| Turkish Wikipedia | Resmî Wikimedia dump identity + proje manifestleri | Cross-domain control | Ana in-domain adaptation corpus'u değildir |
| CulturaX | [Paper](https://aclanthology.org/2024.lrec-main.377/) | Literatür karşılaştırması | Projede `excluded_access_blocked`; comparative selection yapılamaz |

Exact model revision'ları ve frozen candidate rolleri için
[Document 151ab](151ab_MEASUREMENT_DESIGN_AUTHORITY_AND_MINIMAL_BASELINE_CONTRACT_TR.md) esas
alınmalıdır. Literatür model seçimini tek başına açmaz.

## 5. En kritik 19 paper için ayrıntılı okuma kartları

### P05 — Qi, Fernández ve Bisazza (2023): Cross-Lingual Consistency

**Önce okunacak:** §3.2 RankC, §5.1–5.2, §6.2 vocabulary overlap, §7 editing case, Limitations.

**Ne gösteriyor?** Aynı factual relation için farklı dillerde doğru tahmin kümelerinin sıralama
uyumunu ölçüyor. Daha büyük modeller genellikle daha doğru olsa da cross-lingual consistency aynı
oranda büyümüyor. Alt-sözcük vocabulary overlap, language-pair consistency ile anlamlı ilişki
gösteriyor. İngilizce ROME edit'inin transferi yüksek RankC dillerinde daha güçlü.

**Teze etkisi:** M1'de source-correct filtresi; dil-yönü bazında paired sonuç; tokenizer fertility ve
lexical overlap'i mekanizma değil moderator olarak tutma; accuracy ve consistency'yi ayırma.

**Kanıtlamadığı:** Türkçe CPT'nin İngilizce factual knowledge'i erişilebilir kıldığı veya target-fact
repetition'ın relearning olduğu.

### P06 — Schott, Furman ve Bhat (2023): Polyglot or Not?

**Önce okunacak:** §3 Task, §4 Dataset, §5 Results, §6 Analysis, Limitations.

**Ne gösteriyor?** Gerçek ve counterfactual 303K association üzerinden 20 dilde encyclopedic
knowledge eşitsizliği; script, model ailesi ve prompt dilinin etkisini gösteriyor. Contrastive
candidate scoring, açık-uçlu generation'ın yüzey sorunlarından bir bölümünü ayırıyor.

**Teze etkisi:** Candidate-ranking evaluator, language-direction reporting, model-family screen ve
Latin-script Türkçenin yine de “kolay transfer” varsayılmaması.

**Kanıtlamadığı:** Knowledge'in hangi dilde edinildiği; doğal olgular contamination'a açıktır.

### P08 — Zhao, Yoshinaga ve Oba (2024): Facts'in kökenini izleme

**Önce okunacak:** §4.1–4.3, §5.1–5.2, §6.1–6.2, Limitations.

**Ne gösteriyor?** mBERT ve mLAMA üzerinde factual traces'i Wikipedia co-occurrence ile
eşleştirerek language-independent, shared ve transferred biçimleri ayırıyor. Bir olgunun hedef dil
verisinde bulunmaması, modelde bağımsız bir temsil olmadığını tek başına göstermez; fakat gerçek
transfer sınırlıdır.

**Teze etkisi:** Source-model Turkish provenance audit'i, target-fact overlap kontrolü ve “ortak
temsil” ile “nedensel transfer” terminolojisini ayırma.

**Kanıtlamadığı:** Decoder-only CPT davranışı veya Turkish adaptation'ın etkisi.

### P09 — Wang et al. (2025): Lost in Multilinguality

**Önce okunacak:** §5.2 latent states, §5.3 information flow, §5.4 concept-space composition,
§6, §7.

**Ne gösteriyor?** Bir factual object'in language-independent concept space içinde seçilebilmesine
rağmen son katmanlarda hedef dil üretimine haritalanamaması mümkün. Linear shortcut bazı
inconsistency'leri düzeltir.

**Teze etkisi:** `TR→EN` primary iken `TR→TR` secondary tutulmalıdır. Bir model Türkçe soruyu
anlayıp İngilizce object'i seçebilir ama Türkçe object'i lexicalize edemeyebilir; tersine Türkçe
answer surface'i ezberleyebilir ama fact binding zayıf kalabilir.

**Kanıtlamadığı:** Genel Türkçe CPT'nin otomatik olarak interface'i düzelttiği.

### P10 — Goldman et al. (2025): ECLeKTic

**Önce okunacak:** dataset construction, source-language correctness filtresi, overall/transfer
metric ve limitations.

**Ne gösteriyor?** Yalnız bir Wikipedia dilinde bulunan sayfaları source exposure proxy'si yapıyor;
384 unique soru ve 12 dil üzerinden source-known olguların target dilde erişimini ölçüyor.

**Teze etkisi:** Transfer denominator'ının M1'de gerçekten öğrenilmiş olgulara koşullanması doğru.
Source ve target doğruluğu aynı metrikte karıştırılmamalı.

**Kanıtlamadığı:** Wikipedia'da olmayan bilginin model pretraining'inde hiç olmadığı; ayrıca hiçbir
target-language adaptation müdahalesi yok.

### P11 — Aggarwal et al. (2025): Language of Inquiry

**Önce okunacak:** §3, §4.2.2–4.2.4, §4.3, §4.4, Limitations.

**Ne gösteriyor?** 10,000 country fact ve 13 dilde FRS, KTS ve cross-lingual transferability
ölçüleriyle factual answer'ın soru diline bağlı kaldığını gösteriyor.

**Teze etkisi:** EN/TR average tek başına verilmemeli; fact-level paired state transitions ve
relation/name/frequency stratification raporlanmalı.

**Kanıtlamadığı:** CPT müdahalesinin nedeni veya sentetik fact acquisition.

### P13 — Guo et al. (2026): LiveCLKTBench

**Önce okunacak:** §1 pp. 15193–15194; §3.1–3.3 pp. 15195–15197; §4; Limitations.

**Ne gösteriyor?** Model cutoff'undan en az altı ay sonraki gerçek-world entity/event belgelerini
source dilde CPT ile enjekte ediyor; source-correct olgular arasında target correctness'i
`Transfer = A/(A+B)` olarak ölçüyor. Beş dilde transfer dil uzaklığına, yöne ve domaine bağlı.

**Teze etkisi:** Bu, “kaynak dilde yeni bilgi öğret → hedef dilde test et” çekirdeğinin en yakın
güncel doğrulamasıdır. Aynı zamanda sentetik facts'in mevcut semantik ağla çatışma/zayıf bağlanma
riskini açıkça gündeme getirir. Projenin yanıtı sentetik olgudan vazgeçmek değil; M1 exact-storage,
candidate-ranking, diverse forms, relation binding ve source-retrievable admission gate'i birlikte
zorunlu kılmaktır.

**Kanıtlamadığı:** Hedef dil yeterliği adaptation ile değiştiğinde transferin nasıl değiştiği veya
target-language re-exposure'ın ek etkisi.

### P14 — Gao et al. (2024): CLiKA

**Önce okunacak:** §3.1–3.2; §4; §5.1–5.3; §7.

**Ne gösteriyor?** Cross-lingual alignment'ı performance (PF), consistency (CT) ve conductivity
(CD) olarak üçe ayırıyor. Continued pretraining trained-language yüzey performansını artırsa bile
other-language damage yaratabilir ve deep conductivity'yi güvenilir biçimde artırmaz.

**Teze etkisi:** Türkçe capability manipulation check, factual transfer outcome ve cross-language
consistency ayrı ölçülmelidir. M2-A'nın Turkish BPB/TurBLiMP iyileştirmemesi hâlinde factual delta
“adaptation enabled access” diye yorumlanamaz.

**Kanıtlamadığı:** Eş bütçeli factual replacement arm'i veya Türkçe özel sonuç.

### P15 — Zhang, Liao ve Feng (2025): Cultural Knowledge Transfer

**Önce okunacak:** §2 framework, özellikle “Decoupling of Transfer Effects”; §3; §4; §5.

**Ne gösteriyor?** Filtrelenmiş English Wikipedia ile from-scratch base, sonra Korean/Chinese/
Tibetan/Mongolian CPT. Aynı veri içeriğinde paralel cümleleri aynı context'e koyan “bridge” ile
ayıran “no bridge” ayarı karşılaştırılıyor. High-resource dillerde daha bidirectional, low-resource
dillerde target→English ağırlıklı asimetri ve frequency ilişkisi bulunuyor.

**Teze etkisi:** Training-data transparency, bilingual parallel probing, direction asymmetry ve
fact-frequency moderators bu tez için doğrudan relevant. Projenin sibling-arm mantığı bu paper'a
benzer biçimde tek bir mekanizmayı izole etmeyi amaçlar.

**Kanıtlamadığı:** Bridge farkı, fact repetition farkı değildir. Kollar aynı total factual exposure'ı
farklı co-occurrence ile sunar; bizim `M2-B − M2-A` contrast'ımız hedef olgunun adaptation verisinde
bulunmasıdır.

### P16 — Zhao et al. (2026): Domain Adaptation Dynamics

**Önce okunacak:** §2.1–2.3 AdaXEval; §3.2–3.3; §4.1–4.2; §5.1–5.2; Limitations.

**Ne gösteriyor?** Training corpus ile evaluation knowledge coverage'ı eşleştiriyor; EN/JA
biomedical CPT'de monolingual paraphrase kazanımları büyükken ilk deneyde interlingual artışlar
sınırlı. State transitions, edinilen ve unutulan fact'lerin birbirini maskeleyebildiğini gösteriyor.
Lexical paraphrase çeşitliliği ve early checkpoint dynamics önemlidir.

**Teze etkisi:** Her endpoint delta'nın acquired/retained/forgotten transition tablosu olmalı;
training–evaluation fact identity hash-bound olmalı; intermediate checkpoint analizi primary gate
değil ama güçlü destekleyici sonuçtur.

**Kanıtlamadığı:** Transfer ile target-side relearning'i no-fact/fact sibling arms yoluyla ayırmaz.

### P17 — Chua et al. (2025): Knowledge Barriers

**Önce okunacak:** §2.1–2.2; §3.1 general knowledge; §3.2 domain knowledge; §4.1–4.2; Appendix D/E.

**Ne gösteriyor?** Explicit MT ve embedding alignment iyi olsa da implicit cross-lingual QA
başarısız olabilir. Basit inference promptları sınırlı; mixed-language WikiText fine-tuning daha
etkili.

**Teze etkisi:** Dil becerisi ölçümü transfer sonucu değildir. Aynı context içindeki bilingual
bridge güçlü ama farklı bir intervention olduğu için ana M2-A corpus'una yanlışlıkla girmemeli.

**Kanıtlamadığı:** Turkish-only CPT veya factual re-exposure estimand'i.

### P20 — Tran et al. (2026): CPT'nin mekanizması

**Önce okunacak:** §4.1–4.3, §5.1–5.3, §6.

**Ne gösteriyor?** Qwen2.5/Llama2 tabanlı farklı dil CPT'lerinde interface katmanları ile daha
language-agnostic semantic hub ayrışıyor; attention component swapping causal biçimde language
adaptation davranışını daha çok etkiliyor.

**Teze etkisi:** Ana behavioral gate tamamlandıktan sonra M2-A/M2-B parameter-delta veya
attention/interface analysis'i mekanizma extension'ı olabilir.

**Kanıtlamadığı:** Semantic hub'da bir fact'in bulunması onun Türkçe prompttan erişilebilir veya
relearning'den ayırt edilmiş olduğu anlamına gelmez.

### P24 — Allen-Zhu ve Li (2023): Storage vs Extraction

**Önce okunacak:** §2; §3; §4.1–4.2; §5.1–5.2; §8.

**Ne gösteriyor?** Kontrollü sentetik biyografilerde eğitim verisi çeşitliliği olmadan bilgi
depolanabilir fakat natural QA extraction başarısız kalabilir; sonradan instruction tuning her
zaman bu açığı kapatmaz.

**Teze etkisi:** M1'in yalnız exact storage ile seçilmemesi, canonical form diversity, unseen
paraphrase, candidate ranking ve robust intersection kapısının bilimsel gerekçesidir.

**Kanıtlamadığı:** Cross-lingual transfer.

### P26 — Maini et al. (2024): TOFU

**Önce okunacak:** §2.1 fictitious authors; §2.2 metrics; §3–5; Limitations.

**Ne gösteriyor?** 200 fictitious author × 20 QA ile knowledge source ve forget/retain setlerini
kontrollü kurar.

**Teze etkisi:** Gerçek-world contamination'dan kaçınmak için fictitious entities kullanma fikrini
destekler; retained facts ve model utility ölçme prensibi English retention'a akrabadır.

**Kanıtlamadığı:** Unlearning başarısının acquisition veya transfer başarısı olduğu.

### P31/P32 — ParaRel ve mParaRel

**Önce okunacak:** ParaRel §3–6; mParaRel dataset ve multilingual results.

**Ne gösteriyor?** Semantik olarak eşdeğer promptlar factual predictions'ı ciddi değiştirebilir;
problem multilingual setting'de daha büyüktür.

**Teze etkisi:** Direct/QA × forms A–D eight-cell robust metric, prompt-level bootstrap ve minimum
cell reporting keyfî değil, literatürün doğrudan gereğidir.

**Kanıtlamadığı:** Her paraphrase'in eş zorlukta veya çevirilerin eş anlamlı olduğu; human audit
ve form counterbalance gerekir.

### P35 — Açıkgöz, Erdoğan ve Yuret (2024): Bridging the Bosphorus

**Önce okunacak:** §§3.1–4.1 ve Appendix C/F.

**Ne gösteriyor?** Mistral-7B ve GPT2-xl Turkish adaptation; CulturaX'tan yaklaşık 0.05B–2.5B
token dose ladder; LoRA ayarları; Turkish BPC/capability artışı yanında English forgetting.

**Teze etkisi:** Wikipedia-only yaklaşık 1M-token pilotun Türkçe manipulation için çok küçük ve
dar olabileceğini, dose ladder ve English retention'ın önceden dondurulması gerektiğini gösterir.

**Kanıtlamadığı:** Turkish gain'in cross-lingual factual transfer olduğu.

### P47 — Başar et al. (2025): TurBLiMP

**Önce okunacak:** benchmark construction, 16 linguistic phenomenon, human judgments, model
results ve limitations.

**Ne gösteriyor?** Turkish word-order flexibility ve morphology/subordination dahil 16 fenomeni
her biri 1,000 minimal pair ile ölçer; güçlü modeller dahi insanlara kolay bazı yapılarda zorlanır.

**Teze etkisi:** Genel Turkish corpus'un gerçekten linguistic capability manipulation'ı yarattığını
factual probe'dan bağımsız ölçmek için en temiz adaydır.

**Kanıtlamadığı:** Factual knowledge veya transfer; exact item revision, license, overlap ve
small-model floor/ceiling audit'i yapılmadan primary kapı olamaz.

### P56 — Yamaguchi et al. (2026): Source-Shielded Updates

**Önce okunacak:** §3.1–3.3; §4.5; §5–6; §7.

**Ne gösteriyor?** Beş target dil ve 7B/13B instruct modelde full fine-tuning source task'larda
ortalama yaklaşık %20–22 degradation yaratırken SSU bunu yaklaşık %3 düzeyine indiriyor ve target
performansını koruyor.

**Teze etkisi:** Qwen pilotundaki TR-involving düşüşün olağan bir adaptation riski olduğunu ve
source retention guardrail'inin zorunluluğunu güçlendirir. SSU daha sonraki ablation olabilir.

**Kanıtlamadığı:** SSU'nun 1B base causal modelde aynı etkiyi yaratacağı veya transfer/relearning
estimand'ini değiştirmeden kullanılabileceği.

### 5.1 Exposé'de bulunan fakat ana matrisin dışında kalmaması gereken mekanizma çalışmaları

| ID | Kaynak | Ana bulgu | Proje bağlantısı |
|---|---|---|---|
| **P69** | [Tracing Multilingual Factual Knowledge Acquisition in Pretraining](https://aclanthology.org/2025.findings-emnlp.113/) — Findings EMNLP 2025 | OLMo-7B checkpointlerinde fact frequency dominant ve büyük ölçüde language-agnostic predictor; cross-lingual transfer daha sınırlı, erken ve özellikle named-entity relation'larda | M1 frequency buckets, checkpoint dynamics, named-object/relation stratification ve OLMo provenance için çekirdek kaynak |
| **P70** | [How Do Multilingual Language Models Remember Facts?](https://aclanthology.org/2025.findings-acl.827/) — Findings ACL 2025 | Subject enrichment daha language-independent, object extraction daha language-dependent; last-token function vector hem query dilini hem çıkarılacak içeriği taşır | `TR→EN`/`TR→TR` ayrımına ve object lexicalization analizine mekanistik destek |
| **P71** | [Beneath the Surface of Consistency](https://aclanthology.org/2025.findings-naacl.475/) — Findings NAACL 2025 | Yüksek behavioral consistency shared representation garantisi değildir; script similarity önemli | Aynı answer'ın iki dilde çıkmasını doğrudan “ortak depolama” diye adlandırmama uyarısı |
| **P72** | [When Language Shapes Thought](https://arxiv.org/abs/2505.24409) — CIKM 2025 | QA'de input dili ve “thought language” uyumu factual erişimi etkileyebilir; Language-to-Thought prompting önerir | Inference-time prompt-language etkisini secondary analysis yapar; CPT etkisiyle karıştırılmamalı |
| **P73** | [Give Me the Facts! A Survey on Factual Knowledge Probing](https://aclanthology.org/2023.findings-emnlp.1043/) — Findings EMNLP 2023 | Factual probing dataset, prompt, metric ve interpretation sorunlarını toplar | Related Work terminolojisini ve probing limitations bölümünü kurmak için referans survey |

P69 özellikle ana tez metninde [P05, P08, P09, P13, P15, P16] ile aynı çekirdek grupta
anılmalıdır. Sonuç, frequency'nin transferle karıştırılmaması gerektiğini doğrudan destekler:
M2-B treatment facts ile M2-A neutral rows, toplam token ve fact-frequency bütçeleri önceden
eşlenmelidir.

## 6. Literatüre göre tezdeki gerçek araştırma boşluğu

### 6.1 En yakın çalışmalarla bileşen karşılaştırması

| Tasarım bileşeni | ECLeKTic [P10] | LiveCLKTBench [P13] | Cultural transfer [P15] | Domain adaptation [P16] | Bu tez |
|---|:---:|:---:|:---:|:---:|:---:|
| Source dilde knowledge origin kontrolü | Proxy | Güçlü, zaman-temelli | Güçlü, from-scratch corpus | Training corpus eşleşmesi | Güçlü, sentetik M1 manifesti |
| Source retrieval admission gate | Evet | Evet | Kısmi | Evet/metric dependent | Evet, robust M1 |
| Hedef dil adaptation müdahalesi | Hayır | Hayır | Evet | Evet | Evet |
| Hedef olgu adaptation'da yok kontrolü | Gözlemsel proxy | Post-training target dil yok | Olgular corpusta doğal | Hayır | Evet, M2-A |
| Hedef olgu re-exposure treatment'i | Hayır | Hayır | Hayır; bridge var | Corpus recipe'leri | Evet, M2-B |
| Eş toplam token/update bütçesi | Uygulanamaz | Model karşılaştırmasına bağlı | Yakın ama bridge müdahalesi | Recipe'e bağlı | Tasarım gereği |
| Aynı M1'den sibling arms | Hayır | Hayır | Karşılaştırmalı settings | Çeşitli recipes | Evet |
| Transfer ve relearning ayrı estimand | Hayır | Yalnız transfer | Bridge-induced transfer | Acquisition/transfer | Evet |
| English retention | Hayır | Source score içinde | Kısmi | State transitions | Zorunlu EN→EN |
| Türkçe capability manipulation check | Hayır | Türkçe yok | Türkçe yok | Japonca domain QA | BPB + TurBLiMP + broad capability |
| Synthetic contamination control | Hayır | Live real-world facts | Filtreli culture data | Domain corpus | Evet |

### 6.2 Savunulabilir novelty cümlesi

Türkçe tez metni için öneri:

> Sistematik taramamız, cross-lingual factual consistency, source-language knowledge injection,
> target-language continued pretraining ve multilingual knowledge editing üzerine yakın
> çalışmalar bulmuştur. Ancak taranan çalışmalar arasında, İngilizcede kontrollü olarak edinilmiş
> ve geri getirilebilirliği doğrulanmış sentetik olgular için aynı M1 checkpoint'inden başlayan,
> toplam Türkçe adaptation bütçesi eşlenmiş iki kardeş kolu karşılaştırarak genel Türkçe
> adaptation etkisini hedef-olgu Türkçe re-exposure etkisinden ayıran bir çalışma bulunmamıştır.
> Bu tez, transferi `TR→EN(M2-A)−TR→EN(M1)` ve yeniden öğrenmeyi
> `TR→EN(M2-B)−TR→EN(M2-A)` olarak ayrı, önceden tanımlı kestirimlerle ölçmeyi amaçlar.

İngilizce tez/paper cümlesi için öneri:

> Prior work has studied multilingual factual inconsistency, source-language knowledge injection,
> knowledge transfer during continued pretraining, and cross-lingual knowledge editing. In the
> literature reviewed here, however, we did not find a study that starts two target-language CPT
> arms from the same source-retrievable English factual state, matches their total adaptation
> budget, and changes only whether controlled target facts replace neutral target-language text.
> This design separately estimates adaptation-enabled transfer and the incremental effect of
> target-language factual re-exposure.

“İlk çalışma” veya “literatürde hiç yoktur” yerine “taranan literatürde bulunmadı” denmelidir.
Yeni yayınlar çıkabileceği için bu belge teslimden hemen önce yeniden taranmalıdır.

### 6.3 Tezin iddia etmemesi gerekenler

- Qwen pilotu cross-lingual transferi kanıtladı.
- Qwen pilotu iki seed'de relearning'i tekrarladı.
- Türkçe Wikipedia CPT genel Turkish capability'yi artırdı.
- Qwen Türkçe görmemiş bir modeldir.
- İki dilde aynı cevabı üretmek shared representation kanıtıdır.
- PPL iyileşmesi factual transfer kanıtıdır.
- M2-B'nin M2-A'dan fazla token/fact exposure alması hâlinde fark “relearning” olarak izole edilir.
- Açık uçlu exact match tek başına factual knowledge'i güvenilir ölçer.
- Editing sonuçları CPT ile aynıdır.

## 7. Literatürden doğrudan çıkan deney tasarım kuralları

### 7.1 Model seçimi

1. Source model için “English-dominant” etiketi yetmez; exact revision, training stage, corpus
   provenance ve Turkish baseline headroom kaydedilmelidir [P08, P10, P13, P69].
2. OLMo-2 provenance açısından primary candidate; Falcon-RW English-only signal açısından güçlü
   comparator; Qwen multilingual positive control'dür. Bunlar eş anlamlı model rolleri değildir.
3. Model, M1 factual learnability ve Turkish headroom'ı birlikte geçmelidir. Yalnız birinde iyi
   olması causal deney için yeterli değildir.

### 7.2 M1 factual acquisition

1. Sentetik fact inventory natural-world collision ve alias overlap açısından taranmalıdır [P26,
   P34].
2. Tek verbalization yerine dengeli canonical forms ve paraphrase families kullanılmalıdır
   [P24, P29–P33].
3. Olgu sıklığı, name family ve relation ayrı faktörler olarak dondurulmalıdır [P15, P69].
4. M1 admission gate en az exact storage, candidate ranking, relation binding, direct/QA ve
   unseen paraphrase robustness içermelidir.
5. Yalnız M1'de İngilizce olarak gerçekten geri getirilen facts transfer denominator'ına alınmalıdır
   [P10, P13].

### 7.3 M2-A / M2-B causal kardeş kollar

1. İki kol aynı exact M1 checkpoint'inden başlamalıdır.
2. Optimizer, LR schedule, sequence length, batch, update sayısı, toplam tokens, tokenizer ve
   checkpoint-selection rule aynı olmalıdır.
3. M2-B'de factual rows eklenmemeli; aynı sayıda neutral Turkish token/row ile değiştirilmelidir.
4. Target fact contamination M2-A corpus'unda exact ve semantic overlap düzeyinde audit edilmelidir.
5. English replay kullanılacaksa iki kolda aynı ve pre-frozen olmalıdır [P42, P45, P55, P56].
6. Tokenizer extension yapılacaksa ayrı tek-faktör ablation olmalı; M2-A ve M2-B arasında
   değişmemelidir [P36, P43, P44, P46].

### 7.4 Ölçüm paketi

Her `M0/M1/M2-A/M2-B` state için aynı paket:

| Boyut | Minimum çıktı | Literatür gerekçesi |
|---|---|---|
| Turkish language manipulation | Turkish BPB, within-model PPL, TurBLiMP/grammar | [P14, P20, P35, P47] |
| Tokenization | TR ve EN fertility, byte-normalized loss | [P05, P36, P43, P46] |
| Source retention | English BPB/PPL ve EN→EN | [P14, P35, P53–P58] |
| Transfer | TR→EN, M1 source-correct facts | [P09, P10, P13] |
| Target lexicalization | TR→TR secondary | [P09, P70] |
| Reverse direction | EN→TR exploratory | [P15, P69] |
| Prompt robustness | Forms × direct/QA; robust intersection | [P04, P24, P31–P33] |
| Binding | relation-confusion / joint-relation control | [P22, P25] |
| Uncertainty | paired bootstrap CI, seed-level replication | [P05, P13, proje pilotu] |
| State transitions | acquired/retained/forgotten/unacquired | [P16, P55] |

### 7.5 Analiz hiyerarşisi

1. **Primary:** `TR→EN(M2-A)−TR→EN(M1)` ve `TR→EN(M2-B)−TR→EN(M2-A)`.
2. **Guardrail:** EN→EN retention ve Turkish capability manipulation check.
3. **Secondary:** TR→TR, form-level robust accuracy, relation minima.
4. **Exploratory:** EN→TR, frequency/name moderators, layer/attention mechanisms.
5. Global average'ın yanında minimum relation/form cell ve robust intersection verilmelidir.
6. Seed'lerden biri pozitif, diğeri null ise tek pooled sonuçla “başarı” denmemelidir.

## 8. Tezde hangi paper nerede kullanılmalı?

| Tez bölümü | Ana kaynaklar | Kurulacak argüman |
|---|---|---|
| Introduction: problem | P05, P06, P09–P13, P17 | Factual access language-sensitive; multilingual ability cross-lingual knowledge access garantisi değil |
| Research gap | P10, P13–P18 | Gözlemsel transfer veya CPT gain'i relearning'i ayırmıyor; matched factual re-exposure contrast eksik |
| Synthetic design | P24–P34 | Contamination kontrolü; storage/extraction ayrımı; paraphrase ve relation binding |
| Target-language adaptation | P14–P20, P35–P46 | CPT hedef dili değiştirebilir ama forgetting/alignment/tokenizer/corpus confound'ları vardır |
| Turkish context | P35–P40, P47–P52 | Türkçe adaptation recipes, corpus gerçekliği ve measurement araçları |
| Model choice/provenance | P08, P10, P13, P69 + model papers/cards | “Unseen Turkish” yerine evidence-bounded provenance ve measured headroom |
| Methods: estimands | P09, P10, P13, P15, P16 | Source-correct conditioning, direction split, sibling comparison ve state transitions |
| Retention/forgetting | P14, P35, P53–P58 | Target gain ile source degradation birlikte raporlanmalı |
| Discussion: mechanisms | P09, P20, P63, P69–P71 | Semantic sharing, interface mapping ve frequency alternatif açıklamalar |
| Limitations | P10, P13, P16, P24, P34, P47 | Synthetic artificiality, coverage, translation, benchmark overlap, model/corpus generalizability |

## 9. Exposé bibliyografisi için düzeltmeler ve eklemeler

### 9.1 Düzeltilecek kayıtlar

1. **Qi et al.** Exposé'de 2025 olarak yazılmıştır. Peer-reviewed kayıt
   [EMNLP 2023, Anthology ID 2023.emnlp-main.658](https://aclanthology.org/2023.emnlp-main.658/)
   olmalıdır.
2. **Zhao et al. domain adaptation** Exposé'de 2025 arXiv olarak geçer. Çalışma artık
   [EACL 2026, Anthology ID 2026.eacl-long.269](https://aclanthology.org/2026.eacl-long.269/)
   olarak cite edilmelidir.
3. **Chua et al.** yalnız arXiv yerine mevcut venue kaydıyla
   [COLM 2025 OpenReview](https://openreview.net/forum?id=AwRFhS5grK) olarak güncellenebilir.
4. **Yamaguchi et al.** artık
   [ACL 2026, Anthology ID 2026.acl-long.865](https://aclanthology.org/2026.acl-long.865/)
   olarak cite edilebilir.
5. **Kang & Kim** için arXiv yanında CIKM 2025 proceedings metadata kullanılmalıdır; paper'ın
   inference-time L2T kapsamı açıkça belirtilmelidir.

### 9.2 Related Work'e mutlaka eklenecekler

- LiveCLKTBench [P13] — en yakın güncel knowledge-injection/transfer benchmark;
- ECLeKTic [P10] — source-known conditional transfer;
- Cross-Lingual Transfer of Cultural Knowledge [P15] — CPT altında kontrollü bridge farkı;
- CLiKA [P14] — performance/consistency/conductivity ayrımı;
- Physics of Language Models 3.1 [P24] — storage/extraction ve data diversity;
- ParaRel ve mParaRel [P31–P32] — robust prompt evaluation;
- TurBLiMP [P47] — Türkçe capability manipulation check;
- Tracing Multilingual Factual Knowledge Acquisition [P69] — frequency ve early transfer;
- How Do Multilingual LMs Remember Facts? [P70] — subject enrichment/object extraction ayrımı;
- Beneath the Surface of Consistency [P71] — consistency ≠ shared representation.

## 10. Öncelikli okuma sırası

### Seviye 1 — Tezin omurgası, ilk 12

1. P13 — LiveCLKTBench.
2. P15 — Cross-Lingual Transfer of Cultural Knowledge.
3. P16 — Tracing Knowledge Acquisition in Domain Adaptation.
4. P69 — Tracing Multilingual Factual Knowledge Acquisition in Pretraining.
5. P09 — Lost in Multilinguality.
6. P14 — CLiKA.
7. P05 — Cross-Lingual Consistency / RankC.
8. P24 — Physics 3.1.
9. P31/P32 — ParaRel ve mParaRel.
10. P35 — Bridging the Bosphorus.
11. P47 — TurBLiMP.
12. P56 — Source-Shielded Updates.

### Seviye 2 — Tasarım ve yorum için

P08, P10, P11, P17, P20, P25, P26, P29, P34, P36, P42, P46, P70 ve P71.

### Seviye 3 — Kapsam sınırı ve geniş related work

P01–P04, P06–P07, P18–P19, P21–P23, P27–P28, P30, P33, P37–P46, P48–P55 ve P59–P68.

## 11. Workspace içindeki paper PDF'leri

Bu envanter, hangi yerel dosyanın tezde hangi rolde olduğunu gösterir. Aynı paper'ın iki kopyası
varsa bu açıkça belirtilmiştir.

| Yerel PDF | İçerik | Öncelik | Kullanım kararı |
|---|---|---:|---|
| [2023.findings-acl.48.pdf](../papers/2023.findings-acl.48.pdf) | Overcoming Catastrophic Forgetting in Massively Multilingual Continual Learning | B | Forgetting/CFT/CBT yöntemsel kaynağı [P55] |
| [2023.ldk-1.59.pdf](../papers/2023.ldk-1.59.pdf) | Cross-Lingual Transfer Learning for Misinformation Detection | C | Task transfer örneği; factual parametric transferle karıştırılmamalı |
| [2025.xllm-1.7.pdf](../papers/2025.xllm-1.7.pdf) | Exploring Multilingual Probing in LLMs | C | Genel probing context'i; ana causal soruya doğrudan kanıt değil |
| [2026.eacl-long.46.pdf](../papers/2026.eacl-long.46.pdf) | CETVEL | B | Turkish capability benchmark [P50] |
| [2026.sigturk-1.12.pdf](../papers/2026.sigturk-1.12.pdf) | TurkBench | B | Turkish benchmark taxonomy [P51] |
| [2309.14316v3.pdf](../papers/2309.14316v3.pdf) | Physics of Language Models 3.1 | A | Storage/extraction ve data diversity [P24] |
| [2309.14402v2.pdf](../papers/2309.14402v2.pdf) | Physics of Language Models 3.2 | A/B | Retrieval/manipulation ayrımı [P25] |
| [2310.10378v5.pdf](../papers/2310.10378v5.pdf) | Cross-Lingual Consistency | A | RankC ve editing case [P05] |
| [2405.04685v1.pdf](../papers/2405.04685v1.pdf) | Bridging the Bosphorus | A/B | Turkish CPT dose/forgetting [P35] |
| [2512.04844v1.pdf](../papers/2512.04844v1.pdf) | Source-Shielded Updates preprint | B | Güncel peer-reviewed ACL 2026 sürümü cite edilmeli [P56] |
| [2601.06675v1.pdf](../papers/2601.06675v1.pdf) | Evaluating Cross-Lingual Unlearning | C | Ters yönlü komşu problem [P68] |
| [Important/Cross-Lingual Consistency…pdf](<../papers/Important/Cross-Lingual Consistency of Factual Knowledge in Multilingual Language Models .pdf>) | Qi et al. 2023 | A | `2310.10378v5.pdf` ile aynı paper'ın proceedings kopyası |
| [Important/Crosslingual Capabilities…pdf](<../papers/Important/Crosslingual Capabilities and Knowledge Barriers in Multilingual Large Language Models.pdf>) | Chua et al. | A | Knowledge barrier ve mixed-language FT [P17] |
| [Important/Language Models' Factuality…pdf](<../papers/Important/Language Models’ Factuality Depends on the Language of Inquiry.pdf>) | Aggarwal et al. | A | Language-of-inquiry metrics [P11] |
| [Important/Lost in Multilinguality…pdf](<../papers/Important/Lost in Multilinguality Dissecting Crosslingual Factual Inconsistencyin Transformer Language Models.pdf>) | Wang et al. 2025 | A | Concept space → output-language bariyeri [P09] |
| [Important/Polyglot or Not…pdf](<../papers/Important/Polyglot or Not%3F Measuring Multilingual Encyclopedic Knowledge in Foundation Models.pdf>) | Schott et al. 2023 | A | Multilingual encyclopedic probing [P06] |
| [Important/TOFU…pdf](<../papers/Important/TOFU A Task of Fictitious Unlearning for LLMs.pdf>) | Maini et al. | A/B | Fictitious knowledge control [P26] |
| [Important/Tracing Multilingual Factual…pdf](<../papers/Important/Tracing Multilingual Factual Knowledge Acquisition in Pretraining.pdf>) | Liu et al. 2025 | A | Frequency ve early transfer dynamics [P69] |
| [Important/Tracing … Domain Adaptation…pdf](<../papers/Important/Tracing Multilingual Knowledge Acquisition Dynamicsin Domain Adaptation A CaseStudy of Biomedical Adaptation.pdf>) | Zhao et al. 2026 | A | AdaXEval, loss shielding ve transfer/forgetting [P16] |
| [Important/Tracing the Roots…pdf](<../papers/Important/Tracing the Roots of Facts in Multilingual Language Models Independent, Shared, and Transferred Knowledge.pdf>) | Zhao et al. 2024 | A | Fact provenance/representation [P08] |
| [Important/When Language Shapes Thought…pdf](<../papers/Important/When Language Shapes Thought Cross-Lingual Transfer of Factual Knowledge in Question Answering.pdf>) | Kang & Kim 2025 | B/C | Inference-time thought-language alignment [P72] |

### Yerel koleksiyondaki kritik eksikler

Tez yazımı için aşağıdaki çekirdek paper'ların yerel PDF'i görünmüyor; bağlantıları bu belgede var:

- LiveCLKTBench [P13];
- ECLeKTic [P10];
- Cross-Lingual Transfer of Cultural Knowledge [P15];
- CLiKA [P14];
- ParaRel ve mParaRel [P31–P32];
- TurBLiMP [P47];
- How Do Multilingual LMs Remember Facts? [P70];
- Beneath the Surface of Consistency [P71].

Bu liste indirme talimatı değildir; yalnız yerel arşiv kapsamını gösterir.

## 12. Project-specific sentez: literatür bugünkü kararları nasıl değiştiriyor?

### 12.1 Tamamlanan pilotun bilimsel değeri

Qwen pilotu “başarısız olduğu için çöpe atılacak” bir deney değildir. [P14–P17, P35, P55–P58]
gösteriyor ki hedef dil adaptation'ı sıklıkla source knowledge erişimini bozabilir ve target gain
deep transfer anlamına gelmeyebilir. Pilotun iki seed'de broad TR-involving decline ve yalnız mütevazı
factual-arm recovery göstermesi literatürle uyumludur. Bilimsel katkısı:

- pipeline ve sibling-arm execution'ın çalışabildiğini göstermesi;
- scale-up öncesi form/generalization/relation-binding sorunlarını ortaya çıkarması;
- Wikipedia-only yaklaşık 1M-token adaptation'ın yeterli Turkish manipulation sağlamadığını
  düşündürmesi;
- seed heterogeneity nedeniyle güçlü gate ve uncertainty ihtiyacını doğrulaması.

### 12.2 Yeni ana deney neden Qwen pilotunun tekrarı değildir?

Yeni tasarım:

- provenance'i daha açık ve Turkish headroom'ı ölçülmüş English-dominant model arar;
- Qwen'i positive control olarak tutar;
- geniş ve denetlenmiş Turkish corpus ister;
- capability manipulation check'i factual outcome'dan önce zorunlu kılar;
- M2-B factual treatment'ı ek bütçe değil matched replacement olarak kurar;
- transfer ve relearning'i iki ayrı paired contrast olarak tanımlar.

Bu farklar [P10, P13–P17, P24, P35, P47, P56, P69–P71] tarafından birlikte
gerekçelendirilir.

### 12.3 Hâlen çözülmemiş bilimsel/operasyonel girdiler

- `trwiki-20260601` yalnız cross-domain control;
- CulturaX `excluded_access_blocked`;
- exact primary in-domain split henüz seçilmiş/materialize edilmiş değil;
- benchmark exact revisions, item hashes, licenses, overlap ve floor/ceiling kuralları tam
  dondurulmuş değil;
- 151at yalnız local Hugging Face redirect protokolünü düzeltir; source access yürütülmemiştir;
- dolayısıyla literatür tasarımı güçlendirir ama execution readiness üretmez.

## 13. Hızlı tez-yazım iskeleti

### 13.1 Related Work paragraf akışı

1. **Multilingual factual access is inconsistent.** P01–P06, P11, P12.
2. **Consistency does not imply shared or transferable knowledge.** P05, P08, P14, P71.
3. **Retrieval failures can occur at language-dependent output stages.** P09, P20, P70.
4. **Cleaner transfer benchmarks condition on source acquisition or inject new knowledge.** P10,
   P13, P15, P16.
5. **Target-language CPT changes capability but introduces forgetting/confounds.** P14, P17,
   P35–P46, P53–P58.
6. **Synthetic controlled facts trade ecological realism for provenance control.** P24–P34.
7. **Gap:** no matched Turkish no-reexposure/reexposure sibling comparison found.

### 13.2 Discussion paragraf akışı

1. Önce Turkish manipulation'ın gerçekten gerçekleşip gerçekleşmediğini söyle.
2. Sonra M2-A−M1 transfer contrast'ını ver.
3. Ardından M2-B−M2-A relearning contrast'ını ver.
4. EN→EN retention ve state transitions ile alternative explanations'ı sınırla.
5. TR→TR ile object lexicalization farkını tartış.
6. Frequency/name/relation ve form heterogeneity'yi exploratory olarak sun.
7. Qwen positive control ile English-dominant model arasındaki farkı provenance üzerinden yorumla.
8. Synthetic fact artificiality ve corpus/benchmark kapsamını açık limitation yap.

## 14. Terim sözlüğü

| Terim | Bu projedeki kesin anlam |
|---|---|
| **Multilingual ability** | Modelin birden fazla dilde görev yapabilmesi; cross-lingual factual transfer garantisi değil |
| **Factual retrieval** | Bir subject/relation sorgusunda doğru object'i seçme/üretme |
| **Source acquisition** | Fact'in M1'de İngilizce eğitim sonrası pre-frozen robust gate'i geçmesi |
| **Transfer** | Target fact Türkçe adaptation verisinde yokken M2-A'nın M1'e göre TR→EN değişimi |
| **Reaffirmation/relearning** | Aynı bütçede target fact Türkçe re-exposure'ının M2-B−M2-A ek etkisi |
| **Consistency** | Eş anlamlı/diller arası promptlarda aynı sonucu verme; shared representation veya transferle eş anlamlı değil |
| **Conductivity** | Bir dilde edinilen bilginin diğer dil sorgusunda erişilebilirliği [P14] |
| **Retention** | M1 English factual retrieval'ın adaptation sonrasında korunması |
| **Storage** | Fact sinyalinin parametrelerde bulunması; natural QA extraction ile aynı değil |
| **Lexicalization** | Seçilen factual concept'in istenen answer dilinde yüzeye çıkarılması |
| **Fertility** | Bir metnin tokenizer altında kaç token'a parçalandığı; language capability metriği değil |
| **BPB** | Bits per UTF-8 byte; tokenizerlar arası loss karşılaştırması için PPL'den daha uygun normalizasyon |

## 15. Tarama kayıt özeti ve güncelleme protokolü

| Alan | Kayıt |
|---|---|
| Son tarama | 2026-08-09, Europe/Berlin |
| Birincil dizinler | ACL Anthology, OpenReview, arXiv, resmî model/dataset cards |
| Yerel kaynak | 21 paper PDF + Expose.pdf + kronolojik proje belgeleri |
| Çekirdek/yöntemsel kaynak sayısı | Bu belgede P01–P73 arası 73 kimlik; bazı kimlikler aynı paper'ın farklı rolünü veya survey/model kaynağını tekrar bağlar |
| Ana yeni 2026 kaynakları | LiveCLKTBench; Zhao et al. EACL; Disentangling CPT; Source-Shielded Updates; CETVEL; TurkBench |
| Novelty riski | 2025–2026 yakın komşular nedeniyle geniş “first” claim'i savunulamaz; matched Turkish fact-reexposure estimand'i düzeyinde daraltılmalı |
| Yürütme etkisi | Yok; bu dosya execution contract değildir |

Literatür haritası tez tesliminden önce şu sorgularla bir kez daha güncellenmelidir:

- `"cross-lingual factual knowledge" continued pretraining 2026 2027`;
- `"knowledge transfer" "language adaptation" synthetic facts`;
- `Turkish factual knowledge transfer LLM adaptation`;
- LiveCLKTBench/ECLeKTic citing papers;
- ACL/EMNLP/NAACL/EACL 2027 accepted-paper araması.

Yeni paper eklenirken dört soru cevaplanmalıdır:

1. Source fact'in nerede edinildiği gerçekten biliniyor mu?
2. Target-language capability ile factual transfer ayrılmış mı?
3. Target fact target-language training verisinde bulunuyor mu?
4. Müdahale CPT mi, SFT mi, editing mi, prompting mi, retrieval mı?

Bu dört alan yoksa çalışma related work'e girebilir, fakat ana transfer/relearning kanıtı olarak
kullanılmamalıdır.

## 16. Son hüküm

Literatür, tezin temel sezgisini güçlü biçimde destekliyor: hedef dilde doğru factual cevap görmek,
o bilginin kaynak dilden transfer edildiğini kanıtlamaz. Önceden exposure, target-side relearning,
prompt surface, tokenizer, dil yeterliği, output lexicalization ve forgetting aynı gözlemi
üretebilir. Projenin bilimsel değeri bu alternatifleri tek tek adlandırmasında değil, onları
**aynı M1'den başlayan, bütçesi eşlenmiş M2-A/M2-B kardeş kollar ve yön-ayrılmış ölçümlerle**
deneysel olarak ayırmaya çalışmasındadır.

Tamamlanan Qwen pilotu bu iddiayı doğrulamadı; fakat neden daha güçlü bir Turkish manipulation
check, daha açık model/corpus provenance, matched replacement ve daha sıkı robust retrieval gate
gerektiğini gösterdi. Bir sonraki bilimsel adım, literatürdeki en iyi dersleri bir araya getiren bu
tasarımı dondurmak olabilir; mevcut proje kayıtlarına göre bu adım henüz eğitim için yetkili veya
hazır değildir.
