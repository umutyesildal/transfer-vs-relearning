# M1 Historical Checkpoint Trajectory Inventory v1

**Lifecycle:** prepared, not frozen

**Execution authorized:** no

## Purpose

Determine exactly which retained M1 checkpoints can support a no-retraining historical trajectory
before deciding whether a new matched three-model M1 wave is necessary. This is a source inventory,
not evaluation and not model selection.

## Bounded families

The machine config names four exact families: Qwen seed 42, Qwen seed 43, OLMo seed 42 dose/Pareto,
and the matched factual-LM SmolLM seed-42 control. Other historical runs are outside this first
inventory. Pythia, Falcon, contrastive SmolLM treatments, M2 runs and optimizer cleanup are excluded.

## Permitted evidence

After separate exact authorization, a read-only HU pass may:

- verify each exact root exists and resolve its training manifest;
- list only expected checkpoint directories and their immediate model/config/tokenizer manifests;
- record file existence, byte size and existing compact manifest hashes;
- verify selected Qwen artifact-manifest identities;
- record evaluation summary paths already present;
- write one compact inventory only under the fresh output root.

The first inventory must not hash large model weights or optimizer states. A later checkpoint chosen
for eval-v2 backfill must receive a separately bounded full-byte hash verification before scoring.

## Scientific classification

Every point is `historical_backfill`. Missing epoch weights are `not_observed_historically`; they
are never interpolated, reconstructed from adjacent checkpoints or treated as zero. Heterogeneous
recipes cannot be presented as a matched three-model causal comparison.

## Prohibitions

- no GPU, Slurm, model load, inference, scoring, training or resume;
- no network or new artifact acquisition;
- no mutation, deletion, relocation, cleanup or HU-home write;
- no primary-model promotion or M1 closure;
- no claim that sparse legacy checkpoints satisfy prospective every-epoch tracking.
