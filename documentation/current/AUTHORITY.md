# Authority and reading order

This file answers two questions: “What can I do?” and “What must I read?”

## Authority hierarchy

1. System/developer constraints and the user's current explicit instruction.
2. Root `AGENTS.md` stable operating rules.
3. The applicable frozen contract for the exact proposed work.
4. `PROJECT_STATE.yaml` and the current gate.
5. Task-local plan or orchestration decision.
6. Historical records and old handoffs.

A lower item cannot grant authority missing from a higher item. In particular, an old numbered
document that once authorized a single wave cannot authorize another execution.

## Minimum new-agent set

Every new agent reads exactly these first:

1. `AGENTS.md`;
2. `documentation/current/PROJECT_STATE.yaml`;
3. the current user request or bounded task packet.

Then it adds only task-specific material from the table below. This is the default micro-context
boundary.

| Task | Additional reading |
|---|---|
| Repository orientation | root `README.md` |
| Scientific interpretation | `current/STATUS.md` and cited result/gate records |
| Evaluation design | Document 178, Document 177, relevant evaluator code/config/tests |
| Execute a frozen local contract | that exact contract plus named inputs and acceptance tests |
| HU/Slurm work | exact authorized contract, `ssh-client/README.md`, relevant launcher/preflight |
| Corpus work | exact corpus contract, provenance manifest, contamination policy, relevant scripts |
| Historical investigation | only the numbered chain cited by the current state/result |
| Paper writing | relevant paper source and the result manifests being cited |

## Is `AGENTS.md` enough?

No. It should stay stable and compact. If it also carried every live job, hash, blocker, and result,
it would become stale and consume the worker's context before the task begins.

The intended split is:

```text
AGENTS.md                    stable rules
PROJECT_STATE.yaml           live facts and gates
current task packet          one bounded objective
relevant frozen contract     exact semantics/authority when needed
evidence named by the task   proof, not background loading
```

## Authorization checklist

Before any external or scientific execution, all answers must be yes:

- Does the current user instruction authorize this exact class of action?
- Is there an applicable frozen contract with immutable identities and bounds?
- Does `PROJECT_STATE.yaml` permit the stage, or does the new contract explicitly resolve its gate?
- Are output paths fresh, storage-safe, and preservation-checked?
- Are failure semantics and acceptance criteria fixed before outcomes are visible?

If any answer is no or ambiguous, stop at local analysis/planning and ask for a bounded decision.

## Handoffs

A handoff should contain only:

- outcome and current state change;
- exact paths changed;
- tests/evidence;
- unresolved blockers;
- one next boundary;
- links to the contract/result/manifest.

Do not make a new agent reconstruct the project by reading all numbered documents or a previous
chat transcript.
