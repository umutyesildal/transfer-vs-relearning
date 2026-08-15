from __future__ import annotations

import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / ".tmp" / "paper_work" / "extracted_text"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def markdown_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.parts.append(data.strip())


def html_text(path: Path) -> str:
    parser = _TextExtractor()
    parser.feed(path.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parser.parts)


def pdf_text(path: Path) -> tuple[str, int]:
    reader = PdfReader(str(path))
    pages = []
    for index, page in enumerate(reader.pages, start=1):
        pages.append(f"===== PAGE {index} =====\n{page.extract_text() or ''}")
    return "\n\n".join(pages), len(reader.pages)


def title_for(path: Path, text: str) -> str:
    for line in text.splitlines():
        candidate = re.sub(r"^#+\s*", "", line.strip())
        if candidate and not candidate.startswith("====="):
            return candidate[:240]
    return path.stem


def high_signal_lines(text: str) -> list[str]:
    pattern = re.compile(
        r"(?i)(status|durum|decision|karar|verdict|result|sonuç|finding|bulgu|gate|kapı|"
        r"accuracy|top-1|perplex|ppl|robust|interaction|confidence|bootstrap|primary|"
        r"transfer|relearning|reaffirm|retention|forget|blocked|pass|fail|hold|seed|"
        r"M0|M1|M2|M3|token|subject|fact)"
    )
    selected = []
    seen = set()
    for raw in text.splitlines():
        line = re.sub(r"\s+", " ", raw).strip()
        if not line or len(line) > 700 or not pattern.search(line):
            continue
        if line in seen:
            continue
        seen.add(line)
        selected.append(line)
        if len(selected) >= 90:
            break
    return selected


def headings(text: str) -> list[str]:
    found = []
    for raw in text.splitlines():
        line = raw.strip()
        if re.match(r"^#{1,6}\s+", line):
            found.append(line)
        elif re.match(r"^(abstract|introduction|related work|method|methods|results?|discussion|conclusion|limitations?)\b", line, re.I):
            found.append(line[:240])
        if len(found) >= 120:
            break
    return found


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    paths = sorted(
        [p for p in (ROOT / "documentation").rglob("*") if p.is_file() and p.suffix.lower() in {".md", ".html", ".pdf"}]
        + [p for p in (ROOT / "papers").rglob("*.pdf") if p.is_file()]
    )
    manifest = []
    digest = ["# Paper source digest", ""]
    for path in paths:
        suffix = path.suffix.lower()
        pages = None
        if suffix == ".md":
            text = markdown_text(path)
        elif suffix == ".html":
            text = html_text(path)
        else:
            text, pages = pdf_text(path)

        rel = path.relative_to(ROOT)
        out_path = OUT / (str(rel).replace("/", "__") + ".txt")
        out_path.write_text(text, encoding="utf-8")
        words = len(re.findall(r"\S+", text))
        record = {
            "path": str(rel),
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
            "pages": pages,
            "words": words,
            "title": title_for(path, text),
            "extracted_text": str(out_path.relative_to(ROOT)),
        }
        manifest.append(record)

        digest.extend([
            f"## {record['path']}",
            "",
            f"- Title: {record['title']}",
            f"- SHA-256: `{record['sha256']}`",
            f"- Words: {words}" + (f"; pages: {pages}" if pages is not None else ""),
            "",
        ])
        hs = headings(text)
        if hs:
            digest.append("Headings:")
            digest.extend(f"- {line}" for line in hs)
            digest.append("")
        sig = high_signal_lines(text)
        if sig:
            digest.append("High-signal lines:")
            digest.extend(f"- {line}" for line in sig)
            digest.append("")

    (ROOT / ".tmp" / "paper_work" / "source_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (ROOT / ".tmp" / "paper_work" / "source_digest.md").write_text(
        "\n".join(digest), encoding="utf-8"
    )
    print(json.dumps({
        "files": len(manifest),
        "words": sum(item["words"] for item in manifest),
        "pdf_pages": sum(item["pages"] or 0 for item in manifest),
        "manifest": ".tmp/paper_work/source_manifest.json",
        "digest": ".tmp/paper_work/source_digest.md",
    }, indent=2))


if __name__ == "__main__":
    main()
