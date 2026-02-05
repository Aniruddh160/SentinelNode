import re


def split_into_sentences(text: str) -> list[str]:
    # Simple, deterministic sentence splitter
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s for s in sentences if len(s) > 3]


def is_sentence_grounded(sentence: str, contexts: list[str]) -> bool:
    sentence = sentence.lower()

    for ctx in contexts:
        ctx = ctx.lower()
        # loose containment check (robust, fast)
        if any(token in ctx for token in sentence.split()[:4]):
            return True

    return False


def compute_grounding_coverage(answer: str, contexts: list[str]) -> dict:
    sentences = split_into_sentences(answer)

    if not sentences:
        return {
            "coverage": 0.0,
            "grounded": 0,
            "total": 0
        }

    grounded = 0
    for s in sentences:
        if is_sentence_grounded(s, contexts):
            grounded += 1

    return {
        "coverage": round(grounded / len(sentences), 2),
        "grounded": grounded,
        "total": len(sentences)
    }
