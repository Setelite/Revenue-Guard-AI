# Revenue Guard AI

Мобильный интерфейс: https://setelite.github.io/Revenue-Guard-AI/


## Запуск и тестирование дома без оплаты хостинга

Это можно сделать на **Windows**. Нужен установленный Python 3.11+ и интернет для первой установки зависимостей. **Платная аренда хостинга не требуется.** 

1. Скачайте проект через GitHub → **Code → Download ZIP**, распакуйте в обычную папку.
2. Запустите двойным щелчком `run_local_test_windows.bat`. Скрипт установит библиотеки, затем проведёт **бесплатный тест с имитацией Cloud.ru**. Никаких токенов не списывается.
3. После успешного бесплатного теста можно выбрать второй вариант — **реальный платный запрос** к Cloud.ru. Система отдельно спросит разрешение, а ключ вводится скрыто в терминале. Ключ не записывается в файл и не загружается в GitHub.
4. Для работы с интерфейсом на компьютере используйте `python local_app.py` (без ИИ, без тарифицируемых запросов) или `python local_app.py --real` (с реальным Cloud.ru). Откройте **http://127.0.0.1:8000**. В реальном режиме терминал покажет отдельный временный код доступа, который нужно ввести в «Бизнес → Подключение ИИ» вместе с адресом `http://127.0.0.1:8000`.
5. Введите тестовую задачу без данных настоящих клиентов. Остановка локального сервера: **Ctrl+C**.

Можно и без Windows-файла: `python -m pip install -r requirements.txt`, затем `python local_probe.py` для бесплатной имитации, `python local_probe.py --real` для настоящего Cloud.ru.

**Статус:** тесты с имитацией проверяют API-контракт, но не качество реальных ответов модели. Живой запрос к Cloud.ru должен быть запущен на вашем компьютере с личным ключом. Не публикуйте ни сам ключ, ни временный код доступа.

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

## Визуальные материалы

Главная страница использует открытые демонстрационные фотографии с Unsplash. Это иллюстрации интерфейса, а не фотографии клиентов или выполненных работ:

- [Alexandra Tran — cosmetics flat lay](https://unsplash.com/photos/a-table-topped-with-lots-of-different-types-of-cosmetics-vOJDvdBYYzQ)
- [Ozkan Guner — makeup artist](https://unsplash.com/photos/a-woman-in-a-white-shirt-is-smiling-and-holding-makeup-brushes-EGZ7CTBSmF8)
- [Vitaly Gariev — studio makeup](https://unsplash.com/photos/makeup-artist-applying-makeup-to-a-model-in-studio-f9qZXRNtXGc)
- [Sonia Roselli — skincare](https://unsplash.com/photos/white-and-pink-labeled-pump-bottle-4ib07-bBqIc)

Используются фотографии, обозначенные на их страницах как *Free to use under the Unsplash License*. Фото требуют загрузки из интернета; без сети страница остаётся читаемой на цветных фонах.
