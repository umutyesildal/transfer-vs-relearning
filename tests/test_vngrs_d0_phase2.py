from __future__ import annotations

import json
import hashlib
from pathlib import Path

import pytest
import yaml

from transfer_vs_relearning.corpora.vngrs.d0_audit import (
    D0Document,
    EXPECTED_MODELS,
    exact_heldout_split,
    human_review_sample_with_stratum_floor,
)
from transfer_vs_relearning.corpora.vngrs.d0_phase2 import (
    run_oscar_phase2_evidence,
    split_tokenizer_accounting,
)
from transfer_vs_relearning.corpora.vngrs.d0_review import (
    build_review_packet,
    decision_template,
    review_packet_sha256,
)
from transfer_vs_relearning.corpora.vngrs.metadata import (
    FROZEN_SELECTED_SHARD_PATHS,
    canonical_json_sha256,
)


ROOT = Path(__file__).resolve().parents[1]


class _Tokenizer:
    def __len__(self) -> int:
        return 1024


class _Adapter:
    def __init__(self, role: str, width: int) -> None:
        self.role = role
        self.model_id, self.revision = EXPECTED_MODELS[role]
        self.manifest_sha256 = f"{width:064x}"
        self.asset_sha256 = f"{width + 10:064x}"
        self.tokenizer = _Tokenizer()
        self.width = width

    def encode(self, text: str, *, add_special_tokens: bool = False) -> list[int]:
        assert add_special_tokens is False
        return list(range(max(1, len(text.split()) + self.width)))


def _documents() -> list[D0Document]:
    return [
        D0Document(
            f"doc-{index:04d}",
            FROZEN_SELECTED_SHARD_PATHS[index % 8],
            "oscar",
            f"Türkçe Phase 2 deneme belgesi {index}." + ("\u0085devam" if index == 3 else ""),
        )
        for index in range(128)
    ]


def _jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def _predecessors(tmp_path: Path, documents: list[D0Document]) -> tuple[Path, Path, list[dict]]:
    split_root = tmp_path / "split"
    coverage_root = tmp_path / "coverage"
    split = exact_heldout_split(documents, heldout_documents=16)
    split_state = {
        "status": "AWAITING_HUMAN_REVIEW",
        "document_count": len(documents),
        "document_ids_sha256": canonical_json_sha256(
            sorted(row.stable_document_id for row in documents)
        ),
        "split_namespace": split["namespace"],
        "split_seed": split["seed"],
        "split_sha256": canonical_json_sha256(split),
    }
    (split_root / "control").mkdir(parents=True)
    (split_root / "control/phase1_state.json").write_text(json.dumps(split_state))
    _jsonl(
        split_root / "splits/train_document_ids.jsonl",
        [{"stable_document_id": value} for value in split["train_document_ids"]],
    )
    _jsonl(
        split_root / "splits/heldout_document_ids.jsonl",
        [{"stable_document_id": value} for value in split["heldout_document_ids"]],
    )
    sample = human_review_sample_with_stratum_floor(documents, sample_size=8)
    packet = build_review_packet(documents, sample)
    packet_hash = review_packet_sha256(packet)
    coverage_state = {
        "status": "AWAITING_HUMAN_REVIEW",
        "review_packet_sha256": packet_hash,
    }
    coverage_final = {
        "status": "AWAITING_HUMAN_REVIEW",
        "coverage_validated": True,
        "split_rewritten": False,
    }
    inventory = {
        "nonempty_strata": 1,
        "strata": [
            {"stratum": "q0", "documents": len(documents), "utf8_bytes": 1_553_923_133},
            *[
                {"stratum": f"q{index}", "documents": 0, "utf8_bytes": 0}
                for index in (1, 2, 3)
            ],
        ],
    }
    (coverage_root / "control").mkdir(parents=True)
    (coverage_root / "reports").mkdir(parents=True)
    (coverage_root / "control/coverage_state.json").write_text(json.dumps(coverage_state))
    (coverage_root / "control/final_audit.json").write_text(json.dumps(coverage_final))
    (coverage_root / "reports/quartile_population_inventory.json").write_text(
        json.dumps(inventory)
    )
    _jsonl(coverage_root / "reports/human_review_packet.jsonl", packet)
    decisions = [
        {**row, "verdict": "usable", "reviewer": "fixture-reviewer"}
        for row in decision_template(packet)
    ]
    return split_root, coverage_root, decisions


def test_split_tokenizer_accounting_is_exact_for_all_roles_and_splits() -> None:
    documents = _documents()
    split = exact_heldout_split(documents, heldout_documents=16)
    compatibility, reports = split_tokenizer_accounting(
        documents,
        train_ids=set(split["train_document_ids"]),
        heldout_ids=set(split["heldout_document_ids"]),
        tokenizers=[_Adapter("olmo", 1), _Adapter("qwen", 2), _Adapter("smollm", 3)],
    )
    assert set(compatibility) == {"olmo", "qwen", "smollm"}
    assert all(row["status"] == "TOKENIZER_COMPATIBILITY_PASS" for row in compatibility.values())
    assert all(reports[role]["train"]["document_count"] == 112 for role in reports)
    assert all(reports[role]["heldout"]["document_count"] == 16 for role in reports)
    assert all(reports[role][split_name]["status"] == "ACCOUNTING_COMPLETE" for role in reports for split_name in ("train", "heldout"))


def test_phase2_writes_compact_evidence_and_stops_before_training(tmp_path: Path) -> None:
    documents = _documents()
    split_root, coverage_root, decisions = _predecessors(tmp_path, documents)

    def loader(*_args, execution_enabled: bool = False, **_kwargs):
        assert execution_enabled
        # Production binds the exact byte total; the fixture substitutes text while preserving
        # the operator path through a narrow monkeypatch below.
        return documents

    expected_bytes = sum(len(row.text.encode("utf-8")) for row in documents)
    output = tmp_path / "phase2"
    result = run_oscar_phase2_evidence(
        tmp_path / "source",
        split_root,
        coverage_root,
        output,
        [],
        decisions=decisions,
        tokenizers=[_Adapter("olmo", 1), _Adapter("qwen", 2), _Adapter("smollm", 3)],
        expected_document_count=len(documents),
        expected_utf8_bytes=expected_bytes,
        execution_enabled=True,
        document_loader=loader,
    )
    assert result["status"] == "D0_EVIDENCE_COMPLETE"
    assert result["ready_to_train"] is False
    assert result["final_audit"]["artifact_count"] == 12
    assert result["final_audit"]["model_weight_access"] is False
    assert (output / "reports/tokenizer_accounting_olmo_train.json").is_file()
    assert not (output / "splits").exists()


def test_phase2_does_not_load_tokenizers_before_population_validation(tmp_path: Path) -> None:
    documents = _documents()
    split_root, coverage_root, decisions = _predecessors(tmp_path, documents)
    loaded = False

    def tokenizers():
        nonlocal loaded
        loaded = True
        return [_Adapter("olmo", 1), _Adapter("qwen", 2), _Adapter("smollm", 3)]

    with pytest.raises(ValueError, match="byte total"):
        run_oscar_phase2_evidence(
            tmp_path / "source",
            split_root,
            coverage_root,
            tmp_path / "phase2",
            [],
            decisions=decisions,
            tokenizers=tokenizers,
            expected_document_count=len(documents),
            expected_utf8_bytes=1,
            execution_enabled=True,
            document_loader=lambda *_args, **_kwargs: documents,
        )
    assert loaded is False


def test_phase2_disabled_performs_zero_writes(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="disabled"):
        run_oscar_phase2_evidence(
            tmp_path / "source",
            tmp_path / "split",
            tmp_path / "coverage",
            tmp_path / "output",
            [],
            decisions=[],
            tokenizers=[],
        )
    assert not (tmp_path / "output").exists()


def test_phase2_frozen_launcher_is_cpu_only_and_hash_bound() -> None:
    config_path = ROOT / "configs/corpora/vngrs_m2_oscar_phase2_evidence_v1.yaml"
    contract_path = ROOT / "documentation/contracts/corpora/vngrs-m2-oscar-phase2-evidence-v1.md"
    runner_path = ROOT / "scripts/corpora/run_vngrs_m2_oscar_phase2_v1.py"
    submitter_path = ROOT / "scripts/corpora/submit_vngrs_m2_oscar_phase2_v1.sh"
    slurm_path = ROOT / "slurm/m2/phase2_vngrs_m2_oscar_v1.slurm"
    operator_path = ROOT / "src/transfer_vs_relearning/corpora/vngrs/d0_phase2.py"
    bundle_path = ROOT / "src/transfer_vs_relearning/corpora/vngrs/d0_bundle.py"

    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    assert config["contract_id"] == "vngrs-m2-oscar-phase2-evidence-v1"
    assert config["status"] == "frozen_unexecuted"
    assert set(config["tokenizers"]["roles"]) == {"olmo", "qwen", "smollm"}
    assert config["output"]["root"] == "/vol/tmp2/yesildau/vngrs_m2_oscar_phase2_evidence_v1"
    assert config["output"]["maximum_success_bytes"] == 128 * 1024 * 1024
    assert config["authority"]["local_preparation"] is True
    assert all(
        value is False
        for key, value in config["authority"].items()
        if key != "local_preparation"
    )

    runner = runner_path.read_text(encoding="utf-8")
    submitter = submitter_path.read_text(encoding="utf-8")
    slurm = slurm_path.read_text(encoding="utf-8")
    combined = "\n".join((runner, submitter, slurm)).lower()
    assert "automodel" not in combined
    assert "train_clm" not in combined
    assert "requests." not in combined
    assert "http://" not in combined and "https://" not in combined
    assert "#SBATCH --gres" not in slurm
    assert "TRANSFORMERS_OFFLINE=1" in slurm
    assert "--test-only" in submitter

    contract = contract_path.read_text(encoding="utf-8")
    bindings = {
        "config": config_path,
        "operator": operator_path,
        "bundle": bundle_path,
        "runner": runner_path,
        "submitter": submitter_path,
        "Slurm": slurm_path,
    }
    for label, path in bindings.items():
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert label in contract and digest in contract
