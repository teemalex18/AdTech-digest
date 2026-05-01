# Source Recon 2026-05-01 17:39

## Условия тестирования

**Среда исполнения:** облачный CI/CD (Claude Code sandbox, Linux)

**Сетевые ограничения, выявленные до тестирования:**

- **curl (Bash):** все внешние хосты заблокированы сетевым прокси среды.
  Любой curl-запрос возвращает `HTTP_CODE=403 SIZE=21` с телом `Host not in allowlist`.
  Это **не ответ сайта** — это ограничение исполняющей среды.
  Переменная окружения `CLAUDE_CODE_PROXY_RESOLVES_HOSTS=true` подтверждает,
  что DNS и TCP идут через внутренний прокси с жёстким allowlist.

- **WebFetch:** инструмент работает через инфраструктуру Anthropic, обходя
  ограничение среды. Все 11 источников вернули `HTTP 403` — IP Anthropic-прокси
  блокируется российскими сайтами (геоблок / bot-protection / datacenter IP filter).

- **RSS через curl:** невозможно (те же ограничения среды).
  **RSS через WebFetch:** все попытки вернули `HTTP 403`.

> **Вывод:** ни один из трёх методов доступа не работает из данной облачной среды.
> Для реального сбора данных нужна среда с российским IP или с IP вне datacenter-диапазонов,
> либо использование внешнего RSS-агрегатора (например, Feedly API, Inoreader API).

---

## 1. ppc.world

### Главная: https://ppc.world/news/
- **WebFetch:** HTTP 403, тело не возвращается
- **curl + UA:** недоступно — `Host not in allowlist` в среде исполнения
- **Свежие материалы 28-30.04 видны в HTML:** НЕТ (контент не получен)
- **Извлечение дат:** не определено

### RSS-проверка:
- `/rss`: HTTP 403 (WebFetch)
- `/rss/`: HTTP 403 (WebFetch)
- `/rss.xml`: не тестировалось (curl заблокирован)
- `/feed`: не тестировалось
- `/feed/`: HTTP 403 (WebFetch)
- `/feed.xml`: не тестировалось
- `/atom.xml`: не тестировалось
- `/news/rss`: не тестировалось
- `/news/rss.xml`: не тестировалось
- **РАБОЧИЙ RSS:** не найден

### Рекомендация:
Тестировать из среды с российским IP. Ожидаемый метод: curl+UA или прямой RSS.
WebFetch из облака блокируется. ppc.world — WordPress-based сайт, вероятно имеет `/feed/`.

---

## 2. AdIndex

### URL-разделы:
- https://adindex.ru/news/releases/
- https://adindex.ru/news/marketing/
- https://adindex.ru/news/adv/

#### https://adindex.ru/news/releases/
- **WebFetch:** HTTP 403
- **curl + UA:** `Host not in allowlist`
- **Свежие материалы 28-30.04:** НЕТ (контент не получен)
- **Извлечение дат:** не определено

#### https://adindex.ru/news/marketing/
- **WebFetch:** HTTP 403
- **curl + UA:** `Host not in allowlist`

#### https://adindex.ru/news/adv/
- **WebFetch:** HTTP 403
- **curl + UA:** `Host not in allowlist`

### RSS-проверка (домен adindex.ru):
- `/rss`: HTTP 403 (WebFetch)
- `/rss.xml`: HTTP 403 (WebFetch)
- `/rss/news.xml`: HTTP 403 (WebFetch)
- `/feed`: не тестировалось (curl заблокирован)
- `/feed/`: не тестировалось
- **РАБОЧИЙ RSS:** не найден

### Рекомендация:
Тестировать из среды с российским IP. adindex.ru — крупный отраслевой портал,
исторически имел RSS-ленту на `/rss/news.xml`. Приоритет: RSS из другой среды.

---

## 3. Yandex

### Главная: https://yandex.ru/adv/news
- **WebFetch:** HTTP 403
- **curl + UA:** `Host not in allowlist`
- **Свежие материалы 28-30.04:** НЕТ (контент не получен)
- **Извлечение дат:** не определено

### RSS-проверка (yandex.ru/adv):
- `/adv/rss`: HTTP 403 (WebFetch)
- `/rss`: не тестировалось
- `/feed`: не тестировалось
- **РАБОЧИЙ RSS:** не найден

### Рекомендация:
Yandex — наиболее агрессивный блокировщик bot-трафика. Высокая вероятность,
что потребуется авторизация или JS-рендеринг (SPA). Рассмотреть парсинг
через Яндекс.API или RSS Яндекс.Новостей как альтернативу.

---

## 4. Avito

### Главная: https://ads.avito.com/blog
- **WebFetch:** HTTP 403
- **curl + UA:** `Host not in allowlist`
- **Свежие материалы 28-30.04:** НЕТ (контент не получен)
- **Извлечение дат:** не определено

### RSS-проверка (ads.avito.com):
- `/blog/feed/`: не тестировалось (curl заблокирован)
- `/blog/rss/`: не тестировалось
- `/rss`: не тестировалось
- `/feed`: не тестировалось
- **РАБОЧИЙ RSS:** не найден

### Рекомендация:
ads.avito.com — маркетинговый блог Avito для рекламодателей. Вероятно Next.js/React SPA.
Тестировать curl+UA из среды с нероссийским нешаблонным IP. Возможен API-эндпоинт блога.

---

## 5. Ozon Seller

### URL-разделы:
- https://seller.ozon.ru/media/boost/
- https://seller.ozon.ru/media/

#### https://seller.ozon.ru/media/boost/
- **WebFetch:** HTTP 403
- **curl + UA:** `Host not in allowlist`
- **Свежие материалы 28-30.04:** НЕТ
- **Извлечение дат:** не определено

#### https://seller.ozon.ru/media/
- **WebFetch:** HTTP 403
- **curl + UA:** `Host not in allowlist`

### RSS-проверка (seller.ozon.ru):
- `/media/feed/`: HTTP 403 (WebFetch)
- `/rss`: не тестировалось
- `/feed`: не тестировалось
- `/media/boost/rss/`: HTTP 403 (WebFetch)
- **РАБОЧИЙ RSS:** не найден

### Рекомендация:
Ozon Seller — портал на современном React-стеке. Контент может подгружаться через
API-запросы. Искать публичный API `/api/media/articles` или аналогичный при тестировании
из незаблокированной среды.

---

## 6. Wildberries

### URL-разделы:
- https://pro.wildberries.ru/insight/
- https://pro.wildberries.ru/

#### https://pro.wildberries.ru/insight/
- **WebFetch:** HTTP 403
- **curl + UA:** `Host not in allowlist`
- **Свежие материалы 28-30.04:** НЕТ
- **Извлечение дат:** не определено

#### https://pro.wildberries.ru/
- **WebFetch:** HTTP 403
- **curl + UA:** `Host not in allowlist`

### RSS-проверка (pro.wildberries.ru):
- `/insight/rss/`: HTTP 403 (WebFetch)
- `/insight/feed/`: не тестировалось
- `/rss`: не тестировалось
- `/feed`: не тестировалось
- **РАБОЧИЙ RSS:** не найден

### Рекомендация:
WB Pro — корпоративный портал Wildberries для продавцов. Вероятно строгая
bot-protection. Приоритет: curl+UA с реальным браузерным UA из нероссийской
незаблокированной среды. Возможен Cloudflare-блок.

---

## 7. eLama

### Главная: https://elama.ru/blog/
- **WebFetch:** HTTP 403
- **curl + UA:** `Host not in allowlist`
- **Свежие материалы 28-30.04:** НЕТ (контент не получен)
- **Извлечение дат:** не определено

### RSS-проверка (elama.ru):
- `/blog/feed/`: HTTP 403 (WebFetch)
- `/blog/rss/`: HTTP 403 (WebFetch)
- `/rss`: не тестировалось
- `/feed`: не тестировалось
- **РАБОЧИЙ RSS:** не найден

### Рекомендация:
eLama — блог маркетинговой платформы, вероятно на WordPress (стандартный `/feed/`).
Из среды с правильным IP должен быть доступен через curl+UA или через `/blog/feed/`.

---

## 8. Magnetto

### Главная: https://magnetto.pro/media/news/
- **WebFetch:** HTTP 403
- **curl + UA:** `Host not in allowlist`
- **Свежие материалы 28-30.04:** НЕТ (контент не получен)
- **Извлечение дат:** не определено

### RSS-проверка (magnetto.pro):
- `/rss/`: HTTP 403 (WebFetch)
- `/feed/`: HTTP 403 (WebFetch)
- `/media/news/rss/`: не тестировалось
- `/rss`: не тестировалось
- **РАБОЧИЙ RSS:** не найден

### Рекомендация:
magnetto.pro — небольшой профессиональный ресурс. Меньший трафик означает меньше
bot-protection. Вероятно доступен через curl+UA из нешаблонной среды. Приоритет при
следующем тесте: curl+UA + `/media/news/`.

---

## 9. MTS Marketolog

### Главная: https://marketolog.mts.ru/blog
- **WebFetch:** HTTP 403
- **curl + UA:** `Host not in allowlist`
- **Свежие материалы 28-30.04:** НЕТ (контент не получен)
- **Извлечение дат:** не определено

### RSS-проверка (marketolog.mts.ru):
- `/blog/rss/`: HTTP 403 (WebFetch)
- `/blog/feed/`: HTTP 403 (WebFetch)
- `/rss`: не тестировалось
- `/feed`: не тестировалось
- **РАБОЧИЙ RSS:** не найден

### Рекомендация:
Корпоративный блог МТС Маркетолог. Вероятно SPA или WordPress. Проверить
наличие открытого API блога. Из незаблокированной среды — curl+UA.

---

## 10. Sostav

### URL-разделы:
- https://www.sostav.ru/
- https://www.sostav.ru/news/

#### https://www.sostav.ru/
- **WebFetch:** HTTP 403
- **curl + UA:** `Host not in allowlist`
- **Свежие материалы 28-30.04:** НЕТ
- **Извлечение дат:** не определено

#### https://www.sostav.ru/news/
- **WebFetch:** HTTP 403
- **curl + UA:** `Host not in allowlist`

### RSS-проверка (sostav.ru):
- `/rss/`: HTTP 403 (WebFetch)
- `/rss.xml`: HTTP 403 (WebFetch)
- `/rss/news.xml`: HTTP 403 (WebFetch)
- `/feed`: не тестировалось
- **РАБОЧИЙ RSS:** не найден

### Рекомендация:
Sostav — одно из крупнейших рекламных медиа России. Исторически имел RSS.
Высокий приоритет для тестирования из среды с российским IP. Вероятный
рабочий путь: `/rss/news.xml` или `/rss.xml`.

---

## 11. SEOnews

### URL-разделы:
- https://www.seonews.ru/
- https://www.seonews.ru/events/

#### https://www.seonews.ru/
- **WebFetch:** HTTP 403
- **curl + UA:** `Host not in allowlist`
- **Свежие материалы 28-30.04:** НЕТ
- **Извлечение дат:** не определено

#### https://www.seonews.ru/events/
- **WebFetch:** HTTP 403
- **curl + UA:** `Host not in allowlist`

### RSS-проверка (seonews.ru):
- `/rss/`: HTTP 403 (WebFetch)
- `/rss.xml`: HTTP 403 (WebFetch)
- `/rss/news/`: HTTP 403 (WebFetch)
- `/feed`: не тестировалось
- **РАБОЧИЙ RSS:** не найден

### Рекомендация:
SEOnews — специализированное медиа по SEO/digital. Исторически имел RSS.
Приоритетные пути для проверки из другой среды: `/rss/`, `/rss.xml`.

---

# Сводная таблица

| # | Источник | Лучший метод | URL | Свежие материалы есть |
|---|----------|--------------|-----|-----------------------|
| 1 | ppc.world | не определён | https://ppc.world/news/ | НЕТ (нет доступа) |
| 2 | AdIndex | не определён | https://adindex.ru/news/releases/ | НЕТ (нет доступа) |
| 3 | Yandex | не определён | https://yandex.ru/adv/news | НЕТ (нет доступа) |
| 4 | Avito | не определён | https://ads.avito.com/blog | НЕТ (нет доступа) |
| 5 | Ozon Seller | не определён | https://seller.ozon.ru/media/ | НЕТ (нет доступа) |
| 6 | Wildberries | не определён | https://pro.wildberries.ru/insight/ | НЕТ (нет доступа) |
| 7 | eLama | не определён | https://elama.ru/blog/ | НЕТ (нет доступа) |
| 8 | Magnetto | не определён | https://magnetto.pro/media/news/ | НЕТ (нет доступа) |
| 9 | MTS Marketolog | не определён | https://marketolog.mts.ru/blog | НЕТ (нет доступа) |
| 10 | Sostav | не определён | https://www.sostav.ru/news/ | НЕТ (нет доступа) |
| 11 | SEOnews | не определён | https://www.seonews.ru/ | НЕТ (нет доступа) |

---

# Итого

- **Источников проверено:** 11
- **Доступны через WebFetch:** 0 (все вернули HTTP 403 — IP Anthropic-прокси заблокирован)
- **Доступны через curl+UA:** 0 (среда исполнения блокирует все внешние хосты: `Host not in allowlist`)
- **Доступны через RSS:** 0 (RSS-эндпоинты также возвращают HTTP 403 через WebFetch; curl заблокирован)
- **Полностью недоступны:** 11

---

# Технический анализ блокировок

## Почему curl не работает

Исполняющая среда (Claude Code sandbox) использует сетевой прокси с allowlist.
Переменная `CLAUDE_CODE_PROXY_RESOLVES_HOSTS=true` подтверждает принудительную
маршрутизацию TCP через внутренний прокси. Список разрешённых хостов включает
только служебные эндпоинты (api.anthropic.com и т.п.).

```
$ curl ... https://ppc.world/news/
HTTP_CODE=403 SIZE=21
body: "Host not in allowlist"
```

## Почему WebFetch не работает

WebFetch использует инфраструктуру Anthropic и приходит с IP из диапазонов
AWS/GCP/Azure. Российские новостные сайты массово блокируют запросы с datacenter IP:
- Геоблок (US/EU IP → блок)
- Bot-protection (Cloudflare, DDoS-Guard, QRATOR) — блокируют datacenter IP
- Прямая блокировка диапазонов облачных провайдеров

## Рекомендации для следующего запуска разведки

1. **Запустить curl-тесты с VPS с российским IP** или нешаблонным residential IP
2. **Использовать RSS-агрегаторы с API:** Feedly, Inoreader, NewsBlur — они уже
   имеют кэшированные фиды российских сайтов
3. **Проверить GitHub Actions runner с другим IP** — если у проекта есть self-hosted runner
4. **Добавить хосты в allowlist среды** через настройки Claude Code, если возможно
5. **Приоритетные RSS-пути для проверки вне данной среды:**
   - adindex.ru/rss/news.xml
   - www.sostav.ru/rss/news.xml
   - www.seonews.ru/rss/
   - elama.ru/blog/feed/
   - ppc.world/feed/
