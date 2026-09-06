# DND Adventure — Project Context

## Purpose
This repository is an existing web application being developed as a D&D-style adventure/game interface. It is **not a new project**. Future work must preserve the existing architecture, authentication, database, deployment, and UI unless explicitly requested otherwise.

Repository: `uplink0/devops-survival`
Main branch: `main`
Production domain: `https://atlas-infra.ru`

## Stack
- Frontend: React + TypeScript + Vite
- Backend: FastAPI + SQLAlchemy
- Database: PostgreSQL 16
- Authentication: JWT + Argon2 password hashing
- Frontend web server: Nginx inside the frontend Docker image
- Local/prod app container port: host `8088` → Nginx `80`
- Production orchestration: Docker Compose behind a k3s/Traefik setup
- CI/CD: GitHub Actions

## Architecture
Browser → Traefik → Kubernetes Service/EndpointSlice → Docker Compose frontend on host port 8088 → Nginx → FastAPI backend → PostgreSQL.

Nginx proxies:
- `/api/*` → `backend:8000`
- `/uploads/*` → `backend:8000/uploads/`
- everything else → React SPA (`index.html` fallback)

There is no separate Nginx ingress. Traefik handles public HTTPS routing.

## Production server
- Hostname: `AtlasInfra`
- IP: `194.147.215.29`
- OS: Ubuntu 24.04 LTS
- Docker: 29.8.0
- k3s: v1.36.4+k3s1
- Node: `atlasinfra.com`, Ready control-plane
- Public ports: 80/443 through Traefik
- App Docker Compose host port: 8088

Do not expose PostgreSQL publicly.
Do not run `docker compose down -v` because it destroys the PostgreSQL persistent volume.

## Deployment
GitHub Actions workflow: `.github/workflows/ci-cd.yml`

Push to `main`:
1. GitHub Actions validates frontend and backend.
2. Workflow SSHes to production.
3. Server performs `git pull`.
4. Docker Compose rebuilds/restarts the application.
5. Workflow checks `http://localhost:8088/api/health` with retries.

When changing deployment code, verify CI rather than assuming it passed.

## Database and migrations
Alembic is the migration system.
Current migrations include:
- `0001_initial.py`
- `0002_dnd_entities.py`
- `0003_character.py`
- `0004_gold.py`

Backend entrypoint handles an existing legacy schema by stamping `0001_initial` when needed, then runs `alembic upgrade head`.
Do not replace Alembic with `Base.metadata.create_all`.

Persistent Docker volumes:
- `postgres_data` — PostgreSQL data
- `uploads_data` — avatar uploads

## Authentication
Existing routes include:
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`

Authentication/login/registration must remain functional.

## Main API routes
- `GET /api/health`
- `GET /api/profile`
- `POST /api/progress`
- `GET /api/leaderboard`
- `GET /api/inventory`
- `GET /api/shop`
- `POST /api/shop/buy`
- `GET /api/companions`
- `GET /api/chat`
- `POST /api/chat`
- `DELETE /api/chat`
- `POST /api/avatar`
- `POST /api/character`
- `DELETE /api/character`
- `POST /api/inventory/use/{item_key}`

## Current UI/navigation
Main menu tabs:
- Главная
- Инвентарь
- Персонаж
- Кампания
- Настройки

Navigation is currently SPA state/custom-event based; do not introduce React Router unless explicitly requested.

The right-hand global sidebar component is still named `CompanionsPanel.tsx`, but it currently represents the global shop/sidebar UI. Do not rename it casually.

## Visual direction
The UI is a light parchment/fantasy interface:
- warm paper backgrounds
- brown/gold borders
- Georgia/serif used for fantasy headings/content
- Inter/system font for interface text
- moderately large, bold readable text
- subtle shadows and hover/click transitions

Keep the visual language consistent. Avoid generic modern SaaS styling.

## Character creation
Character data:
- name
- race
- class
- background
- six stats: STR, DEX, CON, INT, WIS, CHA

Classes:
- Воин
- Плут
- Волшебник
- Жрец
- Следопыт
- Варвар
- Бард
- Паладин
- Колдун

Races currently include:
- Человек
- Эльф
- Дварф
- Полурослик
- Полуорк
- Гном
- Тифлинг
- Дроу

Background choices are class-specific and currently defined in `src/main.tsx`.

### Stat rules — IMPORTANT
- Exactly **72 base/manual points** are distributed among the six stats.
- Base/manual stat range: 3–18.
- Racial bonuses are **additional** and do NOT count toward the 72 points.
- Final stat can therefore exceed 18.
- Racial bonuses must NEVER be recalculated from manual stat changes.
- Manual editing changes only base stats.
- Racial bonuses change only when the race changes.

Current racial bonuses:
- Human: +1 all stats
- Elf: +2 DEX
- Dwarf: +2 CON
- Halfling: +2 DEX
- Half-orc: +2 STR, +1 CON
- Gnome: +2 INT
- Tiefling: +2 CHA, +1 INT
- Drow: +2 DEX, +1 CHA

The UI should show base/manual value, fixed racial bonus (blank when zero), and final value separately.

## Inventory
Current catalog/properties:
- potion — consumable — healing +20 HP — 0.5 kg
- torch — equipment — 1d4 fire — 0.5 kg
- dagger — weapon — 1d4 piercing — range 5 ft — 1 kg
- shortsword — weapon — 1d6 piercing — range 5 ft — 1 kg
- leather_armor — armor — 5 kg
- mana_scroll — magic — one-time spell — 0.1 kg
- antidote — consumable — removes poison — 0.3 kg
- rope — equipment — 10 m rope — 2 kg

Shop prices:
- potion 20
- torch 8
- dagger 35
- shortsword 60
- leather_armor 75
- mana_scroll 45
- antidote 30
- rope 12

New characters start with 100 gold.

### Consumable/reusable rules
One-time consumables:
- potion
- torch
- mana_scroll
- antidote

Reusable items:
- dagger
- shortsword
- leather_armor
- rope

Only the consumables should have their inventory quantity decremented by the use endpoint. Reusable equipment remains in inventory.

## Inventory combat flow
From **Главная → Чат мастера → Варианты действий → Использовать инвентарь**:
1. Enter inventory use mode.
2. Navigate to the Inventory tab.
3. Clicking an item selects/uses it.
4. Return to Главная → Чат мастера.
5. Chat displays that the item was used and asks for a d20 hit roll.
6. If hit (currently 10+ on d20), ask for damage roll.
7. Damage die mapping currently:
   - dagger → d4
   - shortsword → d6
   - torch → d4
   - mana_scroll → d6
   - fallback → d4

IMPORTANT: This special use flow must only activate when Inventory was reached through the **Использовать инвентарь** action. Opening Inventory through the normal menu must only allow selecting an item to view its description; it must not use the item.

## DM chat
Chat is persisted in PostgreSQL.
- `GET /api/chat` loads history.
- `POST /api/chat` stores user messages.
- `DELETE /api/chat` clears the current user's chat history.

Current chat UI:
- Header: `МАСТЕР ПРИКЛЮЧЕНИЯ`
- Clear button: `Очистить чат`
- Player messages display the **character name** (fallback to username if no character name exists).
- Assistant messages display **Мастер**.
- The old explanatory block about AI being connected later should not occupy the chat message area.

The actual AI Dungeon Master backend is not implemented yet. Current chat persistence is real, but assistant responses are not yet a full AI integration.

## Current important frontend files
- `src/main.tsx` — main SPA shell, character creation data and pages
- `src/api.ts` — API client/types
- `src/context/GameContext.tsx` — game state, dice, quest actions, inventory combat flow
- `src/components/DmChat.tsx` — DM chat UI
- `src/components/InventoryPage.tsx` — inventory page/use-mode handling
- `src/components/MainMenu.tsx` — menu/navigation
- `src/components/CompanionsPanel.tsx` — global sidebar/shop
- `src/components/HeroHud.tsx` — top HUD
- `src/styles.css` — global/layout styles
- `src/character.css` — character page/creator styles
- `src/components/dm-chat.css` — DM chat-specific styling

## Important development rules
1. Inspect the existing implementation before changing it.
2. Do not rebuild the project from scratch.
3. Preserve working authentication, database persistence, migrations, deployment, and routing.
4. Make small focused changes.
5. After significant changes, run the existing CI/build workflow or at minimum validate the relevant build locally.
6. Never claim CI/CD is green without checking the actual workflow result.
7. Keep secrets out of Git. `.env`/production secrets must remain server-side.
8. Do not commit real passwords, JWT secrets, SSH keys, or API keys.
9. When modifying a file, preserve unrelated existing functionality.
10. For future AI integration, keep the current chat API contract unless there is a concrete reason to change it.

## How to continue from another ChatGPT account
Connect the GitHub account with access to this repository, open the repository, and first read this file plus the current source code.

Suggested first prompt:

"Продолжаем разработку существующего DND Adventure приложения. Репозиторий `uplink0/devops-survival`. Прочитай `PROJECT_CONTEXT.md`, затем изучи текущую реализацию и последние изменения в `main`. Ничего не создавай заново. Дальше будем вносить изменения по одному запросу."
