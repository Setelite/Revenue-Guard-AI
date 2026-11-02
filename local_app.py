"""Start Revenue Guard AI on this computer (no hosting fee).

python local_app.py        # offline UI demo, no external AI
python local_app.py --real # optional Cloud.ru model (may use paid tokens)
"""
import getpass
import os
import secrets
import sys

def main():
    live = "--real" in sys.argv
    os.environ["AI_PROVIDER"] = "cloudru"
    if live:
        print("Внимание: реальные обращения к Cloud.ru могут тарифицироваться.")
        if input("Подключить настоящую модель? (да/нет): ").strip().lower() != "да":
            return
        key = getpass.getpass("Введите Cloud.ru Key Secret (не отображается): ").strip()
        if not key:
            print("Ключ пуст. Запуск отменён.")
            return
        os.environ["CLOUDRU_API_KEY"] = key
    else:
        os.environ.pop("CLOUDRU_API_KEY", None)
    os.environ["RG_DEMO_ACCESS_TOKEN"] = secrets.token_urlsafe(32)
    os.environ["RG_ALLOWED_ORIGINS"] = "http://127.0.0.1:8000,http://localhost:8000,https://setelite.github.io"
    import uvicorn

    print("\nRevenue Guard AI — локально, без аренды сервера")
    print("Откройте на компьютере: http://127.0.0.1:8000")
    if live:
        print("В интерфейсе: Бизнес → Подключение ИИ")
        print("Адрес сервера: http://127.0.0.1:8000")
        print("ВРЕМЕННЫЙ код доступа:", os.environ["RG_DEMO_ACCESS_TOKEN"])
        print("Этот код не является ключом Cloud.ru. Не публикуйте его.")
    else:
        print("Работает только шаблонный деморежим; реальный ИИ не вызывается.")
    print("Остановить сервер: Ctrl+C\n")
    try:
        uvicorn.run("server:app", host="127.0.0.1", port=8000, log_level="warning")
    finally:
        os.environ.pop("CLOUDRU_API_KEY", None)

if __name__ == "__main__":
    main()
