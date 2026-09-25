# hh.ru → LinkedIn агент

Скрипт ищет на hh.ru вакансии, в **описании** которых встречается слово `linkedin`,
и для каждой находит LinkedIn-профиль компании-работодателя.

## Как ищется профиль компании

| Шаг | Источник | `linkedin_source` |
|---|---|---|
| 1 | Ссылка `linkedin.com/company/...` прямо в тексте вакансии | `description` |
| 2 | Ссылка на LinkedIn на сайте компании (сайт берётся из карточки работодателя hh.ru) | `company_site` |
| 3 | Веб-поиск `<компания> site:linkedin.com/company` и `"<домен>" site:linkedin.com/company` | `web_search` |
| — | Ничего подходящего | `not_found` |

Шаги 2–3 выполняются один раз на работодателя (кэш). Результаты веб-поиска
оцениваются по похожести названия (с транслитерацией) и совпадению домена
сайта; ниже порога `--min-score` (по умолчанию 0.75) профиль не
присваивается, но топ-3 кандидата с оценками остаются в колонке
`linkedin_candidates`, так что их можно проверить вручную.

> Результаты `web_search` для компаний с общими названиями (например,
> «FRONTLINE») стоит перепроверять. `company_site` и `description` надёжны.

## Установка

```bash
cd hh-linkedin-agent
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
```

## Запуск

```bash
# быстрый тест на 20 вакансиях → results.csv
python hh_linkedin_agent.py --limit 20 -v

# все вакансии + запись в Google Таблицу
python hh_linkedin_agent.py \
  --sheet-id <ID из URL таблицы> \
  --google-credentials service-account.json
```

Основные параметры:

- `--query` — искомое слово (по умолчанию `linkedin`);
- `--limit` — максимум вакансий (по умолчанию все, hh.ru отдаёт до 2000 на поиск);
- `--search-provider` — `ddg` (DuckDuckGo, без ключа, по умолчанию), `serpapi`
  (`SERPAPI_KEY`), `brave` (`BRAVE_API_KEY`) или `none`;
- `--delay` — пауза между запросами, сек (по умолчанию 1);
- `--csv` — куда сохранить CSV (по умолчанию `results.csv`).

## Google Таблица

1. В [Google Cloud Console](https://console.cloud.google.com/) создайте проект,
   включите **Google Sheets API**, создайте **сервисный аккаунт** и скачайте JSON-ключ.
2. Откройте нужную таблицу и дайте доступ «Редактор» на e-mail сервисного
   аккаунта (`...@...iam.gserviceaccount.com`).
3. Передайте `--sheet-id` и `--google-credentials` (или переменные
   `GOOGLE_SHEET_ID` и `GOOGLE_APPLICATION_CREDENTIALS`).

Скрипт перезаписывает лист `hh_linkedin` (имя меняется через `--worksheet`).
CSV сохраняется всегда.

## Колонки результата

`vacancy_id`, `vacancy_url`, `vacancy_name`, `published`, `area`, `company_id`,
`company_name`, `hh_company_url`, `company_site`, `linkedin_url`,
`linkedin_source`, `linkedin_candidates`, `mention` (фрагмент описания вокруг
слова linkedin).

## Замечания

- Данные берутся со страниц hh.ru (JSON, встроенный в страницу), потому что
  официальный API `api.hh.ru` отвечает `403 forbidden` без токена приложения.
  Если структура страниц hh.ru поменяется, правка нужна в `parse_state`,
  `search_vacancy_ids` и `fetch_vacancy`.
- Сам LinkedIn скрипт не открывает: ссылки берутся из вакансии, с сайта компании
  или из поисковой выдачи.
- Тесты: `python -m pytest -q`.
