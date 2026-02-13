# Log Handler Api

Backend REST API for collecting, storing and analyzing error events from
multiple applications.\
This project was created for recruitment and technical evaluation
purposes.

## Notes

All environment variables and secrets are stored in `.env` file for
**testing and recruitment purposes only**.\
In production environments, secrets should be stored using secure secret
management solutions (e.g. Vault, cloud secret managers, etc.).

## Running the Project

Build and start the project using:

``` bash
docker compose up --build
```

After startup:

-   API: http://localhost:8000\
-   Swagger: http://localhost:8000/docs

------------------------------------------------------------------------

## API Overview

Base path:

    /apps

------------------------------------------------------------------------

## Applications

### Create application

    POST /apps/{name}

Response includes **ingest_key** (required to send events for this
application later):

``` json
{
  "id": 1,
  "name": "my-app",
  "ingest_key": "0123456789abcdef...",
  "created_at": "2026-02-10T10:00:00Z"
}
```

------------------------------------------------------------------------

### Get application

    GET /apps/{app_id}

------------------------------------------------------------------------

### List applications

    GET /apps/

------------------------------------------------------------------------

## Events

### Ingest event (requires header)

    POST /apps/{app_id}/events

Header:

    X-INGEST-KEY: <ingest_key>

Body example:

``` json
{
  "occurred_at": "2026-02-10T10:00:00Z",
  "level": "ERROR",
  "message": "TimeoutError: request timed out",
  "stack": {"frames": []},
  "tags": {"env": "prod", "version": "1.2.3"}
}
```

------------------------------------------------------------------------

### List events (pagination + filters)

    GET /apps/{app_id}/events?limit=20&offset=0&level=ERROR&since=...&until=...

Parameters:

-   `limit`: 1..50\
-   `offset`: 0+\
-   optional:
    -   `level`
    -   `since`
    -   `until`\
        (filters are applied to `received_at` field)

Response:

``` json
{
  "items": [ ... ],
  "next_offset": 20
}
```

------------------------------------------------------------------------

## Statistics

All statistics are calculated using `received_at`.

------------------------------------------------------------------------

### Timeseries

    GET /apps/{app_id}/stats/timeseries?since=...&until=...&interval=HOUR&level=ERROR

Response:

``` json
{
  "interval": "HOUR",
  "since": "2026-02-10T00:00:00Z",
  "until": "2026-02-11T00:00:00Z",
  "series": [
    { "bucket_start": "2026-02-10T10:00:00Z", "count": 42 }
  ]
}
```

------------------------------------------------------------------------

### By level

    GET /apps/{app_id}/stats/by-level?since=...&until=...

Response:

``` json
{
  "since": "2026-02-10T00:00:00Z",
  "until": "2026-02-11T00:00:00Z",
  "items": [
    { "level": "INFO", "count": 40 },
    { "level": "ERROR", "count": 21 }
  ]
}
```

------------------------------------------------------------------------

### Top messages

    GET /apps/{app_id}/stats/top-messages?since=...&until=...&limit=10&level=ERROR

Response:

``` json
{
  "limit": 10,
  "items": [
    {
      "message": "TimeoutError: request timed out",
      "count": 18,
      "last_seen": "2026-02-10T22:05:00Z"
    }
  ]
}
```

------------------------------------------------------------------------

## Technical Notes (MVP Scope)

-   Only event ingestion endpoint uses authentication (`X-INGEST-KEY`)
-   Pagination is implemented using `limit/offset`
-   `stack` and `tags` fields are stored using PostgreSQL `JSONB`
-   Statistics are based on `received_at` timestamp
