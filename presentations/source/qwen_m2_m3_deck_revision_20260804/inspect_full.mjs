import fs from "node:fs/promises";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const source = "/Users/umutyesildal/Desktop/UniDE/Semester6/Thesis/implementation/outputs/qwen_m2_m3_research_update_august_2026.pptx";
const output = "/Users/umutyesildal/Desktop/UniDE/Semester6/Thesis/implementation/.tmp/qwen_m2_m3_deck_revision_20260804/template-inspect/template-inspect-full.ndjson";

const presentation = await PresentationFile.importPptx(await FileBlob.load(source));
const snapshot = await presentation.inspect({
  kind: "slide,textbox,shape,image,table,chart",
  include: "id,slide,name,title,text,textPreview,textChars,textLines,bbox,bboxUnit,isPlaceholder",
  maxChars: 250000,
});
await fs.writeFile(output, snapshot.ndjson, "utf8");
console.log(output);
