import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

BASE_URL = "https://reserve.la55.ru/"
DATE_START = datetime(2026, 2, 27)
JSON_PATH = "reserve_la55_news.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def fetch_and_parse():
    r = requests.get(BASE_URL, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    lines = [l.strip() for l in soup.get_text("\n").split("\n") if l.strip()]

    event_data = {
        "city": "",
        "event": "",
        "date_start": "",
        "date_end": "",
        "schedule": [],
        "results": []
    }

    capture = False

    for i, line in enumerate(lines):

        # Определяем город
        if line == "Тюмень":
            event_data["city"] = line

        # Определяем даты
        try:
            dt = datetime.strptime(line, "%d.%m.%Y")
            if dt >= DATE_START:
                capture = True
                if not event_data["date_start"]:
                    event_data["date_start"] = line
                else:
                    event_data["date_end"] = line
        except:
            pass

        if not capture:
            continue

        # Название соревнования
        if "ПЕРВЕНСТВО" in line:
            event_data["event"] = line

        # Расписание (время + дисциплина)
        if ":" in line and len(line) <= 5:
            if i + 2 < len(lines):
                event_data["schedule"].append({
                    "time": line,
                    "discipline": lines[i + 1],
                    "category": lines[i + 2]
                })

        # Результаты (место + имя + регион + результат)
        if line.isdigit():
            if i + 3 < len(lines):
                name = lines[i + 1]
                region = lines[i + 2]
                result = lines[i + 3]
                if any(c.isdigit() for c in result):
                    event_data["results"].append({
                        "place": int(line),
                        "name": name,
                        "region": region,
                        "result": result
                    })

    return event_data


def save_json(data):
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    data = fetch_and_parse()
    save_json(data)
    print("JSON обновлён")


if __name__ == "__main__":
    main()
