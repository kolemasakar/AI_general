# OpenAI: retirement Custom GPTs і перехід до Plugins

**Дата перевірки:** 2026-09-16  
**Статус:** офіційно підтверджений напрямок переходу  
**Тема:** наслідки для вже опублікованих Custom GPTs і GPTs у розробці

## Висновок

Станом на 16 вересня 2026 року OpenAI офіційно заявила про план retirement Custom GPTs у ChatGPT на всіх планах і перехід до моделі Plugins. Це не просте перейменування GPT у Plugin і не гарантована 1:1 міграція.

Для розробника змінюється сама одиниця продукту:

- інструкції GPT мають переходити у **skills**;
- зовнішні сервіси та дані — у **apps / connectors / MCP-based integrations**;
- старі Custom Actions не переносяться автоматично;
- модель, conversation starters, історія чатів та частина GPT-specific UX не мають гарантії повного переносу;
- migrated GPT стає read-only до моменту retirement;
- replacement plugin спочатку private, тому публічність і доступ не успадковуються автоматично.

Практичний висновок: нові серйозні проєкти варто вже проєктувати навколо workflow/skill + integrations, а Custom GPT розглядати як тимчасовий deployment wrapper до завершення переходу.

---

## 1. Що саме оголосила OpenAI

OpenAI офіційно повідомила про retirement Custom GPTs та migration path до Plugins.

Основні офіційні джерела:

- [ChatGPT Release Notes](https://help.openai.com/en/articles/6825453-chatgpt-release-notes)
- [Custom GPT retirement and migration FAQ](https://help.openai.com/en/articles/20001519-custom-gpt-retirement-and-migration-faq)
- [Plugins in ChatGPT and Codex](https://help.openai.com/en/articles/20001256)

Це означає, що стратегічна модель змінюється від окремих кастомних ботів до reusable workflow-компонентів, які ChatGPT може використовувати як skills та apps.

---

## 2. Що буде з уже опублікованими Custom GPTs

Існуючі GPT не зникають миттєво. До дати retirement вони продовжують працювати.

Для affected Enterprise OpenAI описала орієнтовний графік:

| Дата | Подія |
|---|---|
| 2026-09-11 | Оголошення та підготовка |
| 2026-09-17 | Цільова дата появи migration experience |
| 2026-09-25 | Планове припинення створення нових Custom GPTs |
| 2026-12-11 | Запланований retirement Custom GPTs |

Важливо: ці дати позначені як planned/target і можуть змінюватися. Для інших планів OpenAI також оголосила перехід, але точний календар може відрізнятися і має підтверджуватися in-product notice конкретного акаунта/workspace.

### Після міграції

За офіційним FAQ:

- старий GPT продовжує працювати до retirement;
- після migration він стає **read-only**;
- редагування продовжується вже у replacement plugin;
- після retirement старий GPT перестає запускатися;
- він має зникнути з GPT directory;
- OpenAI планує redirect старого GPT link на replacement plugin, якщо користувач має до нього доступ.

### Важливе обмеження для публічних GPTs

Публічний GPT не стає автоматично публічним Plugin.

Replacement plugin спочатку створюється **private**. Sharing/access треба налаштовувати заново. Старий доступ до GPT не означає автоматичний доступ до replacement plugin.

У перевірених офіційних матеріалах немає гарантії автоматичного переносу:

- рейтингу GPT;
- reviews;
- usage counters;
- ranking / Store position;
- інших GPT Store metrics.

Тому існуючу позицію в GPT Store не варто вважати гарантовано переносимим активом.

---

## 3. Що переноситься, а що ні

| Компонент Custom GPT | Очікувана доля |
|---|---|
| Instructions | → Skill у plugin |
| Connected apps | → Apps у plugin |
| Reference files / templates / examples | Потребують перевірки після міграції |
| Conversation starters | Можуть не перенестися |
| Previous chats | Можуть не перенестися |
| Selected model | Не переноситься |
| Custom Actions | Не переносяться автоматично |
| Sharing/access | Налаштовуються заново |
| Сам GPT | Після migration стає read-only |

Отже, migration не можна вважати повним clone GPT у Plugin.

---

## 4. Custom Actions — головний технічний ризик

OpenAI прямо вказує, що GPT custom actions не переносяться через migration workflow.

Якщо GPT використовує:

- OpenAPI Actions;
- власний backend;
- OAuth;
- API integration;
- складний workflow з зовнішніми сервісами,

цю частину треба окремо переоцінювати та, ймовірно, перебудовувати через supported connector або custom MCP server.

Практично це означає, що Custom Actions варто вже зараз розглядати як legacy integration layer, а не як довгострокову архітектурну основу.

---

## 5. Що робити з GPTs, які ще в розробці

Для описаного Enterprise migration flow draft GPT не можна мігрувати напряму. GPT має бути **published**.

При цьому published не обов'язково означає public: GPT можна опублікувати без розміщення у GPT Store та без публічного sharing.

OpenAI рекомендує опублікувати drafts, які потрібно мігрувати, до відповідного cutoff.

Для affected Enterprise поточний planned cutoff — 2026-09-25.

### Практична стратегія

Для GPT, що зараз у розробці:

1. Зберегти основну цінність у чітких instructions/workflow.
2. Винести reference assets у структуровані файли.
3. Створити regression suite з типових і складних prompts.
4. Окремо задокументувати всі Actions/API/OAuth dependencies.
5. Не вкладати зайві ресурси у GPT-specific UX, якщо він не потрібен для короткострокового запуску.
6. Якщо проєкт потрібно мігрувати через офіційний workflow — довести його до published state до cutoff.
7. Після міграції перевірити:
   - вибір правильного skill;
   - використання reference materials;
   - формат output;
   - складні edge cases;
   - integrations;
   - permissions і sharing.

---

## 6. Концептуальна зміна архітектури

### Раніше

**Persona + Instructions + Knowledge + Tools → окремий Custom GPT**

### Нова модель

**Plugin = Skills + Apps + Integrations → reusable capability для ChatGPT**

Тобто конкурентна перевага зміщується від:

> «у мене є хороший кастомний бот»

до:

> «у мене є добре спроєктований workflow/skill, якісні reference assets і потрібні data/actions».

ChatGPT може автоматично вибирати релевантний installed skill за його description, тому plugin не обов'язково є окремою «персоною», яку користувач відкриває вручну.

---

## 7. Рекомендації залежно від стану проєкту

| Стан проєкту | Рекомендована дія |
|---|---|
| GPT уже public / GPT Store | Зберегти instructions, knowledge, integration specs, regression prompts; готувати міграцію; не вважати Store distribution гарантовано переносимим |
| GPT published, але private/link-only | Хороший кандидат для migration workflow |
| GPT draft, майже готовий | Для affected Enterprise — publish до cutoff, навіть без public sharing |
| GPT тільки почали розробляти | Проєктувати логіку вже як skill/workflow |
| GPT із Custom Actions | Планувати окрему міграцію на connector/MCP |
| GPT переважно instructions + knowledge | Найпростіший тип для переходу, але потрібні regression tests |
| GPT залежить від конкретної selected model | Відв'язати логіку від конкретно вибраної моделі |

---

# ПЕРЕВІРКА ТВЕРДЖЕНЬ

## 1. OpenAI планує retirement Custom GPTs на користь Plugins

**Вердикт:** ПІДТВЕРДЖЕНО  
**Cross-check:** 1/1 — PASS

Офіційні Release Notes та Help Center підтверджують напрямок переходу.

## 2. Для affected Enterprise вказані milestones 17.09 / 25.09 / 11.12.2026

**Вердикт:** ПІДТВЕРДЖЕНО  
**Cross-check:** 1/1 — PASS

Дати позначені як planned/target і можуть змінитися.

## 3. Точний Enterprise calendar гарантовано застосовується до всіх personal plans

**Вердикт:** НЕ ПІДТВЕРДЖЕНО  
**Cross-check:** 1/1 — PASS

Retirement заявлений ширше, але plan-specific timing та exceptions можуть відрізнятися.

## 4. Migration повністю відтворює старий GPT

**Вердикт:** СУПЕРЕЧИТЬ ДЖЕРЕЛАМ  
**Cross-check:** 1/1 — PASS

Custom Actions не мігрують автоматично, model selection не переноситься, starters/chats можуть не перейти.

## 5. Public GPT автоматично залишиться public як Plugin

**Вердикт:** СУПЕРЕЧИТЬ ДЖЕРЕЛАМ  
**Cross-check:** 1/1 — PASS

Replacement plugin starts private; sharing треба налаштовувати заново.

## 6. Draft GPT можна мігрувати напряму

**Вердикт:** СУПЕРЕЧИТЬ ДЖЕРЕЛАМ для описаного Enterprise workflow  
**Cross-check:** 1/1 — PASS

GPT має бути published, хоча public sharing не потрібен.

## 7. Після migration старий GPT залишається editable

**Вердикт:** СУПЕРЕЧИТЬ ДЖЕРЕЛАМ  
**Cross-check:** 1/1 — PASS

Migrated original GPT стає read-only.

---

# ПІДСУМОК ЗА ТВЕРДЖЕННЯМИ

| Твердження | Потрібно | Отримано незалежних | Виняток |
|---|---:|---:|---|
| OpenAI планує retirement Custom GPTs | 1 | 1 | НЕМАЄ |
| Enterprise milestones 17.09 / 25.09 / 11.12.2026 | 1 | 1 | НЕМАЄ |
| Точні Enterprise dates гарантовано застосовуються до всіх personal plans | 1 | 1 | НЕМАЄ — твердження не підтверджено |
| Migration не є повним 1:1 clone | 1 | 1 | НЕМАЄ |
| Public access не переноситься автоматично | 1 | 1 | НЕМАЄ |
| Enterprise drafts не мігруються напряму | 1 | 1 | НЕМАЄ |
| Migrated original GPT стає read-only | 1 | 1 | НЕМАЄ |

---

# ПРОТОКОЛ ПЕРЕВІРКИ

**Домен:** програмні продукти / ChatGPT platform / Custom GPT → Plugin migration  
**Рівень ризику:** СЕРЕДНІЙ  
**Мінімум перехресної перевірки:** 1 незалежне evidence origin на матеріальне твердження  
**Вимога до свіжості:** актуальна документація OpenAI станом на 2026-09-16  
**Затверджено користувачем:** 2026-09-16T16:57:00+03:00

Основними джерелами були офіційні матеріали OpenAI: Help Center та ChatGPT Release Notes.

Під час критичної перевірки окремо виправлено ризик надмірного узагальнення Enterprise-дат на всі плани.

**Фінальна перевірка:** PASS  
**Оцінка надійності:** 0.95

## Невирішені обмеження

OpenAI поки не дала однаково деталізований календар для кожного personal/Business plan.

У перевірених матеріалах також не документовано гарантований перенос:

- GPT Store ratings;
- reviews;
- ranking;
- usage history;
- інших distribution metrics.

Ці частини слід вважати невизначеними до появи окремої офіційної документації.

---

## Джерела

1. OpenAI — ChatGPT Release Notes  
   https://help.openai.com/en/articles/6825453-chatgpt-release-notes

2. OpenAI — Custom GPT retirement and migration FAQ  
   https://help.openai.com/en/articles/20001519-custom-gpt-retirement-and-migration-faq

3. OpenAI — Plugins in ChatGPT and Codex  
   https://help.openai.com/en/articles/20001256
