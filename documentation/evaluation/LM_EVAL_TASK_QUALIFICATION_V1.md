# LM Evaluation Harness task qualification v1

**Status:** upstream semantics verified; data/runtime qualification incomplete  
**Upstream:** `lm_eval` v0.4.12 at commit
`6d642546f4688648fced259eb3302efd36ece5af`

## Verified interface

Version 0.4.12 provides the `lm-eval run`, `lm-eval ls` and `lm-eval validate` commands, YAML run
configs, the Hugging Face backend and native JSON results. eval-v1 will call the CLI in a dedicated
locked environment and then normalize the native output. It will not vendor or fork the whole
harness.

Primary upstream references:

- [release/tag](https://github.com/EleutherAI/lm-evaluation-harness/releases/tag/v0.4.12);
- [CLI reference](https://github.com/EleutherAI/lm-evaluation-harness/blob/v0.4.12/docs/interface.md);
- [task guide](https://github.com/EleutherAI/lm-evaluation-harness/blob/v0.4.12/docs/task_guide.md);
- [task catalog](https://github.com/EleutherAI/lm-evaluation-harness/tree/v0.4.12/lm_eval/tasks).

## Proposed core matrix

| Task | Exact task ID | Role | Primary metric | Shot | Cadence | Qualification |
|---|---|---|---|---:|---|---|
| WikiText-2 | `wikitext` | primary English retention | BPB | 0 | dense | task verified; dataset revision/parity open |
| Pile-10k | `pile_10k` | broad-domain English control | BPB | 0 | runtime decides dense/full | task verified; dataset revision/runtime open |
| BLiMP | `blimp` | English grammar | macro `acc` | 0 | full | 67-task group verified |
| HellaSwag | `hellaswag` | English commonsense | `acc_norm` | 0 | full | task verified |
| WinoGender | gender slice task IDs | coreference/bias diagnostic | `acc` and gaps | 0 | full | task IDs verified |
| TurBLiMP | `turblimp_core` | Turkish grammar check | macro `acc_norm` | 0 | full | duplicate-key parity test open |
| TurkishMMLU | `turkishmmlu_*` | Turkish knowledge, secondary | `acc` | 5 | full | access unresolved |

All tasks use the full frozen split. `--limit` is test-only and cannot define a scientific cheap
panel. Any cheap subset must be an explicit immutable sample-ID registry selected before outcomes.

## Task-specific decisions

### Retention

`wikitext` is canonical and reports word PPL, byte PPL and BPB using
`loglikelihood_rolling`. BPB is the primary retention statistic; all three raw values and the
parent-relative delta/ratio are retained. The official detokenizer remains unchanged. Heading or
Markdown transformations are bounded sensitivity analyses only.

Version 0.4.12 already contains `pile_10k`; a custom replacement is unnecessary unless parity
fails. It is complementary because it is a Pile sample and may overlap a model's pretraining.

### English capability

- BLiMP uses the upstream unweighted macro over 67 subtasks and official `acc`.
- HellaSwag uses length-normalized `acc_norm`; raw `acc` is sensitivity-only.
- WinoGender is diagnostic, not a model-selection gate. Female, male and neutral slices are run
  without duplicating the `all` task; sample-count-weighted overall accuracy and slice gaps are
  derived locally.

### Turkish capability

- TurBLiMP uses `acc_norm` as primary and raw `acc` as sensitivity. Its group YAML repeats the
  `aggregate_metric_list` key, so v0.4.12 effectively exposes the later normalized aggregate. The
  normalizer must prove the intended 16-subtask macro before freeze.
- TurkishMMLU follows the benchmark's published five-shot setup, but is secondary because it mixes
  language, curriculum knowledge and reasoning. It enters eval-v1 only if access and revision are
  frozen before contract freeze.

`xcopa_tr` is a reserve secondary task. `xquad_tr` is excluded from the proposed core because
free-form answer formatting adds a new source of variance without filling a missing primary
estimand. EWOK and Turkish HellaSwag remain outside eval-v1 until exact sources are supplied;
automatic translation is forbidden.

## Fixed harness settings

- base/pretrained causal-LM evaluation, `apply_chat_template = false`;
- no system instruction and no outcome-dependent prompt changes;
- task-specific few-shot settings above;
- fixed Python/NumPy/Torch/few-shot seeds of 42;
- canonical task YAMLs at the pinned commit;
- identical task, prompt, dataset and precision binding within every paired comparison;
- raw harness JSON preserved outside Git; normalized tables contain artifact hashes and paths.

## Remaining freeze evidence

The contract cannot become frozen until exact Hugging Face dataset commits/content manifests,
offline reload, final `lm-eval ls`/`validate`, OLMo base smoke, WikiText parity, Pile-10k runtime,
TurBLiMP normalization, TurkishMMLU inclusion/exclusion and the dedicated environment lock are
recorded. None of those checks has been executed by this document.
