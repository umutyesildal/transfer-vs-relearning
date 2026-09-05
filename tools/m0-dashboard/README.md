# M0–M2 Evidence Explorer

Dependency-free, bilingual, read-only local dashboard for the frozen M0 baseline, M1 endpoint,
and completed OSCAR M2-A/M2-B result layers. The app reads the versioned derived manifest
`tools/m0-dashboard/data/results_explorer_data.json` (with a compatibility fallback for the planned
`results_explorer_v1.json` name); the browser only filters and formats validated
rows and never performs scientific joins.

## Run locally

From the repository root:

```bash
python3 tools/m0-dashboard/serve.py
```

Open <http://127.0.0.1:8765/tools/m0-dashboard/>.

The five sections are:

- Overview: M0 → M1 → parallel M2-A/M2-B timeline, completion counts, and terminal conclusion.
- Primary result: transfer (`M2-A − M1`) and relearning (`M2-B − M2-A`) intervals, the +0.05
  threshold, endpoint states, and the model-by-criterion gate ledger.
- Trajectories: model/arm/metric checkpoint curves and denominator-aware checkpoint rows.
- Diagnostics: relation, prompt-form, and scaffold/direction endpoint breakdowns.
- Provenance: source paths, hashes, glossary, and the historical `fact_id` bootstrap warning.

Missing data stays visibly pending and is never rendered as zero. M2-A and M2-B are displayed as
parallel sibling arms initialized from the same M1 parent; the dashboard does not promote a
descriptive model as an automatic primary selection.

No HU/network access, model loading, inference, training, or evaluation is performed by this app.
