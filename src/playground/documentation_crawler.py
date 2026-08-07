"""Build a local, graph-shaped documentation corpus with Crawl4AI.

Install once (Python 3.10+ recommended):
    pip install "crawl4ai==0.9.2"
    crawl4ai-setup

Then edit ROOT_URL if needed and run from the repository root:
    python playground/documentation_knowledge_builder.py

The output directory is intentionally git-friendly: each URL is translated into
the same hierarchy under markdown/, html/, and metadata/.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import re
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, unquote, urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen

from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.deep_crawling.filters import FilterChain, URLPatternFilter


# ------------------------------ Configuration ------------------------------
# Change these three values before running a different crawl.
DEFAULT_ROOT_URL = "https://docs.inventree.org/en/stable/part/"
PROJECT_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "crawl_output"
MAX_DEPTH = 5
MAX_PAGES = 200

# crawl_output/ is placed beside this script's parent directory, regardless of
# the directory from which Python is invoked.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "crawl_output"

REQUEST_TIMEOUT_SECONDS = 15
PAGE_TIMEOUT_MS = 30_000
CRAWL_TIMEOUT_SECONDS = 15 * 60
ASSET_BATCH_TIMEOUT_SECONDS = 60
MAX_ASSET_CONCURRENCY = 8
USER_AGENT = "documentation-knowledge-builder/1.0 (+local knowledge corpus)"
ASSET_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".zip",
    ".csv", ".svg", ".png", ".jpg", ".jpeg", ".gif",
}
IMAGE_EXTENSIONS = {".svg", ".png", ".jpg", ".jpeg", ".gif"}
LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(message)s"


class PageHTMLParser(HTMLParser):
    """Dependency-free collection of titles, links, image sources, and assets."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self._in_title = False
        self.links: list[str] = []
        self.asset_urls: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {name.lower(): value for name, value in attrs if value}
        if tag.lower() == "title":
            self._in_title = True
        # href is a page link for <a>, but a downloadable asset if it has one
        # of our supported extensions. Stylesheets/scripts are deliberately not
        # copied: the stored raw HTML remains useful without mirroring a site.
        if tag.lower() == "a" and attributes.get("href"):
            self.links.append(attributes["href"])
            if is_asset_url(attributes["href"]):
                self.asset_urls.append(attributes["href"])
        if tag.lower() in {"img", "source"}:
            for key in ("src", "srcset"):
                if attributes.get(key):
                    # For srcset, use every candidate URL; descriptors are removed.
                    for item in attributes[key].split(","):
                        self.asset_urls.append(item.strip().split()[0])

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)

    @property
    def title(self) -> str:
        return " ".join(" ".join(self.title_parts).split())


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


def normalize_url(url: str, base_url: str | None = None) -> str | None:
    """Return a stable HTTP(S) URL, removing fragments and tracker parameters."""
    if base_url:
        url = urljoin(base_url, url)
    try:
        parsed = urlsplit(url)
    except ValueError:
        return None
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
        return None
    hostname = parsed.hostname.lower() if parsed.hostname else ""
    try:
        port = f":{parsed.port}" if parsed.port else ""
    except ValueError:
        return None
    netloc = hostname + port
    path = re.sub(r"/{2,}", "/", unquote(parsed.path or "/"))
    # Preserve meaningful query parameters but discard common analytics ones.
    query = [(key, value) for key, value in parse_qsl(parsed.query, keep_blank_values=True)
             if not key.lower().startswith(("utm_", "fbclid", "gclid"))]
    return urlunsplit((parsed.scheme.lower(), netloc, path, "&".join(f"{k}={v}" for k, v in query), ""))


def same_domain(url: str, root_url: str) -> bool:
    """Require the exact host; docs.example.com and example.com stay separate."""
    return urlsplit(url).hostname == urlsplit(root_url).hostname


def is_child_url(url: str, root_url: str) -> bool:
    """Allow only the root page and descendants below its URL path.

    For ROOT_URL ``https://docs.inventree.org/en/stable/``, this permits
    ``/en/stable/part/`` but rejects same-host siblings such as ``/en/latest/``.
    """
    candidate = urlsplit(url)
    root = urlsplit(root_url)
    if (candidate.scheme, candidate.netloc) != (root.scheme, root.netloc):
        return False
    root_path = root.path.rstrip("/") or "/"
    return candidate.path == root_path or candidate.path.startswith(root_path.rstrip("/") + "/")


def is_asset_url(url: str) -> bool:
    return Path(urlsplit(url).path.lower()).suffix in ASSET_EXTENSIONS


def is_image_url(url: str) -> bool:
    return Path(urlsplit(url).path.lower()).suffix in IMAGE_EXTENSIONS


def deduplicate(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(values))


def url_output_stem(url: str) -> Path:
    """Map a URL to a safe, readable relative path without an output suffix."""
    parsed = urlsplit(url)
    parts = [re.sub(r"[^A-Za-z0-9._-]+", "-", unquote(piece)).strip(".-") or "_"
             for piece in parsed.path.split("/") if piece]
    if not parts:
        parts = ["index"]
    elif parsed.path.endswith("/"):
        parts.append("index")
    # A query represents a distinct resource. Avoid a silent collision.
    if parsed.query:
        parts[-1] += "--" + hashlib.sha256(parsed.query.encode()).hexdigest()[:10]
    return Path(*parts)


def page_paths(url: str) -> dict[str, Path]:
    stem = url_output_stem(url)
    return {
        "markdown": OUTPUT_DIR / "markdown" / stem.with_suffix(".md"),
        "html": OUTPUT_DIR / "html" / stem.with_suffix(".html"),
        "metadata": OUTPUT_DIR / "metadata" / stem.with_suffix(".json"),
        "images_dir": OUTPUT_DIR / "images" / stem,
        "attachments_dir": OUTPUT_DIR / "attachments" / stem,
    }


def output_relative(path: Path) -> str:
    return path.relative_to(OUTPUT_DIR).as_posix()


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def as_markdown(result: Any) -> str:
    """Crawl4AI 0.9 returns MarkdownGenerationResult in some configurations."""
    value = getattr(result, "markdown", "") or ""
    if isinstance(value, str):
        return value
    return getattr(value, "raw_markdown", None) or getattr(value, "markdown", None) or str(value)


def result_html(result: Any) -> str:
    return getattr(result, "html", None) or getattr(result, "cleaned_html", None) or ""


def result_links(result: Any, page_url: str, root_url: str) -> list[str]:
    """Read Crawl4AI's links field, then filter it consistently with HTML links."""
    candidates: list[str] = []
    links = getattr(result, "links", None) or {}
    groups = links.values() if isinstance(links, dict) else links
    for group in groups:
        if not isinstance(group, list):
            continue
        for entry in group:
            href = entry.get("href") if isinstance(entry, dict) else entry
            if isinstance(href, str):
                candidates.append(href)
    normalized = [normalize_url(value, page_url) for value in candidates]
    return deduplicate(value for value in normalized if value and is_child_url(value, root_url) and not is_asset_url(value))


def download_binary(url: str, destination: Path) -> tuple[bool, str | None]:
    """Download one asset atomically enough to avoid corrupt partial files."""
    try:
        request = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            data = response.read()
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        return True, None
    except (HTTPError, URLError, OSError, ValueError) as exc:
        return False, str(exc)


async def download_assets(page_url: str, raw_assets: Iterable[str], images_dir: Path,
                          attachments_dir: Path, semaphore: asyncio.Semaphore) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    """Download supported page assets, recording failures without stopping a crawl."""
    urls = []
    for raw_url in raw_assets:
        absolute = normalize_url(raw_url, page_url)
        if absolute and is_asset_url(absolute):
            urls.append(absolute)
    urls = deduplicate(urls)

    async def one(asset_url: str) -> tuple[dict[str, str] | None, dict[str, str] | None]:
        suffix = Path(urlsplit(asset_url).path).suffix.lower() or ".bin"
        base_name = Path(unquote(urlsplit(asset_url).path)).name or "asset"
        base_name = re.sub(r"[^A-Za-z0-9._-]+", "-", base_name).strip(".-") or "asset"
        if not base_name.lower().endswith(suffix):
            base_name += suffix
        name = f"{hashlib.sha256(asset_url.encode()).hexdigest()[:10]}-{base_name}"
        destination = (images_dir if is_image_url(asset_url) else attachments_dir) / name
        async with semaphore:
            success, error = await asyncio.to_thread(download_binary, asset_url, destination)
        if success:
            record = {"url": asset_url, "local_path": output_relative(destination)}
            return (record, None) if is_image_url(asset_url) else (None, record)
        return None, {"url": asset_url, "error": error or "unknown asset download error"}

    results = await asyncio.gather(*(one(url) for url in urls))
    images = [image for image, result in results if image]
    attachments = [attachment for image, attachment in results if attachment and "local_path" in attachment]
    failures = [failure for image, failure in results if failure and "error" in failure]
    return images, attachments, failures


def prepare_output() -> None:
    # Existing output is preserved. Files written in this run overwrite only
    # matching URL paths, which makes re-runs and interrupted-crawl recovery easy.
    for directory in ("markdown", "html", "metadata", "images", "attachments"):
        (OUTPUT_DIR / directory).mkdir(parents=True, exist_ok=True)


async def save_result(result: Any, index: int, root_url: str, pages: dict[str, dict[str, Any]],
                      failures: list[dict[str, str]], asset_failures: list[dict[str, str]],
                      asset_semaphore: asyncio.Semaphore) -> None:
    """Persist one streamed Crawl4AI result without allowing slow assets to stall the crawl."""
    page_url = normalize_url(getattr(result, "url", ""))
    if not page_url:
        failures.append({"url": "unknown", "error": "Crawl result did not provide a valid URL"})
        return
    if not is_child_url(page_url, root_url):
        logging.info("[%s] Skipped outside root path: %s", index, page_url)
        return
    if not getattr(result, "success", True):
        error = str(getattr(result, "error_message", "Crawl4AI returned success=False"))
        failures.append({"url": page_url, "error": error})
        logging.warning("[%s] Failed: %s", index, page_url)
        return

    html = result_html(result)
    parser = PageHTMLParser()
    try:
        parser.feed(html)
    except Exception as exc:
        logging.warning("Could not fully parse HTML for %s: %s", page_url, exc)
    child_links = deduplicate(result_links(result, page_url, root_url) + [
        link for link in (normalize_url(value, page_url) for value in parser.links)
        if link and is_child_url(link, root_url) and not is_asset_url(link)
    ])
    paths = page_paths(page_url)
    write_text(paths["markdown"], as_markdown(result))
    write_text(paths["html"], html)
    try:
        images, attachments, failed_assets = await asyncio.wait_for(
            download_assets(page_url, parser.asset_urls, paths["images_dir"], paths["attachments_dir"], asset_semaphore),
            timeout=ASSET_BATCH_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        #######
        logging.warning(
            "Crawl attempt %s/3 timed out.",
            attempt,
        )

        if attempt == 3:

            message = (
                f"Crawl reached its "
                f"{CRAWL_TIMEOUT_SECONDS}-second timeout."
            )

            failures.append(

                {

                    "url": root_url,

                    "error": message,

                }

            )

            raise RuntimeError(
                message,
            )

        await asyncio.sleep(
            attempt * 2,
            )
        #######
    asset_failures.extend({"page_url": page_url, **item} for item in failed_assets)

    metadata = getattr(result, "metadata", None) or {}
    title = parser.title or str(metadata.get("title") or "")
    pages[page_url] = {
        "url": page_url,
        "title": title,
        "depth": int(metadata.get("depth", 0) or 0),
        "parent_url": None,  # populated from graph edges after all pages are known
        "child_links": child_links,
        "markdown_path": output_relative(paths["markdown"]),
        "html_path": output_relative(paths["html"]),
        "metadata_path": output_relative(paths["metadata"]),
        "images": images,
        "attachments": attachments,
        "asset_download_failures": failed_assets,
    }
    logging.info("[%s] Saved depth %s: %s", index, pages[page_url]["depth"], page_url)


async def crawl(
    root_url: str,
    output_dir: Path,
) -> bool:
    global OUTPUT_DIR
    OUTPUT_DIR = output_dir / "scrape_output"
    OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
    )
    configure_logging()
    prepare_output()
    started = time.monotonic()
    started_at = datetime.now(timezone.utc).isoformat()
    root_url = normalize_url(root_url)
    if not root_url:
        raise ValueError(f"ROOT_URL must be an absolute http(s) URL: {ROOT_URL!r}")

    logging.info("Starting BFS crawl: %s (max depth=%s, max pages=%s)", root_url, MAX_DEPTH, MAX_PAGES)
    browser_config = BrowserConfig(headless=True, verbose=False)
    # Enforce scope within Crawl4AI itself, rather than merely discarding pages
    # after the browser has already fetched them.
    root_pattern = root_url.rstrip("/")
    root_filter = FilterChain([URLPatternFilter(patterns=[root_pattern, f"{root_pattern}/*"])])
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        deep_crawl_strategy=BFSDeepCrawlStrategy(
            max_depth=MAX_DEPTH,
            max_pages=MAX_PAGES,
            include_external=False,
            filter_chain=root_filter,
        ),
        page_timeout=PAGE_TIMEOUT_MS,
        max_retries=1,
        stream=True,
        verbose=False,
    )

    pages: dict[str, dict[str, Any]] = {}
    failures: list[dict[str, str]] = []
    asset_failures: list[dict[str, str]] = []
    asset_semaphore = asyncio.Semaphore(MAX_ASSET_CONCURRENCY)

    async with AsyncWebCrawler(config=browser_config) as crawler:
        async def consume_results() -> None:
            """Stream results so saved pages are visible immediately during a long crawl."""
            result_stream = await crawler.arun(url=root_url, config=run_config)
            if hasattr(result_stream, "__aiter__"):
                index = 0
                async for result in result_stream:
                    index += 1
                    await save_result(result, index, root_url, pages, failures, asset_failures, asset_semaphore)
            else:
                # Kept for unexpected compatible builds that ignore stream=True.
                results = result_stream if isinstance(result_stream, list) else [result_stream]
                for index, result in enumerate(results, start=1):
                    await save_result(result, index, root_url, pages, failures, asset_failures, asset_semaphore)
####===================
        # for attempt in range(1, 4):
        #     try:
        #         await asyncio.wait_for(consume_results(), timeout=CRAWL_TIMEOUT_SECONDS)
        #         ########
        #         message = f"crawl reached its {CRAWL_TIMEOUT_SECONDS}-second time limit"
        #         failures.append({"url": root_url, "error": message})
        #         logging.warning("%s; writing the %s pages already saved", message, len(pages))
        #         break
        #         ########
        #     except Exception as exc:
        #         #######
        #         logging.warning(
        #             "Crawl attempt %s/3 failed : %s",
        #             attempt,
        #             exc,
        #         )

        #         if attempt == 3:

        #             failures.append(

        #                 {

        #                     "url": root_url,

        #                     "error": str(exc),

        #                 }

        #             )

        #             raise

        #         await asyncio.sleep(
        #             attempt * 2,
        #         )
                #######


######
        for attempt in range(1, 4):
            try:
                await asyncio.wait_for(consume_results(), timeout=CRAWL_TIMEOUT_SECONDS)
                break  # Clean exit on success
            except asyncio.TimeoutError:
                message = f"crawl reached its {CRAWL_TIMEOUT_SECONDS}-second time limit on attempt {attempt}"
                failures.append({"url": root_url, "error": message})
                logging.warning(message)
                if attempt == 3:
                    raise
            except Exception as exc:
                logging.warning("Crawl attempt %s/3 failed: %s", attempt, exc)
                if attempt == 3:
                    failures.append({"url": root_url, "error": str(exc)})
                    raise
                await asyncio.sleep(attempt * 2)

#####
####===================
    # Derive a reproducible parent: among incoming links, choose a shallower page
    # first, then lexical URL. This handles results where Crawl4AI only records depth.
    incoming: dict[str, list[str]] = defaultdict(list)
    edges: list[dict[str, str]] = []
    for source, page in pages.items():
        for target in page["child_links"]:
            if target in pages:
                incoming[target].append(source)
                edges.append({"source": source, "target": target})
    for page_url, page in pages.items():
        candidates = incoming.get(page_url, [])
        if candidates:
            page["parent_url"] = min(candidates, key=lambda candidate: (pages[candidate]["depth"], candidate))
        write_text(page_paths(page_url)["metadata"], json.dumps(page, ensure_ascii=False, indent=2) + "\n")

    elapsed_seconds = round(time.monotonic() - started, 2)
    graph = {
        "root_url": root_url,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "nodes": [{"url": url, "title": page["title"], "depth": page["depth"], "parent_url": page["parent_url"]}
                  for url, page in sorted(pages.items())],
        "edges": sorted(edges, key=lambda edge: (edge["source"], edge["target"])),
    }
    manifest = {
        "root_url": root_url,
        "started_at": started_at,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": elapsed_seconds,
        "configuration": {"max_depth": MAX_DEPTH, "max_pages": MAX_PAGES},
        "pages_crawled": len(pages),
        "assets_downloaded": sum(len(page["images"]) + len(page["attachments"]) for page in pages.values()),
        "failed_pages": failures,
        "failed_asset_downloads": asset_failures,
        "visited_urls": sorted(pages),
    }

####
    documentation = {

        "documentation_url": root_url,

        "generated_at": datetime.now(
            timezone.utc,
        ).isoformat(),

        "pages": []

    }

    for url, page in sorted(
        pages.items(),
    ):

        markdown = ""

        html = ""

        try:

            markdown = (
                OUTPUT_DIR
                / page["markdown_path"]
            ).read_text(
                encoding="utf-8",
            )

        except Exception:
            pass

        try:

            html = (
                OUTPUT_DIR
                / page["html_path"]
            ).read_text(
                encoding="utf-8",
            )

        except Exception:
            pass

        documentation["pages"].append(

            {

                "title": page["title"],

                "url": page["url"],

                "depth": page["depth"],

                "parent_url": page["parent_url"],

                "child_pages": page["child_links"],

                "markdown": markdown,

                "html": html,

                "images": page["images"],

                "attachments": page["attachments"],

            }

        )

    write_text(

        output_dir / "documentation.json",

        json.dumps(

            documentation,

            indent=2,

            ensure_ascii=False,

        ) + "\n",

    )
###


    write_text(OUTPUT_DIR / "graph.json", json.dumps(graph, ensure_ascii=False, indent=2) + "\n")
    write_text(OUTPUT_DIR / "manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

    if not pages:

        raise RuntimeError(
            "Crawler could not download the root documentation. "
            "No pages were successfully crawled."
        )

    logging.info("Finished: %s pages, %s assets, %s page failures in %.2fs",
                 manifest["pages_crawled"], manifest["assets_downloaded"], len(failures), elapsed_seconds)
    logging.info("Output: %s", OUTPUT_DIR)
    return True

if __name__ == "__main__":
    try:
        asyncio.run(
            crawl(
                root_url=DEFAULT_ROOT_URL,
                output_dir=DEFAULT_OUTPUT_DIR,
                )
        )
    except KeyboardInterrupt:
        logging.warning("Crawl cancelled by user; completed pages remain under %s", OUTPUT_DIR)
        sys.exit(130)
    except Exception as exc:
        logging.error("Crawl stopped: %s", exc)
        sys.exit(1)
