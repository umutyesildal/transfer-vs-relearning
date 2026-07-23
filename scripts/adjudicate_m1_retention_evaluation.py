#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from transfer_vs_relearning.evaluation.general_capability import has_lexical_content
from transfer_vs_relearning.utils.io import write_csv, write_json


GATE_KEYS = (
    "exact_global_gate",
    "exact_relation_gate",
    "heldout_ab_gate",
    "heldout_cd_gate",
    "robust_global_gate",
    "robust_relation_gate",
    "ppl_gate",
)


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _completed_general_dir(root: Path, label: str) -> Path:
    matches: list[Path] = []
    for path in (root / "general_capability" / label).glob("*/summary_metrics.json"):
        payload = _json(path)
        if payload.get("completion_status", payload.get("status")) in {"complete", "completed"}:
            matches.append(path.parent)
    if len(matches) != 1:
        raise FileNotFoundError(f"Expected one completed general result for {label}, found {len(matches)}")
    return matches[0]


def adjudicate_rows(root: Path, original_rows: list[dict]) -> list[dict]:
    adjudicated: list[dict] = []
    for original in original_rows:
        row = dict(original)
        run_dir = _completed_general_dir(root, str(row["label"]))
        generations = _jsonl(run_dir / "generations.jsonl")
        lexical_empty_rows = [item for item in generations if not has_lexical_content(str(item["continuation"]))]
        short_rows = [item for item in generations if bool(item["empty_or_near_empty"])]
        intrusion_count = int(row["synthetic_subject_intrusion_count"])
        factual_and_ppl = all(bool(row[key]) for key in GATE_KEYS)
        corrected_integrity = not lexical_empty_rows and intrusion_count == 0
        row.update(
            {
                "legacy_near_empty_by_token_length_count": len(short_rows),
                "lexical_empty_generation_count": len(lexical_empty_rows),
                "lexical_empty_prompt_ids": [item["prompt_id"] for item in lexical_empty_rows],
                "short_but_lexical_prompt_ids": [
                    item["prompt_id"] for item in short_rows if has_lexical_content(str(item["continuation"]))
                ],
                "factual_robustness_and_ppl_gates_pass": factual_and_ppl,
                "corrected_generic_integrity_gate": corrected_integrity,
                "all_corrected_gates_pass": factual_and_ppl and corrected_integrity,
            }
        )
        adjudicated.append(row)
    return adjudicated


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wave-root", type=Path, required=True)
    args = parser.parse_args()
    root = args.wave_root.resolve()
    original_path = root / "retention_checkpoint_summary.json"
    original = _json(original_path)
    original_rows = list(original["rows"])
    if len(original_rows) != 22:
        raise ValueError(f"Expected 22 frozen summary rows, found {len(original_rows)}")

    rows = adjudicate_rows(root, original_rows)
    conditions = sorted({str(row["condition"]) for row in rows})
    passing: dict[str, list[int]] = {}
    earliest: dict[str, int | None] = {}
    for condition in conditions:
        steps = sorted(
            int(row["checkpoint_step"])
            for row in rows
            if row["condition"] == condition and row["all_corrected_gates_pass"]
        )
        passing[condition] = steps
        earliest[condition] = steps[0] if steps else None

    replay_step = earliest.get("replay_w0_5")
    corrected_decision = "replicate_replay_seed43" if replay_step is not None else "retention_remediation_failed"
    payload = {
        "status": "complete",
        "adjudication_type": "post_outcome_evaluator_correction",
        "original_frozen_summary": str(original_path),
        "original_frozen_decision": original["decision"],
        "original_frozen_selection_rule": original["selection_rule"],
        "correction": {
            "thresholds_changed": False,
            "legacy_diagnostic_preserved": "empty_or_near_empty / token_ids <= 2",
            "corrected_hard_empty_rule": "decoded continuation contains no Unicode letter or number",
            "synthetic_intrusion_rule_changed": False,
        },
        "rows": rows,
        "corrected_passing_checkpoints": passing,
        "corrected_earliest_passing_checkpoint": earliest,
        "corrected_decision": corrected_decision,
        "replication_candidate": (
            {"condition": "replay_w0_5", "checkpoint_step": replay_step} if replay_step is not None else None
        ),
        "scientific_status": "discovery_only_requires_independent_seed43_replication",
    }
    csv_path = root / "retention_checkpoint_adjudicated_summary.csv"
    json_path = root / "retention_checkpoint_adjudicated_summary.json"
    write_csv(csv_path, rows)
    write_json(json_path, payload)
    print(csv_path)
    print(json_path)


if __name__ == "__main__":
    main()
