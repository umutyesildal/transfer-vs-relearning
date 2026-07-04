from __future__ import annotations

import bz2
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, Iterable, Iterator, TextIO

from transfer_vs_relearning.corpora.config import stage_dirs
from transfer_vs_relearning.corpora.document import CorpusDocument
from transfer_vs_relearning.corpora.io import write_jsonl
from transfer_vs_relearning.utils.io import write_json


def parse_wikitext(text: str) -> tuple[str, dict[str, int]]:
    try:
        import mwparserfromhell

        _assert_package_version("mwparserfromhell", "mwparserfromhell", "0.7.2")
        parsed = mwparserfromhell.parse(text)
        plain = parsed.strip_code(normalize=True, collapse=True)
    except ModuleNotFoundError:
        plain = _fallback_strip_wikitext(text)
    artifacts = {
        "template_markers": plain.count("{{"),
        "link_markers": plain.count("[["),
        "html_ref_markers": plain.lower().count("<ref"),
    }
    return plain, artifacts


def extract_from_xml_text(xml_text: str, config: dict[str, Any]) -> tuple[list[CorpusDocument], list[dict[str, Any]]]:
    root = ET.fromstring(xml_text)
    ns = _namespace(root.tag)
    documents: list[CorpusDocument] = []
    failures: list[dict[str, Any]] = []
    for page in root.findall(f"{ns}page"):
        doc, failure = _extract_page(page, ns, config)
        if doc:
            documents.append(doc)
        if failure:
            failures.append(failure)
    return documents, failures


def iter_extract_from_xml_stream(handle: TextIO, config: dict[str, Any]) -> Iterator[tuple[CorpusDocument | None, dict[str, Any] | None]]:
    ns = ""
    for event, element in ET.iterparse(handle, events=("start", "end")):
        if event == "start" and not ns:
            ns = _namespace(element.tag)
        if event == "end" and element.tag == f"{ns}page":
            doc, failure = _extract_page(element, ns, config)
            yield doc, failure
            element.clear()


def extract_from_xml_stream(handle: TextIO, config: dict[str, Any]) -> tuple[list[CorpusDocument], list[dict[str, Any]]]:
    documents: list[CorpusDocument] = []
    failures: list[dict[str, Any]] = []
    for doc, failure in iter_extract_from_xml_stream(handle, config):
        if doc:
            documents.append(doc)
        if failure:
            failures.append(failure)
    return documents, failures


def extract_stage(config: dict[str, Any]) -> Path:
    raw_path = stage_dirs(config)["raw"] / config["dump_filename"]
    out_path = stage_dirs(config)["extracted"] / "documents.jsonl"
    failures_path = stage_dirs(config)["reports"] / "extraction_failures.jsonl"
    actual_parser = "mwxml"
    parser_versions = {}
    use_fixture_parser = bool(config.get("extraction", {}).get("allow_stdlib_fixture_parser", False))
    if not use_fixture_parser:
        parser_versions = _assert_extraction_versions(config)
    document_count = 0
    failure_count = 0
    out_path.parent.mkdir(parents=True, exist_ok=True)
    failures_path.parent.mkdir(parents=True, exist_ok=True)
    out_tmp = out_path.with_suffix(out_path.suffix + ".tmp")
    fail_tmp = failures_path.with_suffix(failures_path.suffix + ".tmp")
    with out_tmp.open("w", encoding="utf-8") as out_handle, fail_tmp.open("w", encoding="utf-8") as fail_handle:
        iterator = _iter_fixture_dump(raw_path, config) if use_fixture_parser else _iter_real_dump(raw_path, config)
        if use_fixture_parser:
            actual_parser = "xml.etree.fixture_only"
        for doc, failure in iterator:
            if doc:
                out_handle.write(json.dumps(doc.to_json(), ensure_ascii=False, sort_keys=True) + "\n")
                document_count += 1
            if failure:
                fail_handle.write(json.dumps(failure, ensure_ascii=False, sort_keys=True) + "\n")
                failure_count += 1
    out_tmp.replace(out_path)
    fail_tmp.replace(failures_path)
    write_json(stage_dirs(config)["manifests"] / "extraction_manifest.json", {
        "status": "completed",
        "document_count": document_count,
        "failure_count": failure_count,
        "actual_parser": actual_parser,
        "runtime_versions": parser_versions,
        "template_expansion": "best_effort_not_perfect",
    })
    return out_path


def _iter_real_dump(raw_path: Path, config: dict[str, Any]) -> Iterator[tuple[CorpusDocument | None, dict[str, Any] | None]]:
    import mwxml

    with bz2.open(raw_path, "rt", encoding="utf-8", errors="replace") as handle:
        dump = mwxml.Dump.from_file(handle)
        for page in dump:
            try:
                namespace_value = getattr(page, "namespace", -1)
                namespace = -1 if namespace_value is None else int(namespace_value)
                if namespace != int(config.get("extraction", {}).get("namespace", 0)):
                    continue
                if getattr(page, "redirect", None) and config.get("extraction", {}).get("skip_redirects", True):
                    continue
                revision = None
                for revision in page:
                    pass
                if revision is None:
                    yield None, {"page_id": str(getattr(page, "id", "")), "title": getattr(page, "title", ""), "error": "missing revision"}
                    continue
                wikitext = getattr(revision, "text", "") or ""
                extracted, artifacts = parse_wikitext(wikitext)
                page_id = str(getattr(page, "id", ""))
                revision_id = str(getattr(revision, "id", ""))
                yield CorpusDocument(
                    document_id=f"{config['corpus_id']}:{page_id}:{revision_id}",
                    page_id=page_id,
                    revision_id=revision_id,
                    title=getattr(page, "title", ""),
                    namespace=namespace,
                    dump_date=str(config["dump_date"]),
                    source_project=config["project"],
                    text=extracted,
                    raw_wikitext_sha256=hashlib.sha256(wikitext.encode("utf-8")).hexdigest(),
                    processing_stage="extracted",
                    provenance={
                        "is_redirect": bool(getattr(page, "redirect", None)),
                        "is_disambiguation": _is_disambiguation(getattr(page, "title", ""), wikitext),
                        "unresolved_markup": artifacts,
                    },
                ), None
            except Exception as exc:
                yield None, {"page_id": str(getattr(page, "id", "")), "title": getattr(page, "title", ""), "error": str(exc)}


def _iter_fixture_dump(raw_path: Path, config: dict[str, Any]) -> Iterator[tuple[CorpusDocument | None, dict[str, Any] | None]]:
    with bz2.open(raw_path, "rt", encoding="utf-8", errors="replace") as handle:
        yield from iter_extract_from_xml_stream(handle, config)


def _fallback_strip_wikitext(text: str) -> str:
    text = re.sub(r"<ref[^>]*>.*?</ref>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"\{\{[^{}]*\}\}", " ", text)
    text = re.sub(r"\[\[([^|\]]*\|)?([^\]]+)\]\]", r"\2", text)
    text = re.sub(r"'{2,}", "", text)
    return text


def _extract_page(page: ET.Element[str], ns: str, config: dict[str, Any]) -> tuple[CorpusDocument | None, dict[str, Any] | None]:
    title = _text(page.find(f"{ns}title"))
    page_id = _text(page.find(f"{ns}id"))
    namespace = int(_text(page.find(f"{ns}ns")) or -1)
    redirect = page.find(f"{ns}redirect") is not None
    if namespace != int(config.get("extraction", {}).get("namespace", 0)):
        return None, None
    if redirect and config.get("extraction", {}).get("skip_redirects", True):
        return None, None
    revision = page.find(f"{ns}revision")
    if revision is None:
        return None, {"page_id": page_id, "title": title, "error": "missing revision"}
    revision_id = _text(revision.find(f"{ns}id"))
    wikitext = _text(revision.find(f"{ns}text"))
    try:
        extracted, artifacts = parse_wikitext(wikitext)
        document_id = f"{config['corpus_id']}:{page_id}:{revision_id}"
        return CorpusDocument(
            document_id=document_id,
            page_id=page_id,
            revision_id=revision_id,
            title=title,
            namespace=namespace,
            dump_date=str(config["dump_date"]),
            source_project=config["project"],
            text=extracted,
            raw_wikitext_sha256=hashlib.sha256(wikitext.encode("utf-8")).hexdigest(),
            processing_stage="extracted",
            provenance={
                "is_redirect": redirect,
                "is_disambiguation": _is_disambiguation(title, wikitext),
                "unresolved_markup": artifacts,
            },
        ), None
    except Exception as exc:
        return None, {"page_id": page_id, "title": title, "error": str(exc)}


def _is_disambiguation(title: str, text: str) -> bool:
    lowered = f"{title}\n{text}".casefold()
    return "anlam ayrımı" in lowered or "{{anlam ayrımı" in lowered


def _namespace(tag: str) -> str:
    if tag.startswith("{"):
        return tag.split("}", 1)[0] + "}"
    return ""


def _text(element: ET.Element[str] | None) -> str:
    return element.text or "" if element is not None else ""


def _write_documents(path: Path, documents: Iterable[CorpusDocument]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        for doc in documents:
            handle.write(json.dumps(doc.to_json(), ensure_ascii=False, sort_keys=True) + "\n")
    tmp.replace(path)


def _write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    write_jsonl(path, rows)


def _assert_extraction_versions(config: dict[str, Any]) -> dict[str, str]:
    expected = {
        "mwxml": config["extraction"]["mwxml_version"],
        "mwparserfromhell": config["extraction"]["mwparserfromhell_version"],
    }
    observed = {}
    for package in expected:
        observed[package] = _assert_package_version(package, package, expected[package])
    return observed


def _assert_package_version(import_name: str, package_name: str, expected: str) -> str:
    try:
        observed = version(package_name)
    except PackageNotFoundError as exc:
        raise ModuleNotFoundError(f"Required extraction package missing: {package_name}=={expected}") from exc
    if observed != expected:
        raise RuntimeError(f"{package_name} version mismatch: expected {expected}, observed {observed}")
    return observed
