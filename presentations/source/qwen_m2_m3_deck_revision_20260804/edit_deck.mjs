import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const starterPath = "/Users/umutyesildal/Desktop/UniDE/Semester6/Thesis/implementation/.tmp/qwen_m2_m3_deck_revision_20260804/template-starter.pptx";
const finalPath = "/Users/umutyesildal/Desktop/UniDE/Semester6/Thesis/implementation/outputs/qwen_m2_m3_research_update_august_2026_revised.pptx";
const renderDir = "/Users/umutyesildal/Desktop/UniDE/Semester6/Thesis/implementation/.tmp/qwen_m2_m3_deck_revision_20260804/final-render";
const layoutDir = "/Users/umutyesildal/Desktop/UniDE/Semester6/Thesis/implementation/.tmp/qwen_m2_m3_deck_revision_20260804/final-layout";

async function writeBlob(filePath, blob) {
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

function shapeByName(slide, name) {
  const shape = slide.shapes.items.find((item) => item.name === name);
  if (!shape) throw new Error(`Missing shape '${name}' on slide ${slide.id}`);
  return shape;
}

function replaceText(slide, name, oldText, newText) {
  const shape = shapeByName(slide, name);
  shape.text.replace(oldText, newText);
}

function setNotes(slide, sources) {
  const block = [
    "[Sources]",
    ...sources.map((source) => `- ${source}`),
    "[/Sources]",
  ].join("\n");
  slide.speakerNotes.textFrame.setText(block);
  slide.speakerNotes.setVisible(true);
}

const presentation = await PresentationFile.importPptx(await FileBlob.load(starterPath));
if (presentation.slides.items.length !== 19) {
  throw new Error(`Expected 19 slides; found ${presentation.slides.items.length}`);
}

const s = presentation.slides.items;

replaceText(s[0], "title", "to cross-lingual adaptation", "to a diagnostic M2/M3 result");
replaceText(s[0], "subtitle", "What changed, what the first causal family shows, and what remains", "What the completed causal family establishes—and what still requires measurement");
replaceText(s[0], "scope", "Qwen M1 replication · M2/M3 endpoint evidence · 2,500 facts", "Qwen M1 replication · M2/M3 v1 evidence · staged next decision");

replaceText(s[1], "headline", "We moved from an apparent M1 solution to a completed causal test", "The first causal family is complete—and the next bottleneck is clear");
replaceText(s[1], "close-label-0", "Stronger measurement", "Validated foundation");
replaceText(s[1], "close-body-0", "Subject-held-out forms showed that SmolLM’s 500-fact success depended strongly on prompt exposure.", "Hard-form testing overturned the apparent SmolLM solution; Qwen then replicated at 2,500 facts.");
replaceText(s[1], "close-label-1", "Model decision", "Controlled execution");
replaceText(s[1], "close-body-1", "A frozen cross-family screen and retention replay selected Qwen, replicated at 2,500 facts.", "Two M2-clean/M3-fact sibling chains completed at one fixed endpoint and passed integrity review.");
replaceText(s[1], "close-label-2", "Causal execution", "Decision, not dead end");
replaceText(s[1], "close-body-2", "M2-clean and M3-fact completed in two seed chains at a fixed endpoint with 240,000 endpoint probes.", "M2 reduced Turkish-prompt access; M3 recovered little; a missing adaptation check now determines the redesign.");
replaceText(s[1], "discussion-text", "The result is valid but not conclusive: M3 partially recovers access, while the primary interaction replicates in only one seed.", "A valid negative/inconclusive v1 result now gives us a precise diagnostic path—not a finished thesis and not a failed project.");
replaceText(s[1], "page", "2", "2");

replaceText(s[2], "page", "3", "3");

replaceText(s[3], "kicker", "SCIENTIFIC INTERPRETATION", "WHY M2/M3 MATTERS");
replaceText(s[3], "headline", "The causal family is complete—not the thesis question", "Sibling arms separate transfer from factual re-exposure");
replaceText(s[3], "close-label-0", "What we know", "Transfer question");
replaceText(s[3], "close-body-0", "English-acquired facts were already partly accessible from Turkish prompts; clean adaptation strongly reduced that access.", "After clean Turkish adaptation, can the model access an English-learned fact without seeing the fact again?");
replaceText(s[3], "close-label-1", "What M3 adds", "Relearning question");
replaceText(s[3], "close-body-1", "Correct Turkish factual exposure produced a small, consistent descriptive recovery relative to M2-clean.", "When correct Turkish facts are repeated, do they add benefit beyond the matched clean-adaptation arm?");
replaceText(s[3], "close-label-2", "What we cannot claim", "Causal identification");
replaceText(s[3], "close-body-2", "The Branch-B-specific factual-relearning advantage was not replicated under the precommitted two-seed confidence rule.", "Sibling starts, equal budgets and the Branch A/B contrast isolate factual re-exposure from generic adaptation.");
replaceText(s[3], "discussion-text", "This is a valid negative/inconclusive result—not a failed experiment and not evidence that all future transfer mechanisms are exhausted.", "Without this matched design, any Turkish gain could be generic adaptation, factual repetition—or both.");
replaceText(s[3], "page", "14", "4");

replaceText(s[4], "page", "4", "5");
replaceText(s[5], "page", "5", "6");
replaceText(s[6], "slide-title", "Only Qwen passed every factual robustness gate", "Only Qwen could be repaired to pass every robustness gate");
replaceText(s[6], "preserved", "Qwen alone achieved near-ceiling held-out robustness and relation binding.", "After retention repair, Qwen achieved near-ceiling held-out robustness and relation binding.");
replaceText(s[6], "interpretation", "Next move: preserve Qwen’s factual strength while repairing retention—not more model fishing.", "Decision: carry Qwen forward after repair—and stop model fishing.");
replaceText(s[6], "page", "6", "7");
replaceText(s[7], "page", "7", "8");
replaceText(s[8], "page", "8", "9");
replaceText(s[9], "page", "9", "10");

replaceText(s[10], "kicker", "SCIENTIFIC INTERPRETATION", "EVALUATION LOGIC");
replaceText(s[10], "headline", "The causal family is complete—not the thesis question", "The mechanism requires three separate measurements");
replaceText(s[10], "close-label-0", "What we know", "Language adaptation");
replaceText(s[10], "close-body-0", "English-acquired facts were already partly accessible from Turkish prompts; clean adaptation strongly reduced that access.", "Did M2 improve general Turkish modeling? Held-out Turkish PPL or LM loss is the manipulation check.");
replaceText(s[10], "close-label-1", "What M3 adds", "Cross-lingual access");
replaceText(s[10], "close-body-1", "Correct Turkish factual exposure produced a small, consistent descriptive recovery relative to M2-clean.", "What changed from M1 to M2 on TR→EN while no target fact was repeated?");
replaceText(s[10], "close-label-2", "What we cannot claim", "Factual re-exposure");
replaceText(s[10], "close-body-2", "The Branch-B-specific factual-relearning advantage was not replicated under the precommitted two-seed confidence rule.", "Does Branch B gain more than Branch A in M3 relative to M2 under the fixed endpoint?");
replaceText(s[10], "discussion-text", "This is a valid negative/inconclusive result—not a failed experiment and not evidence that all future transfer mechanisms are exhausted.", "The factual suite was complete; the post-training language-adaptation check was not reported.");
replaceText(s[10], "page", "14", "11");

replaceText(s[11], "page", "10", "12");
replaceText(s[12], "page", "11", "13");
replaceText(s[13], "slide-title", "Turkish adaptation reduced access; M3 recovered little", "M2-clean reduced Turkish-prompt access; M3 recovered little");
replaceText(s[13], "preserved", "The dominant effect is broad Turkish-prompt factual-access degradation in M2.", "The dominant effect is broad Turkish-prompt factual-access degradation after M2-clean.");
replaceText(s[13], "page", "12", "14");

replaceText(s[14], "slide-title", "The primary causal interaction did not replicate", "The Branch-specific effect replicated in only one seed");
replaceText(s[14], "capacity-meaning", "Overall frozen decision: primary_success_criterion_not_met", "Overall frozen decision: primary criterion not met");
replaceText(s[14], "page", "13", "15");

replaceText(s[15], "kicker", "SCIENTIFIC INTERPRETATION", "WHAT FAILED—AND WHAT DID NOT");
replaceText(s[15], "headline", "The causal family is complete—not the thesis question", "Execution was valid; the primary replication failed");
replaceText(s[15], "close-label-0", "What we know", "Execution held");
replaceText(s[15], "close-body-0", "English-acquired facts were already partly accessible from Turkish prompts; clean adaptation strongly reduced that access.", "Matched budgets, sibling starts, 96/96 slices, fixed endpoint, integrity and retention gates all passed.");
replaceText(s[15], "close-label-1", "What M3 adds", "Primary evidence failed");
replaceText(s[15], "close-body-1", "Correct Turkish factual exposure produced a small, consistent descriptive recovery relative to M2-clean.", "The Branch-B interaction excluded zero in seed 43 but not seed 42; the two-seed rule was not met.");
replaceText(s[15], "close-label-2", "What we cannot claim", "Interpretation remains open");
replaceText(s[15], "close-body-2", "The Branch-B-specific factual-relearning advantage was not replicated under the precommitted two-seed confidence rule.", "We still cannot distinguish Turkish learning with interference from an insufficient M2 adaptation.");
replaceText(s[15], "discussion-text", "This is a valid negative/inconclusive result—not a failed experiment and not evidence that all future transfer mechanisms are exhausted.", "Therefore v1 is a valid negative/inconclusive family—not an infrastructure failure or a final thesis verdict.");
replaceText(s[15], "page", "14", "16");

replaceText(s[16], "kicker", "SCIENTIFIC INTERPRETATION", "CRITICAL MANIPULATION CHECK");
replaceText(s[16], "headline", "The causal family is complete—not the thesis question", "Did M2 learn Turkish? The answer changes the mechanism");
replaceText(s[16], "close-label-0", "What we know", "If TR PPL improves");
replaceText(s[16], "close-body-0", "English-acquired facts were already partly accessible from Turkish prompts; clean adaptation strongly reduced that access.", "Language adaptation worked; the factual decline becomes evidence of interference or access disruption.");
replaceText(s[16], "close-label-1", "What M3 adds", "If TR PPL is flat/worse");
replaceText(s[16], "close-body-1", "Correct Turkish factual exposure produced a small, consistent descriptive recovery relative to M2-clean.", "The M2 manipulation was insufficient; transfer was not cleanly tested and the recipe needs calibration.");
replaceText(s[16], "close-label-2", "What we cannot claim", "Corpus-dose caveat");
replaceText(s[16], "close-body-2", "The Branch-B-specific factual-relearning advantage was not replicated under the precommitted two-seed confidence rule.", "Training used a 1.05M-token stored-order prefix; document coverage and representativeness need audit.");
replaceText(s[16], "discussion-text", "This is a valid negative/inconclusive result—not a failed experiment and not evidence that all future transfer mechanisms are exhausted.", "Evaluate frozen PPL and checkpoint curves before designing any new training family.");
replaceText(s[16], "page", "14", "17");

replaceText(s[17], "kicker", "WHAT REMAINS", "IMMEDIATE NEXT ACTION");
replaceText(s[17], "slide-title", "This experiment is complete; substantial work remains", "Close the measurement gap before launching more training");
replaceText(s[17], "ranking-title", "Without new training", "Read-only diagnostic");
replaceText(s[17], "ranking-example", "Finalize figures, methods, limitations, seed heterogeneity and the interpretation of broad Turkish-access degradation.", "Evaluate M1/M2/M3 × seeds 42/43 on the same held-out Turkish and English PPL sets.");
replaceText(s[17], "ranking-result", "Turn the verified evidence chain into the thesis narrative and supervisor-ready decisions.", "Add checkpoint-32/64/96/128 curves and audit exact document/token coverage.");
replaceText(s[17], "binding-title", "Possible amended experiments", "Decision after evidence");
replaceText(s[17], "binding-example", "M3-lexical, a revised Turkish adaptation intervention, additional replication, or 25,000-fact scale validation.", "TR PPL improves → retention-preserving M2-v2.\nTR PPL is flat/worse → dose, LR and sampling calibration.");
replaceText(s[17], "binding-result", "Each option needs a separate scientific rationale and frozen contract; none follows automatically from this gate.", "Keep factual TR outcomes blind during recipe selection; use them only in the confirmatory family.");
replaceText(s[17], "strategy-shift", "Decision boundary", "Launch boundary");
replaceText(s[17], "strategy-body", "Treat the completed 2,500-fact family as the main current result—then add only experiments that resolve a specific remaining mechanism.", "No 25,000-fact scale-up and no new M2/M3 family until the diagnostic selects the scientific branch.");
replaceText(s[17], "source", "Current milestone, review, exploratory result and retention closure; reports 138, 140a, 142 and 143", "Proposed amendment from the frozen v1 contract and delayed secondary-outcome completion");
replaceText(s[17], "page", "15", "18");

replaceText(s[18], "kicker", "WHAT REMAINS", "SUPERVISOR DECISION");
replaceText(s[18], "slide-title", "This experiment is complete; substantial work remains", "The next step is staged—not a blind rerun");
replaceText(s[18], "ranking-title", "Without new training", "Current claim");
replaceText(s[18], "ranking-example", "Finalize figures, methods, limitations, seed heterogeneity and the interpretation of broad Turkish-access degradation.", "The 2,500-fact v1 family is valid and negative/inconclusive: M2 hurt access; M3 recovered only a little.");
replaceText(s[18], "ranking-result", "Turn the verified evidence chain into the thesis narrative and supervisor-ready decisions.", "Preserve it as the current result; do not rewrite its endpoint, seed rule or gate.");
replaceText(s[18], "binding-title", "Possible amended experiments", "Proposed amendment");
replaceText(s[18], "binding-example", "M3-lexical, a revised Turkish adaptation intervention, additional replication, or 25,000-fact scale validation.", "Authorize the PPL/checkpoint/corpus audit, then freeze either M2 calibration or a retention-preserving v2.");
replaceText(s[18], "binding-result", "Each option needs a separate scientific rationale and frozen contract; none follows automatically from this gate.", "Optional M3-lexical can separate factual binding from name and lexical familiarity.");
replaceText(s[18], "strategy-shift", "Decision boundary", "Discussion with Max");
replaceText(s[18], "strategy-body", "Treat the completed 2,500-fact family as the main current result—then add only experiments that resolve a specific remaining mechanism.", "Should the missing M2 manipulation check determine the next experiment—and should 25k wait?");
replaceText(s[18], "source", "Current milestone, review, exploratory result and retention closure; reports 138, 140a, 142 and 143", "Decision proposal; frozen v1 evidence remains in reports 136, 138, 140a, 142 and 143");
replaceText(s[18], "page", "15", "19");

const slideSources = [
  ["documentation/127 (replicated Qwen M1)", "documentation/138_QWEN_M2_M3_COMPLETED_MILESTONE_AND_SCIENTIFIC_INTERPRETATION_EN.md"],
  ["documentation/94–98 (measurement remediation)", "documentation/127 (Qwen M1)", "documentation/136_QWEN_M2_M3_ENDPOINT_EVALUATION_GPU_ALLOCATION_STATUS.md", "documentation/138_QWEN_M2_M3_COMPLETED_MILESTONE_AND_SCIENTIFIC_INTERPRETATION_EN.md"],
  ["documentation/Expose.pdf", "documentation/133–136 (frozen M2/M3 contract and result)"],
  ["documentation/133_QWEN_M2_M3 plan", "documentation/135_QWEN_M2_M3_CONTRACT_AND_MATERIALIZATION_STATUS.md", "documentation/136_QWEN_M2_M3_ENDPOINT_EVALUATION_GPU_ALLOCATION_STATUS.md"],
  ["documentation/94–98 (frozen hard evaluation and controls)"],
  ["documentation/127–128 (SmolLM frozen comparison and remediation)"],
  ["documentation/106 (cross-family screen)"],
  ["documentation/127 (replicated 2,500-fact Qwen M1 selection)"],
  ["documentation/132–135 (pre-M2 readiness and contract freeze)"],
  ["documentation/133 and documentation/135_QWEN_M2_M3_CONTRACT_AND_MATERIALIZATION_STATUS.md"],
  ["transfer-vs-relearning/configs/experiments/qwen_m2_m3_contract_v1.json", "documentation/136_QWEN_M2_M3_ENDPOINT_EVALUATION_GPU_ALLOCATION_STATUS.md"],
  ["documentation/136_QWEN_M2_M3_ENDPOINT_EVALUATION_GPU_ALLOCATION_STATUS.md", "documentation/140a_QWEN_M2_M3_INDEPENDENT_REVIEW_RESULT_EN.md", "documentation/143_QWEN_M2_M3_ARTIFACT_RETENTION_FREEZE_AND_STORAGE_AUDIT_EN.md"],
  ["documentation/134 (frozen bilingual and generic-PPL M1 baselines)"],
  ["documentation/136_QWEN_M2_M3_ENDPOINT_EVALUATION_GPU_ALLOCATION_STATUS.md", "documentation/142_QWEN_M2_M3_EXPLORATORY_MECHANISM_ANALYSIS_RESULT_EN.md"],
  ["documentation/136_QWEN_M2_M3_ENDPOINT_EVALUATION_GPU_ALLOCATION_STATUS.md", "documentation/140a_QWEN_M2_M3_INDEPENDENT_REVIEW_RESULT_EN.md"],
  ["documentation/136_QWEN_M2_M3_ENDPOINT_EVALUATION_GPU_ALLOCATION_STATUS.md", "documentation/138_QWEN_M2_M3_COMPLETED_MILESTONE_AND_SCIENTIFIC_INTERPRETATION_EN.md", "documentation/142_QWEN_M2_M3_EXPLORATORY_MECHANISM_ANALYSIS_RESULT_EN.md"],
  ["transfer-vs-relearning/configs/experiments/qwen_m2_m3_contract_v1.json", "documentation/135_QWEN_M2_M3_CONTRACT_AND_MATERIALIZATION_STATUS.md", "documentation/136_QWEN_M2_M3_ENDPOINT_EVALUATION_GPU_ALLOCATION_STATUS.md", "transfer-vs-relearning/src/transfer_vs_relearning/data/qwen_pre_m2.py"],
  ["transfer-vs-relearning/configs/experiments/qwen_m2_m3_contract_v1.json", "documentation/135_QWEN_M2_M3_CONTRACT_AND_MATERIALIZATION_STATUS.md", "documentation/136_QWEN_M2_M3_ENDPOINT_EVALUATION_GPU_ALLOCATION_STATUS.md"],
  ["documentation/138_QWEN_M2_M3_COMPLETED_MILESTONE_AND_SCIENTIFIC_INTERPRETATION_EN.md", "documentation/139_POST_M2_M3_INDEPENDENT_NEXT_ACTION_PLAN_EN.md", "documentation/142_QWEN_M2_M3_EXPLORATORY_MECHANISM_ANALYSIS_RESULT_EN.md", "documentation/143_QWEN_M2_M3_ARTIFACT_RETENTION_FREEZE_AND_STORAGE_AUDIT_EN.md"],
];

for (let index = 0; index < s.length; index += 1) {
  setNotes(s[index], slideSources[index]);
}

await fs.mkdir(renderDir, { recursive: true });
await fs.mkdir(layoutDir, { recursive: true });
for (let index = 0; index < s.length; index += 1) {
  const stem = `slide-${String(index + 1).padStart(2, "0")}`;
  await writeBlob(path.join(renderDir, `${stem}.png`), await presentation.export({ slide: s[index], format: "png", scale: 1 }));
  await fs.writeFile(path.join(layoutDir, `${stem}.layout.json`), await (await s[index].export({ format: "layout" })).text(), "utf8");
}
await writeBlob(
  "/Users/umutyesildal/Desktop/UniDE/Semester6/Thesis/implementation/.tmp/qwen_m2_m3_deck_revision_20260804/final-montage.webp",
  await presentation.export({ format: "webp", montage: true, scale: 1 }),
);

const pptx = await PresentationFile.exportPptx(presentation);
await pptx.save(finalPath);
console.log(finalPath);
