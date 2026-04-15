# AgentSuite Production-Quality Architecture

## Overview
AgentSuite is an AI agent platform with Next.js (TypeScript + Tailwind) frontend and FastAPI (Python) backend. Designed for scalability, real-time chat, and clean separation of concerns.

## 1. Folder Structure

```
agentsuite/
├── README.md                    # Project overview + setup
├── docker-compose.yml           # Postgres + Redis + dev/prod services
├── .env.example                 # Environment variables template
├── .gitignore
│
├── frontend/                    # Next.js 14+ (App Router)
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── package.json
│   ├── .env.local
│   ├── public/favicon.ico
│   └── src/
│       ├── app/
│       │   ├── layout.tsx
│       │   ├── page.tsx
│       │   └── agents/[id]/
│       │       └── page.tsx
│       ├── components/
│       │   ├── ui/             # shadcn/ui
│       │   ├── AgentCard.tsx
│       │   └── ChatInterface.tsx
│       ├── lib/
│       │   ├── api.ts          # Axios/TanStack Query
│       │   └── utils.ts
│       ├── hooks/
│       │   └── useChat.ts
│       ├── types/agent.ts
│       └── store/              # Zustand
│           └── useAgents.ts
│
├── backend/                     # FastAPI
│   ├── requirements.txt
│   ├── pyproject.toml          # Poetry
│   ├── main.py
│   ├── Dockerfile
│   └── app/
│       ├── __init__.py
│       ├── main.py             # FastAPI(app)
│       ├── database.py         # SQLModel + Alembic
│       ├── core/
│       │   ├── config.py
│       │   └── security.py
│       ├── api/
│       │   └── v1/
│       │       ├── endpoints/
│       │       │   ├── agents.py
│       │       │   └── chat.py
│       │       └── api.py
│       ├── schemas/
│       │   ├── agent.py
│       │   └── chat.py
│       ├── crud/
│       │   └── agent.py
│       └── services/
│           └── llm.py          # LiteLLM integration
│
└── infra/                       # Future: Terraform/Docker
```

## 2. API Contract (OpenAPI auto-generated)

**Base:** `/api/v1`

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| GET | `/health` | Health check | - | `{status: 'ok'}` |
| GET | `/agents` | List agents | - | `Agent[]` |
| POST | `/agents` | Create agent | `AgentCreate` | `Agent` |
| GET | `/agents/{agent_id}` | Get agent | - | `Agent` |
| POST | `/agents/{agent_id}/chat` | Chat (stream support) | `ChatRequest` | `ChatResponse \| Stream` |
| WS | `/ws/{agent_id}/chat` | Real-time streaming | JSON messages | SSE token stream |

**Schemas:**
```python
from pydantic import BaseModel
from typing import List
from uuid import UUID

class AgentCreate(BaseModel):
    name: str
    description: str
    model: str = 'gpt-4o-mini'
    system_prompt: str = ''

class Agent(AgentCreate):
    id: UUID

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    stream: bool = False
```

## 3. Data Flow Diagram

```
User Input (ChatInterface.tsx)
         ↓
useChat hook → POST /api/v1/agents/{id}/chat
         ↓ (TanStack Query + streaming)
FastAPI endpoint → LLMService.chat(messages)
         ↓
LiteLLM → OpenAI/Anthropic (streaming)
         ↓
SQLModel ORM → Postgres (history)
         ↓ (SSE/WebSocket)
ChatInterface → Optimistic UI + Zustand store
         ↓
Rendered Response
```

## 4. Implementation Phases

**Phase 1: Foundation (Day 1)**
- Setup monorepo + Docker Compose (Postgres)
- Backend: FastAPI + /health + DB models
- Frontend: Next.js + Tailwind + Agent list

**Phase 2: Core Features (Days 2-3)**
- Backend: Agent CRUD + chat endpoint + LiteLLM
- Frontend: Chat UI + real-time streaming (SSE)
- Shared validation (Zod/Pydantic)

**Phase 3: Production Polish (Day 4)**
- Auth (JWT), error boundaries, loading states
- Tests (Vitest/Pytest), CI (GitHub Actions)
- Deploy (Vercel frontend, Render backend)

**Phase 4: Scale (Day 5+)**
- Redis caching, rate limiting
- Monitoring (Sentry), migrations (Alembic)

**Commands to start:**
```bash
docker-compose up -d
cd backend && uvicorn app.main:app --reload
cd frontend && npm run dev
```

**Scalability:** Stateless services, DB sharding ready, Kubernetes compatible.

