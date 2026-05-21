# KoStreet API

Base local URL:

```text
http://localhost:8000
```

Versioned API prefix:

```text
/api/v1
```

OpenAPI docs:

```text
http://localhost:8000/docs
```

## Health

```text
GET /health
GET /api/v1/health
```

## Reports

```text
GET /api/v1/reports
POST /api/v1/reports
```

Report categories:

- `pothole`
- `garbage`
- `broken_streetlight`
- `blocked_sidewalk`
- `damaged_sign`
- `other`

Ticket statuses:

- `new`
- `verified`
- `assigned`
- `in_progress`
- `resolved`
- `rejected`

## Street Audit Runs

```text
GET /api/v1/audit-runs
POST /api/v1/audit-runs
```

Audit run statuses:

- `queued`
- `running`
- `completed`
- `failed`

