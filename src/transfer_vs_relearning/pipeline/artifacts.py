from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import pandas as pd

from transfer_vs_relearning.utils.io import write_csv, write_json


CHECKPOINT_FIELDS = (
    "eval_contract",
    "experiment_id",
    "state",
    "parent_state",
    "arm",
    "model_id",
    "model_revision",
    "tokenizer_id",
    "tokenizer_revision",
    "run_id",
    "seed",
    "checkpoint_id",
    "checkpoint_sha256",
    "update",
    "epoch",
    "normalized_progress",
    "cumulative_examples",
    "cumulative_fact_exposures",
    "cumulative_supervised_tokens",
    "cumulative_total_tokens",
    "learning_rate",
    "train_loss",
    "microbatch",
    "gradient_accumulation",
    "effective_row_batch",
    "max_sequence_length",
    "mean_nonpad_tokens",
    "p50_nonpad_tokens",
    "p95_nonpad_tokens",
    "padding_fraction",
    "truncation_count",
    "truncation_rate",
    "precision",
    "hardware_class",
    "record_status",
    "manifest_path",
    "manifest_sha256",
)

METRIC_FIELDS = (
    "eval_contract",
    "experiment_id",
    "state",
    "parent_state",
    "arm",
    "seed",
    "checkpoint_id",
    "lane",
    "family",
    "task_id",
    "task_version",
    "dataset_id",
    "dataset_revision",
    "split",
    "prompt_id",
    "fewshot",
    "metric",
    "filter",
    "role",
    "value",
    "unit",
    "higher_is_better",
    "denominator_name",
    "denominator_value",
    "sample_count",
    "stderr",
    "ci_low",
    "ci_high",
    "uncertainty_method",
    "comparison_reference",
    "absolute_delta",
    "ratio_to_reference",
    "result_status",
    "missing_reason",
    "raw_artifact_path",
    "raw_artifact_sha256",
)

FACTUAL_FIELDS = (
    "eval_contract",
    "experiment_id",
    "state",
    "parent_state",
    "arm",
    "seed",
    "checkpoint_id",
    "subject_id",
    "fact_id",
    "probe_id",
    "direction",
    "relation",
    "form",
    "scaffold",
    "correct_object_id",
    "predicted_object_id",
    "mean_answer_token_log_probability",
    "total_answer_token_log_probability",
    "rank",
    "margin",
    "answer_token_count",
    "probe_registry_sha256",
    "result_status",
)


def derive_retention_observation(
    *,
    checkpoint_bpb: float,
    parent_bpb: float,
    checkpoint_perplexity: float,
    parent_perplexity: float,
) -> dict[str, float | str | bool]:
    values = (checkpoint_bpb, parent_bpb, checkpoint_perplexity, parent_perplexity)
    if any(not math.isfinite(value) or value <= 0 for value in values):
        raise ValueError("Retention inputs must be finite and positive")
    perplexity_ratio = checkpoint_perplexity / parent_perplexity
    return {
        "primary_metric": "bits_per_byte",
        "checkpoint_bpb": checkpoint_bpb,
        "parent_bpb": parent_bpb,
        "bpb_absolute_delta": checkpoint_bpb - parent_bpb,
        "perplexity_ratio_to_parent": perplexity_ratio,
        "retention_score": 100.0 / perplexity_ratio,
        "retention_score_role": "visualization_only",
        "retention_score_scientific_gate": False,
    }


def _empty_parquet(path: Path, fields: tuple[str, ...]) -> None:
    pd.DataFrame(columns=list(fields)).to_parquet(path, index=False)


def initialize_artifact_scaffold(output_root: Path, pipeline_plan: dict[str, Any]) -> Path:
    """Create a fresh, explicitly not-run namespace without fabricating result rows."""
    if output_root.exists():
        raise FileExistsError(f"Artifact namespace already exists: {output_root}")
    output_root.mkdir(parents=True)
    _empty_parquet(output_root / "checkpoint_registry.parquet", CHECKPOINT_FIELDS)
    _empty_parquet(output_root / "metric_observations.parquet", METRIC_FIELDS)
    _empty_parquet(output_root / "factual_probe_results.parquet", FACTUAL_FIELDS)
    write_csv(output_root / "trajectory_wide.csv", [], fieldnames=["checkpoint_id"])
    write_csv(
        output_root / "hyperparameters.csv",
        [
            {"name": key, "value": value}
            for key, value in pipeline_plan["derived_training"].items()
        ],
        fieldnames=["name", "value"],
    )
    presentation = output_root / "presentation"
    (presentation / "plot_data").mkdir(parents=True)
    figures = [
        {
            "figure_id": "fact_access_vs_epoch",
            "status": "not_generated_no_complete_metrics",
            "required_metrics": ["factual_top1_accuracy", "robust_fact_intersection"],
        },
        {
            "figure_id": "retention_vs_epoch",
            "status": "not_generated_no_complete_metrics",
            "required_metrics": ["bits_per_byte", "bpb_absolute_delta"],
        },
        {
            "figure_id": "fact_retention_pareto",
            "status": "not_generated_no_complete_metrics",
            "required_metrics": ["factual_top1_accuracy", "bpb_absolute_delta"],
        },
        {
            "figure_id": "m2a_m2b_branch_comparison",
            "status": "not_generated_no_complete_metrics",
            "required_metrics": ["tr_to_en_top1_accuracy", "bits_per_byte"],
        },
    ]
    write_json(presentation / "figure_manifest.json", {"schema_version": 1, "figures": figures})
    write_json(
        presentation / "captions.json",
        {
            "schema_version": 1,
            "status": "not_generated_no_complete_metrics",
            "required_metadata": [
                "model_id",
                "model_revision",
                "dataset_revision",
                "seed",
                "microbatch",
                "gradient_accumulation",
                "effective_row_batch",
                "max_sequence_length",
                "precision",
            ],
        },
    )
    write_json(
        output_root / "evaluation_manifest.json",
        {
            "schema_version": 1,
            "status": "planned_not_run",
            "result_rows": 0,
            "pipeline_plan_id": pipeline_plan["plan_id"],
            "pipeline_config_sha256": pipeline_plan["config_sha256"],
            "missing_reason": "evaluation_not_authorized_or_executed",
            "artifacts": [
                "checkpoint_registry.parquet",
                "metric_observations.parquet",
                "factual_probe_results.parquet",
                "trajectory_wide.csv",
                "hyperparameters.csv",
                "presentation/figure_manifest.json",
                "presentation/captions.json",
            ],
        },
    )
    return output_root
