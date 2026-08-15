# 109 - Turkish Bridge, Retention, And Scale Decision Plan

**Date:** 2026-07-19

**Status:** Accepted staged plan. The dated Turkish Wikipedia corpus component of Phase 109A is
complete and frozen; no HU bridge training or evaluation job is authorized yet. Localized-answer,
model-specific eligibility, exact token/update budgets, artifact estimates, and resolved bridge
output paths must still be frozen.

**Supersedes:** The narrower proposal to proceed directly to a Qwen-only retention experiment.
Documents 100 and 108 remain the authoritative summaries of the evidence that motivated this
change. Earlier failed results remain part of the scientific record.

## 1. Decision Summary

The project will not start final M2/M3, seed-43 replication, or the 5,000-subject M1. The next work
is a bounded feasibility and model-selection ladder:

1. run a small Turkish bridge pilot from the already-trained Qwen and SmolLM M1 checkpoints;
2. use pre/post bilingual access, Turkish/English PPL, and English fact retention to decide whether
   either family is a viable basis for Turkish adaptation;
3. if Qwen shows a usable bridge signal, compare a small number of controlled M1 retention
   mechanisms, because Qwen's factual retrieval passes while its PPL drift fails;
4. replicate a fully passing 100-subject candidate with seed 43;
5. move next to 500 subjects / 2,500 facts, not directly to 5,000 subjects / 25,000 facts;
6. freeze the learned/eligible fact pool at that scale;
7. only then run matched clean, lexical-alignment, and true-fact Turkish adaptation arms.

Gemma is removed from the active experimental path. StableLM and Llama remain recorded negative or
backup evidence but receive no further work under this plan.

## 2. Why The Order Changes

Document 108 ruled out Qwen early stopping: the first retained checkpoint that passes the factual
gates already has a PPL ratio of 1.455. A new acquisition objective is therefore required if Qwen
is to become the final M1 candidate.

However, lowering English PPL is valuable only if Turkish adaptation can expose measurable
cross-lingual access to the facts. A short bridge pilot using existing M1 artifacts has higher
information value than immediately launching a broad acquisition sweep. It can distinguish four
otherwise-confounded explanations:

- the model has no useful cross-lingual bridge;
- the Turkish adaptation dose is inadequate;
- localized free generation is hiding candidate-level access;
- the model/corpus combination is promising but English retention must be improved.

The bridge pilot is exploratory feasibility evidence. It is not the final transfer-versus-
relearning experiment and cannot support the thesis's final causal claim.

## 3. Active Models And Frozen Starting Points

### 3.1 Qwen

Use Qwen2.5-1.5B update 50 from Documents 106 and 108 as the primary Qwen M1 starting point. It is
the earliest retained checkpoint that passes the frozen factual gates:

- exact-prefix: 99.8%;
- minimum A/B held-out accuracy: 100%;
- minimum C/D held-out accuracy: 97%;
- robust global/minimum-relation intersection: 99.2% / 97%;
- English PPL ratio: 1.455, which fails the 1.25 retention gate.

The Qwen base model is its M0 comparator. Update 252 may be evaluated as a training-free sensitivity
reference, but it will not receive a second Turkish adaptation run unless a later plan justifies
the extra condition.

### 3.2 SmolLM

Use the selected SmolLM2-1.7B canonical-plus-diversity endpoint from Document 104 and its pinned
base model. SmolLM is the complementary comparison:

- exact-prefix: 100%;
- English PPL ratio: approximately 1.080, which already passes the retention gate;
- held-out and robust intersections remain below the frozen prompt-robustness gates.

SmolLM is therefore not assigned a generic `lower PPL` experiment by default. Its current problem
is robust access, not generic English retention. It enters the bridge pilot on a pre-frozen
eligible subset so that the project can test whether its genuinely learned facts become accessible
through Turkish. New SmolLM training opens only if the bridge results make it the uniquely useful
candidate and a separate plan states which failed gate the intervention targets.

### 3.3 Excluded models

- **Gemma:** removed from active consideration because the current result is not interpretable as a
  viable candidate and no clean positive acquisition/evaluation result exists.
- **StableLM:** retained only as historical backup evidence; it failed both a per-relation held-out
  floor and PPL retention.
- **Llama:** retained only as historical negative evidence; no new job is planned.

## 4. Phase 109A - Freeze The Bridge Contract Before Training

No bridge job may start until a compact implementation manifest freezes all items in this section.

### 4.1 Turkish corpus

Use the project's already configured dated Turkish Wikipedia source:

```text
trwiki-20260601-pages-articles.xml.bz2
```

The existing preparation route is `configs/corpora/trwiki_gpt2_calibration.yaml` with
`scripts/prepare_trwiki.py`. Reuse is conditional on verifying the local/HU artifact, its checksum,
the exact preprocessing version, and its contamination audit. Do not silently substitute a newer
dump after results are known.

Freeze document-hash-disjoint adaptation and held-out Turkish PPL splits. The held-out PPL split
must never be used for optimization, checkpoint selection, or dose selection.

### 4.2 Contamination exclusions

Before adaptation, reject or quarantine any document or span matching the synthetic inventory by:

- synthetic subject identifier or normalized subject name;
- exact or normalized object answer and alias when coupled to a target subject/relation;
- English or Turkish canonical target-fact sentence;
- templated subject--relation--object combinations;
- known generated corpus markers.

Record counts at every filtering stage and manually inspect a deterministic sample. Freeze the
filtered corpus manifest and SHA-256 hashes before examining bridge outcomes.

### 4.3 Localized answer contract

Create and audit one versioned mapping for all controlled object labels:

- English canonical answer;
- Turkish canonical answer;
- accepted aliases and Unicode normalization;
- relation-specific distractor set;
- tokenizer length under each model.

`TR->EN` and `TR->TR` are different outcomes. `TR->EN` tests whether a Turkish cue reaches the
English-acquired association without requiring answer translation. `TR->TR` additionally requires
localized lexical production and must not be treated as pure factual access.

### 4.4 Eligible facts, frozen before adaptation

Report the all-fact population, but define model-specific eligibility from English M1 evidence
before any Turkish training:

- correct top-1 candidate on at least three frozen held-out English prompt cells;
- positive normalized log-probability margin over the strongest relation-matched distractor in
  those cells;
- no integrity, alias, or ambiguous-answer failure.

Also freeze:

- a strict all-required-English-cells subset;
- the intersection eligible in both Qwen and SmolLM for direct cross-family comparison;
- fact and subject counts by relation and branch.

Do not require a subject to have four of five eligible facts for the primary fact-level pilot.
That rule can be reported as a subject-level sensitivity analysis; making it primary would discard
usable facts and reduce power.

### 4.5 Adaptation dose

Use two precommitted dose checkpoints, `low` and `full`, plus the unadapted endpoint. Exact token and
update counts must be frozen after tokenizing the audited corpus and before training. The contract
must satisfy:

- the same ordered raw Turkish documents for both model families;
- no repeated cycling through the small subset unless explicitly recorded;
- model-specific token counts reported because tokenizers differ;
- comparable raw text bytes/documents and optimizer exposure;
- the full dose bounded to a short feasibility run rather than final M2 scale;
- no choosing a dose after seeing factual metrics.

Phase 109A must add the numeric budgets to the manifest/config. Until those numbers exist, the plan
is scientifically accepted but not executable.

## 5. Phase 109B - Turkish Bridge Pilot

### 5.1 Required states

For each active family, evaluate:

| State | Meaning |
|---|---|
| M0 | pinned base model before English synthetic acquisition |
| M1 | selected existing English fact-acquisition checkpoint |
| B-low | M1 after the frozen low Turkish Wikipedia dose |
| B-full | M1 after the frozen full Turkish Wikipedia dose |

M0 is evaluated but not Turkish-adapted in the primary pilot. It measures pre-existing priors and
translation ability rather than learned-fact transfer.

### 5.2 Measurement matrix

At M0, M1, B-low, and B-full, report where applicable:

| Measure | Primary interpretation |
|---|---|
| EN->EN candidate rank and margin | storage/retention of the English fact |
| TR->EN candidate rank and margin | cross-lingual access without answer localization |
| TR->TR candidate rank and margin | localized Turkish access |
| English PPL and ratio to M0 | generic English drift/retention |
| Turkish PPL | whether Turkish adaptation had measurable language-model effect |
| frozen English prompt suite | factual retention after adaptation |

The primary retrieval metric is relation-specific candidate ranking using length-normalized
sequence log-probability and correct-versus-strongest-distractor margin. Exact/alias match, free
generation, and paraphrase agreement remain secondary diagnostic measures.

Report all facts, each model's eligible facts, the shared eligible intersection, the strict subset,
and every relation separately. Never hide a failed relation behind the global average.

### 5.3 Bridge decision rule

The bridge pilot does not reuse the final M1 PPL threshold as a binary transfer claim. Instead,
promotion requires all of the following qualitative and quantitative evidence to point in the same
direction:

1. Turkish PPL improves from M1 at the frozen dose, proving that adaptation had a measurable effect.
2. EN->EN eligible-fact accuracy and margins do not collapse.
3. TR->EN candidate access improves over the unadapted M1 with confidence intervals and relation-
   level reporting.
4. The gain is not explained solely by M0 priors, answer-frequency bias, or one relation.
5. TR->TR is interpreted consistently with the localized-answer audit rather than used alone.

The result report must classify each family as `promising`, `inconclusive`, or `not viable` using
the frozen bootstrap/uncertainty procedure. Numeric minimum effect sizes and confidence-interval
rules are part of Phase 109A and must be chosen before training.

### 5.4 Branching after the pilot

- **Qwen promising:** open the bounded Qwen retention intervention in Phase 109C.
- **SmolLM promising, Qwen not promising:** do not run Qwen retention by inertia; prepare a separate
  SmolLM prompt-robustness/eligibility decision.
- **Both promising:** prioritize Qwen retention because it has the stronger all-fact acquisition
  result; retain SmolLM as a low-drift reference.
- **Neither promising:** do not scale. Audit Turkish dose, localization, contamination, and
  candidate evaluation before changing models.

## 6. Phase 109C - Bounded Qwen Retention Intervention

This phase opens only if Phase 109B supports Qwen as a bridge candidate. It is not an open-ended
hyperparameter sweep.

### 6.1 Conditions

Run seed-42 discovery with identical Qwen base model, factual dataset, factual curriculum, update
count, batching, checkpoint schedule, and supervised factual-token exposure:

| Condition | Intended change |
|---|---|
| Q-control | matched factual-only rerun/reference under the current implementation |
| Q-replay | add a frozen clean English anchor stream with next-token replay loss |
| Q-KL | add base-model KL/logit retention on the same anchor stream |

The English anchor source must be disjoint from the English PPL test set and must pass the synthetic
fact contamination audit. Q-replay and Q-KL use the same ordered anchor text and anchor-token
budget. Losses are normalized per supervised token. The exact mixing schedule, KL direction,
temperature, coefficient, anchor budget, and total compute must be frozen in the implementation
manifest before any result is produced.

Only one primary coefficient is allowed per mechanism. A second coefficient may be launched only
if an implementation-scale, outcome-blind loss-magnitude check proves the primary coefficient
numerically invalid; this exception must be documented before factual/PPL evaluation.

### 6.2 Unchanged gates

The retention intervention does not receive easier thresholds:

- exact-prefix >= 90%;
- minimum held-out A/B accuracy, global and per relation >= 80%;
- minimum held-out C/D accuracy, global and per relation >= 80%;
- required robust intersection >= 70%, global and per relation;
- English PPL ratio <= 1.25, with < 1.10 preferred;
- no integrity failure, common-knowledge collapse, or generation degeneration.

Select the earliest retained checkpoint that passes every required gate. If no checkpoint passes,
the condition fails. Do not choose a later checkpoint because it looks subjectively better.

### 6.3 Replication rule

Seed 43 opens only for a seed-42 condition that passes every gate and whose bridge relevance was
established in Phase 109B. A seed-43 failure blocks scale-up and is reported without adding a third
seed post hoc.

## 7. Phase 109D - 500-Subject Intermediate Scale

After a model/recipe passes seed 42, seed 43, and the bridge feasibility decision, train the next
stage at:

```text
500 subjects x 5 relations = 2,500 facts
```

This is the next authorized scale; it is not the final 5,000-subject run. Preserve branch,
relation, object-frequency, and exposure balance. Apply the same frozen M1 gates and report
model-specific and strict eligible sets.

The decision after 500 subjects is evidence-based:

- proceed at 500 subjects if uncertainty is adequate for the planned causal contrasts;
- increase to 1,000 subjects if power or subgroup cell sizes are inadequate but the effect and
  retention profiles remain valid;
- consider 5,000 subjects only if a documented power/scaling analysis shows that the larger scale
  is scientifically necessary and operationally safe.

The historical 5,000-subject/25,000-fact design remains the upper scale contract, not an automatic
next run or a success criterion in itself.

## 8. Phase 109E - Refined M2/M3 Causal Design

The final adaptation experiment retains the original Branch A/B control and adds a lexical
mechanism control. Do not split the limited subject population into three unrelated groups; use
three matched adaptation runs from the same frozen M1 instead.

| Run | Branch A | Branch B | Scientific role |
|---|---|---|---|
| M2-clean | no target entity/fact injection | token-matched neutral/control material | pure generic Turkish adaptation |
| M3-lexical | no target entity/fact injection | subject names and Turkish labels without correct relation binding | entity/lexical alignment |
| M3-fact | no target entity/fact injection | correct Turkish subject--relation--object facts | true factual re-exposure |

M3-lexical must prevent binding leakage through shuffled/counterbalanced object assignments and a
frozen audit. Merely removing the exact fact sentence is insufficient if co-occurrence reveals the
correct binding.

All three runs must start independently from the same frozen M1 weights and the same fresh
optimizer-state policy. They must match:

- adaptation seed;
- generic Turkish documents and order;
- total raw text and model-token budget;
- optimizer updates and learning-rate schedule;
- injection/control token budget;
- evaluation checkpoints;
- storage and retention policy.

Discovery uses one adaptation seed. Three adaptation seeds are required only after the full design
and the discovery implementation pass; they are not launched as an exploratory sweep.

## 9. Frozen Estimands And Outcome Hierarchy

### 9.1 Primary factual access

Use normalized candidate log-probability, top-1 relation-specific ranking, and correct-versus-
distractor margin. Free generation is not the sole or primary measure.

### 9.2 Transfer estimand

For facts never repeated in Turkish, estimate the pre/post change in M2-clean:

```text
TR->EN access at M2-clean minus TR->EN access at frozen M1
```

Report Branch A and B separately to verify pre-treatment parity. TR->TR is a co-reported localized
access outcome, not a substitute for TR->EN.

### 9.3 Lexical-alignment increment

Use the original branch control in a difference-in-differences contrast:

```text
(M3-lexical - M2-clean change for Branch B)
minus
(M3-lexical - M2-clean change for Branch A)
```

### 9.4 True-fact re-exposure increment

Estimate the extra value of the correct Turkish binding beyond lexical exposure:

```text
(M3-fact - M3-lexical change for Branch B)
minus
(M3-fact - M3-lexical change for Branch A)
```

English factual retention, English PPL, Turkish PPL, relation-specific outcomes, and strict-subset
sensitivity accompany every primary contrast.

## 10. Moderator And Subgroup Policy

- English synthetic exposure frequency remains the single planned secondary moderator and must be
  balanced/randomized before training.
- Relation remains a required reporting dimension, not an optional moderator.
- English-like versus Turkish-like names moves to exploratory/appendix analysis.
- Model-specific eligible facts, shared eligible intersection, strict English subset, and all-fact
  intention-to-treat results are all retained; no subset may be invented after Turkish outcomes.

## 11. Execution And Documentation Order

| Step | Deliverable | Opens next step when |
|---:|---|---|
| 1 | Phase 109A corpus/evaluator/config manifest | localization, contamination, budgets, paths, and uncertainty rules are frozen |
| 2 | Turkish bridge pilot | one family is classified promising under the frozen rule |
| 3 | `110_TURKISH_BRIDGE_PILOT_RESULT.md` | bridge results and post-run audit are complete |
| 4 | Qwen retention intervention, only if opened | one seed-42 condition passes every unchanged M1 gate |
| 5 | `111_QWEN_RETENTION_INTERVENTION_RESULT.md` | selected artifact, manifest, hashes, and post-run audit are complete |
| 6 | seed-43 replication | the same condition passes all gates on seed 43 |
| 7 | 500-subject/2,500-fact plan and run | replication and scale manifest pass |
| 8 | power/scaling decision | 500-subject result establishes the required next sample size |
| 9 | three-arm M2/M3 implementation plan | eligible pool and causal contracts are frozen |

Document numbers after 111 are descriptive reservations only; the next actual report must use the
next unused chronological number at creation time.

## 12. HU And Artifact Rules

This plan currently authorizes planning and implementation preparation, not submission. Before
each newly opened coordinated job family:

- read `AGENTS.md`, Document 84, and `ssh-client/README.md`;
- perform one complete family-level home/capacity/inode/path preflight;
- enumerate every sibling job and resolved scratch destination;
- estimate combined checkpoints, caches, corpora, logs, temporary data, and evaluation outputs;
- place every high-volume artifact under `/vol/tmp/yesildau` or `/vol/tmp2/yesildau`;
- inspect queue state, verify `RUNNING`, node/GPU assignment, and immediate stderr;
- report the expected runtime range and return control if the job will take more than five minutes;
- perform one post-run storage audit after the family reaches terminal state;
- preserve selected artifacts with manifests and SHA-256 before any cleanup.

Parallel sibling jobs are allowed after the common preflight proves their combined layout fits.
No output, cache, checkpoint, corpus, or verbose log may be written to HU home.

## 13. Stop Conditions

Stop rather than improvise when:

- exact bridge token budgets or localized answer mappings are not frozen;
- corpus contamination or split overlap is found;
- Qwen does not show a bridge signal but retention training is about to be launched by inertia;
- SmolLM receives a PPL-only intervention despite its active failure being prompt robustness;
- a threshold, eligible subset, checkpoint, coefficient, or dose would be selected after outcomes;
- a 1,000- or 5,000-subject run is proposed without the 500-subject evidence and power decision;
- M2/M3 runs do not start independently from the same M1 or do not match budgets;
- an output path resolves to HU home or storage state conflicts with the recorded preflight.

## 14. Immediate Next Action

Implement Phase 109A locally: audit the existing Turkish Wikipedia configuration and artifacts,
create the frozen Turkish localization/candidate contract, implement the EN->EN/TR->EN/TR->TR
candidate evaluator, define the eligible subsets from existing English evidence, and add exact
numeric low/full adaptation budgets plus HU storage estimates. Run local unit and micro smoke tests.

Do not submit the bridge pilot until those artifacts are reviewed against this document. No M2,
M3, seed-43, 500-subject, 1,000-subject, or 5,000-subject training is active or authorized yet.

## 15. Phase 109A Implementation Progress - 2026-07-19

The first local implementation pass is complete in `transfer-vs-relearning`:

- `data/turkish_bridge.py` builds the frozen bilingual localization registry, the 1,500-probe
  EN->EN/TR->EN/TR->TR registry, and model-specific eligibility tables;
- `evaluate_turkish_bridge.py` performs direction-explicit candidate ranking without conflating
  prompt language and answer language;
- `summarize_turkish_bridge.py` applies paired subject bootstrap and the frozen promotion rule;
- `trwiki_turkish_bridge_v1.yaml` uses the dated 2026-06-01 Turkish Wikipedia dump, enforced
  filtering, Relation V2 contamination inventory, deterministic split, and scratch artifact root;
- `turkish_bridge_adaptation_template.yaml` adds bounded full-sequence adaptation;
- the shared CLM trainer now honors explicit positive `max_steps` and reports that bounded budget
  as the expected optimizer-step count.

The numeric bridge dose is now frozen:

| Endpoint | Optimizer step | Supervised model tokens |
|---|---:|---:|
| low | 32 | 262,144 |
| full | 128 | 1,048,576 |

Each step contains `512 x 2 x 8 = 8,192` supervised tokens on one GPU. Checkpoints at steps 64 and
96 are operational intermediates and cleanup candidates after low/full artifacts are verified.

The generated local smoke contract contains:

- 100 subjects;
- 500 facts;
- 1,500 direction-specific probes;
- 430 unique bilingual candidate objects;
- zero English or Turkish candidate-surface ambiguity under project normalization.

Local verification passed 166 tests with four optional tests skipped. The complete local collection
could not include `test_m1_cross_family.py` because the system Python lacks the separately declared
PyYAML dependency; the new bridge tests, training core, corpus pipeline, and evaluation core all
passed. HU remains the authoritative dependency environment before submission.

The initial read-only HU helper attempts failed because sandboxed DNS could not resolve the HU host,
not because of the HU password. With explicit network access, SSH and the credential helper were
verified and HU was fast-forwarded to commit `92c47dc`. The remote checkout's historical dirty
artifact/symlink state was preserved without reset or cleanup.

Existing hard suites produced the frozen eligibility contract under:

```text
/vol/tmp2/yesildau/turkish_bridge_v1/contracts/v1
```

Manifest SHA-256:

```text
ce3586a4ec3050a72f02ed73c76579c295fe4769845ccadc5692697d0ab649a2
```

On the first invocation, local-shell expansion emptied a remote `$out` variable and the compact
contract files were created in the HU repository root. The exact newly created files (about 580
KiB total) were immediately identified and moved, without overwrite, to the scratch path above.
Verification confirmed that no new bridge contract file remained in the HU repository root.

| Population | Eligible 3/4 C/D | Strict 8/8 |
|---|---:|---:|
| Qwen update 50 | 497/500 | 496/500 |
| SmolLM Document 104 endpoint | 359/500 | 198/500 |
| Shared eligible intersection | 357/500 | reported through model-specific strict sensitivity |

For SmolLM, eligible counts by relation are born-in 76, field-of-study 91, lives-in 76,
profession 42, and works-in-industry 74. This confirms that SmolLM's bridge result must not be
interpreted only through its global average.

The historical Turkish Wikipedia directory contains only placeholder `.gitkeep` files; no dump,
processed documents, clean split, or corpus manifest exists yet. A new six-hour, scratch-only std
partition launcher is prepared in `slurm/prepare_turkish_bridge_corpus.slurm`. It runs the complete
resolve-through-report pipeline and freezes train/validation/manifest hashes. No corpus or training
job has yet been submitted.

The first HU-wide pytest invocation lost its SSH transport after emitting progress and temporarily
left a pytest process; a later process audit confirmed it terminated without manual deletion. The
targeted HU suite exposed only an exact floating-point test assertion (`0.3000000000000001` versus
`0.3`), not a classifier error. Commit `87f0d51` changes that assertion to a tolerance check;
commit `e483f12` adds the corpus launcher. Both await Git push/HU synchronization before the
authoritative targeted suite is rerun.

Remaining Phase 109A gates are:

1. push commits `87f0d51` and `e483f12`, then fast-forward HU and rerun the targeted tests;
2. complete the mandatory corpus-family storage/inode/path/queue preflight;
3. submit and verify the Turkish Wikipedia corpus pipeline, then freeze split hashes;
4. audit that both tokenizers have enough clean blocks for 128 updates;
5. materialize model configs and record combined checkpoint/cache/corpus/evaluation estimates;
6. complete the later coordinated training/evaluation family preflight;
7. only then submit the coordinated bridge model family.

## 16. Corpus Preflight And Submission - 2026-07-19

HU was fast-forwarded to `e483f12a76df2be17b0990c156cf579d88988fc9`. The targeted bridge,
training-core, evaluation-core, and corpus tests passed on HU.

The fast preflight components recorded:

- `/vol/tmp2`: 115 TiB available, 18% used, 3% inode use;
- `/vol/tmp`: 19 TiB available, 87% used, 3% inode use;
- HU home filesystem: 720 GiB globally available, 44% filesystem/inode use;
- `artifacts` resolves to `/vol/tmp/yesildau/transfer-vs-relearning/artifacts`;
- `runs` resolves to `/vol/tmp/yesildau/transfer-vs-relearning/runs`;
- experiment root resolves to `/vol/tmp2/yesildau/turkish_bridge_v1`;
- the new corpus target was absent;
- queue was empty before submission;
- corpus upper reserve: 100 GiB; later complete bridge-family reserve: 350 GiB;
- corpus checkpoint count: zero.

The interactive `du -xsh` lost its SSH transport while traversing many small Torch/Conda files.
Its orphan process was identified and terminated. The mandatory measurement was therefore moved
to a short `std` Slurm preflight whose scratch log records `du -xsk`, rejects home usage above 10
GiB, repeats capacity/inode/path/source checks, and rejects less than 100 GiB free on `/vol/tmp2`.

Submitted jobs:

| Job | Role | Initial state | Dependency |
|---:|---|---|---|
| 410140 | mandatory corpus preflight | RUNNING on `gruenau` | none |
| 410141 | full Turkish Wikipedia corpus pipeline | PENDING | `afterok:410140` |

Slurm moved job 410141 to the `longrun` partition. It cannot start if job 410140 fails. At the last
check, preflight stdout/stderr were still empty because the home traversal was active; no preflight
PASS is claimed yet. Corpus logs, temporary files, dump, processing stages, clean splits, and
manifests all target `/vol/tmp2/yesildau/turkish_bridge_v1`.

## 17. Corpus Preflight Result And Download Corrections - 2026-07-19

Job 410140 completed the safety measurements but failed after them because the installed HU
`df` rejects the combined `-Pk --output=avail` option form. Its dependent corpus job 410141 never
ran and was cancelled after Slurm reported `DependencyNeverSatisfied`. No corpus artifact was
created by either job.

The corrected preflight was submitted as job 410142 and passed completely with empty stderr:

| Check | Recorded result |
|---|---:|
| HU-home regular-file usage | 8,297,052 KiB, approximately 7.91 GiB |
| `/vol/tmp2` available | 123,157,794,816 KiB, approximately 115 TiB |
| `/vol/tmp2` inode use | 3% |
| Corpus destination | `/vol/tmp2/yesildau/turkish_bridge_v1/corpus/trwiki_20260601_bridge_v1` |
| Expected checkpoints | 0 |
| Corpus-family upper reserve | 100 GiB |
| Final status | `passed` |

This is direct evidence that the former approximately 474 GB HU-home incident has not recurred.
The family layout, caches, logs, temporary data, dump, derived documents, and manifests remain on
scratch.

The first dependent corpus attempt, job 410143, stopped before any download because `readlink -f`
returned an empty string for the not-yet-created final corpus directory. The target directory was
then created explicitly under scratch and its resolved path was verified. Job 410144 passed the
path guard but stopped during official Wikimedia metadata resolution with HTTP 403. It downloaded
no dump or corpus intermediate. The cause was an anonymous Python `urllib` request without an
identifying User-Agent, not capacity, inode exhaustion, or artifact placement.

The local correction:

- sends an explicit project-identifying User-Agent for both metadata and dump requests;
- preserves the User-Agent on resumed Range downloads;
- changes the launcher guard to `readlink -m`, which safely resolves a not-yet-created target;
- adds a reusable, version-controlled Slurm preflight rather than another one-off remote command;
- tests both metadata and dump request headers, including resume behavior.

The targeted tests pass, and the full available local suite passes 166 tests with four optional
skips when the separately PyYAML-dependent cross-family file is excluded. The corrected source
must be pushed and fast-forwarded on HU. Because that will be a new submission wave, the complete
reusable preflight must run again; the corpus job may be submitted only with an `afterok`
dependency on that fresh PASS. No bridge training job is active or authorized yet.

The fresh version-controlled preflight ran as job 410145 and passed with empty stderr. It recorded
8,297,108 KiB home usage, the same 123,157,794,816 KiB available on `/vol/tmp2`, 3% scratch inode
use, and the intended scratch resolutions. Its dependent corpus job 410146 therefore entered
`RUNNING` on `gruenau3`, proving that the dependency gate operated correctly. Job 410146 then
stopped during metadata resolution before downloading the dump: the identifying User-Agent
correctly eliminated HTTP 403, exposing HTTP 404 for the configured checksum filename
`sha1sums.txt`.

Official read-only HEAD requests from HU returned HTTP 200 for both the approximately 1.036 GB dump
and the correct date-scoped checksum file:

```text
https://dumps.wikimedia.org/trwiki/20260601/trwiki-20260601-pages-articles.xml.bz2
https://dumps.wikimedia.org/trwiki/20260601/trwiki-20260601-sha1sums.txt
```

The bridge and calibration corpus configs now use the verified date-scoped checksum filename, and
a config regression test freezes the resulting official URL. The available local suite again
passes 166 tests with four optional skips. No dump bytes were downloaded by jobs 410143, 410144,
or 410146. Commit `d35e200` must be pushed and synchronized before another fresh preflight and
dependent corpus submission wave.

Commit `d35e200` was pushed and HU was fast-forwarded to the exact commit. The next coordinated
submission wave is active:

| Job | Role | Verified state |
|---:|---|---|
| 410147 | reusable corpus-family preflight | PASS; stderr empty |
| 410148 | Turkish Wikipedia corpus pipeline | RUNNING on `gruenau3` |

Preflight 410147 again recorded approximately 7.91 GiB in HU home, approximately 115 TiB free on
`/vol/tmp2`, 3% scratch inode use, zero checkpoints, and all intended destinations on scratch. The
`afterok` dependency released job 410148 only after that PASS. Initial corpus evidence shows a
completed official metadata manifest, a completed resolve state, an active download state, and a
growing scratch-only file:

```text
/vol/tmp2/yesildau/turkish_bridge_v1/corpus/trwiki_20260601_bridge_v1/raw/
  trwiki-20260601-pages-articles.xml.bz2.partial
```

At the first check the partial was 5,242,880 bytes and job stderr was empty. This confirms that the
403, missing-target, and checksum-name failures are resolved. Job 410148 must be allowed to finish;
do not submit a duplicate. Inspect it again after approximately 15 minutes, with an initial
expected end-to-end range of 30--90 minutes and a conservative two-hour check window. A post-run
storage audit and split/manifest checksum freeze remain mandatory before the corpus stage is
complete.

At the approximately 12-minute progress check, job 410148 remained `RUNNING` on `gruenau3` with
zero-byte stderr. Official metadata resolution, the 1,035,804,970-byte dump download, and SHA-1
verification had completed. The verified expected SHA-1 is
`1869bcc9a7209962af01b9507cb5cb0da48694da`. Extraction was actively running and had produced a
221,839,796-byte `extracted/documents.jsonl.tmp`. No failure evidence or duplicate submission is
present. The next useful check remains approximately 15--20 minutes later.

## 18. Corpus Pipeline Partial Result And Relation-V2 Contamination Blocker - 2026-07-20

Job 410148 reached terminal state after approximately 2 hours 39 minutes. It did not complete the
full corpus contract. The following expensive stages completed successfully and remain reusable
under the same frozen config and input hashes:

- official metadata resolution and 1,035,804,970-byte dump download;
- official SHA-1 verification against
  `1869bcc9a7209962af01b9507cb5cb0da48694da`;
- extraction, normalization, audit, filtering, and exact deduplication;
- 505,100 input documents, 505,016 kept unique documents, and 84 exact duplicates removed;
- zero extraction failures;
- approximately 11 GiB total scratch corpus tree.

The pipeline stopped at `contamination-preflight` before contamination scanning or split creation:

```text
KeyError: 'university_en'
```

This is a schema-binding defect, not evidence of corpus contamination. The configured canonical
dataset is Relation V2 and contains `field_of_study_*` and `works_in_industry_*`. The contamination
inventory calls `expand_canonical_row`, which iterates the global legacy Relation V1 tuple and
therefore requests `university_*` and `employer_*`. In addition, the Relation V2 gate release
stores its generated acquisition sentences in versioned `acquisition_*` directories rather than
the legacy `output/english_training.jsonl` and `output/turkish_repetition.jsonl` layout expected by
the current inventory builder. Fixing only the missing column would therefore reveal a second
artifact-layout mismatch.

No split or final corpus manifest is frozen, so the corpus stage remains incomplete and bridge
training remains blocked. Do not delete or rebuild the 11 GiB scratch tree: the completed stage
states allow safe reuse after a tested, config-driven Relation V2 contamination inventory fix.

Post-run storage audit job 410149 passed with empty stderr. It recorded 8,297,152 KiB
(approximately 7.91 GiB) in HU home, approximately 115 TiB free and 3% inode use on `/vol/tmp2`,
and unchanged scratch resolutions for `artifacts`, `runs`, and the corpus destination. Two
interactive read-only audit attempts exceeded the SSH helper silence timeout; their exact orphan
`du`/`find` processes were identified and terminated without touching corpus artifacts or other
jobs.

## 19. Relation-V2 Contamination Resume Implementation - 2026-07-20

The local correction is complete without changing the frozen corpus config or its hash. This is
intentional: the already completed download-through-deduplication stage states remain valid, while
the corrected contamination stages will record the new processing Git commit.

The inventory contract now:

- reads the relation list from the dataset release manifest, with schema inference only as a
  backward-compatible fallback;
- expands canonical facts only for those declared relations;
- supports both Relation V1 (`studied_at`, `works_at`) and Relation V2 (`field_of_study`,
  `works_in_industry`) without silently mixing them;
- reads only manifest-declared Relation V2 acquisition `train.jsonl` and `validation.jsonl`
  sources, rather than globbing arbitrary files;
- preserves the legacy manifest-declared English-training/Turkish-repetition sources for V1;
- verifies SHA-256 for every manifest-declared canonical or synthetic-text artifact used;
- rejects duplicate canonical subject IDs, unknown subject IDs, undeclared relations, empty text,
  unknown relation names, missing schema columns, and hash mismatches.

Against the real `relation_v2_gate_v1` release, the corrected builder produced:

| Inventory item | Count |
|---|---:|
| canonical subjects | 5,000 |
| synthetic fact IDs | 25,000 |
| total deduplicated patterns | 106,635 |
| unique manifest-declared exact synthetic sentences | 20,000 |
| exact-NFC automaton states | 907,042 |
| casefold automaton states | 37,543 |
| Turkish-lower automaton states | 37,506 |

A new resume launcher runs only `contamination-preflight`, `scan-contamination`, `split`, and
`report`. It requires the completed deduplicated corpus, refuses to overwrite an existing final
split or corpus manifest, and freezes SHA-256 for train split, validation split, and corpus
manifest. Its paired preflight records home/capacity/inodes/path resolution, the existing corpus
size, zero checkpoints, a 50 GiB incremental upper reserve, and the retention policy.

Targeted corpus/data/bridge tests pass. The complete available local suite passes 169 tests with
four optional skips; the separately PyYAML-dependent cross-family collection remains excluded on
the system Python as previously documented. The code must be committed, pushed, synchronized on
HU, tested in the authoritative environment, and submitted through a fresh `afterok` preflight
wave. No resume job has yet been submitted.

Commit `007b4c8` was pushed and HU was fast-forwarded to the exact commit. The authoritative HU
targeted corpus/data/bridge suite passed. A real-release pre-submission smoke also verified the
manifest hashes and exact frozen inventory counts: 106,635 patterns, 5,000 subjects, 25,000 fact
IDs, and 20,000 unique exact synthetic sentences.

The coordinated resume wave is submitted:

| Job | Role | Initial verified state |
|---:|---|---|
| 411177 | Relation V2 corpus-resume storage preflight | RUNNING on `gruenau`; stderr empty |
| 411178 | contamination-preflight → scan → split → report | PENDING on `afterok:411177` |

Job 411178 cannot start unless preflight 411177 passes. No duplicate resume job should be
submitted. Recheck the preflight/dependency transition after approximately five minutes. Once job
411178 enters `RUNNING`, the expected remaining end-to-end range is approximately 30--90 minutes,
with a conservative two-hour check window.

At the 1 hour 26 minute check, preflight 411177 had passed with home at 8,297,260 KiB,
approximately 115 TiB free and 3% inode use on `/vol/tmp2`, and all paths on scratch. Job 411178
was still `RUNNING` on `gruenau3`; contamination preflight completed in under five seconds with
the exact frozen inventory counts and approximately 400 MiB peak RSS. Stderr remained empty.

The streaming scan exposed a new operational/scientific defect. After processing approximately
209,403 clean documents, `matches.jsonl.tmp` was already approximately 72.3 GB while the clean
document stream was approximately 874 MB. The corpus tree had grown to approximately 78 GB,
exceeding the preflight's 50 GiB incremental estimate, although current scratch capacity remained
safe at approximately 115 TiB free and 3% inode use.

The cause is not one large corpus document. Canonical object patterns are currently stored once per
subject. Shared, generic object surfaces such as industry/field/city labels therefore emit many
duplicate object-only match records for a single surface occurrence. At the observed throughput,
505,016 documents project to approximately 3.5 hours, beyond the job's 3-hour limit, with a final
raw match stream on the order of 170 GB. Job 411178 is therefore likely to time out unless
throughput changes materially. It has not been cancelled or duplicated without user direction.

The required correction is to aggregate identical canonical-object surfaces into one pattern while
preserving the complete sorted `associated_subject_ids` tuple. This matches the existing scanner
data model and keeps subject-object co-occurrence semantics without emitting one redundant row per
subject association. The current job's `.tmp` outputs are not frozen artifacts and must not be
promoted to a final corpus result.

## 20. Shared-Object Aggregation Correction And Scratch Cleanup - 2026-07-20

With user approval to protect HU home and avoid a predictably failing run, job 411178 was cancelled
at approximately 1 hour 30 minutes. It left the queue cleanly. Every large output was confirmed
under `/vol/tmp2/yesildau`; no corpus artifact was written to HU home.

Before cleanup, the exact failed scratch intermediates were resolved and measured:

- `matches.jsonl.tmp`: 74,375,112,366 bytes;
- `clean_documents.jsonl.tmp`: 908,530,290 bytes;
- `removed_documents.jsonl.tmp`: 708,750,972 bytes;
- partial `document_ids.sqlite` plus journal: approximately 23 MB.

These files were reproducible, incomplete scan temporaries rather than selected/frozen scientific
artifacts. They were deleted from scratch only after the job reached terminal state. The completed
1,870,026,239-byte deduplicated corpus and all stage evidence were preserved. The corpus tree
returned from approximately 78 GB to approximately 11 GB.

The local correction now aggregates each identical NFC canonical-object surface into one pattern
with a complete sorted `associated_subject_ids` tuple. The scanner can still test every relevant
subject-object co-occurrence, but an object occurrence is no longer emitted once per associated
subject. A regression test verifies one emitted object match while preserving both subject IDs for
a shared surface.

Real Relation V2 inventory counts after aggregation are:

| Inventory item | Before | After |
|---|---:|---:|
| total patterns | 106,635 | 65,717 |
| canonical-object patterns | 41,631 | 713 |
| subjects | 5,000 | 5,000 |
| fact IDs | 25,000 | 25,000 |
| exact synthetic sentences | 20,000 | 20,000 |

The exact-NFC/casefold/Turkish-lower automata remain valid, and the full available local suite
passes 170 tests with four optional skips. No corrected job has yet been submitted. Commit, push,
HU sync/test, a fresh preflight with the corrected 65,717-pattern count, and one dependent resume
job are required next.

Commit `c9a46fd` was pushed and synchronized on HU. The authoritative targeted suite passed, and
the real release reproduced the corrected frozen counts: 65,717 total patterns, 713 aggregated
object surfaces, 5,000 subjects, 25,000 fact IDs, and 20,000 exact synthetic sentences.

The corrected coordinated wave is submitted:

| Job | Role | Initial verified state |
|---:|---|---|
| 411179 | fresh home/capacity/inode/path preflight | RUNNING on `gruenau`; stderr empty |
| 411180 | corrected contamination → split → report resume | PENDING on `afterok:411179` |

Every high-volume path in both launchers is the absolute scratch namespace
`/vol/tmp2/yesildau/turkish_bridge_v1`. Slurm stdout/stderr, task temporary data, caches, corpus,
match outputs, splits, and reports all stay on scratch. HU home contains only the permitted small
Git checkout/config/metadata. Job 411180 cannot start unless preflight 411179 proves the home and
resolved-path gates. No PASS is claimed until that job finishes; recheck after approximately five
minutes and do not submit a duplicate.

Preflight 411179 passed with empty stderr. It recorded 8,297,312 KiB (approximately 7.91 GiB) in
HU home, approximately 115 TiB free and 3% inode use on `/vol/tmp2`, an approximately 10.0 GiB
existing corpus tree, and all resolved destinations on scratch. Its dependency released corrected
resume job 411180 on `gruenau3`.

At the 26-minute progress check, job 411180 remained `RUNNING` with empty stderr. The scan had
produced approximately 1.77 GB of clean-document temporary output, 3.20 GB of match output, 50 MB
of removed-document output, and a 52 MB SQLite index; the full corpus tree was approximately 15
GB. This directly confirms the aggregation correction: the failed run had produced approximately
72 GB of matches after 86 minutes, whereas the corrected run remains at approximately 3.2 GB and
is progressing faster. No home artifact or capacity/inode issue is present. Recheck in
approximately 10--15 minutes; do not submit a duplicate.

## 21. Corrected Resume Result - Content Complete, Freeze Pending - 2026-07-20

Job 411180 completed with empty stderr. The corrected contamination scan ran from
19:46:36 to 20:13:46 UTC, approximately 27 minutes, followed by split generation and manifest
reporting. Final content counts are:

| Metric | Count |
|---|---:|
| deduplicated input documents | 505,016 |
| clean retained documents | 504,287 |
| removed contaminated documents | 729 |
| retained flag-only documents | 285,303 |
| recorded matches | 1,550,180 |
| train documents | 494,253 |
| validation documents | 10,034 |

The scan explicitly reports `target_retained_verified_full_name_matches: 0`. Final scan artifacts
are approximately 1.86 GB clean documents, 3.34 GB matches, and 53.6 MB removed documents. The
complete corpus tree is approximately 17 GB, entirely under `/vol/tmp2`.

Candidate hashes currently written by the launcher are:

```text
d06ec3b129c040ca98d3a9bf72871fa6117d5cd7102bf6c29eae5b20a834f87d  train_documents.jsonl
15480c1f543acf6df7aac1b2a2ee15fdcb3a544814f0063a181bd7a9cb0ca4f8  validation_documents.jsonl
7fab737c56487cc15dca11bd33ebe0a9e735151d14240c75c2baa4e11dab2f87  corpus_manifest.json
```

These are candidate, not yet final/frozen, hashes. `contamination-preflight` was reused from job
411178, so the corpus manifest embeds the obsolete pre-aggregation 106,635-pattern preflight state
even though the completed scan used commit `c9a46fd` and the corrected 65,717-pattern inventory.
The corpus content and split are not invalidated; only preflight/report provenance must be rerun
and the manifest hash regenerated. The stage framework's `--force` behavior must first be corrected
so an unchanged completed stage can actually rerun.

In addition, Document 109's frozen contract requires deterministic manual inspection of a
contamination sample before the filtered corpus manifest is declared final. Therefore bridge
training remains blocked until:

1. corrected contamination-preflight and corpus report provenance are regenerated;
2. deterministic samples of removed, flag-only, and clean documents are produced and reviewed;
3. the manifest status/finalization decision is recorded explicitly;
4. final split/manifest SHA-256 values are regenerated;
5. post-run audit 411181 passes, including the separate large-home-file check.

Post-run storage audit 411181 is currently running on `gruenau` with empty initial stdout/stderr.
No duplicate audit or corpus job should be submitted.

Post-run audit 411181 subsequently passed with empty stderr. It recorded 8,297,312 KiB
(approximately 7.91 GiB) in HU home, 123,140,274,176 KiB (approximately 115 TiB) available on
`/vol/tmp2`, 3% scratch inode use, and unchanged scratch resolutions for `artifacts`, `runs`, and
the corpus root. No orphan `du` or `find` process remained. The reusable audit launcher did not
include AGENTS.md's separate `find ... -size +500M` home-file listing, so that check remains to be
run in a bounded Slurm audit before operational closure.

On 2026-07-21 the corpus queue was empty, the candidate hashes remained unchanged, and the corpus
tree remained approximately 17 GB under `/vol/tmp2`. The missing AGENTS.md large-home-file check
was submitted as bounded Slurm audit job 411183. It searches only HU home for regular files above
500 MB and writes its stdout/stderr to the Turkish-bridge scratch log directory. At the initial
check it was `RUNNING` on `gruenau` with empty stdout/stderr. Recheck after approximately three to
five minutes; no corpus job is active.

Large-home-file audit 411183 passed with empty stderr and no orphan process. It found exactly three
regular files above 500 MB, all inside the pre-existing `xfer-relearn` Conda environment rather
than any experiment artifact:

| File | Bytes | Modification time |
|---|---:|---|
| `torch/lib/libtorch_cuda.so` | 1,342,901,921 | 2026-06-30 15:58 CEST |
| `nvidia/cublas/lib/libcublasLt.so.12` | 781,053,840 | 2026-06-30 15:57 CEST |
| `nvidia/cudnn/lib/libcudnn_engines_precompiled.so.9` | 555,760,440 | 2026-06-30 15:57 CEST |

These are understood runtime dependencies created weeks before the Turkish-bridge corpus wave;
they are not corpus, checkpoint, cache, evaluation, or log outputs. Combined with the unchanged
approximately 7.91 GiB home usage and scratch-resolved experiment paths, the AGENTS.md post-run
storage audit is complete. No deletion or migration of the active Conda runtime is indicated.

## 22. Compact Provenance And Deterministic Review Implementation - 2026-07-21

The remaining closure work is implemented locally without rerunning download, extraction,
deduplication, contamination scanning, or split generation. The implementation makes four bounded
changes:

1. `--force` now genuinely reruns an unchanged completed stage. Previously the stage framework
   returned a reused state before the caller could force regeneration, which caused the obsolete
   106,635-pattern preflight to remain embedded in the candidate manifest.
2. Corpus manifests exclude the manifest itself, candidate/final checksum files, and the report
   stage's transient running state from their embedded hash/state inventory. This removes
   self-referential and timing-dependent provenance.
3. A deterministic seed-42 review generator selects the 20 lowest
   `SHA-256(seed|bucket|document_id)` documents independently from each frozen bucket: removed,
   retained flag-only, and clean. The compact output includes document excerpts, removal reasons,
   match counts, and bounded match context while binding the sample to the frozen scan hashes.
4. A scratch-only provenance launcher force-regenerates only contamination preflight and report,
   produces the review sample, verifies the corrected 65,717 total patterns and 713 canonical
   object patterns, confirms the observed 729 / 285,303 / 218,984 bucket counts, writes candidate
   checksums, and performs the complete post-run home/capacity/inode/large-file audit.

A dedicated submission-wave preflight records zero checkpoints, approximately 5 GiB of existing
scan data read, less than 1 GiB of new compact output reserve, the resolved home/scratch paths, and
the retention policy. All corpus, review, manifest, task temporary, cache, and Slurm log paths are
under `/vol/tmp2/yesildau/turkish_bridge_v1`; only source and compact Git metadata remain in HU
home. The launcher does not overwrite the historical candidate hash file and writes the refreshed
set as `bridge_split_candidate_sha256.txt`.

The full available local suite passes 174 tests with four optional skips. The new wave has not yet
been submitted. Required order is: commit and push the narrow implementation, synchronize the
exact commit on HU, run the authoritative tests, submit the dedicated provenance preflight, submit
the refresh job with `afterok`, inspect the 60 deterministic samples, record the manual decision,
and only then mark the manifest final and freeze final hashes. Turkish bridge training remains
HOLD until this closure passes. Expected provenance-job runtime is approximately 5--15 minutes,
with a conservative 45-minute Slurm limit; no duplicate or sleep-based monitor is needed.

Commit `2e3837c` was pushed and HU was fast-forwarded to that exact commit without modifying the
intentional artifact-symlink migration state. The authoritative HU test command completed
successfully. The compact closure wave was then submitted exactly once:

| Job | Role | Initial verified state |
|---:|---|---|
| 411188 | home/capacity/inode/path and existing-input preflight | RUNNING on `gruenau`; stderr 0 bytes |
| 411189 | provenance refresh + deterministic review sample + post-run audit | PENDING on `afterok:411188` |

Job 411189 cannot run unless preflight 411188 succeeds. No corpus reconstruction, model training,
or checkpoint writing is part of either job. Recheck after approximately five minutes. Once the
dependent job starts, its expected runtime is 5--15 minutes; do not submit a duplicate.

Both jobs completed successfully with empty stderr. Preflight 411188 recorded home at 8,297,432
KiB, approximately 115 TiB free and 3% inode use on `/vol/tmp2`, and every experiment path on
scratch. Job 411189 regenerated the corrected 65,717-pattern / 713-canonical-object provenance,
created a 416,261-byte deterministic review artifact with 20 removed, 20 flag-only, and 20 clean
documents, regenerated the candidate checksum set, and passed its post-run storage audit. The
corpus remained approximately 17 GB under `/vol/tmp2`; home remained approximately 8.0 GB with
only the three previously understood Conda runtime libraries above 500 MB.

The first manual review found no bucket-assignment failure: every sampled removed document had a
full-synthetic-name removal rule, every flag-only sample contained only object-only flags, and all
20 clean samples had zero matches. The removed names frequently collide with real-world Turkish
or international names. Removing these 729 documents is therefore deliberately conservative, not
evidence that Wikipedia contains the synthetic facts; the loss is approximately 0.14% of the
505,016-document deduplicated corpus.

One compact-evidence defect prevents immediate finalization. Four removed samples had more than
25 total matches, and the review artifact retained only the first 25 stream matches. In those four
cases the decisive full-name/co-occurrence context could be omitted behind frequent object-only
flags even though `removal_rule_ids` correctly recorded the removal. The corpus and split remain
unchanged, but a human-review artifact must always expose decisive evidence. The local generator
is therefore corrected to retain decisive `automatic_decision=remove` matches before filling the
25-item context budget with flag matches, and to record a separate decisive-match count. Tests
cover a decisive match occurring after 30 flag matches. A narrow commit/push and one compact
provenance rerun are required before final review; no scan or split rerun is required.

The decisive-first correction was committed and pushed as `4b72215`, synchronized on HU, and the
authoritative targeted corpus suite passed. A new submission wave was required because this is a
later run with changed review code:

| Job | Role | Initial verified state |
|---:|---|---|
| 411190 | fresh storage/path/input preflight | RUNNING on `gruenau` |
| 411191 | decisive-first provenance/review refresh | PENDING on `afterok:411190` |

The refresh again changes no corpus, scan, or split content. Recheck preflight transition after
approximately five minutes; once 411191 starts, expect approximately 5--15 minutes.

Jobs 411190 and 411191 completed successfully with empty stderr. The refreshed review artifact is
409,329 bytes with SHA-256
`5a1ced0b691cd5849ce0a7fa017e0f1832f3338d8ad177787e0de597f7154a6b`. Its source scan hashes are
unchanged. Final manual inspection passed all frozen structural and semantic checks:

- all 20 removed examples have at least one visible decisive removal match and a full-name rule;
- all 20 flag-only examples have zero decisive matches and only object-only visible rules;
- all 20 clean examples have zero matches;
- no sampled document lacks an ID;
- the one sampled co-occurrence removal and every high-match-count removed document now expose the
  decisive context before ordinary object flags.

The corpus is approved for freezing. To preserve the chronological evidence, finalization is
implemented as an append-only operation: it refuses to overwrite any existing final artifact,
leaves `corpus_manifest.json` and historical candidate checksum files untouched, and creates
`contamination_review_decision_seed42.json`, `corpus_manifest_final.json`, and
`bridge_split_final_sha256.txt`. The final checksum set binds train, validation, review sample,
review decision, and final manifest. A scratch-only Slurm launcher verifies all hashes and repeats
the complete storage audit. Local targeted and full available suites pass. Commit, push, exact HU
sync/test, a fresh preflight, and one finalization job remain before the corpus is operationally
frozen.

Append-only finalization was committed as `ab2e9f3`; the dedicated storage preflight followed as
`8fe6bd5`. Both were pushed, HU was fast-forwarded to exact commit
`8fe6bd5a5b9bb445962707c86ea3249efc4ba281`, and the authoritative targeted suite passed. The
final wave is:

| Job | Role | Initial verified state |
|---:|---|---|
| 411192 | append-only finalization storage/path/non-overwrite preflight | PASS; stderr empty |
| 411193 | create review decision, final manifest, and final checksums | RUNNING on `gruenau`; stderr empty |

Preflight recorded home at 8,297,588 KiB, approximately 115 TiB free and 3% scratch inode use,
zero checkpoints, less than 1 MiB new compact output, and every destination on scratch. Job 411193
will hash the existing train/validation files and may take several minutes. Do not submit a
duplicate; recheck after approximately five minutes.

Job 411193 completed with empty stderr and `status=finalized`. Every entry in the final checksum
file was independently verified `OK`. The final manifest reports `completion_status: finalized`,
`finalized: true`, and finalization commit `8fe6bd5a5b9bb445962707c86ea3249efc4ba281`.
The complete result and hashes are frozen in Document 110. The Turkish corpus component of Phase
109A is closed; the next work is the localized-answer audit, frozen Qwen/SmolLM eligibility sets,
and numeric low/full tokenizer-specific dose contract. No training starts before those three
contracts and their storage estimates are complete.

## 23. Remaining Contract V2 Implementation - 2026-07-21

The remaining localized-answer, eligibility, and numeric dose contracts are implemented as the
append-only `contracts/v2` flow described in Document 111. Existing `contracts/v1` is preserved
but superseded because its large artifacts were correctly on scratch while some embedded source
paths still recorded their pre-migration HU-home names. V2 resolves all model, tokenizer, corpus,
evaluation, output, cache, log, and temporary paths against approved scratch and refuses
overwrite.

The frozen pilot remains Qwen update 50 versus the selected Document 104 SmolLM2 endpoint. V2
asserts the known 497/359 model-specific eligible counts and 357 shared eligible facts, freezes a
canonical-only localized-answer policy and relation-family distractors, and constructs one common
raw-document prefix large enough for both tokenizers to reach the step-128 endpoint without
cycling. Low/full endpoints remain 32/128 optimizer updates (262,144/1,048,576 model tokens), with
four checkpoint directories and one final model expected per model. Local tests, compilation,
shell syntax, and whitespace checks pass. Training remains HOLD until HU materialization and
manifest review pass.
