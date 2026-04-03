"""
main.py — Agentic RAG: CLI Entry Point
=======================================
Two agents in one interactive menu:
  1. GraphRAG for Technical Documentation  (Neo4j + LangChain + LLM)
  2. Autonomous Research Paper Synthesizer (ArXiv + PyMuPDF + LaTeX)
"""
import os
import sys
from rich.console import Console
from rich.panel   import Panel
from rich.table   import Table
from rich         import box

console = Console()

# ── Banner ────────────────────────────────────────────────────────────────────

BANNER = """
[bold cyan]
 █████╗  ██████╗ ███████╗███╗   ██╗████████╗██╗ ██████╗    ██████╗  █████╗  ██████╗
██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝██║██╔════╝    ██╔══██╗██╔══██╗██╔════╝
███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   ██║██║         ██████╔╝███████║██║  ███╗
██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   ██║██║         ██╔══██╗██╔══██║██║   ██║
██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   ██║╚██████╗    ██║  ██║██║  ██║╚██████╔╝
╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝ ╚═════╝    ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝
[/bold cyan]
[bold white]         Agentic RAG System — Reasoning over Data[/bold white]
[dim]         College Project | Neo4j · LangChain · ArXiv · LaTeX[/dim]
"""


def print_banner():
    console.print(BANNER)


def print_menu():
    table = Table(box=box.ROUNDED, show_header=False, border_style="cyan")
    table.add_column("Option", style="bold yellow", width=8)
    table.add_column("Agent",  style="white")
    table.add_column("Description", style="dim")

    table.add_row("  [1]", "🕸  GraphRAG Agent",
                  "Build Knowledge Graph from docs & answer impact-analysis questions")
    table.add_row("  [2]", "📚  Research Synthesizer",
                  "Search ArXiv, download papers, write LaTeX literature review")
    table.add_row("  [q]", "🚪  Quit", "Exit the program")

    console.print(Panel(table, title="[bold cyan]SELECT AN AGENT[/bold cyan]", border_style="cyan"))


# ── Agent 1: GraphRAG ─────────────────────────────────────────────────────────

def run_graph_rag():
    console.print(Panel(
        "[bold]Agent 1: GraphRAG for Technical Documentation[/bold]\n"
        "Builds a Knowledge Graph from your docs in [cyan]sample_docs/[/cyan] "
        "and answers impact-analysis questions.",
        border_style="green",
    ))

    # Check API key
    import config
    if not config.GROQ_API_KEY:
        console.print("[red]✘ GROQ_API_KEY not set in .env — please configure it first.[/red]")
        return

    # Import here to avoid heavy imports on startup
    from graph_rag import KnowledgeGraph, load_documents, build_graph_from_chunks, GraphQueryEngine

    # --- Connect to Neo4j ---
    try:
        kg = KnowledgeGraph()
    except Exception as e:
        console.print(f"[red]✘ Neo4j connection failed:[/red] {e}")
        console.print("[yellow]  Tip: Run Neo4j locally with Docker:[/yellow]")
        console.print("  [dim]docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j[/dim]")
        return

    console.print("\n[bold]Step 1:[/bold] Loading documents from [cyan]sample_docs/[/cyan]")
    chunks = load_documents(config.SAMPLE_DOCS_DIR)
    if not chunks:
        console.print("[yellow]⚠ No documents found. Add .pdf or .txt files to sample_docs/[/yellow]")
        kg.close()
        return
    console.print(f"  Loaded [green]{len(chunks)}[/green] text chunks.")

    # Ask if user wants to rebuild graph
    rebuild = console.input("\n[bold]Rebuild the Knowledge Graph from scratch? (y/n):[/bold] ").strip().lower()
    if rebuild == "y":
        kg.clear_graph()
        console.print("\n[bold]Step 2:[/bold] Building Knowledge Graph (this may take a minute)…")
        nodes, edges = build_graph_from_chunks(chunks, kg.driver)
        console.print(f"\n  [green]✔ Graph built:[/green] {nodes} nodes, {edges} edges")

    # Show stats
    stats = kg.get_stats()
    console.print(f"\n  Graph stats → [cyan]{stats['nodes']} nodes, {stats['edges']} edges[/cyan]")

    # --- Q&A Loop ---
    engine = GraphQueryEngine(kg)
    console.print(Panel(
        "[bold]Knowledge Graph is ready![/bold] Ask questions like:\n"
        "• [italic]If I change UserAuthModule access modifier, what is affected?[/italic]\n"
        "• [italic]What modules depend on DatabaseConnectionPool?[/italic]\n"
        "• [italic]What does TokenService call?[/italic]\n"
        "Type [bold yellow]'back'[/bold yellow] to return to main menu.",
        border_style="green",
    ))

    while True:
        question = console.input("\n[bold cyan]Your Question:[/bold cyan] ").strip()
        if question.lower() in ("back", "exit", "q"):
            break
        if not question:
            continue
        answer = engine.query(question)
        console.print(Panel(answer, title="[bold green]🤖 Agent Answer[/bold green]", border_style="green"))

    kg.close()


# ── Agent 2: Research Synthesizer ────────────────────────────────────────────

def run_research_synthesizer():
    console.print(Panel(
        "[bold]Agent 2: Autonomous Research Paper Synthesizer[/bold]\n"
        "Searches ArXiv, downloads top papers, reads them with PyMuPDF,\n"
        "and writes a structured literature review in [cyan]LaTeX[/cyan].",
        border_style="magenta",
    ))

    import config
    if not config.GROQ_API_KEY:
        console.print("[red]✘ GROQ_API_KEY not set in .env[/red]")
        return

    from research_synthesizer import (
        fetch_top_papers, read_papers, run_synthesis_pipeline,
        synthesize_literature_review, write_latex,
    )

    topic = console.input(
        "\n[bold cyan]Enter research topic[/bold cyan] "
        "[dim](e.g. 'Retrieval Augmented Generation 2024')[/dim]: "
    ).strip()
    if not topic:
        return

    n_papers_str = console.input(
        f"[bold cyan]How many papers to analyze?[/bold cyan] [dim](default: {config.MAX_PAPERS})[/dim]: "
    ).strip()
    n_papers = int(n_papers_str) if n_papers_str.isdigit() else config.MAX_PAPERS

    papers_dir = os.path.join(config.OUTPUT_DIR, "papers")

    # --- Step 1: Fetch papers ---
    console.print(f"\n[bold]Step 1:[/bold] Searching & downloading papers…")
    papers = fetch_top_papers(topic, save_dir=papers_dir, max_papers=n_papers)

    if not papers:
        console.print("[red]✘ No papers found.[/red]")
        return

    # --- Step 2: Read PDFs ---
    console.print(f"\n[bold]Step 2:[/bold] Reading PDFs with PyMuPDF…")
    papers = read_papers(papers)

    # --- Step 3: Analyze each paper ---
    console.print(f"\n[bold]Step 3:[/bold] Analyzing papers with LLM…")
    papers = run_synthesis_pipeline(topic, papers)

    # --- Step 4: Synthesize review ---
    console.print(f"\n[bold]Step 4:[/bold] Synthesizing literature review…")
    synthesis = synthesize_literature_review(topic, papers)
    console.print(Panel(synthesis[:800] + "…", title="[bold]Review Preview[/bold]", border_style="magenta"))

    # --- Step 5: Write LaTeX ---
    console.print(f"\n[bold]Step 5:[/bold] Writing LaTeX document…")
    tex_path = write_latex(topic, papers, synthesis, config.OUTPUT_DIR)

    console.print(Panel(
        f"[bold green]✔ Literature review complete![/bold green]\n\n"
        f"  [cyan]LaTeX file:[/cyan] {tex_path}\n\n"
        f"  [bold]To compile to PDF:[/bold]\n"
        f"  [dim]cd output && pdflatex {os.path.basename(tex_path)}[/dim]\n\n"
        f"  [bold]Or use Overleaf:[/bold]\n"
        f"  [dim]Upload the .tex file to https://www.overleaf.com[/dim]",
        border_style="green",
    ))


# ── Entry Point ───────────────────────────────────────────────────────────────

def main():
    print_banner()

    while True:
        print_menu()
        choice = console.input("[bold]Enter choice:[/bold] ").strip().lower()

        if choice == "1":
            run_graph_rag()
        elif choice == "2":
            run_research_synthesizer()
        elif choice in ("q", "quit", "exit"):
            console.print("\n[cyan]Goodbye! 👋[/cyan]\n")
            sys.exit(0)
        else:
            console.print("[red]Invalid choice. Please enter 1, 2, or q.[/red]")


if __name__ == "__main__":
    main()
