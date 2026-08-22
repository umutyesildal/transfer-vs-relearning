from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "configs/evaluation/eval_v2_m0_metric_normalization_v1.yaml"
CONTRACT = ROOT / "documentation/contracts/evaluation/eval-v2-m0-metric-normalization-v1.md"


def test_m0_normalization_contract_is_prepared_and_fail_closed() -> None:
    payload = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))

    assert payload["status"] == "prepared_unexecuted"
    assert payload["execution_authorized"] is False
    assert payload["normalization_authorized"] is False
    assert payload["rescore_authorized"] is False
    assert payload["input_projection"]["required_source_rows"] == 24
    assert payload["input_projection"]["canonical_non_pile_rows"] == 21
    assert payload["input_projection"]["exact_prefix_rows"] == 3
    assert payload["primary_retention_unit"] == "bits_per_byte"
    assert payload["parent_comparison_at_m0"] == "not_applicable"
    assert not any("pile" in lane.casefold() for lane in payload["required_lane_ids"])
    assert payload["operator"]["status"] == "contract_only_operator_not_implemented"
    assert CONTRACT.is_file()


def test_m0_normalization_contract_binds_completed_projection() -> None:
    payload = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    projection = payload["input_projection"]

    assert projection["source_registry_sha256"] == (
        "a0dca252afe7c1d03e458a60a8b48d7e8d8858e0ad95e6e8be696311a0b34265"
    )
    assert projection["projection_manifest_sha256"] == (
        "9081b8eabef1ddfe1139754176cdcb1a26757fa3367d511cf81183536c8a9e0c"
    )
    assert payload["output_root"].endswith("eval_v2_m0_metric_normalization_v1")
