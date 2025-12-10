# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Multi-agent regulatory compliance system that searches, crawls, and analyzes legal regulations using LangGraph and Azure OpenAI. The system targets financial, cybersecurity, and data protection regulations across 40+ countries.

## Common Commands

```bash
# Development
python app.py                          # Start Gradio Web UI (http://localhost:7860)
./start.sh                             # Alternative startup script

# Testing
pytest tests/                          # Run all tests
pytest tests/test_cache.py             # Run specific test file
pytest --cov=src tests/                # Run with coverage

# Code Quality
black src/                             # Format code
ruff check src/                        # Lint
mypy src/                              # Type check

# Dependencies
pip install -r requirements.txt        # Install dependencies
pip install -e ".[dev]"                # Install with dev tools
```

## Architecture

### LangGraph Multi-Agent Pipeline

The system uses a 3-agent sequential workflow orchestrated by LangGraph:

```
User Query → Planner → Researcher → Validator → Structured Results
```

1. **Planner** (`src/agents/langgraph_team.py:planner_node`): Analyzes query intent, identifies region/industry/topic, and determines if clarification is needed before searching.

2. **Researcher** (`src/agents/langgraph_team.py:researcher_node`): Executes multi-keyword searches using LLM-driven tool selection. Fetches web pages/PDFs in parallel (up to 50 items, 10 threads).

3. **Validator** (`src/agents/langgraph_team.py:validator_node`): Deduplicates results, extracts regulation names from original text, generates compliance checklists, outputs structured JSON.

### Key Components

- **Agent Prompts**: Markdown files in `config/prompts/` define each agent's behavior and output format
- **Tool System**: `src/agents/tools.py` provides web search (Google/DuckDuckGo), law database crawlers (Taiwan/Japan/EU), PDF parsing
- **Tool Schemas**: `src/agents/tool_schemas.py` generates OpenAI function-calling schemas from Python type annotations
- **State Management**: `AgentState` TypedDict flows through the graph with messages, search results, and validation outputs
- **Caching**: 24-hour query cache with auto-expiration (`src/utils/cache.py`)

### LLM Configuration

The system uses Azure OpenAI GPT-5.1 (400K context). Configuration via environment variables:
- `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_GPT5_DEPLOYMENT` (default: "gpt-5.1")
- `AZURE_OPENAI_API_VERSION` (default: "2024-12-01-preview")

### Database

SQLite database (`src/database/`) stores baseline regulations with search keywords per country/industry. `BaselineManager` provides regulation discovery and keyword retrieval for the Researcher agent.

## Code Patterns

### Adding New Search Tools

Tools in `src/agents/tools.py` use `Annotated` type hints for automatic schema generation:

```python
def new_tool(
    query: Annotated[str, "Search keywords"],
    limit: Annotated[int, "Max results"] = 10,
) -> str:
    """Tool description shown to LLM."""
    return json.dumps({"status": "success", "results": [...]})
```

Register in `AVAILABLE_TOOLS` list and add schema to `src/agents/tool_schemas.py`.

### Adding Country Support

1. Add region config to `REGION_CONFIG` dict in `web_search()` (`src/agents/tools.py`) with sites, language codes, geolocation
2. Add mandatory search keywords to database via `src/database/seed_regulations.py`
3. Update region-to-code mappings in `_get_mandatory_keywords_from_db()` (`src/agents/langgraph_team.py`)

## Testing Notes

- Tests use pytest fixtures defined in `tests/conftest.py`
- Mock Azure OpenAI responses for unit tests
- Integration tests may require valid API keys in `.env`
