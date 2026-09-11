\# ClaimTrace



ClaimTrace reconstructs how a claim mutates as it spreads across platforms, distinguishing organic propagation from coordinated amplification. It serves institutional buyers (newsroom standards desks, political monitoring teams, brand reputation teams) who need to know how a claim moved and warped, not just whether it is true\[cite: 3].



\*\*Core Thesis:\*\* The atomic unit worth tracking is the \*mutation edge\*, not the claim in isolation. A single claim cluster is a lineage tree — each edge represents one hop with a measurable change in language, framing, or facts.



\## System Architecture

\*   \*\*Database:\*\* PostgreSQL with `pgvector`.

\*   \*\*Backend:\*\* FastAPI, processing inputs via a deterministic (non-agentic) pipeline\[cite: 2].

\*   \*\*Frontend:\*\* Vite + D3.js timeline-based mutation river visualization\[cite: 1, 3].

\*   \*\*Infrastructure:\*\* Three-service Docker Compose split (`api`, `worker`, `db`)\[cite: 1].



\## Quickstart

1\.  Copy `backend/.env.example` to `backend/.env` and fill in API keys.

2\.  Run `docker-compose up --build` to start the API, the background watcher, and the database.

3\.  Apply Alembic migrations.

