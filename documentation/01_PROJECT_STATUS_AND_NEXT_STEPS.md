# RETIRED DEFAULT STATUS — preserved historical snapshot

> Stop: this July 2026 snapshot is not current authority. Read `current/AGENT_BRIEF.yaml` and, when
> interpretation is needed, `current/STATUS.md`. The historical body remains unchanged below.

# 01 - Project Status And Next Steps

Last updated: 2026-07-11

This document is the working project documentation for the thesis implementation workspace.
It consolidates the current handoff, the Notion export, the exposed thesis plan, repository
commit history, local artifact manifests, and the latest readiness audit.

## Source Of Truth

The handoff document is the current source of truth when it conflicts with older Notion
notes or early design documents.

Older Notion pages are still useful as design history, but some of them describe earlier
versions of the project. In particular, older synthetic-data notes mention a four-relation
dataset with 20,000 facts. The current system uses the final five-relation dataset with
25,000 facts.

Historical `synthetic_v1` relations:

- `profession`
- `born_in`
- `lives_in`
- `studied_at`
- `works_at`

The new `relation_v2` release replaces the final two with `field_of_study` and
`works_in_industry`. Its candidate and independent-assignment gates have passed; the first
10-subject / 50-fact acquisition gate is the active M1 experiment.

## Current M1 Decision: Acquisition Ladder

After the binding-mix evaluation failed the learned-fact gate, the complete documentation
history was re-audited. The historical deployment plan explicitly required a small English
acquisition pilot before full-scale M1. In practice, previous M1 runs trained on all 25,000
facts while the 100-subject subset was used only for evaluation.

The next active M1 direction therefore restores that missing feasibility experiment:

1. 10 subjects / 50 facts;
2. 100 subjects / 500 facts;
3. 500 subjects / 2,500 facts;
4. full 5,000 subjects only if the smaller levels pass.

The subsets are deterministic and nested. Training uses three declarative plus two QA rows
per fact with answer-only loss. MCQ negatives are excluded from the CLM sequence. Each
checkpoint is evaluated with exact-prefix, held-out direct, held-out QA, and robust-overlap
metrics against the full candidate inventories.

The executable plan and precommitted progression gate are recorded in
`48_M1_ACQUISITION_LADDER_PLAN.md`.

Implementation is complete locally at commit `8ee4f17`. All local tests and the real-data
builder smoke test pass. Push, HU pull, and the first 10-subject Slurm launch remain pending
because external command execution was unavailable until 18:38 CEST on 2026-07-10.

### Acquisition Ladder 10-Subject Result

Commit `8ee4f17` was subsequently pushed and pulled on HU. Training job `390992` completed
successfully in 116.6 seconds, but no checkpoint passed the diagnostic progression gate.

Best checkpoint-level results over 50 facts:

- exact-prefix top-1: 12/50
- direct top-1: 1/50
- QA-matched top-1: 11/50
- direct/QA robust overlap: 1/50

The 100-subject level is blocked by the precommitted gate and must not be launched with the
same recipe. Full details are in `49_M1_ACQUISITION_LADDER_10_SUBJECT_REPORT.md`.

### Single-Fact Diagnostic Result

The next diagnostic reduced training to one controlled fact:

```text
Augusta Rodriquez -> born_in -> Van
```

Training job `391013` completed 250 optimizer steps. From checkpoint 25 onward, `Van` ranked
first for both the seen exact prefix and a held-out QA-matched prompt, with large positive
margins. The scaffold-free direct prompt improved only to rank 4 and never reached rank 1.

This proves that the small model can store and retrieve a synthetic fact under the
Question/Answer scaffold. The currently isolated failure is prompt-format transfer to the
direct question. The strict three-view gate failed, so the 10-fact single-relation level was
not launched. Full details are in `51_M1_SINGLE_FACT_DIAGNOSTIC_REPORT.md`.

### Direct-Supervision Single-Fact Result

The matched-budget follow-up added two scaffold-free direct training paraphrases for the
same `Augusta Rodriquez -> born_in -> Van` fact. Training job `391034` completed 252 steps.

From the first saved checkpoint onward:

- exact prefix: rank 1;
- held-out direct: rank 1;
- held-out QA: rank 1.

The direct margin changed from negative in the original control to strongly positive. This
localizes the previous failure to missing direct-format coverage and shows that it is
teachable without changing the fact or model. The next controlled level is ten `born_in`
facts with the same direct-aware format mix, starting again from the base model. Full details
are in `53_M1_SINGLE_FACT_DIRECT_SUPERVISION_REPORT.md`.

The next 10-fact `born_in` direct-aware control is implemented locally at commit `6ea6136`.
All local tests pass, but push/HU launch remain pending because external execution was
unavailable until 2026-07-11 03:23 CEST. The planned gate and current deployment status are
recorded in `54_M1_BORN_IN_10_DIRECT_SUPERVISION_PLAN.md`.

### Ten-Fact Born-In Direct-Supervision Result

Commit `6ea6136` was pushed and pulled on HU. Training job `391048` completed 252 optimizer
steps from the base SmolLM2-360M model. Evaluation jobs `391049` through `391059` completed
without errors.

At checkpoint 25 the model was still partial, but from checkpoint 50 onward:

- exact-prefix top-1: 10/10;
- held-out direct top-1: 10/10;
- held-out QA top-1: 10/10;
- direct/QA overlap: 10/10;
- mean rank in all three views: 1.0.

The precommitted gate passed. The next controlled level is the same seven-row direct-aware
format across all five relations and 50 facts for the same ten subjects. Full details are in
`55_M1_BORN_IN_10_DIRECT_SUPERVISION_REPORT.md`.

### Fifty-Fact All-Relations Direct-Supervision Result

Commit `845c1dc` was pushed and pulled on HU. Training job `391060` completed 252 optimizer
steps from the base model. Evaluation jobs `391061` through `391071` completed successfully.

The gate passed at checkpoint 50. Checkpoint 75 produced the strongest robust result:

- exact-prefix top-1: 50/50;
- held-out direct top-1: 48/50;
- held-out QA top-1: 49/50;
- direct/QA overlap: 48/50.

All five relations learned successfully. The remaining misses are one `lives_in` direct fact
and one `studied_at` robustness fact. The next controlled level is 100 subjects / 500 facts
with the same seven-row format contract and matched effective update budget. Full details are
in `57_M1_ALL_RELATIONS_50_DIRECT_SUPERVISION_REPORT.md`.

### Five-Hundred-Fact Direct-Supervision Interim Status

Commit `bfc8d9b` was pushed and pulled on HU. Training job `391072` completed 252 optimizer
updates over 3,500 rows without OOM. Initial evaluation jobs `391073` through `391075`
completed for checkpoints 25/50/75.

Checkpoint 75 is strongly improved but below the progression gate:

- exact-prefix top-1: 197/500;
- held-out direct top-1: 149/500;
- held-out QA top-1: 143/500;
- direct/QA overlap: 106/500.

Checkpoints 100/125/150 completed as jobs `391076` through `391078`. Checkpoint 150 reached
444 exact, 315 direct, 337 QA, and 266 overlap, so the curve is still improving but remains
below the prompt-robustness gate. Checkpoints 175/200/225 were submitted as jobs `391079`
through `391081`. Their expected parallel wall time is approximately 6 minutes, with a safe
6-8 minute range. Under the current user instruction, no sleep monitor is active. Full
interim details are in `59_M1_500_FACT_DIRECT_SUPERVISION_INTERIM_REPORT.md`.

Checkpoints 175/200/225 subsequently completed. Exact reached 451/500, but checkpoint 225
remained at 320 direct, 337 QA, and 274 overlap, showing a prompt-robustness plateau below the
precommitted gate. Final checkpoints 250/252 were submitted as jobs `391083` and `391084`.
Their expected wall time is approximately 6 minutes, with a safe 6-8 minute range. No sleep
monitor is active.

The Relation V2 500-fact initial evaluation wave completed without failures. Checkpoints 25/50/75
reached exact 21/79/307 and overlap 11/42/176 respectively. Although checkpoint 75 remains below
the 450/400/400/350 gate, the curve is rising strongly. The second wave is submitted as jobs
`391930`, `391931`, and `391932` for checkpoints 100/125/150; all were initially `PENDING`.
Expected parallel runtime is six minutes with a safe six-to-nine minute range. No sleep monitor
is active.

The final exploratory 2,500-fact evaluations completed without failures. Checkpoint 252 is
selected with 2,498 exact, 1,249 direct, 1,293 QA, 958 overlap, and 957 triple; checkpoint 250 has
slightly higher individual direct/QA counts but lower overlap. The proportional gate fails.
Normalized overlap falls from 65.8% at 500 facts to 38.3% at 2,500 facts while exact storage
remains approximately 100%, isolating retrieval/binding interference under scale. The full
25,000-fact recipe is not launched. See
`77_M1_RELATION_V2_2500_FACT_EXPLORATORY_EVALUATION_REPORT.md`.

The exploratory 2,500-fact late wave completed without failures. Checkpoint 225 reaches 2,497
exact, 1,232 direct, 1,294 QA, and 936 overlap, showing near-perfect storage but a prompt-robust
plateau far below the exploratory gate. Final jobs `393015` and `393016` now evaluate checkpoints
250/252; both were initially `PENDING`. Expected parallel runtime is approximately 30 minutes
with a safe 25-45 minute range. No sleep monitor is active.

The exploratory 2,500-fact middle wave completed without failures. Exact rises from 751 at
checkpoint 100 to 1,912 at checkpoint 150, while overlap rises from 378 to 768. Storage has not
saturated and the curve remains positive. Late-wave jobs `393012`, `393013`, and `393014` now
evaluate checkpoints 175/200/225; initial states were running/pending/pending. Expected parallel
runtime is approximately 30 minutes with a safe 25-45 minute range. No sleep monitor is active.

The exploratory 2,500-fact initial evaluation wave completed without failures. Checkpoints
25/50/75 reached exact 43/76/261 and overlap 9/38/134. The curve is still rising but learns much
later than the 500-fact run. Middle-wave jobs `393009`, `393010`, and `393011` now evaluate
checkpoints 100/125/150; all were initially `PENDING`. Expected parallel runtime is approximately
30 minutes with a safe 25-45 minute range. No sleep monitor is active.

The Relation V2 500-fact middle wave completed without failures. Checkpoint 125 reaches perfect
500/500 exact storage but only 375 direct, 367 QA, and 324 overlap; checkpoint 150 is 500/371/369/320.
The strongest middle checkpoint remains 125, with prompt failures concentrated in `lives_in` and
`works_in_industry`. Late-wave jobs `391937`, `391938`, and `391939` now evaluate checkpoints
175/200/225. All were initially `PENDING`; expected parallel runtime is six minutes with a safe
six-to-nine minute range. No sleep monitor is active.

The Relation V2 500-fact late wave completed without failures. Checkpoints 175/200/225 produced
overlap 326/325/328, with checkpoint 225 currently strongest at 500 exact, 377 direct, 375 QA,
and 328 overlap/triple. The final checkpoint-250/252 launcher is ready, but its submit attempt did
not execute because the Codex external-action usage limit was reached; no final job IDs exist yet.
The final gate decision remains pending. No sleep monitor is active.

After the limit cleared, checkpoint-250 and checkpoint-252 evaluations were submitted as jobs
`392003` and `392004`. Both were initially `PENDING`; expected parallel runtime is approximately
six minutes with a safe six-to-nine minute range. No sleep monitor is active.

The final Relation V2 500-fact jobs completed without failures. Checkpoint 250 is selected with
500 exact, 378 direct, 377 QA, and 329 overlap/triple; checkpoint 252 is slightly lower at
500/377/373/328/328. The strict 450/400/400/350 gate therefore fails by 0/22/23/21 facts, blocking
2,500-fact scaling under the current recipe. Compared with historical V1 checkpoint 250, Relation
V2 improves exact by 49, direct by 61, QA by 28, and overlap by 52. All five relations remain
unchanged; the next problem is prompt-robust extraction, not storage. Full results are in
`75_M1_RELATION_V2_500_FACT_EVALUATION_REPORT.md`.

The user explicitly approved an exploratory 500-subject / 2,500-fact scale run despite the
unchanged canonical 500-fact gate failure. This does not retroactively mark that gate as passed.
The new release contains 17,500 direct-aware training rows and preserves all five relations,
including the permanent shared-inventory city pair. It starts from the base model with 36 epochs,
effective batch 2,500, and 252 updates. Full override semantics and frozen hashes are in
`76_M1_RELATION_V2_2500_FACT_EXPLORATORY_SCALE_PLAN.md`.

The exploratory 2,500-fact artifact was integrated at transfer commit `43f801c`. Local and HU
focused suites passed 38/38; nesting, row counts, and all frozen hashes matched. Training job
`392293` is submitted on one A100 80GB with initial state `PENDING`. Expected runtime is
approximately 48 minutes, with a safe 40-70 minute range. No sleep monitor is active.

Exploratory 2,500-fact training job `392293` completed 252/252 updates in 2,590 seconds with
aggregate training loss 0.9441 and final validation loss 0.8760. Initial checkpoint evaluation
jobs are `392728` (checkpoint 25, running), `392729` (checkpoint 50, running), and `392730`
(checkpoint 75, pending). Each covers all 2,500 facts in exact, direct, and QA views. Expected
parallel runtime is approximately 30 minutes with a safe 25-45 minute range. No sleep monitor
is active.

All Relation V2 checkpoint evaluations completed. The aggregate gate first passes at checkpoint
75. Checkpoint 125 is the earliest point on the best stable plateau: 50/50 exact, 45/50 direct,
46/50 QA, 45/50 direct/QA overlap, and 45/50 triple robustness. `profession`, `born_in`,
`field_of_study`, and `works_in_industry` are each 10/10 triple robust; `lives_in` is 5/10.
Four of its five misses retrieve the same subject's birthplace, proving a city-relation binding
failure rather than missing storage. The replacement relations are accepted, but the 500-fact
scale-up is paused under the precommitted relation-specific-failure rule. Full results are in
`69_M1_RELATION_V2_10_SUBJECT_EVALUATION_REPORT.md`.

The city relations will not be removed. Their shared candidate inventory is an intentional hard
binding test. The next controlled run replaces three of seven training rows for each `born_in`
and `lives_in` fact with symmetric paired-city contrast, while preserving all 50 facts, 350-row
budget, held-out prompts, base model, 36 epochs, and 252 updates. Success requires at least 8/10
`lives_in` triple robustness, at most one birthplace-for-residence error, and no meaningful
regression in the other relations. The frozen intervention and gate are in
`70_M1_RELATION_V2_CITY_BINDING_CONTROL_PLAN.md`.

The binding-control implementation was pushed at commit `6d145c2`. Local and HU focused suites
passed 28/28. HU training job `391889` is submitted on one A100 80GB; its initial state is
`PENDING`. Expected runtime after start is approximately two minutes, with a safe two-to-five
minute range. No sleep monitor is active.

All hard-negative evaluations completed and every checkpoint exactly matched the unmodified V2
checkpoint-125 result: 50/45/46/45/45 globally, 10/10 `born_in` triple, 5/10 `lives_in` triple,
and four residence-to-birthplace swaps. The continuation is metric-neutral and discarded. The
project now proceeds with the clean V2 direct-aware recipe at 100 subjects / 500 facts, preserving
all five relations and the 252-update budget. See
`73_M1_RELATION_V2_CITY_HARD_NEGATIVE_EVALUATION_REPORT.md` and
`74_M1_RELATION_V2_500_FACT_SCALE_PLAN.md`.

The nested Relation V2 500-fact release was pushed at synthetic commit `b33aa8b` and transfer
commit `062a90a`. The synthetic suite passed 58/58; local and HU transfer preflight passed 37/37;
artifact hashes and ten-within-one-hundred nesting match exactly. Training job `391918` is
submitted on one A100 80GB with initial state `PENDING`. Based on the matched historical run,
expected runtime is approximately ten minutes with a safe eight-to-fifteen minute range. No
sleep monitor is active.

Relation V2 500-fact training job `391918` completed 252/252 updates in 575.4 seconds with
aggregate training loss 0.6418 and final validation loss 0.3910. Initial checkpoint evaluation
jobs are `391922` (checkpoint 25, running), `391923` (checkpoint 50, running), and `391924`
(checkpoint 75, pending). Each covers exact, direct, and QA views over all 500 facts. Expected
parallel runtime is approximately six minutes, with a safe six-to-nine minute range. No sleep
monitor is active.

Hard-negative ranking job `391903` completed all 35 updates without runtime errors. Nine
checkpoints are under unchanged exact/direct/QA evaluation as jobs `391906` through `391914`.
Their initial state is `PENDING`; expected parallel wall time after scheduling is three to four
minutes, with a safe three-to-seven minute range. No sleep monitor is active.

City-binding control training job `391889` completed 252/252 updates in 115.7 seconds with
aggregate training loss 0.4378 and final validation loss 0.09264. Evaluation jobs `391891`
through `391901` now cover all eleven canonical checkpoints in exact-prefix, held-out direct,
and QA-matched views. Their initial state is `PENDING`; expected parallel runtime after scheduling
is three to four minutes, with a safe three-to-seven minute range. No sleep monitor is active.

All city-binding control evaluations completed, but no checkpoint passed the precommitted gate.
At checkpoint 100, global exact/direct/QA/overlap/triple is 50/45/46/44/44 and `lives_in` is
10/5/7/5/5. Five residence facts select the same subject's birthplace in at least one held-out
view, up from four in the unmodified V2 run, and one reverse residence-for-birthplace QA error
appears. The paired-city CLM intervention is rejected; both city relations remain as the
intentional hard pair. Full results and the next hard-negative binding recommendation are in
`71_M1_RELATION_V2_CITY_BINDING_CONTROL_EVALUATION_REPORT.md`.

The city pair is now frozen as permanent. The next control starts from unmodified Relation V2
checkpoint 125 and performs one low-LR epoch of pairwise ranking over 140 city examples. Every
example compares the correct city only against the same subject's city from the other relation.
This is explicitly an extraction/binding intervention. After evaluation, the project proceeds to
500 facts: a passing hard-negative stage may be retained separately; a failed stage is discarded
and scaling uses the clean V2 CLM recipe. Full precommitted rules are in
`72_M1_RELATION_V2_CITY_HARD_NEGATIVE_PLAN.md`.

The hard-negative implementation was pushed at `b402719`. Local and HU focused suites passed
31/31. HU verified the canonical checkpoint-125 base and the exact 140-example, twenty-fact,
70+70 paired-city contract. Ranking job `391903` is submitted on one A100 80GB with initial
state `PENDING`. Expected runtime after start is one to two minutes, with a safe two-to-five
minute range. No sleep monitor is active.

Final jobs `391083` and `391084` completed without runtime errors. Checkpoint 250 produced
451 exact, 317 direct, 349 QA, and 277 direct/QA overlap. Checkpoint 252 produced 450 exact,
320 direct, 344 QA, and 276 overlap. Exact-prefix storage passes, but the complete 450/400/400/350
gate fails. Checkpoint 250 is retained for analysis because it has the strongest final robust
overlap and QA result. The 2,500-fact run is blocked; the next work is a per-fact triple-robust
audit followed by a controlled 500-fact prompt-transfer intervention focused especially on
`studied_at` and `works_at`.

The checkpoint-250 audit is now complete. The strict three-view subset contains 265/500
facts: 85 profession, 74 lives-in, 53 born-in, 29 studied-at, and 24 works-at. Branch A/B
rates are 52%/54%, and English-like/Turkish-like name rates are 54.4%/51.6%, so neither
branch nor name type explains the failure. Errors instead collapse heavily onto relation-level
candidates: `19 Mayis Universitesi` dominates studied-at failures and `3M` dominates works-at
failures. The frozen membership list and summary are versioned under
`artifacts/analysis/m1_acquisition_500_facts_direct_checkpoint-250`.

The selected remediation is a one-epoch, low-LR candidate-ranking continuation from
checkpoint 250. It uses all seven existing training formats and 15 deterministic balanced
same-relation negatives per prompt. Held-out direct and QA prompts are excluded from training.
The frozen plan is `62_M1_CHECKPOINT_250_RANKING_CONTINUATION_PLAN.md`.

Implementation commit `fb2697e` was pushed and pulled on HU. Initial job `391085` failed
before training because the ranking trainer ignored the manifest tokenizer fallback. Commit
`53ccc10` fixed and tested the loader. Canonical retry `391086` is running on `gruenau9` with
one A100 80GB. Accidental duplicate `391087` was cancelled after detection. Expected average
runtime remains approximately 12 minutes, with a safe 10-20 minute range. No sleep monitor
is active. Live run details are in `63_M1_CHECKPOINT_250_RANKING_CONTINUATION_RUN_REPORT.md`.

Canonical retry `391086` completed 350/350 optimizer updates in 716.26 seconds with aggregate
logged train loss 1.5508. Initial external evaluation jobs `391088`, `391089`, and `391090`
are running for checkpoints 35/70/105. Each job evaluates exact-prefix, held-out direct, and
QA-matched views. Expected parallel wall time is approximately 6 minutes, with a safe 6-9
minute range. No sleep monitor is active.

The checkpoint 35/70/105 evaluation wave completed. Checkpoint 35 was the strongest ranking
continuation result at 452 exact, 321 direct, 343 QA, 277 overlap, and 264 triple robust. This
does not improve the original checkpoint-250 overlap or triple-robust subset. Checkpoints 70
and 105 regressed to 262 and 256 triple-robust facts. Relation audit showed no triple-robust
gain for `studied_at` or `works_at`, and the `19 Mayis Universitesi` / `3M` candidate collapse
remained. Later continuation checkpoints are not being evaluated. The original checkpoint 250
remains the analysis checkpoint, and 2,500-fact scale-up remains blocked.

The next relation redesign is frozen conceptually: replace `studied_at` with
`field_of_study` and `works_at` with `works_in_industry`, preserving five relations.
Candidate concepts are sourced from UNESCO ISCED-F 2013 and Eurostat NACE Rev. 2.1, then
filtered for tokenizer length and base-model prior. Assignments must be independently seeded,
globally and block balanced, and audited with normalized mutual information, Cramer's V, and
conditional-probability checks. Full requirements are in
`65_M1_RELATION_REPLACEMENT_DECISION_AND_DATA_PLAN.md`.

The first sourced draft contains 50 fields and 50 industries on syntheticFacts branch
`relation-redesign-v2`. Commits `85badbb` and `9a12716` were pushed. Local tests passed 47/47,
and HU focused preflight passed 5/5. The first tokenizer/prior audit ran as job `391097` on
`gruenau9` with one A100 80GB. Assignment and regeneration remain blocked until the revised
audit list is accepted.

Audit job `391097` completed: 62/100 candidates passed and 38 require review. English token
lengths are uniformly 1-2, while Turkish surfaces range up to 9-10 tokens and account for most
flags. A smaller set also has extreme base-prior shares. The precommitted thresholds are not
being relaxed. V1 outputs are frozen; Turkish surfaces and prior outliers must be revised and
rerun before assignment.

The V1 audit artifacts were frozen at commit `a7e524d`. Revised candidate and Turkish prompt
surfaces were pushed at commit `bde7a88`, pulled on HU, and passed the focused HU preflight
(5/5). The unchanged V2 audit was submitted as Slurm job `391098`. Expected average runtime is
approximately 2 minutes, with a safe 2-5 minute range and no sleep monitor.

Job `391098` completed successfully and produced 76/100 passing candidates, improving the V1
result by 14 while reducing the review list from 38 to 24. Turkish maximum token lengths fell
from 9/10 to 6/7 for field/industry candidates. The remaining failures include token-length
and base-prior outliers, so thresholds remain unchanged and independent assignment is still
blocked. Initial SSH timeouts were traced to the local network sandbox rather than HU: a
normal connection confirmed `gruenau10` was healthy and the result files were intact.

V2 outputs were frozen at commit `3b441a2`. The remaining review surfaces were revised at
commit `588e7e8`, with the original taxonomy provenance, 50+50 relation sizes, and audit
thresholds preserved. Local tests passed 47/47 and HU focused preflight passed 5/5. Initial
Slurm job `391099` failed before execution because `MODEL_MANIFEST` was not exported. Canonical
retry `391100` explicitly pins the model manifest and is running on `gruenau9` with one A100
80GB. Expected average runtime is approximately 2 minutes, with a safe 2-5 minute range and no
sleep monitor. Assignment remains blocked pending the V3 result.

V3 job `391100` completed with 94/100 passes and no remaining Turkish token-length failures.
Its outputs were frozen at commit `35e7cf4`. Six prior outliers were revised at `54f0397`, and
V4 job `391101` improved the gate to 96/100. V4 was frozen at `b1569be`; the final four review
surfaces were revised at `f898f95`. V5 job `391102` was launched on `gruenau9` with one A100 80GB
after 47/47 local tests and 5/5 HU preflight tests. Expected average is approximately 2 minutes,
with a safe 2-5 minute range and no sleep monitor. Assignment remains blocked pending V5.

V5 job `391102` completed with 97/100 passes. The three remaining candidates included the
three-token `agribusiness`, whose English prior share rose to 0.832 under mean token
log-probability. V5 was frozen at commit `56f1ab0`; the three surfaces were revised at
`9499cda` without changing thresholds. V6 job `391103` is running on `gruenau9` with one A100
80GB after 47/47 local tests and 5/5 HU preflight tests. Expected average is approximately 2
minutes, with a safe 2-5 minute range and no sleep monitor. Assignment remains blocked pending
V6 and the final candidate freeze.

V6 job `391103` completed with 99/100 passes. Every field-of-study candidate passed; the only
remaining review was English `industrial goods` at prior share 0.152. V6 was frozen at commit
`fe0bff5`, and the final surface was revised to `fabrication` at `351cae5`. Local tests passed
47/47 and the commits were pushed. An initial HU deployment attempt did not execute because the
local Codex external-action usage limit was reached. After VPN restoration, HU pulled
`351cae5`, focused preflight passed 5/5, and V7 job `391104` started on `gruenau9` with one A100
80GB. Expected average runtime is approximately 2 minutes, with a safe 2-5 minute range and no
sleep monitor. Assignment remains blocked pending V7.

V7 job `391104` completed with 100/100 passes and an empty review list under unchanged
thresholds. The accepted inventory and audit outputs were frozen and pushed at commit
`984231e`; the final candidate CSV hash is
`22d06b989dab62e4cfe216fd7788df4b6c5d42bf2ba1f683460b635925fd2060`.
The candidate gate is now passed. The next active stage is independent globally/block-balanced
assignment followed by NMI, Cramer's V, and conditional-probability audits; regeneration waits
for that dependence gate.

The assignment/dependence stage is now implemented and passed. Each new candidate occurs
exactly 100 times globally and twice per 100-subject block. The final field-industry table covers
all 2,500 pairs with cell counts from one to three. Primary metrics are: profession-field NMI
0.00337 / Cramer's V 0.03056; profession-industry 0.00396 / 0.03374; field-industry 0.00225 /
0.01852. All conditional and branch/name/rarity/popularity slice gates pass under the frozen
small-sample tolerance. The complete local suite passes 53/53. Full implementation history,
including two rejected assignment designs and the final six-swap repair, is in
`67_M1_RELATION_V2_ASSIGNMENT_AND_DEPENDENCE_AUDIT.md`.

Dataset regeneration is now unblocked, but it must create a new version and preserve historical
`synthetic_v1`. The next training rung remains the 10-subject / 50-fact acquisition gate.

The assignment implementation was pushed at `0da69cf`; cross-Python metric serialization was
stabilized at `e13e182`. HU pulled `e13e182`, passed the verbose 53/53 suite, reran the real
5,000-subject builder, and reproduced the local assignment, summary, and contingency hashes
exactly. Assignment/audit is therefore closed as a reproducible passed stage.

### Relation V2 Dataset Release And First M1 Gate

The isolated V2 generator was released at synthetic-data-generation commit `ae0399b`, with a
CPU regeneration job (`391105`) completing successfully on HU. The generated full corpus has
5,000 profiles, 25,000 facts, 120,500 English rows, and 60,235 Branch-B Turkish rows. The
historical `studied_at` and `works_at` relations are absent. The full raw output is deliberately
not tracked in Git; its manifest freezes all hashes.

The immediately required gate is tracked in full: the same stratified ten subjects, 50 facts,
350 direct-aware English rows (three declarative, two QA, two direct per fact), 50 held-out QA
rows, and 50 exact-prefix probes. HU reproduced the release hashes exactly. The compact gate
package is now being integrated into transfer-vs-relearning for a base-SmolLM2-360M run with
the previously successful 252-update recipe (`1e-4`, 36 epochs, answer-only loss).

The complete release, hashes, and first-run contract are recorded in
`68_M1_RELATION_V2_DATASET_RELEASE_AND_10_SUBJECT_GATE.md`.

Transfer integration commit `c154cb4` packages the compact V2 gate and adds schema-aware field
and industry candidate inventories without changing `synthetic_v1`. HU pulled the commit and
passed 65/65 relevant tests. Training job `391106` is submitted on one A100 80GB with the
matched 350-row / 252-update direct-aware recipe. Its initial queue state is `PENDING`; after it
starts, expected wall time is about two minutes, with a safe two-to-five minute range. No
automatic sleep monitor is active.

Canonical training job `391106` subsequently completed 252/252 updates in 129.6 seconds with
aggregate training loss 0.4452 and final validation loss 0.1082. Timeout-disconnected remote
shells also produced completed duplicate `391107` and pre-training collision failure `391108`;
both are excluded from analysis. Evaluation jobs `391878` through `391888` now cover all eleven
canonical checkpoints in exact-prefix, held-out direct, and QA-matched views. Their initial state
is `PENDING`, expected parallel runtime is two to three minutes after scheduling, and no sleep
monitor is active.

## Active M1-To-M3 Roadmap

The complete gated execution path is now frozen in `60_M1_TO_M3_EXECUTION_ROADMAP.md`.

Immediate order:

1. audit and finalize the field-of-study and industry candidate inventories;
2. implement independent balanced assignment and dependence audits;
3. run the new 10-subject acquisition gate before returning to 500 facts;
4. keep original checkpoint 250 and its frozen 265-fact subset as the comparison anchor;
5. reconsider 500 subjects / 2,500 facts only after the complete gate passes;
6. perform a scale audit before full 25,000-fact M1;
7. freeze M1 artifacts and learned-fact membership;
8. run M2 generic Turkish adaptation without synthetic target facts;
9. run M3 with Branch B Turkish repetitions under the same adaptation budget;
10. compare Branch A transfer-only behavior against Branch B relearning.

SmolLM2-360M remains the model throughout this ladder unless a corrected-recipe capacity
boundary is demonstrated.

## Scientific Goal

The thesis is not simply a Turkish factual-probing benchmark. The core question is whether
facts that become retrievable through Turkish prompts after Turkish adaptation are due to:

- cross-lingual transfer from English parametric knowledge, or
- Turkish-side reaffirmation/relearning because the fact appeared again in Turkish data.

The experiment uses synthetic facts so that fact exposure history can be controlled. Real
facts are avoided as target facts because a pretrained model may already have seen them in
English, Turkish, or another language.

Main research question:

```text
When factual knowledge becomes retrievable in Turkish after Turkish adaptation of a
language model, does this primarily reflect cross-lingual transfer from previously
acquired English knowledge, or reaffirmation/relearning from Turkish adaptation data?
```

## Repository Layout

This workspace contains two main repositories plus documentation and paper folders.

### `syntheticFacts`

Purpose: generate and validate the synthetic biography-style dataset.

Current relation-redesign working state:

- branch: `relation-redesign-v2`
- commit: `bde7a88`
- remote tracking: `origin/relation-redesign-v2`
- status: candidate/audit commits pushed; pre-existing generated outputs remain untracked and
  intentionally excluded

Relevant commit line:

- `99388e5` - merge of `world-update`, including residence relation and final dataset output.
- `5808d87` - adds `lives_in` / residence relation and final dataset output.
- `ebb4628` - deterministic canonical source generation.
- `5773d43` - subject profile world creation data.
- `62a6dcf` - initial synthetic data generator.

### `transfer-vs-relearning`

Purpose: consume the pinned dataset, run evaluation, prepare Turkish corpus data, and later
train/evaluate model states.

Current local state after pull:

- branch: `corpus-update`
- commit: `59a63e378afac19e313d81bf4eca9b17ff8778b1`
- status: code pushed; local workspace also contains the synced `synthetic_v1_bio_qa`
  artifact directory for verification
- remote tracking: `origin/corpus-update`

Relevant commit line:

- `59a63e3` - add memory-safe binding-mix relaunch config.
- `fdfb7ad` - add M1 binding-mix config.
- `4db0688` - add tokenizer fallback for checkpoint eval.
- `a0bbbaf` - add M1 BIO-QA pilot dataset support.
- `638b697` - fix corpus production parser smoke test.
- `e2890f7` - fix TrainingArguments compatibility for M1 training on HU.
- `be23062` - add M1 English fact acquisition training.
- `3080903` - patch corpus lifecycle preflight.
- `c0ed666` - patch corpus pipeline streaming correctness.
- `654257e` - add Turkish Wikipedia corpus Phase 1.
- `5ba61f7` - fix resume metrics and path resolution.
- `73fa953` - patch evaluator batching and resume.
- `e1df785` - initial evaluation scaffold.

## Current Dataset Snapshot

Dataset version:

```text
synthetic_v1
```

Pinned source:

```text
repository: https://github.com/umutyesildal/synthetic-data-generation
branch: main
commit: 99388e5defe4d5a49d21be29a06dba055f4b3453
```

Dataset validation status:

```text
passed
```

Core counts:

- 5,000 canonical subjects
- 25,000 normalized facts
- 2,500 Branch A subjects
- 2,500 Branch B subjects
- 12,500 Branch A facts
- 12,500 Branch B facts
- 104,169 English training rows
- 52,183 Turkish repetition rows
- 25,000 English probe rows
- 25,000 Turkish probe rows

Relation counts:

- `profession`: 5,000
- `born_in`: 5,000
- `lives_in`: 5,000
- `studied_at`: 5,000
- `works_at`: 5,000

Candidate inventory sizes:

- profession: 200
- city: 130
- university: 91
- employer: 241

Controlled metadata distributions:

- `english_like` names: 2,500
- `turkish_like` names: 2,500
- common names: 2,000
- medium-rarity names: 1,750
- rare names: 1,250
- high-popularity subjects: 500
- medium-popularity subjects: 1,500
- low-popularity subjects: 3,000

Important dataset invariant:

Branch assignment is subject-level, not relation-level. This avoids partial leakage where
one fact about a subject is repeated in Turkish while another fact about the same subject
is supposed to remain transfer-only.

## Generated Dataset Files

In `transfer-vs-relearning/artifacts/datasets/synthetic_v1/`:

- `data/canonical_subject_profiles_5000.csv`
- `output/english_training.jsonl`
- `output/turkish_repetition.jsonl`
- `output/probes_en.csv`
- `output/probes_tr.csv`
- `output/canonical_generation_summary.json`
- `output/source_validation_report.json`
- `manifest.json`
- `validation_summary.json`
- `validation_summary.md`
- `pilot_100_subjects.json`

These artifacts are generated/pinned dependencies. They should not be casually edited by
hand.

## Model States

The experimental design uses four main model states.

### M0 - Base Model

Base checkpoint:

```text
openai-community/gpt2
```

Purpose:

- check evaluator correctness,
- estimate chance/bias behavior,
- measure English and Turkish prompt baselines,
- confirm that synthetic facts are not naturally known.

Low accuracy is expected for M0.

### M1 - English Fact Acquisition

M1 is M0 after continued pretraining on English synthetic fact statements only.

Training file:

```text
artifacts/datasets/synthetic_v1/output/english_training.jsonl
```

Critical rule:

Only facts that are demonstrably learned in English by M1 should enter the main transfer
analysis. If a fact was not learned in English, later Turkish failure is not evidence
against transfer.

Current active M1 branch:

- dataset family: `synthetic_v1_binding_mix`
- base model: `HuggingFaceTB/SmolLM2-360M`
- active relaunch config:
  `configs/training/m1_smollm2_360m_english_facts_binding_mix_lr5e-5_ep1_bs2_ga8_gc.yaml`
- completed training job: `389939`
- scheduler note:
  `389721` was cancelled after proving that excluding the now-clean `gruenau10` left no
  immediately eligible A100 node; replacement job `389939` started in one second
- latest live check: `2026-07-10 09:54 CEST`
- training node: `gruenau10`
- training result: complete in 21 minutes 54 seconds; train loss `1.2978754163`, eval loss
  `1.1413165331`, four checkpoints retained
- evaluation status: jobs `389946` through `389953` completed successfully
- best binding-mix English result: direct top1 `0.014`, QA top1 `0.022`, robust overlap
  `3/500`
- binding-mix decision: do not promote; successful CLM optimization did not beat R2 or
  recover a stronger learned-fact gate

Recommended M1 learned-fact gate:

- main gate: English direct prompt, primary mean-logprob score, correct answer is top-1,
  and score margin is positive;
- diagnostic/sensitivity: top-5 is reported but not sufficient to count as learned;
- stricter robustness subset: top-1 under both direct and QA-matched English prompts.

Implementation status as of 2026-07-06:

- M1 training infrastructure has been added and the first pilot job has completed.
- First M1 pilot completed after a compatibility fix:
  - config: `configs/training/m1_gpt2_english_facts_lr5e-5_ep1.yaml`
  - job: `378784`
  - run directory: `runs/training/m1_gpt2_english_facts/20260705T195512Z_m1_gpt2_english_facts_lr5e-5_ep1_1a968945`
  - status: `complete`
  - train loss: `2.815246306270002`
  - eval loss: `2.2544260025024414`
- Checkpoint evaluation completed for `checkpoint-42`, `checkpoint-84`,
  `checkpoint-126`, and `checkpoint-166` under English direct and QA-matched prompts.
- First M1 pilot should not be promoted as M1:
  - best direct top1: `0.024` at `checkpoint-42`
  - best QA-matched top1: `0.024` at `checkpoint-42`
  - robust direct-and-QA top1 overlap: `5/500` at `checkpoint-42`
- Second M1 pilot also should not be promoted as M1:
  - config: `configs/training/m1_gpt2_english_facts_lr1e-4_ep1.yaml`
  - job: `378793`
  - run directory: `runs/training/m1_gpt2_english_facts/20260705T200848Z_m1_gpt2_english_facts_lr1e-4_ep1_20c47712`
  - train loss: `2.5172426901667952`
  - eval loss: `2.0019617080688477`
  - best direct top1: `0.018` at `checkpoint-42`
  - best QA-matched top1: `0.024` at `checkpoint-42`
  - robust direct-and-QA top1 overlap: `5/500` at `checkpoint-42`
- Third M1 pilot also should not be promoted as M1:
  - config: `configs/training/m1_gpt2_english_facts_lr5e-5_ep3.yaml`
  - job: `378802`
  - run directory: `runs/training/m1_gpt2_english_facts/20260705T201752Z_m1_gpt2_english_facts_lr5e-5_ep3_d83f491c`
  - train loss: `2.267362948881096`
  - eval loss: `1.8304280042648315`
  - checkpoint eval jobs: `378803` through `378812`
  - best direct top1: `0.016` at `checkpoint-124`
  - best QA-matched top1: `0.016` at `checkpoint-124`
  - robust direct-and-QA top1 overlap: `3/500` at `checkpoint-124`
  - conclusion: do not promote this pilot as M1
  - implication: the current M1 recipe has failed under three tested variants and likely needs a recipe change instead of another small extension.
- First non-GPT-2 pilot also should not be promoted as M1:
  - model: `HuggingFaceTB/SmolLM2-360M`
  - config: `configs/training/m1_smollm2_360m_english_facts_lr5e-5_ep1.yaml`
  - training job: `379044`
  - run directory: `runs/training/m1_smollm2_360m_english_facts/20260706T064952Z_m1_smollm2_360m_english_facts_lr5e-5_ep1_8f852a51`
  - train loss: `3.069818079118898`
  - eval loss: `2.74118971824646`
  - checkpoint eval jobs: `379060` through `379069`
  - best direct top1: `0.014` at `checkpoint-126`, `checkpoint-168`, and `checkpoint-169`
  - best QA-matched top1: `0.016` at `checkpoint-126`, `checkpoint-168`, and `checkpoint-169`
  - robust direct-and-QA top1 overlap: `3/500`
  - conclusion: do not promote this pilot as M1
  - implication: changing from GPT-2 to SmolLM2-360M did not solve the learned-fact gate; the remaining bottleneck now looks more like recipe/objective weakness than model-loading infrastructure.
- First recipe-change path has now been prepared locally:
  - recipe label: `M1-R1`
  - strategy: stronger repetition plus QA-mixed English acquisition data
  - builder script: `transfer-vs-relearning/scripts/build_m1_recipe_dataset.py`
  - builder module: `transfer-vs-relearning/src/transfer_vs_relearning/training/recipe_data.py`
  - derived train file: `artifacts/datasets/synthetic_v1/output/english_training_m1_r1_qamix_d2_q2.jsonl`
  - derived summary file: `artifacts/datasets/synthetic_v1/output/english_training_m1_r1_qamix_d2_q2_summary.json`
  - derived row count: `416676` from original `104169`
  - declarative rows: `208338`
  - QA rows: `208338`
  - launch config: `configs/training/m1_gpt2_english_facts_r1_qamix_lr5e-5_ep1.yaml`
  - rationale: test whether stronger answer-oriented acquisition signal improves the English learned-fact gate before escalating to a larger model or a new objective.
- First recipe-change run also should not be promoted as M1:
  - recipe label: `M1-R1`
  - config: `configs/training/m1_gpt2_english_facts_r1_qamix_lr5e-5_ep1.yaml`
  - training job: `379169`
  - run directory: `runs/training/m1_gpt2_english_facts_r1_qamix/20260706T073332Z_m1_gpt2_english_facts_r1_qamix_lr5e-5_ep1_5fa91c43`
  - valid checkpoint eval jobs after corrected resubmission: `379279`, `379290`, `379291`, `379292`, `379295`, `379296`, `379300`, `379305`, `379306`, `379307`
  - best direct top1: `0.010`
  - best QA-matched top1: `0.030`
  - best robust direct-and-QA top1 overlap: `5/500`
  - conclusion: do not promote this pilot as M1
  - implication: stronger repetition plus QA-mixed formatting changed QA sensitivity but did not solve direct retrieval, so the next reasonable escalation is bigger model plus stronger recipe.
- Second M1 escalation also should not be promoted as M1:
  - recipe label: `M1-R2`
  - strategy: SmolLM2-360M plus the same QA-mixed R1 dataset
  - launch config: `configs/training/m1_smollm2_360m_english_facts_r1_qamix_lr5e-5_ep1.yaml`
  - rationale: combine the two partially promising changes instead of testing them in isolation again.
  - training job: `379336`
  - training status: complete
  - run directory: `runs/training/m1_smollm2_360m_english_facts_r1_qamix/20260706T082339Z_m1_smollm2_360m_english_facts_r1_qamix_lr5e-5_ep1_62ab81e7`
  - final training metrics: train loss `1.956`, eval loss `1.751`, runtime `300.8s`
  - retained checkpoints: `checkpoint-204`, `checkpoint-408`, `checkpoint-612`, `checkpoint-816`
  - evaluation manifests/configs: prepared under `runs/local_model_manifests/m1_smollm2_360m_english_facts_r1_qamix_lr5e-5_ep1/` and `runs/local_configs/m1_checkpoint_eval_smollm2_360m_r1_qamix_lr5e-5_ep1/`
  - checkpoint evaluation jobs: `380472` through `380479`
  - best direct top1: `0.022`
  - best QA-matched top1: `0.024`
  - best robust direct-and-QA top1 overlap: `5/500`
  - conclusion: do not promote this pilot as M1
  - implication: combining SmolLM2-360M with the stronger QA-mixed recipe improves direct retrieval relative to SmolLM2-alone, but still fails to beat the project-wide M1 gate.
- Third M1 escalation also should not be promoted as M1:
  - recipe label: `M1-R3`
  - strategy: SmolLM2-360M plus the same QA-mixed R1 dataset with `3` epochs
  - launch config: `configs/training/m1_smollm2_360m_english_facts_r1_qamix_lr5e-5_ep3.yaml`
  - training job: `380480`
  - run directory: `runs/training/m1_smollm2_360m_english_facts_r1_qamix/20260707T084629Z_m1_smollm2_360m_english_facts_r1_qamix_lr5e-5_ep3_edc280af`
  - final training metrics: train loss `1.7061`, eval loss `1.5707`, runtime `1454.68s`
  - retained checkpoints: `checkpoint-612`, `checkpoint-1224`, `checkpoint-1836`, `checkpoint-2448`
  - checkpoint evaluation jobs: `380481` through `380488`
  - best direct top1: `0.018`
  - best QA-matched top1: `0.008`
  - best robust direct-and-QA top1 overlap: `2/500`
  - conclusion: do not promote this pilot as M1
  - implication: more exposure on the same SmolLM2 + QA-mixed branch made the learned-fact gate worse, so the next step should not be another same-family exposure increase.
- Fourth M1 escalation has completed training and entered checkpoint evaluation:
  - recipe label: `M1-R4`
  - strategy: SmolLM2-1.7B plus the same QA-mixed R1 dataset with training length reset to `1` epoch
  - launch config: `configs/training/m1_smollm2_1_7b_english_facts_r1_qamix_lr5e-5_ep1.yaml`
  - rationale: test whether the remaining bottleneck is model capacity rather than exposure, after R3 showed that more epochs on SmolLM2-360M made retrieval worse
  - training job: `380489`
  - training status: complete
  - run directory: `runs/training/m1_smollm2_1_7b_english_facts_r1_qamix/20260707T101345Z_m1_smollm2_1_7b_english_facts_r1_qamix_lr5e-5_ep1_2f6d82df`
  - final training metrics: train loss `1.5105`, eval loss `1.3128`, runtime `1975.9s`
  - retained checkpoints: `checkpoint-204`, `checkpoint-408`, `checkpoint-612`, `checkpoint-816`
  - evaluation manifests/configs: prepared under `runs/local_model_manifests/m1_smollm2_1_7b_english_facts_r1_qamix_lr5e-5_ep1/` and `runs/local_configs/m1_checkpoint_eval_smollm2_1_7b_r1_qamix_lr5e-5_ep1/`
  - invalid evaluation submission wave 1: `380490` through `380497`
  - invalid evaluation submission wave 2: `380498` through `380505`, plus `380506` through `380516`
  - cause of invalid eval waves: malformed checkpoint-specific config generation, then fallback to default base-GPT-2 evaluator config
  - valid checkpoint evaluation jobs: `380517` through `380524`
  - best direct top1: `0.024` at `checkpoint-612` and `checkpoint-816`
  - best QA-matched top1: `0.006` at `checkpoint-408`, `checkpoint-612`, and `checkpoint-816`
  - best robust direct-and-QA top1 overlap: `1/500`
  - conclusion: do not promote this pilot as M1
  - implication: the larger model recovered direct retrieval but made prompt-robust fact access even weaker, so the next step should change the objective rather than keep scaling the same QA-mixed CLM recipe
- Selected redesign direction after R4:
  - branch label: `M1-BIO-QA`
  - primary repo for first implementation: `syntheticFacts`
  - recommended working branch: `bio-qa-m1`
  - strategy: generate richer English synthetic biographies plus controlled English QA-style acquisition rows, then train a new M1 family on that mixture
  - rationale: current evidence suggests the bottleneck is extractable subject-centered fact acquisition, not only model scale or exposure
  - design guardrail: keep M1 English-only for target facts so the later M2/M3 transfer-versus-relearning comparison remains scientifically clean
  - implementation status: initial data-generation pass started locally on `bio-qa-m1`
  - first generated outputs:
    - `output/english_biographies.jsonl` with `104169` rows
    - `output/english_qa_train.jsonl` with `31234` rows
    - `output/english_training_m1_bio_qa.jsonl` with `135403` rows
    - `output/english_training_m1_bio_qa_summary.json` with biography-majority mixture metadata
  - pushed synthetic repo commit: `ae0e457`
  - pushed training repo commit for BIO-QA support: `a0bbbaf`
  - first run choice: SmolLM2-360M + `synthetic_v1_bio_qa` + `1` epoch for clean comparison against R2
  - first BIO-QA training job: `380525`
  - training status: complete
  - run directory: `runs/training/m1_smollm2_360m_english_facts_bio_qa/20260707T122837Z_m1_smollm2_360m_english_facts_bio_qa_lr5e-5_ep1_ed208753`
  - final training metrics: train loss `1.347`, eval loss `1.167`, runtime `417.6s`
  - training-only comparison versus R2:
    - train loss improved from `1.956` to `1.347`
    - eval loss improved from `1.751` to `1.167`
    - runtime increased from `300.8s` to `417.6s`
  - checkpoint evaluation jobs: `381760` through `381767`
  - best direct top1: `0.016` at `checkpoint-163`
  - best QA-matched top1: `0.022`
  - best robust direct-and-QA top1 overlap: `3/500`
  - conclusion: do not promote this pilot as M1
  - implication: biography-majority BIO-QA improved the training objective but still did
    not beat R2 on the English learned-fact gate, so the next step should change the
    acquisition objective more directly rather than continuing this recipe unchanged
- Selected next branch after BIO-QA:
  - branch label: `M1-TWO-STAGE`
  - strategy: separate English acquisition from English extraction
  - Stage A: biography-only English acquisition from `english_biographies.jsonl`
  - Stage B: English QA-only continuation from the Stage A final model
  - first runnable Stage A config:
    `configs/training/m1_smollm2_360m_english_biographies_stage_a_lr5e-5_ep1.yaml`
  - helper added for Stage B handoff:
    `scripts/create_local_model_manifest.py`
  - rationale: current evidence suggests CLM fit can improve without improving retrieval,
    so the branch now needs a cleaner acquire-vs-extract separation
  - first Stage A training job: `382768`
  - Stage A training status: complete
  - Stage A run directory:
    `runs/training/m1_smollm2_360m_english_biographies_stage_a/20260707T171129Z_m1_smollm2_360m_english_biographies_stage_a_lr5e-5_ep1_fa548873`
  - Stage A final training metrics: train loss `1.291`, eval loss `1.115`,
    runtime `360.0s`
  - training-only comparison versus BIO-QA single-stage:
    - train loss improved from `1.347` to `1.291`
    - eval loss improved from `1.167` to `1.115`
    - runtime decreased from `417.6s` to `360.0s`
  - Stage A checkpoint evaluation jobs: `382769` through `382776`
  - best Stage A direct top1: `0.014`
  - best Stage A QA-matched top1: `0.014`
  - best Stage A robust direct-and-QA overlap: `3/500`
  - conclusion: do not promote Stage A as M1
  - implication: acquisition-only Stage A improved training loss but further weakened
    retrieval, so the correct next step is Stage B1 QA-only continuation from the Stage A
    final model
  - Stage B1 launch commit: `0f43613`
  - Stage B1 training job: `382777`
  - Stage B1 training status: complete
  - Stage B1 run directory:
    `runs/training/m1_smollm2_360m_english_qa_stage_b1/20260707T173927Z_m1_smollm2_360m_english_qa_stage_b1_lr5e-5_ep1_0c420e40`
  - Stage B1 final training metrics: train loss `2.054`, eval loss `1.951`,
    runtime `66.59s`
  - Stage B1 checkpoint evaluation jobs: `383458`, `383463`, `383468`, `383470`,
    `383471`, `383472`, `383473`, `383474`, `383475`, `383476`
  - best Stage B1 direct top1: `0.012`
  - best Stage B1 QA-matched top1: `0.020`
  - best Stage B1 robust direct-and-QA overlap: `3/500`
  - conclusion: do not promote Stage B1 as M1
  - implication: Stage B1 recovered some QA-side extraction but not enough to cross the
    English gate, so the clean next escalation inside the two-stage branch is Stage B2
    with answer-focused loss
  - Stage B2 launch commit: `04457b0`
  - Stage B2 training job: `383788`
  - Stage B2 training status: complete
  - Stage B2 run directory:
    `runs/training/m1_smollm2_360m_english_qa_stage_b2_answer_only/20260707T181202Z_m1_smollm2_360m_english_qa_stage_b2_answer_only_lr5e-5_ep1_0d974577`
  - Stage B2 final training metrics: train loss `1.328`, eval loss `1.308`,
    runtime `1251s`
  - retained checkpoints: `checkpoint-478`, `checkpoint-956`, `checkpoint-1434`,
    `checkpoint-1912`, `checkpoint-1914`
  - first Stage B2 eval retry fix commit: `4db0688`
  - clean Stage B2 eval retry jobs: `385813` through `385822`
  - best Stage B2 direct top1: `0.012` at `checkpoint-478`
  - best Stage B2 QA-matched top1: `0.012` at `checkpoint-478`
  - best Stage B2 robust direct-and-QA overlap: `2/500`
  - conclusion: do not promote Stage B2 as M1
  - implication: answer-only continuation greatly improved training loss but still failed
    to improve the English learned-fact gate, so the next step should be a larger recipe
    or objective redesign rather than another small same-family extension
  - user-selected follow-up override after Stage B2:
    return once to the original plain M1 recipe family with the small model, but train
    longer at a lower learning rate before abandoning that path entirely
  - selected retry config:
    `configs/training/m1_smollm2_360m_english_facts_lr2e-5_ep5.yaml`
  - return-to-baseline high-exposure training job: `389159`
  - return-to-baseline high-exposure run directory:
    `runs/training/m1_smollm2_360m_english_facts/20260708T182752Z_m1_smollm2_360m_english_facts_lr2e-5_ep5_0b566348`
  - final training metrics: train loss `3.0044`, eval loss `2.7378`, runtime `523.6s`
  - retained checkpoints: `checkpoint-211`, `checkpoint-422`, `checkpoint-633`,
    `checkpoint-844`, `checkpoint-845`
  - training-only interpretation: lower LR plus longer exposure improved loss only
    slightly relative to the 1-epoch plain SmolLM2 baseline, so checkpoint evaluation is
    required before judging this branch
  - checkpoint-eval jobs: `389164` through `389173`
  - best return-to-baseline direct top1: `0.010`
  - best return-to-baseline QA-matched top1: `0.014`
  - best return-to-baseline robust direct-and-QA overlap: `2/500`
  - conclusion: do not promote the high-exposure return-to-baseline branch as M1
  - implication: lower LR plus longer exposure did not beat the original plain SmolLM2
    baseline, so the plain small-model CLM branch is now even less likely to be rescued
    by simply training longer
  - next selected branch after the negative high-exposure retry:
    change the M1 objective itself instead of extending another CLM-only branch
  - selected next branch label: `M1-RANKING`
  - first ranking-objective config:
    `configs/training/m1_smollm2_360m_english_fact_ranking_lr2e-5_ep3.yaml`
  - first ranking-objective rationale:
    train directly on correct-vs-negative answer discrimination for English prompts so the
    optimization target is closer to the actual retrieval metric
  - first ranking-objective pilot job: `389222`
  - first ranking-objective pilot status: complete
  - first ranking-objective pilot config:
    `configs/training/m1_smollm2_360m_english_fact_ranking_lr2e-5_ep1.yaml`
  - first ranking-objective run directory:
    `runs/training/m1_smollm2_360m_english_fact_ranking/20260708T203650Z_m1_smollm2_360m_english_fact_ranking_lr2e-5_ep1_e5698316`
  - first ranking-objective final training metrics:
    train loss `5.3664`, internal eval loss `2.5550`, internal eval top1 `0.1733`,
    runtime `4014.45s`
  - retained checkpoints: `checkpoint-1722`, `checkpoint-3444`, `checkpoint-5166`,
    `checkpoint-6888`, `checkpoint-6889`
  - first ranking-objective eval jobs: `389464` through `389473`
  - best ranking-objective direct top1: `0.014`
  - best ranking-objective QA-matched top1: `0.018`
  - best ranking-objective robust direct-and-QA overlap: `5/500`
  - interpretation: the new objective did not yet improve direct top1, but it recovered
    the stronger robust subset better than the recent CLM-only branches
  - selected ranking follow-up policy:
    keep the ranking objective and the same English BIO-QA candidate world, but lower the
    learning rate and use a medium-length run before opening a larger branch change
  - selected ranking follow-up config:
    `configs/training/m1_smollm2_360m_english_fact_ranking_lr1e-5_ep2.yaml`
  - ranking follow-up launch commit: `7d2b9ab`
  - ranking follow-up training job: `389480`
  - ranking follow-up final state: `complete`
  - ranking follow-up run directory:
    `runs/training/m1_smollm2_360m_english_fact_ranking/20260709T060700Z_m1_smollm2_360m_english_fact_ranking_lr1e-5_ep2_0b3462e1`
  - ranking follow-up final training metrics:
    train loss `6.4562`, internal eval loss `3.2171`, internal eval top1 `0.1422`,
    runtime `3905.52s`
  - ranking follow-up retained checkpoints:
    `checkpoint-3444`, `checkpoint-6888`, `checkpoint-10332`, `checkpoint-13776`,
    `checkpoint-13778`
  - ranking follow-up evaluation jobs: `389515` through `389524`
  - ranking follow-up best direct top1: `0.006`
  - ranking follow-up best QA-matched top1: `0.014`
  - ranking follow-up best robust direct-and-QA overlap: `2/500`
  - conclusion:
    this lower-LR, longer ranking follow-up regressed badly relative to the first ranking
    pilot and should not be promoted as M1
  - implication:
    the ranking objective family still produced the strongest recent positive signal, but
    this exact follow-up recipe is not the right continuation and should not be tuned
    incrementally much further
  - deep-research synthesis:
    the main M1 bottleneck is now judged to be a combined failure of relation binding,
    extraction robustness, and prompt robustness rather than simple undertraining
  - selected next English-side redesign:
    move from first-pass BIO-QA data to a second-generation synthetic regime with
    multi-view biographies, multi-form QA rows, and relation-contrastive support
  - implemented synthetic-data outputs in `syntheticFacts`:
    `english_biographies_multiview.jsonl`, `english_qa_multiform.jsonl`,
    `english_relation_contrastive.jsonl`,
    `english_training_m1_binding_mix.jsonl`,
    `english_training_m1_binding_mix_summary.json`
  - current project meaning:
    the next serious M1 attempt should be based on the new binding-focused dataset family,
    not another small continuation of the existing ranking or CLM branches
  - synced training-repo dataset version:
    `synthetic_v1_binding_mix`
  - synced key train artifact:
    `artifacts/datasets/synthetic_v1_binding_mix/output/english_training_m1_binding_mix.jsonl`
  - pilot file prepared:
    `artifacts/datasets/synthetic_v1_binding_mix/pilot_100_subjects.json`
  - first binding-mix training config:
    `configs/training/m1_smollm2_360m_english_facts_binding_mix_lr5e-5_ep1.yaml`
  - synthetic-data repo launch commit:
    `ab018c0`
  - training-repo launch commit:
    `fdfb7ad`
  - first binding-mix training job:
    `389597`
  - first binding-mix job outcome:
    `389597` failed with CUDA OOM on `gruenau10`
  - memory-safe retry outcome:
    `389719` failed after landing on the same externally contaminated node
  - current clean-node retry:
    job `389721` was cancelled because excluding `gruenau10` caused an artificial 41-hour
    wait while all A100s on `gruenau9` were allocated
  - current clean-node relaunch:
    job `389939`, `COMPLETED` on verified-clean `gruenau10`
  - latest scheduler timing:
    submitted `2026-07-10 08:40:54 CEST`, started one second later
  - current clean-node retry log paths:
    `logs/m1-gpt2-english-389939.out` and `logs/m1-gpt2-english-389939.err`
  - binding-mix checkpoint evaluation jobs:
    `389946` through `389953`, all complete
  - binding-mix English gate result:
    best direct top1 `0.014`, best QA top1 `0.022`, robust overlap `3/500`
  - binding-mix conclusion:
    no checkpoint is promoted as M1; the richer binding-focused data remained weak under
    candidate-ranking retrieval despite low CLM loss
- Training entrypoint: `transfer-vs-relearning/scripts/train_clm.py`
- Generic Slurm wrapper: `transfer-vs-relearning/slurm/train_m1_gpt2_english_facts.slurm`
- Pilot configs:
  - `transfer-vs-relearning/configs/training/m1_gpt2_english_facts_lr5e-5_ep1.yaml`
  - `transfer-vs-relearning/configs/training/m1_gpt2_english_facts_lr1e-4_ep1.yaml`
  - `transfer-vs-relearning/configs/training/m1_gpt2_english_facts_lr5e-5_ep3.yaml`
  - `transfer-vs-relearning/configs/training/m1_smollm2_360m_english_facts_lr5e-5_ep1.yaml`
  - `transfer-vs-relearning/configs/training/m1_smollm2_360m_english_facts_lr5e-5_ep3.yaml`
  - `transfer-vs-relearning/configs/training/m1_smollm2_1_7b_english_facts_r1_qamix_lr5e-5_ep1.yaml`
- Pilot rationale and job protocol: `documentation/07_M1_FACT_ACQUISITION_PLAN.md`

### M2 - Turkish Adaptation Without Fact Exposure

M2 starts from M1 and trains on clean generic Turkish corpus only.

The Turkish corpus must not contain:

- synthetic subject names,
- generated synthetic fact sentences,
- subject IDs,
- fact IDs,
- dataset artifact names,
- synthetic subject-object co-occurrences.

M2 is the main transfer condition.

### M3 - Turkish Adaptation With Branch B Repetition

M3 also starts from the same M1 checkpoint.

Training data:

- same clean generic Turkish corpus,
- plus Turkish repetitions for Branch B facts only.

Branch A remains transfer-only. Branch B becomes the repetition/relearning control.

Budget-matching decision:

Use the cleaner default where M3 replaces some generic Turkish tokens with Branch B
repetition tokens, rather than giving M3 extra total tokens.

Example:

```text
M2 = 25M generic Turkish tokens
M3 = 24M generic Turkish tokens + 1M Branch B Turkish repetition tokens
```

M2 and M3 should match as closely as possible on:

- starting checkpoint,
- total token budget,
- optimizer steps,
- effective batch size,
- learning rate,
- scheduler,
- checkpoint intervals.

## Evaluation System

The evaluator uses candidate ranking rather than free generation.

For each probe, it scores relation-specific candidate answers and ranks them by answer
continuation likelihood.

Primary scoring:

```text
mean answer-token log probability
```

Sensitivity scoring:

```text
total answer-token log probability
```

Why mean-logprob is primary:

Candidate answers have different token lengths. Mean answer-token log probability reduces
the bias toward shorter answers.

Important technical detail:

GPT-2 uses byte-level BPE, so the evaluator tokenizes the full prompt-plus-candidate
string and then masks only answer tokens. Candidate answers are not scored by tokenizing
them separately.

Current prompt configs:

- `configs/evaluation/m0_gpt2_pilot_direct.yaml`
- `configs/evaluation/m0_gpt2_pilot_qa_matched.yaml`

Direct prompt is the primary evaluation. QA-matched prompt is a sensitivity check.

## Relation Binding

`born_in` and `lives_in` intentionally share the same city candidate inventory.

This allows the evaluator to test whether the model has learned:

- only a subject-city association, or
- the correct relation-specific mapping.

Key metrics:

- pairwise relation-binding accuracy,
- `born_in` top-1 accuracy,
- `lives_in` top-1 accuracy,
- swapped-answer rate,
- rank of birthplace under residence probe,
- rank of residence under birthplace probe.

## Pilot Evaluation Status

The 100-subject diagnostic pilot file exists:

```text
artifacts/datasets/synthetic_v1/pilot_100_subjects.json
```

Pilot properties:

- 100 subjects
- 500 facts
- 1,000 probe-language evaluations
- 50 Branch A subjects
- 50 Branch B subjects
- 50 English-like names
- 50 Turkish-like names
- 25 subjects in each Branch x name-type cell

The 100-subject pilot is not a population-weighted estimate. It is a balanced diagnostic
pilot intended to test the pipeline and establish a controlled M0 baseline.

From the handoff, HU already completed a 4-subject M0 micro evaluation:

- run: `runs/evaluation/m0_gpt2_micro_direct/20260704T165220Z_f359d82e`
- expected probes: 40
- successful probes: 40
- failed probes: 0
- model: `openai-community/gpt2`
- resolved revision: `607a30d783dfa663caf39e06633721c8d4cfcd7e`
- GPU: NVIDIA A100 80GB PCIe
- dtype: BF16
- primary top-1 accuracy: 0.0
- primary top-5 accuracy: 0.075

This was a smoke test, not a scientific result. Low M0 accuracy is expected.

## Turkish Corpus Pipeline

The current Turkish adaptation corpus source is Turkish Wikipedia.

Configured dump:

```text
trwiki-20260601-pages-articles.xml.bz2
```

Config:

```text
configs/corpora/trwiki_gpt2_calibration.yaml
```

Safe intended order:

1. configured metadata resolve
2. official metadata resolve
3. contamination matcher preflight
4. download
5. checksum verify
6. production parser smoke
7. extract
8. normalize
9. audit
10. threshold review
11. filter
12. deduplicate
13. contamination scan/removal
14. train/validation split
15. corpus manifest/report

Phase 2 is not implemented yet. It should later add GPT-2 tokenization and deterministic
token-budget subsets such as 10M, 25M, and 50M tokens.

Corpus contamination policy:

- remove-level: synthetic full subject names, synthetic fact sentences, subject IDs,
  fact IDs, dataset artifact names, and subject-own-object co-occurrence;
- flag-only: object-only matches such as city, university, employer, or profession names.

Object-only matches are not removal evidence because many objects are real-world strings.

## HU / HPC Execution Notes

HU path from handoff:

```text
/vol/fob-vol6/mi25/yesildau/transfer-vs-relearning
```

Conda env:

```text
xfer-relearn
```

Expected runtime:

- Python 3.11.15
- Torch 2.7.0+cu128
- CUDA 12.8
- NVIDIA A100 80GB PCIe
- BF16 supported

Slurm script:

```text
slurm/eval_m0_gpt2_pilot.slurm
```

GPU jobs should run through Slurm, not on the login node.

Offline model loading should use:

```text
HF_HUB_OFFLINE=1
TRANSFORMERS_OFFLINE=1
```

Local machine note:

The local checkout currently has the dataset artifacts but not the pinned GPT-2 model
manifest under:

```text
artifacts/models/openai-community__gpt2/model_manifest.json
```

That model manifest exists on HU according to the handoff. Local execution is not the main
target for GPU evaluation.

## Current Readiness Audit

Completed in this workspace:

- pulled `transfer-vs-relearning` to `638b697` on `corpus-update`;
- confirmed both repositories are clean;
- confirmed synthetic dataset artifacts exist locally;
- validated `synthetic_v1`;
- confirmed the 100-subject diagnostic pilot exists;
- checked evaluator and corpus configs;
- ran local focused tests.

Validation command:

```bash
PYTHONPATH=src python3 scripts/validate_dataset.py \
  --dataset-dir artifacts/datasets/synthetic_v1
```

Result:

```text
Validation passed
Facts: 25000
candidates: {'profession': 200, 'city': 130, 'university': 91, 'employer': 241}
```

Focused test command:

```bash
PYTHONPATH=src python3 -m pytest \
  tests/test_data_core.py \
  tests/test_evaluation_core.py \
  tests/test_corpora_phase1.py \
  -q -ra
```

Result:

```text
59 test outcomes reached
3 skipped
```

Skipped locally because this machine lacks optional execution dependencies:

- two Torch-dependent evaluator tests,
- one `mwxml==0.3.8` production parser smoke test.

These should be non-skipped on HU if the environment matches the handoff.

## Immediate Next Steps

The project is past HU readiness and past the first full set of M0 and early M1 pilots.

Current immediate order:

1. Prepare the next post-R3 branch:

   ```bash
   larger model or objective change
   ```

2. Compare English-only direct, QA-matched, and robust-overlap metrics against the best
   already-tested branches:

   ```text
   direct top1 = 0.024
   QA top1 = 0.030
   robust overlap = 5/500
   ```

3. Default next recommendation:

   ```text
   do not spend another run on the same SmolLM2 + QA-mix objective with only more exposure
   ```

4. Confirm GPT-2 model manifest:

   ```bash
   python -m json.tool \
     artifacts/models/openai-community__gpt2/model_manifest.json
   ```

5. Run 100-subject M0 direct evaluation via Slurm:

   ```bash
   sbatch slurm/eval_m0_gpt2_pilot.slurm
   ```

6. After completion, summarize and inspect:

   ```bash
   python scripts/summarize_evaluation.py \
     --run-dir runs/evaluation/m0_gpt2_pilot/<run_id>
   ```

7. Then run 100-subject M0 QA-matched sensitivity evaluation.

## Proposed Agent Roles

The project should use specialized agents, but all agents must treat this document,
the handoff, and repository state as shared context.

### Experiment Lead Agent

Owns scientific consistency.

Responsibilities:

- preserve M0/M1/M2/M3 semantics;
- maintain Branch A/B interpretation;
- decide metric gates and analysis subsets;
- prevent uncontrolled scope drift.

### Dataset And Evaluator Agent

Owns synthetic dataset use and candidate-ranking evaluation.

Responsibilities:

- validate `synthetic_v1`;
- inspect probe and candidate inventories;
- run/summarize M0/M1/M2/M3 evaluations;
- maintain M1 learned-fact gates;
- track relation-binding metrics.

### Corpus And Contamination Agent

Owns Turkish corpus pipeline.

Responsibilities:

- run official Wikimedia metadata resolve;
- run matcher preflight;
- download and verify trwiki dump;
- extract/normalize/audit/filter/deduplicate;
- perform contamination removal;
- prepare clean train/validation splits.

### HPC And Slurm Ops Agent

Owns HU execution reliability.

Responsibilities:

- confirm conda/GPU/runtime environment;
- submit Slurm jobs;
- monitor logs;
- handle resume;
- keep local artifacts out of commits.

### Documentation Agent

Owns documentation cleanup.

Responsibilities:

- convert old Notion notes into current docs;
- mark historical/stale notes clearly;
- maintain this status document;
- document commands, outputs, run IDs, and decisions after each milestone.

## Commit Hygiene

Do not commit local operational artifacts unless explicitly intended.

Usually do not commit:

- `artifacts/models/openai-community__gpt2/`
- `artifacts/datasets/synthetic_v1.incomplete_*/`
- ad hoc pilot files except agreed stable selections
- `runs/evaluation/`
- `runs/local_configs/`
- `logs/`
- `src/transfer_vs_relearning.egg-info/`

Commit code, tests, configs, and curated documentation changes deliberately.

## Current Milestone Summary

The project currently has:

- a finalized 5,000-subject / 25,000-fact synthetic dataset;
- deterministic Branch A/B design;
- English-only acquisition data and Branch B Turkish repetition data;
- English and Turkish probe files;
- pinned dataset manifest and validation summaries;
- candidate-ranking evaluator with batched scoring;
- relation-binding analysis for `born_in` vs `lives_in`;
- 100-subject diagnostic pilot selection;
- Turkish Wikipedia corpus Phase 1 pipeline;
- HU setup and 4-subject M0 micro evaluation completed per handoff;
- local repo updated to the latest handoff commit.

The next major milestone is the 100-subject M0 direct baseline evaluation on HU.
