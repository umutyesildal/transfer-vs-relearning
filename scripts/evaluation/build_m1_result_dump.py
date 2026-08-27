#!/usr/bin/env python3
"""Build compact M1 result tables and a human-readable M0/M1 ledger.

The input is the NDJSON emitted by ``emit_m1_compact_remote.py``.  Only manifests and metric
summaries are copied into the generated JSON; raw samples, CSV/parquet payloads, checkpoints and
model weights remain on HU scratch storage.
"""

import argparse
import csv
import hashlib
import json
import os
from collections import defaultdict


M0_EXACT_PREFIX_TOP1 = {
    "olmo": 0.022,
    "qwen": 0.030,
    "smollm": 0.032,
}

M0_EXACT_PREFIX_SOURCE = "documentation/records/evaluation/M0_SMOLLM_EXACT_PREFIX_RECOVERY_RESULT_2026-08-21.md"


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def local_artifact(path):
    return {
        "path": path,
        "bytes": os.path.getsize(path),
        "sha256": sha256_file(path),
    }


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_ndjson(path):
    with open(path, "r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def compact_artifact_ref(artifact):
    if artifact is None:
        return None
    return {
        "path": artifact["path"],
        "bytes": artifact["bytes"],
        "sha256": artifact["sha256"],
    }


def source_ref(artifact, kind):
    if artifact is None:
        return None
    return {
        "kind": kind,
        "path": artifact["path"],
        "bytes": artifact["bytes"],
        "sha256": artifact["sha256"],
    }


def number(value):
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def sample_count_from_metric(metric, default=None):
    sample_count = metric.get("sample_count")
    if isinstance(sample_count, dict):
        for value in sample_count.values():
            if isinstance(value, int):
                return value
    if isinstance(metric.get("sample_len"), int):
        return metric["sample_len"]
    return default


def source_record_for_m0(m0_sources, model, metric):
    aliases = {
        "wikitext_bpb": "english_retention_wikitext",
        "wikitext_word_ppl": "english_retention_wikitext",
        "wikitext_byte_ppl": "english_retention_wikitext",
        "blimp_accuracy": "english_grammar_blimp",
        "hellaswag_accuracy": "english_capability",
        "hellaswag_acc_norm": "english_capability",
        "winogender_female": "english_capability",
        "winogender_male": "english_capability",
        "winogender_neutral": "english_capability",
        "turblimp_acc_norm": "turkish_capability",
        "turkish_bpb": "turkish_perplexity",
        "turkish_ppl": "turkish_perplexity",
        "turkish_byte_ppl": "turkish_perplexity",
        "factual_top1_count": "factual_access",
        "factual_top1_rate": "factual_access",
        "factual_forced_choice_rate": "factual_access",
        "factual_prompt_form_failures": "factual_access",
        "generation_top1_accuracy": "generation_integrity",
        "generation_empty_or_near_empty": "generation_integrity",
        "generation_distinct_2": "generation_integrity",
        "generation_repeated_3gram": "generation_integrity",
        "generation_ppl": "generation_integrity",
    }
    lane = aliases.get(metric)
    if lane is None:
        return None
    prefix = model + "_"
    candidates = [
        item
        for item in m0_sources
        if item.get("model") == model and item.get("lane") == lane
    ]
    if candidates:
        item = candidates[0]
        return {
            "kind": "m0_source_record",
            "path": item["path"],
            "bytes": item.get("bytes"),
            "sha256": item["sha256"],
            "source_ref": item.get("source_ref"),
        }
    return None


def baseline_rows(m0):
    rows = {}
    source_by_ref = {item["source_ref"]: item for item in m0.get("source_records", [])}
    for row in m0.get("metric_rows", []):
        metric = row["metric"]
        if metric.startswith("pile_"):
            continue
        model = row["model"]
        ref = source_by_ref.get(row.get("source_ref"))
        rows[(model, metric)] = {
            "value": row.get("value"),
            "unit": row.get("unit"),
            "direction": row.get("direction"),
            "denominator": row.get("sample_count"),
            "source": (
                {
                    "kind": "m0_source_record",
                    "path": ref["path"],
                    "bytes": ref.get("bytes"),
                    "sha256": ref["sha256"],
                    "source_ref": row.get("source_ref"),
                }
                if ref
                else None
            ),
        }
    for model, value in M0_EXACT_PREFIX_TOP1.items():
        rows[(model, "exact_prefix_top1_accuracy")] = {
            "value": value,
            "unit": "fraction",
            "direction": "higher",
            "denominator": 500,
            "source": None,
        }
    return rows


def comparison_for(value, denominator, model, metric, panel, baseline):
    base = baseline.get((model, metric))
    if base is None:
        return {
            "m0_value": None,
            "m0_denominator": None,
            "delta_from_m0": None,
            "relative_delta_pct": None,
            "comparison_status": "no_m0_reference",
        }
    base_value = base.get("value")
    base_denominator = base.get("denominator")
    if panel == "factual_cheap" or metric.startswith("factual_cheap_"):
        status = "panel_or_denominator_mismatch"
        direct = False
    elif base_denominator is None or denominator is None:
        status = "m0_reference_denominator_unbound"
        direct = False
    elif base_denominator != denominator:
        status = "denominator_mismatch"
        direct = False
    else:
        status = "direct_same_metric_and_denominator"
        direct = True
    delta = value - base_value if direct and number(value) is not None and number(base_value) is not None else None
    relative = (100.0 * delta / base_value) if delta is not None and base_value != 0 else None
    return {
        "m0_value": base_value,
        "m0_denominator": base_denominator,
        "delta_from_m0": delta,
        "relative_delta_pct": relative,
        "comparison_status": status,
    }


def override_from_canonical_parent_projections(records, baseline):
    """Use the M1 family's hash-bound M0 projection for metrics it explicitly carries."""
    mapping = {
        ("english_retention_wikitext", "bits_per_byte"): "wikitext_bpb",
        ("english_retention_wikitext", "word_perplexity"): "wikitext_word_ppl",
        ("english_retention_wikitext", "byte_perplexity"): "wikitext_byte_ppl",
        ("english_grammar_blimp", "accuracy"): "blimp_accuracy",
        ("english_capability", "hellaswag_acc_norm"): "hellaswag_acc_norm",
        ("turkish_capability", "accuracy"): "turblimp_acc_norm",
        ("turkish_perplexity", "bits_per_byte"): "turkish_bpb",
        ("turkish_perplexity", "word_perplexity"): "turkish_ppl",
        ("turkish_perplexity", "byte_perplexity"): "turkish_byte_ppl",
        ("factual_access", "top1_accuracy"): "factual_top1_rate",
        ("generation_integrity", "repeated_3gram_fraction"): "generation_repeated_3gram",
        ("exact_prefix", "exact_prefix_accuracy"): "exact_prefix_top1_accuracy",
    }
    for record in records:
        if record["checkpoint"] != "parent":
            continue
        projection = record["task_result"]["data"].get("projection", {})
        for item in projection.get("rows", []):
            metric = mapping.get((item.get("lane_id"), item.get("metric")))
            if metric is None:
                continue
            key = (record["model"], metric)
            if key not in baseline:
                continue
            prior = baseline[key]
            baseline[key] = {
                "value": item.get("value"),
                "unit": prior.get("unit"),
                "direction": prior.get("direction"),
                "denominator": prior.get("denominator"),
                "source": {
                    "kind": "m0_canonical_projection_source",
                    "path": item.get("raw_artifact_path"),
                    "bytes": None,
                    "sha256": item.get("raw_artifact_sha256"),
                },
            }


def add_metric(rows, state, metric, value, unit, direction, denominator, panel, artifact, status="measured"):
    if value is None:
        return
    rows.append(
        {
            "model": state["model"],
            "state": state["state"],
            "checkpoint": state["checkpoint"],
            "epoch": state["epoch"],
            "update": state["update"],
            "full_state": state["full_state"],
            "metric": metric,
            "panel": panel,
            "value": value,
            "unit": unit,
            "direction": direction,
            "denominator": denominator,
            "measurement_status": status,
            "source_artifact_path": artifact["path"] if artifact else None,
            "source_artifact_sha256": artifact["sha256"] if artifact else None,
            "source_artifact_bytes": artifact["bytes"] if artifact else None,
        }
    )


def state_header(record):
    task = record["task_result"]["data"]
    return {
        "model": record["model"],
        "state": record["state"],
        "checkpoint": record["checkpoint"],
        "epoch": task.get("epoch", 0),
        "update": task.get("update", 0),
        "full_state": bool(task.get("full", False)),
        "task_status": task.get("status"),
        "task_result_path": record["task_result"]["path"],
        "task_result_sha256": record["task_result"]["sha256"],
        "task_result_bytes": record["task_result"]["bytes"],
        "archived_failed_attempts": task.get("archived_failed_attempts", []),
        "memory_gate": task.get("memory_gate"),
        "validations": task.get("validations"),
    }


def extract_metric_rows(records, m0, baseline):
    rows = []
    headers = []
    for record in records:
        state = state_header(record)
        headers.append(state)
        model = state["model"]
        if state["checkpoint"] == "parent":
            for (row_model, metric), base in sorted(baseline.items()):
                if row_model != model:
                    continue
                source = base.get("source")
                add_metric(
                    rows,
                    state,
                    metric,
                    base.get("value"),
                    base.get("unit") or "fraction",
                    base.get("direction") or "higher",
                    base.get("denominator"),
                    "m0_parent_projection",
                    source,
                    status="projected_from_canonical_m0_evidence_without_rescoring",
                )
            continue

        harness = record.get("harness")
        if harness:
            h = harness["data"]
            results = h.get("results", {})
            groups = h.get("groups", {})
            wiki = results.get("wikitext", {})
            add_metric(rows, state, "wikitext_bpb", number(wiki.get("bits_per_byte,none")), "bits/byte", "lower", sample_count_from_metric(wiki, 62), "wikitext", harness)
            add_metric(rows, state, "wikitext_word_ppl", number(wiki.get("word_perplexity,none")), "PPL", "lower", sample_count_from_metric(wiki, 62), "wikitext", harness)
            add_metric(rows, state, "wikitext_byte_ppl", number(wiki.get("byte_perplexity,none")), "PPL", "lower", sample_count_from_metric(wiki, 62), "wikitext", harness)
            blimp = groups.get("blimp", {})
            add_metric(rows, state, "blimp_accuracy", number(blimp.get("acc,none")), "fraction", "higher", sample_count_from_metric(blimp, 67000), "blimp", harness)
            hellaswag = results.get("hellaswag", {})
            add_metric(rows, state, "hellaswag_accuracy", number(hellaswag.get("acc,none")), "fraction", "higher", sample_count_from_metric(hellaswag, 10042), "hellaswag", harness)
            add_metric(rows, state, "hellaswag_acc_norm", number(hellaswag.get("acc_norm,none")), "fraction", "higher", sample_count_from_metric(hellaswag, 10042), "hellaswag", harness)
            for name in ("female", "male", "neutral"):
                wino = results.get("winogender_" + name, {})
                add_metric(rows, state, "winogender_" + name, number(wino.get("acc,none")), "fraction", "higher", sample_count_from_metric(wino, 240), "winogender", harness)
            turblimp = groups.get("turblimp_core", {})
            add_metric(rows, state, "turblimp_acc_norm", number(turblimp.get("acc_norm,none")), "fraction", "higher", sample_count_from_metric(turblimp, 16000), "turblimp", harness)

        exact = record.get("exact_prefix")
        if exact:
            p = exact["data"].get("primary_mean_logprob", {})
            for key, metric, unit, direction in (
                ("top1_accuracy", "exact_prefix_top1_accuracy", "fraction", "higher"),
                ("top5_accuracy", "exact_prefix_top5_accuracy", "fraction", "higher"),
                ("mrr", "exact_prefix_mrr", "fraction", "higher"),
                ("mean_rank", "exact_prefix_mean_rank", "rank", "lower"),
                ("mean_score_margin", "exact_prefix_mean_score_margin", "logprob", "higher"),
            ):
                add_metric(rows, state, metric, number(p.get(key)), unit, direction, p.get("n", 500), "exact_prefix", exact)

        cheap = record.get("factual_cheap")
        if cheap:
            d = cheap["data"]
            add_metric(rows, state, "factual_cheap_top1_count", number(d.get("top1")), "count", "higher", d.get("probes", 1500), "factual_cheap", cheap, d.get("status", "measured"))
            add_metric(rows, state, "factual_cheap_top1_rate", number(d.get("top1_accuracy")), "fraction", "higher", d.get("probes", 1500), "factual_cheap", cheap, d.get("status", "measured"))

        full = record.get("factual_full")
        if full:
            d = full["data"]
            n = d.get("probes", 12000)
            add_metric(rows, state, "factual_top1_count", number(d.get("top1")), "count", "higher", n, "factual_full", full)
            add_metric(rows, state, "factual_top1_rate", (d.get("top1") / float(n)) if isinstance(d.get("top1"), int) and n else None, "fraction", "higher", n, "factual_full", full)
            forced = d.get("relation_swapped_forced_choice", {})
            forced_n = forced.get("n", 4800)
            add_metric(rows, state, "factual_forced_choice_rate", (forced.get("correct") / float(forced_n)) if isinstance(forced.get("correct"), int) and forced_n else None, "fraction", "higher", forced_n, "factual_full", full)
            taxonomy = d.get("failure_taxonomy", {})
            for key, metric in (
                ("early_eos_preference", "factual_failure_early_eos"),
                ("none", "factual_failure_none"),
                ("prompt_form_failure", "factual_prompt_form_failures"),
                ("same_subject_relation_swap", "factual_failure_relation_swap"),
            ):
                add_metric(rows, state, metric, number(taxonomy.get(key)), "count", "lower", n, "factual_full", full)

        turkish = record.get("turkish_cross_domain") or record.get("turkish")
        if turkish:
            d = turkish["data"]
            if "corpora" in d:
                d = d["corpora"].get("trwiki_cross_domain", {})
            add_metric(rows, state, "turkish_bpb", number(d.get("bits_per_byte")), "bits/byte", "lower", d.get("scored_token_count"), "turkish_cross_domain", turkish)
            add_metric(rows, state, "turkish_ppl", number(d.get("perplexity")), "PPL", "lower", d.get("scored_token_count"), "turkish_cross_domain", turkish)
            add_metric(rows, state, "turkish_byte_ppl", number(d.get("byte_perplexity")), "PPL", "lower", d.get("scored_token_count"), "turkish_cross_domain", turkish)

        generation = record.get("generation")
        if generation:
            d = generation["data"]
            g = d.get("generation", {})
            c = d.get("generic_completions", {})
            loss = d.get("generic_loss", {})
            n = g.get("prompt_count", c.get("item_count", 30))
            add_metric(rows, state, "generation_top1_accuracy", number(c.get("top1_accuracy")), "fraction", "higher", n, "generation", generation)
            add_metric(rows, state, "generation_empty_or_near_empty", number(g.get("empty_or_near_empty_count", g.get("empty_generation_count"))), "count", "lower", n, "generation", generation)
            add_metric(rows, state, "generation_distinct_2", number(g.get("mean_distinct_2")), "fraction", "higher", n, "generation", generation)
            add_metric(rows, state, "generation_repeated_3gram", number(g.get("mean_repeated_3gram_fraction")), "fraction", "lower", n, "generation", generation)
            add_metric(rows, state, "generation_repeated_4gram", number(g.get("mean_repeated_4gram_fraction")), "fraction", "lower", n, "generation", generation)
            add_metric(rows, state, "generation_ppl", number(loss.get("perplexity")), "PPL", "lower", loss.get("scored_token_count"), "generation", generation)

    by_state_metric = {}
    for row in rows:
        by_state_metric[(row["state"], row["metric"])] = row
    for row in rows:
        if row["panel"] == "m0_parent_projection":
            row.update({
                "m0_value": row["value"],
                "m0_denominator": row["denominator"],
                "delta_from_m0": 0,
                "relative_delta_pct": 0,
                "comparison_status": "m0_parent_projection",
            })
        else:
            row.update(comparison_for(row["value"], row["denominator"], row["model"], row["metric"], row["panel"], baseline))
    return headers, rows


def sort_states(records):
    return sorted(records, key=lambda record: (record["model"], 0 if record["checkpoint"] == "parent" else int(record["checkpoint"].split("-")[-1])))


def value_map(metric_rows):
    values = {}
    for row in metric_rows:
        values[(row["state"], row["metric"])] = row
    return values


TRAJECTORY_METRICS = [
    "wikitext_bpb",
    "exact_prefix_top1_accuracy",
    "factual_cheap_top1_rate",
    "factual_top1_rate",
    "factual_forced_choice_rate",
    "turkish_bpb",
    "generation_top1_accuracy",
    "generation_distinct_2",
    "generation_repeated_3gram",
    "generation_ppl",
    "blimp_accuracy",
    "hellaswag_acc_norm",
    "turblimp_acc_norm",
]


def trajectory_rows(records, metric_rows, baseline):
    values = value_map(metric_rows)
    out = []
    for record in sort_states(records):
        state = state_header(record)
        row = dict(state)
        row["state_kind"] = "m0_parent_projection" if state["checkpoint"] == "parent" else "m1_gpu_snapshot"
        for metric in TRAJECTORY_METRICS:
            value = values.get((state["state"], metric))
            row[metric] = value["value"] if value else None
            row[metric + "_m0"] = value["m0_value"] if value else baseline.get((state["model"], metric), {}).get("value")
            row[metric + "_delta"] = value["delta_from_m0"] if value else None
        out.append(row)
    return out


def csv_write(path, rows):
    if not rows:
        return
    fields = []
    for row in rows:
        for field in row:
            if field not in fields:
                fields.append(field)
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def fmt(value):
    if value is None:
        return "—"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float):
        return "%.6f" % value
    return str(value)


def md_table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(fmt(row.get(key)) for key in headers) + " |")
    return "\n".join(lines)


def report_markdown(path, payload, trajectory, metric_rows, control_refs):
    family = payload["control_artifact_data"]["evaluation_family_result"]
    counts = payload["counts"]
    lines = [
        "# M1 eval-v2 matched three-model wave — terminal result ledger (2026-08-27)",
        "",
        "## Terminal status",
        "",
        "The HU evaluation family is operationally complete: **111/111 scientific states**, including",
        "108 GPU checkpoint snapshots and 3 explicit M0 parent projections. This document records",
        "execution evidence and arithmetic M0→M1 comparisons; it is not a primary-model selection",
        "or a causal interpretation of the training effect.",
        "",
        "| Item | Result |",
        "|---|---:|",
        "| Family status | `%s` |" % family.get("status"),
        "| Complete scientific states | %s / %s |" % (family.get("complete_count"), family.get("task_count")),
        "| GPU snapshots | %s / %s |" % (family.get("gpu_complete_count"), family.get("gpu_task_count")),
        "| M0 parent projections | %s / %s |" % (family.get("parent_complete_count"), family.get("parent_projection_count")),
        "| Models | 3 (OLMo, Qwen, SmolLM) |",
        "| Checkpoints per model | parent + epoch-001…epoch-036 |",
        "",
        "## Control and immutable identity",
        "",
        md_table(["Artifact", "Remote path", "SHA-256", "Bytes"], [
            {"Artifact": key, "Remote path": value["path"], "SHA-256": value["sha256"], "Bytes": value["bytes"]}
            for key, value in control_refs.items()
        ]),
        "",
        "| Execution identity | Value |",
        "|---|---|",
        "| Matrix ID | `%s` |" % payload["identity"]["matrix_id"],
        "| M1 contract SHA-256 | `%s` |" % payload["identity"]["contract_sha256"],
        "| M1 execution config SHA-256 | `%s` |" % payload["identity"]["execution_config_sha256"],
        "| Adapter module SHA-256 | `%s` |" % payload["identity"]["adapter_module_sha256"],
        "| Entrypoint SHA-256 | `%s` |" % payload["identity"]["entrypoint_sha256"],
        "| Output root | `%s` |" % payload["identity"]["output_root"],
        "| Harness | `lm-eval 0.4.12` |",
        "| Turkish corpus | 10,034 validation documents; corpus SHA bound in summaries |",
        "",
        "## Job chain",
        "",
        "| Role | Job | Terminal evidence |",
        "|---|---:|---|",
        "| Read-only preflight | 479444 | `ready`; 111 total scientific states |",
        "| GPU array | 479445 | no longer in queue; 108 canonical result paths complete |",
        "| Family finalizer | 479446 | `complete_count: 111`; stderr 0 bytes |",
        "",
        "## State coverage",
        "",
        "Every model has 37 canonical rows: one `parent` projection plus 36 measured snapshots.",
        "Dense checkpoints have the recurring retention/integrity panels; epoch-18 and epoch-36",
        "also have the 12,000-probe factual panel and full Harness capability panel. The JSON dump",
        "retains the complete compact summary bundle and SHA-256 for each summary artifact.",
        "",
        md_table(["Model", "Parent", "Epoch 1–17", "Epoch 18", "Epoch 19–35", "Epoch 36", "Total"], [
            {"Model": model, "Parent": 1, "Epoch 1–17": 17, "Epoch 18": 1, "Epoch 19–35": 17, "Epoch 36": 1, "Total": 37}
            for model in ("olmo", "qwen", "smollm")
        ]),
        "",
        "## M0 ↔ M1 endpoint comparison",
        "",
        "Values are shown as recorded; `Δ` is the arithmetic difference `M1 − M0`. A delta is not",
        "by itself a causal estimate. Lower is better for BPB/PPL/repetition; higher is better for",
        "accuracy, top-1, MRR, distinct-2 and forced-choice rate.",
        "",
    ]
    endpoint_metrics = [
        "wikitext_bpb", "wikitext_word_ppl", "blimp_accuracy", "hellaswag_acc_norm",
        "turblimp_acc_norm", "turkish_bpb", "factual_top1_rate", "factual_forced_choice_rate",
        "exact_prefix_top1_accuracy", "generation_top1_accuracy", "generation_distinct_2",
        "generation_repeated_3gram", "generation_ppl",
    ]
    values = value_map(metric_rows)
    endpoint = []
    for model in ("olmo", "qwen", "smollm"):
        for metric in endpoint_metrics:
            base = baseline_value(payload, model, metric)
            e18 = values.get((model + "/epoch-018", metric))
            e36 = values.get((model + "/epoch-036", metric))
            endpoint.append({
                "Model": model,
                "Metric": metric,
                "M0": base,
                "M1 e18": e18["value"] if e18 else None,
                "Δ e18": e18["delta_from_m0"] if e18 else None,
                "M1 e36": e36["value"] if e36 else None,
                "Δ e36": e36["delta_from_m0"] if e36 else None,
                "Comparison": (e18 or e36 or {}).get("comparison_status", "—"),
            })
    lines.append(md_table(["Model", "Metric", "M0", "M1 e18", "Δ e18", "M1 e36", "Δ e36", "Comparison"], endpoint))
    lines.extend([
        "",
        "Factual endpoint rows are the directly comparable 12,000-probe full panel. The 1,500-probe",
        "cheap panel is kept separately in the trajectory and JSON dump; it is never substituted for",
        "the 12,000-probe M0 denominator.",
        "",
        "## Full-state detailed comparison",
        "",
        md_table(["State", "Metric", "Value", "M0", "Δ", "Denominator", "Status"], [
            {
                "State": row["state"], "Metric": row["metric"], "Value": row["value"],
                "M0": row["m0_value"], "Δ": row["delta_from_m0"],
                "Denominator": row["denominator"], "Status": row["comparison_status"],
            }
            for row in metric_rows
            if row["checkpoint"] in ("epoch-018", "epoch-036")
            and row["metric"] in endpoint_metrics + [
                "factual_top1_count", "factual_prompt_form_failures", "factual_failure_early_eos",
                "factual_failure_none", "factual_failure_relation_swap", "generation_empty_or_near_empty",
                "generation_repeated_4gram", "exact_prefix_top5_accuracy", "exact_prefix_mrr",
            ]
        ]),
        "",
        "## All-checkpoint trajectory list",
        "",
        "The following is the compact review list requested for M0-style comparison. `parent` is",
        "the M0 evidence projection; all epoch rows are measured M1 GPU snapshots. Missing cells are",
        "not zero and mean that the panel was not scheduled at that cadence.",
        "",
    ])
    trajectory_headers = [
        "model", "checkpoint", "epoch", "update", "state_kind", "wikitext_bpb", "wikitext_bpb_m0", "wikitext_bpb_delta",
        "exact_prefix_top1_accuracy", "factual_cheap_top1_rate", "factual_top1_rate", "factual_forced_choice_rate",
        "turkish_bpb", "generation_top1_accuracy", "generation_distinct_2", "generation_repeated_3gram", "generation_ppl",
        "blimp_accuracy", "hellaswag_acc_norm", "turblimp_acc_norm",
    ]
    lines.append(md_table(trajectory_headers, trajectory))
    lines.extend([
        "",
        "## Missingness, retry and evidence notes",
        "",
        "- The final canonical family is complete. Historical failed attempts remain on HU scratch and",
        "  are represented through each task's `archived_failed_attempts` field; they are not counted as",
        "  additional scientific states.",
        "- Qwen epoch-018 records `epoch-018__killed_0` as an archived hard-killed attempt. The final",
        "  canonical result is complete and is counted once.",
        "- `sacct` accounting metadata was unavailable during live inspection because of the cluster's",
        "  Munge/SlurmDBD authentication failure. This does not invalidate the independently written",
        "  finalizer family result, task results, or metric-summary hashes.",
        "- Raw sample JSONL, CSV/parquet evidence, checkpoints and weights remain on HU scratch. The",
        "  compact Git layer stores summary values, provenance paths and hashes only.",
        "- Token PPL is a within-tokenizer companion. BPB is the primary retention metric for cross-model",
        "  comparison. Exact-prefix is candidate ranking, not free-generation exact-match accuracy.",
        "",
        "## Reproducible local views",
        "",
        "- `artifacts/evaluations/m1_three_model_v1/dump/m1_metrics.json` — compact canonical result layer",
        "  for this snapshot, including state bundles, normalized metric rows and provenance.",
        "- `artifacts/evaluations/m1_three_model_v1/dump/m0_m1_comparison.csv` — long-form M0/M1 comparison",
        "  with denominators, deltas and comparison status for every normalized row.",
        "- `artifacts/evaluations/m1_three_model_v1/dump/m1_trajectory.csv` — one row per model × parent/epoch",
        "  with the recurring trajectory metrics.",
        "",
    ])
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


def baseline_value(payload, model, metric):
    for row in payload["m0_baseline_rows"]:
        if row["model"] == model and row["metric"] == metric:
            return row["value"]
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-ndjson", required=True)
    parser.add_argument("--m0", required=True)
    parser.add_argument("--family-result", required=True)
    parser.add_argument("--preflight", required=True)
    parser.add_argument("--submission", required=True)
    parser.add_argument("--task-matrix", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--exact-prefix-record", required=True)
    parser.add_argument("--finalizer-out-path", required=True)
    parser.add_argument("--finalizer-out-sha256", required=True)
    parser.add_argument("--finalizer-out-bytes", required=True, type=int)
    parser.add_argument("--adapter-module-sha256", required=True)
    parser.add_argument("--entrypoint-sha256", required=True)
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    records = load_ndjson(args.source_ndjson)
    m0 = load_json(args.m0)
    family = load_json(args.family_result)
    preflight = load_json(args.preflight)
    submission = load_json(args.submission)
    task_matrix = load_json(args.task_matrix)
    baseline = baseline_rows(m0)
    exact_source = local_artifact(args.exact_prefix_record)
    exact_source["kind"] = "m0_exact_prefix_result_record"
    for model in M0_EXACT_PREFIX_TOP1:
        baseline[(model, "exact_prefix_top1_accuracy")]["source"] = exact_source
    override_from_canonical_parent_projections(records, baseline)
    headers, metric_rows = extract_metric_rows(records, m0, baseline)
    trajectory = trajectory_rows(records, metric_rows, baseline)

    m0_baseline_rows = []
    for (model, metric), row in sorted(baseline.items()):
        source = row.get("source")
        m0_baseline_rows.append({
            "model": model,
            "metric": metric,
            "value": row.get("value"),
            "unit": row.get("unit"),
            "direction": row.get("direction"),
            "denominator": row.get("denominator"),
            "source": source,
        })

    control = {
        "evaluation_family_result": local_artifact(args.family_result),
        "preflight": local_artifact(args.preflight),
        "submission_manifest": local_artifact(args.submission),
        "task_matrix": local_artifact(args.task_matrix),
        "finalizer_log": {
            "path": args.finalizer_out_path,
            "sha256": args.finalizer_out_sha256,
            "bytes": args.finalizer_out_bytes,
        },
    }
    output_root = task_matrix.get("output_root")
    control_names = {
        "evaluation_family_result": "evaluation_family_result.json",
        "preflight": "preflight.json",
        "submission_manifest": "submission_manifest.json",
        "task_matrix": "task_matrix.json",
    }
    for name, filename in control_names.items():
        control[name]["path"] = os.path.join(output_root, "control", filename)
    control_data = {
        "evaluation_family_result": family,
        "preflight": preflight,
        "submission_manifest": submission,
        "task_matrix": task_matrix,
    }
    identity = {
        "matrix_id": task_matrix.get("matrix_id"),
        "contract_sha256": task_matrix.get("authorization", {}).get("contract_sha256"),
        "execution_config_sha256": task_matrix.get("authorization", {}).get("execution_config_sha256"),
        "adapter_module_sha256": args.adapter_module_sha256,
        "entrypoint_sha256": args.entrypoint_sha256,
        "output_root": output_root,
    }
    payload = {
        "schema_version": "m1-eval-v2-compact-result-v1",
        "generated_at": "2026-08-27",
        "state": "M1",
        "status": family.get("status"),
        "identity": identity,
        "counts": {
            "scientific_states": family.get("task_count"),
            "complete_states": family.get("complete_count"),
            "gpu_states": family.get("gpu_task_count"),
            "gpu_complete_states": family.get("gpu_complete_count"),
            "parent_projections": family.get("parent_projection_count"),
            "parent_complete_states": family.get("parent_complete_count"),
            "models": len(sorted(set(record["model"] for record in records))),
            "states_per_model": {model: sum(record["model"] == model for record in records) for model in sorted(set(record["model"] for record in records))},
            "metric_rows": len(metric_rows),
        },
        "control_artifacts": control,
        "control_artifact_data": control_data,
        "m0_source": {
            "dump": local_artifact(args.m0),
            "exact_prefix_record": local_artifact(args.exact_prefix_record),
            "pile_lanes_excluded": True,
        },
        "m0_baseline_rows": m0_baseline_rows,
        "states": records,
        "state_headers": headers,
        "metric_rows": metric_rows,
        "trajectory": trajectory,
        "quality_checks": {
            "family_complete_count_matches_task_count": family.get("complete_count") == family.get("task_count") == len(records),
            "three_models_each_37_states": sorted({record["model"] for record in records}) == ["olmo", "qwen", "smollm"] and all(sum(record["model"] == model for record in records) == 37 for model in ("olmo", "qwen", "smollm")),
            "no_noncomplete_canonical_task_results": all(record["task_result"]["data"].get("status") in ("complete", "completed") for record in records),
            "full_states_are_epoch_18_or_36": all((not record["task_result"]["data"].get("full")) or record["checkpoint"] in ("epoch-018", "epoch-036") for record in records),
        },
    }
    json_path = os.path.join(args.out_dir, "m1_metrics.json")
    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=True, indent=2, sort_keys=True)
        handle.write("\n")
    csv_write(os.path.join(args.out_dir, "m0_m1_comparison.csv"), metric_rows)
    csv_write(os.path.join(args.out_dir, "m1_trajectory.csv"), trajectory)
    report_markdown(os.path.join(args.out_dir, "M1_RESULT_LEDGER_2026-08-27.md"), payload, trajectory, metric_rows, control)
    generated_paths = [
        json_path,
        os.path.join(args.out_dir, "m0_m1_comparison.csv"),
        os.path.join(args.out_dir, "m1_trajectory.csv"),
        os.path.join(args.out_dir, "M1_RESULT_LEDGER_2026-08-27.md"),
    ]
    manifest = {
        "schema_version": "m1-eval-v2-compact-dump-manifest-v1",
        "generated_at": "2026-08-27",
        "state": "M1",
        "source_family_result_sha256": sha256_file(args.family_result),
        "artifacts": [local_artifact(path) for path in generated_paths],
    }
    manifest_path = os.path.join(args.out_dir, "dump_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, ensure_ascii=True, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps({
        "json": json_path,
        "manifest": manifest_path,
        "metric_rows": len(metric_rows),
        "states": len(records),
        "trajectory_rows": len(trajectory),
        "quality_checks": payload["quality_checks"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
