"""
demo_test.py - Quick demo to test your setup WITHOUT Neo4j or API keys.
Run this first to verify Python environment is working.

Usage:
    python demo_test.py
"""
import sys
import os

print("\n" + "="*55)
print("  Agentic RAG — Environment Check")
print("="*55)

# ── Python version ────────────────────────────────────────────
pv = sys.version_info
ok = "✔" if pv.major == 3 and pv.minor >= 10 else "✘"
print(f"\n[{ok}] Python version: {pv.major}.{pv.minor}.{pv.micro}  (need 3.10+)")

# ── Check packages ─────────────────────────────────────────────
packages = {
    "openai":    "openai",
    "arxiv":     "arxiv",
    "fitz":      "PyMuPDF",
    "neo4j":     "neo4j",
    "langchain": "langchain",
    "rich":      "rich",
    "jinja2":    "jinja2",
    "dotenv":    "python-dotenv",
    "tqdm":      "tqdm",
    "requests":  "requests",
}

print("\nPackage checks:")
all_ok = True
for import_name, pip_name in packages.items():
    try:
        __import__(import_name)
        print(f"  [✔] {pip_name}")
    except ImportError:
        print(f"  [✘] {pip_name}  →  run: pip install {pip_name}")
        all_ok = False

# ── Check .env ────────────────────────────────────────────────
print("\n.env file:")
if os.path.exists(".env"):
    print("  [✔] .env file found")
    from dotenv import load_dotenv
    load_dotenv()
    groq_key = os.getenv("GROQ_API_KEY", "")
    neo4j_pass = os.getenv("NEO4J_PASSWORD", "")
    if groq_key:
        print("  [✔] GROQ_API_KEY is set")
    else:
        print("  [!] GROQ_API_KEY not set — open .env and add your key")
    if neo4j_pass and neo4j_pass != "your-neo4j-password":
        print("  [✔] NEO4J_PASSWORD is set")
    else:
        print("  [!] NEO4J_PASSWORD not set — needed for GraphRAG agent")
else:
    print("  [✘] .env not found — run: cp .env.example .env")
    all_ok = False

# ── Check sample_docs ──────────────────────────────────────────
print("\nSample documents:")
docs = [f for f in os.listdir("sample_docs") if f.endswith((".pdf", ".txt"))]
if docs:
    for d in docs:
        print(f"  [✔] sample_docs/{d}")
else:
    print("  [!] No docs found in sample_docs/ — add .pdf or .txt files")

# ── Demo: ArXiv search (no key needed) ────────────────────────
print("\nArXiv connectivity test:")
try:
    import arxiv
    client = arxiv.Client()
    search = arxiv.Search(query="retrieval augmented generation", max_results=2)
    results = list(client.results(search))
    if results:
        print(f"  [✔] ArXiv reachable — found: '{results[0].title[:50]}…'")
    else:
        print("  [!] ArXiv returned no results (check internet)")
except Exception as e:
    print(f"  [✘] ArXiv error: {e}")

# ── Summary ────────────────────────────────────────────────────
print("\n" + "="*55)
if all_ok:
    print("  ✔  All checks passed! Run: python main.py")
else:
    print("  ✘  Some issues found. Fix them above, then run: python main.py")
print("="*55 + "\n")
