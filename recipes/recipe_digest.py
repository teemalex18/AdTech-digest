"""
Новый рецепты.
Источники: vkusnyblog (RSS) + say7 (HTML).

Настройки:
  TG_BOT_TOKEN  — токен бота
  TG_CHAT_ID    — chat_id получателя (узнать через @userinfobot или написать боту /start)
  DAYS_BACK     — сколько дней назад брать рецепты (по умолчанию 7)

Запуск:
  python recipe_digest.py

Для еженедельного запуска — добавить в cron или Task Scheduler.
"""

import datetime
import os
import re

import feedparser
import requests
from bs4 import BeautifulSoup

# --- Настройки ---
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "ВАШ_ТОКЕН_СЮДА")
TG_CHAT_ID   = os.environ.get("TG_CHAT_ID",   "ВАШ_CHAT_ID_СЮДА")
DAYS_BACK    = int(os.environ.get("DAYS_BACK", "7"))
# -----------------

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ru-RU,ru;q=0.9",
}


def date_from(days_back):
    return datetime.date.today() - datetime.timedelta(days=days_back)


def parse_say7_date(text):
    """Парсит дату вида '19.05.2026' из текста."""
    m = re.search(r"(\d{2})\.(\d{2})\.(\d{4})", text)
    if m:
        return datetime.date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
    return None


def fetch_vkusnyblog(since):
    """Берёт рецепты из RSS vkusnyblog за период с since."""
    url = "https://www.vkusnyblog.com/feed/"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"[vkusnyblog] Ошибка загрузки фида: {e}")
        return []

    feed = feedparser.parse(resp.content)
    recipes = []

    for entry in feed.entries:
        # Дата публикации
        pub = entry.get("published_parsed") or entry.get("updated_parsed")
        if not pub:
            continue
        pub_date = datetime.date(pub.tm_year, pub.tm_mon, pub.tm_mday)
        if pub_date < since:
            continue

        title = entry.get("title", "").strip()
        link  = entry.get("link", "").strip()
        if title and link:
            recipes.append({
                "source": "Вкусный блог",
                "title": title,
                "url": link,
                "date": pub_date,
            })

    return recipes


def fetch_say7(since):
    """Парсит рецепты со страницы say7, отсортированной по дате."""
    url = "https://www.say7.info/cook/linkqi_order-3.html"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"[say7] Ошибка загрузки страницы: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    recipe_list = soup.find("div", id="recipes-list")
    if not recipe_list:
        print("[say7] Не найден блок #recipes-list")
        return []

    recipes = []

    for li in recipe_list.find_all("li"):
        a = li.find("a", href=True)
        if not a:
            continue

        # Заголовок — текст ссылки без alt картинки
        img = a.find("img")
        if img:
            img.decompose()
        title = a.get_text(strip=True)
        if not title:
            continue

        href = a["href"]
        if not href.startswith("http"):
            href = "https://www.say7.info" + href

        # Дата — берём весь текст <li> и ищем паттерн ДД.ММ.ГГГГ
        pub_date = parse_say7_date(li.get_text(" ", strip=True))
        if not pub_date:
            continue
        if pub_date < since:
            # Страница отсортирована по дате — дальше только старее
            break

        recipes.append({
            "source": "Say7",
            "title": title,
            "url": href,
            "date": pub_date,
        })

    return recipes


def format_message(recipes, since):
    """Форматирует сообщение для Telegram."""
    today = datetime.date.today()

    lines = [
        f"Новые рецепты за {since.strftime('%d.%m')} - {today.strftime('%d.%m.%Y')}",
        "",
    ]

    # Группируем по источнику
    by_source = {}
    for r in recipes:
        by_source.setdefault(r["source"], []).append(r)

    for source, items in by_source.items():
        lines.append(f"📌 {source}")
        for r in items:
            date_str = r["date"].strftime("%d.%m")
            lines.append(f"  {date_str} — {r['title']}")
            lines.append(f"  {r['url']}")
        lines.append("")

    if not recipes:
        lines.append("За период новых рецептов не найдено.")

    return "\n".join(lines).strip()


def send_telegram(text, token, chat_id):
    """Отправляет сообщение в Telegram."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": False,
    }
    try:
        resp = requests.post(url, json=payload, timeout=15)
        data = resp.json()
        if data.get("ok"):
            print("Telegram: сообщение отправлено.")
        else:
            print(f"Telegram error: {data}")
    except Exception as e:
        print(f"Telegram: ошибка отправки: {e}")


def main():
    since = date_from(DAYS_BACK)
    print(f"Собираем рецепты с {since.strftime('%d.%m.%Y')}...")

    recipes = []
    recipes += fetch_vkusnyblog(since)
    recipes += fetch_say7(since)

    # Сортируем по дате — новые первыми
    recipes.sort(key=lambda r: r["date"], reverse=True)

    print(f"Найдено рецептов: {len(recipes)}")
    for r in recipes:
        print(f"  {r['date']} | {r['source']:12s} | {r['title']}")

    message = format_message(recipes, since)
    print("\n--- Сообщение ---")
    print(message)
    print("-----------------\n")

    if TG_BOT_TOKEN == "ВАШ_ТОКЕН_СЮДА" or TG_CHAT_ID == "ВАШ_CHAT_ID_СЮДА":
        print("Токен или chat_id не заданы — Telegram не отправляем.")
        print("Задай переменные TG_BOT_TOKEN и TG_CHAT_ID или впиши прямо в скрипт.")
    else:
        send_telegram(message, TG_BOT_TOKEN, TG_CHAT_ID)


if __name__ == "__main__":
    main()
