"""Агент поиска компаний по отрасли и стране + их страниц в LinkedIn.

Пример:
    python find_companies.py --industry iGaming --country Cyprus \
        --segment "B2C-операторы: онлайн-казино и букмекеры (НЕ провайдеры, НЕ платформы, НЕ аффилиаты)" \
        --out results/cyprus_igaming_operators_agent.csv

Шаги:
  1. research  — Claude с web_search/web_fetch ищет компании, проверяет,
                 что это операторы, и находит linkedin.com/company/... страницу.
  2. extract   — ответ исследования превращается в строго типизированный список.
  3. export    — валидация LinkedIn-ссылок и запись в CSV.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from typing import Literal

import anthropic
from pydantic import BaseModel, Field

MODEL = "claude-opus-5"
MAX_CONTINUATIONS = 10  # сколько раз продолжаем turn после pause_turn

LINKEDIN_COMPANY_RE = re.compile(
    r"^https?://([a-z]{2,3}\.)?(www\.)?linkedin\.com/(company|showcase)/[^/?#\s]+/?", re.I
)


class Company(BaseModel):
    name: str = Field(description="Название компании / группы")
    legal_entity: str = Field(description="Юрлицо, если найдено, иначе пустая строка")
    brands: list[str] = Field(description="Основные B2C-бренды")
    website: str = Field(description="Основной сайт")
    company_type: Literal[
        "online_casino_and_sportsbook",
        "online_casino",
        "online_sportsbook",
        "land_based_casino",
        "hybrid_operator_and_provider",
    ]
    presence_in_country: str = Field(description="HQ / офис / лицензия в стране — чем подтверждено")
    licences: str = Field(description="Лицензии (регулятор, номер), если известны")
    linkedin_url: str = Field(description="URL linkedin.com/company/... или пустая строка")
    source_urls: list[str] = Field(description="Ссылки-доказательства")
    confidence: Literal["high", "medium", "low"]
    notes: str


class CompanyList(BaseModel):
    companies: list[Company]


SYSTEM_PROMPT = """Ты — research-агент по B2B-лидогенерации. Задача: найти компании \
заданной отрасли, реально присутствующие в заданной стране, и их официальные \
страницы компании в LinkedIn.

Правила отбора (iGaming):
- Нужны ОПЕРАТОРЫ (B2C): компании, которые сами принимают ставки/игру от игроков \
под своими брендами — онлайн-казино, букмекеры, наземные казино.
- ИСКЛЮЧИ провайдеров: разработчиков игр/слотов, платформы и white-label, \
PAM/CRM/KYC/платёжные сервисы, аффилиатов и медиа, консалтинг и юристов.
- Если компания и оператор, и провайдер — включи с типом hybrid_operator_and_provider.
- «Присутствие в стране» = штаб-квартира, операционный офис или локальная лицензия. \
Для каждой компании укажи, чем это подтверждено (URL).

Правила для LinkedIn:
- Ищи запросами вида `site:linkedin.com/company <бренд>`.
- Бери основную корпоративную страницу (или страницу кипрского/локального юрлица), \
а НЕ affiliates/partners-страницы и не личные профили /in/.
- Если уверенной ссылки нет — оставь поле пустым, не выдумывай.

Работай тщательно: проверь регуляторные реестры, отраслевые СМИ, вакансии. \
В конце выдай итоговую таблицу со всеми найденными компаниями и полями: \
название, юрлицо, бренды, сайт, тип, подтверждение присутствия, лицензии, \
LinkedIn, источники, уверенность, заметки."""


def research(client: anthropic.Anthropic, industry: str, country: str, segment: str, limit: int) -> str:
    """Шаг 1: исследование с web_search / web_fetch, обработка pause_turn."""
    user_msg = (
        f"Отрасль: {industry}\nСтрана: {country}\nСегмент: {segment}\n"
        f"Найди до {limit} компаний и их LinkedIn company pages."
    )
    messages: list[dict] = [{"role": "user", "content": user_msg}]
    tools = [
        {"type": "web_search_20260209", "name": "web_search", "max_uses": 60},
        {"type": "web_fetch_20260209", "name": "web_fetch", "max_uses": 30},
    ]

    for _ in range(MAX_CONTINUATIONS + 1):
        with client.beta.messages.stream(
            model=MODEL,
            max_tokens=64000,
            system=SYSTEM_PROMPT,
            thinking={"type": "adaptive"},
            output_config={"effort": "high"},
            tools=tools,
            messages=messages,
            betas=["server-side-fallback-2026-07-01"],
            extra_body={"fallbacks": "default"},
        ) as stream:
            response = stream.get_final_message()

        if response.stop_reason == "refusal":
            raise RuntimeError(f"Модель отказалась: {response.stop_details}")
        if response.stop_reason != "pause_turn":
            return "".join(b.text for b in response.content if b.type == "text")
        # Сервер прервал длинный цикл инструментов — продолжаем тот же turn.
        messages = [messages[0], {"role": "assistant", "content": response.content}]
        print("  …продолжаю исследование (pause_turn)", file=sys.stderr)

    raise RuntimeError("Исследование не завершилось за MAX_CONTINUATIONS продолжений")


def extract(client: anthropic.Anthropic, research_text: str) -> CompanyList:
    """Шаг 2: превращаем текст исследования в валидированную структуру."""
    response = client.messages.parse(
        model=MODEL,
        max_tokens=16000,
        messages=[{
            "role": "user",
            "content": "Перенеси ВСЕ компании из отчёта ниже в структуру. "
                       "Ничего не добавляй от себя, пустые поля оставляй пустыми.\n\n"
                       + research_text,
        }],
        output_format=CompanyList,
    )
    if response.stop_reason == "refusal" or response.parsed_output is None:
        raise RuntimeError(f"Не удалось извлечь структуру (stop_reason={response.stop_reason})")
    return response.parsed_output


def export_csv(companies: list[Company], path: str) -> None:
    """Шаг 3: запись в CSV; невалидные LinkedIn-ссылки обнуляются."""
    fields = ["name", "legal_entity", "brands", "website", "company_type",
              "presence_in_country", "licences", "linkedin_url",
              "source_urls", "confidence", "notes"]
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for c in companies:
            row = c.model_dump()
            if row["linkedin_url"] and not LINKEDIN_COMPANY_RE.match(row["linkedin_url"]):
                row["notes"] = f"{row['notes']} [отброшена невалидная LinkedIn-ссылка: {row['linkedin_url']}]"
                row["linkedin_url"] = ""
            row["brands"] = "; ".join(row["brands"])
            row["source_urls"] = " ".join(row["source_urls"])
            writer.writerow(row)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--industry", default="iGaming")
    p.add_argument("--country", default="Cyprus")
    p.add_argument("--segment", default="B2C-операторы: онлайн-казино и букмекеры, "
                                        "НЕ провайдеры/платформы/аффилиаты")
    p.add_argument("--limit", type=int, default=40)
    p.add_argument("--out", default="results/companies.csv")
    args = p.parse_args()

    client = anthropic.Anthropic()
    print(f"[1/3] Исследование: {args.industry} / {args.country}", file=sys.stderr)
    text = research(client, args.industry, args.country, args.segment, args.limit)
    print("[2/3] Структурирование", file=sys.stderr)
    result = extract(client, text)
    print(f"[3/3] Запись {len(result.companies)} компаний → {args.out}", file=sys.stderr)
    export_csv(result.companies, args.out)


if __name__ == "__main__":
    main()
