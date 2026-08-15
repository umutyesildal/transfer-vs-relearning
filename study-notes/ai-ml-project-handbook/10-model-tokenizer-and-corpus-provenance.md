# 10 — Model, Tokenizer, and Corpus Provenance

## 1. Provenance is part of the independent variable

An experiment cannot be reproduced from a model name such as “OLMo 1B.” A usable identity includes:

\[
\text{model identity}
=
\text{repository}
+\text{immutable revision}
+\text{file inventory and hashes}
+\text{architecture config}
+\text{tokenizer identity}
+\text{loading code}
+\text{runtime}.
\]

Similarly:

\[
\text{corpus identity}
=
\text{source}
+\text{revision}
+\text{license}
+\text{schema}
+\text{filters}
+\text{split}
+\text{ordered bytes}
+\text{hashes}.
\]

If any component changes, the treatment can change even when the human-readable label stays the same.

## 2. Immutable revisions

Branches and tags can move. An immutable Git commit or model snapshot hash fixes the source at one state.

For each model:

- repository ID;
- exact commit/revision;
- resolved snapshot path;
- configuration hash;
- weight-file names and hashes;
- tokenizer sources and hashes;
- license evidence;
- model-card raw bytes and hash.

The Pythia repair preserved the exact weight revision while changing only the tokenizer source under a separately frozen contract. This made it possible to say that the repair addressed tokenization compatibility rather than substituting another model.

## 3. Model-card claims versus measured evidence

A model card may state:

- training data;
- language coverage;
- intended use;
- limitations;
- tokenizer family;
- parameter count.

These statements are primary metadata from the publisher, but they are not substitutes for runtime verification. Examples:

- claimed vocabulary size versus loaded tokenizer size;
- claimed parameter count versus tensor inventory;
- stated language distribution versus observed Turkish capability;
- stated revision versus local cache contents.

Use a two-column evidence model:

| Claim source | Example |
|---|---|
| publisher metadata | “trained on English-language web data” |
| local measured evidence | Turkish fertility, PPL, task score, file hashes |

Disagreement should be reported, not reconciled by assumption.

## 4. Tokenizer provenance

Tokenizer identity can require several files:

- tokenizer JSON/model;
- vocabulary;
- merges;
- tokenizer config;
- special-token map;
- added-token registry;
- normalization rules;
- upstream source commit.

Runtime audit should record:

- vocabulary size;
- special token strings and IDs;
- PAD/BOS/EOS/UNK semantics;
- encode/decode probes;
- offset mappings if available;
- save/reload equivalence;
- maximum token ID;
- embedding/output matrix compatibility.

A minimum compatibility condition is:

\[
\max(\text{encoded IDs})
<
\text{number of embedding rows}.
\]

But shape compatibility alone is insufficient. The ID-to-string mapping must also be the intended mapping.

## 5. Corpus selection versus corpus materialization

These are separate stages.

### Selection

Decide which source and subset can support the scientific estimand using metadata, documentation, licenses, sample audits, and bounded inventories.

### Materialization

Actually retrieve, filter, deduplicate, split, and write the training corpus.

The project’s literature-first realignment authorizes read-only audits before training contracts. This avoids downloading or processing a huge corpus before the study has a defensible measurement design.

## 6. License and access evidence

Record:

- license identifier and exact text/source;
- whether redistribution is allowed;
- whether derivatives can be shared;
- gated-access terms;
- personal-data considerations;
- repository access date;
- immutable data revision where possible.

“Publicly downloadable” is not the same as “licensed for every use.” The scientific record should distinguish technical access from legal/ethical permission.

## 7. Schema and record validation

A corpus record may contain:

- text;
- language label;
- source URL;
- document ID;
- timestamp;
- quality score;
- metadata.

Validation should test:

- required fields exist;
- text is a string;
- encoding is valid UTF-8;
- null/empty rates;
- duplicate IDs;
- length distributions;
- impossible metadata;
- parser failures;
- compressed-file integrity.

A schema pass does not prove text quality; it proves only that records conform to expected structure.

## 8. Language identification

Language identification estimates whether text is Turkish. Useful outputs include:

- document-level predicted language;
- confidence;
- character/script features;
- mixed-language proportion;
- aggregate pass rate by source.

Failure modes:

- short text is difficult;
- names and code are language-ambiguous;
- related Turkic languages can be confused;
- web navigation contains multilingual boilerplate;
- model confidence can be miscalibrated.

Use stratified human-readable samples to audit LID outcomes. LID should be one signal in a pipeline, not unquestioned truth.

## 9. Quality filtering

Possible filters:

- minimum/maximum document length;
- alphabetic-character proportion;
- control-character rate;
- repeated-line rate;
- HTML/boilerplate detection;
- URL density;
- punctuation or digit extremes;
- perplexity- or classifier-based quality;
- toxic or sensitive-content policy.

Each filter changes the target distribution. Over-filtering can remove informal Turkish, dialectal usage, or legitimate structured text. Report pre/post counts and token yields by rule.

## 10. Exact deduplication

Normalize a document with a frozen function \(n(x)\), then compute:

\[
h_i=\operatorname{SHA256}(n(x_i)).
\]

Documents with identical \(h_i\) are exact duplicates under that normalization.

Normalization decisions matter:

- Unicode form;
- whitespace collapse;
- case;
- punctuation;
- HTML removal.

Aggressive normalization can merge genuinely different text. Store both raw-source identity and normalized-dedup identity.

## 11. Near-duplicate detection

Near duplicates may differ by a few words or formatting. A common pipeline:

1. generate word or character shingles;
2. compute MinHash signatures;
3. use locality-sensitive hashing to find candidates;
4. verify similarity with Jaccard or another exact comparison.

For shingle sets \(A,B\):

\[
J(A,B)
=
\frac{|A\cap B|}{|A\cup B|}.
\]

Threshold choice changes what is removed. Report:

- shingle definition;
- signature size;
- candidate threshold;
- final similarity threshold;
- cluster policy;
- representative selection.

## 12. Train/validation/test splitting

Random row splitting after deduplication can leak near-identical documents across splits. Better:

1. deduplicate or cluster first;
2. assign whole clusters or source documents to one split;
3. freeze the assignment seed;
4. hash ordered split manifests;
5. verify zero ID overlap.

For time-sensitive corpora, a chronological split may better test future generalization. For domain comparisons, stratification may preserve source proportions.

## 13. Token yield

Raw bytes, characters, words, and tokens differ. After the exact tokenizer is frozen, calculate:

\[
\text{token yield}
=
\sum_{d\in D}|\operatorname{tok}(d)|.
\]

Also record non-padding and supervised tokens after block construction. A 10 GB corpus does not imply a predictable training dose because compression, markup, language, and tokenizer fertility vary.

## 14. Corpus-domain role

The project distinguishes:

- **primary in-domain Turkish held-out data:** measures adaptation on the selected target distribution;
- **trwiki-20260601 cross-domain control:** measures encyclopedic Turkish but is not automatically the primary training domain;
- **English WikiText-2:** measures English generic-language retention;
- capability benchmarks: measure specific behaviors rather than corpus likelihood.

Each dataset needs one declared role. Reusing the same corpus for selection, training, and final evaluation creates optimistic bias.

## 15. Synthetic-fact contamination

For each controlled fact, search the clean corpus for:

- exact subject string;
- exact object string;
- subject–object co-occurrence within a window;
- canonical sentence;
- paraphrase templates;
- normalized or transliterated variants;
- Turkish and English versions.

A staged audit can report:

\[
N_{\text{exact}},
\quad
N_{\text{cooccur}},
\quad
N_{\text{near}},
\quad
N_{\text{manual-confirmed}}.
\]

If the clean arm contains controlled facts, either exclude them under a frozen rule or redefine the estimand. Silent leakage invalidates the “fact-free” label.

## 16. Benchmark contamination

Benchmark overlap can occur in:

- source-model pretraining;
- M1 factual data;
- Turkish adaptation corpus;
- prompt templates;
- few-shot examples.

Exact hashes catch exact copies. Near-duplicate and phrase-level searches catch variants. For a pretrained source model, complete absence is usually impossible to establish because training data may be unavailable. Use calibrated language: “no overlap found under these checks,” not “contamination impossible.”

## 17. Provenance graph

~~~mermaid
flowchart TD
    Src["Raw source<br/>URL/revision/license"] --> Raw["Raw immutable files<br/>size + SHA-256"]
    Raw --> Parse["Parser/schema version"]
    Parse --> Filter["LID + quality filters"]
    Filter --> Dedup["Exact + near dedup"]
    Dedup --> Split["Frozen split assignment"]
    Split --> Tok["Pinned tokenizer"]
    Tok --> Blocks["Ordered token blocks"]
    Blocks --> Train["Training manifest and checkpoints"]
    Train --> Eval["Evaluation results"]

    Code["Code commit"] --> Parse
    Code --> Train
    Code --> Eval
    Runtime["Runtime manifest"] --> Train
    Runtime --> Eval
~~~

Every edge should be reconstructable from manifests. If a processed file exists without a recorded parent or transform, provenance is broken.

## 18. Hashes: what they prove and what they do not

SHA-256 of a file proves exact byte identity relative to another copy with the same digest, assuming the hash function’s collision resistance.

It does not prove:

- the bytes are scientifically correct;
- the source is trustworthy;
- the file was used by the job;
- two datasets with different serialization are semantically different;
- the process that produced the bytes was unbiased.

Hashes are identity evidence, not validity by themselves.

## 19. Ordered manifests

A dataset hash can be:

- hash of one packed file;
- hash of concatenated records;
- hash of a sorted list of per-file hashes;
- Merkle-style tree root.

Order must be specified. Two training streams with the same records in different order can produce different models. A robust manifest records each artifact:

\[
(\text{relative path},\text{size},\text{SHA-256},\text{role}).
\]

Then a manifest hash freezes the inventory.

## 20. Sampling audits

Aggregate metrics can hide data-quality failures. Draw frozen, stratified samples by:

- source;
- length bin;
- LID confidence;
- quality score;
- dedup cluster size;
- time;
- domain.

For each sample, inspect:

- actual Turkish quality;
- boilerplate;
- sensitive data;
- factual/benchmark leakage;
- formatting;
- topic distribution.

Sampling rules and sample IDs must be frozen before manual labels when the labels will influence selection.

## 21. Common mistakes

### “The repository name identifies the model”

Not without an immutable revision, tokenizer, file inventory, and runtime.

### “A corpus hash means the corpus is good”

It identifies bytes; quality requires separate evidence.

### “Deduplication is one universal operation”

It depends on normalization, similarity representation, thresholds, and cluster policy.

### “No exact overlap means no contamination”

Paraphrases and entity co-occurrences can still leak the target mapping.

### “A model card proves language capability”

Measure capability and tokenizer behavior directly.

## 22. Chapter summary

- Model and corpus provenance define the actual independent variables.
- Pin immutable revisions and record raw-byte inventories and hashes.
- Tokenizer special-token semantics and ID mapping are part of model identity.
- Separate corpus selection from materialization.
- LID, quality filters, exact dedup, near-dedup, split integrity, and token yield answer different questions.
- Contamination audits need exact, co-occurrence, and near-duplicate checks.
- Hashes prove byte identity, not scientific validity.
- An end-to-end provenance graph should connect raw sources to every evaluation result.

