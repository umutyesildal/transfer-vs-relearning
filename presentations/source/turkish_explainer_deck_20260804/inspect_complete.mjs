import fs from "node:fs/promises";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const source = "/Users/umutyesildal/Desktop/UniDE/Semester6/Thesis/implementation/outputs/qwen_m2_m3_research_update_august_2026.pptx";
const output = "/Users/umutyesildal/Desktop/UniDE/Semester6/Thesis/implementation/tmp/turkish_explainer_deck_20260804/template-inspect-complete.ndjson";
const presentation = await PresentationFile.importPptx(await FileBlob.load(source));
const snapshot = await presentation.inspect({
  kind: "slide,textbox,shape,image,table,chart,notes,layout",
  maxChars: 250000,
});
await fs.writeFile(output, snapshot.ndjson, "utf8");
console.log(output);
