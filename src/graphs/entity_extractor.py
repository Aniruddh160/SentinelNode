import json
import re
from typing import List
from .entities import Entity
from llm.ollama_client import OllamaClient

ENTITY_TYPES = [
    "SERVICE",
    "API",
    "DATABASE",
    "LIBRARY",
    "INFRASTRUCTURE",
    "EXTERNAL_SERVICE",
    "CONFIG",
    "QUEUE",
]

class EntityExtractor:

    def __init__(self):
        self.llm = OllamaClient()

    def extract(self, text: str, source_doc: str) -> List[Entity]:

        prompt = f"""
You are an enterprise system analyzer.

Extract all technical entities from the text.

Allowed entity types:
{ENTITY_TYPES}

Rules:
- Only extract real system components.
- Do not hallucinate.
- If none exist, return [].
- Output STRICT JSON.
- No explanations.
- No markdown.
- No commentary.

Output format:
[
  {{"name": "EntityName", "type": "TYPE"}}
]

Text:
{text}
"""

        raw_response = self.llm.generate(prompt)

        cleaned = self._clean_json(raw_response)

        try:
            parsed = json.loads(cleaned)
        except:
            return []

        entities = []

        for item in parsed:
            if (
                isinstance(item, dict)
                and item.get("type") in ENTITY_TYPES
                and item.get("name")
            ):
                entities.append(
                    Entity(
                        name=item["name"].strip(),
                        type=item["type"],
                        source_doc=source_doc
                    )
                )

        return entities

    def _clean_json(self, response: str) -> str:
        """
        Removes markdown fences or extra text.
        """
        response = re.sub(r"```.*?```", "", response, flags=re.DOTALL)
        response = response.strip()
        return response
