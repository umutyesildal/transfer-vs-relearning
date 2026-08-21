# M0 Three-Model Historical Exact-Prefix A100 Recovery Authorization

Date: 2026-08-21  
Status: `AUTHORIZED_SINGLE_WAVE`

- Contract SHA-256: `2469d25a78b552c82b6005b75f03b68199a1c7d2c2d8e0e557a2b8f585a80ac4`
- Pre-authorization config SHA-256:
  `f6ebaa43d3517d55ad9311ab40f236530f69b0f07c9f43cc5bf2560f85c7cbb7`
- Frozen implementation commit: `97831d167315f0ef34c7a554d1f7d2e4c74d71de`

The user explicitly authorized publication/HU synchronization, one final fail-closed preflight and
exactly one four-job A100 recovery DAG bound to the hashes above.

The wave may evaluate only the three operationally missing M0 historical exact-prefix lanes for
OLMo, Qwen and SmolLM as one `0-2%3` array pinned to `gruenau9`, requesting one A100-80GB per task,
plus one `afterany` finalizer. The first exact-prefix root remains immutable.

This authorization does not permit changing the model/input/prompt/candidate/scoring identity,
lowering the 20 GiB execution guard, changing the frozen route, rerunning robust A--D lanes,
automatic retry, a second recovery wave, normalization, M1/M2 work, cleanup, deletion, HU-home
writes, prior-root mutation, intervention in foreign processes, or alteration of the independent
Qwen Pile-10k DAG.
