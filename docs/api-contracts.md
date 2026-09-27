# Контракти API (етап 1)

Усі сервіси мають `GET /health` та автоматичну документацію OpenAPI (`/docs`, `/openapi.json`).

## auth-service (порт 8001)

| Метод | Шлях | Тіло / заголовки | Відповідь |
|---|---|---|---|
| POST | `/api/v1/auth/register` | `{email, password}` (пароль ≥ 8 символів) | `201 {id, email, role}`; `409` — користувач існує |
| POST | `/api/v1/auth/login` | `{email, password}` | `200 {access_token, token_type}`; `401` |
| GET | `/api/v1/auth/me` | `Authorization: Bearer <JWT>` | `200 {id, email, role}`; `401` |

Паролі хешуються Argon2id, токени — JWT (HS256), строк дії задається `ACCESS_TOKEN_TTL_MINUTES`.

## forecast-service (порт 8002)

| Метод | Шлях | Параметри | Відповідь |
|---|---|---|---|
| GET | `/api/v1/forecast` | `lat` ∈ [-90; 90], `lon` ∈ [-180; 180] | `200 Forecast`; `422` — некоректні координати; `503` — усі постачальники недоступні |

`Forecast`: `latitude, longitude, provider, updated_at, cached, current{temperature_c, humidity_pct, pressure_hpa, wind_speed_ms, precipitation_mm, cloud_cover_pct}, hourly_temperature_c[48]`.

Постачальники опитуються за пріоритетом (основний — Open-Meteo), за збою використовується наступний. Відповіді кешуються 10 хв у комірці ≈1 км.

## history-service (порт 8003)

Ідентифікатор користувача на етапі 1 передається заголовком `X-User-Id` (на наступних етапах — з JWT через шлюз).

| Метод | Шлях | Параметри | Відповідь |
|---|---|---|---|
| POST | `/api/v1/history` | `{location, latitude, longitude, forecast_snapshot}` | `201 HistoryRecord` |
| GET | `/api/v1/history` | `location`, `page`, `size` (≤100) | `200 {items, total, page, size}` |
| DELETE | `/api/v1/history/{id}` | — | `204`; `404` — чужий або відсутній запис |
| GET | `/api/v1/history/export` | `fmt=json\|csv` | файл експорту |
