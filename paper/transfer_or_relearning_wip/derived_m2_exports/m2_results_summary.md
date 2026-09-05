---
title: M2 results thesis export package
input_manifest_sha256: 8cd18cd458b8261205721e93f09310fe67dc0c133f5daa772de4a36688d61ad9
---

# M2 results export package

The canonical estimands are transfer (M2-A minus M1) and relearning (M2-B minus M2-A), both on `tr_to_en` factual access. The two M2 arms are parallel siblings initialized from the same M1 parent; M2-B was not trained from M2-A.

## Corrected all-subject contrasts

| Model | Transfer (pp) | Relearning (pp) |
|---|---:|---:|
| OLMo | -14.1 | 2 |
| Qwen | -30.7 | 4.35 |
| SmolLM | -16.175 | 0.35 |

The corrected paired-subject bootstrap uses `probe_id`, 100 subjects, eight prompt variants, 10,000 draws and seed 42. The historical `fact_id` bootstrap is superseded and is not used by these exports. Qwen has the strongest descriptive relearning estimate, but its point gain remains below the precommitted +5 percentage-point gate; no model passes all primary gates and no primary model is selected.

Checkpoint factual top-1 uses 1,500 probes and must not be read as the 12,000-probe endpoint suite. Missing values remain missing; no composite score combines factual accuracy, BPB, exact-prefix or capability metrics.
