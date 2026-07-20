from __future__ import annotations

import json
import re
import unicodedata
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from transfer_vs_relearning.data.constants import DATASET_FILES, RELATION_MAP
from transfer_vs_relearning.data.facts import expand_canonical_row
from transfer_vs_relearning.utils.io import read_csv_rows, read_jsonl, sha256_file


TURKISH_LOWER = str.maketrans({"I": "ı", "İ": "i"})


@dataclass(frozen=True)
class Pattern:
    pattern_id: str
    text: str
    channel: str
    rule_id: str
    source_artifact: str
    subject_id: str | None = None
    associated_subject_ids: tuple[str, ...] = ()


def nfc(value: str) -> str:
    return unicodedata.normalize("NFC", value)


def turkish_lower(value: str) -> str:
    return nfc(value).translate(TURKISH_LOWER).lower()


def build_contamination_inventory(dataset_dir: Path) -> tuple[list[Pattern], dict[str, set[str]]]:
    manifest = _load_dataset_manifest(dataset_dir)
    canonical_path = dataset_dir / DATASET_FILES["canonical_profiles"]
    _verify_declared_artifact(dataset_dir, canonical_path, manifest)
    canonical = read_csv_rows(canonical_path)
    if not canonical:
        raise ValueError(f"Canonical profile table is empty: {canonical_path}")
    relations = _manifest_relations(manifest, canonical[0])
    patterns: dict[tuple[str, str, str, str | None], Pattern] = {}
    subject_objects: dict[str, set[str]] = {}
    object_subjects: dict[str, set[str]] = {}

    def add(pattern: Pattern) -> None:
        key = (pattern.text, pattern.channel, pattern.rule_id, pattern.subject_id)
        if pattern.text.strip():
            patterns.setdefault(key, pattern)

    for row in canonical:
        subject = nfc(row["subject"])
        subject_id = row["subject_id"]
        if subject_id in subject_objects:
            raise ValueError(f"Duplicate canonical subject_id: {subject_id}")
        add(Pattern(f"subject_exact:{subject_id}", subject, "exact_nfc_full_name", "exact_full_synthetic_name", "canonical_subject_profiles", subject_id))
        add(Pattern(f"subject_casefold:{subject_id}", subject.casefold(), "casefold_full_name", "casefold_full_synthetic_name", "canonical_subject_profiles", subject_id))
        add(Pattern(f"subject_trlower:{subject_id}", turkish_lower(subject), "turkish_lower_full_name", "turkish_lower_full_synthetic_name", "canonical_subject_profiles", subject_id))
        add(Pattern(f"subject_id:{subject_id}", subject_id, "subject_id", "synthetic_subject_id", "canonical_subject_profiles", subject_id))
        subject_objects[subject_id] = set()
        for fact in expand_canonical_row(row, relations):
            add(Pattern(f"fact_id:{fact.fact_id}", fact.fact_id, "fact_id", "synthetic_fact_id", "canonical_subject_profiles", subject_id))
            for surface in (nfc(fact.object_en), nfc(fact.object_tr)):
                subject_objects[subject_id].add(surface)
                object_subjects.setdefault(surface, set()).add(subject_id)

    for index, surface in enumerate(sorted(object_subjects)):
        associated_subject_ids = tuple(sorted(object_subjects[surface]))
        add(Pattern(
            f"object_surface:{index}",
            surface,
            "canonical_object",
            "object_only_flag",
            "canonical_subject_profiles",
            None,
            associated_subject_ids,
        ))

    source_paths = _manifest_text_sources(dataset_dir, manifest)
    for source_path in source_paths:
        source_artifact = source_path.relative_to(dataset_dir).as_posix()
        _verify_declared_artifact(dataset_dir, source_path, manifest)
        for index, row in enumerate(read_jsonl(source_path)):
            text = row.get("text")
            if not isinstance(text, str) or not text.strip():
                raise ValueError(f"Synthetic text row has no non-empty text: {source_path}:{index + 1}")
            subject_id = row.get("subject_id")
            if subject_id is not None and subject_id not in subject_objects:
                raise ValueError(f"Synthetic text row references unknown subject_id {subject_id}: {source_path}:{index + 1}")
            relation = row.get("relation")
            if relation is not None and relation not in relations:
                raise ValueError(f"Synthetic text row references undeclared relation {relation}: {source_path}:{index + 1}")
            add(Pattern(
                f"synthetic_text:{source_artifact}:{index}",
                nfc(text),
                "exact_training_sentence",
                "exact_generated_training_sentence",
                source_artifact,
                subject_id,
            ))

    artifact_names = {
        dataset_dir.name,
        DATASET_FILES["canonical_profiles"].name,
        *(path.name for path in source_paths),
    }
    for artifact in sorted(artifact_names):
        add(Pattern(f"artifact:{artifact}", artifact, "dataset_artifact", "dataset_artifact", "dataset_manifest", None))

    return list(patterns.values()), subject_objects


def _load_dataset_manifest(dataset_dir: Path) -> dict[str, Any]:
    path = dataset_dir / "manifest.json"
    if not path.is_file():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Dataset manifest must be an object: {path}")
    return payload


def _manifest_relations(manifest: dict[str, Any], canonical_row: dict[str, str]) -> tuple[str, ...]:
    declared = manifest.get("relations")
    if declared is None and isinstance(manifest.get("relation_counts"), dict):
        declared = list(manifest["relation_counts"])
    if declared is None and isinstance(manifest.get("frequency_counts_by_relation"), dict):
        declared = list(manifest["frequency_counts_by_relation"])
    if declared is None:
        declared = [
            relation
            for relation, columns in RELATION_MAP.items()
            if all(column in canonical_row for column in columns)
        ]
    if not isinstance(declared, list) or not declared or any(not isinstance(item, str) for item in declared):
        raise ValueError("Dataset manifest must declare a non-empty string relation list")
    unknown = sorted(set(declared) - set(RELATION_MAP))
    if unknown:
        raise ValueError(f"Dataset manifest declares unknown relations: {unknown}")
    relations = tuple(relation for relation in RELATION_MAP if relation in set(declared))
    if len(relations) != len(set(declared)):
        raise ValueError(f"Dataset manifest relation list contains duplicates: {declared}")
    for relation in relations:
        missing = [column for column in RELATION_MAP[relation] if column not in canonical_row]
        if missing:
            raise ValueError(f"Canonical profile schema is missing {missing} for declared relation {relation}")
    return relations


def _manifest_text_sources(dataset_dir: Path, manifest: dict[str, Any]) -> list[Path]:
    artifacts = manifest.get("artifacts")
    if isinstance(artifacts, dict):
        legacy_sources = []
        for key in ("english_training", "turkish_repetition"):
            entry = artifacts.get(key)
            if isinstance(entry, dict) and isinstance(entry.get("path"), str):
                legacy_sources.append(dataset_dir / entry["path"])
        if legacy_sources:
            return legacy_sources

    files = manifest.get("files")
    if isinstance(files, dict):
        return [
            dataset_dir / relative
            for relative in sorted(files)
            if relative.startswith("acquisition_")
            and Path(relative).name in {"train.jsonl", "validation.jsonl"}
        ]

    return [
        dataset_dir / DATASET_FILES[key]
        for key in ("english_training", "turkish_repetition")
        if (dataset_dir / DATASET_FILES[key]).is_file()
    ]


def _verify_declared_artifact(dataset_dir: Path, path: Path, manifest: dict[str, Any]) -> None:
    if not path.is_file():
        raise ValueError(f"Declared contamination artifact is missing: {path}")
    relative = path.relative_to(dataset_dir).as_posix()
    expected = None
    files = manifest.get("files")
    if isinstance(files, dict):
        expected = files.get(relative)
    artifacts = manifest.get("artifacts")
    if expected is None and isinstance(artifacts, dict):
        for entry in artifacts.values():
            if isinstance(entry, dict) and entry.get("path") == relative:
                expected = entry.get("sha256")
                break
    if expected is not None:
        observed = sha256_file(path)
        if observed != expected:
            raise ValueError(f"Manifest SHA-256 mismatch for {path}: expected {expected}, observed {observed}")


class AhoCorasickMatcher:
    def __init__(self, patterns: list[Pattern]):
        self.patterns = patterns
        self.goto: list[dict[str, int]] = [{}]
        self.fail: list[int] = [0]
        self.out: list[list[int]] = [[]]
        for index, pattern in enumerate(patterns):
            state = 0
            for char in pattern.text:
                if char not in self.goto[state]:
                    self.goto[state][char] = self._new_state()
                state = self.goto[state][char]
            self.out[state].append(index)
        queue: deque[int] = deque()
        for state in self.goto[0].values():
            queue.append(state)
            self.fail[state] = 0
        while queue:
            state = queue.popleft()
            for char, next_state in self.goto[state].items():
                queue.append(next_state)
                fallback = self.fail[state]
                while fallback and char not in self.goto[fallback]:
                    fallback = self.fail[fallback]
                self.fail[next_state] = self.goto[fallback].get(char, 0)
                self.out[next_state].extend(self.out[self.fail[next_state]])

    def _new_state(self) -> int:
        self.goto.append({})
        self.fail.append(0)
        self.out.append([])
        return len(self.goto) - 1

    def finditer(self, text: str) -> list[tuple[int, int, Pattern]]:
        matches: list[tuple[int, int, Pattern]] = []
        state = 0
        for index, char in enumerate(text):
            while state and char not in self.goto[state]:
                state = self.fail[state]
            state = self.goto[state].get(char, 0)
            for pattern_index in self.out[state]:
                pattern = self.patterns[pattern_index]
                start = index - len(pattern.text) + 1
                end = index + 1
                if _phrase_boundary(text, start, end):
                    matches.append((start, end, pattern))
        return matches


class ContaminationScanner:
    constructions = 0

    def __init__(self, patterns: list[Pattern], subject_objects: dict[str, set[str]], max_context_chars: int = 80):
        type(self).constructions += 1
        self.subject_objects = subject_objects
        self.max_context_chars = max_context_chars
        self.matchers = {
            "exact_nfc": AhoCorasickMatcher([p for p in patterns if _pattern_applies(p, "exact_nfc")]),
            "casefold": AhoCorasickMatcher([p for p in patterns if _pattern_applies(p, "casefold")]),
            "turkish_lower": AhoCorasickMatcher([p for p in patterns if _pattern_applies(p, "turkish_lower")]),
        }
        self.pattern_counts = {channel: len(matcher.patterns) for channel, matcher in self.matchers.items()}
        self.automaton_state_counts = {channel: len(matcher.goto) for channel, matcher in self.matchers.items()}

    def scan(self, document: dict[str, Any]) -> dict[str, Any]:
        channels = {
            "exact_nfc": nfc(document["text"]),
            "casefold": nfc(document["text"]).casefold(),
            "turkish_lower": turkish_lower(document["text"]),
        }
        matches: list[dict[str, Any]] = []
        matched_subjects: set[str] = set()
        matched_objects: dict[str, list[dict[str, Any]]] = {}
        for channel_name, text in channels.items():
            for start, end, pattern in self.matchers[channel_name].finditer(text):
                associated_subject_ids = sorted(set(pattern.associated_subject_ids or ((pattern.subject_id,) if pattern.subject_id else ())))
                if pattern.subject_id and pattern.channel != "canonical_object":
                    matched_subjects.add(pattern.subject_id)
                if pattern.channel == "canonical_object":
                    for subject_id in associated_subject_ids:
                        matched_objects.setdefault(subject_id, []).append({
                            "surface": pattern.text,
                            "pattern_id": pattern.pattern_id,
                            "associated_subject_ids": associated_subject_ids,
                        })
                decision = _decision_for(pattern)
                matches.append({
                    "document_id": document["document_id"],
                    "title": document["title"],
                    "matched_pattern_id": pattern.pattern_id,
                    "match_channel": pattern.channel,
                    "rule_id": pattern.rule_id,
                    "context": _snippet(document["text"], start, end, self.max_context_chars),
                    "associated_canonical_object_matches": [],
                    "associated_subject_ids": associated_subject_ids,
                    "automatic_decision": decision,
                    "source_synthetic_artifact": pattern.source_artifact,
                })
        for subject_id in sorted(matched_subjects):
            objects = matched_objects.get(subject_id, [])
            if objects:
                matches.append({
                    "document_id": document["document_id"],
                    "title": document["title"],
                    "matched_pattern_id": f"subject_object:{subject_id}",
                    "match_channel": "subject_object_cooccurrence",
                    "rule_id": "subject_object_cooccurrence",
                    "context": "",
                    "associated_canonical_object_matches": objects[:10],
                    "associated_subject_ids": [subject_id],
                    "automatic_decision": "remove",
                    "source_synthetic_artifact": "canonical_subject_profiles",
                })
        status = "contaminated" if any(match["automatic_decision"] == "remove" for match in matches) else "flagged_only" if matches else "clean"
        return {"document_id": document["document_id"], "contamination_status": status, "matches": matches}


def scan_document(document: dict[str, Any], patterns: list[Pattern], subject_objects: dict[str, set[str]], max_context_chars: int = 80) -> dict[str, Any]:
    return ContaminationScanner(patterns, subject_objects, max_context_chars).scan(document)


def _pattern_applies(pattern: Pattern, channel_name: str) -> bool:
    return (
        channel_name == "exact_nfc" and pattern.channel in {"exact_nfc_full_name", "subject_id", "fact_id", "exact_training_sentence", "dataset_artifact", "canonical_object"}
    ) or (channel_name == "casefold" and pattern.channel == "casefold_full_name") or (
        channel_name == "turkish_lower" and pattern.channel == "turkish_lower_full_name"
    )


def _decision_for(pattern: Pattern) -> str:
    if pattern.channel == "canonical_object":
        return "flag"
    return "remove"


def _phrase_boundary(text: str, start: int, end: int) -> bool:
    before = text[start - 1] if start > 0 else " "
    after = text[end] if end < len(text) else " "
    return not before.isalnum() and not after.isalnum()


def _snippet(text: str, start: int, end: int, max_chars: int) -> str:
    half = max_chars // 2
    left = max(0, start - half)
    right = min(len(text), end + half)
    return re.sub(r"\s+", " ", text[left:right]).strip()
