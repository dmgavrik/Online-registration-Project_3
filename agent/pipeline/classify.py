"""Автоклассификатор кандидатов: оператор / провайдер / аффилиат / прочее.

    python classify.py candidates.json > classified.json

candidates.json — список объектов с полями name, description/evidence, website (любые доступные).
Нужен ANTHROPIC_API_KEY.
"""
import json
import sys
from typing import Literal

import anthropic
from pydantic import BaseModel

MODEL = "claude-opus-5"
BATCH = 25

SYSTEM = """Ты классифицируешь компании iGaming-индустрии.
- operator: сам принимает ставки/игру от игроков под своими брендами (онлайн-казино, букмекер, покер, лотерея, наземное казино).
- hybrid: одновременно оператор своих брендов и B2B-платформа/white-label.
- provider: B2B — игры/слоты, платформы, white-label, PAM/CRM/KYC, платежи, данные.
- affiliate: аффилиат-программы, партнёрки, SEO/медиа, обзорники казино.
- other: всё остальное (рекрутинг, консалтинг, юристы, регуляторы, гостиницы без казино).
Если данных мало — ставь confidence=low, не выдумывай."""


class Item(BaseModel):
    name: str
    category: Literal["operator", "hybrid", "provider", "affiliate", "other"]
    confidence: Literal["high", "medium", "low"]
    reason: str


class Batch(BaseModel):
    items: list[Item]


def classify(cands: list[dict]) -> list[dict]:
    client = anthropic.Anthropic()
    out = []
    for i in range(0, len(cands), BATCH):
        chunk = cands[i:i + BATCH]
        resp = client.messages.parse(
            model=MODEL,
            max_tokens=16000,
            system=SYSTEM,
            messages=[{"role": "user", "content": "Классифицируй каждую компанию:\n"
                       + json.dumps(chunk, ensure_ascii=False)}],
            output_format=Batch,
        )
        if resp.parsed_output is None:
            raise RuntimeError(f"Не удалось разобрать ответ (stop_reason={resp.stop_reason})")
        out += [c | it.model_dump() for c, it in zip(chunk, resp.parsed_output.items)]
    return out


if __name__ == "__main__":
    json.dump(classify(json.load(open(sys.argv[1]))), sys.stdout, ensure_ascii=False, indent=1)
