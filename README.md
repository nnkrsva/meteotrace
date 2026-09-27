# MeteoTrace

Вебсервіс прогнозу погоди з історією запитів користувача. Репозиторій містить **етап 1** плану реалізації (ЛР1): базові версії `auth-service`, `forecast-service`, `history-service`, вебінтерфейс і конвеєр CI.

## Структура

```
services/
  auth-service/       FastAPI: реєстрація, вхід, JWT, Argon2id
  forecast-service/   FastAPI: Open-Meteo, нормалізація, кеш, резервний постачальник
  history-service/    FastAPI: історія зі знімком прогнозу, фільтр, пагінація, експорт CSV/JSON
frontend/             React + TypeScript + Vite, Vitest
docs/api-contracts.md контракти API
.github/workflows/ci.yml
```

## Конвеєр CI

Запускається для кожного Pull Request у `main` і після злиття:

| Завдання | Що робить |
|---|---|
| `changes` | визначає змінені сервіси (`dorny/paths-filter`) |
| `secret-scan` | пошук секретів у всій історії (gitleaks) |
| `python-lint` | ruff (лінтер і перевірка форматування) |
| `python-tests` | матриця лише за зміненими сервісами, PyTest, покриття ≥ 75% |
| `frontend` | ESLint, TypeScript, Vitest (покриття ≥ 75%), збірка |
| `ci-success` | підсумкова перевірка, обов'язкова для злиття в `main` |

Гілка `main` захищена: зміни лише через Pull Request з успішним `ci-success`.

## Локальний запуск

```bash
cd services/forecast-service && pip install -r requirements-dev.txt
uvicorn app.main:app --port 8002        # аналогічно auth (8001), history (8003)
pytest --cov=app

cd frontend && npm ci && npm run dev    # http://localhost:5173
npm run lint && npm test
```
