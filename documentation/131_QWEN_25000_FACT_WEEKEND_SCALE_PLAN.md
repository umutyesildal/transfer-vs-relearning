# 131 — Qwen 25,000-Fact Weekend Canonical-Scale Plan

**Date:** 30 July 2026  
**Status:** Thursday implementation authorized; no HU training submission authorized yet  
**Scientific role:** One-seed upper-canonical-scale validation of the replicated 2,500-fact Qwen
recipe. This run does not replace the two frozen 2,500-fact M1 artifacts merely by being larger.

## 1. Decision and scope

The user authorizes preparation of one Qwen2.5-1.5B run over the complete Relation V2 population:

- 5,000 subjects, balanced as 2,500 Branch A and 2,500 Branch B;
- five relations and 25,000 English facts;
- seed/data-seed 42 only;
- one A100-80GB, one training submission, no parallel seed and no automatic evaluation wave;
- default Slurm priority; no artificial `--nice` penalty and no elevated priority/QoS request;
- target start Friday evening and training completion before Monday morning.

The run is exploratory upper-scale evidence. A passing result may motivate a separately authorized
seed-43 replication or may be retained as a scale-robustness analysis. A failure does not erase the
replicated 2,500-fact Qwen result in Documents 127 and 130.

“One chance” means one scientific training run. Outcome-free preparation, CPU audits, a bounded
one-update GPU capacity smoke, and tested checkpoint resume support are technical validity gates,
not additional scientific runs. A continuation from the same run's latest verified checkpoint is
permitted after interruption; it must not change data, order, seed, optimizer state, config, or
output identity. No duplicate fresh run is permitted.

## 2. Why the run uses one A100

The passing 2,500-fact recipe is a single-GPU contract. A second A100 would require distributed
training changes and a new parity validation for gradient averaging, effective batch size,
checkpoint state, and resume behavior. It would not make the existing code automatically twice as
fast. One A100 therefore gives the closest comparison to the replicated evidence and imposes the
smallest scheduler footprint. The job must not request `--exclusive`. It uses the account's
ordinary scheduler priority: the run is important enough not to self-demote, but it does not seek
an elevated QoS or bypass other users.

## 3. Frozen scientific contract

| Item | Frozen value |
|---|---|
| Model | Pinned local `Qwen/Qwen2.5-1.5B` base manifest used by the 2,500-fact runs |
| Population | All 5,000 canonical Relation V2 subjects; 25,000 facts |
| Curriculum | Per fact: 3 canonical declaratives + Form A direct/QA + Form B direct/QA |
| Held out | Forms C and D receive zero training exposure |
| Factual rows | 175,000 train rows; 25,000 canonical monitoring candidates before alignment |
| Loss | Answer-only causal LM, `supervise_eos: false` |
| Retention | Clean-English replay, coefficient 0.5, maximum 64 Qwen tokens |
| LR/scheduler | `5e-5`, constant-with-warmup, warmup ratio 0.02, weight decay 0 |
| Epochs | 36 |
| Physical batch | 50 |
| Gradient accumulation | 500 |
| Effective factual batch | 25,000 rows |
| Optimizer budget | 7 updates/epoch × 36 = 252 updates |
| Seed | model/data seed 42/42 |
| Checkpoints | Steps 25, 50, 75, 100, 125, 150, 175, 200, 225, 250, and 252 |
| Hardware | One A100-80GB; world size 1; BF16 and gradient checkpointing |

Keeping gradient accumulation at 50 would create approximately 2,520 optimizer updates and would
change both scale and learning intensity. It is explicitly forbidden by this plan.

### 3.1 Replay alignment

WikiText-2 does not provide 175,000 unique clean training rows under the existing filter. The
upper-scale run therefore reuses the already frozen 17,500-row Qwen scale-probe clean-English
anchor in ten deterministic cycles, after re-auditing every selected anchor against all 5,000
synthetic subject surfaces. This preserves the factual-to-replay row ratio and the exact 2,500-fact
anchor distribution while making the repeated exposure explicit. The 2,301-row frozen validation
anchor remains paired with a deterministic 2,301-row factual monitoring subset. Anchor cycling,
order, source hashes, and full-population contamination results must be recorded in the dataset
manifest before training.

## 4. Precommitted evaluation contract

Evaluation is a separate later wave and is not automatically started during the weekend. It must
cover every retained checkpoint before the selected checkpoint is named:

- 25,000 exact-prefix probes;
- 200,000 Form A/B/C/D × direct/QA hard probes;
- eight-cell fact intersection globally, by relation and by branch;
- same-subject relation forced choice;
- nested 100-subject and 500-subject retention subsets;
- frozen WikiText-2 PPL and generic completion integrity.

The earliest checkpoint passing every gate is selected. Gates remain percentage-equivalent to the
replicated intermediate-scale contract:

- exact primary at least 90%;
- every relation/form/scaffold cell at least 80%;
- eight-cell robust global and every relation at least 70%;
- PPL/base ratio at most 1.25;
- zero lexical-empty output and zero synthetic-subject intrusion under the corrected integrity
  rule.

No threshold, checkpoint subset, or metric may be changed after results are inspected. Because the
full evaluation is roughly ten times the 2,500-fact probe volume, its compute and scheduler plan
must be frozen separately after training.

## 5. Thursday implementation checklist

1. Implement an append-only 5,000-subject dataset builder that verifies the declared Relation V2
   source files and hashes.
2. Assert 5,000 unique subjects, 25,000 facts, 175,000 rows, seven representations per fact,
   balanced branches, five complete relations, and zero C/D exposure.
3. Materialize a 200,000-row frozen probe registry and nested 100/500 membership lists.
4. Implement deterministic ten-cycle replay construction and full-subject contamination audit.
5. Add a new 25k config with physical batch 50, accumulation 500, and exactly 252 updates.
6. Add tested same-run checkpoint resume support; a resume must preserve config and input hashes.
7. Add dedicated preparation, preflight, smoke, training, and post-run-audit launchers. Historical
   launchers are references only.
8. Run local tests and syntax/config/hash audits. Do not connect to HU or submit work on Thursday.

## 6. Friday go/no-go contract

The family may be submitted only when all of the following pass immediately before the wave:

- HU home is below the administrator-approved 30 GB ceiling with no unexplained increase; the
  verified selected-Qwen durability copy is an explained, allowlisted component;
- `df -h` and `df -i` show sufficient `/vol/tmp2` capacity and inodes;
- at least 300 GiB is reserved in the written estimate and at least 1 TiB is actually free;
- every dataset, run, cache, log, temporary, and evaluation path resolves under
  `/vol/tmp2/yesildau`;
- the unique canonical output root is absent and all input manifests/hashes match;
- 11 checkpoints at the observed approximately 8.9 GiB/run-checkpoint footprint fit with safety
  margin; expected training tree is approximately 100–130 GiB;
- the exact HU Git commit passes targeted tests;
- the one-update A100 smoke passes without OOM, non-finite loss, or checkpoint/resume error;
- fresh queue inspection finds no unacceptable contention and one A100 can be requested without
  `--exclusive`;
- user approval is recorded after the final go/no-go report.

No artificial scratch reservation file will be created. Shared scratch cannot be guaranteed
against all future external writes, so the plan uses a large observed headroom and stops if that
headroom is absent.

## 7. Weekend operating window

- Target submission: Friday 18:00 Europe/Berlin.
- Hard useful-start cutoff: Friday 19:30 Europe/Berlin.
- If allocation begins after the cutoff, the launcher exits before model load and before creating
  the scientific run directory.
- Requested wall time: 60 hours.
- Expected training time from the measured 2,500-fact runs: approximately 45–55 hours.
- Allocation-time GPU guard must see no foreign compute process on the allocated visible GPU.
- No second seed, duplicate job, or evaluation array is launched while training is active.
- After terminal state, run one family storage audit and preserve every checkpoint until the
  separately frozen evaluation selects an artifact.

The scheduler remains the authority for allocation. Weekend or holiday expectations are not a
go/no-go signal; current queue, allocation, device-process, capacity, and inode evidence are.

## 8. Stop conditions

Stop before training if any source hash differs, the dataset/probe/replay audit fails, the output
root already exists, a high-volume path resolves to HU home, free capacity/inodes are inadequate,
the GPU is contaminated, the smoke/resume test fails, the job cannot start before the cutoff, or
the local documentation and HU state disagree materially.

Stop and ask the user before deleting or overwriting any selected/frozen artifact, unique dataset,
canonical manifest, or non-reproducible result. No cleanup is authorized by this plan.

## 9. Thursday implementation status — 30 July 2026

The local implementation is complete enough for the Thursday gate; no HU connection or Slurm
submission was made.

- A dedicated 5,000-subject builder reconstructs the frozen Relation V2 curriculum from the
  tracked canonical profile table and verifies its hash against the tracked release manifest.
- The builder verifies all row, fact, relation, branch, representation, nested-100/nested-500,
  and C/D non-exposure invariants. Its declarative rows are regression-checked against the frozen
  passing 500-subject package.
- It creates 175,000 factual rows, 25,000 exact-prefix probes, 200,000 hard probes, and the
  ten-cycle 175,000-row replay alignment. The replay source manifest and both replay file hashes
  must match before materialization, followed by a 5,000-subject surface audit.
- The new training config freezes `batch=50`, `gradient_accumulation=500`, `world_size=1`, and
  exactly 252 optimizer updates.
- The CLM entrypoint now supports same-run resume only when config, dataset, validation, replay,
  and base-model manifest hashes match. It selects the latest checkpoint containing Trainer,
  optimizer, and scheduler state and rejects completed, moved, or mismatched runs.
- After a resume, custom mean replay-loss diagnostics are explicitly labeled as covering only the
  post-resume segment; they are not misreported as full-run aggregates. Checkpoint selection does
  not use Trainer or replay aggregate loss.
- Dedicated preparation preflight, materialization, exact one-update replay smoke plus real
  Trainer resume rehearsal, fresh training preflight, 60-hour one-A100 launcher, start-cutoff
  guard, clean-GPU guard, and post-run storage audit are present.

A full local materialization using a temporary clean 17,500/2,301-row anchor fixture passed and
occupied approximately 195 MiB. Deterministic non-anchor hashes from that audit were:

- factual train: `014f88ee984dc7e0b64b01197b409808f76250c6f81e174056c0ddfb9fc47e98`;
- exact-prefix registry: `3f3dc9e0e868deed00692e6ee270b84547d6c2fa845654c347e3fa1a6e4cd497`;
- hard-probe registry: `3653db0916397e8cfbb5d42a27f76c706b97c1f466329d483768b7e6369e57f1`.

Targeted tests pass with three optional Torch-dependent skips, all new shell launchers pass
`bash -n`, Python sources pass bytecode compilation, and `git diff --check` is clean. A temporary
PyYAML dependency layer then allowed the full local suite to pass with seven optional skips; the
temporary dependency directory was removed after verification. The exact HU `xfer-relearn`
environment must still run the authoritative suite before preparation or GPU submission.

The implementation is committed and pushed on `corpus-update` as `55a7a7b` (`Prepare guarded Qwen
25k canonical scale run`). At the user's instruction, both the smoke and main job use the account's
normal Slurm priority; the earlier self-demotion proposal was removed. They still request only one
A100 and never request `--exclusive`.

HU synchronization was attempted only after the push, but no remote state was accepted as
verified: DNS resolved `gruenau10.informatik.hu-berlin.de` to `141.20.21.44`, while a direct
five-second SSH banner test timed out. No HU Git pull, test, preflight, or Slurm submission is
therefore claimed, and no job ID exists. The next action after HU network/VPN access returns is
exact-commit synchronization, the authoritative HU suite, and the preparation-only preflight.
Training still requires a later fresh go/no-go preflight and explicit user approval.

### 9.1 HU synchronization and login-node test correction

The general login host `gruenau.informatik.hu-berlin.de` was subsequently reachable even though
direct SSH to `gruenau9/10` remained unavailable. The HU checkout fast-forwarded without reset to
exact commit `55a7a7bd84b4d852677813f819ae38d9bf9eb6e2`. Existing artifact/runs migration state was
preserved: the tracked checkout shows historical deletions because `artifacts` and `runs` are now
untracked symlinks resolving to `/vol/tmp/yesildau/transfer-vs-relearning/...`; the required
Relation V2 manifest and canonical profile file remain readable through that approved scratch
target.

Running the full suite on the login CPU stopped during collection because the environment's NumPy
was compiled with an `X86_V2` baseline that the login machine does not support. This is an
environment/hardware mismatch, not a test failure and not permission to alter the frozen Conda
environment. A dedicated zero-GPU `std` Slurm test launcher is added so the authoritative suite
and launcher syntax checks run on the same supported compute class used by project preflights.

### 9.2 HU tests, preparation preflight, and frozen dataset materialization

The dedicated zero-GPU test job `439439` ran on `gruenau6` and completed successfully. The full
pytest suite reached 100%, the launcher syntax checks passed, stdout recorded
`status=passed commit=93ac926da700d411d4d5cc6c93aa165a84afd79f`, and stderr was empty. This
replaces the unsupported login-CPU attempt as the authoritative HU test result for the initial
implementation.

Preparation preflight job `439440` passed before materialization. It recorded HU home use of
approximately 8.0 GiB, approximately 113 TiB available on `/vol/tmp2`, 3% inode use there, a
300-GiB family reserve estimate, 11 planned checkpoints, and scratch-resolved output and cache
paths. Its manifest is retained at
`/vol/tmp2/yesildau/qwen_canonical_25k_seed42_v1/preflight/prepare_439440.json`.

Preparation job `439444` then completed on `gruenau6` in 4 minutes 56 seconds with zero-byte
stderr. The frozen dataset manifest reports:

- 5,000 subjects, 25,000 facts, and balanced 2,500/2,500 Branch A/B membership;
- 175,000 factual training rows, with 25,000 rows in each of seven frozen representations;
- 35,000 training rows for each of the five relations and zero Form C/D training exposure;
- 25,000 exact-prefix probes and 200,000 four-form/scaffold probes;
- 175,000 replay rows from ten deterministic cycles and 2,301 validation rows;
- zero full-population synthetic-subject surface hits in the replay source.

The materialized factual-train, exact-prefix, and hard-probe hashes respectively equal
`014f88ee984dc7e0b64b01197b409808f76250c6f81e174056c0ddfb9fc47e98`,
`3f3dc9e0e868deed00692e6ee270b84547d6c2fa845654c347e3fa1a6e4cd497`, and
`3653db0916397e8cfbb5d42a27f76c706b97c1f466329d483768b7e6369e57f1`, matching the independent
local materialization. The frozen manifest is
`/vol/tmp2/yesildau/qwen_canonical_25k_seed42_v1/prepared/dataset_manifest.json`.

### 9.3 First A100 smoke allocation and environmental stop

Immediately before the smoke submission, Slurm reported all three `gruenau9` A100s allocated and
only one of the three `gruenau10` A100s allocated. Because two A100s therefore appeared available,
one normal-priority, non-exclusive smoke job was submitted as `439445`. Slurm assigned one A100 on
`gruenau10`, with `Nice=0` and normal QoS.

The allocation-time guard found an already-running foreign Python process using approximately
8.67 GiB on the visible assigned GPU. It exited with code 3 before the base model was loaded and
before any optimizer update. This is not a scientific run or an OOM/training failure. A node-level
read-only audit showed that all three physical `gruenau10` A100s contained active processes even
though Slurm accounted for only one allocated GPU; three long-running processes belonged to
another user and began on 28 or 29 July. The remaining A100 node, `gruenau9`, was fully allocated
to job `439304`, whose declared time limit extends to 3 August. No process was killed and no second
smoke was submitted into this contaminated state.

The failed attempt's empty canonical directory was preserved, not deleted, as
`/vol/tmp2/yesildau/qwen_canonical_25k_seed42_v1/smoke_failed_gpu_contamination_439445`. The smoke
launcher was corrected so the clean-GPU guard runs before creation of the canonical `smoke/`
directory. A regression test fixes this ordering. The correction is committed and pushed as
`eee224433692c82141744909da3ef36d573787a7`; HU was fast-forwarded to that exact commit, the shell
syntax check passed, and the focused HU test file passed four tests.

The remaining Thursday gate is therefore a clean one-update A100 smoke plus the real Trainer
checkpoint-resume rehearsal. The main 25,000-fact training job remains unsubmitted. It still
requires a successfully frozen smoke report, a fresh Friday training preflight no more than one
hour old, an acceptable live queue/device audit, and explicit user approval.

### 9.4 Late-Thursday storage correction, exact-commit tests, and queued clean smoke

After Ralf Moritz explicitly authorized current HU-home use below 30 GB and the approximately
6.2 GB selected-Qwen durability copy, the 25,000-fact preparation/training preflights and post-run
audit were corrected from the former conservative 10-GiB check to the administrator-approved
30-GB ceiling. The post-run large-file audit now freezes its comparison baseline immediately
before training, so the separately authorized selected-model backup is allowlisted by provenance
rather than misclassified as a new training output. High-volume outputs, caches, logs, datasets,
and ordinary checkpoints remain restricted to scratch. The correction is committed and pushed as
`15279338b6c28756485916078ef867fa3fca42df`; the HU checkout was fast-forwarded to that exact
commit.

Authoritative compute-node test job `439526` then completed on `gruenau3` in 3 minutes 13 seconds.
All 234 tests passed, stdout recorded
`status=passed commit=15279338b6c28756485916078ef867fa3fca42df`, exit code was zero, and stderr
was empty. A prior submission attempt, job `439520`, stopped before test execution because the
required `EXPECTED_COMMIT` environment variable was omitted; it is an invocation error rather
than a code/test failure and was not retried more than once.

Normal-priority, non-exclusive A100 smoke job `439521` is submitted and pending for resources.
While pending it holds no GPU, CPU, or memory allocation. At the recorded queue audit, all three
`gruenau9` A100s remained allocated to job `439304`. On `gruenau10`, a long CPU/RAM job held 64 of
72 CPUs and 500 GB, two A100s contained foreign processes outside the visible Slurm GPU
allocation, and the third physical A100 was clean. The canonical `smoke/` path remains absent;
only the preserved environmental-stop directory from job `439445` exists. The main training job
remains unsubmitted and may not be submitted until `439521` produces the frozen successful resume
report, the Friday preflight is no more than one hour old, live contention is acceptable, the
start cutoff can be met, and the user gives the final explicit go/no-go approval.

### 9.5 Slurm memory-placement correction and contamination-safe queue state

Inspection of pending smoke `439521` exposed a Slurm placement mismatch: the launcher requested
eight CPUs and `64G`, while the `gpu` partition caps memory at 8,000 MB per requested CPU. Because
`64G` is 65,536 MB, Slurm computed `MinCPUsNode=9` even though `NumCPUs=8`. The job therefore could
not use the exactly eight unallocated CPUs on `gruenau10`. This affected both the smoke and main
launcher and would have made the Friday plan dependent on an unrecorded ninth CPU.

The smoke and main launchers now request `60G`, preserving the precommitted eight-CPU, one-A100,
normal-priority, non-exclusive design while satisfying the partition rule. Dataset, model,
physical batch, accumulation, update count, evaluation, and retention contracts are unchanged.
A regression test freezes both resource directives. Commit
`6969a5037b1787d73e16611afb4ca3af3972979a` is pushed and exact on HU; compute-node test job
`439541` passed all 234 tests on that commit with zero exit status and empty stderr.

The obsolete, never-allocated `64G` smoke `439521` was cancelled after the replacement passed.
Corrected smoke `439542` immediately received eight CPUs, 60 GiB, and one `gruenau10` A100, proving
the placement fix (`MinCPUsNode=8`). Slurm assigned physical GPU 0, where the allocation guard
found a foreign Python process using approximately 8.7 GiB. The guard again exited with code 3 in
two seconds before model load, update, or canonical-directory creation. This is a second recorded
environmental stop, not a training failure.

Because ordinary users cannot safely select the physically clean GPU 2 while Slurm considers all
three `gruenau10` A100s available, the active clean smoke is job `439543`, constrained to
`gruenau9`. It is pending at normal priority and holds no resources. At the latest audit, job
`439304` still held all three `gruenau9` A100s; its declared end is 3 August at 02:43 CEST, though
an earlier terminal state would release the node sooner. Under current evidence the Friday main
start is therefore not guaranteed. Friday execution remains blocked unless a clean smoke passes
and the full fresh go/no-go contract, cutoff, and explicit user approval are satisfied.

### 9.6 Final Friday gruenau10 environmental retry

At the user's explicit request, one final normal-priority, non-exclusive gruenau10 smoke was
submitted as job `439673` while the safe gruenau9-only smoke `439543` remained pending. Slurm
again assigned physical GPU 0. The allocation guard found four foreign Python processes using a
combined approximately 47.8 GiB on that device and exited with code 3 after two seconds. No model
was loaded, no optimizer update occurred, and the canonical `smoke/` directory remains absent.
Job `439543` remains the sole active smoke and continues to hold no resources while pending. This
retry confirms that priority and CPU/memory placement are not the blocker; gruenau10's physical
GPU use remains outside Slurm accounting. No further gruenau10 retry is justified without an
administrator-confirmed allocation-state correction.
