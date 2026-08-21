const DATA_URL = '../../artifacts/evaluations/m0_three_model_v1/dump/m0_metrics.json';
const MODEL_ORDER = ['olmo', 'qwen', 'smollm'];
const MODEL_LABELS = { olmo: 'OLMo', qwen: 'Qwen', smollm: 'SmolLM' };
const MODEL_CLASSES = { olmo: 'olmo', qwen: 'qwen', smollm: 'smollm' };
const LANE_ORDER = ['english_retention_wikitext', 'english_retention_pile_10k', 'english_grammar_blimp', 'english_capability', 'turkish_capability', 'turkish_perplexity', 'factual_access', 'generation_integrity'];
const LANE_LABELS = { english_retention_wikitext: 'WikiText', english_retention_pile_10k: 'Pile-10k', english_grammar_blimp: 'BLiMP', english_capability: 'English cap.', turkish_capability: 'Turkish cap.', turkish_perplexity: 'trwiki PPL', factual_access: 'Facts', generation_integrity: 'Integrity' };
const METRICS = {
  turkish_bpb: { label: 'Turkish trwiki BPB', help: 'Bits per byte · aynı byte-level corpus · düşük daha iyi', format: v => v.toFixed(6), scale: 'relative', direction: 'lower', caption: 'Qwen bu byte-level ölçümde en düşük loss değerini veriyor.' },
  turkish_ppl: { label: 'Turkish trwiki token PPL', help: 'Token perplexity · tokenizer-sensitive · düşük daha iyi', format: v => v.toFixed(4), scale: 'relative', direction: 'lower', caption: 'Token PPL companion evidence’tır; tokenizer farkı nedeniyle BPB’nin yerine geçmez.' },
  turblimp_acc_norm: { label: 'TurBLiMP acc_norm', help: '16,000 Türkçe sentaktik örnek · yüksek daha iyi', format: v => `${(v * 100).toFixed(2)}%`, scale: 'fraction', direction: 'higher', caption: 'Türkçe sentaktik tercih doğruluğu.' },
  blimp_accuracy: { label: 'English BLiMP accuracy', help: '67,000 İngilizce grammar örneği · yüksek daha iyi', format: v => `${(v * 100).toFixed(2)}%`, scale: 'fraction', direction: 'higher', caption: 'İngilizce grammar acceptability.' },
  hellaswag_acc_norm: { label: 'HellaSwag acc_norm', help: '10,042 commonsense örneği · yüksek daha iyi', format: v => `${(v * 100).toFixed(2)}%`, scale: 'fraction', direction: 'higher', caption: 'Commonsense completion capability.' },
  wikitext_bpb: { label: 'WikiText-2 BPB', help: '62 WikiText segmenti · düşük daha iyi', format: v => v.toFixed(6), scale: 'relative', direction: 'lower', caption: 'English retention için byte-level metric.' },
  pile_bpb: { label: 'Pile-10k BPB', help: '10,000 Pile örneği · düşük daha iyi', format: v => v.toFixed(6), scale: 'relative', direction: 'lower', caption: 'Qwen lane’i pending; eksik değer sıfır değildir.' },
  factual_top1_rate: { label: 'Factual access top-1 rate', help: '12,000 probe · yüksek daha iyi', format: v => `${(v * 100).toFixed(2)}%`, scale: 'fraction', direction: 'higher', caption: 'Doğru ilk cevap oranı; canonical normalized winner değildir.' },
  generation_distinct_2: { label: 'Generation distinct-2', help: '30 completion · çeşitlilik yüksek daha iyi', format: v => v.toFixed(3), scale: 'fraction', direction: 'higher', caption: 'Üretim çeşitliliği; generation integrity diagnostic.' },
  generation_repeated_3gram: { label: 'Repeated 3-gram fraction', help: '30 completion · tekrar düşük daha iyi', format: v => v.toFixed(3), scale: 'fraction', direction: 'lower', caption: 'Tekrarlı üretim oranı; düşük olması daha iyi.' }
};
let data;
let currentMetric = 'turkish_bpb';

const $ = id => document.getElementById(id);
const escapeHtml = value => String(value ?? '').replace(/[&<>'"]/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[char]));
const rowsFor = metric => data.metric_rows.filter(row => row.metric === metric);
const sourceByRef = () => Object.fromEntries(data.source_records.map(source => [source.source_ref, source]));
const formatNumber = value => typeof value === 'number' ? value.toLocaleString('en-US', { maximumFractionDigits: 6 }) : 'pending';

function initSummary() {
  $('valid-lanes').textContent = `${data.coverage.valid_lanes}/${data.coverage.total_lanes}`;
  $('model-count').textContent = Object.keys(data.models).length;
  $('pending-lanes').textContent = data.coverage.pending_lanes;
  $('source-count').textContent = data.source_records.length;
  $('generated-at').textContent = `snapshot: ${data.generated_at}`;
  $('provenance-note').textContent = `${data.contract.extraction_mode}; source roots HU scratch üzerinde read-only. ${data.contract.scientific_note}`;
}

function initMetricSelect() {
  const select = $('metric-select');
  Object.entries(METRICS).forEach(([key, metric]) => {
    const option = document.createElement('option'); option.value = key; option.textContent = metric.label; select.appendChild(option);
  });
  select.value = currentMetric;
  select.addEventListener('change', event => { currentMetric = event.target.value; renderChart(); });
}

function renderChart() {
  const meta = METRICS[currentMetric];
  const rows = rowsFor(currentMetric);
  const present = rows.filter(row => typeof row.value === 'number');
  const max = present.length ? Math.max(...present.map(row => row.value)) : 1;
  $('chart-title').textContent = meta.label;
  $('chart-direction').textContent = meta.direction === 'lower' ? '↓ düşük daha iyi' : '↑ yüksek daha iyi';
  $('metric-help').textContent = meta.help;
  $('chart-caption').textContent = meta.caption;
  $('chart').innerHTML = MODEL_ORDER.map(model => {
    const row = rows.find(item => item.model === model);
    const isPending = !row || typeof row.value !== 'number';
    const width = isPending ? 3 : meta.scale === 'fraction' ? row.value * 100 : (row.value / max) * 100;
    const bestValue = meta.direction === 'lower' ? Math.min(...present.map(item => item.value)) : Math.max(...present.map(item => item.value));
    const best = !isPending && row.value === bestValue;
    return `<div class="bar-row"><span class="model-name model-${model}">${MODEL_LABELS[model]}</span><div class="bar-track"><div class="bar-fill ${MODEL_CLASSES[model]}${isPending ? ' pending' : ''}" style="width:${Math.max(width, 3)}%"></div></div><span class="bar-value ${best ? 'best' : ''} ${isPending ? 'pending-text' : ''}">${isPending ? 'pending' : meta.format(row.value)}</span></div>`;
  }).join('');
  $('chart').setAttribute('aria-label', `${meta.label}: ${MODEL_ORDER.map(model => { const row = rows.find(item => item.model === model); return `${MODEL_LABELS[model]} ${row?.value == null ? 'pending' : meta.format(row.value)}`; }).join(', ')}`);
}

function renderLaneMatrix() {
  const lookup = new Map(data.lane_status.map(row => [`${row.model}/${row.lane}`, row]));
  $('lane-matrix').innerHTML = `<div></div>${LANE_ORDER.map(lane => `<div class="lane-head" title="${LANE_LABELS[lane]}">${LANE_LABELS[lane]}</div>`).join('')}${MODEL_ORDER.map(model => `<div class="lane-model model-${model}">${MODEL_LABELS[model]}</div>${LANE_ORDER.map(lane => { const row = lookup.get(`${model}/${lane}`); const pending = row?.status !== 'complete'; return `<div class="lane-cell${pending ? ' pending' : ''}" title="${MODEL_LABELS[model]} · ${LANE_LABELS[lane]} · ${pending ? 'pending' : 'complete'}">${pending ? '—' : '✓'}</div>`; }).join('')}`).join('')}`;
}

function displayRow(row) {
  if (row.value == null) return '<span class="pending-text">pending</span>';
  if (row.unit === 'fraction') return `${(row.value * 100).toFixed(2)}%`;
  if (row.unit === 'count') return Math.round(row.value).toLocaleString('en-US');
  return formatNumber(row.value);
}

function renderMetricTable() {
  const filter = $('metric-filter').value.trim().toLowerCase();
  const metricKeys = [...new Set(data.metric_rows.map(row => row.metric))].filter(key => !filter || key.includes(filter));
  const byMetric = Object.fromEntries(data.metric_rows.map(row => [`${row.metric}/${row.model}`, row]));
  $('metric-table').innerHTML = metricKeys.map(metric => {
    const sample = data.metric_rows.find(row => row.metric === metric);
    return `<tr><td><code>${escapeHtml(metric)}</code></td><td>${escapeHtml(sample.family)}</td>${MODEL_ORDER.map(model => { const row = byMetric[`${metric}/${model}`]; return `<td class="model-${model}">${row ? displayRow(row) : '—'}</td>`; }).join('')}<td>${sample.direction === 'lower' ? '↓ lower' : '↑ higher'}</td></tr>`;
  }).join('');
}

function renderSources() {
  $('sources').innerHTML = data.source_records.map(source => `<div class="source-row"><strong>${escapeHtml(source.source_ref)}</strong><span class="muted"> · ${escapeHtml(source.model)} · ${escapeHtml(source.lane)} · ${source.bytes.toLocaleString('en-US')} bytes</span><code>${escapeHtml(source.path)}</code><code>sha256: ${escapeHtml(source.sha256)}</code></div>`).join('');
}

async function main() {
  try {
    const response = await fetch(DATA_URL, { cache: 'no-store' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    data = await response.json();
    initSummary(); initMetricSelect(); renderChart(); renderLaneMatrix(); renderMetricTable(); renderSources();
    $('metric-filter').addEventListener('input', renderMetricTable);
  } catch (error) {
    document.querySelector('.shell').innerHTML = `<section class="panel"><h1>Dashboard yüklenemedi</h1><p>Canonical dump okunamadı: <code>${escapeHtml(error.message)}</code></p><p>Repo root’tan <code>python3 tools/m0-dashboard/serve.py</code> ile aç.</p></section>`;
  }
}
main();
