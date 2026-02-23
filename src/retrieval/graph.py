from collections import defaultdict


class GraphIndex:
    def __init__(self, chunks):
        self.chunks = chunks
        self.graph = defaultdict(set)
        self._build_graph()

    def _build_graph(self):
        doc_map = defaultdict(list)

        for chunk in self.chunks:
            doc_map[chunk["file_path"]].append(chunk)


        for doc_chunks in doc_map.values():
            doc_chunks.sort(key=lambda c: c["chunk_id"])

            for i, chunk in enumerate(doc_chunks):
                cid = chunk["chunk_id"]

                if i > 0:
                    self.graph[cid].add(doc_chunks[i - 1]["chunk_id"])
                if i < len(doc_chunks) - 1:
                    self.graph[cid].add(doc_chunks[i + 1]["chunk_id"])

    def expand(self, seed_chunks, hops=1):
        visited = set()
        frontier = set(seed_chunks)

        for _ in range(hops):
            next_frontier = set()
            for cid in frontier:
                for neighbor in self.graph.get(cid, []):
                    if neighbor not in visited:
                        next_frontier.add(neighbor)
            visited |= frontier
            frontier = next_frontier

        return visited
