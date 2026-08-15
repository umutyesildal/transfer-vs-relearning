# 11 — Reproducibility, Artifacts, and HPC Execution

## 1. Reproducibility has layers

### Computational reproducibility

Can the same code, data, configuration, and environment recreate the output?

### Inferential reproducibility

Would an independent analyst compute the same statistics and conclusion from the artifacts?

### Replicability

Does the scientific conclusion survive a new stochastic run, model, or dataset?

### Auditability

Can a reviewer reconstruct what actually ran, including failures and missing work?

The project’s documentation and artifact rules target all four.

## 2. The run manifest

A run manifest should contain:

- run ID and timestamp;
- code commit and dirty-state audit;
- model/tokenizer revisions and hashes;
- data and block manifests;
- training config hash;
- resolved hyperparameters;
- seed;
- host/GPU identity;
- runtime versions;
- precision topology;
- Slurm job IDs and dependencies;
- input/output paths;
- start and terminal status;
- checkpoint inventory;
- integrity results;
- failure classification.

The manifest is the bridge between a planned contract and actual execution.

## 3. Configuration as data

A YAML file is not enough if defaults are resolved dynamically. Store:

- original config bytes and hash;
- fully resolved config after defaults;
- command-line overrides;
- environment-derived values;
- library defaults that matter;
- validation output.

Two commands can reference the same YAML but produce different behavior because of environment variables or versioned defaults.

## 4. Code commit and dirty overlap

A Git commit identifies tracked content. A dirty worktree can contain uncommitted changes that alter execution.

Audit:

- exact commit;
- whether the tree is dirty;
- which changed files overlap the execution path;
- whether untracked code is imported;
- whether the remote/HU checkout matches the local commit.

The project uses ordinary non-force pushes and preservation-checked fast-forwards so chronological evidence is not rewritten.

## 5. SHA-256 contracts

A frozen document’s SHA-256 binds authorization to exact bytes. This prevents a subtle but serious failure:

1. user authorizes a contract;
2. implementation or scope changes;
3. old authorization is treated as permission for the new plan.

With SHA binding, any byte change produces a new hash and requires a new authorization when the contract says so.

The hash does not make the contract scientifically good. It makes the authorized text unambiguous.

## 6. Fail-closed gates

A fail-closed system stops when required evidence is missing or unexpected:

\[
\text{proceed}
=
\bigwedge_{j=1}^{k}\text{gate}_j.
\]

Examples:

- expected model revision matches;
- tokenizer probe encodings are nonempty;
- data hash matches;
- scratch root is fresh;
- storage/inode capacity passes;
- GPU is clean under the frozen rule;
- optimizer smoke is finite;
- output row counts are exact.

Fail-open behavior would warn and continue, creating artifacts whose validity is uncertain. For a thesis pipeline, stopping is often the safer scientific choice.

## 7. Preflight, smoke, training, evaluation

The project separates stages:

~~~mermaid
flowchart LR
    P["Read-only preflight<br/>identity, paths, storage, data"] --> S["Runtime/optimizer smoke<br/>memory + finite math"]
    S --> T["Scientific training<br/>optimizer updates"]
    T --> EP["Evaluation preflight<br/>checkpoint + registry integrity"]
    EP --> E["Scientific evaluation"]
    E --> A["Analysis and gate"]
    A --> F["Retention freeze<br/>inventory + hashes"]
~~~

Each stage can fail without implying that later scientific work ran.

## 8. Operational NOT-RUN versus scientific negative

### Operational NOT-RUN examples

- tokenizer encodes probes as empty;
- GPU kernel lacks the target architecture;
- optimizer smoke OOMs before update zero;
- clean-GPU selector finds no eligible device;
- dependency prevents evaluation from starting.

### Scientific negative examples

- training completes validly;
- evaluation integrity passes;
- exact acquisition is 100%;
- PPL ratio is above 1.25;
- robust minimum is below 70%.

The terminal classification should answer:

1. Did scientific training begin?
2. How many optimizer updates completed?
3. Was the checkpoint valid?
4. Did scientific evaluation run?
5. Which gate failed?

## 9. Slurm dependency semantics

An HPC directed acyclic graph may use:

- training preflight;
- training job after preflight success;
- evaluation preflight after training;
- evaluation after evaluation preflight;
- summary after all required evaluations.

An after-success dependency means a downstream job remains dependency-pending or becomes dead if the parent fails. A dependency-dead summary is not a completed negative summary.

Job IDs belong in the record, but scheduler accounting is secondary evidence. Primary scientific evidence is in immutable manifests, checkpoints, logs, and results.

## 10. Clean-GPU guards

Scheduler allocation alone may not imply a physically clean GPU. Foreign processes can occupy VRAM even when Slurm state looks idle.

A guard can inspect:

- GPU UUID;
- total/free/used memory;
- process list;
- required minimum free memory;
- maximum permitted used memory;
- stable selection rule.

The Falcon recovery contract used a frozen clean-UUID selection and persisted a full four-GPU failure ledger when no device qualified. All four A6000s were occupied by foreign processes, so no model load or scientific evaluation ran.

The audit ledger matters because “no GPU selected” without observations is not independently verifiable.

## 11. Storage architecture

HPC environments often separate:

- home: small, backed-up or policy-limited;
- scratch: large, fast, less durable;
- project/shared storage: managed retention;
- local node temporary storage.

Large weights, caches, optimizer checkpoints, and corpora should resolve to approved scratch roots. A no-home-write policy prevents accidental quota incidents.

Preflight can check:

- exact root path;
- root absence for fresh runs;
- free bytes;
- free inodes;
- filesystem identity;
- cache/temp environment variables;
- expected output upper bound.

Never trust an unresolved path variable for destructive or high-volume work.

## 12. Artifact lifecycle

Artifacts have roles:

- **source evidence:** raw data and metadata;
- **intermediate:** token blocks, caches;
- **scientific output:** checkpoints, per-probe results, summaries;
- **audit:** manifests, logs, hashes;
- **temporary:** recomputable staging files.

A retention plan decides:

- what must be kept;
- for how long;
- whether model-only checkpoints are enough;
- which artifacts can be recomputed;
- what deletion requires approval.

The completed Qwen M2/M3 freeze retained model-only scientific checkpoints and audit evidence under a documented storage policy. It did not silently delete chronological failures.

## 13. Model-only versus resumable retention

### Model-only

Keeps weights, config, tokenizer bindings, and enough metadata for evaluation.

Advantages:

- smaller;
- sufficient for inference and mechanism analysis.

Limitations:

- cannot exactly resume optimizer trajectory;
- scheduler/scaler/RNG state may be gone.

### Resumable

Adds optimizer, scheduler, scaler, RNG, and sampler state.

Advantages:

- restart training more faithfully;
- inspect optimizer dynamics.

Limitations:

- much larger;
- version compatibility remains a risk.

The retention level should follow the planned future analyses.

## 14. Artifact manifests and one-way audit chains

An artifact manifest can list:

\[
(\text{path},\text{bytes},\text{SHA-256},\text{producer},\text{role}).
\]

Avoid self-referential hashing. A practical chain is:

1. produce outputs;
2. write manifest excluding itself and the final audit;
3. hash manifest;
4. write final audit that names the manifest hash.

The project’s coverage-repair protocols explicitly froze one-way final-audit chains to avoid impossible self-reference.

## 15. Exact counts and completeness

Integrity assertions should include:

- expected file count;
- expected evaluation rows;
- unique key count;
- no duplicates;
- exact checkpoint set;
- exact task set;
- no NaN/Inf;
- valid denominator count.

For the dose family, 18 cheap rows were required. With 15 present, no family summary or automatic model selection was valid. A nearly complete matrix is still incomplete if the frozen gate requires all rows.

## 16. Logs versus manifests

Logs are chronological and useful for diagnosis, but they can be verbose, truncated, or environment-dependent. Manifests are structured declarations.

Use both:

- logs show what the process reported over time;
- manifests store resolved identity and terminal facts;
- result files store scientific measurements;
- documentation interprets them.

No single source should carry the entire evidentiary burden.

## 17. Checkpoint identity

A path such as “checkpoint-252” is not globally unique. Bind it to:

- model family;
- run ID;
- parent M0/M1 identity;
- seed;
- config hash;
- update count;
- file hashes;
- tokenizer;
- precision/runtime manifest.

This prevents evaluating a stale checkpoint with a valid-looking directory name.

## 18. Reproducible evaluation

An evaluation manifest should resolve:

- checkpoint identity/hash;
- task and slice registry;
- prompt-rendering code;
- candidate and alias registries;
- generation parameters;
- dtype and device;
- expected and actual counts;
- per-probe outputs;
- summary algorithm;
- bootstrap seed and replicate count.

Storing per-probe results enables independent recomputation. A summary JSON alone cannot expose pairing errors or slice imbalance.

## 19. Chronological scientific record

Failed attempts remain scientifically useful:

- they reveal incompatible tokenizer behavior;
- document memory ceilings;
- distinguish hardware/runtime constraints;
- prevent repeated unsafe retries;
- explain why a later repair changed one field.

Rewriting old reports to show only the final successful path creates hindsight bias and destroys the chain of reasoning. Append-only corrections preserve both error and repair.

## 20. Why no automatic retry?

An automatic retry can unintentionally change:

- GPU model;
- precision;
- batch decomposition;
- optimizer implementation;
- seed;
- input order;
- environment.

Each change can alter the scientific treatment. The project therefore separates:

- bounded operational reroute preserving the scientific recipe;
- scientific recipe amendment requiring a new contract.

This is conservative, but it prevents infrastructure adaptation from becoming hidden hyperparameter search.

## 21. Environment capture

Record:

- OS/kernel;
- Python;
- PyTorch;
- CUDA toolkit/runtime;
- GPU driver;
- Transformers;
- Datasets;
- evaluation harness;
- tokenizer libraries;
- package lock or environment export;
- relevant environment variables.

Container or environment hashes improve portability, but hardware kernels can still differ. “Same packages” does not guarantee bitwise results across GPU architectures.

## 22. Scientific versus bitwise reproducibility

Bitwise equality may fail because floating-point reductions and kernels are nondeterministic. Scientific reproducibility can still hold if:

- metrics agree within predefined tolerance;
- gate conclusions match;
- artifacts pass identity/integrity checks;
- stochastic variation is reported.

If exact bytes are required—for a frozen dataset or contract—use hashes. If scientific behavior is required, define numerical tolerances and replication rules.

## 23. A minimal evidence package

For one checkpoint evaluation:

- frozen plan/contract;
- source-model and tokenizer manifest;
- training config and code commit;
- data/block manifest;
- runtime manifest;
- training terminal manifest;
- checkpoint file inventory/hashes;
- evaluation config and task registry;
- per-probe results;
- summary metrics;
- bootstrap outputs;
- integrity report;
- scientific interpretation;
- retention/cleanup status.

The package should be navigable without relying on the researcher’s memory.

## 24. Common mistakes

### “The run completed because a checkpoint directory exists”

It may be partial or stale. Validate terminal state and hashes.

### “The scheduler says failed, so the model failed”

Scheduler failure can occur before scientific training or evaluation.

### “A hash makes analysis reproducible”

Only if the hash is connected to code, inputs, configuration, and outputs.

### “Cleanup is harmless after summaries are written”

Per-probe rows and checkpoints may be required for independent verification or new read-only analyses.

### “A retry is the same experiment”

Only if every scientifically relevant field remains frozen and the operational change is explicitly bounded.

## 25. Chapter summary

- Reproducibility includes computation, inference, replication, and auditability.
- Run manifests bind plans to actual code, data, model, runtime, jobs, and outputs.
- Fail-closed gates stop invalid evidence from entering the scientific record.
- Preflight, optimizer smoke, training, evaluation, and analysis are distinct stages.
- Operational NOT-RUN and scientific negative results must never be conflated.
- Slurm dependencies, clean-GPU evidence, storage roots, and artifact lifecycle affect validity.
- Per-probe outputs and exact inventories enable independent recomputation.
- Append-only chronological records prevent hindsight from hiding failures and repairs.

