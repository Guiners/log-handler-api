# Example API Requests (curl)

This file contains example curl commands to test the API end-to-end.

------------------------------------------------------------------------

## ⚠️ IMPORTANT --- Replace These Values

Before running commands, replace:

-   **APP_ID** → Application ID returned from create app request
-   **INGEST_KEY** → Ingest key returned from create app request

Example: If create app returns:

{ "id": 1, "name": "test-app", "ingest_key": "abc123" }

Then use: APP_ID = 1\
INGEST_KEY = abc123

------------------------------------------------------------------------

## 1️⃣ Create Application

``` bash
curl -X POST http://localhost:8000/apps/test-app
```

✔ Copy from response: - id → APP_ID - ingest_key → INGEST_KEY

------------------------------------------------------------------------

## 2️⃣ Send Events

Replace APP_ID and INGEST_KEY before running.

### Event 1 --- ERROR

``` bash
curl -X POST http://localhost:8000/apps/APP_ID/events   -H "X-INGEST-KEY: INGEST_KEY"   -H "Content-Type: application/json"   -d '{
    "occurred_at": "2026-02-10T10:00:00Z",
    "level": "ERROR",
    "message": "TimeoutError: request timed out",
    "tags": {"env": "prod"}
  }'
```

------------------------------------------------------------------------

### Event 2 --- ERROR

``` bash
curl -X POST http://localhost:8000/apps/APP_ID/events   -H "X-INGEST-KEY: INGEST_KEY"   -H "Content-Type: application/json"   -d '{
    "occurred_at": "2026-02-10T10:05:00Z",
    "level": "ERROR",
    "message": "TimeoutError: request timed out"
  }'
```

------------------------------------------------------------------------

### Event 3 --- INFO

``` bash
curl -X POST http://localhost:8000/apps/APP_ID/events   -H "X-INGEST-KEY: INGEST_KEY"   -H "Content-Type: application/json"   -d '{
    "occurred_at": "2026-02-10T11:00:00Z",
    "level": "INFO",
    "message": "User logged in"
  }'
```

------------------------------------------------------------------------

## 3️⃣ List Events

``` bash
curl "http://localhost:8000/apps/APP_ID/events?limit=50&offset=0"
```

------------------------------------------------------------------------

## 4️⃣ Timeseries Stats

⚠ interval must be lowercase: hour or day

``` bash
curl "http://localhost:8000/apps/APP_ID/stats/timeseries?since=2026-02-10T09:00:00Z&until=2026-02-10T12:00:00Z&interval=hour"
```

------------------------------------------------------------------------

## 5️⃣ Timeseries Stats (Filtered by Level)

``` bash
curl "http://localhost:8000/apps/APP_ID/stats/timeseries?since=2026-02-10T09:00:00Z&until=2026-02-10T12:00:00Z&interval=hour&level=ERROR"
```

------------------------------------------------------------------------

## 6️⃣ By Level Stats

``` bash
curl "http://localhost:8000/apps/APP_ID/stats/by-level?since=2026-02-10T09:00:00Z&until=2026-02-10T12:00:00Z"
```

------------------------------------------------------------------------

## 7️⃣ Top Messages

``` bash
curl "http://localhost:8000/apps/APP_ID/stats/top-messages?since=2026-02-10T09:00:00Z&until=2026-02-10T12:00:00Z&limit=10"
```

------------------------------------------------------------------------

## 8️⃣ Top Messages (Filtered by Level)

``` bash
curl "http://localhost:8000/apps/APP_ID/stats/top-messages?since=2026-02-10T09:00:00Z&until=2026-02-10T12:00:00Z&limit=10&level=ERROR"
```

------------------------------------------------------------------------

## ✔ Expected Result

After sending events: - Timeseries → should show counts per hour -
By-level → should show ERROR, INFO, etc counts - Top messages → should
show most common messages

------------------------------------------------------------------------
