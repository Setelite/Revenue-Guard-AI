"""Revenue Guard AI local smoke test (Windows/macOS/Linux).

Run:
    python local_probe.py            # offline / free mock
    python local_probe.py --real     # paid Cloud.ru API request, hidden key
No secrets are written to disk.
"""
from __future__ import annotations

import getpass
import json
import os
import secrets
import sys

GOAL = "Завтра у мастера может быть свободное время. Предложи 3 способа привлечь клиентов без скидок."
DATA = {
    "goal": GOAL,
    "business": {
        "name": "Тестовая студия",
        "city": "Екатеринбург",
        "voice": "Тепло, ясно, без штампов",
        "channels": "Telegram и VK",
        "budget": 0,
        "services": [{"name": "Окрашивание волос", "price": 4500, "duration": 0}],
    },
}


def mock_provider(server):
    class MockResponse:
        def raise_for_status(self): pass

        def json(self):
            angles = [
                ("Проверить окна", "Согласуем расписание и опубликуем свободное время."),
                ("Вопрос мастеру", "Предложим подписчикам узнать нюансы окрашивания."),
                ("Изнутри студии", "Покажем подготовку к услуге с согласия мастера."),
            ]
            offers = []
            for title, copy in angles:
                offers.append({
                    "title": title,
                    "reason": "Рассказать о конкретной услуге без непроверенных обещаний",
                    "channel": "Telegram",
                    "description": "Подготовить публикацию и проверить информацию",
                    "headline": title,
                    "copy": copy + " Уточните подробности через сообщения студии.",
                    "steps": ["Проверить факты", "Согласовать и опубликовать"],
                    "caution": "Не обещайте неподтвержденное время записи",
                })
            return {"choices": [{"message": {"content": json.dumps({"offers": offers}, ensure_ascii=False)}}]}

    class MockClient:
        def __init__(self, **kwargs): pass
        async def __aenter__(self): return self
        async def __aexit__(self, *args): pass
        async def post(self, url, **kwargs):
            assert url == "https://foundation-models.api.cloud.ru/v1/chat/completions"
            assert "Authorization" in kwargs["headers"]
            return MockResponse()

    server.httpx.AsyncClient = MockClient


def main():
    live = "--real" in sys.argv
    token = secrets.token_urlsafe(36)
    os.environ["AI_PROVIDER"] = "cloudru"
    os.environ["RG_DEMO_ACCESS_TOKEN"] = token
    os.environ["CLOUDRU_MODEL"] = os.getenv("CLOUDRU_MODEL", "ai-sage/GigaChat3-10B-A1.8B")
    if live:
        print("Настоящий запрос в Cloud.ru может списать деньги за токены.")
        if input("Продолжить? (да/нет): ").strip().lower() not in ("да", "yes", "y"):
            return 0
        key = getpass.getpass("Key Secret Cloud.ru (скрытый ввод): ").strip()
        if not key:
            print("Ключ не введен. Запрос отменён.")
            return 2
        os.environ["CLOUDRU_API_KEY"] = key
    else:
        os.environ["CLOUDRU_API_KEY"] = "mock-never-sent"
        print("БЕСПЛАТНЫЙ ТЕСТ: модель имитируется. В Cloud.ru запрос НЕ отправляется.")

    try:
        import server
        from fastapi.testclient import TestClient
        if not live:
            mock_provider(server)
        with TestClient(server.app) as client:
            response = client.post("/api/generate", json=DATA, headers={"X-Demo-Token": token})
        if response.status_code != 200:
            try:
                detail = response.json().get("detail", "")
            except Exception:
                detail = ""
            print("Ошибка:", response.status_code, str(detail)[:300])
            return 1
        offers = response.json()["offers"]
        assert len(offers) == 3
        for i, offer in enumerate(offers, 1):
            print("\n" + str(i) + ". " + offer["title"])
            print("Канал:", offer["channel"])
            print("Идея:", offer["reason"])
            print("Заголовок:", offer["headline"])
            print("Текст:", offer["copy"])
            print("Проверить:", offer["caution"])
        print("\nПроверка пройдена:", "реальный Cloud.ru API" if live else "локальная имитация")
        return 0
    except Exception as exc:
        print("Ошибка проверки:", type(exc).__name__)
        return 1
    finally:
        os.environ.pop("CLOUDRU_API_KEY", None)


if __name__ == "__main__":
    raise SystemExit(main())
