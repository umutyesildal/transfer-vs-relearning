#!/usr/bin/env python3
"""Run one exact, offline OSCAR Phase-2 evidence/accounting pass."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import yaml

from transfer_vs_relearning.corpora.vngrs.d0_bundle import write_d0_failure
from transfer_vs_relearning.corpora.vngrs.d0_inputs_v3 import load_source_objects_v3
from transfer_vs_relearning.corpora.vngrs.d0_phase2 import run_oscar_phase2_evidence
from transfer_vs_relearning.corpora.vngrs.d0_review import read_jsonl_rows
from transfer_vs_relearning.corpora.vngrs.d0_runtime import FrozenTokenizerAdapter
from transfer_vs_relearning.corpora.vngrs.sample_transport import SOURCE_ROOT


CONFIG = Path("configs/corpora/vngrs_m2_oscar_phase2_evidence_v1.yaml")
SOURCE_V3_ROOT = Path("/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v3")
SPLIT_ROOT = Path("/vol/tmp2/yesildau/vngrs_m2_oscar_split_review_v1")
COVERAGE_ROOT = Path("/vol/tmp2/yesildau/vngrs_m2_oscar_review_coverage_repair_v1")
OUTPUT_ROOT = Path("/vol/tmp2/yesildau/vngrs_m2_oscar_phase2_evidence_v1")
INPUT_HASHES = {
    SOURCE_V3_ROOT / "control/materialization_v3.json": "bb413e9acafd0d891ea9c4461abc77acea1c737489560650db56dacf781dbd10",
    SPLIT_ROOT / "control/phase1_state.json": "a09c0c62fffb8536b9917cc9755a40c35eb8c0f862f5b41d044f3de8f4e7d609",
    SPLIT_ROOT / "control/final_audit.json": "3add7667d202cb5547dc0847c9ad302a47e7e57cd7fb8f2f43fd4211dba86e7e",
    SPLIT_ROOT / "splits/train_document_ids.jsonl": "90b74fbcfe62107693c35161fc328a6e43b13a830fc9590cc9810d3e99955aac",
    SPLIT_ROOT / "splits/heldout_document_ids.jsonl": "dc30629fe76ca722745fcd0148021de6c042218ed2994281d52d13c06011dc91",
    COVERAGE_ROOT / "control/coverage_state.json": "3c0305d89f1496ea397694e18e7888e9d1dc58724ac588f3aa797240f73f24f6",
    COVERAGE_ROOT / "control/final_audit.json": "6ce5f1f7b13fa61ae3f9c021b237b0464e4989ae179dc73fe32030049772c177",
    COVERAGE_ROOT / "reports/quartile_population_inventory.json": "8ff29ad8d72ad81616d4af3dee5951e55bde2752254988dad76c9cbbb03dd51f",
    COVERAGE_ROOT / "reports/human_review_packet.jsonl": "621d8416f120803cc37f75453f0068a5fecaa60562698f11936b22caa3b75c61",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _comment(value: str) -> None:
    job_id = os.environ.get("SLURM_JOB_ID")
    if not job_id:
        return
    safe = re.sub(r"[^A-Za-z0-9_.:-]+", "_", value)[:240]
    subprocess.run(
        ["scontrol", "update", f"JobId={job_id}", f"Comment={safe}"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _preflight(repo: Path, expected_commit: str, config: dict) -> None:
    if OUTPUT_ROOT.exists():
        raise ValueError("fresh Phase-2 output root is not absent")
    if subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip() != expected_commit:
        raise ValueError("authorized Git commit drift")
    if subprocess.check_output(["git", "status", "--porcelain=v1"], cwd=repo, text=True).strip():
        raise ValueError("reviewed checkout is not clean")
    for path, expected in INPUT_HASHES.items():
        if not path.is_file() or path.is_symlink() or _sha256(path) != expected:
            raise ValueError(f"preserved Phase-2 input drift: {path}")
    local_inputs = {
        repo / config["human_review"]["decisions"]: config["human_review"]["decisions_sha256"],
        repo / config["tokenizers"]["inventory"]: config["tokenizers"]["inventory_sha256"],
    }
    for path, expected in local_inputs.items():
        if not path.is_file() or path.is_symlink() or _sha256(path) != expected:
            raise ValueError(f"repository Phase-2 input drift: {path}")
    usage = shutil.disk_usage(OUTPUT_ROOT.parent)
    stat = os.statvfs(OUTPUT_ROOT.parent)
    if usage.free < config["output"]["minimum_available_bytes"] or stat.f_favail < config["output"]["minimum_available_inodes"]:
        raise ValueError("Phase-2 scratch capacity gate failed")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    config = yaml.safe_load((repo / CONFIG).read_text(encoding="utf-8"))
    try:
        _preflight(repo, args.expected_commit, config)
        inventory = json.loads(
            (repo / config["tokenizers"]["inventory"]).read_text(encoding="utf-8")
        )
        def load_tokenizers():
            return [
                FrozenTokenizerAdapter.load(
                    role=role,
                    snapshot_root=config["tokenizers"]["models"][role]["snapshot_root"],
                    inventory=inventory["models"][role],
                )
                for role in config["tokenizers"]["roles"]
            ]

        result = run_oscar_phase2_evidence(
            SOURCE_V3_ROOT,
            SPLIT_ROOT,
            COVERAGE_ROOT,
            OUTPUT_ROOT,
            load_source_objects_v3(SOURCE_ROOT),
            decisions=read_jsonl_rows(repo / config["human_review"]["decisions"]),
            tokenizers=load_tokenizers,
            expected_document_count=config["source"]["document_count"],
            expected_utf8_bytes=config["source"]["utf8_bytes"],
            execution_enabled=True,
        )
    except Exception as exc:
        if not (OUTPUT_ROOT / "control/d0_failure.json").exists() and not OUTPUT_ROOT.exists():
            write_d0_failure(OUTPUT_ROOT, phase="oscar_phase2_preflight", error=exc)
        _comment(f"OSCAR_PHASE2_FAILED:{type(exc).__name__}:{exc}")
        raise
    _comment("D0_EVIDENCE_COMPLETE_M2_CONTRACT_NOT_FROZEN")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
