# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
```bash
# Quick start (recommended)
chmod +x run.sh
./run.sh

# Manual start
cd backend
uv run uvicorn app:app --reload --port 8000
```

### Package Management
```bash
# Install dependencies
uv sync

# Add new dependency
uv add <package-name>

# Install development dependencies (code quality tools)
uv sync --group dev
```

### Code Quality
```bash
# Format code automatically
python scripts/format_code.py
# or
./scripts/format_code.sh

# Run all quality checks
python scripts/quality_check.py
# or
./scripts/quality_check.sh

# Individual tools
uv run black .                    # Format code
uv run isort .                    # Sort imports
uv run flake8 .                   # Lint code
uv run mypy backend/             # Type checking

# Check without modifying files
uv run black --check .           # Check formatting
uv run isort --check-only .      # Check import sorting
```

### Environment Setup
Create `.env` file in root directory:
```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

## Architecture Overview

This is a Retrieval-Augmented Generation (RAG) system with a FastAPI backend serving a vanilla HTML/CSS/JS frontend. The system processes course documents and enables AI-powered querying with semantic search.

### Core RAG Pipeline Architecture

**RAGSystem** (`rag_system.py`) is the central orchestrator that coordinates:
- **DocumentProcessor**: Parses structured course documents with lessons
- **VectorStore**: ChromaDB with sentence-transformers embeddings
- **AIGenerator**: Anthropic Claude integration with tool-calling capabilities
- **SessionManager**: Conversation history tracking
- **ToolManager**: Manages AI tools (currently CourseSearchTool)

### Document Processing Flow

Documents follow a structured format:
```
Course Title: [title]
Course Link: [url]
Course Instructor: [instructor]

Lesson 0: Introduction
Lesson Link: [lesson_url]
[content...]
```

Processing pipeline:
1. Parse metadata (title, instructor, course link)
2. Split content by lesson markers (`Lesson N:`)
3. Chunk lesson content (800 chars, 100 char overlap, sentence-aware)
4. Add contextual prefixes: `"Course {title} Lesson {number} content: {chunk}"`
5. Store in ChromaDB with metadata

### AI Tool Integration

The system uses Claude's tool-calling capabilities:
- **CourseSearchTool**: Semantic search with course/lesson filtering
- **ToolManager**: Abstract tool registration and execution
- **AI-driven search**: Claude autonomously decides when to search content

### Query Processing Flow

1. **Frontend**: User input → POST `/api/query` with session_id
2. **FastAPI**: Route handling, session management
3. **RAGSystem**: Query coordination, context building
4. **AIGenerator**: Claude API call with tools and conversation history
5. **Tool Execution**: If needed, search course content via vector store
6. **Response**: AI synthesis of search results with source attribution

### Key Configuration

**Config Settings** (`config.py`):
- Chunk size: 800 characters
- Chunk overlap: 100 characters
- Max search results: 5
- Conversation history: 2 exchanges
- Embedding model: `all-MiniLM-L6-v2`
- Claude model: `claude-sonnet-4-20250514`

### Session & State Management

- **Session IDs**: Track conversation context across queries
- **Conversation History**: Limited to last 2 exchanges per session
- **Source Tracking**: Tool searches store sources for UI display
- **Stateless Tools**: Each tool execution is independent

### Frontend Architecture

Static files served by FastAPI with vanilla JS:
- **No framework dependencies** (just marked.js for markdown)
- **Real-time interaction** with loading states
- **Source attribution** via collapsible UI elements
- **Session persistence** across page reloads

### ChromaDB Collections

The vector store creates separate collections for course metadata and content chunks, enabling both semantic search and metadata-based filtering.

### Error Handling Patterns

- **Tool errors**: Return error messages to AI for context
- **Empty results**: Clear messaging about no content found
- **API failures**: Frontend displays error messages with retry capability
- **Document processing**: Per-file error handling with continuation

### Extension Points

To add new functionality:
- **New tools**: Implement `Tool` interface, register with `ToolManager`
- **Document types**: Extend `DocumentProcessor.read_file()` method
- **Search filters**: Add parameters to `CourseSearchTool`
- **UI features**: Modify static files in `frontend/` directory
- always use uv to run the server do not use pip directly
- make sure to use uv to manage all dependencies