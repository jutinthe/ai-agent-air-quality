# Aeris Research UI

A polished Next.js frontend for the Air Quality–Health Research Agent.

## Run

```bash
npm install
cp .env.local.example .env.local
npm run dev
```

Open `http://localhost:3000`.

The FastAPI backend should be running at `http://127.0.0.1:8000`.

## Backend endpoints used

- `POST /api/papers/upload`
- `POST /api/papers/{paper_id}/extract`

## Notes

The dashboard includes demo records so it looks complete before your database layer is implemented. Real uploaded papers use the backend API.
