import json
import os
from datetime import datetime

LOG_DIR = "data/eval_logs"
LOG_FILE = os.path.join(LOG_DIR, "strategy_log.jsonl")


def log_strategy(
    query: str,
    strategy: str,
    chunk_ids: list[int]
):
    os.makedirs(LOG_DIR, exist_ok=True)

    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "query": query,
        "strategy": strategy,
        "num_chunks": len(chunk_ids),
        "chunk_ids": chunk_ids,
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")
