"""Convert crawl_output into structured, traceable QA knowledge.

Run after documentation_knowledge_builder.py:
    python playground/qa_knowledge_builder.py

The generated crawl_output/qa_knowledge.json is deliberately deterministic: it
does not call an LLM or invent requirements. A later test-case generator can
retrieve its chunks and use their source URLs as evidence for each test case.
"""

from __future__ import annotations

import csv
import hashlib
import json
import logging
import re
import sys
import zipfile
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from xml.etree import ElementTree


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CRAWL_OUTPUT = PROJECT_ROOT / "crawl_output"
OUTPUT_FILE = CRAWL_OUTPUT / "qa_knowledge.json"
MAX_CHUNK_CHARACTERS = 3_500
MIN_TEXT_CHARACTERS = 40
SUPPORTED_TEXT_ATTACHMENTS = {".pdf", ".docx", ".xlsx", ".pptx", ".csv", ".txt", ".md", ".html", ".htm"}


class TextHTMLParser(HTMLParser):
    """Small dependency-free HTML-to-text fallback."""

    BLOCK_TAGS = {"p", "div", "section", "article", "main", "li", "br", "h1", "h2", "h3", "h4", "h5", "h6", "tr"}
    IGNORE_TAGS = {"script", "style", "noscript", "svg"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.ignored_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self.IGNORE_TAGS:
            self.ignored_depth += 1
        if tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in self.IGNORE_TAGS and self.ignored_depth:
            self.ignored_depth -= 1
        if tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.ignored_depth:
            self.parts.append(data)

    def text(self) -> str:
        return normalize_text("".join(self.parts))


def normalize_text(value: str) -> str:
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def relative(path: Path) -> str:
    return path.relative_to(CRAWL_OUTPUT).as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def html_to_text(html: str) -> str:
    parser = TextHTMLParser()
    try:
        parser.feed(html)
    except Exception as exc:
        logging.warning("Could not fully parse HTML: %s", exc)
    return parser.text()


def markdown_sections(markdown: str, fallback_title: str) -> list[tuple[str, str]]:
    """Split a page into heading-based sections suitable for retrieval."""
    heading = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
    matches = list(heading.finditer(markdown))
    if not matches:
        return [(fallback_title, markdown)] if markdown.strip() else []
    sections: list[tuple[str, str]] = []
    preamble = markdown[:matches[0].start()].strip()
    if preamble:
        sections.append((fallback_title, preamble))
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        title = re.sub(r"\s+#*$", "", match.group(2)).strip()
        body = markdown[match.end():end].strip()
        if body:
            sections.append((title, body))
    return sections


def split_large_section(text: str, size: int = MAX_CHUNK_CHARACTERS) -> list[str]:
    """Split at a paragraph or sentence boundary without losing any text."""
    if len(text) <= size:
        return [text]
    chunks: list[str] = []
    remaining = text
    while len(remaining) > size:
        boundary = max(remaining.rfind("\n\n", 0, size), remaining.rfind(". ", 0, size))
        if boundary < size // 2:
            boundary = size
        else:
            boundary += 1
        chunks.append(remaining[:boundary].strip())
        remaining = remaining[boundary:].strip()
    if remaining:
        chunks.append(remaining)
    return chunks


def zip_xml_text(path: Path, members: list[str]) -> str:
    """Extract readable text from Office Open XML files without extra packages."""
    texts: list[str] = []
    try:
        with zipfile.ZipFile(path) as archive:
            for member in members:
                if member not in archive.namelist():
                    continue
                root = ElementTree.fromstring(archive.read(member))
                texts.extend(node.text for node in root.iter() if node.text)
    except (OSError, zipfile.BadZipFile, ElementTree.ParseError) as exc:
        logging.warning("Could not read %s: %s", path.name, exc)
    return normalize_text(" ".join(texts))


def extract_pdf(path: Path) -> str:
    """Use pypdf when installed; PDFs without text are retained as assets only."""
    try:
        from pypdf import PdfReader  # Optional, installed with: pip install pypdf
        return normalize_text("\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages))
    except ImportError:
        logging.info("Skipping PDF text extraction for %s (install pypdf to enable it)", path.name)
    except Exception as exc:
        logging.warning("Could not extract PDF text from %s: %s", path.name, exc)
    return ""


def extract_attachment(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return extract_pdf(path)
    if suffix == ".docx":
        return zip_xml_text(path, ["word/document.xml"])
    if suffix == ".pptx":
        slide_members = []
        try:
            with zipfile.ZipFile(path) as archive:
                slide_members = sorted(name for name in archive.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", name))
        except (OSError, zipfile.BadZipFile):
            pass
        return zip_xml_text(path, slide_members)
    if suffix == ".xlsx":
        return zip_xml_text(path, ["xl/sharedStrings.xml", "xl/worksheets/sheet1.xml"])
    if suffix == ".csv":
        try:
            with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
                return normalize_text("\n".join(" | ".join(row) for row in csv.reader(handle)))
        except OSError as exc:
            logging.warning("Could not read %s: %s", path.name, exc)
            return ""
    if suffix in {".txt", ".md", ".html", ".htm"}:
        text = read_text(path)
        return html_to_text(text) if suffix in {".html", ".htm"} else normalize_text(text)
    return ""


def chunk_record(*, source_type: str, source_path: str, source_url: str | None,
                 page_title: str, section_title: str, text: str, sequence: int) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    for part, piece in enumerate(split_large_section(normalize_text(text)), start=1):
        if len(piece) < MIN_TEXT_CHARACTERS:
            continue
        identity = f"{source_path}|{section_title}|{part}|{piece}"
        chunks.append({
            "id": "chunk_" + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16],
            "sequence": sequence + part - 1,
            "source_type": source_type,
            "source_path": source_path,
            "source_url": source_url,
            "page_title": page_title,
            "section_title": section_title,
            "text": piece,
        })
    return chunks


def load_metadata() -> list[dict[str, Any]]:
    records = []
    for path in sorted((CRAWL_OUTPUT / "metadata").rglob("*.json")):
        try:
            record = json.loads(read_text(path))
            if isinstance(record, dict) and record.get("url"):
                records.append(record)
        except (OSError, json.JSONDecodeError) as exc:
            logging.warning("Ignoring invalid metadata %s: %s", path, exc)
    return records


def build_knowledge() -> dict[str, Any]:
    if not CRAWL_OUTPUT.is_dir():
        raise FileNotFoundError(f"Crawler output was not found: {CRAWL_OUTPUT}")

    manifest_path = CRAWL_OUTPUT / "manifest.json"
    manifest = json.loads(read_text(manifest_path)) if manifest_path.exists() else {}
    metadata_records = load_metadata()
    documents: list[dict[str, Any]] = []
    chunks: list[dict[str, Any]] = []
    known_paths: set[str] = set()

    for record in metadata_records:
        markdown_path = CRAWL_OUTPUT / record.get("markdown_path", "")
        html_path = CRAWL_OUTPUT / record.get("html_path", "")
        source_path = relative(markdown_path) if markdown_path.exists() else relative(html_path)
        content = read_text(markdown_path) if markdown_path.exists() else html_to_text(read_text(html_path)) if html_path.exists() else ""
        known_paths.update(filter(None, [record.get("markdown_path"), record.get("html_path")]))
        document = {
            "id": "page_" + hashlib.sha256(record["url"].encode("utf-8")).hexdigest()[:16],
            "type": "documentation_page",
            "title": record.get("title") or record["url"],
            "source_url": record["url"],
            "parent_url": record.get("parent_url"),
            "child_links": record.get("child_links", []),
            "depth": record.get("depth", 0),
            "source_path": source_path,
            "assets": {"images": record.get("images", []), "attachments": record.get("attachments", [])},
        }
        documents.append(document)
        sequence = 1
        for section_title, section_text in markdown_sections(content, document["title"]):
            section_chunks = chunk_record(
                source_type="documentation_page", source_path=source_path, source_url=record["url"],
                page_title=document["title"], section_title=section_title, text=section_text, sequence=sequence,
            )
            chunks.extend(section_chunks)
            sequence += len(section_chunks)

    # Crawl attachment folders independently. This also finds attachments whose
    # page metadata was not written because the crawl was interrupted.
    for folder in (CRAWL_OUTPUT / "attachments",):
        if not folder.exists():
            continue
        for path in sorted(folder.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in SUPPORTED_TEXT_ATTACHMENTS:
                continue
            source_path = relative(path)
            text = extract_attachment(path)
            documents.append({
                "id": "attachment_" + hashlib.sha256(source_path.encode("utf-8")).hexdigest()[:16],
                "type": "attachment",
                "title": path.name,
                "source_url": None,
                "source_path": source_path,
                "extractable_text": bool(text),
            })
            chunks.extend(chunk_record(
                source_type="attachment", source_path=source_path, source_url=None,
                page_title=path.name, section_title="Document content", text=text, sequence=1,
            ))

    graph_path = CRAWL_OUTPUT / "graph.json"
    graph = json.loads(read_text(graph_path)) if graph_path.exists() else {"nodes": [], "edges": []}
    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_crawl": {
            "root_url": manifest.get("root_url"),
            "manifest_path": "manifest.json" if manifest_path.exists() else None,
            "pages_crawled": manifest.get("pages_crawled", len(metadata_records)),
        },
        "documents": documents,
        "chunks": chunks,
        "navigation_graph": graph,
        "statistics": {
            "documentation_pages": len(metadata_records),
            "documents": len(documents),
            "retrieval_chunks": len(chunks),
            "extractable_attachments": sum(item["type"] == "attachment" and item["extractable_text"] for item in documents),
        },
        "test_generation_contract": {
            "instruction": "Generate test cases only from cited chunks; retain chunk_ids and source_url for traceability. Each step must contain exactly one user action and no expected-result text.",
            "required_test_case_fields": ["id", "title", "priority", "preconditions", "steps", "expected_result", "source_chunk_ids", "source_urls"],
            "step_schema": {"action": "One atomic user action only."},
        },
    }


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s")
    knowledge = build_knowledge()
    OUTPUT_FILE.write_text(json.dumps(knowledge, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    logging.info("Created %s (%s documents, %s chunks)", OUTPUT_FILE, knowledge["statistics"]["documents"], knowledge["statistics"]["retrieval_chunks"])


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        logging.error("Knowledge build failed: %s", exc)
        sys.exit(1)
