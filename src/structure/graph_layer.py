from dataclasses import dataclass
import networkx as nx

# -----------------------------
# Entity & Relation Definitions
# -----------------------------

@dataclass
class Entity:
    id: str
    name: str
    type: str
    aliases: list[str]


@dataclass
class Relation:
    source: str
    relation: str
    target: str


# -----------------------------
# Entity Registry (Manual, Deterministic)
# -----------------------------

ENTITIES = [
    Entity("E1", "SentinelNode", "System", ["sentinelnode"]),
    Entity("E2", "RAG", "Technique", ["rag", "retrieval augmented generation"]),
    Entity("E3", "Ingestion Layer", "Component", ["ingestion layer", "ingestion"]),
    Entity("E4", "Retrieval Layer", "Component", ["retrieval layer", "retrieval"]),
    Entity("E5", "LLM", "Model", ["llm", "large language model"]),
    Entity("E6", "Vector Database", "Component", ["vector database", "faiss"]),
    Entity("E7", "Graph Database", "Component", ["graph database", "graph"]),
]


# -----------------------------
# Relations (Manual, Explicit)
# -----------------------------

RELATIONS = [
    Relation("E1", "uses", "E2"),
    Relation("E1", "has_layer", "E3"),
    Relation("E1", "has_layer", "E4"),
    Relation("E4", "uses", "E6"),
    Relation("E1", "integrates", "E7"),
    Relation("E2", "reduces", "E5"),
]


# -----------------------------
# Entity → Chunk Mapping
# -----------------------------

def map_entities_to_chunk(chunk_text: str, entities: list[Entity]) -> list[str]:
    text = chunk_text.lower()
    found = []

    for e in entities:
        for alias in e.aliases:
            if alias in text:
                found.append(e.id)
                break

    return found


def build_entity_chunk_map(chunks: list[dict], entities: list[Entity]) -> dict:
    entity_chunk_map = {e.id: [] for e in entities}

    for chunk in chunks:
        entity_ids = map_entities_to_chunk(chunk["text"], entities)
        for eid in entity_ids:
            entity_chunk_map[eid].append(chunk["chunk_id"])

    return entity_chunk_map


# -----------------------------
# Graph Construction
# -----------------------------

def build_graph(entities: list[Entity], relations: list[Relation]) -> nx.DiGraph:
    graph = nx.DiGraph()

    for e in entities:
        graph.add_node(e.id, name=e.name, type=e.type)

    for r in relations:
        graph.add_edge(r.source, r.target, relation=r.relation)

    return graph


# -----------------------------
# Graph Traversal → Chunk Resolution
# -----------------------------

def traverse_graph(graph: nx.DiGraph, start_entities: list[str], depth: int = 2):
    paths = []

    for eid in start_entities:
        for target, path in nx.single_source_shortest_path(
            graph, eid, cutoff=depth
        ).items():
            paths.append(path)

    return paths


def resolve_chunks_from_paths(
    paths: list[list[str]],
    entity_chunk_map: dict
) -> list[int]:
    chunks = set()

    for path in paths:
        for entity_id in path:
            chunks.update(entity_chunk_map.get(entity_id, []))

    return sorted(list(chunks))


# -----------------------------
# Intent Routing (Simple & Correct)
# -----------------------------

GRAPH_TRIGGERS = ["how", "why", "relationship", "connected", "depends", "architecture"]


def needs_graph(query: str) -> bool:
    q = query.lower()
    return any(word in q for word in GRAPH_TRIGGERS)


def extract_query_entities(query: str, entities: list[Entity]) -> list[str]:
    q = query.lower()
    found = []

    for e in entities:
        for alias in e.aliases:
            if alias in q:
                found.append(e.id)
                break

    return found


# -----------------------------
# MAIN GRAPH-AWARE RETRIEVAL LOGIC
# -----------------------------

def graph_aware_retrieval(query: str, chunks: list[dict]):
    # Build structures
    entity_chunk_map = build_entity_chunk_map(chunks, ENTITIES)
    graph = build_graph(ENTITIES, RELATIONS)

    if not needs_graph(query):
        return {
            "strategy": "vector_only",
            "chunk_ids": [],
        }

    query_entities = extract_query_entities(query, ENTITIES)

    if not query_entities:
        return {
            "strategy": "fallback_vector",
            "chunk_ids": [],
        }

    paths = traverse_graph(graph, query_entities)
    chunk_ids = resolve_chunks_from_paths(paths, entity_chunk_map)

    return {
        "strategy": "graph_aware",
        "query_entities": query_entities,
        "paths": paths,
        "chunk_ids": chunk_ids,
    }
