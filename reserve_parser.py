import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import re

BASE_URL = "https://reserve.la55.ru/"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_soup(url):
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")

def parse_images(soup, base_url):
    images = []
    for img in soup.find_all("img"):
        src = img.get("src")
        if src:
            images.append(urljoin(base_url, src))
    return list(set(images))


def parse_results_table(soup):
    results = []

    table = soup.find("table")
    if not table:
        return results

    rows = table.find_all("tr")

    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 5:
            results.append({
                "place": cols[0].get_text(strip=True),
                "number": cols[1].get_text(strip=True),
                "name": cols[2].get_text(strip=True),
                "region": cols[3].get_text(strip=True),
                "result": cols[4].get_text(strip=True)
            })

    return results


def parse_discipline(url):
    soup = get_soup(url)

    discipline = {
        "name": soup.find("h1").get_text(strip=True) if soup.find("h1") else "",
        "images": parse_images(soup, BASE_URL),
        "heats": []
    }

    # ищем ссылку "Забеги"
    for link in soup.find_all("a", href=True):
        if "Забеги" in link.get_text():
            heat_url = urljoin(BASE_URL, link["href"])
            heat_soup = get_soup(heat_url)

            discipline["heats"].append({
                "url": heat_url,
                "images": parse_images(heat_soup, BASE_URL),
                "results": parse_results_table(heat_soup)
            })

    return discipline


def parse_day(url):
    soup = get_soup(url)

    day = {
        "date": "",
        "images": parse_images(soup, BASE_URL),
        "disciplines": []
    }

    # дата дня
    date_match = re.search(r"\d{2}\.\d{2}\.\d{4}", soup.get_text())
    if date_match:
        day["date"] = date_match.group()

    # ищем дисциплины
    for link in soup.find_all("a", href=True):
        if "м" in link.get_text():
            discipline_url = urljoin(BASE_URL, link["href"])
            day["disciplines"].append(parse_discipline(discipline_url))

    return day


def parse_event(event_url):
    soup = get_soup(event_url)

    event_data = {
        "city": "",
        "event": soup.find("h1").get_text(strip=True) if soup.find("h1") else "",
        "date_start": "",
        "date_end": "",
        "images": parse_images(soup, BASE_URL),
        "days": []
    }

    dates = re.findall(r"\d{2}\.\d{2}\.\d{4}", soup.get_text())
    if dates:
        event_data["date_start"] = dates[0]
        if len(dates) > 1:
            event_data["date_end"] = dates[1]

    # ищем ссылки на дни
    for link in soup.find_all("a", href=True):
        if "День" in link.get_text():
            day_url = urljoin(BASE_URL, link["href"])
            event_data["days"].append(parse_day(day_url))

    return event_data


if __name__ == "__main__":
    # ВСТАВЬ СЮДА ССЫЛКУ НА СТРАНИЦУ СОРЕВНОВАНИЯ
    EVENT_URL = "ВСТАВЬ_ССЫЛКУ_СЮДА"

    data = parse_event(EVENT_URL)

    with open("reserve_la55_news.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Парсинг завершён успешно")
