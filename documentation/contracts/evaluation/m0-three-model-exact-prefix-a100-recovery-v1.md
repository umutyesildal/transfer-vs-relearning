# M0 Three-Model Historical Exact-Prefix A100 Recovery v1

Date: 2026-08-21  
Status: `FROZEN / UNEXECUTED / EXACT AUTHORIZATION REQUIRED`

## Purpose

Recover only the three M0 historical exact-prefix lanes that produced no scientific score in the
first supplement wave. The first root and all terminal evidence remain immutable. Existing robust
A--D direct/QA lanes are not rerun.

## Preserved source evidence

- source root: `/vol/tmp2/yesildau/eval_v1_m0_three_model_exact_prefix_supplement_v1`;
- source family-result SHA-256:
  `fee84e1ec4604c4a1a1dbc96a7f2a52a50d48a00ca9f6dbc2f1347b9bf3aaaa9`;
- source family-inventory SHA-256:
  `cbf35264fc5eef8394e2821bd63eeb047e64ac35b6712bff577595d4262d78c0`;
- terminal class: three operational `NOT_RUN` lanes, zero model loads and zero scientific scores;
- cause: each assigned RTX A6000 exposed only 3,142,844,416 free bytes against the frozen
  21,474,836,480-byte minimum.

## Unchanged scientific identity

The 500 probes, 100 subjects, five balanced relations, three exact model revisions, prompt and
candidate identities, mean-answer-token-log-probability primary ranking, total-logprob diagnostic,
canonical-object tie-break, BF16 runtime and 20 GiB execution guard remain unchanged. The semantic
label remains `historical_exact_prefix_candidate_ranking_not_free_generation`.

## Recovery route and namespace

The only new writable scientific root is:

`/vol/tmp2/yesildau/eval_v1_m0_three_model_exact_prefix_supplement_a100_recovery_v1`

One array `0-2%3` runs OLMo, Qwen and SmolLM concurrently. Every task requests exactly one
A100-80GB on `gruenau9`; one CPU `afterany` finalizer validates all artifacts. The current Slurm
snapshot described `gruenau9` as idle, but this is not an execution guarantee. Every task must
still pass the unchanged 20 GiB free-VRAM guard before model load.

## Frozen implementation

- implementation commit: `97831d167315f0ef34c7a554d1f7d2e4c74d71de`;
- operator SHA-256:
  `d240e091e55953950792295dbb18f64219182147978d16cd0d4b0e453f8ddea9`;
- study module SHA-256:
  `384b6bf989e1aa0d0a6acca7f35d8a04ecf857a998c8711d80b33911a3497664`;
- focused test SHA-256:
  `2698f761b3c135be35b3752ecd715750be874d2c41c48d5ae7cd879ad8a20009`;
- pre-authorization config SHA-256:
  `f6ebaa43d3517d55ad9311ab40f236530f69b0f07c9f43cc5bf2560f85c7cbb7`.

## Authorization boundary

The config remains `execution_authorized: false`. A new exact user instruction must bind this
contract's final SHA-256 and the pre-authorization config SHA-256 before push/HU synchronization,
final preflight or Slurm submission.

That instruction may authorize exactly one four-job recovery DAG. It does not authorize changing
the 20 GiB guard, using another route, mutating the first root, retrying completed robust lanes,
automatic retry, a second recovery wave, normalization, M1/M2 work, cleanup, deletion, HU-home
writes, or intervention in foreign jobs/processes. The Qwen Pile-10k recovery DAG remains
independent.
