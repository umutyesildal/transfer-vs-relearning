import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const STARTER = "/Users/umutyesildal/Desktop/UniDE/Semester6/Thesis/implementation/tmp/m2m3_supervisor_deck_20260803/template-starter.pptx";
const OUTPUT = "/Users/umutyesildal/Desktop/UniDE/Semester6/Thesis/implementation/outputs/qwen_m2_m3_research_update_august_2026.pptx";

const presentation = await PresentationFile.importPptx(await FileBlob.load(STARTER));

function shapeByName(slide, name) {
  const shape = slide.shapes.items.find((item) => item.name === name);
  if (!shape) throw new Error(`Missing inherited shape '${name}'`);
  return shape;
}

function setText(slide, name, value) {
  shapeByName(slide, name).text = value;
}

function setNotes(slide, sources) {
  slide.speakerNotes.textFrame.setText(`[Sources]\n${sources.map((s) => `- ${s}`).join("\n")}`);
  slide.speakerNotes.setVisible(true);
}

function setPage(slide, page) {
  const pageShape = slide.shapes.items.find((item) => item.name === "page");
  if (pageShape) pageShape.text = String(page);
}

// 1 — Title
{
  const s = presentation.slides.items[0];
  setText(s, "eyebrow", "THESIS RESEARCH UPDATE");
  setText(s, "title", "From robust English acquisition\nto cross-lingual adaptation");
  setText(s, "subtitle", "What changed, what the first causal family shows, and what remains");
  setText(s, "meta", "Umut Yeşildal  ·  Thesis progress discussion  ·  August 2026");
  setText(s, "scope", "Qwen M1 replication · M2/M3 endpoint evidence · 2,500 facts");
  setNotes(s, [
    "documentation/138_QWEN_M2_M3_COMPLETED_MILESTONE_AND_SCIENTIFIC_INTERPRETATION_EN.md",
    "documentation/143_QWEN_M2_M3_ARTIFACT_RETENTION_FREEZE_AND_STORAGE_AUDIT_EN.md",
  ]);
}

// 2 — Since the last update
{
  const s = presentation.slides.items[1];
  setText(s, "kicker", "SINCE THE LAST UPDATE");
  setText(s, "headline", "We moved from an apparent M1 solution to a completed causal test");
  setText(s, "close-label-0", "Stronger measurement");
  setText(s, "close-body-0", "Subject-held-out forms showed that SmolLM’s 500-fact success depended strongly on prompt exposure.");
  setText(s, "close-label-1", "Model decision");
  setText(s, "close-body-1", "A frozen cross-family screen and retention replay selected Qwen, replicated at 2,500 facts.");
  setText(s, "close-label-2", "Causal execution");
  setText(s, "close-body-2", "M2-clean and M3-fact completed in two seed chains at a fixed endpoint with 240,000 endpoint probes.");
  setText(s, "discussion-text", "The result is valid but not conclusive: M3 partially recovers access, while the primary interaction replicates in only one seed.");
  setPage(s, 2);
  setNotes(s, [
    "documentation/95_PRE_M2_PARAPHRASE_COUNTERBALANCE_REPORT.md",
    "documentation/106_M1_CROSS_FAMILY_MODEL_SCREENING_RESULT.md",
    "documentation/127_QWEN_SCALE_REPLICATION_RESULT_AND_SMOLLM_LAMBDA025_STATUS.md",
    "documentation/136_QWEN_M2_M3_ENDPOINT_EVALUATION_GPU_ALLOCATION_STATUS.md",
  ]);
}

// 3 — Research question
{
  const s = presentation.slides.items[2];
  setText(s, "kicker", "RESEARCH QUESTION");
  setText(s, "slide-title", "The target is transfer versus relearning");
  setText(s, "question", "Can Turkish adaptation expose an English-learned fact without seeing that fact again—and what changes when the fact is repeated?");
  setText(s, "stage-id-0", "M0");
  setText(s, "stage-title-0", "Absent knowledge");
  setText(s, "stage-body-0", "Verify that the synthetic binding is not already accessible.");
  setText(s, "stage-id-1", "M1");
  setText(s, "stage-title-1", "English acquisition");
  setText(s, "stage-body-1", "Store and robustly retrieve all target facts in English.");
  setText(s, "stage-id-2", "M2");
  setText(s, "stage-title-2", "Clean Turkish");
  setText(s, "stage-body-2", "Adapt to Turkish without repeating any target binding.");
  setText(s, "stage-id-3", "M3");
  setText(s, "stage-title-3", "Turkish facts");
  setText(s, "stage-body-3", "Repeat only Branch B facts under a matched adaptation budget.");
  setText(s, "takeaway", "Matched M2/M3 siblings separate generic adaptation from controlled factual re-exposure.");
  setText(s, "source", "Expose design; frozen causal contract in reports 133–136");
  setPage(s, 3);
  setNotes(s, [
    "documentation/100_MASTER_PROJECT_STATUS_AND_EXECUTION_PLAN.md",
    "documentation/133_QWEN_2500_FACT_M2_M3_EXECUTION_HANDOFF_PLAN.md",
    "documentation/135_QWEN_M2_M3_CONTRACT_AND_MATERIALIZATION_STATUS.md",
  ]);
}

// 4 — Probe evolution
{
  const s = presentation.slides.items[3];
  setText(s, "kicker", "MEASUREMENT EVOLUTION");
  setText(s, "slide-title", "Exact storage does not guarantee robust access");
  setText(s, "fact", "One fact  →  multiple unseen retrieval conditions");
  setText(s, "train-form", "The evaluator became progressively harder before M2/M3 was allowed.");
  setText(s, "initial-probe-title-0", "Exact-prefix");
  setText(s, "initial-probe-example-0", "Can the model complete the canonical fact string?");
  setText(s, "initial-probe-result-0", "Tests storage");
  setText(s, "initial-probe-title-1", "Held-out forms");
  setText(s, "initial-probe-example-1", "Forms A–D under direct and QA scaffolds");
  setText(s, "initial-probe-result-1", "Tests prompt transfer");
  setText(s, "initial-probe-title-2", "Binding + retention");
  setText(s, "initial-probe-example-2", "Forced choice, PPL, generic outputs, intrusion");
  setText(s, "initial-probe-result-2", "Tests interpretation");
  setText(s, "initial-result-text", "A fact is robust only when it survives every required form/scaffold cell—not when one familiar prompt succeeds.");
  setText(s, "source", "Frozen hard evaluation, counterbalance, relation binding and PPL controls; reports 94–98");
  setPage(s, 4);
  setNotes(s, [
    "documentation/94_PRE_M2_FROZEN_HARD_EVALUATION_REPORT.md",
    "documentation/95_PRE_M2_PARAPHRASE_COUNTERBALANCE_REPORT.md",
    "documentation/96_PRE_M2_JOINT_RELATION_CONTROL_REPORT.md",
    "documentation/97_PRE_M2_DRIFT_ABLATION_REPORT.md",
  ]);
}

// 5 — SmolLM result
{
  const s = presentation.slides.items[4];
  setText(s, "kicker", "SMOLLM AT 500 FACTS");
  setText(s, "slide-title", "SmolLM stored every fact, but robust access plateaued");
  setText(s, "capacity-control", "The final gate required eight-cell robustness across Forms A–D × direct/QA, globally and per relation.");
  setText(s, "m360-title", "Exact storage");
  setText(s, "m360-overlap", "100%");
  setText(s, "m360-label", "canonical acquisition");
  setText(s, "arrow", "≠");
  setText(s, "m17-title", "Best robust access");
  setText(s, "m17-overlap", "55.8%");
  setText(s, "m17-label", "frozen gate: ≥70%");
  setText(s, "setup-text", "Eight-cell robust: 39.6% control · 52.2% contrastive · 50.4% higher λ · 55.8% prompt consistency");
  setText(s, "capacity-meaning", "Contrastive and consistency objectives helped—but did not make SmolLM eligible for M2/M3.");
  setText(s, "source", "SmolLM frozen comparison and remediation results; reports 127–128");
  setPage(s, 5);
  setNotes(s, [
    "documentation/106_M1_CROSS_FAMILY_MODEL_SCREENING_RESULT.md",
    "documentation/127_QWEN_SCALE_REPLICATION_RESULT_AND_SMOLLM_LAMBDA025_STATUS.md",
    "documentation/128_SMOLLM_500_FACT_PROMPT_CONSISTENCY_REMEDIATION_PLAN.md",
  ]);
}

// 6 — Model screen
{
  const s = presentation.slides.items[5];
  setText(s, "kicker", "MODEL-FAMILY SCREEN");
  setText(s, "slide-title", "Only Qwen passed every factual robustness gate");
  setText(s, "metric-value-generic perplexity drift", "1.461×");
  setText(s, "metric-label-generic perplexity drift", "initial Qwen PPL ratio");
  setText(s, "metric-value-M1 continuations ended in EOS", "0 / 5");
  setText(s, "metric-label-M1 continuations ended in EOS", "families passed all gates");
  setText(s, "preserved", "Qwen alone achieved near-ceiling held-out robustness and relation binding.");
  setText(s, "interpretation", "Next move: preserve Qwen’s factual strength while repairing retention—not more model fishing.");
  setText(s, "source", "Frozen 500-fact cross-family screen; report 106");
  setPage(s, 6);
  const chart = s.charts.items[0];
  const series = chart.series.items[0];
  series.name = "Eight-cell robust accuracy (%)";
  series.categories = ["Qwen", "StableLM", "Llama", "Gemma", "SmolLM"];
  series.values = [99.6, 93.8, 81.4, 78.0, 39.6];
  chart.yAxis = { min: 0, max: 100, majorUnit: 20, numberFormatCode: "0", majorGridlines: { style: "solid", fill: "#D6DDE8", width: 1 } };
  chart.dataLabels = { showValue: true, position: "outEnd", textStyle: { fontSize: 12, fill: "#17243A" } };
  setNotes(s, ["documentation/106_M1_CROSS_FAMILY_MODEL_SCREENING_RESULT.md"]);
}

// 7 — Qwen 2,500 facts
{
  const s = presentation.slides.items[6];
  setText(s, "kicker", "QWEN AT 2,500 FACTS");
  setText(s, "slide-title", "Qwen passed the 2,500-fact M1 gate in both seeds");
  setText(s, "capacity-control", "The frozen rule selected the earliest checkpoint passing exact, hard, robust, binding, PPL and integrity gates.");
  setText(s, "m360-title", "Seed 42 · step 75");
  setText(s, "m360-overlap", "96.08%");
  setText(s, "m360-label", "robust · exact 99.96% · PPL ×1.082");
  setText(s, "arrow", "↔");
  setText(s, "m17-title", "Seed 43 · step 50");
  setText(s, "m17-overlap", "96.20%");
  setText(s, "m17-label", "robust · exact 99.68% · PPL ×1.032");
  setText(s, "setup-text", "500 subjects · 2,500 facts · 20,000 hard probes per seed · Forms A–D × direct/QA");
  setText(s, "capacity-meaning", "Qwen became the sole replicated intermediate-scale M1 candidate and both artifacts were frozen.");
  setText(s, "source", "Replicated Qwen scale result and artifact freeze; report 127");
  setPage(s, 7);
  setNotes(s, ["documentation/127_QWEN_SCALE_REPLICATION_RESULT_AND_SMOLLM_LAMBDA025_STATUS.md"]);
}

// 8 — Pre-M2 freeze
{
  const s = presentation.slides.items[7];
  setText(s, "kicker", "PRE-M2 READINESS");
  setText(s, "slide-title", "Pre-M2 measurements were frozen before training");
  setText(s, "direct-fact", "Three answer directions measure different mechanisms");
  setText(s, "train-label", "Directions");
  setText(s, "train-examples", "EN→EN: English retention\nTR→EN: cross-lingual factual access\nTR→TR: access plus Turkish lexicalization");
  setText(s, "heldout-label", "Surface and scoring controls");
  setText(s, "heldout-example", "Forms A–D · direct/QA · candidate ranking · robust intersection");
  setText(s, "ladder-title", "Frozen package");
  setText(s, "ladder-1", "60k");
  setText(s, "ladder-1r", "probes / M1 seed");
  setText(s, "ladder-2", "2,000");
  setText(s, "ladder-2r", "subject bootstraps");
  setText(s, "ladder-3", "EN + TR");
  setText(s, "ladder-3r", "generic PPL");
  setText(s, "recipe-title", "Pre-adaptation guardrails");
  setText(s, "recipe-body", "Reload both frozen M1 artifacts · audit Turkish contamination · freeze endpoint, aliases, estimand and gates");
  setText(s, "source", "Bilingual baseline and contract freeze; reports 132–135");
  setPage(s, 8);
  setNotes(s, [
    "documentation/132_PRE_M2_QWEN_READINESS_AND_BASELINE_PLAN.md",
    "documentation/134_QWEN_PRE_M2_GPU_BLOCKER_AND_OFFLINE_PREPARATION_STATUS.md",
    "documentation/135_QWEN_M2_M3_CONTRACT_AND_MATERIALIZATION_STATUS.md",
  ]);
}

// 9 — Matched interventions
{
  const s = presentation.slides.items[8];
  setText(s, "kicker", "M2/M3 INTERVENTION");
  setText(s, "slide-title", "M2 and M3 differed only in factual exposure");
  setText(s, "v1-title", "M2-clean");
  setText(s, "v1-result", "1,048,576 tokens · 128 updates");
  setText(s, "v1-weak", "Exposure rule");
  setText(s, "v1-lines", "Generic Turkish + neutral filler\nZero target synthetic facts");
  setText(s, "v1-diagnosis", "Tests what clean Turkish adaptation does to already acquired factual access.");
  setText(s, "v2-title", "M3-fact");
  setText(s, "v2-replace", "Same Turkish blocks and budget\nNeutral filler replaced by correct Branch B facts");
  setText(s, "v2-result", "1,048,576 tokens · 128 updates");
  setText(s, "v2-change", "4 cycles · 5,000 factual exposures");
  setText(s, "v2-limit", "Branch A receives zero factual exposure; M3 starts from M1, never from M2.");
  setText(s, "relations", "Primary estimand:  [(M3 − M2)Branch B  −  (M3 − M2)Branch A]  on TR→EN");
  setText(s, "source", "Frozen matched-input and causal contract; reports 133 and 135");
  setPage(s, 9);
  setNotes(s, [
    "documentation/133_QWEN_2500_FACT_M2_M3_EXECUTION_HANDOFF_PLAN.md",
    "documentation/135_QWEN_M2_M3_CONTRACT_AND_MATERIALIZATION_STATUS.md",
  ]);
}

// 10 — Execution ledger
{
  const s = presentation.slides.items[9];
  setText(s, "kicker", "EXECUTION AND INTEGRITY");
  setText(s, "slide-title", "All four runs used one precommitted endpoint");
  setText(s, "attempt-title-0", "Training");
  setText(s, "attempt-example-0", "Four sibling runs: M2-clean and M3-fact for seed 42 and seed 43; all start from their matching frozen M1.");
  setText(s, "attempt-result-0", "All four completed 128 updates · fixed checkpoint-128");
  setText(s, "attempt-title-1", "Endpoint evaluation");
  setText(s, "attempt-example-1", "24 slices per state × 2,500 probes; all required forms, scaffolds and directions.");
  setText(s, "attempt-result-1", "96 / 96 slices · 240,000 M2/M3 endpoint probes");
  setText(s, "attempt-title-2", "Independent verification");
  setText(s, "attempt-example-2", "Raw manifests, registry membership, hashes, bootstrap logic and gate were checked read-only.");
  setText(s, "attempt-result-2", "PASS WITH CONCERNS · no blocker or major issue");
  setText(s, "attempt-lesson-text", "No checkpoint, seed, threshold or primary metric was selected after seeing the result.");
  setText(s, "source", "Execution, independent review and retention freeze; reports 136, 140a and 143");
  setPage(s, 10);
  setNotes(s, [
    "documentation/136_QWEN_M2_M3_ENDPOINT_EVALUATION_GPU_ALLOCATION_STATUS.md",
    "documentation/140a_QWEN_M2_M3_INDEPENDENT_REVIEW_RESULT_EN.md",
    "documentation/143_QWEN_M2_M3_ARTIFACT_RETENTION_FREEZE_AND_STORAGE_AUDIT_EN.md",
  ]);
}

// 11 — M1 bilingual baseline
{
  const s = presentation.slides.items[10];
  setText(s, "kicker", "BEFORE TURKISH ADAPTATION");
  setText(s, "slide-title", "M1 already exposed substantial cross-lingual factual access");
  setText(s, "v1-title", "M1 seed 42 · step 75");
  setText(s, "v1-result", "EN→EN 99.29% · TR→EN 52.03%");
  setText(s, "v1-weak", "End-to-end Turkish");
  setText(s, "v1-lines", "TR→TR 29.05%\nEN PPL 15.909 · TR PPL 17.349");
  setText(s, "v1-diagnosis", "Cross-lingual access existed before any Turkish adaptation stage.");
  setText(s, "v2-title", "M1 seed 43 · step 50");
  setText(s, "v2-replace", "EN→EN 99.24%\nTR→EN 52.52%");
  setText(s, "v2-result", "TR→TR 30.12%");
  setText(s, "v2-change", "EN PPL 15.170 · TR PPL 15.741");
  setText(s, "v2-limit", "The two seeds provide nearly identical factual starting points for the causal family.");
  setText(s, "relations", "M2 therefore had both headroom to improve Turkish access—and existing access to preserve.");
  setText(s, "source", "Frozen bilingual/PPL M1 baselines; report 134");
  setPage(s, 11);
  setNotes(s, ["documentation/134_QWEN_PRE_M2_GPU_BLOCKER_AND_OFFLINE_PREPARATION_STATUS.md"]);
}

// 12 — Main endpoint chart
{
  const s = presentation.slides.items[11];
  setText(s, "kicker", "PRIMARY DIRECTION: TR→EN");
  setText(s, "slide-title", "Turkish adaptation reduced access; M3 recovered little");
  setText(s, "metric-value-generic perplexity drift", "−18.8 pp");
  setText(s, "metric-label-generic perplexity drift", "M1 → M2 in both seeds");
  setText(s, "metric-value-M1 continuations ended in EOS", "+1.9 pp");
  setText(s, "metric-label-M1 continuations ended in EOS", "M2 → M3 in both seeds");
  setText(s, "preserved", "The dominant effect is broad Turkish-prompt factual-access degradation in M2.");
  setText(s, "interpretation", "M3-fact is consistently higher than M2-clean, but remains far below the M1 baseline.");
  setText(s, "source", "Frozen state accuracy and paired contrasts; reports 136 and 142");
  setPage(s, 12);
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

// 13 — Interaction
{
  const s = presentation.slides.items[12];
  setText(s, "kicker", "FROZEN PRIMARY GATE");
  setText(s, "slide-title", "The primary causal interaction did not replicate");
  setText(s, "capacity-control", "Primary interaction = (M3 − M2)Branch B − (M3 − M2)Branch A on TR→EN; both seeds had to exclude zero.");
  setText(s, "m360-title", "Seed 42");
  setText(s, "m360-overlap", "+0.25 pp");
  setText(s, "m360-label", "95% CI −0.51 to +1.01 · FAIL");
  setText(s, "arrow", "≠");
  setText(s, "m17-title", "Seed 43");
  setText(s, "m17-overlap", "+1.35 pp");
  setText(s, "m17-label", "95% CI +0.51 to +2.18 · PASS");
  setText(s, "setup-text", "Operational validity passed · EN→EN retention guardrail passed · no post-hoc gate change");
  setText(s, "capacity-meaning", "Overall frozen decision: primary_success_criterion_not_met");
  setText(s, "source", "Frozen gate and independent raw-data reproduction; reports 136 and 140a");
  setPage(s, 13);
  setNotes(s, [
    "documentation/136_QWEN_M2_M3_ENDPOINT_EVALUATION_GPU_ALLOCATION_STATUS.md",
    "documentation/140a_QWEN_M2_M3_INDEPENDENT_REVIEW_RESULT_EN.md",
  ]);
}

// 14 — Interpretation
{
  const s = presentation.slides.items[13];
  setText(s, "kicker", "SCIENTIFIC INTERPRETATION");
  setText(s, "headline", "The causal family is complete—not the thesis question");
  setText(s, "close-label-0", "What we know");
  setText(s, "close-body-0", "English-acquired facts were already partly accessible from Turkish prompts; clean adaptation strongly reduced that access.");
  setText(s, "close-label-1", "What M3 adds");
  setText(s, "close-body-1", "Correct Turkish factual exposure produced a small, consistent descriptive recovery relative to M2-clean.");
  setText(s, "close-label-2", "What we cannot claim");
  setText(s, "close-body-2", "The Branch-B-specific factual-relearning advantage was not replicated under the precommitted two-seed confidence rule.");
  setText(s, "discussion-text", "This is a valid negative/inconclusive result—not a failed experiment and not evidence that all future transfer mechanisms are exhausted.");
  setPage(s, 14);
  setNotes(s, [
    "documentation/138_QWEN_M2_M3_COMPLETED_MILESTONE_AND_SCIENTIFIC_INTERPRETATION_EN.md",
    "documentation/140a_QWEN_M2_M3_INDEPENDENT_REVIEW_RESULT_EN.md",
    "documentation/142_QWEN_M2_M3_EXPLORATORY_MECHANISM_ANALYSIS_RESULT_EN.md",
  ]);
}

// 15 — Remaining work
{
  const s = presentation.slides.items[14];
  setText(s, "kicker", "WHAT REMAINS");
  setText(s, "slide-title", "This experiment is complete; substantial work remains");
  setText(s, "ranking-title", "Without new training");
  setText(s, "ranking-example", "Finalize figures, methods, limitations, seed heterogeneity and the interpretation of broad Turkish-access degradation.");
  setText(s, "ranking-result", "Turn the verified evidence chain into the thesis narrative and supervisor-ready decisions.");
  setText(s, "binding-title", "Possible amended experiments");
  setText(s, "binding-example", "M3-lexical, a revised Turkish adaptation intervention, additional replication, or 25,000-fact scale validation.");
  setText(s, "binding-result", "Each option needs a separate scientific rationale and frozen contract; none follows automatically from this gate.");
  setText(s, "strategy-shift", "Decision boundary");
  setText(s, "strategy-body", "Treat the completed 2,500-fact family as the main current result—then add only experiments that resolve a specific remaining mechanism.");
  setText(s, "source", "Current milestone, review, exploratory result and retention closure; reports 138, 140a, 142 and 143");
  setPage(s, 15);
  setNotes(s, [
    "documentation/138_QWEN_M2_M3_COMPLETED_MILESTONE_AND_SCIENTIFIC_INTERPRETATION_EN.md",
    "documentation/139_POST_M2_M3_INDEPENDENT_NEXT_ACTION_PLAN_EN.md",
    "documentation/140a_QWEN_M2_M3_INDEPENDENT_REVIEW_RESULT_EN.md",
    "documentation/142_QWEN_M2_M3_EXPLORATORY_MECHANISM_ANALYSIS_RESULT_EN.md",
    "documentation/143_QWEN_M2_M3_ARTIFACT_RETENTION_FREEZE_AND_STORAGE_AUDIT_EN.md",
  ]);
}

const pptx = await PresentationFile.exportPptx(presentation);
await pptx.save(OUTPUT);
console.log(OUTPUT);
