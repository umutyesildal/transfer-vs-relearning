const DATA_URL = '../../artifacts/evaluations/m0_three_model_v1/dump/m0_metrics.json';
const MODEL_ORDER = ['olmo', 'qwen', 'smollm'];
const MODEL_LABELS = { olmo: 'OLMo', qwen: 'Qwen', smollm: 'SmolLM' };
const MODEL_CLASSES = { olmo: 'olmo', qwen: 'qwen', smollm: 'smollm' };
const LANE_ORDER = ['english_retention_wikitext', 'english_retention_pile_10k', 'english_grammar_blimp', 'english_capability', 'turkish_capability', 'turkish_perplexity', 'factual_access', 'generation_integrity'];
const LANE_LABELS = {
  english_retention_wikitext: { tr: 'WikiText', en: 'WikiText' },
  english_retention_pile_10k: { tr: 'Pile-10k', en: 'Pile-10k' },
  english_grammar_blimp: { tr: 'BLiMP', en: 'BLiMP' },
  english_capability: { tr: 'English cap.', en: 'English cap.' },
  turkish_capability: { tr: 'Turkish cap.', en: 'Turkish cap.' },
  turkish_perplexity: { tr: 'trwiki PPL', en: 'trwiki PPL' },
  factual_access: { tr: 'Facts', en: 'Facts' },
  generation_integrity: { tr: 'Integrity', en: 'Integrity' }
};
const FAMILY_LABELS = {
  english_retention: { tr: 'English retention', en: 'English retention' },
  english_capability: { tr: 'English capability', en: 'English capability' },
  turkish_capability: { tr: 'Turkish capability', en: 'Turkish capability' },
  turkish_perplexity: { tr: 'Turkish perplexity', en: 'Turkish perplexity' },
  factual_access: { tr: 'Factual access', en: 'Factual access' },
  generation_integrity: { tr: 'Generation integrity', en: 'Generation integrity' }
};
const STATE_COPY = {
  M0: {
    tr: { title: 'M0 — frozen pretrained base', description: 'Mevcut snapshot 3 modelin frozen base-model eval sonuçlarını gösterir. 24 lane’in 23’ü geçerli; Qwen Pile-10k beklemede.' },
    en: { title: 'M0 — frozen pretrained base', description: 'This snapshot contains frozen base-model evaluation results for three models. 23 of 24 lanes are valid; Qwen Pile-10k is pending.' }
  },
  M1: {
    tr: { title: 'M1 — English factual adaptation', description: 'M1 için bu dump içinde henüz training/evaluation result snapshot’ı yok. Sayı uydurulmuyor; state yalnızca UI’da hazırlanmış durumda.' },
    en: { title: 'M1 — English factual adaptation', description: 'No M1 training/evaluation result snapshot is present in this dump. The state is prepared in the UI without inventing numbers.' }
  },
  'M2-A': {
    tr: { title: 'M2-A — fact-free Turkish adaptation', description: 'M2-A için bu dump içinde henüz metric snapshot’ı yok. Bu state, M1 parent’tan gelen matched-budget Turkish arm olarak ayrılmıştır.' },
    en: { title: 'M2-A — fact-free Turkish adaptation', description: 'No M2-A metric snapshot is present in this dump. This state is reserved for the matched-budget fact-free Turkish arm from M1.' }
  },
  'M2-B': {
    tr: { title: 'M2-B — controlled factual re-exposure', description: 'M2-B için bu dump içinde henüz metric snapshot’ı yok. Bu state, M2-A ile matched-budget controlled re-exposure arm olarak ayrılmıştır.' },
    en: { title: 'M2-B — controlled factual re-exposure', description: 'No M2-B metric snapshot is present in this dump. This state is reserved for the matched-budget controlled re-exposure arm.' }
  }
};
const I18N = {
  tr: {
    hero: { eyebrow: 'TRANSFER VS. RELEARNING · EVALUATION', title: 'Evaluation Explorer', lede: 'M0, M1, M2-A ve M2-B sonuçlarını aynı ölçüm sözlüğüyle incele.', download: 'JSON dump’ı indir' },
    state: { label: 'State' }, nav: { home: 'Ana sayfa', metrics: 'Metrics', detail: 'Detail' },
    home: { eyebrow: 'OVERVIEW', highlights: 'Snapshot highlights', noSnapshot: 'Bu state için henüz Git’e alınmış metric snapshot’ı yok.', noSnapshotNote: 'Veri geldiğinde aynı metric sözlüğü otomatik olarak bu ekrana bağlanacak.', best: 'En güçlü mevcut gözlem', context: 'Aynı metric içinde model karşılaştırması', status: 'State durumu' },
    summary: { valid: 'Geçerli lane', models: 'Modeller', modelsNote: 'aynı evaluation paneli', pending: 'Bekleyen', pendingNote: 'eksik sonuç sıfır değildir', sources: 'Kaynak artifact', sourcesNote: 'path + SHA-256 bağlı' },
    metrics: { eyebrow: 'METRIC EXPLORER', title: 'Bir metric’i derinlemesine incele', selectLabel: 'Metric seç' },
    selected: { eyebrow: 'SELECTED METRIC', measureLabel: 'Ne ölçüyor?', readLabel: 'Nasıl okunmalı?', caveatLabel: 'Sınır / caveat' },
    detail: { eyebrow: 'DETAIL', metricsTitle: 'Tüm metric satırları', filter: 'metric filtrele', noSnapshot: 'Bu state için detay tablosu oluşturulacak bir metric snapshot’ı yok.' },
    table: { metric: 'Metric', family: 'Family', direction: 'Yön' },
    coverage: { eyebrow: 'COVERAGE', title: 'Lane durumu', legend: 'complete / pending' },
    guide: { eyebrow: 'READING GUIDE', title: 'Sonuçları nasıl yorumlamalı?', accuracy: '<strong>Accuracy</strong> yüksekse daha iyi; <strong>BPB/PPL</strong> ve repetition düşükse daha iyi.', bpb: 'BPB, tokenizer’lar arası ana retention karşılaştırmasıdır. Token PPL companion evidence’tır.', tasks: 'Farklı task’ler tek bir yapay overall score’a zorlanmaz.', missing: 'Pending sonuçlar boş bırakılır; eksik metric sıfır değildir.' },
    provenance: { eyebrow: 'PROVENANCE', title: 'Kaynak ve güven sınırı', show: 'Kaynak artifact hash’lerini göster', noSnapshot: 'Bu state için provenance kaydı yok.' },
    footer: { canonical: 'Canonical data', note: 'read-only derived dump; raw weights/logs Git’te yok.' },
    directions: { lower: '↓ düşük daha iyi', higher: '↑ yüksek daha iyi' },
    status: { observed: 'observed snapshot', pending: 'pending', noSnapshot: 'no result snapshot' }
  },
  en: {
    hero: { eyebrow: 'TRANSFER VS. RELEARNING · EVALUATION', title: 'Evaluation Explorer', lede: 'Explore M0, M1, M2-A, and M2-B through one stable metric vocabulary.', download: 'Download JSON dump' },
    state: { label: 'State' }, nav: { home: 'Home', metrics: 'Metrics', detail: 'Detail' },
    home: { eyebrow: 'OVERVIEW', highlights: 'Snapshot highlights', noSnapshot: 'There is no Git-retained metric snapshot for this state yet.', noSnapshotNote: 'When data arrives, it will use the same metric vocabulary automatically.', best: 'Strongest available observation', context: 'Model comparison within one metric', status: 'State status' },
    summary: { valid: 'Valid lanes', models: 'Models', modelsNote: 'same evaluation panel', pending: 'Pending', pendingNote: 'missing is not zero', sources: 'Source artifacts', sourcesNote: 'path + SHA-256 attached' },
    metrics: { eyebrow: 'METRIC EXPLORER', title: 'Inspect one metric in depth', selectLabel: 'Choose metric' },
    selected: { eyebrow: 'SELECTED METRIC', measureLabel: 'What does it measure?', readLabel: 'How should I read it?', caveatLabel: 'Boundary / caveat' },
    detail: { eyebrow: 'DETAIL', metricsTitle: 'All metric rows', filter: 'filter metric', noSnapshot: 'There is no metric snapshot for this state to populate the detail table.' },
    table: { metric: 'Metric', family: 'Family', direction: 'Direction' },
    coverage: { eyebrow: 'COVERAGE', title: 'Lane status', legend: 'complete / pending' },
    guide: { eyebrow: 'READING GUIDE', title: 'How should I interpret results?', accuracy: '<strong>Accuracy</strong> is better when higher; <strong>BPB/PPL</strong> and repetition are better when lower.', bpb: 'BPB is the primary cross-tokenizer retention comparison. Token PPL is companion evidence.', tasks: 'Different tasks are not forced into one artificial overall score.', missing: 'Pending results stay blank; a missing metric is not zero.' },
    provenance: { eyebrow: 'PROVENANCE', title: 'Source and trust boundary', show: 'Show source artifact hashes', noSnapshot: 'No provenance record exists for this state.' },
    footer: { canonical: 'Canonical data', note: 'read-only derived dump; raw weights/logs are not in Git.' },
    directions: { lower: '↓ lower is better', higher: '↑ higher is better' },
    status: { observed: 'observed snapshot', pending: 'pending', noSnapshot: 'no result snapshot' }
  }
};
const METRICS = {
  turkish_bpb: { label: { tr: 'Turkish trwiki BPB', en: 'Turkish trwiki BPB' }, help: { tr: 'Bits per byte · aynı byte-level corpus · düşük daha iyi', en: 'Bits per byte · same byte-level corpus · lower is better' }, format: v => v.toFixed(6), scale: 'relative', direction: 'lower', measure: { tr: 'Aynı UTF-8 byte akışı üzerindeki ortalama negatif log-likelihood’i ölçer. Tokenizer vocabulary’sinden daha az etkilenir.', en: 'Measures average negative log-likelihood over the same UTF-8 byte stream and is less dependent on tokenizer vocabulary.' }, read: { tr: 'Aynı trwiki corpus ve aynı byte accounting ile düşük değer daha iyi language fit demektir.', en: 'With the same trwiki corpus and byte accounting, a lower value means better language fit.' }, caveat: { tr: 'Bu tek başına overall model skoru değildir; Turkish capability ve factual access ile birlikte okunur.', en: 'This is not an overall model score; read it alongside Turkish capability and factual access.' }, caption: { tr: 'Qwen bu byte-level ölçümde en düşük loss değerini veriyor.', en: 'Qwen has the lowest loss on this byte-level measurement.' } },
  turkish_ppl: { label: { tr: 'Turkish trwiki token PPL', en: 'Turkish trwiki token PPL' }, help: { tr: 'Token perplexity · tokenizer-sensitive · düşük daha iyi', en: 'Token perplexity · tokenizer-sensitive · lower is better' }, format: v => v.toFixed(4), scale: 'relative', direction: 'lower', measure: { tr: 'Modelin token dizisini ne kadar şaşırtığını ölçer; tokenization doğrudan sonucu etkiler.', en: 'Measures how surprised the model is by the token sequence; tokenization directly affects the result.' }, read: { tr: 'Aynı tokenizer ailesinde düşük daha iyi okunur. Farklı tokenizer’larda BPB ana kıyas olmalıdır.', en: 'Lower is better within the same tokenizer family. BPB should lead comparisons across tokenizers.' }, caveat: { tr: 'SmolLM/Qwen/OLMo token sayıları farklı olduğu için token PPL’i tek başına ranking yapmaz.', en: 'Because token counts differ across SmolLM, Qwen, and OLMo, token PPL alone does not rank them.' }, caption: { tr: 'Token PPL companion evidence’tır; tokenizer farkı nedeniyle BPB’nin yerine geçmez.', en: 'Token PPL is companion evidence; tokenizer differences keep it secondary to BPB.' } },
  turblimp_acc_norm: { label: { tr: 'TurBLiMP acc_norm', en: 'TurBLiMP acc_norm' }, help: { tr: '16.000 Türkçe sentaktik örnek · yüksek daha iyi', en: '16,000 Turkish syntax examples · higher is better' }, format: v => `${(v * 100).toFixed(2)}%`, scale: 'fraction', direction: 'higher', measure: { tr: 'Türkçe minimal pair örneklerinde modelin doğru seçimi yapma oranıdır.', en: 'Measures the rate at which the model selects the correct option in Turkish minimal pairs.' }, read: { tr: 'Yüksek değer, Türkçe grammar preference sinyalinin daha güçlü olduğunu gösterir.', en: 'A higher value indicates a stronger Turkish grammar preference signal.' }, caveat: { tr: 'Bu sentaktik capability’dir; factual access veya retention yerine geçmez.', en: 'This is syntactic capability; it is not factual access or retention.' }, caption: { tr: 'Türkçe sentaktik tercih doğruluğu.', en: 'Turkish syntactic preference accuracy.' } },
  blimp_accuracy: { label: { tr: 'English BLiMP accuracy', en: 'English BLiMP accuracy' }, help: { tr: '67.000 İngilizce grammar örneği · yüksek daha iyi', en: '67,000 English grammar examples · higher is better' }, format: v => `${(v * 100).toFixed(2)}%`, scale: 'fraction', direction: 'higher', measure: { tr: 'İngilizce grammar minimal pair örneklerindeki genel doğruluk oranıdır.', en: 'Measures overall accuracy on English grammar minimal pairs.' }, read: { tr: 'Aynı 67.000 örnek üzerinde yüksek değer daha iyi grammar acceptability demektir.', en: 'On the same 67,000 examples, a higher value means better grammar acceptability.' }, caveat: { tr: 'Task-specific bir capability metriğidir; HellaSwag veya Turkish task’leriyle doğrudan karıştırılmaz.', en: 'It is task-specific capability; do not compare it directly with HellaSwag or Turkish tasks.' }, caption: { tr: 'İngilizce grammar acceptability.', en: 'English grammar acceptability.' } },
  hellaswag_acc_norm: { label: { tr: 'HellaSwag acc_norm', en: 'HellaSwag acc_norm' }, help: { tr: '10.042 commonsense örneği · yüksek daha iyi', en: '10,042 commonsense examples · higher is better' }, format: v => `${(v * 100).toFixed(2)}%`, scale: 'fraction', direction: 'higher', measure: { tr: 'Commonsense completion seçeneklerinde normalized accuracy’yi ölçer.', en: 'Measures normalized accuracy on commonsense completion choices.' }, read: { tr: 'Yüksek değer, genel English commonsense completion başarısının daha iyi olduğunu gösterir.', en: 'A higher value indicates stronger English commonsense completion.' }, caveat: { tr: 'Factual access veya Türkçe adaptation etkisini doğrudan ölçmez.', en: 'It does not directly measure factual access or Turkish adaptation.' }, caption: { tr: 'Commonsense completion capability.', en: 'Commonsense completion capability.' } },
  wikitext_bpb: { label: { tr: 'WikiText-2 BPB', en: 'WikiText-2 BPB' }, help: { tr: '62 WikiText segmenti · düşük daha iyi', en: '62 WikiText segments · lower is better' }, format: v => v.toFixed(6), scale: 'relative', direction: 'lower', measure: { tr: 'İngilizce WikiText üzerinde byte-level retention loss’unu ölçer.', en: 'Measures byte-level retention loss on English WikiText.' }, read: { tr: 'Düşük BPB, pretrained English distribution üzerinde daha iyi likelihood demektir.', en: 'Lower BPB means better likelihood on the pretrained English distribution.' }, caveat: { tr: 'Retention ölçümüdür; factual knowledge veya Turkish capability değildir.', en: 'This is retention; it is not factual knowledge or Turkish capability.' }, caption: { tr: 'English retention için byte-level metric.', en: 'Byte-level metric for English retention.' } },
  pile_bpb: { label: { tr: 'Pile-10k BPB', en: 'Pile-10k BPB' }, help: { tr: '10.000 Pile örneği · düşük daha iyi', en: '10,000 Pile examples · lower is better' }, format: v => v.toFixed(6), scale: 'relative', direction: 'lower', measure: { tr: 'Pile-10k corpus üzerinde byte-level retention loss’unu ölçer.', en: 'Measures byte-level retention loss on the Pile-10k corpus.' }, read: { tr: 'OLMo ve SmolLM için mevcut; Qwen lane’i bitmeden üçlü yorum tamamlanmaz.', en: 'Available for OLMo and SmolLM; the three-model reading is incomplete until Qwen finishes.' }, caveat: { tr: 'Qwen sonucu pending; eksik değer sıfır değildir.', en: 'Qwen is pending; a missing value is not zero.' }, caption: { tr: 'Qwen lane’i pending; eksik değer sıfır değildir.', en: 'Qwen is pending; the missing value is not zero.' } },
  factual_top1_rate: { label: { tr: 'Factual access top-1 rate', en: 'Factual access top-1 rate' }, help: { tr: '12.000 factual probe · yüksek daha iyi', en: '12,000 factual probes · higher is better' }, format: v => `${(v * 100).toFixed(2)}%`, scale: 'fraction', direction: 'higher', measure: { tr: 'Modelin factual probe’a doğru ilk cevabı verme oranıdır.', en: 'Measures the rate of correct first answers on factual probes.' }, read: { tr: 'Yüksek değer, probe formatında daha fazla doğru ilk cevap demektir.', en: 'A higher value means more correct first answers in the probe format.' }, caveat: { tr: 'Prompt-form failures ve robust intersection sonuçlarıyla beraber okunmalıdır.', en: 'Read together with prompt-form failures and robust intersection results.' }, caption: { tr: 'Doğru ilk cevap oranı; canonical normalized winner değildir.', en: 'Correct first-answer rate; not a canonical normalized winner.' } },
  generation_distinct_2: { label: { tr: 'Generation distinct-2', en: 'Generation distinct-2' }, help: { tr: '30 completion · çeşitlilik yüksek daha iyi', en: '30 completions · higher diversity is better' }, format: v => v.toFixed(3), scale: 'fraction', direction: 'higher', measure: { tr: 'Üretimlerdeki distinct bigram oranını ölçer.', en: 'Measures the fraction of distinct bigrams in generated completions.' }, read: { tr: 'Yüksek değer daha çeşitli; fakat tek başına factual correctness anlamına gelmez.', en: 'A higher value means more variety, but not factual correctness by itself.' }, caveat: { tr: 'Generation integrity diagnostic’idir; ana scientific winner metriği değildir.', en: 'It is a generation-integrity diagnostic, not the primary scientific winner metric.' }, caption: { tr: 'Üretim çeşitliliği; generation integrity diagnostic.', en: 'Generation diversity; generation-integrity diagnostic.' } },
  generation_repeated_3gram: { label: { tr: 'Repeated 3-gram fraction', en: 'Repeated 3-gram fraction' }, help: { tr: '30 completion · tekrar düşük daha iyi', en: '30 completions · lower repetition is better' }, format: v => v.toFixed(3), scale: 'fraction', direction: 'lower', measure: { tr: 'Üretimlerde tekrar eden 3-gramların oranını ölçer.', en: 'Measures the fraction of repeated 3-grams in generated completions.' }, read: { tr: 'Düşük değer degeneration/repetition riskinin daha düşük olduğunu gösterir.', en: 'A lower value indicates less degeneration or repetition risk.' }, caveat: { tr: 'Kısa bir 30 completion panelidir; tek başına model kalitesi değildir.', en: 'This is a small 30-completion panel; it is not model quality by itself.' }, caption: { tr: 'Tekrarlı üretim oranı; düşük olması daha iyi.', en: 'Repeated-generation fraction; lower is better.' } }
};
const HIGHLIGHTS = ['turkish_bpb', 'turblimp_acc_norm', 'hellaswag_acc_norm'];
let data;
let currentMetric = 'turkish_bpb';
let currentState = 'M0';
let currentPage = 'home';
let language = 'tr';

const $ = id => document.getElementById(id);
const t = key => key.split('.').reduce((value, part) => value?.[part], I18N[language]) ?? key;
const tx = value => typeof value === 'string' ? value : value?.[language] ?? '';
const escapeHtml = value => String(value ?? '').replace(/[&<>'"]/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[char]));
const rowsFor = metric => data.metric_rows.filter(row => row.metric === metric);
const hasCurrentData = () => currentState === 'M0' && Boolean(data.dashboard_states.find(item => item.id === currentState)?.available);
const formatNumber = value => typeof value === 'number' ? value.toLocaleString('en-US', { maximumFractionDigits: 6 }) : 'pending';
const stateCopy = () => STATE_COPY[currentState][language];

function applyI18n() {
  document.documentElement.lang = language;
  document.title = language === 'tr' ? 'M0–M2 Evaluation Explorer' : 'M0–M2 Evaluation Explorer';
  document.querySelectorAll('[data-i18n]').forEach(element => { element.innerHTML = t(element.dataset.i18n); });
  document.querySelectorAll('[data-i18n-placeholder]').forEach(element => { element.placeholder = t(element.dataset.i18nPlaceholder); });
  $('language-toggle').textContent = language === 'tr' ? 'EN' : 'TR';
  $('language-toggle').setAttribute('aria-pressed', language === 'en' ? 'true' : 'false');
  $('metric-select').setAttribute('aria-label', t('metrics.selectLabel'));
  $('state-select').setAttribute('aria-label', t('state.label'));
  renderStateSelect();
}

function renderStateSelect() {
  const select = $('state-select');
  select.innerHTML = data.dashboard_states.map(state => `<option value="${escapeHtml(state.id)}">${escapeHtml(state.label)}</option>`).join('');
  select.value = currentState;
}

function renderStateBanner() {
  const copy = stateCopy();
  $('state-banner-title').textContent = copy.title;
  $('state-banner-text').textContent = ` · ${data.dashboard_states.find(item => item.id === currentState)?.available ? t('status.observed') : t('status.noSnapshot')}`;
  $('state-banner').classList.toggle('is-pending', !hasCurrentData());
}

function renderSummary() {
  const available = hasCurrentData();
  $('home-title').textContent = stateCopy().title;
  $('home-description').textContent = stateCopy().description;
  $('valid-lanes').textContent = available ? `${data.coverage.valid_lanes}/${data.coverage.total_lanes}` : '—';
  $('valid-lanes-note').textContent = available ? (language === 'tr' ? `${data.coverage.total_lanes} toplam lane` : `${data.coverage.total_lanes} total lanes`) : t('status.noSnapshot');
  $('model-count').textContent = available ? Object.keys(data.models).length : '—';
  $('pending-lanes').textContent = available ? data.coverage.pending_lanes : '—';
  $('source-count').textContent = available ? data.source_records.length : '—';
}

function renderHighlights() {
  const target = $('home-highlights');
  if (!hasCurrentData()) {
    target.innerHTML = '';
    $('home-empty').hidden = false;
    $('home-empty').innerHTML = `<strong>${escapeHtml(t('home.noSnapshot'))}</strong><span>${escapeHtml(t('home.noSnapshotNote'))}</span>`;
    return;
  }
  $('home-empty').hidden = true;
  target.innerHTML = `<div class="highlight-heading"><p class="eyebrow">${escapeHtml(t('home.highlights'))}</p></div>${HIGHLIGHTS.map(metric => {
    const meta = METRICS[metric];
    const rows = rowsFor(metric).filter(row => typeof row.value === 'number');
    const bestValue = meta.direction === 'lower' ? Math.min(...rows.map(row => row.value)) : Math.max(...rows.map(row => row.value));
    const best = rows.find(row => row.value === bestValue);
    return `<article class="highlight-card"><span>${escapeHtml(tx(meta.label))}</span><strong class="model-${best.model}">${escapeHtml(MODEL_LABELS[best.model])} · ${meta.format(best.value)}</strong><small>${escapeHtml(t('home.best'))} · ${escapeHtml(tx(meta.read))}</small></article>`;
  }).join('')}`;
}

function initMetricSelect() {
  const select = $('metric-select');
  select.innerHTML = Object.entries(METRICS).map(([key, meta]) => `<option value="${key}">${escapeHtml(tx(meta.label))}</option>`).join('');
  select.value = currentMetric;
}

function renderChart() {
  const meta = METRICS[currentMetric];
  const rows = rowsFor(currentMetric);
  const present = rows.filter(row => typeof row.value === 'number');
  const max = present.length ? Math.max(...present.map(row => row.value)) : 1;
  $('chart-title').textContent = tx(meta.label);
  $('chart-direction').textContent = meta.direction === 'lower' ? t('directions.lower') : t('directions.higher');
  $('metric-measure').textContent = tx(meta.measure);
  $('metric-read').textContent = tx(meta.read);
  $('metric-caveat').textContent = tx(meta.caveat);
  $('chart-caption').textContent = tx(meta.caption);
  $('chart').innerHTML = MODEL_ORDER.map(model => {
    const row = rows.find(item => item.model === model);
    const isPending = !row || typeof row.value !== 'number';
    const width = isPending ? 3 : meta.scale === 'fraction' ? row.value * 100 : (row.value / max) * 100;
    const bestValue = present.length ? (meta.direction === 'lower' ? Math.min(...present.map(item => item.value)) : Math.max(...present.map(item => item.value))) : null;
    const best = !isPending && row.value === bestValue;
    return `<div class="bar-row"><span class="model-name model-${model}">${MODEL_LABELS[model]}</span><div class="bar-track"><div class="bar-fill ${MODEL_CLASSES[model]}${isPending ? ' pending' : ''}" style="width:${Math.max(width, 3)}%"></div></div><span class="bar-value ${best ? 'best' : ''} ${isPending ? 'pending-text' : ''}">${isPending ? t('status.pending') : meta.format(row.value)}</span></div>`;
  }).join('');
  $('chart').setAttribute('aria-label', `${tx(meta.label)}: ${MODEL_ORDER.map(model => { const row = rows.find(item => item.model === model); return `${MODEL_LABELS[model]} ${row?.value == null ? t('status.pending') : meta.format(row.value)}`; }).join(', ')}`);
}

function renderMetricsPage() {
  const available = hasCurrentData();
  $('metrics-empty').hidden = available;
  $('metrics-empty').innerHTML = available ? '' : `<strong>${escapeHtml(t('detail.noSnapshot'))}</strong><span>${escapeHtml(stateCopy().description)}</span>`;
  $('metric-select').disabled = !available;
  $('chart-card').hidden = !available;
  if (available) { initMetricSelect(); renderChart(); }
}

function renderLaneMatrix() {
  const target = $('lane-matrix');
  if (!hasCurrentData()) { target.innerHTML = `<div class="empty-inline">${escapeHtml(t('detail.noSnapshot'))}</div>`; return; }
  const lookup = new Map(data.lane_status.map(row => [`${row.model}/${row.lane}`, row]));
  target.innerHTML = `<div></div>${LANE_ORDER.map(lane => `<div class="lane-head" title="${escapeHtml(tx(LANE_LABELS[lane]))}">${escapeHtml(tx(LANE_LABELS[lane]))}</div>`).join('')}${MODEL_ORDER.map(model => `<div class="lane-model model-${model}">${MODEL_LABELS[model]}</div>${LANE_ORDER.map(lane => { const row = lookup.get(`${model}/${lane}`); const pending = row?.status !== 'complete'; return `<div class="lane-cell${pending ? ' pending' : ''}" title="${MODEL_LABELS[model]} · ${escapeHtml(tx(LANE_LABELS[lane]))} · ${pending ? t('status.pending') : 'complete'}">${pending ? '—' : '✓'}</div>`; }).join('')}`).join('')}`;
}

function displayRow(row) {
  if (row.value == null) return `<span class="pending-text">${escapeHtml(t('status.pending'))}</span>`;
  if (row.unit === 'fraction') return `${(row.value * 100).toFixed(2)}%`;
  if (row.unit === 'count') return Math.round(row.value).toLocaleString('en-US');
  return formatNumber(row.value);
}

function renderMetricTable() {
  const target = $('metric-table');
  const filter = $('metric-filter').value.trim().toLowerCase();
  if (!hasCurrentData()) { target.innerHTML = ''; $('detail-table-wrap').hidden = true; $('detail-empty').hidden = false; $('detail-empty').innerHTML = `<strong>${escapeHtml(t('detail.noSnapshot'))}</strong><span>${escapeHtml(stateCopy().description)}</span>`; return; }
  $('detail-table-wrap').hidden = false; $('detail-empty').hidden = true;
  const metricKeys = [...new Set(data.metric_rows.map(row => row.metric))].filter(key => !filter || key.includes(filter));
  const byMetric = Object.fromEntries(data.metric_rows.map(row => [`${row.metric}/${row.model}`, row]));
  target.innerHTML = metricKeys.map(metric => {
    const sample = data.metric_rows.find(row => row.metric === metric);
    const meta = METRICS[metric];
    const label = meta ? tx(meta.label) : metric;
    const family = FAMILY_LABELS[sample.family]?.[language] ?? sample.family;
    return `<tr><td><code>${escapeHtml(label)}</code><small class="row-key">${escapeHtml(metric)}</small></td><td>${escapeHtml(family)}</td>${MODEL_ORDER.map(model => { const row = byMetric[`${metric}/${model}`]; return `<td class="model-${model}">${row ? displayRow(row) : '—'}</td>`; }).join('')}<td>${sample.direction === 'lower' ? escapeHtml(t('directions.lower')) : escapeHtml(t('directions.higher'))}</td></tr>`;
  }).join('');
}

function renderSources() {
  if (!hasCurrentData()) { $('sources').innerHTML = `<p class="muted">${escapeHtml(t('provenance.noSnapshot'))}</p>`; return; }
  $('sources').innerHTML = data.source_records.map(source => `<div class="source-row"><strong>${escapeHtml(source.source_ref)}</strong><span class="muted"> · ${escapeHtml(source.model)} · ${escapeHtml(source.lane)} · ${source.bytes.toLocaleString('en-US')} bytes</span><code>${escapeHtml(source.path)}</code><code>sha256: ${escapeHtml(source.sha256)}</code></div>`).join('');
}

function renderDetailPage() {
  $('generated-at').textContent = hasCurrentData() ? `${language === 'tr' ? 'snapshot' : 'snapshot'}: ${data.generated_at}` : t('status.noSnapshot');
  $('provenance-note').textContent = hasCurrentData() ? `${data.contract.extraction_mode}; ${language === 'tr' ? 'HU scratch kaynakları read-only.' : 'HU scratch sources are read-only.'} ${data.contract.scientific_note}` : stateCopy().description;
  renderMetricTable(); renderLaneMatrix(); renderSources();
}

function renderPageVisibility() {
  document.querySelectorAll('.tab').forEach(tab => { const active = tab.dataset.page === currentPage; tab.classList.toggle('is-active', active); tab.setAttribute('aria-selected', active ? 'true' : 'false'); });
  document.querySelectorAll('.page').forEach(page => { page.hidden = page.id !== `page-${currentPage}`; });
}

function renderAll() {
  applyI18n(); renderStateBanner(); renderSummary(); renderHighlights(); renderMetricsPage(); renderDetailPage(); renderPageVisibility();
}

async function main() {
  try {
    const response = await fetch(DATA_URL, { cache: 'no-store' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    data = await response.json();
    $('language-toggle').addEventListener('click', () => { language = language === 'tr' ? 'en' : 'tr'; renderAll(); });
    $('state-select').addEventListener('change', event => { currentState = event.target.value; renderAll(); });
    $('metric-select').addEventListener('change', event => { currentMetric = event.target.value; renderMetricsPage(); });
    $('metric-filter').addEventListener('input', renderMetricTable);
    document.querySelectorAll('.tab').forEach(tab => tab.addEventListener('click', () => { currentPage = tab.dataset.page; renderPageVisibility(); }));
    renderAll();
  } catch (error) {
    document.querySelector('.shell').innerHTML = `<section class="panel"><h1>Dashboard yüklenemedi</h1><p>Canonical dump okunamadı: <code>${escapeHtml(error.message)}</code></p><p>Repo root’tan <code>python3 tools/m0-dashboard/serve.py</code> ile aç.</p></section>`;
  }
}
main();
