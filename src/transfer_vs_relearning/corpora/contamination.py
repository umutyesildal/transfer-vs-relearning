from __future__ import annotations

import json
import re
import unicodedata
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from transfer_vs_relearning.data.constants import DATASET_FILES, RELATIONS
from transfer_vs_relearning.data.facts import expand_canonical_row
from transfer_vs_relearning.utils.io import read_csv_rows, read_jsonl


TURKISH_LOWER = str.maketrans({"I": "ı", "İ": "i"})


@dataclass(frozen=True)
class Pattern:
    pattern_id: str
    text: str
    channel: str
    rule_id: str
    source_artifact: str
    subject_id: str | None = None


def nfc(value: str) -> str:
    return unicodedata.normalize("NFC", value)


def turkish_lower(value: str) -> str:
    return nfc(value).translate(TURKISH_LOWER).lower()


def build_contamination_inventory(dataset_dir: Path) -> tuple[list[Pattern], dict[str, set[str]]]:
    canonical = read_csv_rows(dataset_dir / DATASET_FILES["canonical_profiles"])
    patterns: dict[tuple[str, str, str], Pattern] = {}
    subject_objects: dict[str, set[str]] = {}

    def add(pattern: Pattern) -> None:
        key = (pattern.text, pattern.channel, pattern.rule_id)
        if pattern.text.strip():
            patterns.setdefault(key, pattern)

    for row in canonical:
        subject = nfc(row["subject"])
        subject_id = row["subject_id"]
        add(Pattern(f"subject_exact:{subject_id}", subject, "exact_nfc_full_name", "synthetic_full_name", "canonical_subject_profiles", subject_id))
        add(Pattern(f"subject_casefold:{subject_id}", subject.casefold(), "casefold_full_name", "synthetic_full_name_casefold", "canonical_subject_profiles", subject_id))
        add(Pattern(f"subject_trlower:{subject_id}", turkish_lower(subject), "turkish_lower_full_name", "synthetic_full_name_turkish_lower", "canonical_subject_profiles", subject_id))
        add(Pattern(f"subject_id:{subject_id}", subject_id, "subject_id", "synthetic_subject_id", "canonical_subject_profiles", subject_id))
        subject_objects[subject_id] = set()
        for fact in expand_canonical_row(row):
            add(Pattern(f"fact_id:{fact.fact_id}", fact.fact_id, "fact_id", "synthetic_fact_id", "canonical_subject_profiles", subject_id))
            subject_objects[subject_id].add(nfc(fact.object_en))
            subject_objects[subject_id].add(nfc(fact.object_tr))
            add(Pattern(f"object:{subject_id}:{fact.relation}:en", nfc(fact.object_en), "canonical_object", "canonical_object_only", "canonical_subject_profiles", subject_id))
            add(Pattern(f"object:{subject_id}:{fact.relation}:tr", nfc(fact.object_tr), "canonical_object", "canonical_object_only", "canonical_subject_profiles", subject_id))

    for path_key in ("english_training", "turkish_repetition"):
        for index, row in enumerate(read_jsonl(dataset_dir / DATASET_FILES[path_key])):
            add(Pattern(f"{path_key}:{index}", nfc(row["text"]), "exact_training_sentence", "synthetic_training_sentence", path_key, row.get("subject_id")))

    for artifact in ("synthetic_v1", "canonical_subject_profiles_5000.csv", "english_training.jsonl", "turkish_repetition.jsonl"):
        add(Pattern(f"artifact:{artifact}", artifact, "dataset_artifact", "unmistakable_dataset_artifact", "dataset_manifest", None))

    return list(patterns.values()), subject_objects


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


def scan_document(document: dict[str, Any], patterns: list[Pattern], subject_objects: dict[str, set[str]], max_context_chars: int = 80) -> dict[str, Any]:
    channels = {
        "exact_nfc": nfc(document["text"]),
        "casefold": nfc(document["text"]).casefold(),
        "turkish_lower": turkish_lower(document["text"]),
    }
    usable_patterns = [
        pattern for pattern in patterns
        if (
            pattern.channel in {"subject_id", "fact_id", "exact_training_sentence", "dataset_artifact", "canonical_object"}
            or (pattern.channel == "exact_nfc_full_name")
        )
    ]
    transformed_patterns = []
    for pattern in usable_patterns:
        transformed_patterns.append(pattern)
    matcher = AhoCorasickMatcher(transformed_patterns)
    matches: list[dict[str, Any]] = []
    matched_subjects: set[str] = set()
    matched_objects: dict[str, list[str]] = {}
    for channel_name, text in channels.items():
        channel_patterns = [
            pattern for pattern in patterns
            if _pattern_applies(pattern, channel_name)
        ]
        matcher = AhoCorasickMatcher(channel_patterns)
        for start, end, pattern in matcher.finditer(text):
            if pattern.subject_id and pattern.channel != "canonical_object":
                matched_subjects.add(pattern.subject_id)
            if pattern.subject_id and pattern.channel == "canonical_object":
                matched_objects.setdefault(pattern.subject_id, []).append(pattern.text)
            decision = _decision_for(pattern)
            matches.append({
                "document_id": document["document_id"],
                "title": document["title"],
                "matched_pattern_id": pattern.pattern_id,
                "match_channel": pattern.channel,
                "rule_id": pattern.rule_id,
                "context": _snippet(document["text"], start, end, max_context_chars),
                "associated_canonical_object_matches": [],
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
                "rule_id": "synthetic_subject_object_pair",
                "context": "",
                "associated_canonical_object_matches": sorted(set(objects))[:10],
                "automatic_decision": "remove",
                "source_synthetic_artifact": "canonical_subject_profiles",
            })
    status = "contaminated" if any(match["automatic_decision"] == "remove" for match in matches) else "clean"
    return {"document_id": document["document_id"], "contamination_status": status, "matches": matches}


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
