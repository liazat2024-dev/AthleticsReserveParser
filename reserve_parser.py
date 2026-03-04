import requests
import json

BASE = "https://reserve.la55.ru/api/comp/blind_champ_2026-03-04"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def get_json(url):
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.json()


def main():
    final_data = []

    # 1️⃣ Получаем список всех событий
    events = get_json(BASE)

    for event in events:
        event_block = {
            "date": event["date"],
            "time": event["time"],
            "event": event["event"],
            "category": event["cat"],
            "races": []
        }

        # 2️⃣ Проходим по race
        for race_id in event["races"]:
            unit_url = f"{BASE}/unit/{race_id}"

            try:
                unit_data = get_json(unit_url)
            except:
                continue

            race_block = {
                "race_id": race_id,
                "results": []
            }

            # 3️⃣ Если есть участники
            if "lines" in unit_data:
                for athlete in unit_data["lines"]:
                    race_block["results"].append({
                        "rank": athlete.get("rank"),
                        "name": athlete.get("name"),
                        "region": athlete.get("obl"),
                        "result": athlete.get("result"),
                        "attempts": athlete.get("results")
                    })

            event_block["races"].append(race_block)

        final_data.append(event_block)

    # 4️⃣ Сохраняем JSON
    with open("reserve_la55_news.json", "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
