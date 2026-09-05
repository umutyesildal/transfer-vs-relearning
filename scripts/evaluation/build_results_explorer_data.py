#!/usr/bin/env python3
"""Build the validated, static data contract for the M2 results explorer.

The builder intentionally consumes only the compact Git-retained evaluation dumps named in
``M2_RESULTS_WEBSITE_AND_THESIS_REPORTING_PLAN_2026-09-05.md``.  It fails closed when a source
hash, row count, vocabulary, uniqueness constraint, or scientific invariant changes.  No browser
code performs joins or derives scientific estimates from the resulting manifest.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


EXPECTED_SOURCE_SHA256 = {
    "m0_metrics": "859b598fdd3509d6e11e5cbf3f9662bc66accd58291bc635aad028185e1bdbbd",
    "m1_metrics": "41c2f2c6b722fc25ac48af278f1b318acc5e743b3c48d649fe26259848080462",
    "m1_trajectory": "0cf33dca248d35c8c6f49bd8856d2ef801d3cfef522f59bde099a9aef72e269b",
    "m0_m1_comparison": "ee0a9f0bc21e8c360c8fc0b9971cd3be3ff76120bc89c55dee60c356a670e68a",
    "m2_evaluation_family": "c04eff5ba1301f5fcd4a318cc3a88d281e389cd05f542e6f6d569826809bcebf",
    "m2_scientific_analysis": "732c9c23ab795bf3212196d582f8300ca6c02dbf6902c489a1d4ecd6eae6e0ca",
    "m2_checkpoint_trajectory": "2e687bb24befc947ec21fa1e0c9040b27e6be2a3dff6da8ea6ab3e30b9e9a18a",
    "m2_endpoint_breakdown": "4502af97b0878b75b472ada774a6a73c0fe5c9d21b4856702148df09d41d7e9d",
    "m2_corrected_bootstrap": "e16610d1af87fea1f42a13ae1fcc2bc1e80ee78fe7343f91576858505563750d",
}

SOURCE_PATHS = {
    "m0_metrics": "artifacts/evaluations/m0_three_model_v1/dump/m0_metrics.json",
    "m1_metrics": "artifacts/evaluations/m1_three_model_v1/dump/m1_metrics.json",
    "m1_trajectory": "artifacts/evaluations/m1_three_model_v1/dump/m1_trajectory.csv",
    "m0_m1_comparison": "artifacts/evaluations/m1_three_model_v1/dump/m0_m1_comparison.csv",
    "m2_evaluation_family": "artifacts/evaluations/m2_three_model_oscar_v1/dump/evaluation_family_result.json",
    "m2_scientific_analysis": "artifacts/evaluations/m2_three_model_oscar_v1/dump/scientific_analysis.json",
    "m2_checkpoint_trajectory": "artifacts/evaluations/m2_three_model_oscar_v1/dump/m2_checkpoint_trajectory.csv",
    "m2_endpoint_breakdown": "artifacts/evaluations/m2_three_model_oscar_v1/dump/endpoint_relation_form_summary.csv",
    "m2_corrected_bootstrap": "artifacts/evaluations/m2_three_model_oscar_v1/dump/corrected_paired_subject_bootstrap.csv",
}

MODELS = ("olmo", "qwen", "smollm")
M2_ARMS = ("M2-A", "M2-B")
STATES = ("M0", "M1", "M2-A", "M2-B")
DIRECTIONS = ("en_to_en", "tr_to_en", "tr_to_tr")
RELATIONS = ("born_in", "field_of_study", "lives_in", "profession", "works_in_industry")
FORM_IDS = ("form_a", "form_b", "form_c", "form_d")
SCAFFOLDS = ("direct", "qa")
M1_TRAJECTORY_METRICS = (
    "wikitext_bpb",
    "turkish_bpb",
    "factual_cheap_top1_rate",
    "factual_top1_rate",
    "exact_prefix_top1_accuracy",
    "generation_ppl",
    "blimp_accuracy",
    "hellaswag_acc_norm",
    "turblimp_acc_norm",
)
M2_TRAJECTORY_METRICS = (
    "factual_top1",
    "oscar_bpb",
    "trwiki_bpb",
    "wikitext_bpb",
    "exact_top1",
)

MODEL_METADATA = {
    "olmo": {"label": "OLMo-2-0425-1B", "model_id": "allenai/OLMo-2-0425-1B"},
    "qwen": {"label": "Qwen2.5-1.5B", "model_id": "Qwen/Qwen2.5-1.5B"},
    "smollm": {"label": "SmolLM2-1.7B", "model_id": "HuggingFaceTB/SmolLM2-1.7B"},
}

GATE_DEFINITIONS = (
    {
        "id": "m2a_en_to_en_drop_at_most_0_05",
        "threshold": -0.05,
        "operator": ">=",
        "metric": "en_to_en_delta",
        "label": {"en": "M2-A English retention drop ≤ 5 pp", "tr": "M2-A İngilizce koruma düşüşü ≤ 5 yüzde puanı"},
    },
    {
        "id": "m2a_oscar_delta_bpb_at_most_minus_0_07400058",
        "threshold": -0.07400058,
        "operator": "<=",
        "metric": "oscar_delta_bpb",
        "label": {"en": "M2-A OSCAR BPB change ≤ −0.07400058", "tr": "M2-A OSCAR BPB değişimi ≤ −0.07400058"},
    },
    {
        "id": "m2a_wikitext_delta_bpb_at_most_0_32192809",
        "threshold": 0.32192809,
        "operator": "<=",
        "metric": "wikitext_delta_bpb",
        "label": {"en": "M2-A WikiText BPB change ≤ 0.32192809", "tr": "M2-A WikiText BPB değişimi ≤ 0.32192809"},
    },
    {
        "id": "relearning_ci95_low_above_zero",
        "threshold": 0.0,
        "operator": ">",
        "metric": "relearning_ci95_low",
        "label": {"en": "Relearning 95% CI lower bound > 0", "tr": "Yeniden öğrenme %95 GA alt sınırı > 0"},
    },
    {
        "id": "relearning_point_gain_at_least_0_05",
        "threshold": 0.05,
        "operator": ">=",
        "metric": "relearning_estimate",
        "label": {"en": "Relearning point gain ≥ 5 pp", "tr": "Yeniden öğrenme nokta kazanımı ≥ 5 yüzde puanı"},
    },
)


class DataContractError(ValueError):
    """Raised when a frozen source no longer satisfies the reporting contract."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise DataContractError(message)


def _float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def _int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _input_manifest_sha256(provenance: list[dict[str, Any]]) -> str:
    """Hash the ordered source identity list, excluding derived metadata and self-reference."""
    canonical = [
        {"id": record["id"], "path": record["path"], "sha256": record["sha256"]}
        for record in provenance
    ]
    encoded = json.dumps(canonical, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _load_sources(repo_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    loaded: dict[str, Any] = {}
    records: list[dict[str, Any]] = []
    for key, relative in SOURCE_PATHS.items():
        path = repo_root / relative
        _require(path.is_file(), f"missing frozen source: {relative}")
        actual_sha = _hash(path)
        _require(actual_sha == EXPECTED_SOURCE_SHA256[key], f"source SHA mismatch for {relative}: {actual_sha}")
        if path.suffix == ".json":
            loaded[key] = json.loads(path.read_text(encoding="utf-8"))
        else:
            with path.open(newline="", encoding="utf-8") as handle:
                loaded[key] = list(csv.DictReader(handle))
        records.append(
            {
                "id": key,
                "path": relative,
                "sha256": actual_sha,
                "bytes": path.stat().st_size,
                "role": {
                    "m0_metrics": "M0 compact metric snapshot",
                    "m1_metrics": "M1 compact metric/control snapshot",
                    "m1_trajectory": "M1 checkpoint trajectory",
                    "m0_m1_comparison": "M0-to-M1 metric comparison rows",
                    "m2_evaluation_family": "M2 endpoint evaluation completion ledger",
                    "m2_scientific_analysis": "M2 scientific endpoint/gate analysis",
                    "m2_checkpoint_trajectory": "M2 checkpoint trajectory",
                    "m2_endpoint_breakdown": "M2 endpoint relation/form/scaffold breakdown",
                    "m2_corrected_bootstrap": "canonical paired-subject bootstrap correction",
                }[key],
            }
        )
    return loaded, records


def _validate_sources(sources: dict[str, Any]) -> None:
    m0 = sources["m0_metrics"]
    _require(m0.get("state") == "M0", "M0 snapshot has unexpected state")
    _require(len(m0.get("metric_rows", [])) == 75, "M0 metric row count must be 75")
    _require({row.get("model") for row in m0["metric_rows"]} == set(MODELS), "M0 model vocabulary mismatch")
    _require(
        len({(row.get("model"), row.get("metric")) for row in m0["metric_rows"]}) == 75,
        "duplicate M0 model/metric key",
    )

    m1 = sources["m1_metrics"]
    _require(m1.get("state") == "M1", "M1 snapshot has unexpected state")
    _require(m1.get("counts", {}).get("complete_states") == 111, "M1 complete state count must be 111")
    _require(len(m1.get("trajectory", [])) == 111, "M1 JSON trajectory row count must be 111")
    _require(len(m1.get("metric_rows", [])) == 2103, "M1 JSON metric row count must be 2103")

    m1_traj = sources["m1_trajectory"]
    _require(len(m1_traj) == 111, "M1 CSV trajectory row count must be 111")
    _require({row.get("model") for row in m1_traj} == set(MODELS), "M1 trajectory model vocabulary mismatch")
    _require(
        len({(row.get("model"), row.get("checkpoint")) for row in m1_traj}) == 111,
        "duplicate M1 trajectory model/checkpoint key",
    )

    comparison = sources["m0_m1_comparison"]
    _require(len(comparison) == 2103, "M0/M1 comparison row count must be 2103")
    _require(
        len({(row.get("model"), row.get("state"), row.get("metric")) for row in comparison}) == len(comparison),
        "duplicate M0/M1 comparison model/state/metric key",
    )

    family = sources["m2_evaluation_family"]
    _require(family.get("status") == "M2_EVAL_V2_COMPLETE", "M2 family is not complete")
    _require(family.get("gpu_complete_count") == 63, "M2 GPU complete count must be 63")
    _require(family.get("gpu_task_count") == 63, "M2 GPU task count must be 63")
    _require(family.get("total_scientific_states") == 63, "M2 scientific state count must be 63")
    tasks = family.get("tasks", [])
    _require(len(tasks) == 63, "M2 family task row count must be 63")
    _require(len({task.get("state_id") for task in tasks}) == 63, "duplicate M2 family state_id")

    analysis = sources["m2_scientific_analysis"]
    _require(set(analysis.get("roles", {})) == set(MODELS), "M2 scientific model vocabulary mismatch")
    _require(analysis.get("estimands", {}).get("transfer") == "M2-A minus M1", "transfer estimand mismatch")
    _require(analysis.get("estimands", {}).get("relearning") == "M2-B minus M2-A", "relearning estimand mismatch")
    for model in MODELS:
        role = analysis["roles"][model]
        _require(set(role.get("state_metrics", {})) == {"M1", "M2-A", "M2-B"}, f"{model} endpoint states mismatch")
        for state in ("M1", "M2-A", "M2-B"):
            _require(set(role["state_metrics"][state]) == set(DIRECTIONS), f"{model} {state} direction mismatch")

    m2_traj = sources["m2_checkpoint_trajectory"]
    _require(len(m2_traj) == 60, "M2 checkpoint trajectory row count must be 60")
    _require({row.get("model") for row in m2_traj} == set(MODELS), "M2 trajectory model vocabulary mismatch")
    _require({row.get("arm") for row in m2_traj} == set(M2_ARMS), "M2 trajectory arm vocabulary mismatch")
    _require(
        len({(row.get("model"), row.get("arm"), row.get("update")) for row in m2_traj}) == 60,
        "duplicate M2 trajectory model/arm/update key",
    )
    for model in MODELS:
        for arm in M2_ARMS:
            _require(sum(row["model"] == model and row["arm"] == arm for row in m2_traj) == 10, f"{model}/{arm} must have 10 M2 checkpoints")

    breakdown = sources["m2_endpoint_breakdown"]
    _require(len(breakdown) == 66, "M2 endpoint breakdown row count must be 66")
    _require(
        len({(row.get("model"), row.get("arm"), row.get("axis"), row.get("key")) for row in breakdown}) == 66,
        "duplicate M2 endpoint breakdown key",
    )
    _require(
        {row.get("axis") for row in breakdown} == {"relation", "form_id", "scaffold_id"},
        "M2 endpoint breakdown axis vocabulary mismatch",
    )
    expected_axis_counts = {"relation": 30, "form_id": 24, "scaffold_id": 12}
    for axis, count in expected_axis_counts.items():
        _require(sum(row["axis"] == axis for row in breakdown) == count, f"M2 {axis} breakdown count must be {count}")
    for row in breakdown:
        n = int(row["n"])
        top1 = int(row["top1"])
        accuracy = float(row["accuracy"])
        _require(n > 0 and 0 <= top1 <= n, f"invalid M2 breakdown count: {row}")
        _require(abs(accuracy - top1 / n) < 1.1e-6, f"M2 breakdown accuracy/count mismatch: {row}")

    bootstrap = sources["m2_corrected_bootstrap"]
    _require(len(bootstrap) == 39, "corrected bootstrap row count must be 39")
    _require(
        len({(row.get("model"), row.get("contrast"), row.get("subset")) for row in bootstrap}) == 39,
        "duplicate corrected bootstrap model/contrast/subset key",
    )
    _require({row.get("model") for row in bootstrap} == set(MODELS), "bootstrap model vocabulary mismatch")
    _require({row.get("contrast") for row in bootstrap} == {"transfer", "relearning"}, "bootstrap contrast vocabulary mismatch")
    _require(sum(row.get("contrast") == "transfer" for row in bootstrap) == 3, "bootstrap must contain one all-subject transfer row per model")
    _require(sum(row.get("contrast") == "relearning" for row in bootstrap) == 36, "bootstrap relearning row count must be 36")
    for row in bootstrap:
        _require(int(row["n_subjects"]) == 100, f"bootstrap n_subjects must be 100: {row}")
        _require(float(row["ci95_low"]) <= float(row["estimate"]) <= float(row["ci95_high"]), f"bootstrap interval does not contain estimate: {row}")


def _typed_m1_trajectory(rows: Iterable[dict[str, str]]) -> list[dict[str, Any]]:
    output = []
    for row in rows:
        item: dict[str, Any] = {
            "model": row["model"],
            "checkpoint": row["checkpoint"],
            "epoch": int(row["epoch"]),
            "update": int(row["update"]),
            "full_state": row["full_state"] == "True",
            "state_kind": row["state_kind"],
            "task_status": row["task_status"],
        }
        for metric in M1_TRAJECTORY_METRICS:
            item[metric] = _float(row.get(metric))
        output.append(item)
    return output


def _typed_m2_trajectory(rows: Iterable[dict[str, str]]) -> list[dict[str, Any]]:
    output = []
    for row in rows:
        item: dict[str, Any] = {
            "model": row["model"],
            "arm": row["arm"],
            "update": int(row["update"]),
            "dose_pct": float(row["dose_pct"]),
            "n": int(row["n"]),
        }
        for metric in M2_TRAJECTORY_METRICS:
            item[metric] = float(row[metric])
        output.append(item)
    return output


def _m0_rows(source: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in source["metric_rows"]:
        rows.append(
            {
                "model": row["model"],
                "metric": row["metric"],
                "family": row["family"],
                "value": _float(row.get("value")),
                "unit": row.get("unit"),
                "direction": row.get("direction"),
                "sample_count": _int(row.get("sample_count")),
                "status": row.get("status", "observed" if row.get("value") is not None else "pending"),
            }
        )
    return rows


def _state_endpoints(analysis: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for model in MODELS:
        for state in ("M1", "M2-A", "M2-B"):
            for direction in DIRECTIONS:
                metric = analysis["roles"][model]["state_metrics"][state][direction]
                rows.append(
                    {
                        "model": model,
                        "state": state,
                        "direction": direction,
                        "n": int(metric["n"]),
                        "top1_accuracy": float(metric["top1_accuracy"]),
                        "mean_margin": float(metric["mean_margin"]),
                        "per_relation_accuracy": {
                            relation: float(metric["per_relation_accuracy"][relation]) for relation in RELATIONS
                        },
                    }
                )
    return rows


def _breakdown_rows(rows: Iterable[dict[str, str]]) -> list[dict[str, Any]]:
    return [
        {
            "model": row["model"],
            "arm": row["arm"],
            "axis": row["axis"],
            "key": row["key"],
            "n": int(row["n"]),
            "top1": int(row["top1"]),
            "accuracy": float(row["accuracy"]),
        }
        for row in rows
    ]


def _bootstrap_rows(rows: Iterable[dict[str, str]], endpoints: list[dict[str, Any]]) -> list[dict[str, Any]]:
    endpoint_index = {(row["model"], row["state"], row["direction"]): row["top1_accuracy"] for row in endpoints}
    output = []
    for row in rows:
        item: dict[str, Any] = {
            "model": row["model"],
            "contrast": row["contrast"],
            "subset": row["subset"],
            "n_subjects": int(row["n_subjects"]),
            "estimate": float(row["estimate"]),
            "ci95_low": float(row["ci95_low"]),
            "ci95_high": float(row["ci95_high"]),
            "endpoint_delta": None,
        }
        if row["subset"] == "all":
            if row["contrast"] == "transfer":
                item["endpoint_delta"] = endpoint_index[(row["model"], "M2-A", "tr_to_en")] - endpoint_index[(row["model"], "M1", "tr_to_en")]
            else:
                item["endpoint_delta"] = endpoint_index[(row["model"], "M2-B", "tr_to_en")] - endpoint_index[(row["model"], "M2-A", "tr_to_en")]
            _require(abs(item["endpoint_delta"] - item["estimate"]) < 1e-12, f"corrected all-subject estimate does not match endpoint delta: {row}")
        output.append(item)
    return output


def _gates(analysis: dict[str, Any], bootstrap: list[dict[str, Any]], endpoints: list[dict[str, Any]]) -> list[dict[str, Any]]:
    endpoint_index = {(row["model"], row["state"], row["direction"]): row["top1_accuracy"] for row in endpoints}
    bootstrap_all = {(row["model"], row["contrast"]): row for row in bootstrap if row["subset"] == "all"}
    output = []
    for model in MODELS:
        role = analysis["roles"][model]
        m1_en = endpoint_index[(model, "M1", "en_to_en")]
        m2a_en = endpoint_index[(model, "M2-A", "en_to_en")]
        en_delta = m2a_en - m1_en
        oscar_delta = role["bits_per_byte"]["M2-A_oscar"] - role["bits_per_byte"]["M1_oscar"]
        wikitext_delta = role["bits_per_byte"]["M2-A_wikitext"] - role["bits_per_byte"]["M1_wikitext"]
        relearning = bootstrap_all[(model, "relearning")]
        observed = {
            "m2a_en_to_en_drop_at_most_0_05": en_delta,
            "m2a_oscar_delta_bpb_at_most_minus_0_07400058": oscar_delta,
            "m2a_wikitext_delta_bpb_at_most_0_32192809": wikitext_delta,
            "relearning_ci95_low_above_zero": relearning["ci95_low"],
            "relearning_point_gain_at_least_0_05": relearning["estimate"],
        }
        expected_pass = {
            "m2a_en_to_en_drop_at_most_0_05": en_delta >= -0.05,
            "m2a_oscar_delta_bpb_at_most_minus_0_07400058": oscar_delta <= -0.07400058,
            "m2a_wikitext_delta_bpb_at_most_0_32192809": wikitext_delta <= 0.32192809,
            "relearning_ci95_low_above_zero": relearning["ci95_low"] > 0,
            "relearning_point_gain_at_least_0_05": relearning["estimate"] >= 0.05,
        }
        _require(bool(role["all_primary_gates_pass"]) is False, f"{model} unexpectedly has primary gates pass")
        for definition in GATE_DEFINITIONS:
            gate_id = definition["id"]
            legacy_source_pass = bool(role["gates"][gate_id])
            # The compact scientific_analysis.json predates the canonical probe_id correction and
            # therefore contains the superseded CI gate for OLMo and SmolLM.  The corrected
            # paired-subject bootstrap is the authoritative input for this one gate.
            if gate_id != "relearning_ci95_low_above_zero":
                _require(legacy_source_pass == expected_pass[gate_id], f"derived gate mismatch for {model}/{gate_id}")
            source_pass = expected_pass[gate_id]
            output.append(
                {
                    "model": model,
                    "gate_id": gate_id,
                    "label": definition["label"],
                    "operator": definition["operator"],
                    "threshold": definition["threshold"],
                    "observed": observed[gate_id],
                    "passed": source_pass,
                    "source_passed": source_pass,
                    "legacy_analysis_passed": legacy_source_pass,
                }
            )
    return output


def _primary_gate_summary(gates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_model: dict[str, list[dict[str, Any]]] = {model: [] for model in MODELS}
    for row in gates:
        by_model[row["model"]].append(row)
    output = []
    for model in MODELS:
        rows = by_model[model]
        output.append(
            {
                "model": model,
                "all_primary_gates_pass": all(row["passed"] for row in rows),
                "passed_count": sum(row["passed"] for row in rows),
                "gate_count": len(rows),
            }
        )
    return output


def _semantics() -> dict[str, Any]:
    return {
        "states": {
            "M0": {"en": "Frozen pretrained base", "tr": "Dondurulmuş ön-eğitimli taban"},
            "M1": {"en": "English factual acquisition", "tr": "İngilizce olgusal edinim"},
            "M2-A": {"en": "General Turkish adaptation; no target-fact re-exposure", "tr": "Genel Türkçe uyarlama; hedef olgu tekrarı yok"},
            "M2-B": {"en": "Matched Turkish adaptation with controlled target-fact re-exposure", "tr": "Kontrollü hedef olgu tekrarlı eşlenmiş Türkçe uyarlama"},
        },
        "estimands": {
            "transfer": {"en": "M2-A − M1 on tr→en factual access", "tr": "tr→en olgusal erişimde M2-A − M1"},
            "relearning": {"en": "M2-B − M2-A on tr→en factual access", "tr": "tr→en olgusal erişimde M2-B − M2-A"},
        },
        "metrics": {
            "top1_accuracy": {"en": "Factual top-1 accuracy", "tr": "Olgusal top-1 doğruluk", "unit": "fraction", "direction": "higher"},
            "factual_top1": {"en": "Checkpoint factual top-1", "tr": "Checkpoint olgusal top-1", "unit": "fraction", "direction": "higher"},
            "oscar_bpb": {"en": "OSCAR bits per byte", "tr": "OSCAR byte başına bit", "unit": "bits/byte", "direction": "lower"},
            "trwiki_bpb": {"en": "trWiki bits per byte", "tr": "trWiki byte başına bit", "unit": "bits/byte", "direction": "lower"},
            "wikitext_bpb": {"en": "WikiText bits per byte", "tr": "WikiText byte başına bit", "unit": "bits/byte", "direction": "lower"},
            "exact_top1": {"en": "Exact-prefix top-1", "tr": "Exact-prefix top-1", "unit": "fraction", "direction": "higher"},
        },
        "notes": {
            "en": "Missing values remain null. Checkpoint factual top-1 uses 1,500 probes and is not the 12,000-probe endpoint suite.",
            "tr": "Eksik değerler null kalır. Checkpoint olgusal top-1 1.500 prob kullanır; 12.000 prob'luk endpoint paketiyle aynı değildir.",
        },
    }


def build_manifest(repo_root: Path) -> dict[str, Any]:
    sources, provenance = _load_sources(repo_root)
    _validate_sources(sources)
    endpoints = _state_endpoints(sources["m2_scientific_analysis"])
    bootstrap = _bootstrap_rows(sources["m2_corrected_bootstrap"], endpoints)
    gates = _gates(sources["m2_scientific_analysis"], bootstrap, endpoints)
    primary_gate_summary = _primary_gate_summary(gates)
    _require(all(not row["all_primary_gates_pass"] for row in primary_gate_summary), "a model unexpectedly passes every primary gate")
    for record in provenance:
        row_counts = {
            "m0_metrics": 75,
            "m1_metrics": 2103,
            "m1_trajectory": 111,
            "m0_m1_comparison": 2103,
            "m2_evaluation_family": 63,
            "m2_scientific_analysis": 3,
            "m2_checkpoint_trajectory": 60,
            "m2_endpoint_breakdown": 66,
            "m2_corrected_bootstrap": 39,
        }
        record["row_count"] = row_counts[record["id"]]
    input_manifest_sha256 = _input_manifest_sha256(provenance)

    m1_trajectory = _typed_m1_trajectory(sources["m1_trajectory"])
    m2_trajectory = _typed_m2_trajectory(sources["m2_checkpoint_trajectory"])
    breakdown = _breakdown_rows(sources["m2_endpoint_breakdown"])
    all_estimands = [row for row in bootstrap if row["subset"] == "all"]
    _require(len(all_estimands) == 6, "six all-subject estimands are required")

    return {
        "schema_version": "results-explorer-data-v1",
        # ``manifest_sha256`` is retained as the short UI-compatible alias; the explicit
        # ``input_manifest_sha256`` name is the canonical identity field.
        "input_manifest_sha256": input_manifest_sha256,
        "manifest_sha256": input_manifest_sha256,
        "contract": {
            "name": "M2 results website and thesis reporting / Phase A",
            "generated_from": "frozen compact M0/M1/M2 artifacts",
            "scientific_scope": "descriptive transfer and relearning reporting; no model selection",
            "models": list(MODELS),
            "states": list(STATES),
            "m2_arms_are_parallel_siblings": True,
        },
        "overview": {
            "completion": {
                "m1_evaluation_states": {"observed": 111, "expected": 111},
                "m2_evaluation_states": {"observed": 63, "expected": 63},
                "m2_training_checkpoints": {"observed": 60, "expected": 60},
            },
            "terminal_conclusion": {
                "en": "No model passes all precommitted primary gates; Qwen has the strongest descriptive relearning estimate, but remains below the +0.05 threshold.",
                "tr": "Hiçbir model önceden belirlenen tüm birincil kapıları geçmiyor; Qwen en güçlü betimsel yeniden öğrenme tahminine sahip, ancak +0,05 eşiğinin altında kalıyor.",
            },
            "descriptive_relearning_leader": "qwen",
            "primary_model_selected": False,
        },
        "models": [{"id": model, **MODEL_METADATA[model]} for model in MODELS],
        "thresholds": {
            "relearning_point_gain": 0.05,
            "relearning_ci_lower_bound": 0.0,
            "zero_effect": 0.0,
        },
        "estimands": all_estimands,
        "gates": gates,
        "primary_gate_summary": primary_gate_summary,
        "state_endpoints": endpoints,
        "m0_metrics": _m0_rows(sources["m0_metrics"]),
        "trajectories": {"m1": m1_trajectory, "m2": m2_trajectory},
        "breakdowns": breakdown,
        "bootstrap": bootstrap,
        "semantics": _semantics(),
        "provenance": {
            "sources": provenance,
            "input_manifest_sha256": input_manifest_sha256,
            "identity_algorithm": "sha256(canonical JSON of ordered source id/path/sha256 records; derived metadata excluded)",
            "canonical_correction": {
                "artifact": "corrected_paired_subject_bootstrap.csv",
                "probe_id": "paired_subject_bootstrap",
                "subjects": 100,
                "prompt_variants": 8,
                "draws": 10000,
                "seed": 42,
            },
            "historical_bootstrap_warning": {
                "en": "The executed fact_id bootstrap is historical and superseded. The canonical correction uses probe_id paired subjects with 100 subjects, eight prompt variants, 10,000 draws and seed 42.",
                "tr": "Çalıştırılmış fact_id bootstrap tarihsel ve geçersiz kılınmıştır. Kanonik düzeltme probe_id eşlenmiş özneler, 100 özne, sekiz prompt varyantı, 10.000 çekiliş ve seed 42 kullanır.",
            },
        },
    }


def build(repo_root: Path, output_path: Path | None = None) -> Path:
    payload = build_manifest(repo_root)
    output = output_path or repo_root / "tools/m0-dashboard/data/results_explorer_data.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    output = build(args.repo_root.resolve(), args.output.resolve() if args.output else None)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
