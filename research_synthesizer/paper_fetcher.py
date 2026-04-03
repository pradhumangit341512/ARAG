"""
research_synthesizer/paper_fetcher.py
Search ArXiv (free, no key) and optionally Google Scholar via Serper API.
Downloads PDFs and returns metadata.
"""
import os
import time
import arxiv
import requests
import config
from rich.console import Console
from tqdm import tqdm

console = Console()


# ── ArXiv ─────────────────────────────────────────────────────────────────────

def search_arxiv(topic: str, max_results: int = 10) -> list[dict]:
    """Search ArXiv and return paper metadata."""
    console.print(f"  [cyan]Searching ArXiv for:[/cyan] {topic}")
    client = arxiv.Client()
    search = arxiv.Search(
        query=topic,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
    )
    papers = []
    for result in client.results(search):
        papers.append({
            "title":    result.title,
            "authors":  [a.name for a in result.authors],
            "abstract": result.summary,
            "url":      result.entry_id,
            "pdf_url":  result.pdf_url,
            "published": str(result.published.date()),
            "source":   "arxiv",
        })
    console.print(f"  Found [green]{len(papers)}[/green] papers on ArXiv.")
    return papers


# ── Google Scholar via Serper ─────────────────────────────────────────────────

def search_google_scholar(topic: str, max_results: int = 5) -> list[dict]:
    """Search Google Scholar using Serper API."""
    if not config.SERPER_API_KEY:
        console.print("  [yellow]⚠ No SERPER_API_KEY set — skipping Google Scholar.[/yellow]")
        return []

    console.print(f"  [cyan]Searching Google Scholar for:[/cyan] {topic}")
    headers = {"X-API-KEY": config.SERPER_API_KEY, "Content-Type": "application/json"}
    payload = {"q": f"{topic} filetype:pdf", "num": max_results, "gl": "us"}

    try:
        response = requests.post(
            "https://google.serper.dev/search", json=payload, headers=headers, timeout=15
        )
        response.raise_for_status()
        results = response.json().get("organic", [])
        papers  = []
        for r in results:
            papers.append({
                "title":    r.get("title", ""),
                "abstract": r.get("snippet", ""),
                "url":      r.get("link", ""),
                "pdf_url":  r.get("link", "") if r.get("link", "").endswith(".pdf") else None,
                "authors":  [],
                "published": "",
                "source":   "google_scholar",
            })
        console.print(f"  Found [green]{len(papers)}[/green] results from Google Scholar.")
        return papers
    except Exception as e:
        console.print(f"  [red]Serper API error:[/red] {e}")
        return []


# ── PDF Downloader ────────────────────────────────────────────────────────────

def download_pdf(paper: dict, save_dir: str) -> str | None:
    """Download a paper's PDF. Returns local filepath or None."""
    pdf_url = paper.get("pdf_url")
    if not pdf_url:
        return None

    # Safe filename from title
    safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in paper["title"])[:60]
    filepath  = os.path.join(save_dir, f"{safe_name}.pdf")

    if os.path.exists(filepath):
        console.print(f"    [dim]Already downloaded: {safe_name}.pdf[/dim]")
        return filepath

    try:
        resp = requests.get(pdf_url, timeout=30, stream=True)
        resp.raise_for_status()
        with open(filepath, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        console.print(f"    [green]✔[/green] Downloaded: {safe_name}.pdf")
        time.sleep(1)   # be polite
        return filepath
    except Exception as e:
        console.print(f"    [red]✘ Failed:[/red] {e}")
        return None


def fetch_top_papers(topic: str, save_dir: str, max_papers: int = 5) -> list[dict]:
    """
    Combined pipeline:
    1. Search ArXiv + Google Scholar
    2. Deduplicate by title
    3. Download PDFs for the top N
    4. Return enriched metadata list
    """
    os.makedirs(save_dir, exist_ok=True)

    # Gather candidates
    arxiv_papers  = search_arxiv(topic, max_results=config.ARXIV_SEARCH_RESULTS)
    scholar_papers = search_google_scholar(topic, max_results=5)

    all_papers = arxiv_papers + scholar_papers

    # Deduplicate (case-insensitive title match)
    seen, unique = set(), []
    for p in all_papers:
        key = p["title"].lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append(p)

    top = unique[:max_papers]
    console.print(f"\n  [bold]Downloading top {len(top)} papers…[/bold]")

    for paper in tqdm(top, desc="  Downloading"):
        local_path = download_pdf(paper, save_dir)
        paper["local_pdf"] = local_path

    return top
