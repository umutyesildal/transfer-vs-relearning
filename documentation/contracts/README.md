# Contracts

Contracts define a prospective measurement or execution protocol before outcomes are observed.
They are not diaries and do not become authority merely by existing.

## Lifecycle

```text
draft → qualified → frozen → executed
                    └──────→ superseded
```

- `draft`: open questions remain; no execution.
- `qualified`: dependencies, task names, schemas, and feasibility have evidence, but final review
  is incomplete.
- `frozen`: exact semantics and bounds are immutable for the named wave/version.
- `executed`: one authorized wave produced an immutable result record.
- `superseded`: retained for provenance but no longer current.

User authorization and contract state are separate. A frozen contract still needs the exact user
authorization required by `AGENTS.md` and current project state.

## Naming

Use a scoped directory and semantic version, for example:

```text
documentation/contracts/evaluation/eval-v1.md
documentation/contracts/corpora/vngrs-v1.md
documentation/contracts/training/m1-olmo-v1.md
documentation/contracts/training/m2-siblings-v1.md
```

Do not continue the global historical document number sequence for new contracts.

## Required contract fields

Every contract states:

- name, version, status, owner, creation/review date;
- purpose, estimand, in-scope and out-of-scope actions;
- immutable code, model/tokenizer, data, task, and environment identities;
- inputs, outputs, schemas, namespaces, and retention class;
- exact algorithm/configuration and all comparison-matching rules;
- acceptance gates, metric directions, denominators, uncertainty, and missingness behavior;
- preflight, failure, resume, idempotency, and rollback semantics;
- verification tests and evidence required for completion;
- explicit authority boundary and prohibitions;
- supersession/change policy.

Use [`../templates/CONTRACT_TEMPLATE.md`](../templates/CONTRACT_TEMPLATE.md) as a starting point.

## Semantic version rule

After freeze, changing a task, dataset, prompt, preprocessing rule, metric, denominator, threshold,
checkpoint grid, seed policy, or comparison budget creates a new contract version. Implementation
repairs that provably preserve semantics may use an append-only correction, but the repair and its
equivalence evidence must be explicit.

Historical results stay attached to the contract version that produced them.

## Evaluation status

No `eval-v1` contract is frozen yet. The local inventory, upstream task-semantic audit and result
schema now exist. The prospective protocol is
[`evaluation/eval-v1.md`](evaluation/eval-v1.md). Its exact dataset revisions, environment/runtime
evidence, parity checks, cheap-panel identity and numerical margins remain freeze blockers.
