import html
import json

import hh_linkedin_agent as a


def test_parse_state():
    state = {"vacancyView": {"name": "Dev & Ops"}}
    page = (
        '<html><template style="display:none" id="HH-Lux-InitialState">'
        + html.escape(json.dumps(state))
        + "</template></html>"
    )
    assert a.parse_state(page) == state


def test_extract_linkedin_urls_normalizes_and_dedupes():
    text = (
        'Мы в <a href="https://uk.linkedin.com/company/acme-corp/?trk=x">LinkedIn</a>, '
        "https://www.linkedin.com/company/acme-corp/about, "
        "https://linkedin.com/in/john-doe"
    )
    assert a.extract_linkedin_urls(text) == ["https://www.linkedin.com/company/acme-corp"]


def test_mention_snippet():
    text = "x" * 300 + " опыт работы с LinkedIn " + "y" * 300
    snippet = a.mention_snippet(text)
    assert "LinkedIn" in snippet and snippet.startswith("…") and snippet.endswith("…")
    assert a.mention_snippet("без упоминаний") == ""


def test_html_to_text():
    assert a.html_to_text("<p>Hello&nbsp;<b>LinkedIn</b></p>") == "Hello LinkedIn"


def test_rank_candidates_translit_and_domain():
    hits = [
        {"url": "https://www.linkedin.com/company/librasoft", "title": "Librasoft | LinkedIn"},
        {"url": "https://www.linkedin.com/company/libresoft", "title": "LibreSoft | LinkedIn"},
    ]
    ranked = a.rank_candidates("ООО Либрасофт", "http://www.librasoft.by", hits)
    assert ranked[0][1] == "https://www.linkedin.com/company/librasoft"
    assert ranked[0][0] >= 0.75


def test_rank_candidates_rejects_unrelated():
    hits = [{"url": "https://www.linkedin.com/company/invest-gazprom",
             "title": "Газпром инвест | LinkedIn"}]
    ranked = a.rank_candidates("Карбон-Инвест", "", hits)
    assert ranked[0][0] < 0.75


def test_clean_company_name():
    assert a.clean_company_name("А1.Начало карьеры (Специалист по продажам)") == "А1.Начало карьеры"


class FakeWeb:
    def __init__(self, hits):
        self.hits = hits
        self.calls = 0

    def search(self, query, n=8):
        self.calls += 1
        return list(self.hits)


def test_agent_prefers_description_link(monkeypatch):
    vacancy = {
        "name": "SMM",
        "description": "<p>Пишите нам в LinkedIn: https://www.linkedin.com/company/foo</p>",
        "company": {"id": 1, "visibleName": "Foo", "companySiteUrl": ""},
        "area": {"name": "Москва"},
        "publicationDate": "2026-09-01",
    }
    monkeypatch.setattr(a, "fetch_vacancy", lambda http, vid: vacancy)
    web = FakeWeb([])
    r = a.Agent(http=None, web=web).process(42)
    assert r.linkedin_url == "https://www.linkedin.com/company/foo"
    assert r.linkedin_source == "description"
    assert web.calls == 0


def test_agent_web_search_cached_per_company(monkeypatch):
    vacancy = {
        "name": "Sales",
        "description": "<p>Опыт работы с LinkedIn</p>",
        "company": {"id": 7, "visibleName": "Itransition", "companySiteUrl": ""},
    }
    monkeypatch.setattr(a, "fetch_vacancy", lambda http, vid: vacancy)
    web = FakeWeb([{"url": "https://www.linkedin.com/company/itransition",
                    "title": "Itransition Group | LinkedIn"}])
    agent = a.Agent(http=None, web=web)
    r1, r2 = agent.process(1), agent.process(2)
    assert r1.linkedin_url == r2.linkedin_url == "https://www.linkedin.com/company/itransition"
    assert r1.linkedin_source == "web_search"
    assert web.calls == 1


def test_agent_skips_vacancy_without_word(monkeypatch):
    monkeypatch.setattr(a, "fetch_vacancy",
                        lambda http, vid: {"description": "<p>Без упоминаний</p>"})
    assert a.Agent(http=None, web=FakeWeb([])).process(1) is None


def test_search_vacancy_ids_dedupes_across_pages(monkeypatch):
    pages = [
        {"vacancies": [{"vacancyId": 1}, {"vacancyId": 2}], "totalResults": 3,
         "paging": {"next": {"disabled": False}}},
        {"vacancies": [{"vacancyId": 1}, {"vacancyId": 3}],
         "paging": {"next": {"disabled": True}}},
    ]

    class Resp:
        def __init__(self, state):
            self.text = state

        def raise_for_status(self):
            pass

    class FakeHttp:
        def get(self, url, params):
            return Resp(pages[params["page"]])

    monkeypatch.setattr(a, "parse_state", lambda state: {"vacancySearchResult": state})
    assert list(a.search_vacancy_ids(FakeHttp(), "linkedin", None)) == [1, 2, 3]
