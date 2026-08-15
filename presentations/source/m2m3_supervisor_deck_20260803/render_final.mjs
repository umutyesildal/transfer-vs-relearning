import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const pptxPath = "/Users/umutyesildal/Desktop/UniDE/Semester6/Thesis/implementation/outputs/qwen_m2_m3_research_update_august_2026.pptx";
const outDir = "/Users/umutyesildal/Desktop/UniDE/Semester6/Thesis/implementation/tmp/m2m3_supervisor_deck_20260803/final-render";
const layoutDir = "/Users/umutyesildal/Desktop/UniDE/Semester6/Thesis/implementation/tmp/m2m3_supervisor_deck_20260803/final-layout";

async function saveBlob(filePath, blob) {
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

await fs.mkdir(outDir, { recursive: true });
await fs.mkdir(layoutDir, { recursive: true });
const presentation = await PresentationFile.importPptx(await FileBlob.load(pptxPath));

for (let i = 0; i < presentation.slides.items.length; i += 1) {
  const slide = presentation.slides.items[i];
  const stem = `slide-${String(i + 1).padStart(2, "0")}`;
  await saveBlob(path.join(outDir, `${stem}.png`), await presentation.export({ slide, format: "png", scale: 1.5 }));
  const layout = await slide.export({ format: "layout" });
  await fs.writeFile(path.join(layoutDir, `${stem}.layout.json`), await layout.text());
}

await saveBlob(
  "/Users/umutyesildal/Desktop/UniDE/Semester6/Thesis/implementation/tmp/m2m3_supervisor_deck_20260803/final-montage.webp",
  await presentation.export({ format: "webp", montage: true, scale: 1 }),
);

const inspect = await presentation.inspect({
  kind: "slide,textbox,shape,chart,notes,layout",
  include: "id,slide,name,title,textPreview,textChars,textLines,bbox,bboxUnit,isPlaceholder,placeholders",
  maxChars: 120000,
});
await fs.writeFile(
  "/Users/umutyesildal/Desktop/UniDE/Semester6/Thesis/implementation/tmp/m2m3_supervisor_deck_20260803/final-inspect.ndjson",
  inspect.ndjson,
);
console.log(`rendered=${presentation.slides.items.length}`);
