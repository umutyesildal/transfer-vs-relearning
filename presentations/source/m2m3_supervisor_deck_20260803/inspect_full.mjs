import fs from "node:fs/promises";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const source = "/Users/umutyesildal/Desktop/UniDE/Semester6/Thesis/implementation/outputs/max_m1_research_update.pptx";
const out = "/Users/umutyesildal/Desktop/UniDE/Semester6/Thesis/implementation/tmp/m2m3_supervisor_deck_20260803/full-inspect.ndjson";

const presentation = await PresentationFile.importPptx(await FileBlob.load(source));
const snapshot = await presentation.inspect({
  kind: "slide,textbox,shape,image,table,chart,notes,layout",
  include: "id,slide,name,title,text,textPreview,textChars,textLines,bbox,bboxUnit,isPlaceholder,placeholders",
  maxChars: 120000,
});
await fs.writeFile(out, snapshot.ndjson);
console.log(out);
