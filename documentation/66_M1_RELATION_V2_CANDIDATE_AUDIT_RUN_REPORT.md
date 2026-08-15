# 66 - M1 Relation V2 Candidate Audit Run Report

Last updated: 2026-07-11

## Status

The pinned SmolLM2 tokenizer and relation-only base-prior audits completed successfully through
V7. Pass counts improved from 62 to 76, 94, 96, 97, 99, and finally 100 under unchanged
thresholds. The candidate gate is passed and the accepted inventory is frozen.

## Repository State

- repository: `synthetic-data-generation`;
- branch: `relation-redesign-v2`;
- candidate draft commit: `85badbb`;
- audit implementation commit: `9a12716`;
- frozen V1 audit commit: `a7e524d`;
- revised V2 candidate commit: `bde7a88`;
- frozen V2 audit commit: `3b441a2`;
- revised V3 candidate commit: `588e7e8`;
- GitHub branch: pushed;
- HU checkout: `/vol/fob-vol6/mi25/yesildau/synthetic-data-generation`;
- HU checkout commit at V2 submission: `bde7a88`.

Existing untracked outputs on the local prior branch were not added to either commit.

## Candidate Draft

- `field_of_study`: 50 sourced bilingual candidates;
- `works_in_industry`: 50 sourced bilingual candidates;
- provenance: UNESCO ISCED-F 2013 and Eurostat NACE Rev. 2.1;
- lexical and provenance tests: passed;
- full local syntheticFacts suite: 47 tests passed;
- HU focused preflight: 5 tests passed under Python 3.11.

## Audit Contract

The audit records, per candidate and language:

- token IDs with the evaluation answer separator;
- token count;
- mean log-probability over three subject-free relation prompts;
- robust prior z-score;
- softmax prior share;
- review flags.

Precommitted review thresholds:

- English token count outside 1-3;
- Turkish token count outside 1-4;
- absolute robust prior z-score above 3.5;
- prior share above 0.10.

No held-out subject/fact result is used by this audit.

## Slurm Run

- job: `391097`;
- node: `gruenau9`;
- GPU: one A100 80GB PCIe;
- initial state: running;
- initial stderr: empty;
- expected average: approximately 2 minutes;
- safe range: 2-5 minutes;
- no local sleep monitor is active.

## Result

- total candidates: 100;
- pass: 62;
- review: 38;
- field English token range: 1-2;
- industry English token range: 1-2;
- field Turkish token range: 1-9;
- industry Turkish token range: 1-10.

The English candidate design is token-efficient. Most failures come from Turkish surfaces
exceeding the precommitted four-token limit.

Prior-specific review candidates include:

- `computer science`: English prior share 0.242;
- `food production`: English prior share 0.175;
- `real estate`: English prior share 0.138;
- `electronics`: Turkish prior share 0.104;
- `telecommunications`: Turkish prior share 0.182;
- `food services`: Turkish prior share 0.113;
- `medicine` and `veterinary science`: extreme low Turkish prior z-scores.

The thresholds are not relaxed after seeing the result. V1 outputs are frozen under
`data/audits/relation_candidates_v2/v1` with hashes and a revision README.

Expected HU outputs:

```text
output/relation_candidates_v2_audit/summary.json
output/relation_candidates_v2_audit/candidate_audit.csv
```

## Gate

Do not implement canonical assignment or regenerate the dataset until the 38 review candidates
are revised, rerun under the same thresholds, and the accepted list is frozen with hashes.

## V2 Rerun

The review candidates were revised using shorter category-level English and Turkish surfaces.
The Turkish audit prompts were also restored to proper Turkish orthography. This is a candidate
and prompt-surface correction, not a relaxation of the tokenizer or base-prior thresholds.

- revision commit: `bde7a88`;
- local focused candidate tests: passed;
- HU focused preflight: 5/5 passed;
- Slurm job: `391098`;
- expected average: approximately 2 minutes;
- safe range: 2-5 minutes;
- no local sleep monitor is active.

The first live status checks could not reach either login node because the local command ran
inside a network-restricted sandbox. A normal SSH probe outside that sandbox subsequently
confirmed that `gruenau10` was healthy and lightly loaded. Job `391098` had completed and
dropped from `squeue`; its output files were written at 18:55 CEST and stderr contained only
the normal model-loading progress bar.

V2 result:

- total candidates: 100;
- pass: 76;
- review: 24;
- improvement over V1: +14 passes and -14 reviews;
- field English token range: 1-2;
- industry English token range: 1-2;
- field Turkish token range: 1-6;
- industry Turkish token range: 1-7.

Remaining review distribution:

- `field_of_study`: 13 candidates;
- `works_in_industry`: 11 candidates;
- Turkish token-count flags: 13;
- Turkish robust-prior-z flags: 7;
- Turkish prior-share flags: 4;
- English prior-share flags: 3;
- English robust-prior-z flags: 1.

Flag counts exceed 24 because some candidates trigger more than one threshold.

The revision substantially reduced Turkish token-length failures, but 24 candidates still
cross at least one unchanged threshold. Remaining flags include Turkish token length, Turkish
prior outliers, and a smaller number of English/Turkish prior-share outliers. V2 was frozen
before the remaining candidates were revised under the same audit contract.

## V3 Rerun

The V2 outputs were frozen under `data/audits/relation_candidates_v2/v2` with their candidate
and output hashes at commit `3b441a2`. The 24 review candidates were revised at commit
`588e7e8`; one adjacent media surface was also changed to preserve within-relation uniqueness.
The source taxonomy/category fields, relation sizes, and all audit thresholds remain unchanged.

Validation and deployment:

- focused local tests: 5/5 passed;
- complete local suite: 47/47 passed;
- candidate CSV SHA-256: `0ed99c1d62a4b1045fe43ec995b094ff1b712efa1cda5897ba3afda8f0ff9026`;
- commits pushed to `origin/relation-redesign-v2`;
- HU checkout: `588e7e8`;
- HU focused preflight: 5/5 passed.

Initial job `391099` failed before audit execution because `MODEL_MANIFEST` was not exported
to Slurm. This is a launch-environment failure and contains no candidate result. Canonical
retry `391100` explicitly pins the existing SmolLM2 model manifest. Its first check showed:

- state: running;
- node: `gruenau9`;
- GPU: one A100 80GB PCIe;
- stdout: healthy startup metadata;
- stderr: no reported error at the initial check;
- expected average: approximately 2 minutes;
- safe range: 2-5 minutes;
- no local sleep monitor is active.

At this point, independent assignment remained blocked pending the canonical V3 result.

## V3 Result And V4 Rerun

Canonical V3 job `391100` completed successfully:

- pass: 94/100;
- review: 6/100;
- Turkish token-count failures: zero;
- English and Turkish token ranges: within the precommitted limits.

V3 was frozen at commit `35e7cf4`. The six remaining base-prior outliers were revised at
commit `54f0397`; local tests passed 47/47 and HU preflight passed 5/5. Manifest-pinned V4
job `391101` completed successfully with 96/100 passes. Its four reviews were `cultural
studies`, Turkish `öğretim`, `agriculture`, and `manufacturing`. The latter two emerged as the
next-highest English prior shares after earlier dominant candidates were removed.

## V5 Rerun

V4 outputs were frozen at commit `b1569be`. The final four V4 review surfaces were revised at
commit `f898f95`, preserving source provenance, relation sizes, and thresholds.

- candidate CSV SHA-256: `f3d5c133e0f7d44c2661c8b78b0833f5454ec5f7bdc80cd5e2349fd3a720f276`;
- local complete suite: 47/47 passed;
- HU checkout: `f898f95`;
- HU focused preflight: 5/5 passed;
- Slurm job: `391102`;
- initial state: running on `gruenau9`;
- GPU: one A100 80GB PCIe;
- expected average: approximately 2 minutes;
- safe range: 2-5 minutes;
- no local sleep monitor is active.

At this stage, independent assignment remained blocked pending V5 and the final inventory
freeze.

## V5 Result And V6 Rerun

V5 job `391102` completed successfully with 97/100 passes. The remaining reviews were
`didactics`, Turkish `antrenman` for `exercise science`, and `agribusiness`. The last candidate
reached English prior share 0.832 and triggered both English prior thresholds. Its three-token
representation appears strongly advantaged by the mean token-log-probability statistic, so V6
returns it to a single-token surface rather than relaxing the threshold.

V5 outputs were frozen at commit `56f1ab0`. The final three candidates were revised at commit
`9499cda`:

- English `didactics` returns to the previously acceptable `teaching`, while Turkish remains
  `didaktik`;
- Turkish `antrenman` becomes `hareket`;
- English `agribusiness` becomes single-token `farming`.

V6 deployment:

- candidate CSV SHA-256: `c2ac751219d6cecaca7e107f91455e08aa7da8c80750f26b1a111ca0aa434b8b`;
- local complete suite: 47/47 passed;
- HU checkout: `9499cda`;
- HU focused preflight: 5/5 passed;
- Slurm job: `391103`;
- initial state: running on `gruenau9`;
- GPU: one A100 80GB PCIe;
- expected average: approximately 2 minutes;
- safe range: 2-5 minutes;
- no local sleep monitor is active.

## V6 Result And V7 Deployment Status

V6 job `391103` completed successfully with 99/100 passes. All `field_of_study` candidates
passed. The only remaining review was English `industrial goods` in `works_in_industry`, with
prior share 0.152 above the unchanged 0.10 limit. No token-length or robust-z check failed.

V6 outputs were frozen at commit `fe0bff5`. The final candidate was changed from two-token
`industrial goods` to single-token `fabrication` at commit `351cae5`:

- candidate CSV SHA-256: `22d06b989dab62e4cfe216fd7788df4b6c5d42bf2ba1f683460b635925fd2060`;
- local complete suite: 47/47 passed;
- commits pushed to `origin/relation-redesign-v2`.

The first HU pull/preflight/Slurm submission command was rejected locally because the Codex
external-action usage limit was reached and did not execute on HU. After explicit continuation
and VPN restoration, deployment completed successfully:

- HU checkout: `351cae5`;
- HU focused preflight: 5/5 passed;
- Slurm job: `391104`;
- initial state: running on `gruenau9`;
- GPU: one A100 80GB PCIe;
- expected average: approximately 2 minutes;
- safe range: 2-5 minutes;
- no local sleep monitor is active.

## V7 Final Result

V7 job `391104` completed successfully:

- pass: 100/100;
- review: 0;
- `field_of_study`: 50/50 accepted;
- `works_in_industry`: 50/50 accepted;
- every token-count, robust-z, and prior-share threshold passed;
- stderr contained only normal model-loading progress.

The accepted V7 audit was frozen at commit `984231e` under
`data/audits/relation_candidates_v2/v7`:

- candidate CSV SHA-256: `22d06b989dab62e4cfe216fd7788df4b6c5d42bf2ba1f683460b635925fd2060`;
- summary SHA-256: `9c01365bd20e37723d8ac4e4fb17231b490872ff88db7415ecd3a1fca274b8fc`;
- candidate-audit SHA-256: `2d2a231b1bee9beab84eb3b4796e4f4dd9411d8290dbcc65bbea4763f1a2a070`;
- complete local suite after freeze: 47/47 passed;
- final freeze commit pushed to `origin/relation-redesign-v2`.

The candidate gate no longer blocks progress. The next authorized stage is independent,
globally and block-balanced assignment followed by the precommitted NMI, Cramer's V, and
conditional-probability dependence audits. Dataset regeneration remains gated on that stage.
