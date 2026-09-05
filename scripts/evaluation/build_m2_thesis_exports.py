#!/usr/bin/env python3
"""Build deterministic, thesis-ready exports from the compact M2 result layer.

This module deliberately performs the scientific joins once, outside the browser.  The
corrected paired-subject bootstrap is the only source for the two canonical contrasts;
the older fact-id bootstrap is never read.  All output is derived from Git-retained
compact artifacts and carries an input-manifest digest in ``export_manifest.json``.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import shutil
from pathlib import Path
from typing import Iterable, Mapping


ROOT = Path(__file__).resolve().parents[2]
EXPORT_DIR = ROOT / "paper" / "transfer_or_relearning_wip" / "derived_m2_exports"

MODELS = ("olmo", "qwen", "smollm")
MODEL_LABELS = {"olmo": "OLMo", "qwen": "Qwen", "smollm": "SmolLM"}
ARMS = ("M2-A", "M2-B")
STATES = ("M1", "M2-A", "M2-B")
DIRECTIONS = ("en_to_en", "tr_to_en", "tr_to_tr")
GATE_ORDER = (
    "m2a_en_to_en_drop_at_most_0_05",
    "m2a_oscar_delta_bpb_at_most_minus_0_07400058",
    "m2a_wikitext_delta_bpb_at_most_0_32192809",
    "relearning_ci95_low_above_zero",
    "relearning_point_gain_at_least_0_05",
)
GATE_LABELS = {
    "m2a_en_to_en_drop_at_most_0_05": "M2-A EN-to-EN drop ≤ 0.05",
    "m2a_oscar_delta_bpb_at_most_minus_0_07400058": "M2-A OSCAR BPB delta ≤ −0.07400058",
    "m2a_wikitext_delta_bpb_at_most_0_32192809": "M2-A WikiText BPB delta ≤ 0.32192809",
    "relearning_ci95_low_above_zero": "Relearning 95% CI lower bound > 0",
    "relearning_point_gain_at_least_0_05": "Relearning point gain ≥ 0.05",
}
SOURCE_HASHES = {
    "m0_metrics": ("artifacts/evaluations/m0_three_model_v1/dump/m0_metrics.json", "859b598fdd3509d6e11e5cbf3f9662bc66accd58291bc635aad028185e1bdbbd"),
    "m1_metrics": ("artifacts/evaluations/m1_three_model_v1/dump/m1_metrics.json", "41c2f2c6b722fc25ac48af278f1b318acc5e743b3c48d649fe26259848080462"),
    "m1_trajectory": ("artifacts/evaluations/m1_three_model_v1/dump/m1_trajectory.csv", "0cf33dca248d35c8c6f49bd8856d2ef801d3cfef522f59bde099a9aef72e269b"),
    "m0_m1_comparison": ("artifacts/evaluations/m1_three_model_v1/dump/m0_m1_comparison.csv", "ee0a9f0bc21e8c360c8fc0b9971cd3be3ff76120bc89c55dee60c356a670e68a"),
    "m2_family": ("artifacts/evaluations/m2_three_model_oscar_v1/dump/evaluation_family_result.json", "c04eff5ba1301f5fcd4a318cc3a88d281e389cd05f542e6f6d569826809bcebf"),
    "m2_scientific_analysis": ("artifacts/evaluations/m2_three_model_oscar_v1/dump/scientific_analysis.json", "732c9c23ab795bf3212196d582f8300ca6c02dbf6902c489a1d4ecd6eae6e0ca"),
    "m2_trajectory": ("artifacts/evaluations/m2_three_model_oscar_v1/dump/m2_checkpoint_trajectory.csv", "2e687bb24befc947ec21fa1e0c9040b27e6be2a3dff6da8ea6ab3e30b9e9a18a"),
    "m2_endpoint_breakdown": ("artifacts/evaluations/m2_three_model_oscar_v1/dump/endpoint_relation_form_summary.csv", "4502af97b0878b75b472ada774a6a73c0fe5c9d21b4856702148df09d41d7e9d"),
    "m2_corrected_bootstrap": ("artifacts/evaluations/m2_three_model_oscar_v1/dump/corrected_paired_subject_bootstrap.csv", "e16610d1af87fea1f42a13ae1fcc2bc1e80ee78fe7343f91576858505563750d"),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def source_manifest(root: Path) -> tuple[dict, str]:
    sources = []
    for key, (relative, expected) in SOURCE_HASHES.items():
        path = root / relative
        require(path.is_file(), f"missing source: {relative}")
        actual = sha256(path)
        require(actual == expected, f"source hash mismatch for {relative}: {actual} != {expected}")
        sources.append({"id": key, "path": relative, "sha256": actual, "bytes": path.stat().st_size})
    manifest = {"schema_version": "m2-thesis-input-manifest-v1", "sources": sources}
    encoded = canonical_json(manifest)
    return manifest, hashlib.sha256(encoded).hexdigest()


def validate_and_load(root: Path) -> tuple[dict, str, dict]:
    manifest, manifest_hash = source_manifest(root)
    m0 = load_json(root / SOURCE_HASHES["m0_metrics"][0])
    m1 = load_json(root / SOURCE_HASHES["m1_metrics"][0])
    family = load_json(root / SOURCE_HASHES["m2_family"][0])
    analysis = load_json(root / SOURCE_HASHES["m2_scientific_analysis"][0])
    trajectory = load_csv(root / SOURCE_HASHES["m2_trajectory"][0])
    breakdown = load_csv(root / SOURCE_HASHES["m2_endpoint_breakdown"][0])
    bootstrap = load_csv(root / SOURCE_HASHES["m2_corrected_bootstrap"][0])

    require(m0.get("state") == "M0", "M0 compact dump has an unexpected state")
    require(m1.get("state") == "M1", "M1 compact dump has an unexpected state")
    require(m1.get("counts", {}).get("complete_states") == 111, "M1 completion count must be 111")
    require(family.get("gpu_complete_count") == 63 and family.get("gpu_task_count") == 63, "M2 completion must be 63/63")
    require(set(analysis.get("roles", {})) == set(MODELS), "M2 scientific analysis must contain exactly three models")
    require(len(trajectory) == 60, f"M2 trajectory must contain 60 rows, got {len(trajectory)}")
    require(len(breakdown) == 66, f"M2 endpoint breakdown must contain 66 rows, got {len(breakdown)}")
    require(len(bootstrap) == 39, f"corrected bootstrap must contain 39 rows, got {len(bootstrap)}")
    require(len({(r["model"], r["arm"], r["update"]) for r in trajectory}) == 60, "duplicate M2 trajectory key")
    require(len({(r["model"], r["axis"], r["key"], r["arm"]) for r in breakdown}) == 66, "duplicate endpoint breakdown key")
    require(len({(r["model"], r["contrast"], r["subset"]) for r in bootstrap}) == 39, "duplicate bootstrap subset key")
    require(set(r["model"] for r in trajectory) == set(MODELS), "M2 trajectory model vocabulary mismatch")
    require(set(r["arm"] for r in trajectory) == set(ARMS), "M2 trajectory arm vocabulary mismatch")
    require(all(int(r["n"]) == 1500 for r in trajectory), "checkpoint factual denominator must be 1500")
    require({r["axis"] for r in breakdown} == {"relation", "form_id", "scaffold_id"}, "breakdown axes mismatch")
    require({r["axis"]: sum(1 for x in breakdown if x["axis"] == r["axis"]) for r in breakdown} == {"relation": 30, "form_id": 24, "scaffold_id": 12}, "breakdown row counts mismatch")
    require(all(int(r["n_subjects"]) == 100 for r in bootstrap), "bootstrap subject denominator must be 100")

    canonical = {}
    for row in bootstrap:
        key = (row["model"], row["contrast"], row["subset"])
        canonical[key] = {k: float(row[k]) if k not in {"model", "contrast", "subset"} else row[k] for k in row}
    expected = {
        ("olmo", "transfer", "all"): -0.141,
        ("olmo", "relearning", "all"): 0.020,
        ("qwen", "transfer", "all"): -0.307,
        ("qwen", "relearning", "all"): 0.0435,
        ("smollm", "transfer", "all"): -0.16175,
        ("smollm", "relearning", "all"): 0.0035,
    }
    for key, value in expected.items():
        require(math.isclose(canonical[key]["estimate"], value, abs_tol=1e-12), f"canonical estimate mismatch for {key}")

    for model in MODELS:
        role = analysis["roles"][model]
        require(role.get("all_primary_gates_pass") is False, f"{model} must not pass all primary gates")
        require(set(role.get("gates", {})) == set(GATE_ORDER), f"{model} gate vocabulary mismatch")
        require(set(role.get("state_metrics", {})) == set(STATES), f"{model} state vocabulary mismatch")
        for state in STATES:
            require(set(role["state_metrics"][state]) == set(DIRECTIONS), f"{model}/{state} direction vocabulary mismatch")
            require(all(role["state_metrics"][state][direction]["n"] == 4000 for direction in DIRECTIONS), f"{model}/{state} endpoint denominator mismatch")
    return manifest, manifest_hash, {"m0": m0, "m1": m1, "family": family, "analysis": analysis, "trajectory": trajectory, "breakdown": breakdown, "bootstrap": bootstrap}


def fmt(value: float, digits: int = 6) -> str:
    return f"{value:.{digits}f}".rstrip("0").rstrip(".") if value else "0"


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[Mapping[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def effects_rows(data: dict) -> list[dict]:
    rows = []
    for row in data["bootstrap"]:
        if row["subset"] != "all" or row["contrast"] not in {"transfer", "relearning"}:
            continue
        estimate = float(row["estimate"])
        rows.append({
            "model": row["model"], "model_label": MODEL_LABELS[row["model"]], "contrast": row["contrast"],
            "estimand": "M2-A minus M1" if row["contrast"] == "transfer" else "M2-B minus M2-A",
            "subset": row["subset"], "n_subjects": int(row["n_subjects"]), "estimate": fmt(estimate),
            "ci95_low": fmt(float(row["ci95_low"])), "ci95_high": fmt(float(row["ci95_high"])),
            "estimate_pp": fmt(100 * estimate, 4), "ci95_low_pp": fmt(100 * float(row["ci95_low"]), 4),
            "ci95_high_pp": fmt(100 * float(row["ci95_high"]), 4),
            "threshold_zero_pp": "0", "threshold_relearning_pp": "5" if row["contrast"] == "relearning" else "",
            "interval_source": "corrected_paired_subject_bootstrap",
        })
    return sorted(rows, key=lambda r: (MODELS.index(r["model"]), ("transfer", "relearning").index(r["contrast"])))


def endpoint_rows(data: dict) -> list[dict]:
    rows = []
    for model in MODELS:
        for state in STATES:
            for direction in DIRECTIONS:
                metric = data["analysis"]["roles"][model]["state_metrics"][state][direction]
                rows.append({"model": model, "model_label": MODEL_LABELS[model], "state": state, "direction": direction, "n": metric["n"], "top1_accuracy": fmt(metric["top1_accuracy"]), "top1_percent": fmt(100 * metric["top1_accuracy"], 4)})
    return rows


def trajectory_rows(data: dict) -> list[dict]:
    fields = ["model", "arm", "update", "dose_pct", "factual_top1", "n", "oscar_bpb", "trwiki_bpb", "wikitext_bpb", "exact_top1"]
    return [{key: row[key] for key in fields} for row in sorted(data["trajectory"], key=lambda r: (MODELS.index(r["model"]), ARMS.index(r["arm"]), int(r["update"])))]


def breakdown_rows(data: dict, axis: str) -> list[dict]:
    rows = []
    for row in sorted((r for r in data["breakdown"] if r["axis"] == axis), key=lambda r: (MODELS.index(r["model"]), ARMS.index(r["arm"]), r["key"])):
        rows.append({"model": row["model"], "model_label": MODEL_LABELS[row["model"]], "arm": row["arm"], "axis": row["axis"], "key": row["key"], "n": int(row["n"]), "top1": int(row["top1"]), "accuracy": row["accuracy"], "accuracy_percent": fmt(100 * float(row["accuracy"]), 4)})
    return rows


def gate_rows(data: dict) -> list[dict]:
    rows = []
    for model in MODELS:
        role = data["analysis"]["roles"][model]
        for gate in GATE_ORDER:
            rows.append({"model": model, "model_label": MODEL_LABELS[model], "gate_id": gate, "criterion": GATE_LABELS[gate], "pass": str(bool(role["gates"][gate])).lower(), "gate_type": "primary"})
        rows.append({"model": model, "model_label": MODEL_LABELS[model], "gate_id": "all_primary_gates_pass", "criterion": "All frozen primary gates pass", "pass": "false", "gate_type": "summary"})
    return rows


def svg_header(title: str, description: str, width: int, height: int) -> str:
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img"><title>{title}</title><desc>{description}</desc><style>text{{font-family:Arial,sans-serif;fill:#172033}} .grid{{stroke:#d7dce5;stroke-width:1}} .axis{{stroke:#4b5563;stroke-width:1}} .small{{font-size:12px}} .label{{font-size:13px}} .title{{font-size:18px;font-weight:700}} .note{{font-size:11px;fill:#526071}} </style>'


COLORS = {"olmo": "#2563a6", "qwen": "#c2410c", "smollm": "#15803d"}
ARM_COLORS = {"M2-A": "#2563a6", "M2-B": "#d97706"}


def forest_svg(rows: list[dict]) -> str:
    width, height = 920, 500
    left, right, top, bottom = 210, 870, 60, 70
    xmin, xmax = -35, 10
    x = lambda value: left + (value - xmin) / (xmax - xmin) * (right - left)
    out = [svg_header("M2 primary effects", "Corrected paired-subject bootstrap intervals for transfer and relearning; zero and +5 percentage-point threshold are distinct.", width, height)]
    out.append('<text class="title" x="24" y="30">M2 primary effects (percentage points)</text>')
    for tick in (-30, -20, -10, 0, 5, 10):
        cls = "axis" if tick == 0 else "grid"
        out.append(f'<line class="{cls}" x1="{x(tick):.1f}" y1="{top-10}" x2="{x(tick):.1f}" y2="{height-bottom}"/>')
        out.append(f'<text class="small" x="{x(tick):.1f}" y="{height-bottom+20}" text-anchor="middle">{tick}</text>')
    out.append(f'<line x1="{x(5):.1f}" y1="{top-10}" x2="{x(5):.1f}" y2="{height-bottom}" stroke="#7c3aed" stroke-width="2" stroke-dasharray="6 4"/>')
    out.append(f'<text class="note" x="{x(5)+5:.1f}" y="{top-14}">+5 pp gate</text>')
    y = top + 30
    for row in rows:
        color = COLORS[row["model"]]
        estimate, low, high = float(row["estimate_pp"]), float(row["ci95_low_pp"]), float(row["ci95_high_pp"])
        out.append(f'<text class="label" x="{left-12}" y="{y+4}" text-anchor="end">{MODEL_LABELS[row["model"]]} · {row["contrast"]}</text>')
        out.append(f'<line x1="{x(low):.1f}" y1="{y}" x2="{x(high):.1f}" y2="{y}" stroke="{color}" stroke-width="3"/>')
        out.append(f'<line x1="{x(low):.1f}" y1="{y-6}" x2="{x(low):.1f}" y2="{y+6}" stroke="{color}" stroke-width="2"/><line x1="{x(high):.1f}" y1="{y-6}" x2="{x(high):.1f}" y2="{y+6}" stroke="{color}" stroke-width="2"/>')
        out.append(f'<circle cx="{x(estimate):.1f}" cy="{y}" r="5" fill="{color}"/><text class="small" x="{min(x(high)+8,right):.1f}" y="{y+4}">{estimate:.2f} [{low:.2f}, {high:.2f}]</text>')
        y += 54
    out.append(f'<text class="note" x="{left}" y="{height-18}">Negative transfer is shown on the same scale as positive relearning; intervals use 100 subjects and 10,000 draws.</text></svg>')
    return "".join(out)


def endpoint_svg(rows: list[dict]) -> str:
    width, height = 1120, 620
    out = [svg_header("M1 and M2 endpoint state comparison", "Top-1 factual accuracy across three language directions and three model states.", width, height)]
    out.append('<text class="title" x="24" y="30">Endpoint factual access by state</text>')
    for i, state in enumerate(STATES):
        out.append(f'<rect x="{840+i*85}" y="18" width="12" height="12" fill="{("#64748b", ARM_COLORS.get(state,"#64748b"))}"/><text class="small" x="{857+i*85}" y="28">{state}</text>')
    panel_left, panel_w = 75, 330
    max_y = 100
    for p, direction in enumerate(DIRECTIONS):
        left = panel_left + p * 350
        out.append(f'<text class="label" x="{left+panel_w/2}" y="60" text-anchor="middle">{direction.replace("_", "-").upper()}</text>')
        for tick in (0, 25, 50, 75, 100):
            yy = 520 - tick / max_y * 400
            out.append(f'<line class="grid" x1="{left}" y1="{yy:.1f}" x2="{left+panel_w}" y2="{yy:.1f}"/><text class="small" x="{left-8}" y="{yy+4}" text-anchor="end">{tick}</text>')
        out.append(f'<line class="axis" x1="{left}" y1="120" x2="{left}" y2="520"/><line class="axis" x1="{left}" y1="520" x2="{left+panel_w}" y2="520"/>')
        for m, model in enumerate(MODELS):
            center = left + 55 + m * 110
            for s, state in enumerate(STATES):
                row = next(r for r in rows if r["model"] == model and r["state"] == state and r["direction"] == direction)
                value = float(row["top1_percent"])
                bar_w, xx = 20, center + (s-1)*24 - 10
                color = "#64748b" if state == "M1" else ARM_COLORS[state]
                yy = 520 - value / 100 * 400
                out.append(f'<rect x="{xx:.1f}" y="{yy:.1f}" width="{bar_w}" height="{520-yy:.1f}" fill="{color}"/><text class="small" x="{xx+bar_w/2:.1f}" y="{yy-4:.1f}" text-anchor="middle">{value:.1f}</text>')
            out.append(f'<text class="small" x="{center}" y="545" text-anchor="middle">{MODEL_LABELS[model]}</text>')
    out.append('<text class="note" x="75" y="590">Endpoint denominator: 4,000 prompts per direction and state. M2-A and M2-B are parallel sibling arms from the same M1 parent.</text></svg>')
    return "".join(out)


def trajectory_svg(rows: list[dict]) -> str:
    metrics = [("factual_top1", "Factual top-1", 0, 1), ("oscar_bpb", "OSCAR BPB", 1, 2.2), ("trwiki_bpb", "trwiki BPB", 1, 2.2), ("wikitext_bpb", "WikiText BPB", 0.7, 1.2), ("exact_top1", "Exact top-1", 0, 1)]
    width, height = 1540, 900
    out = [svg_header("M2 dose trajectories", "Ten checkpoint trajectories for factual, exact-prefix and BPB metrics; M2-A and M2-B shown separately.", width, height)]
    out.append('<text class="title" x="24" y="30">M2 dose trajectories</text>')
    for mi, model in enumerate(MODELS):
        for pi, (key, label, ymin, ymax) in enumerate(metrics):
            left = 60 + pi * 295; top = 75 + mi * 260; plot_w, plot_h = 245, 180
            out.append(f'<text class="label" x="{left+plot_w/2}" y="{top-20}" text-anchor="middle">{MODEL_LABELS[model]} · {label}</text>')
            for tick in (0, 50, 100):
                yy = top + plot_h - (tick/100)*(plot_h)
                out.append(f'<line class="grid" x1="{left}" y1="{yy:.1f}" x2="{left+plot_w}" y2="{yy:.1f}"/><text class="small" x="{left-5}" y="{yy+4:.1f}" text-anchor="end">{(ymin+(ymax-ymin)*tick/100):.2f}</text>')
            out.append(f'<line class="axis" x1="{left}" y1="{top}" x2="{left}" y2="{top+plot_h}"/><line class="axis" x1="{left}" y1="{top+plot_h}" x2="{left+plot_w}" y2="{top+plot_h}"/>')
            for arm in ARMS:
                subset = sorted((r for r in rows if r["model"] == model and r["arm"] == arm), key=lambda r: int(r["update"]))
                points = []
                for r in subset:
                    xx = left + float(r["dose_pct"]) / 100 * plot_w
                    value = float(r[key]); yy = top + plot_h - (value-ymin)/(ymax-ymin)*plot_h
                    points.append(f"{xx:.1f},{yy:.1f}")
                out.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="{ARM_COLORS[arm]}" stroke-width="2"/>')
            out.append(f'<text class="note" x="{left+plot_w}" y="{top+plot_h+18}" text-anchor="end">dose (%)</text>')
    out.append(f'<line x1="{width-210}" y1="35" x2="{width-190}" y2="35" stroke="{ARM_COLORS["M2-A"]}" stroke-width="3"/><text class="small" x="{width-184}" y="39">M2-A</text><line x1="{width-125}" y1="35" x2="{width-105}" y2="35" stroke="{ARM_COLORS["M2-B"]}" stroke-width="3"/><text class="small" x="{width-99}" y="39">M2-B</text>')
    out.append('<text class="note" x="60" y="885">Checkpoint factual top-1 uses n=1,500 probes; it is not interchangeable with the 12,000-probe endpoint suite.</text></svg>')
    return "".join(out)


def breakdown_svg(rows: list[dict], axis: str, title: str, filename_note: str) -> str:
    keys = sorted({r["key"] for r in rows})
    width, height = 1060, 560
    out = [svg_header(title, f"Endpoint {axis} breakdown for M2-A and M2-B.", width, height), f'<text class="title" x="24" y="30">{title}</text>']
    left, plot_w, top, plot_h = 90, 900, 80, 380
    for tick in (0, 25, 50, 75, 100):
        yy = top + plot_h - tick / 100 * plot_h
        out.append(f'<line class="grid" x1="{left}" y1="{yy:.1f}" x2="{left+plot_w}" y2="{yy:.1f}"/><text class="small" x="{left-8}" y="{yy+4:.1f}" text-anchor="end">{tick}</text>')
    group_w = plot_w / len(keys)
    for i, key in enumerate(keys):
        center = left + group_w * (i + .5)
        for j, arm in enumerate(ARMS):
            row = next(r for r in rows if r["key"] == key and r["arm"] == arm)
            val = float(row["accuracy_percent"]); bw = 28; xx = center + (j-.5)*36 - bw/2; yy = top + plot_h - val/100*plot_h
            out.append(f'<rect x="{xx:.1f}" y="{yy:.1f}" width="{bw}" height="{top+plot_h-yy:.1f}" fill="{ARM_COLORS[arm]}"/><text class="small" x="{xx+bw/2:.1f}" y="{yy-4:.1f}" text-anchor="middle">{val:.1f}</text>')
        out.append(f'<text class="small" x="{center:.1f}" y="{top+plot_h+25}" text-anchor="middle">{key.replace("_", " ")}</text>')
    out.append(f'<line x1="{left+plot_w-115}" y1="45" x2="{left+plot_w-95}" y2="45" stroke="{ARM_COLORS["M2-A"]}" stroke-width="3"/><text class="small" x="{left+plot_w-90}" y="49">M2-A</text><line x1="{left+plot_w-45}" y1="45" x2="{left+plot_w-25}" y2="45" stroke="{ARM_COLORS["M2-B"]}" stroke-width="3"/><text class="small" x="{left+plot_w-20}" y="49">M2-B</text>')
    out.append(f'<text class="note" x="{left}" y="535">Values are endpoint top-1 accuracy (%); source axis: {filename_note}.</text></svg>')
    return "".join(out)


def build(root: Path = ROOT, output_dir: Path = EXPORT_DIR) -> dict:
    manifest, manifest_hash, data = validate_and_load(root)
    output_dir.mkdir(parents=True, exist_ok=True)
    for path in output_dir.iterdir():
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)

    files = {}
    def save(name: str, content: str | bytes) -> None:
        path = output_dir / name
        path.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))
        files[name] = {"sha256": sha256(path), "bytes": path.stat().st_size, "input_manifest_sha256": manifest_hash}

    effect = effects_rows(data)
    endpoint = endpoint_rows(data)
    trajectory = trajectory_rows(data)
    relation = breakdown_rows(data, "relation")
    forms = breakdown_rows(data, "form_id")
    gates = gate_rows(data)
    write_csv(output_dir / "primary_effects.csv", list(effect[0]), effect); files["primary_effects.csv"] = {"sha256": sha256(output_dir / "primary_effects.csv"), "bytes": (output_dir / "primary_effects.csv").stat().st_size, "input_manifest_sha256": manifest_hash}
    write_csv(output_dir / "endpoint_state_comparison.csv", list(endpoint[0]), endpoint); files["endpoint_state_comparison.csv"] = {"sha256": sha256(output_dir / "endpoint_state_comparison.csv"), "bytes": (output_dir / "endpoint_state_comparison.csv").stat().st_size, "input_manifest_sha256": manifest_hash}
    write_csv(output_dir / "dose_trajectories.csv", list(trajectory[0]), trajectory); files["dose_trajectories.csv"] = {"sha256": sha256(output_dir / "dose_trajectories.csv"), "bytes": (output_dir / "dose_trajectories.csv").stat().st_size, "input_manifest_sha256": manifest_hash}
    write_csv(output_dir / "relation_breakdown.csv", list(relation[0]), relation); files["relation_breakdown.csv"] = {"sha256": sha256(output_dir / "relation_breakdown.csv"), "bytes": (output_dir / "relation_breakdown.csv").stat().st_size, "input_manifest_sha256": manifest_hash}
    write_csv(output_dir / "form_breakdown.csv", list(forms[0]), forms); files["form_breakdown.csv"] = {"sha256": sha256(output_dir / "form_breakdown.csv"), "bytes": (output_dir / "form_breakdown.csv").stat().st_size, "input_manifest_sha256": manifest_hash}
    write_csv(output_dir / "gate_table.csv", list(gates[0]), gates); files["gate_table.csv"] = {"sha256": sha256(output_dir / "gate_table.csv"), "bytes": (output_dir / "gate_table.csv").stat().st_size, "input_manifest_sha256": manifest_hash}

    save("primary_forest.svg", forest_svg(effect))
    save("endpoint_state_comparison.svg", endpoint_svg(endpoint))
    save("dose_trajectories.svg", trajectory_svg(trajectory))
    save("relation_breakdown.svg", breakdown_svg(relation, "relation", "Endpoint relation breakdown", "relation"))
    save("form_breakdown.svg", breakdown_svg(forms, "prompt form", "Endpoint prompt-form breakdown", "form_id"))

    summary = f"""---\ntitle: M2 results thesis export package\ninput_manifest_sha256: {manifest_hash}\n---\n\n# M2 results export package\n\nThe canonical estimands are transfer (M2-A minus M1) and relearning (M2-B minus M2-A), both on `tr_to_en` factual access. The two M2 arms are parallel siblings initialized from the same M1 parent; M2-B was not trained from M2-A.\n\n## Corrected all-subject contrasts\n\n| Model | Transfer (pp) | Relearning (pp) |\n|---|---:|---:|\n""" + "\n".join(f"| {r['model_label']} | {next(x['estimate_pp'] for x in effect if x['model']==r['model'] and x['contrast']=='transfer')} | {next(x['estimate_pp'] for x in effect if x['model']==r['model'] and x['contrast']=='relearning')} |" for r in effect if r["contrast"] == "transfer") + """\n\nThe corrected paired-subject bootstrap uses `probe_id`, 100 subjects, eight prompt variants, 10,000 draws and seed 42. The historical `fact_id` bootstrap is superseded and is not used by these exports. Qwen has the strongest descriptive relearning estimate, but its point gain remains below the precommitted +5 percentage-point gate; no model passes all primary gates and no primary model is selected.\n\nCheckpoint factual top-1 uses 1,500 probes and must not be read as the 12,000-probe endpoint suite. Missing values remain missing; no composite score combines factual accuracy, BPB, exact-prefix or capability metrics.\n"""
    save("m2_results_summary.md", summary)
    gate_md = f"""# M2 gate table\n\nInput manifest SHA-256: `{manifest_hash}`\n\n| Model | Criterion | Pass |\n|---|---|:---:|\n""" + "\n".join(f"| {r['model_label']} | {r['criterion']} | {r['pass']} |" for r in gates) + "\n\nAll three `all_primary_gates_pass` values are false.\n"
    save("gate_table.md", gate_md)
    export_manifest = {"schema_version": "m2-thesis-export-manifest-v1", "input_manifest": manifest, "input_manifest_sha256": manifest_hash, "outputs": files}
    (output_dir / "export_manifest.json").write_bytes(canonical_json(export_manifest))
    return export_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root")
    parser.add_argument("--output-dir", type=Path, default=None, help="derived output directory")
    args = parser.parse_args()
    manifest = build(args.root.resolve(), (args.output_dir or (args.root / "paper/transfer_or_relearning_wip/derived_m2_exports")).resolve())
    print(json.dumps({"output_dir": str((args.output_dir or (args.root / "paper/transfer_or_relearning_wip/derived_m2_exports")).resolve()), "input_manifest_sha256": manifest["input_manifest_sha256"], "outputs": len(manifest["outputs"])}, sort_keys=True))


if __name__ == "__main__":
    main()
