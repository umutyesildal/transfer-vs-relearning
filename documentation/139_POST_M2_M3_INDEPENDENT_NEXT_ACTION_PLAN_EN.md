# 139 - Post-M2/M3 Independent Next-Action Plan

**Date:** 2026-08-03  
**Language:** English master version  
**Status:** Ready to execute; no new training authorized  
**Scope:** Work that can proceed without supervisor feedback after the completed Qwen M2/M3 gate

## 1. Decision

The Qwen 2,500-fact M2-clean/M3-fact family is complete through its frozen endpoint and primary
gate. No pre-M2/M3 task remains. The immediate project need is evidence closure, not another GPU
experiment.

This plan contains only work that is independent of future supervisor feedback:

1. independent read-only verification of the completed result package;
2. clearly labeled exploratory analysis of the already completed outputs;
3. source-of-truth and milestone documentation repair;
4. selected endpoint artifact preservation and controlled storage closure;
5. preparation of a decision-ready evidence package without recommending an unapproved experiment.

Any supervisor-facing presentation, feedback-dependent interpretation change, new causal arm,
third seed, factual-dose change, scale-up, or amended training contract is outside this document.

## 2. Phase A - independent adversarial verification

Use Document 137 as the frozen external-review handoff. The reviewer must inspect the HU scratch
package read-only and must not submit jobs, rerun slices, alter thresholds, change checkpoints, or
clean artifacts.

The review must independently check:

- that both M2 and M3 arms start independently from the correct seed-specific frozen M1 artifact;
- equal token, block, update, optimizer, scheduler, and endpoint budgets;
- zero target factual exposure in M2-clean;
- Branch-B-only correct factual exposure and exactly four complete cycles in M3-fact;
- fixed `checkpoint-128` evaluation;
- exact registry membership and uniqueness for all 96 endpoint slices;
- exactly 2,500 completed probes per slice and 60,000 probes per state;
- correct connection of each M1 baseline to its sibling M2/M3 contrasts;
- exact reconstruction of state, paired, robust, and Branch-interaction metrics;
- correct subject-bootstrap grouping, sample count, seed, and confidence-interval direction;
- exact application of the two-seed primary gate and five-point EN-to-EN guardrail;
- separation of infrastructure failures from scientific observations;
- manifest, checksum, commit, and output-path provenance;
- contradictions or stronger-than-supported claims in the documentation.

The required deliverable is a numbered independent review report with one of these verdicts:

```text
PASS
PASS WITH CONCERNS
BLOCKED
```

Any discrepancy must be classified as `BLOCKER`, `MAJOR`, `MINOR`, or `NONE`, with the exact
manifest, result path, document, and line or field supporting it. A review prompt is not itself a
review result; this phase closes only when the independent report exists.

## 3. Phase B - post-hoc exploratory mechanism analysis

After or alongside read-only verification, use only the existing aggregate and row-level outputs
to explain the observed seed difference and the large M1-to-M2/M3 Turkish-prompt decline. Do not
change the frozen gate or present exploratory findings as confirmatory.

### 3.1 Required diagnostic questions

1. Which relations contribute to the positive seed-43 interaction and the near-zero seed-42
   interaction?
2. Are the interaction differences concentrated in direct versus QA scaffolding?
3. Are Forms A/B/C/D affected differently?
4. Do robust intersections tell the same story as average top-1 accuracy?
5. Is the M3-fact benefit concentrated by subject frequency, fact frequency, name rarity,
   popularity, or relation difficulty?
6. Does either seed show a small number of high-leverage subjects or relations?
7. Are Branch A changes unexpectedly positive or negative in a way that suppresses or inflates the
   difference-in-differences?
8. Can the M1-to-M2 decline be localized to particular directions, forms, scaffolds, or relations?
9. Are the seed differences already visible in the pre-adaptation bilingual baselines?
10. Do any data-placement, exposure-position, or candidate-set properties differ despite the
    matched contract?

### 3.2 Required outputs

Produce a compact reproducible analysis package containing:

- relation-level M1/M2/M3 state and paired-change tables;
- Branch A/B arm-change and interaction tables for every direction;
- form-by-scaffold interaction tables;
- robust-intersection comparisons;
- subject-level effect distributions and influence/sensitivity summaries;
- frequency, rarity, and popularity stratifications already supported by the frozen metadata;
- a seed-42 versus seed-43 comparison table;
- a concise explanation of what is descriptive, secondary, and post-hoc.

All figures and tables must be generated from frozen outputs without overwriting the primary
analysis directories. The new package must have its own manifest, source hashes, code commit, and
output hash record.

### 3.3 Interpretation boundary

The primary result remains `primary_success_criterion_not_met` regardless of any subgroup or
sensitivity pattern. Exploratory analysis may motivate a later amendment, but it may not select a
new checkpoint, exclude a seed, redefine the primary metric, relax the confidence rule, or relabel
the current family as successful.

## 4. Phase C - documentation and source-of-truth alignment

The chronological evidence must remain append-only, but the project navigation currently contains
stale top-level statements from the pre-M2 period. Complete the following documentation work:

1. update Document 00's date and current-source guidance so that Documents 136, 138, 139, and the
   later independent review are clearly identified as the post-M2/M3 authority;
2. append a dated correction to Document 100 recording that the 2,500-fact M2/M3 family completed
   and that its frozen primary criterion was not met;
3. update `AGENTS.md` only to the extent necessary to direct future agents to the latest completed
   result and independent action plan while preserving Document 100 as historical synthesis;
4. retain Document 130 unchanged as the milestone that was correct through 30 July;
5. use Document 138 as the new post-M2/M3 milestone rather than rewriting Document 130;
6. add the independent review and exploratory analysis reports to Document 00 after they exist;
7. keep every infrastructure failure and methodological correction in the chronological record.

This phase must not rewrite older documents to imply that the M2/M3 result was known earlier or
that previous HOLD decisions were mistaken at the time they were made.

## 5. Phase D - artifact and storage closure

Do not delete or migrate the four endpoint model trees, evaluation package, aggregate outputs, or
manifests until the independent review is complete and any reported blocker is resolved.

After review acceptance:

1. identify the four fixed scientific endpoints:
   `m2_clean_seed42/checkpoint-128`, `m3_fact_seed42/checkpoint-128`,
   `m2_clean_seed43/checkpoint-128`, and `m3_fact_seed43/checkpoint-128`;
2. preserve model-only weights, configuration, tokenizer linkage, training manifest, evaluation
   linkage, and compact result summary for every retained endpoint;
3. generate a canonical manifest and SHA-256 record for each retained model-only endpoint;
4. record exact source and retained sizes plus the retention location;
5. repeat the mandatory HU home, scratch-capacity, inode, resolved-path, and large-home-file audit;
6. obtain separate authorization before copying any new M2/M3 model weights into HU home, because
   the existing exception covers only the two selected Qwen M1 artifacts;
7. only after verification, classify duplicate intermediate checkpoints, optimizer state,
   scheduler state, RNG state, caches, temporary files, and verbose logs as cleanup candidates;
8. request user approval before deleting any selected/frozen model, unique dataset, canonical
   manifest, or non-reproducible scientific output;
9. record every retained artifact and cleanup decision in the next chronological report.

Scratch is not a backup. Compact manifests, hashes, configs, and scientific summaries should be
retained outside volatile result trees according to the approved storage rules. Large output trees
must not be copied into Git.

## 6. Phase E - decision-ready evidence package

After Phases A--D, prepare a compact internal evidence package containing:

- the independent review verdict and issue ledger;
- the frozen primary and retention-gate results;
- the exploratory mechanism-analysis summary;
- the exact claims supported and unsupported by the experiment;
- the endpoint artifact and storage ledger;
- unresolved questions that would require a new scientific decision.

This internal package must remain neutral between accepting the current negative/inconclusive
result and designing a future amendment. It must not pre-authorize M3-lexical, a third seed, a
higher factual dose, another checkpoint, or the 25,000-fact branch.

## 7. Ordered execution

```text
freeze current evidence against mutation
-> independent read-only external review
-> resolve any review blocker without changing the scientific contract
-> exploratory analysis from existing outputs only
-> source-of-truth and milestone documentation alignment
-> endpoint model-only manifest and checksum freeze
-> storage audit and controlled cleanup classification
-> decision-ready internal evidence package
-> stop for a separate scientific decision
```

Read-only review and local documentation preparation may proceed in parallel. Artifact cleanup may
not begin before review completion. No new GPU training or endpoint evaluation belongs to this
plan.

## 8. Completion criteria

This independent action plan is complete only when:

- an independent review report exists and has no unresolved blocker;
- the frozen headline metrics and gate have been independently reproduced or any discrepancy has
  been documented and resolved;
- exploratory analyses are separately labeled and reproducibly packaged;
- Document 00, Document 100, and `AGENTS.md` point future agents to the current post-M2/M3 state;
- all four fixed endpoint artifacts have verified model-only manifests and SHA-256 records, or a
  documented retention decision explains why a state is not retained;
- the mandatory storage audit is complete;
- no selected evidence has been deleted prematurely;
- a neutral decision-ready internal package exists;
- no unapproved experiment has been launched.

## 9. Explicit stop boundary

Stop after the decision-ready package. Future supervisor feedback may authorize a separately
numbered interpretation update, supervisor briefing, or amended experiment plan. Until that
feedback is received and explicitly converted into a frozen contract, do not launch:

- M3-lexical;
- a third seed;
- a changed factual dose;
- treatment-specific checkpoint selection;
- a relaxed or redefined primary gate;
- a new M2/M3 family;
- the 25,000-fact branch as a claimed prerequisite or automatic continuation.

This boundary preserves the completed result while allowing all evidence, analysis,
documentation, and artifact work that does not depend on external scientific direction.

## 10. Execution progress — 3 August 2026

The following progress is recorded without changing the plan or the frozen scientific contract:

- Phase A: the external-review handoff (Document 137) and result template (Document 140) are
  ready; the completed independent verdict is recorded in Document 140a as `PASS WITH CONCERNS`,
  with no blocker or major issue.
- Phase B: completed from frozen aggregate outputs only. The scratch output is
  `/vol/tmp2/yesildau/qwen_m2_m3_v1/analysis_v1/exploratory_20260803T063406Z`; the result is
  documented in Document 142.
- Phase C: completed for the current state. Document 00, Document 100, and `AGENTS.md` point to
  the post-M2/M3 authority and exploratory result; Document 141 remains the analysis plan.
- Phase D: completed as a model-only retention freeze. Document 143 records the four endpoint
  sources, 24/24 source/retained hash checks, retention path, and storage audit. No cleanup or
  deletion was performed; the home `du` timeout remains documented as a minor procedural concern.
- Phase E: the compact decision-ready evidence chain is now assembled across Documents 136, 138,
  140a, 142, and 143. Stop here pending the next independent inspection or a separately approved
  scientific amendment.
