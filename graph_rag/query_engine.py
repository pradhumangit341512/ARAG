"""
graph_rag/query_engine.py
Natural-language query engine that translates user questions into
graph traversals and then synthesizes a final answer with the LLM.
"""
import re
from utils.llm_client import chat, chat_messages
from graph_rag.knowledge_graph import KnowledgeGraph
from rich.console import Console

console = Console()

# ── Intent detection ──────────────────────────────────────────────────────────

INTENT_SYSTEM = """You are a query parser for a technical Knowledge Graph.
Given a user question, extract:
1. intent: "impact_analysis" | "find_entity" | "get_neighbors" | "general_question"
2. entity: the main technical entity being asked about (class name, module, function, etc.)

Return ONLY JSON. Example:
{"intent": "impact_analysis", "entity": "UserAuthModule"}"""


def detect_intent(question: str) -> dict:
    raw = chat(question, system=INTENT_SYSTEM, temperature=0.0)
    raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
    try:
        import json
        return json.loads(raw)
    except Exception:
        return {"intent": "general_question", "entity": ""}


# ── Answer synthesis ──────────────────────────────────────────────────────────

SYNTHESIS_SYSTEM = """You are an expert software architect and technical documentation analyst.
You have access to a Knowledge Graph of technical relationships.
Use the graph context below to answer the user's question accurately.
Be specific — mention actual entity names and relationship types from the graph data."""


def synthesize_answer(question: str, graph_context: list[dict], intent: str) -> str:
    context_str = "\n".join(
        [f"- {row}" for row in graph_context[:30]]  # cap to avoid huge prompts
    )
    messages = [
        {"role": "system", "content": SYNTHESIS_SYSTEM},
        {
            "role": "user",
            "content": (
                f"User question: {question}\n\n"
                f"Intent detected: {intent}\n\n"
                f"Graph query results:\n{context_str}\n\n"
                "Please provide a detailed, accurate answer based on the graph data above."
            ),
        },
    ]
    return chat_messages(messages, temperature=0.3)


# ── Main query pipeline ───────────────────────────────────────────────────────

class GraphQueryEngine:
    def __init__(self, kg: KnowledgeGraph):
        self.kg = kg

    def query(self, question: str) -> str:
        console.print(f"\n[bold cyan]🔍 Query:[/bold cyan] {question}")

        # 1. Detect intent and entity
        parsed  = detect_intent(question)
        intent  = parsed.get("intent", "general_question")
        entity  = parsed.get("entity", "")
        console.print(f"  Intent: [yellow]{intent}[/yellow]  Entity: [yellow]{entity}[/yellow]")

        graph_data = []

        # 2. Run appropriate graph query
        if intent == "impact_analysis" and entity:
            # First try exact match, then fuzzy
            results = self.kg.find_impact(entity, depth=3)
            if not results:
                matches = self.kg.find_entity(entity)
                if matches:
                    results = self.kg.find_impact(matches[0]["name"], depth=3)
            graph_data = results

        elif intent == "find_entity" and entity:
            graph_data = self.kg.find_entity(entity)

        elif intent == "get_neighbors" and entity:
            # Try exact then fuzzy
            graph_data = self.kg.get_neighbors(entity)
            if not graph_data:
                matches = self.kg.find_entity(entity)
                if matches:
                    graph_data = self.kg.get_neighbors(matches[0]["name"])

        else:
            # Fallback: broad entity search
            if entity:
                graph_data = self.kg.find_entity(entity)

        console.print(f"  Graph rows returned: [green]{len(graph_data)}[/green]")

        # 3. Synthesize final answer
        answer = synthesize_answer(question, graph_data, intent)
        return answer
