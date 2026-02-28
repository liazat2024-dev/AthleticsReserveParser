import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os

# ===== Настройки =====
BASE_URL = "https://reserve.la55.ru/"
DATE_START = datetime(2026, 2, 27)
JSON_PATH = "reserve_la55_news.json"  # сохраняем в корень репозитория

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ===== Парсинг =====
def fetch_and_parse():
    try:
        r = requests.get(BASE_URL, headers=HEADERS)
        r.raise_for_status()
    except Exception as e:
        print("Ошибка запроса:", e)
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    lines = soup.get_text("\n").split("\n")
    results = []

    for line in lines:
        text = line.strip()
        if not text:
            continue
        parts = text.split(" ")
        for p in parts:
            if "." in p and len(p) >= 8:
                try:
                    dt = datetime.strptime(p, "%d.%m.%Y")
                    if dt >= DATE_START:
                        results.append(text)
                    break
                except:
                    pass
    return results

# ===== Сохранение JSON =====
def save_json(news_list):
    unique = list(dict.fromkeys(news_list))  # убираем дубликаты
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)
    print(f"Сохранено {len(unique)} записей в {JSON_PATH}")

# ===== Основная функция =====
def main():
    news = fetch_and_parse()
    if news:
        save_json(news)
    else:
        print("Новостей не найдено")

if __name__ == "__main__":
    main()