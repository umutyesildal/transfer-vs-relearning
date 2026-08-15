import fs from "node:fs";
import path from "node:path";

const dir = path.resolve("final-layout");
const files = fs.readdirSync(dir).filter((name) => name.endsWith(".layout.json")).sort();
const issues = [];

for (const file of files) {
  const doc = JSON.parse(fs.readFileSync(path.join(dir, file), "utf8"));
  const [frameX, frameY, frameW, frameH] = [
    doc.slide.frame.left,
    doc.slide.frame.top,
    doc.slide.frame.width,
    doc.slide.frame.height,
  ];
  for (const element of doc.elements ?? []) {
    if (!Array.isArray(element.bbox) || element.bbox.length !== 4) continue;
    const [x, y, w, h] = element.bbox;
    if (x < frameX - 0.5 || y < frameY - 0.5 || x + w > frameX + frameW + 0.5 || y + h > frameY + frameH + 0.5) {
      issues.push({ file, name: element.name, bbox: element.bbox, frame: [frameX, frameY, frameW, frameH] });
    }
  }
}

const inspectLines = fs.readFileSync("final-inspect.ndjson", "utf8").trim().split("\n").map(JSON.parse);
const notes = inspectLines.filter((row) => row.kind === "notes" && row.text?.startsWith("[Sources]"));
const titles = inspectLines.filter((row) => ["slide-title", "headline"].includes(row.name));
const titleWraps = titles.filter((row) => row.textLines !== 1);

console.log(JSON.stringify({
  slidesChecked: files.length,
  outOfBounds: issues,
  sourceNotes: notes.length,
  titleCount: titles.length,
  multiLineTitles: titleWraps,
}, null, 2));

if (issues.length || notes.length !== files.length || titleWraps.length) process.exitCode = 1;
