from dataclasses import dataclass
import networkx as nx
import re
# ==============================
# Entity & Relation Definitions
# ==============================

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
    weight: float  # NEW: weighted relations


# ==============================
# Entity Registry
# ==============================

ENTITIES = [
    Entity("E1", "SentinelNode", "System", ["sentinelnode"]),
    Entity("E2", "RAG", "Technique", ["rag", "retrieval augmented generation"]),
    Entity("E3", "Ingestion Layer", "Component", ["ingestion layer", "ingestion"]),
    Entity("E4", "Retrieval Layer", "Component", ["retrieval layer", "retrieval"]),
    Entity("E5", "LLM", "Model", ["llm", "large language model"]),
    Entity("E6", "Vector Database", "Component", ["vector database", "faiss"]),
    Entity("E7", "Graph Database", "Technology", ["graph database"]),
    Entity("E8", "Graph-aware Retrieval", "Technique", ["graph-aware retrieval"])


]


# ==============================
# Weighted Relations
# ==============================

RELATIONS = [
    Relation("E1", "has_layer", "E3", 0.9),
    Relation("E1", "has_layer", "E4", 0.9),
    Relation("E4", "uses", "E6", 0.7),
    Relation("E1", "integrates", "E7", 0.6),
    Relation("E2", "reduces", "E5", 0.4),
]


# ==============================
# Entity → Chunk Mapping
# ==============================

def map_entities_to_chunk(chunk_text: str, entities: list[Entity]) -> list[str]:
    text = chunk_text.lower()
    found = []

    for e in entities:
        for alias in e.aliases:
            if re.search(rf"\b{re.escape(alias)}\b", text):
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


# ==============================
# Graph Construction
# ==============================

def build_graph(entities: list[Entity], relations: list[Relation]) -> nx.DiGraph:
    graph = nx.DiGraph()

    for e in entities:
        graph.add_node(e.id, name=e.name, type=e.type)

    for r in relations:
        graph.add_edge(
            r.source,
            r.target,
            relation=r.relation,
            weight=r.weight  # store weight on edge
        )

    return graph


# ==============================
# Intent-Based Traversal Mode
# ==============================

def determine_traversal_mode(query: str) -> str:
    q = query.lower()

    if "architecture" in q or "core" in q:
        return "structural"

    if "how" in q or "why" in q:
        return "causal"

    return "default"


# ==============================
# Weighted Traversal
# ==============================

def weighted_traverse(graph, start_entities, mode="default"):
    paths = []

    for source in start_entities:
        for neighbor in graph.successors(source):
            edge_data = graph.get_edge_data(source, neighbor)
            weight = edge_data.get("weight", 0.5)

            if mode == "structural" and weight >= 0.8:
                paths.append([source, neighbor])

            elif mode == "causal" and weight >= 0.6:
                paths.append([source, neighbor])

            elif mode == "default" and weight >= 0.5:
                paths.append([source, neighbor])

    return paths


# ==============================
# Chunk Resolution
# ==============================

def resolve_chunks_with_scores(scored_paths, entity_chunk_map):
    """
    Returns dict:
        chunk_id -> max path score reaching it
    """
    chunk_scores = {}

    for path, score in scored_paths:
        for entity_id in path:
            chunk_ids = entity_chunk_map.get(entity_id, [])
            for cid in chunk_ids:
                if cid not in chunk_scores:
                    chunk_scores[cid] = score
                else:
                    chunk_scores[cid] = max(chunk_scores[cid], score)

    return chunk_scores



# ==============================
# Query Entity Extraction
# ==============================

def extract_query_entities(query: str, entities: list[Entity]) -> list[str]:
    q = query.lower()
    found = []

    for e in entities:
        for alias in e.aliases:
            if alias in q:
                found.append(e.id)
                break

    return found


# ==============================
# Graph-Aware Retrieval Entry
# ==============================

def graph_aware_retrieval(query: str, chunks: list[dict]):
    entity_chunk_map = build_entity_chunk_map(chunks, ENTITIES)
    graph = build_graph(ENTITIES, RELATIONS)

    query_entities = extract_query_entities(query, ENTITIES)
    mode = determine_traversal_mode(query)

    # Structural fallback only if no explicit entity
    if not query_entities and mode == "structural":
        query_entities = ["E1"]  # SentinelNode root

    if not query_entities:
        return {
            "strategy": "vector_only",
            "chunk_scores": {}
        }

    # 🔥 Multi-hop scored traversal
    scored_paths = scored_traverse(
        graph,
        query_entities,
        max_depth=2,
        min_score=0.5
    )

    # 🔥 Resolve chunks WITH scores
    chunk_scores = resolve_chunks_with_scores(
        scored_paths,
        entity_chunk_map
    )

    if not chunk_scores:
        return {
            "strategy": "fallback_vector",
            "chunk_scores": {}
        }

    return {
        "strategy": "graph_aware",
        "mode": mode,
        "query_entities": query_entities,
        "chunk_scores": chunk_scores
    }
def scored_traverse(graph, start_entities, max_depth=2, min_score=0.5):
    results = []

    for source in start_entities:
        for neighbor in graph.successors(source):
            edge_data = graph.get_edge_data(source, neighbor)
            weight = edge_data.get("weight", 0.5)

            if weight >= min_score:
                results.append(([source, neighbor], weight))

    return results
