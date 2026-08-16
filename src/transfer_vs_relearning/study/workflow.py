from __future__ import annotations

import json
import importlib.util
import re
from pathlib import Path
from typing import Any, Callable

import yaml

from transfer_vs_relearning.utils.io import sha256_file, sha256_text, write_json


STATES = {"STUDY", "M0", "M1", "M2-A", "M2-B"}
STAGE_KINDS = {
    "preflight",
    "evaluation",
    "probing",
    "training",
    "selection",
    "normalization",
    "analysis",
    "presentation",
}
AUTHORITY_CLASSES = {"local_read_only", "local_write", "evaluation", "training"}
_PLACEHOLDER = re.compile(r"^__[A-Z0-9_]+__$")


def load_study_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise ValueError("Study config must contain a YAML mapping")
    return value


def _mapping(value: dict[str, Any], key: str) -> dict[str, Any]:
    child = value.get(key)
    if not isinstance(child, dict):
        raise ValueError(f"Study config requires mapping: {key}")
    return child


def _strings(value: Any, label: str, *, nonempty: bool = False) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError(f"{label} must be a list of strings")
    if nonempty and not value:
        raise ValueError(f"{label} cannot be empty")
    return list(value)


def _placeholder_paths(value: Any, prefix: str = "") -> list[str]:
    if isinstance(value, dict):
        return [
            path
            for key, child in value.items()
            for path in _placeholder_paths(child, f"{prefix}.{key}" if prefix else str(key))
        ]
    if isinstance(value, list):
        return [
            path
            for index, child in enumerate(value)
            for path in _placeholder_paths(child, f"{prefix}[{index}]")
        ]
    return [prefix] if _PLACEHOLDER.fullmatch(str(value).strip()) else []


def _validate_state_design(config: dict[str, Any]) -> None:
    design = _mapping(config, "state_design")
    if design.get("states") != ["M0", "M1", "M2-A", "M2-B"]:
        raise ValueError("Study state order must be M0, M1, M2-A, M2-B")
    siblings = _mapping(design, "m2_siblings")
    if siblings.get("parent") != "M1" or siblings.get("arms") != ["M2-A", "M2-B"]:
        raise ValueError("M2-A and M2-B must be sibling arms with the same M1 parent")
    if siblings.get("matched_budget_required") is not True:
        raise ValueError("M2 sibling budgets must be matched")
    if design.get("evaluation_contract") != "eval-v1":
        raise ValueError("The full study must bind eval-v1 uniformly")


def _validate_stage(stage: dict[str, Any], seen: set[str], ordinal: int) -> dict[str, Any]:
    required = {
        "id",
        "state",
        "kind",
        "objective",
        "depends_on",
        "adapter_id",
        "authority_class",
        "context_files",
        "allowed_paths",
        "acceptance_criteria",
        "outputs",
    }
    missing = required - set(stage)
    if missing:
        raise ValueError(f"Study stage is missing fields: {sorted(missing)}")
    stage_id = str(stage["id"])
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", stage_id) or stage_id in seen:
        raise ValueError(f"Invalid or duplicate study stage id: {stage_id!r}")
    state = str(stage["state"])
    kind = str(stage["kind"])
    authority = str(stage["authority_class"])
    if state not in STATES or kind not in STAGE_KINDS or authority not in AUTHORITY_CLASSES:
        raise ValueError(f"Invalid stage classification for {stage_id}")
    dependencies = _strings(stage["depends_on"], f"{stage_id}.depends_on")
    missing_dependencies = sorted(set(dependencies) - seen)
    if missing_dependencies:
        raise ValueError(
            f"Stage {stage_id} depends on unknown or later stages: {missing_dependencies}"
        )
    context_files = _strings(stage["context_files"], f"{stage_id}.context_files", nonempty=True)
    if len(context_files) > 8:
        raise ValueError(f"Stage {stage_id} exceeds the eight-file context budget")
    allowed_paths = _strings(stage["allowed_paths"], f"{stage_id}.allowed_paths", nonempty=True)
    acceptance = _strings(
        stage["acceptance_criteria"], f"{stage_id}.acceptance_criteria", nonempty=True
    )
    outputs = _strings(stage["outputs"], f"{stage_id}.outputs", nonempty=True)
    seen.add(stage_id)
    return {
        **stage,
        "ordinal": ordinal,
        "id": stage_id,
        "state": state,
        "kind": kind,
        "depends_on": dependencies,
        "authority_class": authority,
        "context_files": context_files,
        "allowed_paths": allowed_paths,
        "acceptance_criteria": acceptance,
        "outputs": outputs,
    }


def _validate_required_causal_edges(stages: list[dict[str, Any]]) -> None:
    by_id = {stage["id"]: stage for stage in stages}
    required = {
        "m1_training": {"m0_normalization"},
        "m1_checkpoint_selection": {"m1_evaluation", "m1_probing"},
        "m2_sibling_preflight": {"m1_checkpoint_selection"},
        "m2a_training": {"m2_sibling_preflight"},
        "m2b_training": {"m2_sibling_preflight"},
        "m2a_evaluation_probing": {"m2a_training"},
        "m2b_evaluation_probing": {"m2b_training"},
        "branch_analysis": {"m2a_evaluation_probing", "m2b_evaluation_probing"},
        "presentation_bundle": {"branch_analysis"},
    }
    if not set(required).issubset(by_id):
        raise ValueError("Study stages do not contain the complete M0-to-M2 causal skeleton")
    for stage_id, dependencies in required.items():
        if not dependencies.issubset(set(by_id[stage_id]["depends_on"])):
            raise ValueError(f"Study causal edge is missing for {stage_id}: {sorted(dependencies)}")


def build_study_plan(config_path: Path, *, repo_root: Path | None = None) -> dict[str, Any]:
    repo_root = (repo_root or Path.cwd()).resolve()
    config_path = config_path.resolve()
    config = load_study_config(config_path)
    if int(config.get("schema_version", 0)) != 1:
        raise ValueError("Unsupported study schema_version")
    if config.get("status") not in {"draft", "frozen"}:
        raise ValueError("Study status must be draft or frozen")
    if config.get("execution_authorized") is not False:
        raise ValueError("Study planning config must keep execution_authorized=false")
    study_id = str(config.get("study_id", "")).strip()
    if not study_id:
        raise ValueError("study_id is required")
    _validate_state_design(config)

    raw_stages = config.get("stages")
    if not isinstance(raw_stages, list) or not raw_stages:
        raise ValueError("Study config requires a non-empty stages list")
    seen: set[str] = set()
    stages = [_validate_stage(stage, seen, ordinal) for ordinal, stage in enumerate(raw_stages)]
    _validate_required_causal_edges(stages)

    if config["status"] == "frozen":
        placeholders = _placeholder_paths(config)
        if placeholders:
            raise ValueError(
                "Frozen study config cannot contain placeholders: " + ", ".join(placeholders[:8])
            )
        for stage in stages:
            for relative in stage["context_files"]:
                path = Path(relative)
                resolved = path if path.is_absolute() else repo_root / path
                if not resolved.is_file():
                    raise FileNotFoundError(f"Frozen study context file is missing: {relative}")

    identity = {
        "study_id": study_id,
        "config_sha256": sha256_file(config_path),
        "stage_ids": [stage["id"] for stage in stages],
        "evaluation_contract": config["state_design"]["evaluation_contract"],
    }
    return {
        "schema_version": 1,
        "plan_id": sha256_text(json.dumps(identity, sort_keys=True))[:16],
        "study_id": study_id,
        "contract_status": config["status"],
        "status": "planned_not_authorized",
        "execution_authorized": False,
        "config_path": str(config_path),
        "config_sha256": sha256_file(config_path),
        "state_design": config["state_design"],
        "stages": stages,
        "stage_count": len(stages),
    }


def assess_m0_readiness(
    config_path: Path,
    *,
    repo_root: Path,
    project_state_path: Path,
) -> dict[str, Any]:
    """Return deterministic M0 execution gates without running evaluation or scoring."""
    repo_root = repo_root.resolve()
    config_path = config_path.resolve()
    project_state_path = project_state_path.resolve()
    config = load_study_config(config_path)
    plan = build_study_plan(config_path, repo_root=repo_root)
    project_state = load_study_config(project_state_path)
    bindings = _mapping(config, "bindings")

    registry_value = bindings.get("eval_registry")
    registry_path = Path(str(registry_value))
    if not registry_path.is_absolute():
        registry_path = repo_root / registry_path
    registry = load_study_config(registry_path) if registry_path.is_file() else {}

    checks: list[dict[str, Any]] = []

    def record(check_id: str, passed: bool, detail: str) -> None:
        checks.append({"id": check_id, "status": "pass" if passed else "blocked", "detail": detail})

    record(
        "study_contract_frozen",
        config.get("status") == "frozen",
        f"study status is {config.get('status')!r}",
    )
    placeholders = _placeholder_paths(bindings)
    record(
        "study_bindings_resolved",
        not placeholders,
        "all bindings resolved" if not placeholders else "unresolved: " + ", ".join(placeholders),
    )

    readiness = _mapping(project_state, "readiness")
    record(
        "project_ready_to_measure",
        readiness.get("ready_to_measure") is True,
        f"ready_to_measure is {readiness.get('ready_to_measure')!r}",
    )
    record(
        "project_eval_contract_frozen",
        readiness.get("evaluation_contract") == "frozen",
        f"evaluation_contract is {readiness.get('evaluation_contract')!r}",
    )
    record(
        "eval_registry_present",
        registry_path.is_file(),
        str(registry_path),
    )
    record(
        "eval_registry_frozen",
        registry.get("status") == "frozen",
        f"registry status is {registry.get('status')!r}",
    )
    record(
        "eval_registry_execution_ready",
        registry.get("execution_ready") is True,
        f"execution_ready is {registry.get('execution_ready')!r}",
    )
    record(
        "lm_eval_environment_available",
        importlib.util.find_spec("lm_eval") is not None,
        "lm_eval import is available"
        if importlib.util.find_spec("lm_eval") is not None
        else "lm_eval is not installed in this Python environment",
    )

    m0_stages = {
        stage["id"]: stage
        for stage in plan["stages"]
        if stage["id"] in {"m0_evaluation", "m0_probing"}
    }
    for stage_id in ("m0_evaluation", "m0_probing"):
        stage = m0_stages[stage_id]
        adapter_paths = [
            repo_root / relative
            for relative in stage["allowed_paths"]
            if relative.startswith("src/") and "*" not in relative
        ]
        present = any(path.is_file() for path in adapter_paths)
        record(
            f"{stage_id}_adapter_present",
            present,
            ", ".join(str(path.relative_to(repo_root)) for path in adapter_paths),
        )

    blockers = [check["id"] for check in checks if check["status"] != "pass"]
    return {
        "schema_version": 1,
        "scope": "m0_evaluation_preflight",
        "status": "ready" if not blockers else "blocked",
        "scientific_work_started": False,
        "plan_id": plan["plan_id"],
        "study_id": plan["study_id"],
        "checks": checks,
        "blockers": blockers,
    }


def initialize_study_namespace(namespace: Path, plan: dict[str, Any]) -> Path:
    if namespace.exists():
        raise FileExistsError(f"Study namespace already exists: {namespace}")
    namespace.mkdir(parents=True)
    write_json(namespace / "study_plan.json", plan)
    write_json(
        namespace / "study_state.json",
        {
            "schema_version": 1,
            "plan_id": plan["plan_id"],
            "study_id": plan["study_id"],
            "status": "planned_not_authorized",
            "stages": {
                stage["id"]: {
                    "status": "pending",
                    "evidence": [],
                    "missing_reason": "not_run",
                }
                for stage in plan["stages"]
            },
        },
    )
    return namespace


def load_study_namespace(namespace: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    plan = json.loads((namespace / "study_plan.json").read_text(encoding="utf-8"))
    state = json.loads((namespace / "study_state.json").read_text(encoding="utf-8"))
    if plan.get("plan_id") != state.get("plan_id"):
        raise ValueError("Study plan/state identity mismatch")
    return plan, state


def next_stage_status(plan: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    for stage in plan["stages"]:
        row = state["stages"][stage["id"]]
        if row["status"] == "complete":
            continue
        incomplete = [
            dependency
            for dependency in stage["depends_on"]
            if state["stages"][dependency]["status"] != "complete"
        ]
        if incomplete:
            return {"stage_id": stage["id"], "status": "waiting_on_dependencies", "dependencies": incomplete}
        if stage["authority_class"] in {"evaluation", "training"}:
            return {
                "stage_id": stage["id"],
                "status": "awaiting_authorization",
                "authority_class": stage["authority_class"],
            }
        return {
            "stage_id": stage["id"],
            "status": "ready_for_registered_adapter",
            "authority_class": stage["authority_class"],
        }
    return {"stage_id": None, "status": "complete"}


Adapter = Callable[[dict[str, Any]], dict[str, Any]]


def run_with_registered_adapters(
    plan: dict[str, Any],
    adapters: dict[str, Adapter],
    *,
    authorized_scopes: set[str],
) -> dict[str, Any]:
    """In-memory deterministic runner used by tested adapters; the CLI registers none yet."""
    results: dict[str, Any] = {}
    for stage in plan["stages"]:
        dependencies = stage["depends_on"]
        if any(results.get(dependency, {}).get("status") != "complete" for dependency in dependencies):
            raise RuntimeError(f"Stage dependencies are incomplete: {stage['id']}")
        if stage["authority_class"] not in authorized_scopes:
            return {
                "status": "awaiting_authorization",
                "blocked_stage": stage["id"],
                "results": results,
            }
        adapter = adapters.get(stage["adapter_id"])
        if adapter is None:
            return {
                "status": "blocked_adapter_not_registered",
                "blocked_stage": stage["id"],
                "results": results,
            }
        outcome = adapter(stage)
        if outcome.get("status") != "complete":
            return {"status": "blocked_stage_failed", "blocked_stage": stage["id"], "results": results}
        results[stage["id"]] = outcome
    return {"status": "complete", "blocked_stage": None, "results": results}


def render_luna_packets(
    plan: dict[str, Any], output_dir: Path, *, replace_existing: bool = False
) -> list[Path]:
    if output_dir.exists() and not replace_existing:
        raise FileExistsError(f"Luna packet directory already exists: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=replace_existing)
    written: list[Path] = []
    for stage in plan["stages"]:
        path = output_dir / f"{stage['ordinal']:02d}-{stage['id']}.md"
        context = "\n".join(f"- `{item}`" for item in stage["context_files"])
        allowed = "\n".join(f"- `{item}`" for item in stage["allowed_paths"])
        criteria = "\n".join(f"- {item}" for item in stage["acceptance_criteria"])
        outputs = "\n".join(f"- `{item}`" for item in stage["outputs"])
        external = stage["authority_class"] in {"evaluation", "training"}
        text = f"""# Luna task packet — {stage['id']}

Packet ID: `{plan['study_id']}::{stage['id']}`
Study plan: `{plan['plan_id']}`
Stage state: `{stage['state']}`
Authority class: `{stage['authority_class']}`
Packet mode: `adapter_implementation_or_validation`

## Objective

Prepare or validate the local registered adapter for stage `{stage['id']}`. Do not execute the
scientific stage from this packet.

Scientific stage objective: {stage['objective']}

## Context budget

Read only the standard agent control files, this packet, and these task-specific files:

{context}

## Allowed paths

{allowed}

## Acceptance criteria

{criteria}

## Expected handoff outputs

{outputs}

## Stop conditions

- Do not broaden the task or read the chronological archive unless this packet names a file.
- Do not commit, push, delete, clean, download, use HU/SSH, or submit Slurm.
- {'This packet prepares or validates an external stage; it does not authorize the evaluation/training itself.' if external else 'Stop if completion requires evaluation, training, network, HU/SSH, Slurm, or new scientific judgment.'}

## Handoff

Return the structured worker report with exact changed paths, tests, unmet criteria, and the single
next blocker. Project state lives in `documentation/current/PROJECT_STATE.yaml`, not chat memory.
"""
        path.write_text(text, encoding="utf-8")
        written.append(path)
    manifest = {
        "schema_version": 1,
        "study_id": plan["study_id"],
        "plan_id": plan["plan_id"],
        "packets": [path.name for path in written],
    }
    write_json(output_dir / "manifest.json", manifest)
    return written
