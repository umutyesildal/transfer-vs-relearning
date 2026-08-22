"""Deterministic presentation views from canonical pipeline tables.

This module never reads model weights and never runs evaluation. It only derives review-friendly
CSV/JSON views from already materialized canonical tables under one run root.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pandas as pd

from transfer_vs_relearning.utils.io import sha256_file, write_json


_FACTUAL_RE = re.compile(r"exact|top.?1|robust|relation|fact", re.IGNORECASE)
_RETENTION_RE = re.compile(
    r"bpb|bits.?per.?byte|perplexity|ppl|retention", re.IGNORECASE
)


def _read_table(root: Path, filename: str) -> pd.DataFrame:
    path = root / filename
    if not path.is_file():
        raise FileNotFoundError(f"Canonical table is missing: {path}")
    return pd.read_parquet(path)


def _sort_columns(frame: pd.DataFrame) -> pd.DataFrame:
    preferred = [
        "model_id",
        "state",
        "parent_state",
        "arm",
        "seed",
        "checkpoint_id",
        "epoch",
        "update",
        "metric",
        "task_id",
        "filter",
    ]
    present = [column for column in preferred if column in frame.columns]
    if present:
        frame = frame.sort_values(present, kind="mergesort")
    return frame.reset_index(drop=True)


def _metric_key(frame: pd.DataFrame) -> pd.Series:
    def key(row: pd.Series) -> str:
        pieces = [
            str(row.get("lane", "")),
            str(row.get("family", "")),
            str(row.get("task_id", "")),
            str(row.get("metric", "")),
            str(row.get("filter", "")),
        ]
        return "__".join(piece for piece in pieces if piece not in {"", "nan", "None"})

    return frame.apply(key, axis=1)


def _write_csv(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, lineterminator="\n")


def _source_manifest(root: Path) -> list[dict[str, Any]]:
    names = (
        "checkpoint_registry.parquet",
        "metric_observations.parquet",
        "factual_probe_results.parquet",
    )
    return [
        {
            "path": str(root / name),
            "bytes": (root / name).stat().st_size,
            "sha256": sha256_file(root / name),
        }
        for name in names
    ]


def build_presentation_bundle(output_root: Path) -> dict[str, Any]:
    """Build deterministic presentation views from canonical tables under ``output_root``.

    Only derived files below ``presentation/`` and ``trajectory_wide.csv`` are written. Raw
    namespaces and canonical parquet tables are never changed. Empty/planned tables produce a
    typed ``not_generated_no_complete_metrics`` manifest instead of fabricated figures.
    """

    output_root = output_root.resolve()
    checkpoint = _read_table(output_root, "checkpoint_registry.parquet")
    metrics = _read_table(output_root, "metric_observations.parquet")
    factual = _read_table(output_root, "factual_probe_results.parquet")
    presentation_root = output_root / "presentation"
    plot_root = presentation_root / "plot_data"
    plot_root.mkdir(parents=True, exist_ok=True)

    metrics = metrics.copy()
    if not metrics.empty:
        metrics["_metric_key"] = _metric_key(metrics)
        metrics = _sort_columns(metrics)
    factual = _sort_columns(factual) if not factual.empty else factual
    checkpoint = _sort_columns(checkpoint) if not checkpoint.empty else checkpoint

    # The trajectory review view is deliberately generated from the checkpoint table plus a
    # disambiguated metric key. Long-form parquet remains the source of truth.
    trajectory = checkpoint.copy()
    if not metrics.empty and "value" in metrics.columns:
        identity_columns = [
            column
            for column in ("state", "arm", "seed", "checkpoint_id")
            if column in metrics.columns
        ]
        metric_view = metrics.copy()
        metric_view["_observation_index"] = metric_view.groupby(
            identity_columns + ["_metric_key"], dropna=False
        ).cumcount()
        metric_view["_wide_key"] = metric_view["_metric_key"] + metric_view[
            "_observation_index"
        ].map(lambda value: "" if value == 0 else f"__{value}")
        pivot_index = [
            column
            for column in ("state", "arm", "seed", "checkpoint_id")
            if column in metric_view.columns
        ]
        pivot = metric_view.pivot_table(
            index=pivot_index,
            columns="_wide_key",
            values="value",
            aggfunc="first",
        ).reset_index()
        pivot.columns.name = None
        if pivot_index:
            trajectory = trajectory.merge(pivot, on=pivot_index, how="left", suffixes=("", "__metric"))
    _write_csv(output_root / "trajectory_wide.csv", _sort_columns(trajectory))

    figures = []
    metric_name = metrics["_metric_key"].astype(str) if not metrics.empty else pd.Series(dtype=str)
    for figure_id, pattern, filename, description in (
        (
            "fact_access_vs_epoch",
            _FACTUAL_RE,
            "fact_access_vs_epoch.csv",
            "Factual access metrics against epoch and cumulative fact exposure.",
        ),
        (
            "retention_vs_epoch",
            _RETENTION_RE,
            "retention_vs_epoch.csv",
            "Raw BPB/PPL/ratio retention metrics against epoch and cumulative exposure.",
        ),
    ):
        selected = (
            metrics[metric_name.str.contains(pattern, regex=True, na=False)].copy()
            if not metrics.empty
            else metrics
        )
        if "_metric_key" in selected.columns:
            selected = selected.drop(columns=["_metric_key"])
        selected = _sort_columns(selected)
        _write_csv(plot_root / filename, selected)
        figures.append(
            {
                "figure_id": figure_id,
                "status": "complete" if not selected.empty else "not_generated_no_complete_metrics",
                "data_path": f"presentation/plot_data/{filename}",
                "row_count": int(len(selected)),
                "description": description,
            }
        )

    pareto_columns = [
        column
        for column in (
            "state",
            "arm",
            "seed",
            "checkpoint_id",
            "epoch",
            "update",
            "cumulative_fact_exposures",
            "metric",
            "value",
            "role",
            "result_status",
        )
        if column in metrics.columns
    ]
    pareto = metrics[pareto_columns].copy() if not metrics.empty else pd.DataFrame()
    if not pareto.empty:
        pareto = pareto[
            pareto["metric"].astype(str).str.contains("fact|bpb|perplexity|ppl|retention", case=False, regex=True)
        ]
    _write_csv(plot_root / "fact_retention_pareto.csv", _sort_columns(pareto))
    figures.append(
        {
            "figure_id": "fact_retention_pareto",
            "status": "complete" if not pareto.empty else "not_generated_no_complete_metrics",
            "data_path": "presentation/plot_data/fact_retention_pareto.csv",
            "row_count": int(len(pareto)),
            "description": "Factual access versus raw retention evidence; no derived score replaces raw values.",
        }
    )

    branch = metrics[metrics["state"].isin(["M2-A", "M2-B"])] if not metrics.empty and "state" in metrics.columns else pd.DataFrame()
    branch = _sort_columns(branch.drop(columns=["_metric_key"], errors="ignore"))
    _write_csv(plot_root / "m2a_m2b_branch_comparison.csv", branch)
    figures.append(
        {
            "figure_id": "m2a_m2b_branch_comparison",
            "status": "complete" if not branch.empty else "not_generated_no_complete_metrics",
            "data_path": "presentation/plot_data/m2a_m2b_branch_comparison.csv",
            "row_count": int(len(branch)),
            "description": "Matched-budget M2-A/M2-B comparison using canonical long-form metrics.",
        }
    )

    complete = any(item["status"] == "complete" for item in figures)
    manifest = {
        "schema_version": 1,
        "status": "complete" if complete else "not_generated_no_complete_metrics",
        "source_tables": _source_manifest(output_root),
        "canonical_source_of_truth": [
            "checkpoint_registry.parquet",
            "metric_observations.parquet",
            "factual_probe_results.parquet",
        ],
        "figures": figures,
        "missing_reason": None if complete else "no_complete_metric_rows",
    }
    write_json(presentation_root / "figure_manifest.json", manifest)
    write_json(
        presentation_root / "captions.json",
        {
            "schema_version": 1,
            "status": manifest["status"],
            "captions": {item["figure_id"]: item["description"] for item in figures},
            "scientific_note": "Raw BPB/PPL and factual metrics remain primary; retention_score is visualization-only.",
        },
    )
    return manifest
