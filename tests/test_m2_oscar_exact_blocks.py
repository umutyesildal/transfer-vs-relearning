from __future__ import annotations

from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/corpora/vngrs_m2_oscar_exact_blocks_v1.yaml"
RUNNER = ROOT / "scripts/m2/materialize_three_model_oscar_m2_blocks.py"


def test_exact_block_contract_freezes_three_models_and_matched_budget() -> None:
    source = CONFIG.read_text(encoding="utf-8")
    for exact_line in (
        "status: frozen_unexecuted",
        "execution_authorized: false",
        "roles: [olmo, qwen, smollm]",
        "train_blocks: 97536",
        "train_tokens_per_arm: 49938432",
        "replacement_blocks: 976",
        "expected_unique_facts: 250",
        "branch_a_exposures: 0",
        "training: false",
        "automatic_retry: false",
    ):
        assert exact_line in source


def test_exact_block_runner_is_disabled_without_explicit_execution_flag() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert 'parser.add_argument("--execution-enabled", action="store_true")' in source
    assert "if not args.execution_enabled:" in source
    assert "Exact block materialization remains execution-disabled" in source


def test_exact_block_launchers_are_syntax_valid_and_cpu_only() -> None:
    slurm = ROOT / "slurm/m2/materialize_three_model_oscar_m2_blocks.slurm"
    submit = ROOT / "scripts/m2/submit_three_model_oscar_m2_blocks.sh"
    subprocess.run(["bash", "-n", str(slurm)], check=True)
    subprocess.run(["bash", "-n", str(submit)], check=True)
    source = slurm.read_text(encoding="utf-8")
    assert "--partition=std" in source
    assert "--gres=gpu" not in source
    assert "--execution-enabled" in source
    assert "HF_HUB_OFFLINE=1" in source
