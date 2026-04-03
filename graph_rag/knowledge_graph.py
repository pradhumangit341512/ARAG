"""
graph_rag/knowledge_graph.py
Neo4j connection manager and graph query helpers.
"""
from neo4j import GraphDatabase
import config
from rich.console import Console

console = Console()


class KnowledgeGraph:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            config.NEO4J_URI,
            auth=(config.NEO4J_USERNAME, config.NEO4J_PASSWORD),
        )
        console.print(f"[green]✔ Connected to Neo4j:[/green] {config.NEO4J_URI}")

    def close(self):
        self.driver.close()

    # ── Retrieval helpers ──────────────────────────────────────────────────────

    def find_entity(self, name: str) -> list[dict]:
        """Fuzzy find an entity by name (case-insensitive contains)."""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (e:Entity)
                WHERE toLower(e.name) CONTAINS toLower($name)
                RETURN e.name AS name, e.type AS type, e.description AS description
                LIMIT 10
                """,
                name=name,
            )
            return [dict(r) for r in result]

    def find_impact(self, entity_name: str, depth: int = 3) -> list[dict]:
        """
        Impact analysis: what other entities are reachable from this one?
        Answers: "If I change X, what else is affected?"
        """
        with self.driver.session() as session:
            result = session.run(
                f"""
                MATCH path = (start:Entity {{name: $name}})-[*1..{depth}]->(affected:Entity)
                RETURN DISTINCT
                    affected.name        AS affected_entity,
                    affected.type        AS entity_type,
                    length(path)         AS hops,
                    [r IN relationships(path) | r.type] AS relationship_chain
                ORDER BY hops
                LIMIT 50
                """,
                name=entity_name,
            )
            return [dict(r) for r in result]

    def get_neighbors(self, entity_name: str) -> list[dict]:
        """Get direct neighbors of an entity (1 hop)."""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (e:Entity {name: $name})-[r]->(neighbor:Entity)
                RETURN neighbor.name AS name, neighbor.type AS type, r.type AS relationship
                UNION
                MATCH (caller:Entity)-[r]->(e:Entity {name: $name})
                RETURN caller.name AS name, caller.type AS type, r.type AS relationship
                """,
                name=entity_name,
            )
            return [dict(r) for r in result]

    def get_stats(self) -> dict:
        """Return basic graph statistics."""
        with self.driver.session() as session:
            nodes = session.run("MATCH (n:Entity) RETURN count(n) AS count").single()["count"]
            edges = session.run("MATCH ()-[r]->() RETURN count(r) AS count").single()["count"]
            types = session.run(
                "MATCH (n:Entity) RETURN DISTINCT n.type AS type, count(*) AS count"
            ).data()
            return {"nodes": nodes, "edges": edges, "types": types}

    def clear_graph(self):
        """Delete all nodes and relationships (fresh start)."""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        console.print("[yellow]⚠ Graph cleared.[/yellow]")
