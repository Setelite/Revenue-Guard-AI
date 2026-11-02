import os
import json
from fastapi.testclient import TestClient
import server

client = TestClient(server.app)
TOKEN = 'test-code-for-local-tests-only-123456'

def headers():
    return {'X-Demo-Token': TOKEN}

def valid_request():
    return {'goal': 'Нужно заполнить свободные окна завтра',
            'business': {'name': 'Салон', 'city': 'Екатеринбург', 'voice': 'Дружелюбно',
                         'channels': 'Telegram', 'budget': 0,
                         'services': [{'name': 'Маникюр', 'price': 2500, 'duration': 90}]}}

def test_front_and_safe_files():
    assert client.get('/').status_code == 200
    assert client.get('/manifest.webmanifest').status_code == 200
    assert client.get('/server.py').status_code == 404
    assert client.get('/.env').status_code == 404

def test_access_required(monkeypatch):
    monkeypatch.setenv('RG_DEMO_ACCESS_TOKEN', TOKEN)
    assert client.get('/api/status').status_code == 401
    assert client.post('/api/generate', json=valid_request()).status_code == 401

def test_status_without_provider(monkeypatch):
    monkeypatch.setenv('RG_DEMO_ACCESS_TOKEN', TOKEN)
    monkeypatch.setenv('AI_PROVIDER', 'cloudru')
    monkeypatch.delenv('CLOUDRU_API_KEY', raising=False)
    r = client.get('/api/status', headers=headers())
    assert r.status_code == 200
    assert r.json()['ai_enabled'] is False
    assert client.post('/api/generate', headers=headers(), json=valid_request()).status_code == 503

def test_provider_contract(monkeypatch):
    monkeypatch.setenv('RG_DEMO_ACCESS_TOKEN', TOKEN)
    monkeypatch.setenv('AI_PROVIDER', 'cloudru')
    monkeypatch.setenv('CLOUDRU_API_KEY', 'fake_key')
    server.attempts.clear()
    seen = {}
    class MockResponse:
        def raise_for_status(self):
            pass
        def json(self):
            offer = {'title': 'Свободные часы', 'reason': 'Сообщить аудитории',
                     'channel': 'Telegram салона', 'description': 'Публикация',
                     'headline': 'Свободное время', 'copy': 'Запишитесь на маникюр, уточните время у мастера.',
                     'steps': ['Проверить расписание', 'Утвердить материалы'],
                     'caution': 'Ничего не публиковать без подтверждения'}
            return {'choices': [{'message': {'content': json.dumps({'offers':[offer]*3}, ensure_ascii=False)}}]}
    class MockClient:
        def __init__(self, **kwargs): pass
        async def __aenter__(self): return self
        async def __aexit__(self, *args): pass
        async def post(self, url, **kwargs):
            seen.update(kwargs)
            assert url == 'https://foundation-models.api.cloud.ru/v1/chat/completions'
            return MockResponse()
    monkeypatch.setattr(server.httpx, 'AsyncClient', MockClient)
    r = client.post('/api/generate', headers=headers(), json=valid_request())
    assert r.status_code == 200, r.text
    assert len(r.json()['offers']) == 3
    assert seen['headers']['Authorization']=='Bearer fake_key'
    assert seen['json']['model']=='ai-sage/GigaChat3-10B-A1.8B'
    assert seen['json']['response_format']=={'type':'json_object'}
    assert seen['json']['max_completion_tokens']==2500

def test_yandex_remains_optional(monkeypatch):
    monkeypatch.setenv('AI_PROVIDER', 'yandex')
    monkeypatch.setenv('YANDEX_API_KEY', 'test_key')
    monkeypatch.setenv('YANDEX_FOLDER_ID', 'test_folder')
    config, name = server.provider_config()
    assert name == 'Yandex AI Studio'
    assert config['url'] == 'https://ai.api.cloud.yandex.net/v1/chat/completions'
    assert config['model'] == 'gpt://test_folder/yandexgpt-5.1'
