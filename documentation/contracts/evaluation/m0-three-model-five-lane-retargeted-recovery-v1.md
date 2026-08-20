# M0 Three-Model Five-Lane Retargeted Recovery Contract v1

Date: 2026-08-20  
Status: `FROZEN / UNEXECUTED / EXACT AUTHORIZATION REQUIRED`

## 1. Purpose and boundary

Complete only the five M0 lanes that remain invalid or missing after the user-authorized
cancellation of exclusive controller `471047`. The 17 valid original-source lanes and the two
valid OLMo isolation results are retained by exact SHA-256. This contract changes no model,
tokenizer, dataset, seed, prompt, metric, batch behavior, precision, memory threshold or eval-v1
scientific semantics.

No execution is authorized by preparation of this document. Publication, HU fast-forward,
preflight and one Slurm DAG require a future exact SHA-bound user instruction.

## 2. Frozen evidence and the 19+5 split

- original M0 family root:
  `/vol/tmp2/yesildau/eval_v1_m0_scientific_three_model_v1`;
- original family bundle SHA-256:
  `75fcd7cf1e388eb5a4e883264c6aa14db83797b2e7832a4bbc8e40bb38865db1`;
- first recovery root:
  `/vol/tmp2/yesildau/eval_v1_m0_scientific_three_model_recovery_v1`;
- cancelled isolation root:
  `/vol/tmp2/yesildau/eval_v1_m0_scientific_three_model_recovery_isolation_v1`;
- cancelled isolation terminal composite SHA-256:
  `8563bfcdfbe49cb3953bfe54fb22cd5910cff2933caf80a74cd51eeb681839cb`;
- OLMo English capability lane-result SHA-256:
  `b254691b103bfae7fb9294b3078ae2a794e6c282d7afd3892e68eff4238df598`;
- OLMo Turkish capability lane-result SHA-256:
  `3c934519740b45f62d6ead3c34e3e3871f62ef9ba9f8e748b663d17c12101c64`.

The new composite must contain exactly 19 retained lanes and five new recovery lanes. The five
targets, in exact sequential order, are:

1. OLMo Turkish perplexity;
2. Qwen Pile-10k English retention;
3. Qwen Turkish capability;
4. Qwen Turkish perplexity;
5. SmolLM English capability.

The Qwen Pile lane keeps its 68,719,476,736-byte free-memory gate. Every other target keeps the
30,064,771,072-byte gate.

## 3. Evidence-integrity correction

The cancelled wave exposed an output-routing defect: the OLMo PPL evaluator completed into its
frozen config's original output path, then the lane wrapper correctly rejected that path as
outside the fresh recovery namespace. Nothing was deleted. The following appended artifacts are
now explicitly frozen as known integrity evidence:

- `.../corpora/summary.json`: 1,991 bytes, SHA-256
  `1b798928c52d1f5d2cb6fb2b4f7b284e22053ddd0f19772ad5c2b1c6d7cb206a`;
- `.../corpora/trwiki_cross_domain/loss_blocks.csv`: 954,202 bytes, SHA-256
  `1a99a61613f267ef83b9151f0ac1142afbdb17cdc953368e439396b931bfc69c`;
- `.../corpora/trwiki_cross_domain/summary.json`: 936 bytes, SHA-256
  `630ab6f16573160df8a13343ffac05706df49892ee971b89fe05cd59f9ebb2e1`.

The correction continues to verify the evaluator config and its original expected-output identity
by hash. Only after that validation, the recovery operator injects a runtime output root equal to
the fresh lane's `raw/corpora` directory. Runtime retargeting is accepted only for the corpus-PPL
adapter and the exact `corpora` subdirectory. Both PPL targets use this mechanism. No frozen
scientific config is rewritten.

## 4. Fresh namespace and execution topology

The only writable scientific root is:

`/vol/tmp2/yesildau/eval_v1_m0_scientific_three_model_recovery_retargeted_v1`

It must be absent at preflight. HU home, all three earlier roots, model roots and dataset caches
remain read-only. The execution topology remains one exclusive `gruenau10`
`gpu:a10080gb:3` controller, three `afterany` model finalizers and one `afterany` family finalizer:
exactly five Slurm jobs. The controller selects an eligible UUID deterministically before each
lane and executes the five targets sequentially in fresh child processes. There is no fallback,
automatic retry or second wave.

## 5. Composite and fail-closed conditions

Preflight must validate:

- the exact contract, config and implementation identities;
- the original 24-lane ledger and family bundle;
- all three known source-appended artifact hashes and sizes;
- both retained OLMo recovery lane results and every referenced artifact;
- exactly 19 retained and five target lanes;
- a clean implementation-descendant HU checkout;
- fresh-root absence, the 30 GiB HU-home gate and no duplicate `m0r-v1-*` jobs;
- the exact exclusive three-A100 Slurm route.

Finalization selects each lane from exactly one source: original root, retained isolation root or
fresh recovery root. Every selected result must have the frozen plan/lane/adapter identity,
scientific classification, `status=complete`, return code zero and artifact path/size/hash
integrity. Only a complete 24/24 result may set `normalization_allowed: true`. Missing or invalid
lanes remain explicit blockers and are never converted to zero scores.

## 6. Frozen implementation

- implementation commit: `caaa380c2b237437b38019ac319e95a82b38f80e`;
- operator SHA-256:
  `842ceb88e5d2831e60c509e3f6820dc8400a7f9baafe7c24f88e241688379551`;
- project-probe adapter SHA-256:
  `e05883a070e0a971620e087e426897a07bd0f1b7de0788e81b519f8dfd9dab18`;
- recovery module SHA-256:
  `8badbc9030b4776f6ba7de7719ca18f8f33e65ca156a194a4f5ee9fc4dd0ebe2`;
- adapter tests SHA-256:
  `c950c9fadd2126833eb67b9336cf45a31104a4c51e9396dc923ea094a3d9519a`;
- recovery tests SHA-256:
  `74693fabb1da2330016c7ea183a241c4d24f65543d76678f58cc5509bf1e6f1a`;
- compatible full suite: 469/469 passed.
- frozen pre-authorization config SHA-256:
  `705661dd5e32d836ee58f64101bc887c7a85059bae3ca2b25505ad967bde9a7d`.

## 7. Prohibitions and authorization request

This contract forbids rescoring the 19 valid lanes, changing eval-v1, lowering memory gates,
writing any evaluator output outside a fresh lane root, modifying/deleting prior evidence,
automatic resubmission, a second retargeted wave, normalization, scientific interpretation,
M1/M2 work, cleanup, deletion, HU-home writes and foreign-process intervention.

The frozen config remains `execution_authorized: false`. A future authorization must name the
final contract SHA-256 and config SHA-256 and explicitly authorize publication/HU fast-forward,
final preflight and the single five-job DAG. That authorization will be consumed by one submission
and will not cover normalization, M1/M2, cleanup or retry.
