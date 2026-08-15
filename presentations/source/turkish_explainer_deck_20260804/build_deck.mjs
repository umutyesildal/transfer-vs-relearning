import { FileBlob, PresentationFile } from "@oai/artifact-tool";
import fs from "node:fs/promises";

const STARTER = "/Users/umutyesildal/Desktop/UniDE/Semester6/Thesis/implementation/tmp/turkish_explainer_deck_20260804/template-starter.pptx";
const OUTPUT = "/Users/umutyesildal/Desktop/UniDE/Semester6/Thesis/implementation/outputs/qwen_m2_m3_arastirma_guncellemesi_tr_agustos_2026.pptx";

const presentation = await PresentationFile.importPptx(await FileBlob.load(STARTER));

function shapeByName(slide, name) {
  const shape = slide.shapes.items.find((item) => item.name === name);
  if (!shape) throw new Error(`Missing inherited shape '${name}'`);
  return shape;
}

function setText(slide, name, value) {
  shapeByName(slide, name).text = value;
}

function setNotes(slide, sources, extra = []) {
  const lines = ["[Sources]", ...sources.map((s) => `- ${s}`), ...extra.map((s) => `- ${s}`)];
  slide.speakerNotes.textFrame.setText(lines.join("\n"));
  slide.speakerNotes.setVisible(true);
}

function setPage(slide, page) {
  const pageShape = slide.shapes.items.find((item) => item.name === "page");
  if (pageShape) pageShape.text = String(page);
}

function setFourStage(slide, stages) {
  stages.forEach((stage, index) => {
    setText(slide, `stage-id-${index}`, stage.id);
    setText(slide, `stage-title-${index}`, stage.title);
    setText(slide, `stage-body-${index}`, stage.body);
  });
}

// 1 — Açılış
{
  const s = presentation.slides.items[0];
  setText(s, "eyebrow", "TEZ ARAŞTIRMA GÜNCELLEMESİ");
  setText(s, "title", "Sağlam İngilizce edinimden\nTürkçe factual adaptasyona");
  setText(s, "subtitle", "Yöntemler, kronoloji, örnekler, Qwen M1 ve M2/M3 sonuçları");
  setText(s, "meta", "Umut Yeşildal  ·  Tez ilerleme görüşmesi  ·  Ağustos 2026");
  setText(s, "scope", "500 ve 2.500 fact · iki seed · 240.000 endpoint probe");
  setNotes(s, [
    "documentation/138_QWEN_M2_M3_COMPLETED_MILESTONE_AND_SCIENTIFIC_INTERPRETATION_EN.md",
    "documentation/143_QWEN_M2_M3_ARTIFACT_RETENTION_FREEZE_AND_STORAGE_AUDIT_EN.md",
  ]);
}

// 2 — Ana hikâye
{
  const s = presentation.slides.items[1];
  setText(s, "kicker", "ANA HİKÂYE");
  setText(s, "headline", "Bir M1 adayından kontrollü M2/M3 sonucuna geldik");
  setText(s, "close-label-0", "Ölçüm sertleşti");
  setText(s, "close-body-0", "Exact ezber yerine unseen Forms A–D, direct/QA, binding, PPL ve robust intersection ölçüldü.");
  setText(s, "close-label-1", "Model seçildi");
  setText(s, "close-body-1", "SmolLM robust gate’i geçemedi; Qwen 2.500 fact’te iki seed ile replicate edildi.");
  setText(s, "close-label-2", "Causal family bitti");
  setText(s, "close-body-2", "M2-clean ve M3-fact dört sibling run, sabit endpoint ve 240.000 probe ile tamamlandı.");
  setText(s, "discussion-text", "M3 küçük bir recovery sağladı; primary interaction yalnız bir seed’de geçti. Bu deney tamamlandı, tez değil.");
  setPage(s, 2);
  setNotes(s, [
    "documentation/106_M1_CROSS_FAMILY_MODEL_SCREENING_RESULT.md",
    "documentation/127_QWEN_SCALE_REPLICATION_RESULT_AND_SMOLLM_LAMBDA025_STATUS.md",
    "documentation/136_QWEN_M2_M3_ENDPOINT_EVALUATION_GPU_ALLOCATION_STATUS.md",
    "documentation/138_QWEN_M2_M3_COMPLETED_MILESTONE_AND_SCIENTIFIC_INTERPRETATION_EN.md",
  ]);
}

// 3 — M0-M3
{
  const s = presentation.slides.items[2];
  setText(s, "kicker", "ARAŞTIRMA SORUSU");
  setText(s, "slide-title", "Asıl soru transfer mi, yeniden öğrenme mi?");
  setText(s, "question", "Türkçe adaptation, İngilizcede öğrenilmiş bir fact’i tekrar görmeden erişilebilir yapabilir mi; fact tekrar edilirse ne değişir?");
  setFourStage(s, [
    { id: "M0", title: "Bilgi yok", body: "Synthetic binding başlangıçta erişilebilir değildir." },
    { id: "M1", title: "İngilizce edinim", body: "Target fact’ler İngilizcede robust biçimde öğrenilir." },
    { id: "M2", title: "Temiz Türkçe", body: "Target fact tekrarı olmadan Türkçe adaptation yapılır." },
    { id: "M3", title: "Türkçe fact", body: "Yalnız Branch B fact’leri matched bütçede tekrar edilir." },
  ]);
  setText(s, "takeaway", "Matched M2/M3 siblings, generic adaptation etkisini factual re-exposure etkisinden ayırır.");
  setText(s, "source", "Expose tasarımı ve frozen causal contract; raporlar 133–136");
  setPage(s, 3);
  setNotes(s, [
    "documentation/100_MASTER_PROJECT_STATUS_AND_EXECUTION_PLAN.md",
    "documentation/133_QWEN_2500_FACT_M2_M3_EXECUTION_HANDOFF_PLAN.md",
    "documentation/135_QWEN_M2_M3_CONTRACT_AND_MATERIALIZATION_STATUS.md",
  ]);
}

// 4 — Kronoloji I
{
  const s = presentation.slides.items[3];
  setText(s, "kicker", "KRONOLOJİ I");
  setText(s, "slide-title", "17–19 Temmuz: ölçüm sertleşti, model farkları açıldı");
  setText(s, "question", "M1’in yalnız canonical string’i değil, unseen promptlarda aynı binding’i koruması gerektiği netleşti.");
  setFourStage(s, [
    { id: "17", title: "Hard evaluation", body: "17 Temmuz: Forms A–C ve direct/QA; exact başarının yeterli olmadığı görüldü." },
    { id: "18", title: "Kontroller", body: "18 Temmuz: A/B counterbalance, joint relation ve PPL/drift ablation tamamlandı." },
    { id: "19", title: "A–D remediation", body: "19 Temmuz: A/B training’e girdi; C/D held-out kaldı; robust gate sertleşti." },
    { id: "19", title: "Model screen", body: "19 Temmuz: Qwen, Gemma, StableLM ve Llama aynı frozen contract ile test edildi." },
  ]);
  setText(s, "takeaway", "Qwen factual olarak öne çıktı; ilk PPL hatası retention-preserving replay ihtiyacını açtı.");
  setText(s, "source", "Raporlar 94–106; tarih ve kararlar chronological record’dan alınmıştır");
  setPage(s, 4);
  setNotes(s, [
    "documentation/94_PRE_M2_FROZEN_HARD_EVALUATION_REPORT.md",
    "documentation/95_PRE_M2_PARAPHRASE_COUNTERBALANCE_REPORT.md",
    "documentation/96_PRE_M2_JOINT_RELATION_CONTROL_REPORT.md",
    "documentation/97_PRE_M2_DRIFT_ABLATION_REPORT.md",
    "documentation/102_M1_FORM_GENERALIZATION_REMEDIATION_RESULT.md",
    "documentation/106_M1_CROSS_FAMILY_MODEL_SCREENING_RESULT.md",
  ]);
}

// 5 — Kronoloji II
{
  const s = presentation.slides.items[4];
  setText(s, "kicker", "KRONOLOJİ II");
  setText(s, "slide-title", "23–30 Temmuz: Qwen ölçeklendi, SmolLM dalı kapandı");
  setText(s, "question", "Amaç: Qwen factual strength’ini düşük PPL drift ile korumak ve SmolLM binding müdahalelerini adil karşılaştırmaktı.");
  setFourStage(s, [
    { id: "23", title: "Retention replay", body: "23–24 Temmuz: seed 42 adjudication, seed 43 replication; 2.500-fact scale gate zorunlu oldu." },
    { id: "25", title: "Scale probe", body: "25–26 Temmuz: Qwen seed 42, 2.500 fact ve 11 checkpoint ile güçlü Pareto noktaları verdi." },
    { id: "28", title: "Yeni wave", body: "28 Temmuz: Qwen seed 43 ile SmolLM control/contrastive training’leri tamamlandı." },
    { id: "29", title: "Karar", body: "29–30 Temmuz: Qwen iki seed’de geçti; SmolLM %55,8’de kaldı ve ana dal kapandı." },
  ]);
  setText(s, "takeaway", "29 Temmuz’da seed 42 step 75 ve seed 43 step 50 seçildi; iki Qwen M1 artifact’i freeze edildi.");
  setText(s, "source", "Raporlar 117–128; 2.500-fact replication ve SmolLM kapanış zinciri");
  setPage(s, 5);
  setNotes(s, [
    "documentation/117_M1_RETENTION_REMEDIATION_AND_500_SUBJECT_SCALE_GATE.md",
    "documentation/118_M1_RETENTION_EVALUATION_RESULT_AND_INTEGRITY_ADJUDICATION.md",
    "documentation/120_M1_QWEN_RETENTION_SEED43_REPLICATION_RESULT.md",
    "documentation/123_QWEN_SCALE_PROBE_RESULT_AND_SMOLLM_PILOT_STATUS.md",
    "documentation/126_QWEN_SEED43_AND_SMOLLM_TRAINING_COMPLETION_REPORT.md",
    "documentation/127_QWEN_SCALE_REPLICATION_RESULT_AND_SMOLLM_LAMBDA025_STATUS.md",
    "documentation/128_SMOLLM_500_FACT_PROMPT_CONSISTENCY_REMEDIATION_PLAN.md",
  ]);
}

// 6 — Kronoloji III
{
  const s = presentation.slides.items[5];
  setText(s, "kicker", "KRONOLOJİ III");
  setText(s, "slide-title", "31 Temmuz–3 Ağustos: M2/M3 tamamlandı ve donduruldu");
  setText(s, "question", "Outcome görülmeden önce yönler, aliases, bütçe, checkpoint, estimand ve gate donduruldu.");
  setFourStage(s, [
    { id: "31", title: "Pre-M2 freeze", body: "31 Temmuz: bilingual baseline, PPL, contamination, registries ve evaluation contract hazırlandı." },
    { id: "1", title: "Dört training", body: "1 Ağustos: M2-42, M3-42, M2-43 ve M3-43 checkpoint-128’e ulaştı." },
    { id: "2", title: "96/96 evaluation", body: "2 Ağustos: 240.000 probe tamamlandı; frozen gate 23:25Z’de uygulandı." },
    { id: "3", title: "Review + freeze", body: "3 Ağustos: exploratory analysis, independent review ve dört model-only artifact donduruldu." },
  ]);
  setText(s, "takeaway", "Current causal family operational olarak kapandı; primary criterion geçmedi ve yeni training otomatik açılmadı.");
  setText(s, "source", "Raporlar 132–143; M2/M3 execution, evaluation, review ve retention closure");
  setPage(s, 6);
  setNotes(s, [
    "documentation/132_PRE_M2_QWEN_READINESS_AND_BASELINE_PLAN.md",
    "documentation/134_QWEN_PRE_M2_GPU_BLOCKER_AND_OFFLINE_PREPARATION_STATUS.md",
    "documentation/135_QWEN_M2_M3_CONTRACT_AND_MATERIALIZATION_STATUS.md",
    "documentation/136_QWEN_M2_M3_ENDPOINT_EVALUATION_GPU_ALLOCATION_STATUS.md",
    "documentation/140a_QWEN_M2_M3_INDEPENDENT_REVIEW_RESULT_EN.md",
    "documentation/142_QWEN_M2_M3_EXPLORATORY_MECHANISM_ANALYSIS_RESULT_EN.md",
    "documentation/143_QWEN_M2_M3_ARTIFACT_RETENTION_FREEZE_AND_STORAGE_AUDIT_EN.md",
  ]);
}

// 7 — Temsili fact
{
  const s = presentation.slides.items[6];
  setText(s, "kicker", "TEK BİR TEMSİLİ FACT");
  setText(s, "slide-title", "Aynı binding farklı dil yüzeylerinde test edilir");
  setText(s, "direct-fact", "Temsili bağ: subject → relation → object");
  setText(s, "train-label", "İngilizce kayıt — M1");
  setText(s, "train-examples", "Kişi-017 works as Profession 17.\nSubject: Kişi-017 · relation: profession\nObject: Profession 17");
  setText(s, "heldout-label", "Türkçe fact — M3 örneği");
  setText(s, "heldout-example", "Kişi-017 → Meslek 17 · Türkçe object alias");
  setText(s, "ladder-title", "Sabit bağ");
  setText(s, "ladder-1", "S");
  setText(s, "ladder-1r", "Kişi-017");
  setText(s, "ladder-2", "R");
  setText(s, "ladder-2r", "profession / meslek");
  setText(s, "ladder-3", "O");
  setText(s, "ladder-3r", "Profession 17 ↔ Meslek 17");
  setText(s, "recipe-title", "Neden temsili?");
  setText(s, "recipe-body", "Bu örnek bir sonuç satırı değildir; direction, form, scaffold ve ranking mantığını açıklar.");
  setText(s, "source", "Prompt ve Turkish fact template mantığı; qwen_pre_m2.py");
  setPage(s, 7);
  setNotes(s, [
    "transfer-vs-relearning/src/transfer_vs_relearning/data/qwen_pre_m2.py",
    "transfer-vs-relearning/tests/test_qwen_pre_m2.py",
  ], ["Illustrative example only; not an empirical dataset row."]);
}

// 8 — Dil yönleri
{
  const s = presentation.slides.items[7];
  setText(s, "kicker", "DİL YÖNLERİ");
  setText(s, "slide-title", "Okun yönü prompt ve beklenen cevabın dilidir");
  setText(s, "question", "Aynı temsili fact: Kişi-017 → profession → Profession 17 / Meslek 17");
  setFourStage(s, [
    { id: "1", title: "EN→EN · Koruma", body: "Q: What occupation does Kişi-017 have?\nA: Profession 17" },
    { id: "2", title: "TR→EN · Erişim", body: "S: Kişi-017 ne iş yapıyor?\nC: Profession 17" },
    { id: "3", title: "TR→TR · Uçtan uca", body: "S: Kişi-017 ne iş yapıyor?\nC: Meslek 17" },
    { id: "4", title: "EN→TR · Kavramsal", body: "Q: What occupation...?\nA: Meslek 17\nBu kontratta ölçülmedi." },
  ]);
  setText(s, "takeaway", "Primary TR→EN, Turkish prompt access’i ölçerken Turkish answer lexicalization etkisini dışarıda tutar.");
  setText(s, "source", "Frozen directions: EN→EN, TR→EN, TR→TR; EN→TR yalnız açıklayıcı örnek");
  setPage(s, 8);
  setNotes(s, [
    "transfer-vs-relearning/src/transfer_vs_relearning/data/qwen_pre_m2.py",
    "documentation/135_QWEN_M2_M3_CONTRACT_AND_MATERIALIZATION_STATUS.md",
  ], ["EN→TR was not part of the frozen evaluated direction set."]);
}

// 9 — Scaffold
{
  const s = presentation.slides.items[8];
  setText(s, "kicker", "PROMPT SCAFFOLD");
  setText(s, "slide-title", "Direct ve QA aynı soruyu farklı çerçevede sunar");
  setText(s, "v1-title", "Direct");
  setText(s, "v1-result", "Prompt etiketsiz verilir");
  setText(s, "v1-weak", "Örnek");
  setText(s, "v1-lines", "Kişi-017 ne iş yapıyor?\n→ model cevabı doğrudan üretir");
  setText(s, "v1-diagnosis", "Question surface’e duyarlılığı ölçen en sade çerçeve.");
  setText(s, "v2-title", "QA scaffold");
  setText(s, "v2-replace", "Soru: Kişi-017 ne iş yapıyor?\nCevap:");
  setText(s, "v2-result", "Beklenen: Meslek 17");
  setText(s, "v2-change", "Aynı fact · aynı candidates");
  setText(s, "v2-limit", "Yalnız scaffold değişir; direction ve form aynı tutulur.");
  setText(s, "relations", "Her Form A–D hem direct hem QA ile test edilir: 4 × 2 = 8 hücre.");
  setText(s, "source", "English/Turkish scaffold templates; pre_m2_followup.py ve qwen_pre_m2.py");
  setPage(s, 9);
  setNotes(s, [
    "transfer-vs-relearning/src/transfer_vs_relearning/data/pre_m2_followup.py",
    "transfer-vs-relearning/src/transfer_vs_relearning/data/qwen_pre_m2.py",
  ]);
}

// 10 — Forms A-D
{
  const s = presentation.slides.items[9];
  setText(s, "kicker", "FORMS A–D");
  setText(s, "slide-title", "Anlam sabit kalır, soru sözdizimi değişir");
  setText(s, "question", "Relation = profession, subject = Kişi-017; dört Türkçe prompt aynı object’i istemektedir.");
  setFourStage(s, [
    { id: "A", title: "Form A · Temel", body: "Kişi-017 hangi mesleği yapıyor?" },
    { id: "B", title: "Form B · Profesyonel", body: "Kişi-017 profesyonel olarak hangi işte çalışıyor?" },
    { id: "C", title: "Form C · Kayıt", body: "Kişi-017 için belirtilen meslek nedir?" },
    { id: "D", title: "Form D · Gündelik", body: "Kişi-017 ne iş yapıyor?" },
  ]);
  setText(s, "takeaway", "M1 recipe A/B yüzeylerini görür; C/D held-out kalır. Robust access bütün formlarda korunmalıdır.");
  setText(s, "source", "Exact Turkish templates; qwen_pre_m2.py");
  setPage(s, 10);
  setNotes(s, [
    "transfer-vs-relearning/src/transfer_vs_relearning/data/qwen_pre_m2.py",
    "transfer-vs-relearning/src/transfer_vs_relearning/data/m1_form_generalization.py",
  ]);
}

// 11 — Measurement evolution
{
  const s = presentation.slides.items[10];
  setText(s, "kicker", "ÖLÇÜMÜN EVRİMİ");
  setText(s, "slide-title", "Exact completion’dan robust binding’e geçtik");
  setText(s, "fact", "Tek fact  →  farklı promptlar, scaffoldlar ve kontroller");
  setText(s, "train-form", "Evaluator, M2/M3 başlamadan önce adım adım daha zor hale getirildi.");
  setText(s, "initial-probe-title-0", "Exact-prefix");
  setText(s, "initial-probe-example-0", "Kişi-017 works as Profession ...");
  setText(s, "initial-probe-result-0", "Storage ölçer");
  setText(s, "initial-probe-title-1", "Held-out forms");
  setText(s, "initial-probe-example-1", "Forms A–D × direct/QA; unseen C/D dahil");
  setText(s, "initial-probe-result-1", "Prompt transfer ölçer");
  setText(s, "initial-probe-title-2", "Binding + retention");
  setText(s, "initial-probe-example-2", "Ranking, forced choice, PPL, generic output, intrusion");
  setText(s, "initial-probe-result-2", "Yorumu korur");
  setText(s, "initial-result-text", "Bir familiar promptun başarısı yetmez; aynı binding gerekli bütün unseen koşullarda korunmalıdır.");
  setText(s, "source", "Frozen hard evaluation ve controls; raporlar 94–98");
  setPage(s, 11);
  setNotes(s, [
    "documentation/94_PRE_M2_FROZEN_HARD_EVALUATION_REPORT.md",
    "documentation/95_PRE_M2_PARAPHRASE_COUNTERBALANCE_REPORT.md",
    "documentation/96_PRE_M2_JOINT_RELATION_CONTROL_REPORT.md",
    "documentation/97_PRE_M2_DRIFT_ABLATION_REPORT.md",
  ]);
}

// 12 — Robust intersection
{
  const s = presentation.slides.items[11];
  setText(s, "kicker", "ROBUST INTERSECTION");
  setText(s, "slide-title", "Bir fact robust sayılmak için 8/8 hücreyi geçmelidir");
  setText(s, "capacity-control", "4 form × 2 scaffold = 8 hücre. Tek bir hücre başarısızsa fact-level robust değeri 0 olur.");
  setText(s, "m360-title", "7 / 8 başarılı");
  setText(s, "m360-overlap", "0");
  setText(s, "m360-label", "fact-level robust");
  setText(s, "arrow", "≠");
  setText(s, "m17-title", "8 / 8 başarılı");
  setText(s, "m17-overlap", "1");
  setText(s, "m17-label", "fact-level robust");
  setText(s, "setup-text", "A-dir ✓  A-QA ✓  B-dir ✓  B-QA ✓  C-dir ✓  C-QA ✓  D-dir ✓  D-QA ✗");
  setText(s, "capacity-meaning", "Population robust accuracy = 8/8 geçen fact sayısı ÷ toplam fact sayısı.");
  setText(s, "source", "Eight-cell robust definition; qwen_m2_m3.py ve rapor 136");
  setPage(s, 12);
  setNotes(s, [
    "transfer-vs-relearning/src/transfer_vs_relearning/metrics/qwen_m2_m3.py",
    "documentation/136_QWEN_M2_M3_ENDPOINT_EVALUATION_GPU_ALLOCATION_STATUS.md",
  ]);
}

// 13 — Candidate ranking
{
  const s = presentation.slides.items[12];
  setText(s, "kicker", "SCORING YÖNTEMİ");
  setText(s, "slide-title", "Candidate ranking factual binding’i daha temiz ölçer");
  setText(s, "v1-title", "Free generation");
  setText(s, "v1-result", "Kişi-017 ne iş yapıyor?");
  setText(s, "v1-weak", "Model çıktısı");
  setText(s, "v1-lines", "“Sanırım bir mühendis...”\nAlias, uzunluk ve biçim sonucu etkiler.");
  setText(s, "v1-diagnosis", "Doğal output faydalıdır ama yüzey biçimine kırılgandır.");
  setText(s, "v2-title", "Candidate ranking");
  setText(s, "v2-replace", "Candidates: Meslek 16, 17, 18, 19");
  setText(s, "v2-result", "Top-1 = Meslek 17");
  setText(s, "v2-change", "correct_rank_mean = 1");
  setText(s, "v2-limit", "Aynı inventory; candidates model likelihood ile sıralanır.");
  setText(s, "relations", "Relation forced choice: aynı subject için yanlış relation object’i doğru binding’i geçmemelidir.");
  setText(s, "source", "Frozen candidate-ranking ve relation-binding ölçümleri; raporlar 106, 127, 136");
  setPage(s, 13);
  setNotes(s, [
    "transfer-vs-relearning/src/transfer_vs_relearning/data/candidates.py",
    "transfer-vs-relearning/src/transfer_vs_relearning/metrics/qwen_m2_m3.py",
    "documentation/136_QWEN_M2_M3_ENDPOINT_EVALUATION_GPU_ALLOCATION_STATUS.md",
  ]);
}

// 14 — PPL
{
  const s = presentation.slides.items[13];
  setText(s, "kicker", "PERPLEXITY — PPL");
  setText(s, "slide-title", "PPL factual accuracy değil, genel dil drift’ini ölçer");
  setText(s, "metric-value-generic perplexity drift", "≤1,25×");
  setText(s, "metric-label-generic perplexity drift", "frozen hard drift gate");
  setText(s, "metric-value-M1 continuations ended in EOS", "<1,10×");
  setText(s, "metric-label-M1 continuations ended in EOS", "tercih edilen bölge");
  setText(s, "preserved", "Düşük PPL: frozen generic text model için daha az şaşırtıcıdır; aynı corpus ve token stream ile karşılaştırılır.");
  setText(s, "interpretation", "Model fact’lerde güçlü ama PPL’de kötü—veya PPL’de iyi ama robust access’te zayıf—olabilir.");
  setText(s, "source", "Qwen PPL trade-off ve selected checkpoints; raporlar 106 ve 127");
  setPage(s, 14);
  const chart = s.charts.items[0];
  const series = chart.series.items[0];
  series.name = "PPL / base oranı";
  series.categories = ["Base", "İlk Qwen", "Seed 42", "Seed 43"];
  series.values = [1.0, 1.461, 1.082, 1.032];
  chart.yAxis = { min: 0, max: 1.6, majorUnit: 0.2, numberFormatCode: "0.0x", majorGridlines: { style: "solid", fill: "#D6DDE8", width: 1 } };
  chart.dataLabels = { showValue: true, position: "outEnd", textStyle: { fontSize: 12, fill: "#17243A" } };
  setNotes(s, [
    "documentation/106_M1_CROSS_FAMILY_MODEL_SCREENING_RESULT.md",
    "documentation/127_QWEN_SCALE_REPLICATION_RESULT_AND_SMOLLM_LAMBDA025_STATUS.md",
  ]);
}

// 15 — SmolLM
{
  const s = presentation.slides.items[14];
  setText(s, "kicker", "SMOLLM — 500 FACT");
  setText(s, "slide-title", "SmolLM fact’leri depoladı ama robust access çözülemedi");
  setText(s, "capacity-control", "Final gate, Forms A–D × direct/QA sekiz-hücre robustness’ı global ve relation bazında gerektiriyordu.");
  setText(s, "m360-title", "Exact storage");
  setText(s, "m360-overlap", "%100");
  setText(s, "m360-label", "canonical acquisition");
  setText(s, "arrow", "≠");
  setText(s, "m17-title", "En iyi robust access");
  setText(s, "m17-overlap", "%55,8");
  setText(s, "m17-label", "frozen gate: ≥%70");
  setText(s, "setup-text", "Control %39,6 · contrastive %52,2 · higher λ %50,4 · prompt consistency %55,8");
  setText(s, "capacity-meaning", "Müdahaleler mekanizmayı iyileştirdi; fakat SmolLM’i M2/M3 için uygun hale getirmedi.");
  setText(s, "source", "SmolLM frozen comparison ve remediation; raporlar 106, 127–128");
  setPage(s, 15);
  setNotes(s, [
    "documentation/106_M1_CROSS_FAMILY_MODEL_SCREENING_RESULT.md",
    "documentation/127_QWEN_SCALE_REPLICATION_RESULT_AND_SMOLLM_LAMBDA025_STATUS.md",
    "documentation/128_SMOLLM_500_FACT_PROMPT_CONSISTENCY_REMEDIATION_PLAN.md",
  ]);
}

// 16 — Model screen
{
  const s = presentation.slides.items[15];
  setText(s, "kicker", "MODEL AİLESİ TARAMASI");
  setText(s, "slide-title", "Factual robustness’ta yalnız Qwen tüm gate’leri geçti");
  setText(s, "metric-value-generic perplexity drift", "1,461×");
  setText(s, "metric-label-generic perplexity drift", "ilk Qwen PPL oranı");
  setText(s, "metric-value-M1 continuations ended in EOS", "0 / 5");
  setText(s, "metric-label-M1 continuations ended in EOS", "bütün gate’leri geçen aile");
  setText(s, "preserved", "Qwen held-out robustness ve relation binding’de near-ceiling sonuç verdi.");
  setText(s, "interpretation", "Sonraki adım model aramak değil, Qwen factual strength’ini retention replay ile korumaktı.");
  setText(s, "source", "Frozen 500-fact cross-family screen; rapor 106");
  setPage(s, 16);
  const chart = s.charts.items[0];
  const series = chart.series.items[0];
  series.name = "Sekiz-hücre robust accuracy (%)";
  series.categories = ["Qwen", "StableLM", "Llama", "Gemma", "SmolLM"];
  series.values = [99.6, 93.8, 81.4, 78.0, 39.6];
  chart.yAxis = { min: 0, max: 100, majorUnit: 20, numberFormatCode: "0", majorGridlines: { style: "solid", fill: "#D6DDE8", width: 1 } };
  chart.dataLabels = { showValue: true, position: "outEnd", textStyle: { fontSize: 12, fill: "#17243A" } };
  setNotes(s, ["documentation/106_M1_CROSS_FAMILY_MODEL_SCREENING_RESULT.md"]);
}

// 17 — Qwen 2500
{
  const s = presentation.slides.items[16];
  setText(s, "kicker", "QWEN — 2.500 FACT");
  setText(s, "slide-title", "Qwen M1 gate’ini iki bağımsız seed’de geçti");
  setText(s, "capacity-control", "Frozen kural, exact, hard, robust, binding, PPL ve integrity gate’lerini geçen en erken checkpoint’i seçti.");
  setText(s, "m360-title", "Seed 42 · step 75");
  setText(s, "m360-overlap", "%96,08");
  setText(s, "m360-label", "robust · exact %99,96 · PPL ×1,082");
  setText(s, "arrow", "↔");
  setText(s, "m17-title", "Seed 43 · step 50");
  setText(s, "m17-overlap", "%96,20");
  setText(s, "m17-label", "robust · exact %99,68 · PPL ×1,032");
  setText(s, "setup-text", "500 subject · 2.500 fact · seed başına 20.000 hard probe · Forms A–D × direct/QA");
  setText(s, "capacity-meaning", "Qwen replicated intermediate-scale M1 oldu; iki selected artifact freeze edildi.");
  setText(s, "source", "Qwen scale replication ve artifact freeze; rapor 127");
  setPage(s, 17);
  setNotes(s, ["documentation/127_QWEN_SCALE_REPLICATION_RESULT_AND_SMOLLM_LAMBDA025_STATUS.md"]);
}

// 18 — Pre-M2 baseline
{
  const s = presentation.slides.items[17];
  setText(s, "kicker", "TÜRKÇE ADAPTATION ÖNCESİ");
  setText(s, "slide-title", "M1’de Türkçe promptlardan zaten kısmi access vardı");
  setText(s, "v1-title", "M1 seed 42 · step 75");
  setText(s, "v1-result", "EN→EN %99,29 · TR→EN %52,03");
  setText(s, "v1-weak", "Türkçe uçtan uca");
  setText(s, "v1-lines", "TR→TR %29,05\nEN PPL 15,909 · TR PPL 17,349");
  setText(s, "v1-diagnosis", "Türkçe adaptation başlamadan önce cross-lingual access mevcuttu.");
  setText(s, "v2-title", "M1 seed 43 · step 50");
  setText(s, "v2-replace", "EN→EN %99,24\nTR→EN %52,52");
  setText(s, "v2-result", "TR→TR %30,12");
  setText(s, "v2-change", "EN PPL 15,170 · TR PPL 15,741");
  setText(s, "v2-limit", "İki seed, causal family için neredeyse aynı factual başlangıç noktasını verdi.");
  setText(s, "relations", "M2’nin hem Türkçe access’i artırma alanı hem de koruması gereken mevcut access vardı.");
  setText(s, "source", "Frozen bilingual/PPL M1 baseline; raporlar 134 ve 136");
  setPage(s, 18);
  setNotes(s, [
    "documentation/134_QWEN_PRE_M2_GPU_BLOCKER_AND_OFFLINE_PREPARATION_STATUS.md",
    "documentation/136_QWEN_M2_M3_ENDPOINT_EVALUATION_GPU_ALLOCATION_STATUS.md",
  ]);
}

// 19 — M2/M3 design
{
  const s = presentation.slides.items[18];
  setText(s, "kicker", "M2/M3 MÜDAHALESİ");
  setText(s, "slide-title", "M2 ve M3 yalnız factual exposure bakımından ayrıldı");
  setText(s, "v1-title", "M2-clean");
  setText(s, "v1-result", "1.048.576 token · 128 update");
  setText(s, "v1-weak", "Exposure kuralı");
  setText(s, "v1-lines", "Generic Turkish + neutral filler\nSıfır target synthetic fact");
  setText(s, "v1-diagnosis", "Temiz Türkçe adaptation mevcut factual access’e ne yapıyor?");
  setText(s, "v2-title", "M3-fact");
  setText(s, "v2-replace", "Aynı Turkish blocks ve bütçe\nNeutral filler yerine doğru Branch B fact’leri");
  setText(s, "v2-result", "1.048.576 token · 128 update");
  setText(s, "v2-change", "4 cycle · 5.000 factual exposure");
  setText(s, "v2-limit", "Branch A sıfır exposure alır; M3, M2’den değil matching M1’den başlar.");
  setText(s, "relations", "Primary estimand: [(M3 − M2) Branch B] − [(M3 − M2) Branch A], TR→EN");
  setText(s, "source", "Frozen matched-input causal contract; raporlar 133 ve 135");
  setPage(s, 19);
  setNotes(s, [
    "documentation/133_QWEN_2500_FACT_M2_M3_EXECUTION_HANDOFF_PLAN.md",
    "documentation/135_QWEN_M2_M3_CONTRACT_AND_MATERIALIZATION_STATUS.md",
  ]);
}

// 20 — Execution
{
  const s = presentation.slides.items[19];
  setText(s, "kicker", "YÜRÜTME VE BÜTÜNLÜK");
  setText(s, "slide-title", "Dört run tek bir precommitted endpoint’te değerlendirildi");
  setText(s, "attempt-title-0", "Training — 1 Ağustos");
  setText(s, "attempt-example-0", "Seed 42 ve 43 için ayrı M2-clean/M3-fact siblings; her çift matching frozen M1’den başladı.");
  setText(s, "attempt-result-0", "Dördü de 128 update tamamladı · fixed checkpoint-128");
  setText(s, "attempt-title-1", "Evaluation — 2 Ağustos");
  setText(s, "attempt-example-1", "State başına 24 slice × 2.500 probe; bütün form, scaffold ve direction hücreleri.");
  setText(s, "attempt-result-1", "96 / 96 slice · 240.000 M2/M3 endpoint probe");
  setText(s, "attempt-title-2", "Independent review — 3 Ağustos");
  setText(s, "attempt-example-2", "Raw manifests, registry membership, hashes, bootstrap logic ve gate read-only kontrol edildi.");
  setText(s, "attempt-result-2", "PASS WITH CONCERNS · blocker veya major issue yok");
  setText(s, "attempt-lesson-text", "Sonuç görüldükten sonra checkpoint, seed, threshold veya primary metric seçilmedi.");
  setText(s, "source", "Execution, independent review ve retention freeze; raporlar 135, 136, 140a, 143");
  setPage(s, 20);
  setNotes(s, [
    "documentation/135_QWEN_M2_M3_CONTRACT_AND_MATERIALIZATION_STATUS.md",
    "documentation/136_QWEN_M2_M3_ENDPOINT_EVALUATION_GPU_ALLOCATION_STATUS.md",
    "documentation/140a_QWEN_M2_M3_INDEPENDENT_REVIEW_RESULT_EN.md",
    "documentation/143_QWEN_M2_M3_ARTIFACT_RETENTION_FREEZE_AND_STORAGE_AUDIT_EN.md",
  ]);
}

// 21 — TR→EN
{
  const s = presentation.slides.items[20];
  setText(s, "kicker", "PRIMARY DIRECTION: TR→EN");
  setText(s, "slide-title", "Türkçe adaptation access’i düşürdü; M3 azını geri aldı");
  setText(s, "metric-value-generic perplexity drift", "−18,8 pp");
  setText(s, "metric-label-generic perplexity drift", "M1 → M2, iki seed");
  setText(s, "metric-value-M1 continuations ended in EOS", "+1,9 pp");
  setText(s, "metric-label-M1 continuations ended in EOS", "M2 → M3, iki seed");
  setText(s, "preserved", "Dominant effect: M2’de geniş Turkish-prompt factual-access degradation.");
  setText(s, "interpretation", "M3 iki seed’de M2’den yüksek; ancak M1 baseline’ın çok altında kalıyor.");
  setText(s, "source", "Frozen state accuracy ve paired contrasts; raporlar 136 ve 142");
  setPage(s, 21);
  const chart = s.charts.items[0];
  const series = chart.series.items[0];
  series.name = "TR→EN top-1 accuracy (%)";
  series.categories = ["M1\nS42", "M2\nS42", "M3\nS42", "M1\nS43", "M2\nS43", "M3\nS43"];
  series.values = [52.03, 33.29, 35.14, 52.52, 33.70, 35.59];
  chart.yAxis = { min: 0, max: 60, majorUnit: 10, numberFormatCode: "0", majorGridlines: { style: "solid", fill: "#D6DDE8", width: 1 } };
  chart.dataLabels = { showValue: true, position: "outEnd", textStyle: { fontSize: 11, fill: "#17243A" } };
  setNotes(s, [
    "documentation/136_QWEN_M2_M3_ENDPOINT_EVALUATION_GPU_ALLOCATION_STATUS.md",
    "documentation/142_QWEN_M2_M3_EXPLORATORY_MECHANISM_ANALYSIS_RESULT_EN.md",
  ]);
}

// 22 — TR→TR
{
  const s = presentation.slides.items[21];
  setText(s, "kicker", "SECONDARY DIRECTION: TR→TR");
  setText(s, "slide-title", "Türkçe cevap üretiminde de aynı yönlü pattern görüldü");
  setText(s, "metric-value-generic perplexity drift", "−6,7 pp");
  setText(s, "metric-label-generic perplexity drift", "M1 → M2, yaklaşık");
  setText(s, "metric-value-M1 continuations ended in EOS", "+1,6–1,7 pp");
  setText(s, "metric-label-M1 continuations ended in EOS", "M2 → M3");
  setText(s, "preserved", "TR→TR, factual access ile Turkish object lexicalization’ı birlikte ölçer.");
  setText(s, "interpretation", "Bu secondary pattern primary TR→EN sonucunu destekler; onun yerine geçmez.");
  setText(s, "source", "Frozen state accuracy ve paired contrasts; rapor 136");
  setPage(s, 22);
  const chart = s.charts.items[0];
  const series = chart.series.items[0];
  series.name = "TR→TR top-1 accuracy (%)";
  series.categories = ["M1\nS42", "M2\nS42", "M3\nS42", "M1\nS43", "M2\nS43", "M3\nS43"];
  series.values = [29.05, 22.46, 24.04, 30.12, 23.25, 24.97];
  chart.yAxis = { min: 0, max: 35, majorUnit: 5, numberFormatCode: "0", majorGridlines: { style: "solid", fill: "#D6DDE8", width: 1 } };
  chart.dataLabels = { showValue: true, position: "outEnd", textStyle: { fontSize: 11, fill: "#17243A" } };
  setNotes(s, ["documentation/136_QWEN_M2_M3_ENDPOINT_EVALUATION_GPU_ALLOCATION_STATUS.md"]);
}

// 23 — Primary gate
{
  const s = presentation.slides.items[22];
  setText(s, "kicker", "FROZEN PRIMARY GATE");
  setText(s, "slide-title", "Primary causal interaction iki seed’de replicate olmadı");
  setText(s, "capacity-control", "Interaction = (M3 − M2) Branch B − (M3 − M2) Branch A, TR→EN; iki seed’in CI’ı da sıfırı dışlamalıydı.");
  setText(s, "m360-title", "Seed 42");
  setText(s, "m360-overlap", "+0,25 pp");
  setText(s, "m360-label", "%95 CI −0,51 ile +1,01 · FAIL");
  setText(s, "arrow", "≠");
  setText(s, "m17-title", "Seed 43");
  setText(s, "m17-overlap", "+1,35 pp");
  setText(s, "m17-label", "%95 CI +0,51 ile +2,18 · PASS");
  setText(s, "setup-text", "Operational validity geçti · EN→EN retention guardrail geçti · post-hoc gate change yok");
  setText(s, "capacity-meaning", "Overall frozen decision: primary_success_criterion_not_met");
  setText(s, "source", "Frozen gate ve independent raw-data reproduction; raporlar 136 ve 140a");
  setPage(s, 23);
  setNotes(s, [
    "documentation/136_QWEN_M2_M3_ENDPOINT_EVALUATION_GPU_ALLOCATION_STATUS.md",
    "documentation/140a_QWEN_M2_M3_INDEPENDENT_REVIEW_RESULT_EN.md",
  ]);
}

// 24 — Interpretation
{
  const s = presentation.slides.items[23];
  setText(s, "kicker", "BİLİMSEL YORUM");
  setText(s, "headline", "Causal family tamamlandı; tez sorusu tamamlanmadı");
  setText(s, "close-label-0", "Bildiklerimiz");
  setText(s, "close-body-0", "İngilizcede edinilmiş fact’lere Türkçe promptlardan kısmi erişim vardı; clean adaptation bu access’i güçlü biçimde düşürdü.");
  setText(s, "close-label-1", "M3 ne ekledi?");
  setText(s, "close-body-1", "Doğru Turkish factual exposure, M2-clean’e göre küçük ve iki seed’de aynı yönlü descriptive recovery üretti.");
  setText(s, "close-label-2", "Ne diyemeyiz?");
  setText(s, "close-body-2", "Branch-B-specific factual relearning advantage, precommitted two-seed confidence rule altında replicate edilmedi.");
  setText(s, "discussion-text", "Bu geçerli bir negative/inconclusive sonuçtur; başarısız deney veya bütün transfer mekanizmalarının tükendiği anlamına gelmez.");
  setPage(s, 24);
  setNotes(s, [
    "documentation/138_QWEN_M2_M3_COMPLETED_MILESTONE_AND_SCIENTIFIC_INTERPRETATION_EN.md",
    "documentation/140a_QWEN_M2_M3_INDEPENDENT_REVIEW_RESULT_EN.md",
    "documentation/142_QWEN_M2_M3_EXPLORATORY_MECHANISM_ANALYSIS_RESULT_EN.md",
  ]);
}

// 25 — What remains
{
  const s = presentation.slides.items[24];
  setText(s, "kicker", "BUNDAN SONRA");
  setText(s, "slide-title", "Bu deney tamamlandı; önemli tez ve mekanizma işi sürüyor");
  setText(s, "ranking-title", "Yeni eğitim olmadan");
  setText(s, "ranking-example", "Final şekiller, yöntemler, sınırlılıklar, seed heterojenliği ve genel Türkçe erişim düşüşü yorumu tamamlanabilir.");
  setText(s, "ranking-result", "Doğrulanmış kanıt zinciri, tez anlatısına ve supervisor görüşmesine hazır kararlara dönüştürülmeli.");
  setText(s, "binding-title", "Olası revize deneyler");
  setText(s, "binding-example", "M3-lexical, revize Türkçe müdahale, ek replication veya 25.000-fact ölçek doğrulaması.");
  setText(s, "binding-result", "Her seçenek ayrı gerekçe, frozen contract, estimand ve gate gerektirir; hiçbiri otomatik değildir.");
  setText(s, "strategy-shift", "Karar sınırı");
  setText(s, "strategy-body", "2.500-fact family ana current result olarak korunmalı; yeni experiment yalnız belirli bir mekanizma açığını çözmelidir.");
  setText(s, "source", "Current milestone, review, exploratory result ve retention closure; raporlar 138, 140a, 142, 143");
  setPage(s, 25);
  setNotes(s, [
    "documentation/138_QWEN_M2_M3_COMPLETED_MILESTONE_AND_SCIENTIFIC_INTERPRETATION_EN.md",
    "documentation/139_POST_M2_M3_INDEPENDENT_NEXT_ACTION_PLAN_EN.md",
    "documentation/140a_QWEN_M2_M3_INDEPENDENT_REVIEW_RESULT_EN.md",
    "documentation/142_QWEN_M2_M3_EXPLORATORY_MECHANISM_ANALYSIS_RESULT_EN.md",
    "documentation/143_QWEN_M2_M3_ARTIFACT_RETENTION_FREEZE_AND_STORAGE_AUDIT_EN.md",
  ]);
}

const inspect = await presentation.inspect({
  kind: "slide,textbox,shape,chart,notes,layout",
  maxChars: 300000,
});
await fs.writeFile(
  "/Users/umutyesildal/Desktop/UniDE/Semester6/Thesis/implementation/outputs/qwen_m2_m3_arastirma_guncellemesi_tr_agustos_2026.pptx.inspect.ndjson",
  inspect.ndjson,
);

const pptx = await PresentationFile.exportPptx(presentation);
await pptx.save(OUTPUT);
console.log(OUTPUT);
