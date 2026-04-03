"""
graph_rag/graph_builder.py
Use an LLM to extract entities and relationships from text chunks,
then store them in Neo4j.
"""
import json
import re
from utils.llm_client import chat
from rich.console import Console

console = Console()

# ── Prompts ───────────────────────────────────────────────────────────────────

EXTRACTION_SYSTEM = """You are a Knowledge Graph expert specializing in technical documentation.
Extract entities (classes, modules, functions, variables, APIs, concepts) and their relationships.
Return ONLY valid JSON with no extra text."""

EXTRACTION_PROMPT = """Analyze this technical documentation chunk and extract:
1. ENTITIES: technical components (classes, modules, functions, APIs, concepts)
2. RELATIONSHIPS: how they connect (CALLS, IMPORTS, EXTENDS, USES, DEPENDS_ON, MODIFIES, RETURNS)

Text:
\"\"\"
{text}
\"\"\"

Return ONLY this JSON format (no markdown, no explanation):
{{
  "entities": [
    {{"name": "ClassName", "type": "Class|Module|Function|API|Concept", "description": "brief description"}}
  ],
  "relationships": [
    {{"from": "EntityA", "to": "EntityB", "type": "RELATIONSHIP_TYPE", "description": "why"}}
  ]
}}"""


def extract_graph_elements(text: str) -> dict:
    """Ask the LLM to extract entities and relationships from one text chunk."""
    prompt   = EXTRACTION_PROMPT.format(text=text[:3000])   # token guard
    raw      = chat(prompt, system=EXTRACTION_SYSTEM, temperature=0.1)

    # Strip any accidental markdown fences
    raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        console.print(f"  [yellow]⚠ JSON parse error, skipping chunk.[/yellow]")
        return {"entities": [], "relationships": []}


def build_graph_from_chunks(chunks: list[dict], driver) -> tuple[int, int]:
    """
    Iterate over document chunks, extract graph elements, write to Neo4j.
    Returns (total_nodes, total_edges) counts.
    """
    total_nodes = 0
    total_edges = 0

    with driver.session() as session:
        # Uniqueness constraint
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE")

        for i, chunk in enumerate(chunks, 1):
            console.print(f"  Processing chunk {i}/{len(chunks)} — {chunk['source']} p.{chunk['page']}")
            elements = extract_graph_elements(chunk["text"])

            # --- Nodes ---
            for ent in elements.get("entities", []):
                session.run(
                    """
                    MERGE (e:Entity {name: $name})
                    SET e.type        = $type,
                        e.description = $description,
                        e.source      = $source
                    """,
                    name=ent.get("name", "Unknown"),
                    type=ent.get("type", "Unknown"),
                    description=ent.get("description", ""),
                    source=chunk["source"],
                )
                total_nodes += 1

            # --- Edges ---
            for rel in elements.get("relationships", []):
                session.run(
                    """
                    MERGE (a:Entity {name: $from_name})
                    MERGE (b:Entity {name: $to_name})
                    MERGE (a)-[r:RELATES {type: $rel_type}]->(b)
                    SET r.description = $desc
                    """,
                    from_name=rel.get("from", ""),
                    to_name=rel.get("to", ""),
                    rel_type=rel.get("type", "RELATED_TO"),
                    desc=rel.get("description", ""),
                )
                total_edges += 1

    return total_nodes, total_edges
