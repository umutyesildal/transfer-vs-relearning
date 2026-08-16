from __future__ import annotations

import pytest

from scripts.operations import select_clean_a6000_uuid
from scripts.operations.select_clean_a6000_uuid import choose_clean_uuid, validate_visible_binding


def gpu(uuid: str, *, free_gib: int = 47, used_mib: int = 100) -> dict[str, object]:
    return {
        "index": int(uuid[-1]),
        "uuid": uuid,
        "name": "NVIDIA RTX A6000",
        "total_bytes": 48 * 1024**3,
        "free_bytes": free_gib * 1024**3,
        "used_bytes": used_mib * 1024**2,
    }


def test_clean_uuid_selection_is_lexicographic_not_visibility_or_memory_rank() -> None:
    rows = [gpu("GPU-d3"), gpu("GPU-a0", free_gib=41), gpu("GPU-c2"), gpu("GPU-b1")]
    selected, audited = choose_clean_uuid(rows, {str(row["uuid"]): [] for row in rows})
    assert selected == "GPU-a0"
    assert len(audited) == 4


def test_dirty_or_low_memory_devices_are_excluded() -> None:
    rows = [gpu("GPU-a0"), gpu("GPU-b1", free_gib=39), gpu("GPU-c2", used_mib=600), gpu("GPU-d3")]
    apps = {str(row["uuid"]): [] for row in rows}
    apps["GPU-a0"] = ["123, python, 100"]
    selected, audited = choose_clean_uuid(rows, apps)
    assert selected == "GPU-d3"
    assert [row["uuid"] for row in audited if row["clean_candidate"]] == ["GPU-d3"]


def test_no_clean_uuid_fails_closed() -> None:
    rows = [gpu(f"GPU-{letter}{index}", free_gib=39) for index, letter in enumerate("abcd")]
    with pytest.raises(ValueError, match="No clean RTX A6000"):
        choose_clean_uuid(rows, {str(row["uuid"]): [] for row in rows})


def test_visible_binding_accepts_exact_indices_or_uuids_only() -> None:
    rows = [gpu(f"GPU-{letter}{index}") for index, letter in enumerate("abcd")]
    assert validate_visible_binding("0,1,2,3", rows) == ["0", "1", "2", "3"]
    assert validate_visible_binding("GPU-a0,GPU-b1,GPU-c2,GPU-d3", rows)[0] == "GPU-a0"
    with pytest.raises(ValueError, match="four-device"):
        validate_visible_binding("0", rows)
    with pytest.raises(ValueError, match="does not match"):
        validate_visible_binding("4,5,6,7", rows)


def test_no_candidate_cli_persists_full_failure_audit(tmp_path, monkeypatch) -> None:
    rows = [gpu(f"GPU-{letter}{index}", free_gib=39) for index, letter in enumerate("abcd")]
    gpu_payload = "\n".join(
        f'{row["index"]}, {row["uuid"]}, {row["name"]}, 49152, 39936, 9216'
        for row in rows
    )

    def fake_run(command: list[str]) -> str:
        return gpu_payload if "--query-gpu=" in " ".join(command) else ""

    output = tmp_path / "audit.json"
    monkeypatch.setattr(select_clean_a6000_uuid, "_run", fake_run)
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "0,1,2,3")
    monkeypatch.setattr(
        "sys.argv", ["select_clean_a6000_uuid.py", "--output", str(output), "--contract-sha256", "abc"]
    )
    with pytest.raises(ValueError, match="No clean RTX A6000"):
        select_clean_a6000_uuid.main()
    payload = __import__("json").loads(output.read_text(encoding="utf-8"))
    assert payload["status"] == "BLOCKED_NO_CLEAN_CANDIDATE"
    assert payload["selected_uuid"] is None
    assert len(payload["gpus"]) == 4
    assert all(row["rejection_reasons"] for row in payload["gpus"])
