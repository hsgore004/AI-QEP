import sys
import os
import asyncio
import json
from pathlib import Path
import httpx
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

# Configurable interaction limit
MAX_INTERACTION_STEPS = 5
CLICK_TARGET_SELECTOR = "button.subpage-trigger"
SESSION_ID = "interactive_site_session"

# File extensions we want to catch and download as artifacts
DOCUMENT_EXTENSIONS = ('.pdf', '.docx', '.xlsx', '.xls', '.csv', '.pptx', '.zip')

def parse_arguments():
    """Parses and validates command line arguments."""
    if len(sys.argv) < 3:
        print("\n❌ Error: Missing arguments.")
        print("Usage: python test_crawl4ai.py <URL> <LOCAL_FOLDER_PATH>")
        print("Example: python test_crawl4ai.py https://inventree.org ./output_data\n")
        sys.exit(1)
        
    url = sys.argv[1]
    base_dir = Path(sys.argv[2]).resolve()
    
    # Create sub-folders for structured storage
    images_dir = base_dir / "images"
    docs_dir = base_dir / "documents"
    
    images_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    return url, base_dir, images_dir, docs_dir

async def download_file(file_url: str, save_dir: Path, client: httpx.AsyncClient) -> str:
    """Downloads an individual file (image or doc) and returns its relative local path."""
    if not file_url or not file_url.startswith(("http://", "https://")):
        return file_url
        
    try:
        # Clean file name extraction
        clean_name = file_url.split("/")[-1].split("?")[0]
        if not clean_name:
            clean_name = f"file_{hash(file_url)}"
            
        local_path = save_dir / clean_name
        
        # Stream content in case of large PDF/documents
        async with client.stream("GET", file_url, timeout=15.0, follow_redirects=True) as response:
            if response.status_code == 200:
                with open(local_path, "wb") as f:
                    async for chunk in response.aiter_bytes():
                        f.write(chunk)
                # Return string representing local path relative to current runtime path
                return str(local_path)
    except Exception as e:
        print(f"⚠️ Failed to download file {file_url}: {e}")
        
    return file_url

async def process_page_data(result, img_dir: Path, doc_dir: Path, client: httpx.AsyncClient) -> dict:
    """Extracts markdown text, identifies documents, and downloads all media artifacts."""
    if not result or not result.success:
        return {"text": "", "images": [], "documents": [], "subpages": {}}
        
    # 1. Collect and download Images
    raw_images = [img.get("src") for img in result.media.get("images", [])] if result.media else []
    img_tasks = [download_file(url, img_dir, client) for url in raw_images if url]
    local_images = await asyncio.gather(*img_tasks)
    
    # 2. Extract Document Links (PDFs, Excel, etc.)
    raw_docs = []
    if result.links and "internal" in result.links:
        for link in result.links["internal"]:
            href = link.get("href", "")
            if href.lower().endswith(DOCUMENT_EXTENSIONS):
                raw_docs.append(href)
                
    doc_tasks = [download_file(url, doc_dir, client) for url in raw_docs if url]
    local_docs = await asyncio.gather(*doc_tasks)
        
    return {
        "text": result.markdown or "",
        "images": local_images,
        "documents": local_docs,
        "subpages": {}
    }

async def main():
    target_url, output_dir, images_dir, docs_dir = parse_arguments()
    site_hierarchy = {}
    
    browser_config = BrowserConfig(headless=True, verbose=True)

    print(f"\n📂 Initializing download folders under: {output_dir}")
    async with httpx.AsyncClient() as http_client:
        async with AsyncWebCrawler(config=browser_config) as crawler:
            
            # --- STEP 1: Main Parent Page ---
            print(f"🌐 Loading main page: {target_url}...")
            main_config = CrawlerRunConfig(session_id=SESSION_ID, cache_mode=CacheMode.BYPASS)
            main_result = await crawler.arun(url=target_url, config=main_config)
            
            site_hierarchy[target_url] = await process_page_data(main_result, images_dir, docs_dir, http_client)

            # --- STEP 2: Interactive Subpages ---
            for i in range(MAX_INTERACTION_STEPS):
                subpage_name = f"Subpage_Action_{i + 1}"
                print(f"🖱️ Triggering click sequence target index #{i}...")

                click_js = (
                    f"const targets = document.querySelectorAll('{CLICK_TARGET_SELECTOR}'); "
                    f"if (targets.length > {i}) {{ targets[{i}].click(); }}"
                )

                subpage_config = CrawlerRunConfig(
                    session_id=SESSION_ID,
                    js_code=click_js,
                    js_only=True, 
                    wait_for="timeout:2000", 
                    cache_mode=CacheMode.BYPASS
                )

                sub_result = await crawler.arun(url=target_url, config=subpage_config)
                site_hierarchy[target_url]["subpages"][subpage_name] = await process_page_data(
                    sub_result, images_dir, docs_dir, http_client
                )

    # Save final data dictionary mapping file inside target runtime directory
    json_path = output_dir / "site_data.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(site_hierarchy, f, indent=4)
        
    print(f"\n✅ Execution Finished successfully!")
    print(f"📊 Layout Schema saved: {json_path}")
    print(f"🖼️ Images saved inside: {images_dir}")
    print(f"📄 PDFs / Files saved inside: {docs_dir}\n")

if __name__ == "__main__":
    asyncio.run(main())
