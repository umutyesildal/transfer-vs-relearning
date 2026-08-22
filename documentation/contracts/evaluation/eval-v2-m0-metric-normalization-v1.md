# eval-v2 M0 metric normalization v1

**Lifecycle:** contract prepared on `agent/m0-metric-normalization`; execution unexecuted

**Execution authorized:** no

## Purpose

Convert the completed hash-closed M0 reference projection into the canonical eval-v2 long-form
metric schema. This is a provenance-preserving schema transformation, not a new model evaluation:
the operator reads only already-computed source artifacts, verifies their declared hashes, and
copies/normalizes their existing metric values. It never loads a model, runs inference, rescored a
lane, or recomputes a factual/bootstrap score.

The M0 source projection is complete, but M0 scientific interpretation remains open until this
contract is separately authorized and its output passes the final inventory gate.

## Frozen input identities

The operator must bind all of the following before reading a metric artifact:

| identity | value |
| --- | --- |
| eval-v2 contract | `documentation/contracts/evaluation/eval-v2.md` / `95eec6fc5a9dd7ce6da3185dfe20e2a183ad3850194c15f88a1299f09a43c6a3` |
| eval-v2 registry | `configs/evaluation/eval_v2_registry.yaml` / `0721412c651f5b112f531e69b53c98ccdb3633bee4888571bd7039d3f693229d` |
| result schema | `documentation/evaluation/RESULT_SCHEMA_V1.md` / `239d00c83aaa0a9bc169a22dfcfe9ece6f8a5b3d5be4f55dabbf254d7b2b64c1` |
| source projection contract | `eval-v2-m0-projection-v1b.md` / `4ee1d08f06f789c01f563cccd7ef80772fa403f51a7fe2bb440c577418f42500` |
| source projection config | `eval_v2_m0_projection_v1b.yaml` / `debc12012e77b323ac1ad73331a5ab4a7d66a7900e5b16efeaa3c274ad1d3f82` |
| source registry | `/vol/tmp2/yesildau/eval_v2_m0_three_model_projection_v1b/source_registry.jsonl` / `a0dca252afe7c1d03e458a60a8b48d7e8d8858e0ad95e6e8be696311a0b34265` |
| source projection manifest | `/vol/tmp2/yesildau/eval_v2_m0_three_model_projection_v1b/projection_manifest.json` / `9081b8eabef1ddfe1139754176cdcb1a26757fa3367d511cf81183536c8a9e0c` |

The source registry must contain exactly 24 rows: 21 required non-Pile lanes and three
`exact_prefix` supplement rows. Any missing, duplicate, Pile, path-escaping, or hash-drifted row
fails closed before creating the output root.

## Read and write boundary

Allowed reads are limited to the frozen projection root, its source registry references, each
referenced top manifest, each referenced lane-result JSON and the artifact paths declared by those
lane results. Model weights, tokenizers, datasets, caches, Slurm state and Pile-10k are outside
scope. Historical source roots remain read-only.

The only writable location is the fresh root from the v1 normalization config:

`/vol/tmp2/yesildau/eval_v2_m0_metric_normalization_v1`

Expected outputs are:

- `checkpoint_registry.parquet` — three M0 model-baseline rows, with unavailable training fields
  explicitly marked `not_observed_historically`;
- `metric_observations.parquet` — canonical long-form rows from the completed lane summaries;
- `factual_probe_results.parquet` — copied factual probe rows only when declared by a verified
  factual artifact;
- `m0_metric_summary.json` — descriptive per-model/lane values and explicit missingness;
- `normalization_manifest.json` — input identities, adapter mapping, zero-rescore status and
  output hashes;
- `final_inventory.json` — one-way output inventory excluding itself.

No normalized row is written until every required lane and required metric mapping passes its
schema and source-hash checks. Partial output roots are forbidden.

## Deterministic metric mapping

The operator uses the existing source summary values and the eval-v2 registry roles:

| lane | canonical observations | role |
| --- | --- | --- |
| `english_retention_wikitext` | raw bits-per-byte, word perplexity, byte perplexity | primary retention observation; M0 parent/delta fields are `not_applicable` |
| `english_grammar_blimp` | macro accuracy and declared sample count | primary capability observation |
| `english_capability` | HellaSwag `acc_norm`; Winogender slice diagnostics | primary plus diagnostic observations |
| `turkish_capability` | TurBLiMP `acc_norm` and declared sensitivity `acc` | primary plus sensitivity |
| `turkish_perplexity` | frozen held-out Turkish raw bits-per-byte and declared perplexities | primary Turkish retention observation; M0 parent/delta fields are `not_applicable` |
| `factual_access` | source-declared top-1, relation/form/scaffold/worst-cell and robust-intersection rows | primary factual observations; paired uncertainty is copied, not recomputed |
| `generation_integrity` | source-declared generation quality/integrity diagnostics | diagnostic observations |
| `exact_prefix` | exact-prefix candidate-ranking accuracy rows | secondary supplement; never treated as free generation |

The canonical primary retention unit is raw bits-per-byte. Byte/word perplexity are retained as
companions. A BPB ratio, `100 / PPL ratio` retention score, z-score, cross-model rescaling or any
other derived comparison is not generated in the M0 normalization pass. M0 has no adaptation
parent, so `parent_state`, `comparison_reference`, `absolute_delta` and `ratio_to_reference` are
`not_applicable` rather than zero or an invented base.

## Fail-closed and interpretation rules

- Source values are copied only after artifact byte count and SHA-256 verification.
- Missing or ambiguous metric keys produce `blocked_by_metric_schema`, not zero-filled rows.
- A raw source metric with an unverified denominator, task revision, split, prompt or filter is
  `not_run`/`missing_reason`, and the aggregate gate remains closed.
- Existing source bootstrap intervals may be copied with their frozen method metadata; no new
  bootstrap, significance test, threshold application or model ranking is performed.
- Cross-model output is descriptive evidence only. No primary-model selection is permitted.
- Pile-10k, normalization of historical weights, M1 inventory/training, M2-A/M2-B work, cleanup,
  deletion, publication and HU-home writes are forbidden.

## Later boundary

After a successful normalization inventory, a separate scientific interpretation decision may
consume the long-form rows to calculate M0 descriptive comparisons. That later decision must not
retroactively alter this input mapping or introduce a different metric family.
