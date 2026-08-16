from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

from transfer_vs_relearning.utils.io import sha256_file, sha256_text, write_json


MODEL_IDS = ["olmo", "qwen", "smollm"]
STATES = ["M0", "M1", "M2-A", "M2-B"]
PHASES = [
    {
        "id": "m0_evaluation",
        "state": "M0",
        "kind": "evaluation",
        "authority": "evaluation",
        "depends_on": [],
        "contract": "evaluation",
        "model_binding": "m0_scientific_evaluation",
    },
    {
        "id": "m1_training",
        "state": "M1",
        "kind": "training",
        "authority": "training",
        "depends_on": ["m0_evaluation"],
        "contract": "m1_training",
        "model_binding": "m1_recipe",
    },
    {
        "id": "m1_evaluation",
        "state": "M1",
        "kind": "evaluation",
        "authority": "evaluation",
        "depends_on": ["m1_training"],
        "contract": "evaluation",
    },
    {
        "id": "m2_sibling_preflight",
        "state": "M1",
        "kind": "preflight",
        "authority": "local_read_only",
        "depends_on": ["m1_evaluation"],
    },
    {
        "id": "m2a_training",
        "state": "M2-A",
        "kind": "training",
        "authority": "training",
        "depends_on": ["m2_sibling_preflight"],
        "contract": "m2_training",
        "model_binding": "m2a_recipe",
    },
    {
        "id": "m2b_training",
        "state": "M2-B",
        "kind": "training",
        "authority": "training",
        "depends_on": ["m2_sibling_preflight"],
        "contract": "m2_training",
        "model_binding": "m2b_recipe",
    },
    {
        "id": "m2a_evaluation",
        "state": "M2-A",
        "kind": "evaluation",
        "authority": "evaluation",
        "depends_on": ["m2a_training"],
        "contract": "evaluation",
    },
    {
        "id": "m2b_evaluation",
        "state": "M2-B",
        "kind": "evaluation",
        "authority": "evaluation",
        "depends_on": ["m2b_training"],
        "contract": "evaluation",
    },
    {
        "id": "branch_analysis",
        "state": "M2-B",
        "kind": "analysis",
        "authority": "local_write",
        "depends_on": ["m2a_evaluation", "m2b_evaluation"],
    },
]
EXECUTION_PHASES = {
    phase["id"] for phase in PHASES if phase["authority"] in {"evaluation", "training"}
}


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Matrix config must contain a YAML mapping: {path}")
    return value


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a mapping")
    return value


def _sha256(value: Any, label: str) -> str:
    text = str(value)
    if not re.fullmatch(r"[0-9a-f]{64}", text):
        raise ValueError(f"{label} must be a lowercase SHA-256")
    return text


def _validate_local_file(binding: dict[str, Any], label: str, repo_root: Path) -> None:
    raw_path = binding.get("path")
    raw_sha = binding.get("sha256")
    if raw_path is None and raw_sha is None:
        return
    if not isinstance(raw_path, str) or not raw_path or raw_sha is None:
        raise ValueError(f"{label} path and sha256 must be supplied together")
    expected = _sha256(raw_sha, f"{label}.sha256")
    path = Path(raw_path)
    resolved = path if path.is_absolute() else repo_root / path
    if not resolved.is_file():
        raise FileNotFoundError(f"{label} is missing: {raw_path}")
    if sha256_file(resolved) != expected:
        raise ValueError(f"{label} SHA-256 mismatch: {raw_path}")


def _validate_contracts(config: dict[str, Any], repo_root: Path) -> dict[str, dict[str, Any]]:
    contracts = _mapping(config.get("contracts"), "contracts")
    if set(contracts) != {"evaluation", "m1_training", "m2_training"}:
        raise ValueError("Matrix requires evaluation, m1_training and m2_training contracts")
    normalized: dict[str, dict[str, Any]] = {}
    for contract_id, raw in contracts.items():
        contract = _mapping(raw, f"contracts.{contract_id}")
        if contract.get("status") not in {"not_frozen", "draft", "frozen"}:
            raise ValueError(f"Unsupported contract status: {contract_id}")
        if not isinstance(contract.get("execution_authorized"), bool):
            raise ValueError(f"Contract authorization must be boolean: {contract_id}")
        _validate_local_file(contract, f"contracts.{contract_id}", repo_root)
        if contract["execution_authorized"] and contract["status"] != "frozen":
            raise ValueError(f"Authorized contract must be frozen: {contract_id}")
        normalized[contract_id] = dict(contract)
    return normalized


def _validate_model(
    model_id: str, raw: Any, *, repo_root: Path
) -> dict[str, Any]:
    model = _mapping(raw, f"models.{model_id}")
    for key in ("repository", "revision", "display_name"):
        if not isinstance(model.get(key), str) or not model[key]:
            raise ValueError(f"models.{model_id}.{key} is required")
    manifest = _mapping(model.get("manifest"), f"models.{model_id}.manifest")
    if not isinstance(manifest.get("path"), str) or not manifest["path"].startswith("/"):
        raise ValueError(f"models.{model_id}.manifest.path must be an absolute HU path")
    _sha256(manifest.get("sha256"), f"models.{model_id}.manifest.sha256")
    bindings = _mapping(model.get("bindings"), f"models.{model_id}.bindings")
    expected = {"m0_scientific_evaluation", "m1_recipe", "m2a_recipe", "m2b_recipe"}
    if set(bindings) != expected:
        raise ValueError(f"models.{model_id}.bindings must contain {sorted(expected)}")
    normalized_bindings: dict[str, dict[str, Any]] = {}
    for binding_id, raw_binding in bindings.items():
        binding = _mapping(raw_binding, f"models.{model_id}.bindings.{binding_id}")
        if binding.get("status") not in {
            "not_frozen",
            "qualification_only",
            "draft",
            "frozen",
        }:
            raise ValueError(f"Unsupported model binding status: {model_id}.{binding_id}")
        if not isinstance(binding.get("execution_authorized"), bool):
            raise ValueError(
                f"Model binding authorization must be boolean: {model_id}.{binding_id}"
            )
        _validate_local_file(binding, f"models.{model_id}.bindings.{binding_id}", repo_root)
        if binding["execution_authorized"] and binding["status"] != "frozen":
            raise ValueError(f"Authorized model binding must be frozen: {model_id}.{binding_id}")
        normalized_bindings[binding_id] = dict(binding)
    return {**model, "manifest": dict(manifest), "bindings": normalized_bindings}


def _node_blockers(
    phase: dict[str, Any],
    model: dict[str, Any],
    contracts: dict[str, dict[str, Any]],
    *,
    matrix_authorized: bool,
) -> list[str]:
    if phase["id"] not in EXECUTION_PHASES:
        return []
    blockers: list[str] = []
    contract = contracts[phase["contract"]]
    if contract["status"] != "frozen":
        blockers.append(f"{phase['contract']}_contract_not_frozen")
    if contract["execution_authorized"] is not True:
        blockers.append(f"{phase['contract']}_contract_not_authorized")
    binding_id = phase.get("model_binding")
    if binding_id:
        binding = model["bindings"][binding_id]
        if binding["status"] != "frozen":
            blockers.append(f"{binding_id}_not_frozen")
        if binding.get("path") is None:
            blockers.append(f"{binding_id}_config_missing")
        if binding["execution_authorized"] is not True:
            blockers.append(f"{binding_id}_not_authorized")
    if not matrix_authorized:
        blockers.append("matrix_not_authorized")
    return blockers


def build_model_matrix_plan(config_path: Path, *, repo_root: Path | None = None) -> dict[str, Any]:
    repo_root = (repo_root or Path.cwd()).resolve()
    config_path = config_path.resolve()
    config = _load_yaml(config_path)
    if config.get("schema_version") != 1:
        raise ValueError("Unsupported model-matrix schema_version")
    if config.get("status") not in {"prepared", "frozen"}:
        raise ValueError("Matrix status must be prepared or frozen")
    if not isinstance(config.get("execution_authorized"), bool):
        raise ValueError("Matrix execution_authorized must be boolean")
    state_design = _mapping(config.get("state_design"), "state_design")
    if state_design.get("states") != STATES:
        raise ValueError("Matrix states must be M0, M1, M2-A, M2-B")
    sibling = _mapping(state_design.get("m2_siblings"), "state_design.m2_siblings")
    if sibling != {
        "parent": "M1",
        "arms": ["M2-A", "M2-B"],
        "matched_budget_required": True,
    }:
        raise ValueError("M2-A and M2-B must be matched siblings from the same M1 parent")
    parallelism = _mapping(config.get("parallelism"), "parallelism")
    if parallelism.get("model_order") != MODEL_IDS:
        raise ValueError(f"Matrix model order must be {MODEL_IDS}")
    if parallelism.get("max_concurrent_jobs") != 3:
        raise ValueError("Matrix v1 requires exactly three concurrent jobs")
    if parallelism.get("barrier_between_waves") is not True:
        raise ValueError("Matrix v1 requires a barrier between three-job waves")

    template = _mapping(config.get("workflow_template"), "workflow_template")
    _validate_local_file(template, "workflow_template", repo_root)
    contracts = _validate_contracts(config, repo_root)
    raw_models = _mapping(config.get("models"), "models")
    if list(raw_models) != MODEL_IDS:
        raise ValueError(f"Matrix must declare models in order: {MODEL_IDS}")
    models = {
        model_id: _validate_model(model_id, raw_models[model_id], repo_root=repo_root)
        for model_id in MODEL_IDS
    }
    identities = [(model["repository"], model["revision"]) for model in models.values()]
    if len(set(identities)) != len(identities):
        raise ValueError("Matrix model repository/revision identities must be unique")

    nodes: list[dict[str, Any]] = []
    waves: list[dict[str, Any]] = []
    previous_wave: list[str] = []
    for wave_index, phase in enumerate(PHASES):
        wave_nodes: list[str] = []
        for model_id in MODEL_IDS:
            node_id = f"{model_id}__{phase['id']}"
            causal = [f"{model_id}__{dependency}" for dependency in phase["depends_on"]]
            dependencies = list(dict.fromkeys([*causal, *previous_wave]))
            blockers = _node_blockers(
                phase,
                models[model_id],
                contracts,
                matrix_authorized=config["execution_authorized"],
            )
            nodes.append(
                {
                    "id": node_id,
                    "ordinal": len(nodes),
                    "wave_index": wave_index,
                    "wave_id": phase["id"],
                    "model_id": model_id,
                    "model_repository": models[model_id]["repository"],
                    "model_revision": models[model_id]["revision"],
                    "state": phase["state"],
                    "kind": phase["kind"],
                    "authority_class": phase["authority"],
                    "causal_dependencies": causal,
                    "depends_on": dependencies,
                    "contract_id": phase.get("contract"),
                    "model_binding_id": phase.get("model_binding"),
                    "execution_blockers": blockers,
                    "status": "blocked_not_authorized" if blockers else "pending",
                }
            )
            wave_nodes.append(node_id)
        waves.append(
            {
                "index": wave_index,
                "id": phase["id"],
                "state": phase["state"],
                "kind": phase["kind"],
                "max_concurrent_jobs": 3,
                "barrier_from_previous_wave": wave_index > 0,
                "nodes": wave_nodes,
            }
        )
        previous_wave = wave_nodes

    all_blockers = sorted(
        {
            f"{node['id']}:{blocker}"
            for node in nodes
            for blocker in node["execution_blockers"]
        }
    )
    if config["execution_authorized"] and all_blockers:
        raise ValueError("Authorized matrix contains unresolved execution blockers")
    identity = {
        "matrix_id": config["matrix_id"],
        "config_sha256": sha256_file(config_path),
        "models": identities,
        "phases": [phase["id"] for phase in PHASES],
    }
    return {
        "schema_version": 1,
        "matrix_id": config["matrix_id"],
        "plan_id": sha256_text(json.dumps(identity, sort_keys=True))[:16],
        "status": "planned_not_authorized" if all_blockers else "ready",
        "contract_status": config["status"],
        "execution_authorized": config["execution_authorized"],
        "config_path": str(config_path),
        "config_sha256": sha256_file(config_path),
        "workflow_template": template,
        "state_design": state_design,
        "parallelism": parallelism,
        "contracts": contracts,
        "models": models,
        "model_count": len(models),
        "nodes": nodes,
        "node_count": len(nodes),
        "training_node_count": sum(node["kind"] == "training" for node in nodes),
        "state_evaluation_node_count": sum(node["kind"] == "evaluation" for node in nodes),
        "waves": waves,
        "wave_count": len(waves),
        "execution_blockers": all_blockers,
    }


def initialize_model_matrix_namespace(namespace: Path, plan: dict[str, Any]) -> Path:
    if namespace.exists():
        raise FileExistsError(f"Model-matrix namespace already exists: {namespace}")
    namespace.mkdir(parents=True)
    write_json(namespace / "matrix_plan.json", plan)
    write_json(
        namespace / "matrix_state.json",
        {
            "schema_version": 1,
            "matrix_id": plan["matrix_id"],
            "plan_id": plan["plan_id"],
            "status": "planned_not_authorized",
            "nodes": {
                node["id"]: {
                    "status": node["status"],
                    "evidence": [],
                    "execution_blockers": node["execution_blockers"],
                }
                for node in plan["nodes"]
            },
        },
    )
    return namespace


def load_model_matrix_namespace(namespace: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    plan = json.loads((namespace / "matrix_plan.json").read_text(encoding="utf-8"))
    state = json.loads((namespace / "matrix_state.json").read_text(encoding="utf-8"))
    if plan.get("plan_id") != state.get("plan_id"):
        raise ValueError("Model-matrix plan/state identity mismatch")
    return plan, state


def next_model_matrix_wave(plan: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    nodes = {node["id"]: node for node in plan["nodes"]}
    for wave in plan["waves"]:
        incomplete = [
            node_id
            for node_id in wave["nodes"]
            if state["nodes"][node_id]["status"] != "complete"
        ]
        if not incomplete:
            continue
        dependency_blockers = sorted(
            {
                dependency
                for node_id in incomplete
                for dependency in nodes[node_id]["depends_on"]
                if state["nodes"][dependency]["status"] != "complete"
            }
        )
        execution_blockers = sorted(
            {
                f"{node_id}:{blocker}"
                for node_id in incomplete
                for blocker in nodes[node_id]["execution_blockers"]
            }
        )
        status = (
            "waiting_on_dependencies"
            if dependency_blockers
            else "blocked_not_authorized"
            if execution_blockers
            else "ready"
        )
        return {
            "wave_id": wave["id"],
            "wave_index": wave["index"],
            "status": status,
            "nodes": incomplete,
            "dependency_blockers": dependency_blockers,
            "execution_blockers": execution_blockers,
        }
    return {"wave_id": None, "wave_index": None, "status": "complete", "nodes": []}


def render_model_matrix_packets(
    plan: dict[str, Any], output_dir: Path, *, replace_existing: bool = False
) -> list[Path]:
    if output_dir.exists() and not replace_existing:
        raise FileExistsError(f"Matrix packet directory already exists: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=replace_existing)
    written: list[Path] = []
    for node in plan["nodes"]:
        model = plan["models"][node["model_id"]]
        path = output_dir / f"{node['ordinal']:02d}-{node['id']}.md"
        blockers = "\n".join(f"- `{blocker}`" for blocker in node["execution_blockers"])
        if not blockers:
            blockers = "- none"
        dependencies = "\n".join(f"- `{item}`" for item in node["depends_on"]) or "- none"
        text = f"""# Luna matrix packet — {node['id']}

Packet ID: `{plan['matrix_id']}::{node['id']}`
Plan ID: `{plan['plan_id']}`
Mode: `bounded_adapter_implementation_or_validation`

## Exact scope

- model: `{model['repository']}`
- revision: `{model['revision']}`
- model manifest: `{model['manifest']['path']}`
- manifest SHA-256: `{model['manifest']['sha256']}`
- state: `{node['state']}`
- phase: `{node['wave_id']}`
- authority class: `{node['authority_class']}`

## Dependencies

{dependencies}

## Current execution blockers

{blockers}

## Context budget

Read root `AGENTS.md`, `documentation/current/PROJECT_STATE.yaml`, this packet, and only:

- `configs/studies/three_model_m0_to_m2_matrix_v1.yaml`
- `documentation/pipeline/README.md`
- `documentation/contracts/evaluation/eval-v1.md`

## Task

Implement or validate only the registered adapter/schema for this node. Preserve exact model,
parent-state, evaluation and corpus identities. Return changed paths, tests, evidence and one next
blocker. Do not rely on chat history.

## Stop conditions

- Do not execute evaluation, scoring or training from this packet.
- Do not use HU/SSH, Slurm, network, Git publication, cleanup or deletion.
- Do not relax a blocker, invent a missing config, or alter M2 sibling budgets.
"""
        path.write_text(text, encoding="utf-8")
        written.append(path)
    write_json(
        output_dir / "manifest.json",
        {
            "schema_version": 1,
            "matrix_id": plan["matrix_id"],
            "plan_id": plan["plan_id"],
            "packets": [path.name for path in written],
        },
    )
    return written
