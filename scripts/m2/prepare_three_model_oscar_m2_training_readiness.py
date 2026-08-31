#!/usr/bin/env python3
"""Prepare CPU-only M2 training-readiness evidence without training or inference."""

from __future__ import annotations

import argparse
import html
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any

import yaml

from transfer_vs_relearning.utils.io import sha256_file, write_json


ROLES = ("olmo", "qwen", "smollm")
EXCLUDED = {"optimizer.pt", "scheduler.pt", "rng_state.pth", "trainer_state.json", "training_args.bin"}


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON mapping required: {path}")
    return value


def _assert_file(path: Path, expected: str) -> None:
    if not path.is_file() or path.is_symlink() or sha256_file(path) != expected:
        raise ValueError(f"Frozen input missing, unsafe or drifted: {path}")


def _rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _validate_precreated_root(root: Path, contract_id: str) -> None:
    state = root / "control/submission_state.json"
    if not root.is_dir() or root.is_symlink() or not state.is_file() or state.is_symlink():
        raise ValueError("Readiness root must be safely precreated by the submitter")
    payload = _json(state)
    if payload.get("status") != "SUBMISSION_PREPARED" or payload.get("contract_id") != contract_id:
        raise ValueError("Readiness submission state drift")
    allowed = {"control/submission_state.json", "control/submission_result.json"}
    for path in (item for item in root.rglob("*") if item.is_file()):
        relative = str(path.relative_to(root))
        if relative not in allowed and not relative.startswith("logs/slurm-"):
            raise ValueError(f"Unexpected pre-run readiness artifact: {relative}")


def _parent(role: str, binding: dict[str, Any]) -> tuple[dict[str, Any], int]:
    snapshot_root = Path(binding["snapshot_root"]).resolve()
    snapshot_manifest = Path(binding["snapshot_manifest"]).resolve()
    model_manifest = Path(binding["model_manifest"]).resolve()
    _assert_file(snapshot_manifest, str(binding["snapshot_manifest_sha256"]))
    _assert_file(model_manifest, str(binding["model_manifest_sha256"]))
    manifest = _json(model_manifest)
    if Path(str(manifest.get("local_path_absolute", ""))).resolve() != snapshot_root:
        raise ValueError(f"{role}: parent manifest local path is not exact epoch-036 snapshot")
    hashes = manifest.get("file_hashes")
    if not isinstance(hashes, dict) or not hashes:
        raise ValueError(f"{role}: parent manifest has no file hash registry")
    assets: list[dict[str, Any]] = []
    for name, expected in sorted(hashes.items()):
        if Path(name).name != name or name in EXCLUDED:
            raise ValueError(f"{role}: unsafe or trainer-state parent asset: {name}")
        path = snapshot_root / name
        _assert_file(path, str(expected))
        assets.append({"name": name, "bytes": path.stat().st_size, "sha256": str(expected)})
    if not any(row["name"] == "config.json" for row in assets):
        raise ValueError(f"{role}: config.json is absent")
    if not any(row["name"].endswith((".safetensors", ".bin")) for row in assets):
        raise ValueError(f"{role}: model weight asset is absent")
    total = sum(int(row["bytes"]) for row in assets)
    return {
        "role": role,
        "status": "EXACT_M1_PARENT_ASSETS_PASS",
        "snapshot_root": str(snapshot_root),
        "snapshot_manifest": {"path": str(snapshot_manifest), "sha256": sha256_file(snapshot_manifest)},
        "model_manifest": {"path": str(model_manifest), "sha256": sha256_file(model_manifest)},
        "asset_count": len(assets),
        "model_only_bytes": total,
        "assets": assets,
    }, total


def _review_html(rows: list[dict[str, Any]], registry_sha256: str) -> str:
    data = json.dumps(rows, ensure_ascii=False).replace("</", "<\\/")
    escaped_hash = html.escape(registry_sha256)
    return f"""<!doctype html><html lang=\"tr\"><meta charset=\"utf-8\"><title>M2 Turkish fact review</title>
<style>body{{font:15px system-ui;max-width:1100px;margin:24px auto;padding:0 16px}}article{{border:1px solid #ccc;border-radius:10px;padding:12px;margin:10px 0}}button{{padding:8px 12px}}.meta{{color:#555}}</style>
<h1>M2 Branch-B Türkçe fact review</h1><p class=\"meta\">Registry SHA-256: {escaped_hash}. Tüm 250 satırı usable veya issue olarak işaretle.</p>
<label>Reviewer <input id=\"reviewer\"></label><button id=\"export\">JSONL indir</button><div id=\"list\"></div>
<script>const rows={data};const state={{}};const list=document.getElementById('list');
for(const r of rows){{const a=document.createElement('article');a.innerHTML=`<b>${{r.fact_id}}</b> · ${{r.relation}}<p>${{r.text}}</p><label><input type=radio name=\"${{r.fact_id}}\" value=usable> usable</label> <label><input type=radio name=\"${{r.fact_id}}\" value=issue> issue</label> <input placeholder=\"not\" class=note>`;a.onchange=e=>{{if(e.target.type==='radio')state[r.fact_id]={{verdict:e.target.value,notes:a.querySelector('.note').value||null}}}};a.querySelector('.note').oninput=e=>{{if(state[r.fact_id])state[r.fact_id].notes=e.target.value||null}};list.appendChild(a)}}
document.getElementById('export').onclick=()=>{{const reviewer=document.getElementById('reviewer').value.trim();if(!reviewer)return alert('Reviewer gerekli');const missing=rows.filter(r=>!state[r.fact_id]);if(missing.length)return alert(missing.length+' satır eksik');const out=rows.map(r=>JSON.stringify({{schema_version:1,fact_id:r.fact_id,fact_registry_sha256:'{escaped_hash}',verdict:state[r.fact_id].verdict,reviewer,notes:state[r.fact_id].notes}})).join('\\n')+'\\n';const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([out],{{type:'application/x-ndjson'}}));a.download='m2_fact_review_{escaped_hash[:12]}.jsonl';a.click();URL.revokeObjectURL(a.href)}};</script></html>"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--execution-enabled", action="store_true")
    args = parser.parse_args()
    if not args.execution_enabled:
        raise PermissionError("Readiness evidence execution requires the exact authorized launcher")
    repo = args.repo_root.resolve()
    config_path = (repo / args.config).resolve() if not args.config.is_absolute() else args.config
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    root = Path(config["output"]["root"]).resolve()
    _validate_precreated_root(root, str(config["contract_id"]))

    block_manifest = Path(config["blocks"]["manifest"]).resolve()
    final_audit = Path(config["blocks"]["root"]) / "control/final_audit.json"
    facts_path = Path(config["blocks"]["fact_registry"]).resolve()
    _assert_file(block_manifest, str(config["blocks"]["manifest_sha256"]))
    _assert_file(final_audit, str(config["blocks"]["final_audit_sha256"]))
    _assert_file(facts_path, str(config["blocks"]["fact_sha256"]))
    blocks = _json(block_manifest)
    if blocks.get("status") != "EXACT_THREE_MODEL_M2_BLOCKS_MATERIALIZED":
        raise ValueError("Exact block family PASS is absent")
    if _json(final_audit).get("manifest_sha256") != sha256_file(block_manifest):
        raise ValueError("Block final-audit chain drift")

    fact_rows = _rows(facts_path)
    ids = [str(row.get("fact_id", "")) for row in fact_rows]
    if len(fact_rows) != 250 or len(set(ids)) != 250 or any(not value for value in ids):
        raise ValueError("Exact 250-fact registry identity drift")
    review_rows = [
        {"index": index, "fact_id": str(row["fact_id"]), "relation": str(row["relation"]), "text": str(row["text"])}
        for index, row in enumerate(fact_rows)
    ]

    parent_models: dict[str, Any] = {}
    sizes: dict[str, int] = {}
    for role in ROLES:
        parent_models[role], sizes[role] = _parent(role, config["parents"][role])
    parent_registry = {
        "schema_version": 1,
        "status": "EXACT_M1_PARENT_REGISTRY_PASS",
        "checkpoint": "epoch-036",
        "seed": 42,
        "models": parent_models,
        "model_weight_access": "read_only_hash_validation",
        "training": False,
    }
    write_json(root / "parent_registry.json", parent_registry)

    model_checkpoint_bytes = 20 * sum(sizes.values())
    preserved_smoke_estimate = 5 * sum(sizes.values())
    active_training_estimate = 5 * sum(sizes.values())
    subtotal = int(config["blocks"]["root_bytes"]) + model_checkpoint_bytes + preserved_smoke_estimate + active_training_estimate + int(config["output"]["fixed_headroom_bytes"])
    required = int(subtotal * float(config["output"]["storage_safety_multiplier"]))
    usage = shutil.disk_usage(root)
    inodes = os.statvfs(root).f_favail
    if usage.free < required or inodes < int(config["output"]["minimum_free_inodes"]):
        raise ValueError("Scratch storage/inode gate failed for the conservative six-run family estimate")
    write_json(root / "storage_estimate.json", {
        "schema_version": 1,
        "status": "M2_STORAGE_ESTIMATE_PASS",
        "per_role_model_only_bytes": sizes,
        "sixty_model_only_checkpoints_bytes": model_checkpoint_bytes,
        "preserved_optimizer_smoke_estimate_bytes": preserved_smoke_estimate,
        "three_concurrent_active_training_estimate_bytes": active_training_estimate,
        "fixed_headroom_bytes": int(config["output"]["fixed_headroom_bytes"]),
        "safety_multiplier": float(config["output"]["storage_safety_multiplier"]),
        "required_free_bytes": required,
        "observed_free_bytes": usage.free,
        "observed_free_inodes": inodes,
    })
    review_path = root / "fact_review_packet.jsonl"
    review_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in review_rows), encoding="utf-8")
    (root / "fact_review.html").write_text(_review_html(review_rows, sha256_file(facts_path)), encoding="utf-8")

    output_dir = Path(config["output"]["config_root"]).resolve()
    training_root = Path(config["output"]["future_training_root"]).resolve()
    env = {**os.environ, "PYTHONPATH": f"{repo / 'src'}:{repo}"}
    subprocess.run([
        sys.executable, str(repo / "scripts/m2/prepare_three_model_oscar_m2_training_family.py"),
        "--plan", str(repo / config["repository"]["scientific_plan"]),
        "--preparation-config", str(repo / config["repository"]["preparation_config"]),
        "--block-manifest", str(block_manifest), "--parent-registry", str(root / "parent_registry.json"),
        "--output-dir", str(output_dir), "--training-output-root", str(training_root),
    ], check=True, env=env)
    subprocess.run([
        sys.executable, str(repo / "scripts/m2/validate_three_model_oscar_m2_training_family.py"),
        "--config-manifest", str(output_dir / "config_manifest.json"),
        "--output", str(root / "config_validation.json"),
    ], check=True, env=env)

    artifacts = []
    for path in sorted(
        item
        for item in root.rglob("*")
        if item.is_file()
        and "control" not in item.relative_to(root).parts
        and "logs" not in item.relative_to(root).parts
    ):
        artifacts.append({"path": str(path.relative_to(root)), "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    write_json(root / "evidence_manifest.json", {
        "schema_version": 1,
        "status": "M2_TRAINING_READINESS_EVIDENCE_PASS",
        "artifacts": artifacts,
        "fact_review_complete": False,
        "optimizer_smoke_complete": False,
        "training_authorized": False,
        "ready_to_train": False,
    })
    write_json(root / "control/final_audit.json", {
        "schema_version": 1,
        "status": "EVIDENCE_PREPARED_AWAITING_FACT_REVIEW_AND_GPU_SMOKE",
        "evidence_manifest_sha256": sha256_file(root / "evidence_manifest.json"),
        "model_weights_accessed_read_only": True,
        "gpu": False,
        "training": False,
        "evaluation": False,
        "ready_to_train": False,
    })
    print(root / "control/final_audit.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
