#!/usr/bin/env python3
"""Bounded two-role Codex CLI orchestrator for the thesis workspace."""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import fcntl
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from typing import Any, Iterator


AGENT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = AGENT_DIR / "config.json"
STATE_DIR = AGENT_DIR / "state"
RUNS_DIR = AGENT_DIR / "runs"
STOP_PATH = AGENT_DIR / "STOP"
LOCK_PATH = STATE_DIR / "orchestrator.lock"
SESSIONS_PATH = STATE_DIR / "sessions.json"
RUNTIME_PATH = STATE_DIR / "runtime.json"
DECISION_PATH = STATE_DIR / "decision.json"
REPORT_PATH = STATE_DIR / "worker-report.json"
HISTORY_PATH = STATE_DIR / "history.jsonl"
UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)

DECISION_KEYS = {
    "goal_id",
    "status",
    "task_id",
    "task",
    "reason",
    "scope_class",
    "requires_user_authorization",
    "authorization_request",
    "allowed_paths",
    "forbidden_actions",
    "acceptance_criteria",
    "required_evidence",
}
DECISION_STATUSES = {"continue", "rework", "done", "blocked", "awaiting_authorization"}
SCOPE_CLASSES = {
    "local_read_only",
    "local_write",
    "external_read_only",
    "external_write",
    "destructive",
}
REPORT_KEYS = {
    "goal_id",
    "status",
    "task_id",
    "summary",
    "files_changed",
    "commands_run",
    "tests",
    "acceptance_criteria_results",
    "issues",
    "review_notes",
}
CODEX_UNSUPPORTED_SCHEMA_KEYS = {
    "uniqueItems",
    "minLength",
    "maxLength",
    "pattern",
    "minimum",
    "maximum",
}


class OrchestratorError(RuntimeError):
    """Fail-closed orchestrator error."""


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise OrchestratorError(f"Missing required file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise OrchestratorError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise OrchestratorError(f"Expected a JSON object in {path}")
    return value


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    with temporary.open("w", encoding="utf-8") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def atomic_write_json(path: Path, value: Any) -> None:
    atomic_write_text(path, json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def append_history(value: dict[str, Any]) -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with HISTORY_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def load_config() -> tuple[dict[str, Any], Path]:
    config = read_json(CONFIG_PATH)
    workspace = (AGENT_DIR / str(config.get("workspace_root", ".."))).resolve()
    if workspace == Path("/") or not workspace.is_dir():
        raise OrchestratorError(f"Unsafe or missing workspace root: {workspace}")
    if not (workspace / "AGENTS.md").is_file():
        raise OrchestratorError(f"Workspace AGENTS.md is missing: {workspace / 'AGENTS.md'}")
    return config, workspace


def find_unsupported_schema_keys(value: Any, location: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_location = f"{location}.{key}"
            if key in CODEX_UNSUPPORTED_SCHEMA_KEYS:
                findings.append(child_location)
            findings.extend(find_unsupported_schema_keys(child, child_location))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(find_unsupported_schema_keys(child, f"{location}[{index}]"))
    return findings


def run_command(
    args: list[str],
    *,
    cwd: Path,
    timeout: int,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            args,
            cwd=cwd,
            input=input_text,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise OrchestratorError(f"Command timed out after {timeout}s: {args[0]}") from exc
    except OSError as exc:
        raise OrchestratorError(f"Could not execute {args[0]}: {exc}") from exc


@contextlib.contextmanager
def orchestrator_lock() -> Iterator[None]:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with LOCK_PATH.open("a+", encoding="utf-8") as handle:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise OrchestratorError("Another orchestrator process already holds the lock") from exc
        handle.seek(0)
        handle.truncate()
        handle.write(f"pid={os.getpid()} started_at={utc_now()}\n")
        handle.flush()
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def set_runtime(status: str, round_number: int, message: str, **extra: Any) -> None:
    payload: dict[str, Any] = {
        "status": status,
        "round": round_number,
        "message": message,
        "updated_at": utc_now(),
    }
    payload.update(extra)
    atomic_write_json(RUNTIME_PATH, payload)


def doctor(*, quiet: bool = False) -> tuple[list[str], list[str]]:
    config, workspace = load_config()
    errors: list[str] = []
    warnings: list[str] = []

    required_files = [
        AGENT_DIR / "GOAL.md",
        AGENT_DIR / "POLICY.md",
        AGENT_DIR / "prompts" / "sol-turn.md",
        AGENT_DIR / "prompts" / "luna-turn.md",
        AGENT_DIR / "schemas" / "decision.schema.json",
        AGENT_DIR / "schemas" / "worker-report.schema.json",
        SESSIONS_PATH,
    ]
    for path in required_files:
        if not path.is_file():
            errors.append(f"missing file: {path}")

    for relative in config.get("required_read_files", []):
        path = (workspace / relative).resolve()
        try:
            path.relative_to(workspace)
        except ValueError:
            errors.append(f"required read file escapes workspace: {relative}")
            continue
        if not path.is_file():
            errors.append(f"missing required read file: {path}")

    for schema_path in required_files[-3:-1]:
        if schema_path.is_file():
            try:
                schema = read_json(schema_path)
                unsupported = find_unsupported_schema_keys(schema)
                if unsupported:
                    errors.append(
                        f"Codex-incompatible schema keywords in {schema_path}: {', '.join(unsupported)}"
                    )
            except OrchestratorError as exc:
                errors.append(str(exc))

    codex_bin = str(config.get("codex_bin", "codex"))
    if shutil.which(codex_bin) is None:
        errors.append(f"Codex CLI not found on PATH: {codex_bin}")
    else:
        version = run_command([codex_bin, "--version"], cwd=workspace, timeout=30)
        if version.returncode != 0:
            errors.append(f"codex --version failed: {version.stderr.strip()}")
        exec_help = run_command([codex_bin, "exec", "--help"], cwd=workspace, timeout=30)
        resume_help = run_command([codex_bin, "exec", "resume", "--help"], cwd=workspace, timeout=30)
        combined_help = exec_help.stdout + resume_help.stdout
        for feature in ("--output-schema", "--json", "--output-last-message", "--sandbox"):
            if feature not in combined_help:
                errors.append(f"Installed Codex CLI does not advertise required option {feature}")

    for relative in config.get("repositories", []):
        repo = (workspace / relative).resolve()
        if not repo.is_dir() or not (repo / ".git").exists():
            errors.append(f"Configured Git repository is missing: {repo}")
            continue
        status = run_command(
            ["git", "-C", str(repo), "status", "--porcelain=v1", "--branch"],
            cwd=workspace,
            timeout=30,
        )
        if status.returncode != 0:
            errors.append(f"Git status failed for {relative}: {status.stderr.strip()}")

    goal = (AGENT_DIR / "GOAL.md").read_text(encoding="utf-8") if (AGENT_DIR / "GOAL.md").exists() else ""
    if "Status: NOT_SET" in goal:
        warnings.append("GOAL.md is still the non-authorizing template")

    sessions = read_json(SESSIONS_PATH) if SESSIONS_PATH.is_file() else {}
    for role in ("sol", "luna"):
        value = str(sessions.get(f"{role}_session_id", ""))
        if not UUID_RE.match(value):
            warnings.append(f"{role} session is not initialized")

    if not quiet:
        print(f"Workspace: {workspace}")
        if errors:
            for item in errors:
                print(f"ERROR: {item}")
        else:
            print("Core checks: PASS")
        for item in warnings:
            print(f"WARN: {item}")
    return errors, warnings


def extract_thread_id(jsonl_text: str) -> str:
    candidate_keys = {"thread_id", "threadId", "session_id", "sessionId"}

    def walk(value: Any) -> str | None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key in candidate_keys and isinstance(child, str) and UUID_RE.match(child):
                    return child
            for child in value.values():
                found = walk(child)
                if found:
                    return found
        elif isinstance(value, list):
            for child in value:
                found = walk(child)
                if found:
                    return found
        return None

    for line in jsonl_text.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        found = walk(event)
        if found:
            return found
    raise OrchestratorError("Codex JSONL did not contain a session/thread UUID")


def bootstrap(*, confirmed: bool) -> int:
    if not confirmed:
        raise OrchestratorError("bootstrap creates two Codex sessions; rerun with --yes")
    config, workspace = load_config()
    errors, _ = doctor(quiet=True)
    if errors:
        raise OrchestratorError("Doctor checks failed; run the doctor command for details")

    sessions = read_json(SESSIONS_PATH)
    codex_bin = str(config["codex_bin"])
    timeout = int(config["limits"]["turn_timeout_seconds"])
    for role in ("sol", "luna"):
        key = f"{role}_session_id"
        if UUID_RE.match(str(sessions.get(key, ""))):
            print(f"{role}: existing session {sessions[key]} preserved")
            continue
        label = str(config["session_labels"][role])
        prompt = (
            f"Initialize a persistent Codex CLI role named {label}. Read {workspace / 'AGENTS.md'} "
            "and acknowledge the role without editing any file, running remote commands, or "
            "performing project work. The repository files, not session memory, are the source "
            "of truth. Reply with a brief role-ready acknowledgement."
        )
        args = [
            codex_bin,
            "exec",
            "-C",
            str(workspace),
            "--skip-git-repo-check",
            "-m",
            str(config["models"][role]),
            "-s",
            "read-only",
            "--json",
            "-",
        ]
        result = run_command(args, cwd=workspace, timeout=timeout, input_text=prompt)
        atomic_write_text(STATE_DIR / f"bootstrap-{role}.events.jsonl", result.stdout)
        atomic_write_text(STATE_DIR / f"bootstrap-{role}.stderr.log", result.stderr)
        if result.returncode != 0:
            raise OrchestratorError(f"{role} bootstrap failed with exit {result.returncode}")
        session_id = extract_thread_id(result.stdout)
        sessions[key] = session_id
        atomic_write_json(SESSIONS_PATH, sessions)
        print(f"{role}: created {session_id} ({label})")
    set_runtime("ready", 0, "Persistent Sol and Luna sessions are initialized")
    return 0


def validate_string_list(value: Any, name: str) -> None:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise OrchestratorError(f"{name} must be an array of strings")


def validate_decision(value: dict[str, Any], expected_goal_id: str | None = None) -> None:
    if set(value) != DECISION_KEYS:
        raise OrchestratorError(
            f"Decision keys differ from schema; missing={sorted(DECISION_KEYS - set(value))}, "
            f"extra={sorted(set(value) - DECISION_KEYS)}"
        )
    if value["status"] not in DECISION_STATUSES:
        raise OrchestratorError(f"Invalid decision status: {value['status']}")
    if value["scope_class"] not in SCOPE_CLASSES:
        raise OrchestratorError(f"Invalid scope class: {value['scope_class']}")
    if not isinstance(value["requires_user_authorization"], bool):
        raise OrchestratorError("requires_user_authorization must be boolean")
    for key in ("goal_id", "task_id", "task", "reason", "authorization_request"):
        if not isinstance(value[key], str):
            raise OrchestratorError(f"{key} must be a string")
    if not value["goal_id"].strip() or not value["task_id"].strip() or not value["reason"].strip():
        raise OrchestratorError("goal_id, task_id, and reason must not be empty")
    if expected_goal_id is not None and value["goal_id"] != expected_goal_id:
        raise OrchestratorError("Decision goal_id does not match the active GOAL.md")
    for key in ("allowed_paths", "forbidden_actions", "acceptance_criteria", "required_evidence"):
        validate_string_list(value[key], key)
    if value["status"] in {"continue", "rework"} and not value["task"].strip():
        raise OrchestratorError("A dispatchable decision must contain a task")
    if value["scope_class"] == "local_write" and not value["allowed_paths"]:
        raise OrchestratorError("local_write requires at least one allowed path")
    if value["status"] == "awaiting_authorization" and not value["authorization_request"].strip():
        raise OrchestratorError("awaiting_authorization requires an authorization_request")


def validate_report(value: dict[str, Any], task_id: str, goal_id: str | None = None) -> None:
    if set(value) != REPORT_KEYS:
        raise OrchestratorError(
            f"Worker report keys differ from schema; missing={sorted(REPORT_KEYS - set(value))}, "
            f"extra={sorted(set(value) - REPORT_KEYS)}"
        )
    if value["status"] not in {"completed", "partial", "blocked"}:
        raise OrchestratorError(f"Invalid worker status: {value['status']}")
    if value["task_id"] != task_id:
        raise OrchestratorError("Worker report task_id does not match the decision")
    if goal_id is not None and value["goal_id"] != goal_id:
        raise OrchestratorError("Worker report goal_id does not match the active GOAL.md")
    if not isinstance(value["summary"], str) or not value["summary"].strip():
        raise OrchestratorError("Worker report summary must not be empty")
    for key in ("files_changed", "issues", "review_notes"):
        validate_string_list(value[key], key)
    if not isinstance(value["commands_run"], list) or not isinstance(value["tests"], list):
        raise OrchestratorError("commands_run and tests must be arrays")
    if not isinstance(value["acceptance_criteria_results"], list):
        raise OrchestratorError("acceptance_criteria_results must be an array")


def decision_is_dispatchable(decision: dict[str, Any], config: dict[str, Any]) -> bool:
    return (
        decision["status"] in {"continue", "rework"}
        and not decision["requires_user_authorization"]
        and decision["scope_class"] in set(config["auto_allowed_scope_classes"])
    )


def render_prompt(path: Path, *, workspace: Path, round_number: int, goal_id: str) -> str:
    text = path.read_text(encoding="utf-8")
    return (
        text.replace("{{WORKSPACE_ROOT}}", str(workspace))
        .replace("{{AGENT_DIR}}", str(AGENT_DIR))
        .replace("{{ROUND}}", str(round_number))
        .replace("{{GOAL_ID}}", goal_id)
    )


def call_role(
    *,
    role: str,
    session_id: str,
    sandbox: str,
    schema_path: Path,
    prompt_path: Path,
    round_dir: Path,
    config: dict[str, Any],
    workspace: Path,
    round_number: int,
    goal_id: str,
) -> dict[str, Any]:
    output_path = round_dir / f"{role}-final.json"
    args = [
        str(config["codex_bin"]),
        "exec",
        "-C",
        str(workspace),
        "--skip-git-repo-check",
        "-m",
        str(config["models"][role]),
        "-s",
        sandbox,
        "--json",
        "--output-schema",
        str(schema_path),
        "-o",
        str(output_path),
        "resume",
        session_id,
        "-",
    ]
    prompt = render_prompt(
        prompt_path,
        workspace=workspace,
        round_number=round_number,
        goal_id=goal_id,
    )
    result = run_command(
        args,
        cwd=workspace,
        timeout=int(config["limits"]["turn_timeout_seconds"]),
        input_text=prompt,
    )
    atomic_write_text(round_dir / f"{role}-events.jsonl", result.stdout)
    atomic_write_text(round_dir / f"{role}-stderr.log", result.stderr)
    atomic_write_json(round_dir / f"{role}-invocation.json", {"args": args, "returncode": result.returncode})
    if result.returncode != 0:
        raise OrchestratorError(f"{role} exited with code {result.returncode}")
    return read_json(output_path)


def file_fingerprint(path: Path, max_hash_bytes: int) -> str:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return "missing"
    if path.is_symlink():
        return f"symlink:{os.readlink(path)}"
    if path.is_dir():
        return "directory"
    if not path.is_file():
        return f"special:{info.st_mode}:{info.st_size}:{info.st_mtime_ns}"
    if info.st_size > max_hash_bytes:
        return f"large:{info.st_size}:{info.st_mtime_ns}"
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}:{info.st_size}"


def parse_porcelain_z(data: str) -> dict[str, str]:
    tokens = data.split("\0")
    paths: dict[str, str] = {}
    index = 0
    while index < len(tokens):
        entry = tokens[index]
        index += 1
        if not entry:
            continue
        if len(entry) < 4:
            continue
        status = entry[:2]
        paths[entry[3:]] = status
        if "R" in status or "C" in status:
            if index < len(tokens) and tokens[index]:
                paths[tokens[index]] = f"{status}:source"
                index += 1
    return paths


def capture_snapshot(config: dict[str, Any], workspace: Path) -> dict[str, str]:
    snapshot: dict[str, str] = {}
    max_bytes = int(config["limits"]["max_file_hash_bytes"])

    for relative in config["repositories"]:
        repo = (workspace / relative).resolve()
        normalized = Path(relative).as_posix().rstrip("/")
        is_workspace_repo = normalized in {"", "."}
        head_key = "git::HEAD" if is_workspace_repo else f"{normalized}::HEAD"
        path_prefix = "" if is_workspace_repo else f"{normalized}/"
        head = run_command(["git", "-C", str(repo), "rev-parse", "HEAD"], cwd=workspace, timeout=30)
        if head.returncode != 0:
            raise OrchestratorError(f"Could not read HEAD for {relative}")
        snapshot[head_key] = head.stdout.strip()
        status = run_command(
            ["git", "-C", str(repo), "status", "--porcelain=v1", "-z", "--untracked-files=all"],
            cwd=workspace,
            timeout=60,
        )
        if status.returncode != 0:
            raise OrchestratorError(f"Could not inspect status for {relative}")
        for repo_path, repo_status in parse_porcelain_z(status.stdout).items():
            fingerprint = file_fingerprint(repo / repo_path, max_bytes)
            snapshot[f"{path_prefix}{repo_path}"] = f"status:{repo_status}|{fingerprint}"

    for relative in config["root_watch_paths"]:
        target = (workspace / relative).resolve()
        try:
            target.relative_to(workspace)
        except ValueError as exc:
            raise OrchestratorError(f"Root watch path escapes workspace: {relative}") from exc
        if not target.exists() and not target.is_symlink():
            snapshot[relative] = "missing"
            continue
        if target.is_file() or target.is_symlink():
            snapshot[relative] = file_fingerprint(target, max_bytes)
            continue
        for path in sorted(target.rglob("*")):
            if ".git" in path.parts or path.is_dir():
                continue
            rel_path = path.relative_to(workspace).as_posix()
            snapshot[rel_path] = file_fingerprint(path, max_bytes)
    return snapshot


def changed_paths(before: dict[str, str], after: dict[str, str]) -> list[str]:
    return sorted(key for key in set(before) | set(after) if before.get(key) != after.get(key))


def normalize_allowed_path(pattern: str, workspace: Path) -> str:
    candidate = Path(pattern)
    if candidate.is_absolute():
        try:
            return candidate.resolve().relative_to(workspace).as_posix()
        except ValueError as exc:
            raise OrchestratorError(f"Allowed path escapes workspace: {pattern}") from exc
    normalized = Path(os.path.normpath(pattern)).as_posix()
    if normalized == ".." or normalized.startswith("../"):
        raise OrchestratorError(f"Allowed path escapes workspace: {pattern}")
    return normalized


def path_is_allowed(path: str, patterns: list[str], workspace: Path) -> bool:
    if path.endswith("::HEAD"):
        return False
    for raw_pattern in patterns:
        pattern = normalize_allowed_path(raw_pattern, workspace)
        if fnmatch.fnmatchcase(path, pattern):
            return True
        if pattern.endswith("/**") and path.startswith(pattern[:-3].rstrip("/") + "/"):
            return True
        if path == pattern.rstrip("/"):
            return True
    return False


def decision_fingerprint(decision: dict[str, Any]) -> str:
    stable = {
        "goal_id": decision["goal_id"],
        "status": decision["status"],
        "task_id": decision["task_id"],
        "task": decision["task"],
        "reason": decision["reason"],
        "acceptance_criteria": decision["acceptance_criteria"],
    }
    return hashlib.sha256(json.dumps(stable, sort_keys=True).encode("utf-8")).hexdigest()


def parse_goal_id(goal_text: str) -> str:
    match = re.search(r"(?m)^Goal ID:\s*(\S+)\s*$", goal_text)
    if not match or match.group(1) == "NOT_SET":
        raise OrchestratorError("GOAL.md must define a non-template Goal ID")
    return match.group(1)


def ensure_ready() -> tuple[dict[str, Any], Path, dict[str, Any], str]:
    errors, _ = doctor(quiet=True)
    if errors:
        raise OrchestratorError("Doctor checks failed; run doctor for details")
    config, workspace = load_config()
    goal = (AGENT_DIR / "GOAL.md").read_text(encoding="utf-8")
    if "Status: NOT_SET" in goal or "Status: ACTIVE" not in goal:
        raise OrchestratorError("GOAL.md must contain Status: ACTIVE and a concrete bounded goal")
    goal_id = parse_goal_id(goal)
    sessions = read_json(SESSIONS_PATH)
    for role in ("sol", "luna"):
        if not UUID_RE.match(str(sessions.get(f"{role}_session_id", ""))):
            raise OrchestratorError(f"{role} session is not initialized; run bootstrap")
    return config, workspace, sessions, goal_id


def print_dry_run(config: dict[str, Any], workspace: Path, sessions: dict[str, Any] | None) -> None:
    print("Dry run only; no Codex session will be called.")
    print(f"Workspace: {workspace}")
    print(f"Repositories: {', '.join(config['repositories'])}")
    print(f"Automatic scopes: {', '.join(config['auto_allowed_scope_classes'])}")
    print(f"Maximum rounds: {config['limits']['max_rounds']}")
    if sessions:
        print(f"Sol session: {sessions.get('sol_session_id') or '<not initialized>'}")
        print(f"Luna session: {sessions.get('luna_session_id') or '<not initialized>'}")
    print("Flow: Sol(read-only) -> validated decision -> Luna(bounded) -> scope audit -> Sol")


def run_loop(*, dry_run: bool) -> int:
    if dry_run:
        config, workspace = load_config()
        sessions = read_json(SESSIONS_PATH)
        print_dry_run(config, workspace, sessions)
        return 0

    config, workspace, sessions, goal_id = ensure_ready()
    limits = config["limits"]
    started = time.monotonic()
    decision_fingerprints: list[str] = []
    rework_counts: dict[str, int] = {}
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    run_stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    with orchestrator_lock():
        set_runtime("running", 0, "Orchestrator loop started", run_stamp=run_stamp)
        for round_number in range(1, int(limits["max_rounds"]) + 1):
            if STOP_PATH.exists():
                set_runtime("stopped", round_number - 1, "STOP marker detected", run_stamp=run_stamp)
                print("STOP marker detected; loop ended before the next role turn.")
                return 2
            if time.monotonic() - started > int(limits["run_wall_clock_seconds"]):
                set_runtime("blocked", round_number - 1, "Wall-clock limit reached", run_stamp=run_stamp)
                print("Wall-clock limit reached; human review required.")
                return 3

            round_dir = RUNS_DIR / f"{run_stamp}-round-{round_number:03d}"
            round_dir.mkdir(parents=True, exist_ok=False)
            before = capture_snapshot(config, workspace)
            atomic_write_json(round_dir / "snapshot-before.json", before)

            decision = call_role(
                role="sol",
                session_id=str(sessions["sol_session_id"]),
                sandbox="read-only",
                schema_path=AGENT_DIR / "schemas" / "decision.schema.json",
                prompt_path=AGENT_DIR / "prompts" / "sol-turn.md",
                round_dir=round_dir,
                config=config,
                workspace=workspace,
                round_number=round_number,
                goal_id=goal_id,
            )
            validate_decision(decision, goal_id)
            atomic_write_json(DECISION_PATH, decision)
            atomic_write_json(round_dir / "decision.json", decision)
            append_history({"at": utc_now(), "round": round_number, "type": "decision", "value": decision})

            if decision["status"] == "done":
                set_runtime("done", round_number, decision["reason"], run_stamp=run_stamp)
                print(f"DONE: {decision['reason']}")
                return 0
            if decision["status"] in {"blocked", "awaiting_authorization"}:
                set_runtime(decision["status"], round_number, decision["reason"], run_stamp=run_stamp)
                print(f"{decision['status'].upper()}: {decision['reason']}")
                if decision["authorization_request"]:
                    print(decision["authorization_request"])
                return 2
            if not decision_is_dispatchable(decision, config):
                message = "Decision is outside V1 automatic scope; explicit human authorization is required"
                set_runtime("awaiting_authorization", round_number, message, run_stamp=run_stamp)
                print(message)
                return 2

            fingerprint = decision_fingerprint(decision)
            decision_fingerprints.append(fingerprint)
            same_limit = int(limits["same_decision_max"])
            if len(decision_fingerprints) >= same_limit and len(set(decision_fingerprints[-same_limit:])) == 1:
                message = f"The same decision repeated {same_limit} times"
                set_runtime("blocked", round_number, message, run_stamp=run_stamp)
                print(message)
                return 3
            if decision["status"] == "rework":
                task_id = str(decision["task_id"])
                rework_counts[task_id] = rework_counts.get(task_id, 0) + 1
                if rework_counts[task_id] > int(limits["max_rework_per_task"]):
                    message = f"Rework limit exceeded for task {task_id}"
                    set_runtime("blocked", round_number, message, run_stamp=run_stamp)
                    print(message)
                    return 3

            sandbox = "read-only" if decision["scope_class"] == "local_read_only" else "workspace-write"
            report = call_role(
                role="luna",
                session_id=str(sessions["luna_session_id"]),
                sandbox=sandbox,
                schema_path=AGENT_DIR / "schemas" / "worker-report.schema.json",
                prompt_path=AGENT_DIR / "prompts" / "luna-turn.md",
                round_dir=round_dir,
                config=config,
                workspace=workspace,
                round_number=round_number,
                goal_id=goal_id,
            )
            validate_report(report, str(decision["task_id"]), goal_id)
            atomic_write_json(REPORT_PATH, report)
            atomic_write_json(round_dir / "worker-report.json", report)

            after = capture_snapshot(config, workspace)
            atomic_write_json(round_dir / "snapshot-after.json", after)
            touched = changed_paths(before, after)
            unexpected = [
                path for path in touched if not path_is_allowed(path, decision["allowed_paths"], workspace)
            ]
            scope_check = {"changed_paths": touched, "unexpected_paths": unexpected}
            atomic_write_json(round_dir / "scope-check.json", scope_check)
            append_history(
                {
                    "at": utc_now(),
                    "round": round_number,
                    "type": "worker_report",
                    "value": report,
                    "scope_check": scope_check,
                }
            )
            if unexpected:
                message = "Unexpected changed paths detected; no automatic revert was attempted"
                set_runtime(
                    "blocked",
                    round_number,
                    message,
                    run_stamp=run_stamp,
                    unexpected_paths=unexpected,
                )
                print(message)
                for path in unexpected:
                    print(f"  - {path}")
                return 3
            if report["status"] == "blocked":
                message = f"Worker blocked: {report['summary']}"
                set_runtime("blocked", round_number, message, run_stamp=run_stamp)
                print(message)
                return 2

            print(f"Round {round_number}: {report['status']} — {report['summary']}")

        message = f"Maximum round count reached ({limits['max_rounds']})"
        set_runtime("blocked", int(limits["max_rounds"]), message, run_stamp=run_stamp)
        print(message)
        return 3


def show_status() -> int:
    config, workspace = load_config()
    runtime = read_json(RUNTIME_PATH)
    sessions = read_json(SESSIONS_PATH)
    print(json.dumps({"workspace": str(workspace), "runtime": runtime, "sessions": sessions}, indent=2))
    print(f"Configured repositories: {', '.join(config['repositories'])}")
    print(f"STOP marker: {'present' if STOP_PATH.exists() else 'absent'}")
    return 0


def create_stop() -> int:
    atomic_write_text(STOP_PATH, f"requested_at={utc_now()}\n")
    print(f"STOP marker created: {STOP_PATH}")
    return 0


def clear_stop() -> int:
    if STOP_PATH.exists():
        STOP_PATH.unlink()
        print(f"STOP marker removed: {STOP_PATH}")
    else:
        print("STOP marker was already absent")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("doctor", help="Validate local prerequisites without model calls")
    bootstrap_parser = subparsers.add_parser("bootstrap", help="Create persistent Sol/Luna sessions")
    bootstrap_parser.add_argument("--yes", action="store_true", help="Confirm two session-creating calls")
    run_parser = subparsers.add_parser("run", help="Run the bounded Sol/Luna loop")
    run_parser.add_argument("--dry-run", action="store_true", help="Show the local plan without model calls")
    subparsers.add_parser("status", help="Show persisted orchestrator state")
    subparsers.add_parser("stop", help="Create the cooperative STOP marker")
    subparsers.add_parser("clear-stop", help="Remove the cooperative STOP marker")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "doctor":
            errors, _ = doctor()
            return 1 if errors else 0
        if args.command == "bootstrap":
            with orchestrator_lock():
                return bootstrap(confirmed=args.yes)
        if args.command == "run":
            return run_loop(dry_run=args.dry_run)
        if args.command == "status":
            return show_status()
        if args.command == "stop":
            return create_stop()
        if args.command == "clear-stop":
            return clear_stop()
        raise OrchestratorError(f"Unknown command: {args.command}")
    except OrchestratorError as exc:
        if args.command == "run" and not getattr(args, "dry_run", False):
            try:
                previous_round = int(read_json(RUNTIME_PATH).get("round", 0))
                set_runtime("error", previous_round, str(exc))
            except (OrchestratorError, OSError, ValueError):
                pass
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
