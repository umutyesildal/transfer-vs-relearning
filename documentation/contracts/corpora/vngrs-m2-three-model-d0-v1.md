# vngrs three-model M2 D0 corpus closure contract v1

**Status:** `DRAFT / EXECUTION DISABLED`  
**Owner:** thesis project  
**Created:** 2026-08-27  
**Supersedes:** none; preserves all numbered 151-series evidence

## Purpose and estimand

Prepare one reproducible Turkish adaptation corpus shared by the future OLMo, Qwen and SmolLM
M2-A/M2-B sibling arms. D0 asks only whether the previously verified systematic 32-shard vngrs
subcorpus can be materialized with immutable identity, a lightweight Max-aligned quality check,
a document-disjoint in-domain held-out split and model-specific tokenizer accounting.

D0 has no model-quality, transfer or relearning estimand. It performs no training, inference,
evaluation or checkpoint selection. A D0 PASS makes the corpus eligible for a later dose and
matched-arm contract; it does not make M2 ready to train by itself.

## Scope and prohibitions

The future separately authorized D0 wave may:

- read the accepted metadata/footer evidence root without mutation;
- retrieve exactly the 32 listed immutable-revision Parquet objects;
- write only beneath one fresh scratch root;
- validate source bytes, Parquet schema and row identity;
- produce lightweight quality, contamination, split and tokenizer-yield evidence;
- write compact manifests, ledgers and a final audit atomically.

It may not:

- retrieve any of the other 252 vngrs shards;
- call the 32-shard subset the full vngrs release;
- write to HU home or any prior evidence root;
- load model weights, run inference, score benchmarks, use GPU/Slurm or train M1/M2;
- generate M2-A/M2-B factual replacement rows;
- select a dose, optimizer, learning rate, checkpoint or primary model;
- substitute `trwiki-20260601` as the primary in-domain corpus;
- clean, delete, overwrite, deduplicate in place or mutate historical artifacts.

Preparation of this draft grants none of the future actions above.

## Immutable identities

### Source corpus

| Field | Value |
|---|---|
| Repository | `vngrs-ai/vngrs-web-corpus` |
| Revision | `ee5c6201ee84457a18182bfc483a7d8a7f3655ba` |
| Split | `train` |
| Schema | `text`, `corpus`, `original_id` |
| Selection | systematic midpoint 32 of 284 |
| Selection payload SHA-256 | `dbb9714347970634386ff62366384fcae12cf5f12f1df1df676cb9af3ae25686` |
| Selected compressed bytes | `9,468,474,036` |
| Source role | `vngrs systematic 32-shard subcorpus`; not the full release |

The exact selected paths and their order are frozen in
`configs/corpora/vngrs_m2_three_model_d0_v1.yaml` and must equal
`FROZEN_SELECTED_SHARD_PATHS` from `src/transfer_vs_relearning/corpora/vngrs/metadata.py`.

### Accepted read-only evidence

| Field | Value |
|---|---|
| Root | `/vol/tmp2/yesildau/luna_vngrs_metadata_footer_feasibility_v1` |
| Regular files | `104` |
| Regular bytes | `18,025,945` |
| Inventory SHA-256 | `120cdd7b21e161bf981cf8191fa278a11829d3fc5c155b71ed4bc8836e27f1d3` |
| Shard metadata ledger SHA-256 | `6c6f27651945043ec2dfbf1b26575f416b5d38a8783d0a22320f0ffbf83d3fa3` |
| Metadata/footer audit SHA-256 | `769cda6c1e57170b6a39818b8fdf79dd65f091e3400131a3a964fd215e2015bb` |
| Selection plan SHA-256 | `dbb9714347970634386ff62366384fcae12cf5f12f1df1df676cb9af3ae25686` |

The accepted evidence proves metadata/footer feasibility and zero retrieved corpus rows. It does
not prove downloaded full-object hashes or training readiness.

### Future tokenizer accounting identities

| Model role | Model/revision | Required tokenizer binding |
|---|---|---|
| OLMo focal | `allenai/OLMo-2-0425-1B@a1847dff35000b4271fa70afc5db10fd29fedbdf` | exact frozen M1 parent tokenizer manifest |
| Qwen multilingual positive control | `Qwen/Qwen2.5-1.5B@8faed761d45a263340a0528343f099c05c9a4323` | exact frozen M1 parent tokenizer manifest |
| SmolLM comparator | `HuggingFaceTB/SmolLM2-1.7B@effd688a12921b4cc83e3312b6feb579f70f9c71` | exact frozen M1 parent tokenizer manifest |

Tokenizer audit loads tokenizer assets only and must not load model weights.

## Protocol

### D0.0 — read-only identity and storage preflight

Before network or output-root creation:

1. verify the reviewed Git commit and clean task overlap;
2. verify the accepted evidence root's exact file/byte/hash closure;
3. recompute the exact ordered 32-shard selection;
4. verify HU home is read-only and below the existing 30 GiB policy limit;
5. record `df`, inode capacity, scratch path resolution and expected peak storage;
6. require the fresh output root to be absent;
7. refuse duplicate active jobs or another D0 root for this contract.

### D0.1 — exact source materialization

- Resolve only immutable-revision URLs for the 32 frozen paths.
- Download to `raw/.partial/` and atomically rename only after expected size and SHA-256 pass.
- Bind every downloaded SHA-256 to the immutable source object/LFS identity obtained from the
  exact revision. An unresolved or mismatched source-object identity is a blocker.
- Total successful Parquet payload must be exactly `9,468,474,036` bytes.
- Cumulative HTTP response bytes may not exceed `10,737,418,240` bytes (10 GiB).
- Redirects, retries, content lengths/ranges and terminal hosts are recorded without secrets.
- A partial download is retained as typed failed evidence; it is never treated as a valid shard.

### D0.2 — schema and row identity

Every shard must:

- open as Parquet and reconcile footer row groups with the accepted ledger;
- contain the exact logical schema `text/corpus/original_id`;
- expose non-empty `text` and non-null `corpus/original_id` fields;
- derive the stable document ID from immutable revision, shard path, `corpus`, `original_id`, row
  group and row index;
- fail on duplicate stable IDs or ambiguous source identity.

Raw text is never written to Git. Compact outputs may contain counts, hashes and bounded reviewed
excerpts only where the later privacy review permits them.

### D0.3 — Max-aligned lightweight audit

The mandatory audit is intentionally small:

1. exact OSCAR/mC4 row and UTF-8-byte proportions;
2. deterministic `64`-document human-review sample, stratified by `corpus` label and shard
   quartile, with row IDs selected before text review;
3. deterministic counts/rates for invalid UTF-8/replacement characters, empty/very short text,
   boilerplate, SEO/betting and legal/jurisdiction regex groups;
4. exact and Unicode-normalized scans for the frozen 100 subjects, 500 objects and all frozen
   aliases;
5. exact duplicate stable-ID and normalized-text-hash summary.

The following are not mandatory D0 gates unless a precommitted escalation trigger fires:
corpus-wide learned quality classifiers, broad PII/adult/harmful taxonomies, corpus-wide fuzzy
near-dedup and large manual-labeling studies.

Escalation triggers are any invalid schema/identity row, target subject/object/alias hit, invalid
UTF-8, or human-review evidence of text unsafe/unusable for the intended research. A trigger
blocks D0; it does not silently enlarge the wave.

### D0.4 — document-disjoint split

- Namespace: `vngrs_primary_in_domain_heldout_v2`.
- Split seed: `42`.
- Hold out exactly `10,000` valid documents after identity and mandatory exclusion checks.
- Selection rule: ascending SHA-256 of
  `vngrs_primary_in_domain_heldout_v2|42|<stable_document_id>`; first 10,000 are held out.
- All remaining eligible documents form the raw training reservoir.
- Train and held-out stable document-ID intersection must be empty.
- `trwiki-20260601` remains a separate cross-domain control and contributes zero training rows.

### D0.5 — three-tokenizer accounting

Use the same raw train/held-out document IDs for all three models. For each frozen tokenizer,
record independently:

- non-empty document count and UTF-8 bytes;
- token count with the future packing policy explicitly excluded;
- tokens/byte, tokens/document and quantiles;
- zero-token/exception count;
- tokenizer manifest and asset SHA-256.

Cross-model raw token counts are descriptive, not an equality gate. Exact token/update matching
is required later within each model's M2-A/M2-B pair. BPB remains the cross-tokenizer normalized
language-model metric.

## Inputs, outputs and schemas

Proposed fresh root:

```text
/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v1
```

Required namespaces:

```text
control/       preflight, request/redirect ledger, failure and final audit
raw/           immutable 32 Parquet objects and per-file manifest
manifests/     source rows, document IDs, exclusions, train/held-out and tokenizer ledgers
reports/       schema, composition, regex, contamination and human-review summaries
splits/        document-ID-only train and held-out manifests
```

Required compact terminal artifacts include:

- `control/preflight.json`;
- `control/request_ledger.jsonl`;
- `manifests/source_shards.jsonl`;
- `manifests/document_identity_summary.json`;
- `manifests/exclusions.jsonl`;
- `splits/train_document_ids.jsonl`;
- `splits/heldout_document_ids.jsonl`;
- `reports/corpus_composition.json`;
- `reports/light_regex_quality.json`;
- `reports/human_review_sample.jsonl` and `human_review_summary.json`;
- `reports/synthetic_contamination.json`;
- `reports/tokenizer_accounting_{olmo,qwen,smollm}.json`;
- `manifests/output_artifact_manifest.jsonl`;
- `control/final_audit.json`.

Every JSON/JSONL output uses canonical UTF-8 encoding, atomic temp-write/rename and a schema
version. The output artifact manifest excludes itself and the later final audit; the final audit
binds the manifest hash in a one-way terminal chain.

## Gates and missingness

D0 is `PASS` only when all 32 source objects, exact payload bytes, schema/identity checks,
mandatory lightweight audit, document-disjoint split, three tokenizer reports and output hash
chain pass.

Any missing artifact/row/hash is `BLOCKED` or `INCOMPLETE`, never zero and never PASS. Network,
storage, parser or tokenizer failure is operational `NOT_RUN` evidence, not a corpus-quality or
model result. A serious content signal is a corpus gate failure and requires a separately reviewed
repair/version; it does not authorize post-hoc filtering.

## Preflight, resume and rollback

- The output root must be fresh and absent before first authorized execution.
- Completed source shards are immutable and may be reused only within the same D0 root after
  byte/hash revalidation.
- Resume may continue `.partial` files only if server identity, expected object identity and
  recorded byte prefix are exact; otherwise it fails closed without deletion.
- A terminal PASS root cannot be resumed or overwritten.
- Historical 151 roots and all source/model/M1 artifacts remain read-only rollback evidence.
- No automatic retry, alternate corpus, alternate revision or expanded shard set is authorized.

## Verification

Before this draft can become `qualified`:

1. ~~implement a fail-closed full-object materialization operator and offline fixture tests~~ —
   locally complete in `transfer_vs_relearning.corpora.vngrs.materialization`; the operator has
   no implicit network client, is execution-disabled by default and passed offline fixtures;
2. bind per-shard expected size plus immutable object/LFS SHA-256 from accepted evidence;
3. ~~implement deterministic lightweight audit, split and tokenizer accounting outputs~~ —
   locally complete as execution-disabled, transport-injected operators and offline fixtures;
4. validate config against `FROZEN_SELECTED_SHARD_PATHS` and current model revisions;
5. run the full compatible offline test suite;
6. freeze code/config/contract hashes and expected storage/inode bounds.

Before execution, the contract must become `frozen` and receive separate exact SHA-bound user
authorization.

## Current blockers

- exact per-shard full-object/LFS SHA-256 registry is not locally closed;
- scratch free-space/inode and peak-storage requirements are not yet measured;
- contract, config and implementation hashes are not frozen.

## Local implementation checkpoint (2026-08-27)

The first verification item is locally implemented. Registry closure occurs before root creation
or transport use; production policy requires the frozen 32-path order; size, SHA-256 and LFS OID
must agree; unsafe paths, mutable URLs, response-header drift, encoded bodies, byte-budget drift
and existing roots fail closed. Successful objects move atomically from `raw/.partial/` only after
full verification. A failed object remains typed evidence and is never published as valid.

This checkpoint does not provide the missing real 32-object hash registry and does not enable the
operator, network access or materialization.

The second local checkpoint implements OSCAR/mC4 byte/document composition, the five frozen regex
groups, exact and Unicode-normalized synthetic scans, normalized-text duplicate summaries, a
text-free stratified 64-ID human-review sample, the exact hash-ranked 10,000-document held-out
split and three model-specific tokenizer-accounting reports. The tokenizer layer accepts only the
frozen OLMo/Qwen/SmolLM identities and requires a common raw document-ID hash, but deliberately
does not impose cross-model token-count equality. No tokenizer asset was loaded by this checkpoint.

The local M1 result dump additionally closes each model's epoch-036 path plus snapshot, training
and model-manifest SHA-256. It does not contain the per-file tokenizer asset inventory, so those
parent bindings are recorded without fabricating a tokenizer asset-manifest hash. Closing that
last layer requires a separately authorized read-only inventory of the preserved M1 roots.

A manifest-only tokenizer inventory extractor is now locally implemented and fixture-tested. It
verifies the raw snapshot/model-manifest payload hashes, exact epoch-036 root binding and a closed
tokenizer filename allowlist, then derives a canonical tokenizer asset-manifest hash from declared
rows. It opens neither tokenizer assets nor model weights. At preparation time the real
three-model outputs remained unresolved pending separate authority.

The separately authorized six-file read-only pass subsequently completed with all six expected
hashes matching and 5,988 remote manifest bytes read. HU writes, tokenizer/model asset reads and
corpus reads were zero. The resulting tokenizer asset-manifest hashes are OLMo
`1bb3f5ee04b6f32aab990e46fb99520b1e4ab04bdc3f1cfa75ea732c8f8dfd17`, Qwen
`8e1cbce23938ba773e652fc767002a6687f3ec4f538139d8b760b3fe0b33a2df` and SmolLM
`1f41566541c514dcebac6168f0f2f83f2b54a969c6b36db4501ae4d0683fd652`.
This closes only the tokenizer inventory blocker; D0 remains unqualified and unexecuted.

## Authority boundary

This draft authorizes local code, configuration, documentation, offline fixtures and dry-run
validation requested by the user. It does not authorize network retrieval, corpus
materialization, HU/SSH, Slurm/GPU, tokenizer/model access on HU, training, evaluation, scoring,
publication of this M2 branch, cleanup or deletion.

## Change policy

Changing source revision/path set, split rule, held-out count, human-review sampling, mandatory
quality/contamination rules, tokenizer identities, output root or byte/storage bounds creates v2.
After freeze, only implementation repairs proven semantically equivalent may use an append-only
correction; historical failures remain preserved.
