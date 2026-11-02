import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server

client = TestClient(server.app)

def test_frontpage():
    r = client.get('/')
    assert r.status_code == 200
    assert 'REVENUE GUARD' in r.text
    assert 'SpeechRecognition' in r.text


def test_status_without_keys(monkeypatch):
    monkeypatch.delenv('YANDEX_API_KEY', raising=False)
    monkeypatch.delenv('YANDEX_FOLDER_ID', raising=False)
    r = client.get('/api/status')
    assert r.json()['ai_enabled'] is False


def test_model_is_not_called_without_keys(monkeypatch):
    monkeypatch.delenv('YANDEX_API_KEY', raising=False)
    monkeypatch.delenv('YANDEX_FOLDER_ID', raising=False)
    r = client.post('/api/generate',json={
        'goal':'Заполнить свободные окна завтра',
        'business':{'name':'Тест','city':'Екатеринбург','voice':'Спокойный','channels':'Telegram','budget':0,'services':[{'name':'Маникюр','price':2500,'duration':90}]}
    })
    assert r.status_code == 503


def test_validation():
    r = client.post('/api/generate', json={'goal':'коротко','business':{}})
    assert r.status_code == 422


def test_manifest():
    assert client.get('/manifest.webmanifest').status_code == 200


def test_ai_response_contract_with_mock(monkeypatch):
    import json
    monkeypatch.setenv('YANDEX_API_KEY', 'test_secret_not_real')
    monkeypatch.setenv('YANDEX_FOLDER_ID', 'test_folder')
    sent = {}

    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            row = {
                'title': 'Предложение для салона',
                'reason': 'Проверка спроса в собственном канале',
                'channel': 'Собственный Telegram',
                'description': 'Публикация о свободных часах, только после проверки',
                'headline': 'Свободное время',
                'copy': 'Есть свободное время, уточните актуальные часы у администратора.',
                'steps': ['Проверить расписание', 'Утвердить публикацию'],
                'caution': 'Не обещать неподтвержденную запись',
            }
            return {'choices': [{'message': {'content': json.dumps({'offers': [row] * 3}, ensure_ascii=False)}}]}

    class MockClient:
        def __init__(self, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            pass
        async def post(self, url, **kwargs):
            sent.update(kwargs)
            assert url.endswith('/v1/chat/completions')
            return MockResponse()

    monkeypatch.setattr(server.httpx, 'AsyncClient', MockClient)
    resp = client.post('/api/generate', json={
        'goal': 'Заполнить завтра три свободных часа',
        'business': {'name': 'Студия', 'city': 'Екатеринбург', 'voice': 'Дружелюбно', 'channels': 'Telegram', 'budget': 0,
                     'services': [{'name': 'Окрашивание', 'price': 4500, 'duration': 180}]}
    })
    assert resp.status_code == 200, resp.text
    assert len(resp.json()['offers']) == 3
    assert 'copy' in resp.json()['offers'][0]
    assert sent['headers']['OpenAI-Project'] == 'test_folder'
    assert sent['headers']['Authorization'] == 'Api-Key test_secret_not_real'
