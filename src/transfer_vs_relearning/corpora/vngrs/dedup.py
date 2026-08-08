"""Exact and scalable deterministic LSH/MinHash diagnostics for bounded samples."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import tempfile
from itertools import combinations
from typing import Any, Iterable, Iterator, Mapping


MASK64 = (1 << 64) - 1
MINHASH_PRIME = (1 << 61) - 1
MINHASH_INTEGER_WIDTH = 64
MINHASH_HASH_FAMILY = "sha256_feature_uint64_splitmix64_universal_mod_prime_v1"
NEAR_DEDUP_VERSION = "minhash_lsh_universal_v1"


def _splitmix64(value: int) -> int:
    value = (value + 0x9E3779B97F4A7C15) & MASK64
    value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
    value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & MASK64
    return (value ^ (value >> 31)) & MASK64


def _universal_hash_coefficients(num_perm: int, seed: int) -> tuple[tuple[int, int], ...]:
    """Generate a frozen universal-hash family using SplitMix64 coefficients."""

    state = seed & MASK64
    coefficients: list[tuple[int, int]] = []
    for _ in range(num_perm):
        state = _splitmix64(state)
        a = 1 + (_splitmix64(state) % (MINHASH_PRIME - 1))
        state = _splitmix64(state)
        b = _splitmix64(state) % MINHASH_PRIME
        coefficients.append((a, b))
    return tuple(coefficients)


def _feature_hash(feature: str) -> int:
    return int.from_bytes(hashlib.sha256(feature.encode("utf-8")).digest()[:8], "big") % MINHASH_PRIME


def exact_deduplicate(records: Iterable[Mapping[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Keep the lexicographically first record ID for each normalized-text SHA."""

    ordered = sorted((dict(record) for record in records), key=lambda item: str(item["record_id"]))
    keepers: dict[str, dict[str, Any]] = {}
    duplicates: list[dict[str, Any]] = []
    for record in ordered:
        key = str(record["normalized_text_sha256"])
        if key in keepers:
            duplicates.append(
                {
                    "duplicate_record_id": record["record_id"],
                    "keeper_record_id": keepers[key]["record_id"],
                    "normalized_text_sha256": key,
                }
            )
        else:
            keepers[key] = record
    return list(keepers.values()), duplicates


def character_ngrams(text: str, n: int = 5) -> frozenset[str]:
    if n <= 0:
        raise ValueError("n must be positive")
    return frozenset(text[index : index + n] for index in range(max(len(text) - n + 1, 0)))


def minhash_signature(features: Iterable[str], *, num_perm: int = 128, seed: int = 42) -> tuple[int, ...]:
    """Create a standard deterministic universal-hash MinHash signature.

    The feature universe is SHA-256-to-uint64, followed by the frozen universal family
    ``(a*x+b) mod p`` with the 61-bit Mersenne prime ``p = 2**61-1``.  Coefficients are generated
    by SplitMix64 from the supplied seed.  There is deliberately no feature-count cap.
    """

    if num_perm <= 0:
        raise ValueError("num_perm must be positive")
    feature_hashes = tuple(_feature_hash(feature) for feature in sorted(set(features)))
    if not feature_hashes:
        return tuple([MINHASH_PRIME] * num_perm)
    coefficients = _universal_hash_coefficients(num_perm, seed)
    return tuple(
        min((a * value + b) % MINHASH_PRIME for value in feature_hashes)
        for a, b in coefficients
    )


def exact_jaccard(first: Iterable[str], second: Iterable[str]) -> float:
    first_set = set(first)
    second_set = set(second)
    union = first_set | second_set
    return len(first_set & second_set) / len(union) if union else 1.0


def lsh_candidate_pairs(
    signatures: Mapping[str, tuple[int, ...]], *, num_bands: int = 32, rows_per_band: int = 4,
    max_candidate_pairs: int = 1_000_000,
) -> list[tuple[str, str]]:
    """Generate deterministic candidate pairs with 32 bands × 4 rows.

    The candidate protocol is complete for the frozen band-equality rule, avoids materializing all
    ``n choose 2`` pairs, and verifies the frozen MinHash threshold only on generated candidates.
    Any candidate explosion fails closed instead of silently sampling or truncating pairs.
    """

    if num_bands <= 0 or rows_per_band <= 0 or num_bands * rows_per_band != 128:
        raise ValueError("the frozen protocol requires num_bands * rows_per_band == 128")
    if max_candidate_pairs <= 0:
        raise ValueError("max_candidate_pairs must be positive")
    buckets: dict[tuple[int, tuple[int, ...]], list[str]] = {}
    for record_id in sorted(signatures):
        signature = signatures[record_id]
        if len(signature) != num_bands * rows_per_band:
            raise ValueError("signature length does not match frozen LSH banding")
        for band in range(num_bands):
            start = band * rows_per_band
            key = (band, signature[start : start + rows_per_band])
            buckets.setdefault(key, []).append(record_id)
    candidates: set[tuple[str, str]] = set()
    for members in buckets.values():
        if len(members) < 2:
            continue
        for first, second in combinations(sorted(members), 2):
            candidates.add((first, second))
            if len(candidates) > max_candidate_pairs:
                raise ValueError("near-dedup candidate bound exceeded; wave fails closed")
    return sorted(candidates)


def signature_similarity(first: tuple[int, ...], second: tuple[int, ...]) -> float:
    if len(first) != len(second) or not first:
        raise ValueError("signatures must have equal non-zero length")
    return sum(a == b for a, b in zip(first, second, strict=True)) / len(first)


def iter_near_duplicate_pairs(
    records: Iterable[Mapping[str, Any]], *, threshold: float = 0.80, num_perm: int = 128, seed: int = 42,
    num_bands: int = 32, rows_per_band: int = 4, max_candidate_pairs: int = 1_000_000,
) -> Iterator[dict[str, Any]]:
    """Stream threshold-verified candidate results without an all-pairs comparison."""

    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be between 0 and 1")
    for pair in _iter_near_duplicate_pairs_sqlite(
        records,
        threshold=threshold,
        num_perm=num_perm,
        seed=seed,
        num_bands=num_bands,
        rows_per_band=rows_per_band,
        max_candidate_pairs=max_candidate_pairs,
        max_output_pairs=None,
    ):
        yield pair


def _pack_signature(signature: tuple[int, ...]) -> str:
    return json.dumps(signature, separators=(",", ":"))


def _unpack_signature(value: str) -> tuple[int, ...]:
    return tuple(int(item) for item in json.loads(value))


def _iter_near_duplicate_pairs_sqlite(
    records: Iterable[Mapping[str, Any]], *, threshold: float, num_perm: int, seed: int,
    num_bands: int, rows_per_band: int, max_candidate_pairs: int, max_output_pairs: int | None,
    stats: dict[str, int] | None = None,
) -> Iterator[dict[str, Any]]:
    """Use a temporary SQLite spill so signatures/buckets/candidates are not retained in RAM."""

    if num_bands <= 0 or rows_per_band <= 0 or num_bands * rows_per_band != num_perm:
        raise ValueError("num_bands * rows_per_band must equal num_perm")
    if max_candidate_pairs <= 0:
        raise ValueError("max_candidate_pairs must be positive")
    if max_output_pairs is not None and max_output_pairs <= 0:
        raise ValueError("max_output_pairs must be positive")
    with tempfile.TemporaryDirectory(prefix="vngrs_lsh_") as temp_dir:
        database = sqlite3.connect(f"{temp_dir}/lsh.sqlite3")
        try:
            database.execute("CREATE TABLE signatures (record_id TEXT PRIMARY KEY, signature TEXT NOT NULL)")
            database.execute("CREATE TABLE buckets (band INTEGER NOT NULL, bucket TEXT NOT NULL, record_id TEXT NOT NULL)")
            database.execute("CREATE TABLE candidate_pairs (first_id TEXT NOT NULL, second_id TEXT NOT NULL, PRIMARY KEY (first_id, second_id))")
            seen: set[str] = set()
            record_count = 0
            for record in records:
                record_id = str(record["record_id"])
                if record_id in seen:
                    raise ValueError(f"duplicate record_id in near-dedup input: {record_id}")
                seen.add(record_id)
                signature = minhash_signature(
                    character_ngrams(str(record["normalized_text"]), 5), num_perm=num_perm, seed=seed
                )
                database.execute("INSERT INTO signatures VALUES (?, ?)", (record_id, _pack_signature(signature)))
                for band in range(num_bands):
                    start = band * rows_per_band
                    bucket = json.dumps(signature[start : start + rows_per_band], separators=(",", ":"))
                    database.execute("INSERT INTO buckets VALUES (?, ?, ?)", (band, bucket, record_id))
                record_count += 1
            database.execute("CREATE INDEX bucket_index ON buckets (band, bucket, record_id)")
            database.commit()
            if stats is not None:
                stats["record_count"] = record_count
            candidate_count = 0
            output_count = 0
            cursor = database.execute("SELECT band, bucket FROM buckets GROUP BY band, bucket HAVING COUNT(*) > 1 ORDER BY band, bucket")
            for band, bucket in cursor:
                members = [row[0] for row in database.execute(
                    "SELECT record_id FROM buckets WHERE band = ? AND bucket = ? ORDER BY record_id", (band, bucket)
                )]
                for first_id, second_id in combinations(members, 2):
                    inserted = database.execute(
                        "INSERT OR IGNORE INTO candidate_pairs VALUES (?, ?)", (first_id, second_id)
                    ).rowcount
                    if inserted != 1:
                        continue
                    candidate_count += 1
                    if stats is not None:
                        stats["candidate_pair_count"] = candidate_count
                        stats["evaluated_pair_count"] = candidate_count
                    if candidate_count > max_candidate_pairs:
                        raise ValueError("near-dedup candidate bound exceeded; wave fails closed")
                    first_sig = _unpack_signature(database.execute(
                        "SELECT signature FROM signatures WHERE record_id = ?", (first_id,)
                    ).fetchone()[0])
                    second_sig = _unpack_signature(database.execute(
                        "SELECT signature FROM signatures WHERE record_id = ?", (second_id,)
                    ).fetchone()[0])
                    similarity = signature_similarity(first_sig, second_sig)
                    if similarity < threshold:
                        continue
                    output_count += 1
                    if stats is not None:
                        stats["near_duplicate_pair_count"] = output_count
                    if max_output_pairs is not None and output_count > max_output_pairs:
                        raise ValueError("near-dedup output bound exceeded; wave fails closed")
                    yield {"first_record_id": first_id, "second_record_id": second_id, "estimated_jaccard": similarity}
        finally:
            database.close()


def near_duplicate_summary(
    records: Iterable[Mapping[str, Any]], *, threshold: float = 0.80, num_perm: int = 128, seed: int = 42,
    num_bands: int = 32, rows_per_band: int = 4, max_candidate_pairs: int = 1_000_000,
    max_output_pairs: int = 100_000,
) -> dict[str, Any]:
    """Return compact affected-record diagnostics with explicit denominators and bounds."""

    stats = {"record_count": 0, "candidate_pair_count": 0, "evaluated_pair_count": 0, "near_duplicate_pair_count": 0}
    pairs = []
    affected: set[str] = set()
    candidate_count = 0
    evaluated_count = 0
    for pair in _iter_near_duplicate_pairs_sqlite(
        records,
        threshold=threshold,
        num_perm=num_perm,
        seed=seed,
        num_bands=num_bands,
        rows_per_band=rows_per_band,
        max_candidate_pairs=max_candidate_pairs,
        max_output_pairs=max_output_pairs,
        stats=stats,
    ):
        pairs.append(pair)
        affected.update((pair["first_record_id"], pair["second_record_id"]))
    denominator = stats["record_count"]
    return {
        "protocol": NEAR_DEDUP_VERSION,
        "feature": "unbounded_character_5grams",
        "hash_family": MINHASH_HASH_FAMILY,
        "memory_mode": "sqlite_spill_bounded_v1",
        "num_perm": num_perm,
        "seed": seed,
        "num_bands": num_bands,
        "rows_per_band": rows_per_band,
        "threshold": threshold,
        "candidate_pair_count": stats["candidate_pair_count"],
        "evaluated_pair_count": stats["evaluated_pair_count"],
        "near_duplicate_pair_count": stats["near_duplicate_pair_count"],
        "affected_record_count": len(affected),
        "denominator": denominator,
        "affected_record_rate": (len(affected) / denominator) if denominator else None,
        "pairs": pairs,
    }


def near_duplicate_pairs(
    records: Iterable[Mapping[str, Any]], *, threshold: float = 0.80, num_perm: int = 128, seed: int = 42,
    num_bands: int = 32, rows_per_band: int = 4, max_candidate_pairs: int = 1_000_000,
    max_output_pairs: int = 100_000,
) -> list[dict[str, Any]]:
    """Compatibility wrapper returning only the compact verified pair rows."""

    return near_duplicate_summary(
        records,
        threshold=threshold,
        num_perm=num_perm,
        seed=seed,
        num_bands=num_bands,
        rows_per_band=rows_per_band,
        max_candidate_pairs=max_candidate_pairs,
        max_output_pairs=max_output_pairs,
    )["pairs"]
