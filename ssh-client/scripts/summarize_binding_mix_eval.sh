#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

remote_cmd=$(cat <<'EOF'
cd /vol/fob-vol6/mi25/yesildau/transfer-vs-relearning

/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python - <<'PY'
import csv
import json
from pathlib import Path

repo = Path("/vol/fob-vol6/mi25/yesildau/transfer-vs-relearning")
root = repo / "runs/evaluation"
checkpoints = ["checkpoint-220", "checkpoint-440", "checkpoint-660", "checkpoint-879"]
base = "m1_smollm2_360m_english_facts_binding_mix_lr5e-5_ep1"


def latest_csv(run_root: Path) -> Path:
    candidates = sorted(run_root.glob("*/per_fact_results.csv"))
    if not candidates:
        raise FileNotFoundError(run_root)
    return candidates[-1]


def load_rows(path: Path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return [row for row in reader if row["language"] == "en"]


def rank1_ids(rows):
    return {row["fact_id"] for row in rows if int(row["correct_rank_mean"]) == 1}


def metrics(rows):
    n = len(rows)
    ranks = [int(row["correct_rank_mean"]) for row in rows]
    margins = [float(row["margin"]) for row in rows]
    return {
        "top1": sum(rank == 1 for rank in ranks) / n,
        "top5": sum(rank <= 5 for rank in ranks) / n,
        "mrr": sum(1.0 / rank for rank in ranks) / n,
        "mean_rank": sum(ranks) / n,
        "mean_margin": sum(margins) / n,
        "top1_count": sum(rank == 1 for rank in ranks),
    }


def relation_metrics(direct_rows, qa_rows):
    output = {}
    relations = sorted({row["relation"] for row in direct_rows})
    for relation in relations:
        direct_relation = [row for row in direct_rows if row["relation"] == relation]
        qa_relation = [row for row in qa_rows if row["relation"] == relation]
        direct_top1 = rank1_ids(direct_relation)
        qa_top1 = rank1_ids(qa_relation)
        output[relation] = {
            "direct_top1_count": len(direct_top1),
            "qa_top1_count": len(qa_top1),
            "overlap": len(direct_top1 & qa_top1),
        }
    return output


results = []
for checkpoint in checkpoints:
    direct_csv = latest_csv(root / f"{base}_{checkpoint}_direct")
    qa_csv = latest_csv(root / f"{base}_{checkpoint}_qa_matched")
    direct_rows = load_rows(direct_csv)
    qa_rows = load_rows(qa_csv)
    results.append(
        {
            "checkpoint": checkpoint,
            "direct": metrics(direct_rows),
            "qa": metrics(qa_rows),
            "overlap": len(rank1_ids(direct_rows) & rank1_ids(qa_rows)),
            "union": len(rank1_ids(direct_rows) | rank1_ids(qa_rows)),
            "by_relation": relation_metrics(direct_rows, qa_rows),
            "direct_csv": str(direct_csv.relative_to(repo)),
            "qa_csv": str(qa_csv.relative_to(repo)),
        }
    )

print(json.dumps(results, indent=2))
PY
EOF
)

quoted_remote_cmd=$(printf '%q' "$remote_cmd")
exec "$SCRIPT_DIR/hu_ssh_expect" "bash -lc $quoted_remote_cmd"
