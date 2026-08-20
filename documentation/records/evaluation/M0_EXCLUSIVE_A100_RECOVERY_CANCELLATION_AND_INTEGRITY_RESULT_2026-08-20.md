# M0 Exclusive-A100 Recovery Cancellation and Integrity Result — 2026-08-20

Status: `TERMINAL_PARTIAL_INVALID / CONTROLLER CANCELLED`

Controller `471047` was user-authorized for cancellation after a recovery-output routing defect was
verified. Finalizers `471048`--`471051` completed and preserved a fail-closed terminal bundle.

- OLMo English capability: complete, lane-result SHA-256
  `b254691b103bfae7fb9294b3078ae2a794e6c282d7afd3892e68eff4238df598`;
- OLMo Turkish capability: complete, lane-result SHA-256
  `3c934519740b45f62d6ead3c34e3e3871f62ef9ba9f8e748b663d17c12101c64`;
- OLMo Turkish perplexity: invalid, lane-result SHA-256
  `4d353e02b6312ff719863187d2507fc04648fe852ebfaa93cf70d2a894f47021`;
- Qwen three target lanes: not run;
- SmolLM target lane: not run.

The PPL evaluator used the frozen evaluator config's original source output path rather than the
fresh recovery lane root. It wrote three new evidence files under the original OLMo Turkish-PPL raw
path. They were not deleted or rewritten. The original failed lane-result hash remained unchanged.
This is an evidence-root immutability violation and requires append-only correction, not silent
cleanup.

- isolated-wave ledger SHA-256:
  `26120f9de7a265b45a160d41e46c1f80070ae7840cce5d203f356ae8d5913563`;
- GPU audit SHA-256:
  `23d05c6b441973a68409a648cd82ccae71e5cf924d896b397d56be1dd6e49b35`;
- terminal composite SHA-256:
  `8563bfcdfbe49cb3953bfe54fb22cd5910cff2933caf80a74cd51eeb681839cb`;
- composite status: `partial_invalid_no_cross_model_summary`;
- normalization allowed: false.

No automatic retry, deletion, cleanup, normalization or M1/M2 work is authorized. A new contract
must retarget all project-evaluator outputs into a fresh recovery namespace and bind only the
remaining invalid/missing lanes while retaining the two valid OLMo recovery results by hash.
