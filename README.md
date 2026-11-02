# Revenue Guard AI

Мобильный интерфейс: https://setelite.github.io/Revenue-Guard-AI/

## Cloud.ru Foundation Models

В коде сервера теперь два провайдера: Cloud.ru (по умолчанию) и Yandex (резервный).
При отсутствии своего сервера приложение использует демонстрационные шаблоны.

Для подключения:
1. Откройте Cloud.ru → AI Factory → Foundation Models.
2. Создайте сервисный аккаунт уровня проекта и API-ключ для Foundation Models.
3. На собственном сервере с Python 3.11+ создайте файл `.env` по `.env.example`.
4. Задайте `AI_PROVIDER=cloudru`, `CLOUDRU_API_KEY`, `CLOUDRU_MODEL=ai-sage/GigaChat3-10B-A1.8B`, а также `RG_DEMO_ACCESS_TOKEN` длиной от 24 символов.
5. Установите зависимости через `pip install -r requirements.txt` и запустите `uvicorn server:app --host 127.0.0.1 --port 8000` за HTTPS-прокси.
6. В приложении откройте «Бизнес → Подключение ИИ», укажите HTTPS-адрес сервера и код доступа `RG_DEMO_ACCESS_TOKEN`. Ключ Cloud.ru в браузер не вводить.
7. Проверьте соединение и выполните тестовую генерацию.

API: https://foundation-models.api.cloud.ru/v1/chat/completions
Документация: https://cloud.ru/docs/foundation-models/ug/topics/quickstart

## Безопасность и готовность

Нельзя публиковать действующие API-ключи в GitHub. Серверный код рассчитан на закрытый пилот с демонстрационными данными и общим кодом доступа, не на публичный SaaS. Проверка статуса подтверждает наличие конфигурации, но не реальное соединение с поставщиком. Промышленный запуск требует отдельных учётных записей, лимитов и защиты клиентских данных.

Тестирование: `python -m pip install -r requirements.txt pytest && python -m pytest -q test_server.py`.
