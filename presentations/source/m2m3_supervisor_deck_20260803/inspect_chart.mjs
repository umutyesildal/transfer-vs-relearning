import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const starter = "/Users/umutyesildal/Desktop/UniDE/Semester6/Thesis/implementation/tmp/m2m3_supervisor_deck_20260803/template-starter.pptx";
const presentation = await PresentationFile.importPptx(await FileBlob.load(starter));
const slide = presentation.slides.items[5];
const chart = slide.charts.items[0];
console.log(JSON.stringify({
  slideCount: presentation.slides.items.length,
  chartKeys: Object.keys(chart),
  seriesCount: chart.series.items.length,
  seriesKeys: Object.keys(chart.series.items[0]),
  seriesName: chart.series.items[0].name,
  seriesValues: chart.series.items[0].values,
  seriesCategories: chart.series.items[0].categories,
  xAxis: chart.xAxis,
  yAxis: chart.yAxis,
  chartProto: chart.toProto ? chart.toProto() : null,
}, null, 2));
