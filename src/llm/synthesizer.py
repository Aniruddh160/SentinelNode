import subprocess


class AnswerSynthesizer:
    def __init__(self, model="mistral"):
        self.model = model

    def synthesize(self, query, contexts):
        context_block = "\n\n".join(contexts)

        prompt = f"""
You are an expert system answering strictly from the provided context.

Context:
{context_block}

Question:
{query}

Rules:
- Use only the given context
- If answer is not in context, say "I don't know"
- Be concise and factual
"""

        result = subprocess.run(
            ["ollama", "run", self.model],
            input=prompt.encode("utf-8"),   # ✅ FIX IS HERE
            capture_output=True
        )

        stdout = result.stdout.decode("utf-8", errors="ignore")
        return stdout.strip()

