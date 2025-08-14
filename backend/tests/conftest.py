"""
Test configuration and fixtures for the RAG system tests.
"""
import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from typing import Generator, Dict, Any


@pytest.fixture(scope="session")
def temp_dir() -> Generator[str, None, None]:
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture(scope="session")
def test_documents_dir(temp_dir: str) -> str:
    """Create test documents directory with sample course files."""
    docs_dir = os.path.join(temp_dir, "docs")
    os.makedirs(docs_dir)
    
    # Create sample course document
    sample_course = """Course Title: Introduction to Python Programming
Course Link: https://example.com/python-course
Course Instructor: Dr. Jane Smith

Lesson 0: Getting Started with Python
Lesson Link: https://example.com/lesson0
Python is a powerful programming language that is easy to learn and use.
It has a simple syntax that makes it perfect for beginners.

Lesson 1: Variables and Data Types
Lesson Link: https://example.com/lesson1
In Python, variables are used to store data values.
Python has several built-in data types including strings, integers, and floats.

Lesson 2: Control Structures
Lesson Link: https://example.com/lesson2
Control structures like if statements and loops allow you to control the flow of your program.
They are essential for creating dynamic and interactive applications.
"""
    
    course_file = os.path.join(docs_dir, "python_course.txt")
    with open(course_file, "w", encoding="utf-8") as f:
        f.write(sample_course)
    
    return docs_dir


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client for testing AI generation."""
    with patch("anthropic.Anthropic") as mock_client:
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        
        # Mock a typical response
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = "This is a test response from the AI."
        mock_response.stop_reason = "end_turn"
        mock_response.usage = Mock()
        mock_response.usage.input_tokens = 100
        mock_response.usage.output_tokens = 50
        
        mock_instance.messages.create.return_value = mock_response
        yield mock_instance


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    config = Mock()
    config.ANTHROPIC_API_KEY = "test-api-key"
    config.ANTHROPIC_MODEL = "claude-sonnet-4-20250514"
    config.CHUNK_SIZE = 800
    config.CHUNK_OVERLAP = 100
    config.MAX_SEARCH_RESULTS = 5
    config.CONVERSATION_HISTORY_LIMIT = 2
    config.EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    return config


@pytest.fixture
def mock_vector_store():
    """Mock vector store for testing."""
    vector_store = Mock()
    vector_store.add_documents.return_value = None
    vector_store.search.return_value = [
        {
            "content": "Python is a powerful programming language",
            "metadata": {
                "course_title": "Introduction to Python Programming",
                "lesson_number": 0,
                "lesson_title": "Getting Started with Python"
            },
            "distance": 0.2
        }
    ]
    vector_store.get_course_analytics.return_value = {
        "total_courses": 1,
        "course_titles": ["Introduction to Python Programming"]
    }
    return vector_store


@pytest.fixture
def sample_query_request() -> Dict[str, Any]:
    """Sample query request data."""
    return {
        "query": "What is Python?",
        "session_id": "test-session-123"
    }


@pytest.fixture
def sample_query_response() -> Dict[str, Any]:
    """Sample query response data."""
    return {
        "answer": "Python is a powerful programming language that is easy to learn and use.",
        "sources": [
            {
                "course_title": "Introduction to Python Programming",
                "lesson_number": "0",
                "lesson_title": "Getting Started with Python"
            }
        ],
        "session_id": "test-session-123"
    }


@pytest.fixture
def sample_course_stats() -> Dict[str, Any]:
    """Sample course statistics data."""
    return {
        "total_courses": 1,
        "course_titles": ["Introduction to Python Programming"]
    }


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Set up test environment variables."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-api-key")
    monkeypatch.setenv("TESTING", "true")


@pytest.fixture
def mock_rag_system(mock_config, mock_vector_store):
    """Mock RAG system for testing."""
    mock_rag = Mock()
    
    # Mock query method
    mock_rag.query.return_value = (
        "Python is a powerful programming language that is easy to learn and use.",
        [
            {
                "course_title": "Introduction to Python Programming",
                "lesson_number": "0",
                "lesson_title": "Getting Started with Python"
            }
        ]
    )
    
    # Mock analytics
    mock_rag.get_course_analytics.return_value = {
        "total_courses": 1,
        "course_titles": ["Introduction to Python Programming"]
    }
    
    # Mock session manager
    mock_rag.session_manager = Mock()
    mock_rag.session_manager.create_session.return_value = "test-session-123"
    mock_rag.session_manager.clear_session.return_value = None
    
    return mock_rag