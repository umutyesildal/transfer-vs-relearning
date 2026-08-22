# M0 eval-v2 source-binding discovery — 2026-08-22

Status: `PASS / read-only discovery complete / projection not executed`

This append-only record captures the single source-binding discovery pass authorized against
contract SHA-256 `926cfb019d316e993ee080ab2e2109599bbec9ee504f26b5475262fc45b910c8` and config
SHA-256 `59e41e8e8fc017063e40974579ee60bfd77c8650278b875bc2a88efa9f5b1884`.

No HU file was written. No historical source was mutated. No artifact payload was rehashed, no
lane was rescored, and no projection, normalization, evaluation, or training was started.

## Source closure

The pass resolved four top-level manifests and 24 lane bindings: 21 required non-Pile eval-v2
lanes (seven per model) plus three historical exact-prefix supplement rows. All referenced lane
result hashes matched their manifest declarations. Model repository/revision identities matched
the frozen eval-v2 registry. The exact-prefix family was accepted only with its semantic
classification `historical_exact_prefix_candidate_ranking_not_free_generation`.

| source | path | bytes | SHA-256 |
| --- | --- | ---: | --- |
| OLMo top manifest | `/vol/tmp2/yesildau/eval_v1_m0_scientific_three_model_recovery_retargeted_v1/olmo/evaluation_results.json` | 9,736 | `2adcbea6caeec9a3731b9f3fec4f9c3f3abf1b8c65caff750907e4b0d98c78a1` |
| Qwen top manifest | `/vol/tmp2/yesildau/eval_v1_m0_scientific_three_model_recovery_retargeted_v1/qwen/evaluation_results.json` | 8,875 | `18053c89efcafa7bc01f2b90988afbcf036786d3617f85ab8538e4a82c400f21` |
| SmolLM top manifest | `/vol/tmp2/yesildau/eval_v1_m0_scientific_three_model_recovery_retargeted_v1/smollm/evaluation_results.json` | 9,643 | `2ecc937cedd3860b84e999dbbd311b85c28db1b586d36b08a747419a64675ec4` |
| exact-prefix family | `/vol/tmp2/yesildau/eval_v1_m0_exact_prefix_smollm_recovery_v1/family_result.json` | 1,359 | `1bb5e066767d775b104965122490b873bd147b3f80292bb211175508b3aa03f8` |

The seven required lanes per model are:

`english_retention_wikitext`, `english_grammar_blimp`, `english_capability`,
`turkish_capability`, `turkish_perplexity`, `factual_access`, and `generation_integrity`.

The pass read 207,508 bytes from top manifests and lane-result JSON files. This is a source
identity result only; it does not establish the canonical metric projection or normalization.

## Next authority boundary

The three retargeted top-manifest hashes are now observed but remain `null` in the frozen
pre-discovery config so that the authorized config identity is preserved. A separately authorized
projection-preparation pass must create a new config/contract binding, insert these hashes, and
write only a fresh local projection registry. Metric normalization remains a later, separate
authority. Pile-10k remains excluded.
