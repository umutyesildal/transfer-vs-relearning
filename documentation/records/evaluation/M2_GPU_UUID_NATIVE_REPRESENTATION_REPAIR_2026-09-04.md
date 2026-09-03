# M2 GPU UUID native-representation repair

Status: local tested repair; no new HU access, publication or GPU submission in this preparation.

Source-level cause: the prior gate required `GPU-` in `str(properties.uuid)`. PyTorch 2.6.0
binds CUuuid.__str__ to uuid_to_string, which emits bare 8-4-4-4-12 hex. The old mock supplied
an SMI-prefixed string, concealing the native API mismatch.
Primary source: https://github.com/pytorch/pytorch/blob/v2.6.0/torch/csrc/cuda/Module.cpp#L895-L940

This proves a compatibility bug in the gate. The failed job's audit omitted its raw UUID, so
we cannot retrospectively claim its exact value or prove all earlier V1B failures have this cause.

The repair converts only valid nonzero UUIDs, without physical-index guessing. It records raw
representation/type/Torch version before validation. The 20 GiB threshold, CUDA logical zero,
single-device requirement, SMI UUID equality and failure persistence remain unchanged.
An emulated CUuuid object now exercises the upstream __str__ contract; tests cover bare/prefixed/
uppercase UUIDs and eleven malformed/missing/nil/MIG/index/bytes inputs without SMI access.
The combined targeted suite passes **49/49**, CPU-only. Local Torch is 2.13.0, so this is source-
backed mock compatibility evidence, not a live test of pinned CUDA runtime 2.6.0.

The original contract remains byte-identical. The V1A contract names the full corrected runtime
lock path and a fresh root. New publication/HU/GPU execution requires separate exact approval.
Completed evaluations and failed roots are preserved; scientific recovery is not opened.
