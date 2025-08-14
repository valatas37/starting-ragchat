# RAG System Testing Framework

This directory contains the enhanced testing infrastructure for the RAG system backend.

## Test Structure

```
backend/tests/
├── __init__.py              # Package initialization
├── conftest.py              # Shared pytest fixtures and configuration
├── test_simple_api.py       # API endpoint tests with inline test app
└── README.md               # This documentation
```

## Features Implemented

### 1. Pytest Configuration (pyproject.toml)
- Added test dependencies: `pytest>=8.0.0`, `pytest-asyncio>=0.23.0`, `httpx>=0.27.0`
- Configured test discovery and execution settings
- Added custom markers for test categorization:
  - `integration`: Full API integration tests
  - `unit`: Unit tests for specific components
  - `slow`: Performance or long-running tests

### 2. Shared Test Fixtures (conftest.py)
- **Environment setup**: Automatic test environment configuration
- **Mock components**: Pre-configured mocks for RAG system, vector store, and Anthropic client
- **Test data**: Sample requests, responses, and course statistics
- **Temporary directories**: For file-based testing scenarios

### 3. API Endpoint Tests (test_simple_api.py)
- **Complete API coverage**: Tests for all FastAPI endpoints
- **Request/Response validation**: Pydantic model validation testing
- **Error handling**: Tests for various error scenarios
- **Authentication**: API key configuration testing
- **CORS**: Cross-origin request testing

## Static File Mounting Solution

The original FastAPI app mounts static files from `../frontend` which doesn't exist in the test environment. The solution implemented:

1. **Inline test app**: Created a simplified FastAPI app within the test file
2. **Mock dependencies**: All RAG system components are mocked for consistent testing
3. **No static mounting**: Test app focuses only on API endpoints without frontend dependencies

## Running Tests

### All tests
```bash
uv run pytest
```

### Specific test categories
```bash
# Integration tests only
uv run pytest -m integration

# Unit tests only  
uv run pytest -m unit

# Exclude slow tests
uv run pytest -m "not slow"
```

### Verbose output
```bash
uv run pytest -v
```

### Test coverage by endpoint
- `POST /api/query`: Query processing with session management
- `GET /api/courses`: Course statistics and analytics
- `DELETE /api/session/clear`: Session cleanup
- `GET /api/debug`: System debugging information
- `GET /`: Health check endpoint

## Test Markers

- `@pytest.mark.integration`: Full API integration tests
- `@pytest.mark.unit`: Isolated unit tests
- `@pytest.mark.slow`: Long-running tests (can be excluded)

## Mock Strategy

Tests use comprehensive mocking to avoid external dependencies:
- **RAG System**: Mocked query processing and analytics
- **Vector Store**: Mocked search and document storage
- **Anthropic Client**: Mocked AI response generation
- **Session Manager**: Mocked session lifecycle management

This ensures tests are fast, reliable, and don't require actual API keys or database connections.