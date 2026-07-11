from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from transfer_vs_relearning.utils.io import (
    read_csv_rows,
    read_jsonl,
    sha256_file,
    write_csv,
    write_json,
)


VIEWS = ("exact", "direct", "qa")
METADATA_FIELDS = (
    "subject_id",
    "subject",
    "relation",
    "expected_answer",
    "correct_object_id",
    "branch",
    "frequency",
    "popularity",
    "name_type",
    "name_rarity",
)
GROUP_FIELDS = ("relation", "branch", "frequency", "popularity", "name_type", "name_rarity")


def _index(rows: list[dict[str, str]], label: str) -> dict[str, dict[str, str]]:
    indexed: dict[str, dict[str, str]] = {}
    for row in rows:
        fact_id = row.get("fact_id", "")
        if not fact_id:
            raise ValueError(f"{label}: row without fact_id")
        if fact_id in indexed:
            raise ValueError(f"{label}: duplicate fact_id {fact_id}")
        indexed[fact_id] = row
    return indexed


def _normalize_prompt(text: str) -> str:
    return " ".join(text.split()).strip().rstrip(".?!").casefold()


def _training_prompt(row: dict[str, Any]) -> str:
    text = str(row.get("text", "")).strip()
    answer = str(row.get("answer", "")).strip()
    if answer and text.casefold().rstrip(".?!").endswith(answer.casefold().rstrip(".?!")):
        end = len(text.rstrip(".?!")) - len(answer.rstrip(".?!"))
        text = text.rstrip(".?!")[:end]
    return _normalize_prompt(text)


def _group_summary(rows: list[dict[str, Any]], field: str) -> dict[str, dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row[field])].append(row)
    return {
        value: {
            "facts": len(group),
            "exact_top1": sum(bool(row["exact_top1"]) for row in group),
            "direct_top1": sum(bool(row["direct_top1"]) for row in group),
            "qa_top1": sum(bool(row["qa_top1"]) for row in group),
            "triple_robust": sum(bool(row["triple_robust"]) for row in group),
            "triple_robust_rate": round(
                sum(bool(row["triple_robust"]) for row in group) / len(group), 6
            ),
        }
        for value, group in sorted(groups.items())
    }


def audit_acquisition_checkpoint(
    exact_path: Path,
    direct_path: Path,
    qa_path: Path,
    output_dir: Path,
    *,
    train_path: Path | None = None,
    validation_path: Path | None = None,
) -> dict[str, Any]:
    paths = {"exact": exact_path, "direct": direct_path, "qa": qa_path}
    indexed = {view: _index(read_csv_rows(path), view) for view, path in paths.items()}
    fact_sets = {view: set(rows) for view, rows in indexed.items()}
    if len({frozenset(facts) for facts in fact_sets.values()}) != 1:
        counts = {view: len(facts) for view, facts in fact_sets.items()}
        raise ValueError(f"evaluation fact_id sets differ: {counts}")

    audit_rows: list[dict[str, Any]] = []
    for fact_id in sorted(fact_sets["exact"]):
        source = indexed["exact"][fact_id]
        for view in ("direct", "qa"):
            mismatches = [
                field
                for field in METADATA_FIELDS
                if indexed[view][fact_id].get(field, "") != source.get(field, "")
            ]
            if mismatches:
                raise ValueError(f"{fact_id}: {view} metadata mismatch: {mismatches}")

        statuses = {
            view: int(indexed[view][fact_id]["correct_rank_mean"]) == 1 for view in VIEWS
        }
        pattern = "_".join(f"{view[0].upper()}{int(statuses[view])}" for view in VIEWS)
        row: dict[str, Any] = {
            "fact_id": fact_id,
            **{field: source.get(field, "") for field in METADATA_FIELDS},
            "exact_rank": int(indexed["exact"][fact_id]["correct_rank_mean"]),
            "direct_rank": int(indexed["direct"][fact_id]["correct_rank_mean"]),
            "qa_rank": int(indexed["qa"][fact_id]["correct_rank_mean"]),
            "exact_top1": statuses["exact"],
            "direct_top1": statuses["direct"],
            "qa_top1": statuses["qa"],
            "triple_robust": all(statuses.values()),
            "pass_pattern": pattern,
            "exact_prediction": indexed["exact"][fact_id].get("predicted_surface_form", ""),
            "direct_prediction": indexed["direct"][fact_id].get("predicted_surface_form", ""),
            "qa_prediction": indexed["qa"][fact_id].get("predicted_surface_form", ""),
            "exact_margin": indexed["exact"][fact_id].get("margin", ""),
            "direct_margin": indexed["direct"][fact_id].get("margin", ""),
            "qa_margin": indexed["qa"][fact_id].get("margin", ""),
            "number_of_candidates": source.get("number_of_candidates", ""),
        }
        for view in VIEWS:
            row[f"{view}_outranks_other_city"] = indexed[view][fact_id].get(
                "correct_outranks_other_city", ""
            )
        audit_rows.append(row)

    triple_rows = [row for row in audit_rows if row["triple_robust"]]
    patterns = Counter(str(row["pass_pattern"]) for row in audit_rows)
    subject_triple_counts = Counter(str(row["subject_id"]) for row in triple_rows)

    city_rows = [row for row in audit_rows if row["relation"] in {"born_in", "lives_in"}]
    city_binding = {
        view: {
            "facts": len(city_rows),
            "correct_outranks_other_city": sum(
                str(row[f"{view}_outranks_other_city"]).casefold() == "true" for row in city_rows
            ),
        }
        for view in VIEWS
    }

    prompt_leakage: dict[str, Any] | None = None
    if train_path is not None:
        train_rows = read_jsonl(train_path)
        training_prompts = {_training_prompt(row) for row in train_rows}
        prompt_leakage = {
            "train_rows": len(train_rows),
            "unique_normalized_training_prompts": len(training_prompts),
            "normalized_prompt_matches": {
                view: sum(
                    _normalize_prompt(indexed[view][fact_id].get("rendered_prompt", ""))
                    in training_prompts
                    for fact_id in sorted(fact_sets["exact"])
                )
                for view in VIEWS
            },
        }

    input_paths = dict(paths)
    if train_path is not None:
        input_paths["train"] = train_path
    if validation_path is not None:
        input_paths["validation"] = validation_path

    summary: dict[str, Any] = {
        "facts": len(audit_rows),
        "exact_top1": sum(bool(row["exact_top1"]) for row in audit_rows),
        "direct_top1": sum(bool(row["direct_top1"]) for row in audit_rows),
        "qa_top1": sum(bool(row["qa_top1"]) for row in audit_rows),
        "triple_robust": len(triple_rows),
        "triple_robust_rate": round(len(triple_rows) / len(audit_rows), 6),
        "pass_patterns": dict(sorted(patterns.items())),
        "groups": {field: _group_summary(audit_rows, field) for field in GROUP_FIELDS},
        "subjects": {
            "total": len({row["subject_id"] for row in audit_rows}),
            "with_at_least_one_triple_robust_fact": len(subject_triple_counts),
            "with_all_five_facts_triple_robust": sum(count == 5 for count in subject_triple_counts.values()),
            "triple_robust_fact_count_distribution": dict(
                sorted(Counter(subject_triple_counts.values()).items())
            ),
        },
        "city_relation_binding": city_binding,
        "candidate_inventory_sizes_by_relation": {
            relation: sorted(
                {int(row["number_of_candidates"]) for row in audit_rows if row["relation"] == relation}
            )
            for relation in sorted({str(row["relation"]) for row in audit_rows})
        },
        "input_sha256": {name: sha256_file(path) for name, path in input_paths.items()},
        "prompt_leakage": prompt_leakage,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "fact_audit.csv", audit_rows)
    write_csv(output_dir / "triple_robust_facts.csv", triple_rows, list(audit_rows[0]))
    write_json(output_dir / "summary.json", summary)
    return summary
