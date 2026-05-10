<div align="center">

<br/>

```
  ⬡ QyverixAI
```

# AI Developer Assistant

**Debug. Understand. Ship faster.**

An open-source AI-powered developer assistant that helps beginners
understand code, detect bugs, and improve code quality - with
plain-English explanations and actionable suggestions.

<br/>

[![CI](https://github.com/imDarshanGK/AI-dev-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/imDarshanGK/AI-dev-assistant/actions)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://python.org)
[![GSSoC 2026](https://img.shields.io/badge/GSSoC-2026-orange)](https://gssoc.girlscript.org)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

<br/>

[**Live Demo**](https://qyverixai.onrender.com) · [**API Docs**](https://qyverixai.onrender.com/docs) · [**Contributing Guide**](CONTRIBUTING.md) · [**Good First Issues**](https://github.com/imDarshanGK/AI-dev-assistant/labels/good%20first%20issue)

<br/>

</div>

---

## What is QyverixAI?

Many beginners struggle with reading error messages, understanding what their code does, or knowing how to improve it. QyverixAI solves this with a clean workspace where you paste code and instantly get:

- A **plain-English explanation** - what the code does and why
- A **structured bug report** - what's wrong, which line, and how to fix it
- **Improvement suggestions** - style tips, best practices, and a quality score

No account required. No API key needed to get started. Fully open source.

---

## Features

| Feature | Description |
|---|---|
|  **Code Explanation** | Language detection, summary, key observations, complexity estimate |
|  **Bug Detection** | 15+ rule patterns: ZeroDivisionError, bare excepts, hardcoded secrets, eval(), and more |
|  **Improvement Suggestions** | Pythonic patterns, documentation gaps, dead code, quality score 0–100 |
|  **Full Analysis Endpoint** | One call — all three analyses combined |
|  **File Upload** | Drag-drop or upload `.py`, `.js`, `.java`, `.ts`, `.cpp` files |
|  **Dark / Light Mode** | Persisted theme preference |
|  **Query History** | Last 50 queries saved locally |
|  **Saved Favorites** | Bookmark important results |
|  **Download Results** | Export analysis as `.txt` |
|  **LLM-Ready** | Drop-in OpenAI-compatible API support via env vars |
|  **Swagger Docs** | Full interactive API documentation at `/docs` |

---

## Quick Start

### 1. Clone

```bash
git clone https://github.com/imDarshanGK/AI-dev-assistant.git
cd AI-dev-assistant
```

### 2. Start the backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

| Endpoint | URL |
|---|---|
| API Root | http://localhost:8000/ |
| Interactive Docs | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |

### 3. Open the frontend

```bash
# Open in browser — no build step required
open frontend/index.html
```

Set the API URL in the workspace to `http://localhost:8000` and click **Analyze Code**.

---

## API Reference

All endpoints accept `POST` with JSON body `{ "code": "..." }`.
Optional: `{ "code": "...", "language": "python" }` to override language detection.

### `POST /explanation/`

Returns a plain-English breakdown of the code.

```json
{
  "language": "Python",
  "summary": "This beginner-level Python snippet defines a reusable function...",
  "key_points": [
    "The code is written in Python with 2 lines.",
    "Defines 1 function: add.",
    "No loops or conditionals found."
  ],
  "complexity": "Beginner"
}
```

### `POST /debugging/`

Returns detected issues with line numbers and fix suggestions.

```json
{
  "issues": [
    {
      "type": "Hardcoded Secret",
      "line": 3,
      "description": "Hardcoded password found in code.",
      "suggestion": "Use environment variables: os.getenv('PASSWORD')",
      "severity": "error"
    }
  ],
  "summary": "Found 1 issue. 1 error(s), 0 warning(s).",
  "clean": false
}
```

### `POST /suggestions/`

Returns improvement suggestion cards.

```json
{
  "suggestions": [
    {
      "category": "Documentation",
      "description": "Add docstrings to your functions.",
      "example": "def greet(name: str) -> str:\n    \"\"\"Return a greeting string.\"\"\"",
      "priority": "medium"
    }
  ],
  "overall_score": 80,
  "next_step": "Great code! Consider adding tests next."
}
```

### `POST /analyze/`

All three analyses in one response.

```json
{
  "provider": "rule-based",
  "model": "built-in",
  "explanation": { ... },
  "debugging": { ... },
  "suggestions": { ... }
}
```

---

## Project Structure

```
AI-dev-assistant/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, middleware, routes
│   │   ├── schemas.py           # Pydantic request/response models
│   │   ├── routers/
│   │   │   ├── analyze.py       # POST /analyze/
│   │   │   ├── debugging.py     # POST /debugging/
│   │   │   ├── explanation.py   # POST /explanation/
│   │   │   └── suggestions.py   # POST /suggestions/
│   │   └── services/
│   │       ├── code_assistant.py  # Rule-based analysis engine
│   │       └── ai_provider.py     # LLM abstraction layer
│   ├── requirements.txt
│   └── tests/
│       └── test_endpoints.py    # Full test suite (pytest)
├── frontend/
│   ├── index.html               # Main UI — no build step
│   ├── style.css                # Dark/light theme, responsive
│   └── script.js                # All interactivity
├── .env.example                 # Environment variable reference
├── Dockerfile                   # One-service Docker build
├── render.yaml                  # Render deploy blueprint
└── README.md
```

---

## Running Tests

```bash
cd backend
pytest -q
```

Tests run automatically on every push and pull request via GitHub Actions.

---

## Deployment

### Render (Recommended - Free Tier)

1. Fork this repository
2. Connect it to [Render](https://render.com)
3. Use the `render.yaml` blueprint - one service, zero config
4. Your app will be live at `https://your-service.onrender.com`

The same service serves the frontend at `/app/` and the API from `/`.

### Docker

```bash
docker build -t qyverixai .
docker run -p 8000:8000 qyverixai
```

---

## Optional: Live LLM Integration

QyverixAI works out of the box with its rule-based engine.
To enable richer AI-powered analysis, set these on your backend host:

```env
LLM_ENABLED=true
LLM_API_KEY=sk-your-key-here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
```

Compatible with OpenAI, Groq, Together AI, Ollama, and any OpenAI-compatible endpoint.

> ⚠️ Never commit API keys. Use environment variables or your host's secrets manager.

---

## Contributing

QyverixAI is a **GSSoC 2026** project - beginner contributors are warmly welcome!

```bash
# Fork → Clone → Branch → Code → Test → PR
git checkout -b feat/your-feature-name
pytest -q                         # All tests must pass
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow.

### Good First Issues

Look for issues labeled [`good first issue`](https://github.com/imDarshanGK/AI-dev-assistant/labels/good%20first%20issue):

- Add support for a new language pattern in the debug engine
- Improve explanation key points for a specific language
- Add a new suggestion rule
- Write tests for edge cases
- Improve frontend accessibility

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, Pydantic v2, Python 3.12 |
| Frontend | HTML5, CSS3, Vanilla JS (no build step) |
| Testing | Pytest, FastAPI TestClient |
| Deploy | Docker, Render |
| CI | GitHub Actions |

---

## Roadmap

- [x] Rule-based code explanation engine
- [x] Bug detection with 15+ patterns
- [x] Improvement suggestions with quality score
- [x] Full-analysis combined endpoint
- [x] Dark/light theme, file upload, history, favorites
- [x] LLM provider abstraction layer
- [ ] Language-specific analyzers (Python, JS, Java, Go)
- [ ] Per-user history with database backend
- [ ] VS Code extension
- [ ] AI-powered explanations (LLM integration GA)
- [ ] Multi-file analysis support

---

## License

MIT © [Darshan G K](https://github.com/imDarshanGK)

Built with ♥ for the open source community · GSSoC 2026

---

<div align="center">

[⭐ Star this repo](https://github.com/imDarshanGK/AI-dev-assistant) · [🐛 Report a bug](https://github.com/imDarshanGK/AI-dev-assistant/issues/new?template=bug_report.md) · [💡 Request a feature](https://github.com/imDarshanGK/AI-dev-assistant/issues/new?template=feature_request.md)

</div>