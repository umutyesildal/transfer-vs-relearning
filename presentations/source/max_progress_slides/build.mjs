import fs from "node:fs/promises";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const OUT = "/Users/umutyesildal/Desktop/UniDE/Semester6/Thesis/implementation/Max_Meeting_Progress_and_One_Month_Plan.pptx";
const PREVIEW = "/Users/umutyesildal/Desktop/UniDE/Semester6/Thesis/implementation/.tmp/max_progress_slides/preview";

async function readImageBlob(imagePath) {
  const bytes = await fs.readFile(imagePath);
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
}

const rasterizeChartSlides = process.env.RASTERIZE_CHART_SLIDES === "1";
const chartSlide2Raster = rasterizeChartSlides ? await readImageBlob(`${PREVIEW}/slide-02.png`) : null;
const chartSlide3Raster = rasterizeChartSlides ? await readImageBlob(`${PREVIEW}/slide-03.png`) : null;
const vngrsSampleRaster = await readImageBlob("/Users/umutyesildal/Desktop/UniDE/Semester6/Thesis/implementation/.tmp/max_progress_slides/assets/vngrs_sample.png");

const C = {
  bg: "#F7F7F5",
  ink: "#111111",
  muted: "#646464",
  grid: "#D8D8D2",
  blue: "#2F66F3",
  blue2: "#8AA8FF",
  cyan: "#00A7A7",
  orange: "#F28C28",
  red: "#D64545",
  green: "#2E8B57",
  white: "#FFFFFF",
  paleBlue: "#EAF0FF",
  paleOrange: "#FFF0DF",
  paleGreen: "#E7F4EC",
};

const deck = Presentation.create({ slideSize: { width: 1280, height: 720 } });

function box(slide, left, top, width, height, fill = C.white, line = C.grid, radius = "rounded-xl") {
  return slide.shapes.add({
    geometry: "roundRect",
    position: { left, top, width, height },
    fill,
    line: { style: "solid", fill: line, width: 1 },
    borderRadius: radius,
  });
}

function text(slide, value, left, top, width, height, opts = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    position: { left, top, width, height },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = value;
  shape.text.style = {
    fontFamily: "Aptos",
    fontSize: opts.fontSize ?? 18,
    bold: opts.bold ?? false,
    color: opts.color ?? C.ink,
    alignment: opts.align ?? "left",
    verticalAlignment: opts.vAlign ?? "top",
  };
  return shape;
}

function addBase(slide, number, eyebrow, title, subtitle = "") {
  slide.background.fill = C.bg;
  text(slide, eyebrow.toUpperCase(), 54, 28, 350, 24, { fontSize: 12, bold: true, color: C.blue });
  text(slide, title, 54, 62, 1170, 55, { fontSize: 38, bold: true });
  if (subtitle) text(slide, subtitle, 54, 116, 1160, 32, { fontSize: 18, color: C.muted });
  slide.shapes.add({ geometry: "rect", position: { left: 54, top: 672, width: 1172, height: 1 }, fill: C.grid, line: { fill: "none", width: 0 } });
  text(slide, `TRANSFER VS. RELEARNING  •  ${String(number).padStart(2, "0")} / 06`, 54, 681, 450, 20, { fontSize: 11, bold: true, color: C.muted });
}

function notes(slide, presenter, sources) {
  slide.speakerNotes.textFrame.setText(`${presenter}\n\n[Sources]\n${sources.map((s) => `- ${s}`).join("\n")}`);
}

// 1 — Cover
{
  const s = deck.slides.add();
  s.background.fill = C.bg;
  text(s, "THESIS PROGRESS REVIEW", 72, 54, 400, 28, { fontSize: 13, bold: true, color: C.blue });
  text(s, "From model screening\nto the final thesis experiment", 72, 150, 790, 190, { fontSize: 60, bold: true });
  text(s, "M1 evidence · Turkish corpus decision · one-month closure plan", 76, 368, 780, 40, { fontSize: 22, color: C.muted });
  box(s, 930, 144, 250, 252, C.ink, C.ink);
  text(s, "01", 970, 174, 170, 70, { fontSize: 58, bold: true, color: C.white, align: "center" });
  text(s, "month to a\ndecision-complete\nthesis", 966, 255, 180, 110, { fontSize: 24, bold: true, color: C.white, align: "center" });
  slideFooter(s, "14 AUGUST 2026");
  notes(s, "Open with the change in emphasis: the project now has enough M1 evidence to stop broad model search and close the causal Turkish-adaptation experiment.", [
    "Local: documentation/144_SUPERVISOR_FEEDBACK_AND_SCIENTIFIC_REALIGNMENT_TR.md",
    "Local: documentation/145_LITERATURE_FIRST_M1_MODEL_AND_TURKISH_ADAPTATION_ROUTE_TR.md",
  ]);
}

function slideFooter(slide, label) {
  slide.shapes.add({ geometry: "rect", position: { left: 72, top: 632, width: 1136, height: 1 }, fill: C.grid, line: { fill: "none", width: 0 } });
  text(slide, label, 72, 650, 300, 18, { fontSize: 11, bold: true, color: C.muted });
  text(slide, "TRANSFER VS. RELEARNING", 920, 650, 288, 18, { fontSize: 11, bold: true, color: C.muted, align: "right" });
}

// 2 — Earlier models
{
  const s = deck.slides.add();
  addBase(s, 2, "Earlier M1 screens", "Earlier screens show one recurring trade-off", "Paired bars: blue = robust fact access; orange = retention score (100 ÷ PPL ratio). Higher is better.");
  box(s, 54, 164, 1172, 424);
  text(s, "FACT ACCESS VS. RETENTION", 82, 186, 310, 22, { fontSize: 12, bold: true, color: C.muted });
  text(s, "Five model families, same 500-fact screen", 82, 210, 530, 28, { fontSize: 24, bold: true });
  s.charts.add("bar", {
    position: { left: 96, top: 250, width: 1060, height: 278 },
    categories: ["SmolLM2", "Qwen2.5", "StableLM2", "Gemma-2", "Llama-3.2"],
    series: [
      { name: "Robust fact access (%)", values: [39.6, 99.6, 93.8, 78.0, 81.4], fill: C.blue },
      { name: "Retention score (rounded)", values: [93, 68, 68, 0, 26], fill: C.orange },
    ],
    hasLegend: true,
    legend: { position: "bottom" },
    dataLabels: { showValue: true, position: "outEnd", valuesFormatCode: "0" },
    yAxis: { minimumScale: 0, maximumScale: 110, majorUnit: 25, majorGridlines: { style: "solid", fill: C.grid, width: 1 } },
  });
  box(s, 236, 604, 808, 48, C.ink, C.ink);
  text(s, "No family jointly maximized robust access and retention.", 260, 616, 760, 24, { fontSize: 18, bold: true, color: C.white, align: "center" });
  notes(s, "The earlier screen was useful because it ruled out the idea that exact memorization alone is enough. SmolLM retained English but generalized poorly; stronger robust access came with much larger retention cost.", [
    "Local: documentation/106_M1_CROSS_FAMILY_MODEL_SCREENING_RESULT.md",
    "Local: documentation/130_TR.md",
  ]);
  if (chartSlide2Raster) s.images.add({ blob: chartSlide2Raster, contentType: "image/png", alt: "Earlier paired model chart", fit: "fill", position: { left: 0, top: 0, width: 1280, height: 720 } });
}

// 3 — Recent models
{
  const s = deck.slides.add();
  addBase(s, 3, "Last week", "The recent screen isolates OLMo as the retention candidate", "Blue = aggregate hard-suite access; orange = retention score (100 ÷ PPL ratio). Higher is better.");
  box(s, 54, 164, 1172, 424);
  text(s, "FACT ACCESS VS. RETENTION", 82, 186, 310, 22, { fontSize: 12, bold: true, color: C.muted });
  text(s, "OLMo, Falcon and Pythia", 82, 210, 470, 28, { fontSize: 24, bold: true });
  s.charts.add("bar", {
    position: { left: 130, top: 250, width: 990, height: 278 },
    categories: ["OLMo", "Falcon", "Pythia"],
    series: [
      { name: "Hard-suite access (%)", values: [98.275, 97.025, 98.175], fill: C.blue },
      { name: "Retention score", values: [66.2, 9.1, 6.2], fill: C.orange },
    ],
    hasLegend: true,
    legend: { position: "bottom" },
    dataLabels: { showValue: true, position: "outEnd", valuesFormatCode: "0.0" },
    yAxis: { minimumScale: 0, maximumScale: 110, majorUnit: 25, majorGridlines: { style: "solid", fill: C.grid, width: 1 } },
  });
  box(s, 54, 600, 1172, 52, C.paleBlue, C.blue);
  text(s, "Worst relation floor: OLMo 59% · Falcon 37% · Pythia 65%   |   OLMo checkpoint 42 retention score: 72.2", 78, 613, 1124, 24, { fontSize: 17, bold: true, color: C.ink, align: "center" });
  notes(s, "Aggregate hard-suite scores were 97–98%, so the decisive differences are the relation floor and retention. OLMo is not a PASS, but it is the only model worth one precommitted early-stop decision rather than more open-ended recipe search.", [
    "Local: documentation/158_PYTHIA_REPAIR_POST_EXECUTION_AND_THREE_MODEL_GATE_TR.md",
    "Local: documentation/160_M1_DOSE_PARETO_OLMO_BF16_EXECUTION_AND_FAMILY_STATUS_TR.md",
    "Local: documentation/176_M1_DOSE_PARETO_POST_FALCON_AUDIT_PERSISTENT_RECOVERY_GATE_TR.md",
  ]);
  if (chartSlide3Raster) s.images.add({ blob: chartSlide3Raster, contentType: "image/png", alt: "Recent paired model chart", fit: "fill", position: { left: 0, top: 0, width: 1280, height: 720 } });
}

// 4 — Corpus decision
{
  const s = deck.slides.add();
  addBase(s, 4, "Corpus decision", "Why vngrs is the strongest corpus candidate", "Public, paper-backed, source-tagged Turkish web text — broad enough to replace Wikipedia-only adaptation.");
  box(s, 54, 164, 704, 468);
  text(s, "WHO USED WHAT?", 82, 186, 220, 22, { fontSize: 12, bold: true, color: C.muted });
  const rows = [
    ["VBART", "vngrs: OSCAR + mC4", "arxiv.org/abs/2403.01308"],
    ["TURNA", "vngrs + academic text", "aclanthology.org/2024.findings-acl.600"],
    ["MODA", "Qwen2.5 CPT on vngrs", "aclanthology.org/2026.sigturk-1.17"],
    ["LlamaTurk", "Turkish Wikipedia", "aclanthology.org/2024.mrl-1.3"],
    ["SambaLingo-TR", "CulturaX TR + English", "hf.co/sambanovasystems/SambaLingo-Turkish-Base"],
    ["ModernBERT-TR", "FineWeb2-TR + BERTurk", "cosmos-ytu.github.io/modernbert-tr-1k"],
  ];
  let y = 226;
  for (const [model, corpus, link] of rows) {
    const fill = ["VBART", "TURNA", "MODA"].includes(model) ? C.paleBlue : C.white;
    box(s, 82, y, 648, 55, fill, C.grid, "rounded-md");
    text(s, model, 98, y + 9, 155, 22, { fontSize: model === "ModernBERT-TR" ? 14 : 16, bold: true, color: ["VBART", "TURNA", "MODA"].includes(model) ? C.blue : C.ink });
    text(s, corpus, 252, y + 9, 235, 22, { fontSize: 15, color: C.ink });
    text(s, link, 490, y + 10, 222, 34, { fontSize: 9, bold: true, color: C.blue });
    y += 59;
  }
  box(s, 782, 164, 444, 468, C.ink, C.ink);
  text(s, "WHY VNGRS", 812, 188, 200, 22, { fontSize: 12, bold: true, color: C.blue2 });
  text(s, "84.9 GB", 812, 226, 250, 50, { fontSize: 40, bold: true, color: C.white });
  text(s, "50.3M source-tagged rows\nOSCAR + mC4 web text", 812, 278, 340, 58, { fontSize: 19, color: C.white });
  text(s, "• Used in Turkish CPT papers\n• Broader than Wikipedia\n• Manageable on HU scratch\n• Auditable source labels\n• No instruction-mixture confound", 812, 365, 354, 154, { fontSize: 18, color: C.white });
  box(s, 812, 540, 354, 58, C.paleOrange, C.paleOrange);
  text(s, "Caveat: noisy web data — manual quality audit is mandatory.", 828, 552, 322, 36, { fontSize: 16, bold: true, color: C.ink, align: "center" });
  notes(s, "vngrs is not selected because it is clean by assumption. It is selected because it has the strongest combination of precedent, manageable scale, broad domain coverage and auditable source labels. The caveat is precisely why the next stage begins with human inspection.", [
    "https://huggingface.co/datasets/vngrs-ai/vngrs-web-corpus",
    "https://arxiv.org/abs/2403.01308",
    "https://aclanthology.org/2024.findings-acl.600/",
    "https://aclanthology.org/2026.sigturk-1.17/",
    "https://huggingface.co/vngrs-ai/Kumru-2B-Base",
    "https://aclanthology.org/2024.mrl-1.3/",
    "https://huggingface.co/sambanovasystems/SambaLingo-Turkish-Base",
    "https://cosmos-ytu.github.io/modernbert-tr-1k/",
    "Local: documentation/148_CROSS_LINGUAL_LANGUAGE_ADAPTATION_LITERATURE_MATRIX_TR.md",
  ]);
}

// 5 — Corpus workflow
{
  const s = deck.slides.add();
  addBase(s, 5, "Corpus workflow", "vngrs: inspect first, then train", "The public release already exposes source labels and raw web-text variation.");
  box(s, 54, 176, 696, 420, C.ink, C.ink);
  s.images.add({ blob: vngrsSampleRaster, contentType: "image/png", alt: "vngrs dataset viewer showing text, corpus and original_id fields", fit: "contain", position: { left: 68, top: 190, width: 668, height: 392 } });
  text(s, "REAL VNGRS SAMPLE", 76, 602, 240, 22, { fontSize: 12, bold: true, color: C.blue });
  text(s, "Source labels make OSCAR / mC4 strata directly auditable.", 264, 600, 486, 24, { fontSize: 16, bold: true, color: C.ink });
  s.shapes.add({ geometry: "rect", position: { left: 816, top: 226, width: 8, height: 310 }, fill: C.blue2, line: { fill: "none", width: 0 } });
  const steps = [
    ["1", "Download", "Full 85 GB release to HU scratch"],
    ["2", "Inspect", "Stratified human sample by source"],
    ["3", "Freeze", "Filters, splits and exact hashes"],
    ["4", "Verify", "Turkish gain + English retention, then M2-A/M2-B"],
  ];
  let y = 190;
  for (const [n, h, body] of steps) {
    box(s, 790, y, 56, 48, C.blue, C.blue, "rounded-full");
    text(s, n, 790, y + 11, 56, 24, { fontSize: 18, bold: true, color: C.white, align: "center" });
    text(s, h, 872, y + 1, 270, 26, { fontSize: 22, bold: true });
    text(s, body, 872, y + 30, 310, 38, { fontSize: 16, color: C.muted });
    y += 100;
  }
  notes(s, "The corpus stage is a scientific gate, not just preprocessing. We must show that the Turkish dose genuinely changes Turkish capability while preserving enough English competence; otherwise a null factual result remains uninterpretable.", [
    "https://huggingface.co/datasets/vngrs-ai/vngrs-web-corpus",
    "Local: documentation/145_LITERATURE_FIRST_M1_MODEL_AND_TURKISH_ADAPTATION_ROUTE_TR.md",
    "Local: documentation/151bq_VNGRS_CLUSTERED_WINDOW_SAMPLE_DESIGN_AND_EXECUTION_CONTRACT_TR.md",
  ]);
}

// 6 — One month plan
{
  const s = deck.slides.add();
  addBase(s, 6, "Next four weeks", "Four focused weeks can close the core experimental loop", "Priority order: model decision → corpus freeze → causal comparison → thesis integration.");
  const weeks = [
    ["WEEK 1", "Decide M1 + acquire vngrs", "Precommit OLMo early checkpoint decision. Download, hash and stratify the full corpus."],
    ["WEEK 2", "Audit + freeze corpus", "Human quality audit, filters, contamination checks, train/val/test and dose subsets."],
    ["WEEK 3", "Run M2-A / M2-B", "Matched Turkish adaptation arms; manipulation checks; two seeds if compute permits."],
    ["WEEK 4", "Analyze + write", "Bootstrap contrasts, retention analysis, artifact freeze, near-final Results and Discussion."],
  ];
  let x = 54;
  for (let i = 0; i < weeks.length; i++) {
    const [w, h, body] = weeks[i];
    const accent = [C.blue, C.cyan, C.orange, C.green][i];
    box(s, x, 186, 275, 376, C.white, C.grid);
    s.shapes.add({ geometry: "rect", position: { left: x, top: 186, width: 275, height: 10 }, fill: accent, line: { fill: "none", width: 0 } });
    text(s, w, x + 24, 222, 220, 22, { fontSize: 13, bold: true, color: accent });
    text(s, h, x + 24, 270, 220, 80, { fontSize: 25, bold: true });
    text(s, body, x + 24, 372, 222, 130, { fontSize: 18, color: C.muted });
    x += 299;
  }
  box(s, 224, 590, 832, 58, C.paleOrange, C.orange);
  text(s, "Stop rule: if OLMo still misses retention, freeze it as a negative — no open-ended model fishing.", 248, 606, 784, 26, { fontSize: 18, bold: true, align: "center" });
  notes(s, "This plan is deliberately linear. The main risk is GPU access, not an unresolved scientific decision. The stop rule protects the month from becoming another optimization loop.", [
    "Local: documentation/159_M1_THREE_MODEL_DOSE_PARETO_REMEDIATION_CONTRACT_TR.md",
    "Local: documentation/160_M1_DOSE_PARETO_OLMO_BF16_EXECUTION_AND_FAMILY_STATUS_TR.md",
    "Local: documentation/145_LITERATURE_FIRST_M1_MODEL_AND_TURKISH_ADAPTATION_ROUTE_TR.md",
  ]);
}

async function writeBlob(path, blob) {
  await fs.writeFile(path, new Uint8Array(await blob.arrayBuffer()));
}

await fs.mkdir(PREVIEW, { recursive: true });
for (const [index, slide] of deck.slides.items.entries()) {
  const stem = `slide-${String(index + 1).padStart(2, "0")}`;
  const png = await deck.export({ slide, format: "png", scale: 1 });
  await writeBlob(`${PREVIEW}/${stem}.png`, png);
  const layout = await slide.export({ format: "layout" });
  await fs.writeFile(`${PREVIEW}/${stem}.layout.json`, await layout.text());
}
const montage = await deck.export({ format: "webp", montage: true, scale: 1 });
await writeBlob(`${PREVIEW}/montage.webp`, montage);
const pptx = await PresentationFile.exportPptx(deck);
await pptx.save(OUT);
console.log(OUT);
