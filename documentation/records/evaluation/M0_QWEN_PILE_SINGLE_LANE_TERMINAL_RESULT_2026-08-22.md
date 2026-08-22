# M0 Qwen Pile Single-Lane Terminal Result — 2026-08-22

**Classification:** operational `failed_pre_scoring`; not a model score

**Scientific use:** retired from eval-v2

The authorized single-lane wave was submitted as job `472809`; finalizers were
`472810/472811/472812/472813`. The lane left the queue, ran for approximately 553 seconds and
returned code 1. The route audit selected an exclusive A100 allocation and passed its frozen free
memory guard.

All 10,000 Pile rows were tokenized and Harness selected batch size 1. The run then failed in the
post-forward `log_softmax` allocation: PyTorch attempted approximately 37.09 GiB with approximately
36.65 GiB free on the selected 79.25 GiB device. No valid Qwen Pile BPB/PPL observation was
produced. This is a logits/materialization memory peak, not a dataset-resolution failure and not a
scientific negative result.

The finalizers completed and no matching job remained in the active queue at inspection. Slurm
accounting was unavailable through `sacct` because of the known Munge/SlurmDBD authentication
failure. Exact HU artifact hashes were not imported into this local record; the preserved scratch
namespace remains the raw authority.

The later prospective Pile retirement decision ends all retry need. No cleanup or deletion is
authorized.
