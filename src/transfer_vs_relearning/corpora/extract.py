from __future__ import annotations

import bz2
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Iterable, TextIO

from transfer_vs_relearning.corpora.config import stage_dirs
from transfer_vs_relearning.corpora.document import CorpusDocument
from transfer_vs_relearning.utils.io import write_json


def parse_wikitext(text: str) -> tuple[str, dict[str, int]]:
    try:
        import mwparserfromhell

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


def extract_from_xml_stream(handle: TextIO, config: dict[str, Any]) -> tuple[list[CorpusDocument], list[dict[str, Any]]]:
    documents: list[CorpusDocument] = []
    failures: list[dict[str, Any]] = []
    ns = ""
    for event, element in ET.iterparse(handle, events=("start", "end")):
        if event == "start" and not ns:
            ns = _namespace(element.tag)
        if event == "end" and element.tag == f"{ns}page":
            doc, failure = _extract_page(element, ns, config)
            if doc:
                documents.append(doc)
            if failure:
                failures.append(failure)
            element.clear()
    return documents, failures


def extract_stage(config: dict[str, Any]) -> Path:
    raw_path = stage_dirs(config)["raw"] / config["dump_filename"]
    out_path = stage_dirs(config)["extracted"] / "documents.jsonl"
    failures_path = stage_dirs(config)["reports"] / "extraction_failures.jsonl"
    with bz2.open(raw_path, "rt", encoding="utf-8", errors="replace") as handle:
        documents, failures = extract_from_xml_stream(handle, config)
    _write_documents(out_path, documents)
    _write_jsonl(failures_path, failures)
    write_json(stage_dirs(config)["manifests"] / "extraction_manifest.json", {
        "status": "completed",
        "document_count": len(documents),
        "failure_count": len(failures),
        "mwxml_version": config["extraction"]["mwxml_version"],
        "mwparserfromhell_version": config["extraction"]["mwparserfromhell_version"],
        "template_expansion": "best_effort_not_perfect",
    })
    return out_path


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
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    tmp.replace(path)
