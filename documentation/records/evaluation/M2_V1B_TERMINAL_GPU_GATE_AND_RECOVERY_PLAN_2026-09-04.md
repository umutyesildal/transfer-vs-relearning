# M2 V1B terminal GPU gate and local recovery preparation

Date: 2026-09-04. Status: terminal partial / local repair tested / recovery NOT authorized.

## Verified terminal evidence

The 00:24 Europe/Berlin read-only inspection found no active jobs in array `483838` or
finalizer `483839`. The preserved root is
`/vol/tmp2/yesildau/vnd_m2_oscar_eval_v2_execution_v1b`.

All 63 task-result manifests exist. Exactly 21 report complete (indices 0–20): all 20 OLMo
M2 checkpoint states plus Qwen M2-A update 76. Exactly 42 report failed (indices 21–62):
19 Qwen M2 checkpoints, 20 SmolLM M2 checkpoints, and all three M1-parent OSCAR baselines.
Every failure reports the identical guard observation:

`GPU free-memory gate failed on index 0: 16720592896 bytes free < 21474836480 required`.

The finalizer wrote `M2_EVAL_V2_INCOMPLETE` with `gpu_complete_count=21` and
`gpu_task_count=63`. No `scientific_analysis.json` exists. These guard failures are operational
NOT_RUN evidence, not negative model scores. Completed output validators reported complete;
their full artifact hash inventory still needs binding for recovery. No automatic retry occurred.

## Confirmed code defect versus unconfirmed incident cause

The imported M1 helper passes the first numeric `CUDA_VISIBLE_DEVICES` token directly to
`nvidia-smi -i`. That assumes CUDA logical/device visibility numbering equals host NVML
numbering. The implementation does not establish that identity. Repeating the same free-byte
value across failures is consistent with an incorrect fixed-device probe, but does NOT prove
that was the live cause: real device occupation could also explain the observation. Historical
task audits lack CUDA UUIDs, so allocation identity cannot be reconstructed from those alone.

The M2-only local replacement uses CUDA logical device zero, reads its UUID and available bytes,
then queries SMI by that exact UUID. It requires one visible Slurm device and an A100-80GB;
both memory samples must pass the unchanged 20 GiB threshold. No alternate GPU is selected,
no visibility is changed, and no model is loaded by the guard. Missing UUID, low memory,
identity mismatch, unsupported device, and probe timeout all persist a failure audit before
raising. Existing audit paths cannot be reused. The historical M1 helper and frozen V1B contract
remain unchanged. The M2 executor now calls the local replacement on both task routes.

The next narrow boundary is frozen in
`documentation/contracts/evaluation/vngrs-m2-oscar-gpu-identity-qualification-v1.md`, SHA-256
`4221b25cdd61a55751be85e9636b944a490cea441466d142d6a25e3535bbc34e`.
It proposes one 10-minute-limit A100 metadata-only qualification, without model loading, before
freezing the recovery wave. It is not execution authority until separately authorized.

## Recovery design (not yet frozen or executable)

1. Bind the terminal matrix, preflight, held-out corpus, baseline registry, family result and
   all 63 task-result hashes. Inventory and hash all files in the 21 complete state directories.
   Verify failed state directories contain only pre-scoring configs and failure manifests.
2. Qualify the CUDA-UUID/SMI binding inside one real Slurm allocation with the pinned runtime,
   before any scientific retry. CPU-only mock tests cannot establish this hardware mapping.
   A genuine low-memory result must stop qualification, not relax the threshold.
3. Prepare one separately authorized fresh-root recovery, retaining source and failed evidence
   read-only. Reference the 21 completed states without rescoring; reuse the exact frozen
   10,000-document held-out population without re-materializing the corpus.
4. Run only indices 21–62 with unchanged scientific inputs, metrics, seeds, precision and gates.
   A canary dependency must precede the remaining fan-out; persist identity on PASS and failure.
   Define a fail-stop mechanism so a common guard failure does not blindly consume every task.
5. Close a combined 63-state registry from 21 preserved plus 42 recovered results, verify both
   sources, then run the same precommitted final analysis. Do not overwrite the old finalizer.

Unresolved qualification/binding items above prevent a frozen recovery claim. No new Slurm
submission, inference, push, HU fast-forward, cancellation, cleanup, deletion or retry is
authorized by this local preparation. A new exact contract and user authorization are required.

## Local verification

Ten new mocked runtime tests exercise UUID rather than physical-index selection, unchanged memory
threshold, wrong/absent GPU identity, multiple devices, low CUDA/SMI memory, timeout, non-A100,
invalid total memory, persistent failure, and existing-audit preservation. They run without GPU
access or model loading. Combined with the 24 prior tests: 34 tests pass before publication.
