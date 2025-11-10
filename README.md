# 🪷 Lotus

**Personal AI Task Companion** | Transform reactive task management into intelligent, proactive partnership

---

## What is Lotus?

Lotus is a desktop application that continuously observes your digital environment (Slack DMs, Google Meet transcripts) to automatically infer tasks using agentic AI. It transforms buried commitments into visible, actionable items displayed on a clean, Notion-style task board.

**Core Innovation:** Lotus doesn't just log tasks you manually enter—it *discovers* them from your conversations and meetings, then intelligently prepares context so you can act immediately.

---

## Phase 1: Core MVP (Current Sprint)

**Goal:** Prove the core concept with a working application that demonstrates intelligent task inference.

### Key Features
- ✅ Ingest Slack direct messages and Google Meet transcripts
- ✅ Use agentic AI (LangGraph + Claude API) to infer tasks with 70%+ accuracy
- ✅ Display tasks on minimal, draggable Notion-style board
- ✅ Store all data locally in SQLite (privacy-first)
- ✅ Hybrid local/cloud LLM strategy for cost optimization (<$5/month)

### Success Criteria
- Infer 5+ tasks from real Slack/Google data
- 70%+ task inference accuracy
- Drag-and-drop status updates (To Do → In Progress → Done)
- Full local data storage with no mandatory cloud dependencies

---

## Technology Stack

### Backend
- **Python 3.11** - Core language
- **FastAPI** - REST API server
- **LangGraph** - Multi-agent orchestration framework
- **SQLAlchemy** - ORM for SQLite
- **Ollama** - Local LLM runtime (Llama 3.2, Mistral)
- **Claude Sonnet 4** - Cloud LLM for complex reasoning

### Frontend
- **Electron** - Cross-platform desktop app
- **React + TypeScript** - UI framework
- **Tailwind CSS** - Styling
- **Vite** - Build tool

### Data Storage
- **SQLite** - Local relational database
- **ChromaDB** - Vector database for semantic search (Phase 2)

### APIs & Integrations
- **Slack API** - Direct message ingestion
- **Google Meet API** - Transcript ingestion
- **Anthropic Claude API** - Task inference

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Electron Desktop App                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │             React Frontend (UI Layer)                 │  │
│  │  • TaskBoard (Notion-style drag-and-drop)             │  │
│  │  • SettingsPanel (OAuth, API keys)                    │  │
│  │  • TaskDetailView (context, confidence scores)        │  │
│  └───────────────────────────────────────────────────────┘  │
│                            │                                 │
│                    HTTP (localhost:8000)                     │
│                            │                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │           Python FastAPI Backend (subprocess)         │  │
│  │                                                         │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │         LangGraph Agents                        │  │  │
│  │  │  • TaskInferenceAgent (multi-node workflow)     │  │  │
│  │  │  • ContextWeaverAgent (Phase 2)                 │  │  │
│  │  │  • PriorityOrchestratorAgent (Phase 3)          │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  │                                                         │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │         Integrations                            │  │  │
│  │  │  • SlackClient (DM ingestion)                   │  │  │
│  │  │  • GoogleMeetClient (transcript ingestion)      │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  │                                                         │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │         LLM Clients                             │  │  │
│  │  │  • OllamaClient (local, bulk operations)        │  │  │
│  │  │  • ClaudeClient (cloud, complex reasoning)      │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
│                            │                                 │
│                     SQLite (data/lotus.db)                   │
│                            │                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         Local Data Storage                            │  │
│  │  • Tasks (id, title, description, status, etc.)       │  │
│  │  • Messages (Slack DMs, encrypted)                    │  │
│  │  • Transcripts (Google Meet, encrypted)              │  │
│  │  • OAuth Tokens (encrypted)                           │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
lotus/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── agents/          # LangGraph agentic AI workflows
│   │   │   ├── task_inference.py
│   │   │   ├── context_weaver.py (Phase 2)
│   │   │   └── llm_clients.py
│   │   ├── api/             # FastAPI routes
│   │   │   ├── tasks.py
│   │   │   ├── auth.py
│   │   │   └── integrations.py
│   │   ├── integrations/    # External API clients
│   │   │   ├── slack_client.py
│   │   │   └── google_client.py
│   │   ├── models/          # SQLAlchemy ORM models
│   │   │   ├── task.py
│   │   │   ├── message.py
│   │   │   └── transcript.py
│   │   ├── utils/           # Helpers
│   │   │   ├── encryption.py
│   │   │   └── date_parser.py
│   │   ├── main.py          # FastAPI app entry point
│   │   └── config.py        # Settings (loads from .env)
│   ├── scripts/
│   │   └── init_db.py       # Database initialization
│   ├── tests/               # pytest tests
│   └── requirements.txt     # Python dependencies
├── frontend/                # Electron + React frontend
│   ├── public/              # Static assets
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── TaskBoard.tsx
│   │   │   ├── TaskCard.tsx
│   │   │   └── SettingsPanel.tsx
│   │   ├── api/             # Axios API client
│   │   │   └── client.ts
│   │   ├── types/           # TypeScript types
│   │   ├── utils/           # Frontend helpers
│   │   ├── main.ts          # Electron main process
│   │   └── App.tsx          # React app root
│   ├── package.json         # npm dependencies
│   └── electron-builder.yml # Build configuration
├── data/                    # Local data (gitignored)
│   ├── lotus.db             # SQLite database
│   ├── logs/                # Application logs
│   └── chroma/              # ChromaDB vector store
├── docs/                    # Documentation
├── .env.example             # Environment variable template
├── .gitignore
├── claude.md                # Project directives for Claude Code
└── README.md                # This file
```

---

## Getting Started

### Prerequisites

**Required:**
- Python 3.11+
- Node.js 18+
- npm or yarn
- Ollama (for local LLM)
- Git

**Optional but Recommended:**
- Anthropic Claude API key (for task inference)
- Slack workspace with Developer App configured
- Google Cloud project with Meet API enabled

### Installation

#### 1. Clone Repository
```bash
git clone <repository-url>
cd lotus
```

#### 2. Set Up Environment Variables
```bash
cp .env.example .env
# Edit .env with your actual API keys and configuration
```

#### 3. Set Up Backend
```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python scripts/init_db.py
```

#### 4. Set Up Ollama (Local LLM)
```bash
# Install Ollama (see https://ollama.ai)
ollama serve

# Pull models (in separate terminal)
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

#### 5. Set Up Frontend
```bash
cd frontend

# Install dependencies
npm install
```

### Running the Application

#### Terminal 1: Start Ollama
```bash
ollama serve
```

#### Terminal 2: Start Backend
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

#### Terminal 3: Start Frontend
```bash
cd frontend
npm run dev
```

The Electron app will launch automatically. Backend API runs at `http://localhost:8000`.

---

## Development Workflow

### Running Tests
```bash
# Backend tests
cd backend
pytest -v
pytest --cov=app tests/  # With coverage

# Linting
ruff check .
ruff format .
```

### Database Management
```bash
# Inspect database
sqlite3 data/lotus.db
.tables
.schema tasks
SELECT * FROM tasks LIMIT 10;

# Reset database (WARNING: deletes all data)
rm data/lotus.db
python scripts/init_db.py
```

### Building for Production
```bash
cd frontend
npm run build  # Creates distributable .dmg (macOS), .exe (Windows), .AppImage (Linux)
```

---

## Guiding Principles

1. **Local-First, Privacy-Respecting** - All data stored locally by default
2. **Hybrid Cloud/Local LLM** - Use local models for bulk ops, Claude for complex reasoning (<$5/month)
3. **Agentic Workflow with LangGraph** - Stateful, graph-based agent orchestration
4. **Fail Gracefully with Transparency** - Surface errors clearly, show agent reasoning
5. **Test-Driven Development** - All agent logic must have unit tests with mocked LLM responses

See `claude.md` for detailed development guidelines.

---

## Roadmap

### Phase 1: Core MVP (Week 1) ✅ Current
- Slack DM ingestion
- Google Meet transcript ingestion
- Task inference with LangGraph
- Minimal task board UI
- Local storage (SQLite)

### Phase 2: Context Weaving (Week 2-3)
- ContextWeaverAgent (auto-prepare meeting summaries, research)
- Email integration (Gmail)
- Browser history integration (Chrome extension)
- Task detail view with rich context

### Phase 3: Intelligent Prioritization (Week 4-5)
- PriorityOrchestratorAgent (dynamic prioritization)
- Calendar integration (Google Calendar, Outlook)
- Smart notifications (urgent tasks, deadline reminders)
- Cross-tool task correlation

### Phase 4: Full Workspace Integration (Month 2+)
- Project management tools (Jira, Asana, Linear)
- Document integration (Google Docs, Notion)
- Code repository integration (GitHub PRs, issue tracking)
- Multi-workspace support

---

## Architecture Decisions

### Why Hybrid Electron + Python?
- **Electron:** Beautiful cross-platform UI with React/TypeScript
- **Python:** Best AI/ML ecosystem (LangGraph, LangChain, Ollama)
- **FastAPI:** Clean REST API for frontend-backend communication
- **Benefit:** Parallel UI updates while agents work in background

### Why LangGraph?
- Stateful, graph-based approach perfect for complex task inference
- Supports human-in-the-loop and debugging via state inspection
- Extensible for Phase 2+ multi-agent orchestration
- Aligns with learning goals for agentic AI

### Why SQLite?
- Zero-config, lightweight, perfect for single-user desktop apps
- No external database server required
- Built-in Python support
- Easy encryption for sensitive data

### Why Hybrid LLM Strategy?
- **Local (Ollama):** Free, fast, bulk operations (classification, summarization)
- **Cloud (Claude):** High accuracy, complex reasoning (task inference)
- **Cost:** <$5/month with <50 Claude API calls/day
- **Privacy:** Process most data locally, only send curated prompts to cloud

---

## Security & Privacy

- **Local Data Storage:** All tasks, messages, transcripts stored in local SQLite
- **Encrypted Credentials:** OAuth tokens encrypted using `cryptography` library
- **No Telemetry:** Zero data sent to Lotus servers (none exist!)
- **API Keys in .env:** Never hardcoded, never committed to Git
- **Prompt Injection Prevention:** System prompts constrain LLM behavior

---

## Contributing

This is a personal learning project for Phase 1. Contributions welcome in Phase 2+!

### Development Process
1. Read `claude.md` for project directives
2. Follow test-driven development for agent logic
3. Commit frequently with clear messages
4. Run linters and tests before pushing

---

## License

MIT License - See LICENSE file for details

---

## Acknowledgments

- **LangChain/LangGraph** - Agentic AI framework
- **Anthropic Claude** - Task inference LLM
- **Ollama** - Local LLM runtime
- **FastAPI** - Python web framework
- **Electron** - Cross-platform desktop framework

---

## Contact & Support

For questions, issues, or feature requests, please open an issue on GitHub.

**Built with ❤️ using Claude Code and agentic AI**
