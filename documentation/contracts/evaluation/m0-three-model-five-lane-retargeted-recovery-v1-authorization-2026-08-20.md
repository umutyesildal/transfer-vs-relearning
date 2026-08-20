# Five-Lane Retargeted M0 Recovery Authorization

Date: 2026-08-20  
Status: `AUTHORIZED_SINGLE_WAVE`

- Contract SHA-256: `1b030869455d68aa0ecf933f881c1661e1fbf504997376fdba08a626e1bc0a55`
- Pre-authorization config SHA-256: `705661dd5e32d836ee58f64101bc887c7a85059bae3ca2b25505ad967bde9a7d`
- Frozen implementation commit: `caaa380c2b237437b38019ac319e95a82b38f80e`

The user explicitly authorized publication of the narrow authorization overlay, preservation-checked
HU fast-forward, one final fail-closed preflight and exactly one five-job retargeted M0 recovery
DAG. The wave retains 19 valid lanes by hash and may execute only the five frozen targets under the
fresh recovery root.

This authorization does not permit rescoring the 19 retained lanes, a retry or second wave,
normalization, scientific interpretation, M1/M2 work, cleanup, deletion, prior-root mutation,
HU-home writes, memory-threshold changes or foreign-process intervention.
