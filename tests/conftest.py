"""
Pytest configuration and fixtures for IndiVillage Voice Agent System tests.
"""

import asyncio
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from flask import Flask
from flask_socketio import SocketIO

# Import the main application components
from client import app, socketio
from common.business_logic import MOCK_DATA
from knowledgebase.mdx_handler import MDXKnowledgeBase


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def flask_app():
    """Create a Flask application configured for testing."""
    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret-key"
    })
    
    with app.app_context():
        yield app


@pytest.fixture
def client(flask_app):
    """Create a test client for the Flask application."""
    return flask_app.test_client()


@pytest.fixture
def socketio_client(flask_app):
    """Create a SocketIO test client."""
    return socketio.test_client(flask_app)


@pytest.fixture
def mock_deepgram_api():
    """Mock Deepgram API responses."""
    with patch('os.environ.get') as mock_env:
        mock_env.return_value = 'test-deepgram-key'
        yield mock_env


@pytest.fixture
def mock_websocket():
    """Mock WebSocket connection."""
    mock_ws = AsyncMock()
    mock_ws.send = AsyncMock()
    mock_ws.recv = AsyncMock()
    mock_ws.close = AsyncMock()
    return mock_ws


@pytest.fixture
def sample_customer_data():
    """Sample customer data for testing."""
    return {
        "id": "CUST0001",
        "name": "John Doe",
        "phone": "+15551234567",
        "email": "john.doe@example.com",
        "joined_date": "2024-01-15T10:30:00"
    }


@pytest.fixture
def sample_appointment_data():
    """Sample appointment data for testing."""
    return {
        "id": "APT0001",
        "customer_id": "CUST0001",
        "customer_name": "John Doe",
        "date": "2024-02-15T14:00:00",
        "service": "Consultation",
        "status": "Scheduled"
    }


@pytest.fixture
def sample_order_data():
    """Sample order data for testing."""
    return {
        "id": "ORD0001",
        "customer_id": "CUST0001",
        "customer_name": "John Doe",
        "date": "2024-01-20T09:15:00",
        "items": 3,
        "total": 299.99,
        "status": "Delivered"
    }


@pytest.fixture
def mock_data_setup(sample_customer_data, sample_appointment_data, sample_order_data):
    """Set up mock data for testing."""
    original_data = MOCK_DATA.copy()
    
    # Clear and set up test data
    MOCK_DATA["customers"] = [sample_customer_data]
    MOCK_DATA["appointments"] = [sample_appointment_data]
    MOCK_DATA["orders"] = [sample_order_data]
    MOCK_DATA["sample_data"] = []
    
    yield MOCK_DATA
    
    # Restore original data
    MOCK_DATA.clear()
    MOCK_DATA.update(original_data)


@pytest.fixture
def temp_mdx_directory():
    """Create a temporary directory for MDX files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        mdx_dir = Path(temp_dir) / "mdx"
        mdx_dir.mkdir()
        
        # Create a sample MDX file
        sample_mdx = mdx_dir / "test_entry.mdx"
        sample_mdx.write_text("""---
title: "Test Entry"
topic: "Testing"
tags: ["test", "sample"]
created: "2024-01-15"
updated: "2024-01-15"
---

# Test Entry

This is a test entry for the knowledge base.

## Features

- Feature 1
- Feature 2
- Feature 3
""")
        
        yield str(mdx_dir)


@pytest.fixture
def knowledge_base(temp_mdx_directory):
    """Create a test knowledge base instance."""
    return MDXKnowledgeBase(temp_mdx_directory)


@pytest.fixture
def mock_audio_context():
    """Mock audio context for testing audio functionality."""
    mock_context = MagicMock()
    mock_context.sampleRate = 48000
    mock_context.createMediaStreamSource = MagicMock()
    mock_context.createScriptProcessor = MagicMock()
    mock_context.destination = MagicMock()
    
    return mock_context


@pytest.fixture
def mock_media_stream():
    """Mock media stream for testing audio input."""
    mock_stream = MagicMock()
    mock_stream.getTracks = MagicMock(return_value=[])
    return mock_stream


@pytest.fixture
def voice_agent_settings():
    """Voice agent configuration for testing."""
    return {
        "industry": "indivillage",
        "voiceModel": "aura-2-thalia-en",
        "voiceName": "Thalia",
        "browserAudio": True,
        "inputDeviceId": "default"
    }


@pytest.fixture
def mock_google_api():
    """Mock Google API services."""
    with patch('common.meeting_modular.build') as mock_build:
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        # Mock calendar service
        mock_service.events.return_value.insert.return_value.execute.return_value = {
            'id': 'test-event-id',
            'htmlLink': 'https://calendar.google.com/event/test'
        }
        
        yield mock_service


@pytest.fixture
def mock_email_service():
    """Mock email service for testing."""
    with patch('common.meeting_modular.smtplib') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.SMTP.return_value = mock_server
        yield mock_server


@pytest.fixture
def conversation_messages():
    """Sample conversation messages for testing."""
    return [
        {
            "role": "user",
            "content": "Hello, I need help with my order",
            "timestamp": "2024-01-15T10:00:00"
        },
        {
            "role": "assistant",
            "content": "I'd be happy to help you with your order. Let me look that up for you.",
            "timestamp": "2024-01-15T10:00:05"
        },
        {
            "role": "user",
            "content": "My customer ID is 1",
            "timestamp": "2024-01-15T10:00:10"
        }
    ]


@pytest.fixture
def function_call_data():
    """Sample function call data for testing."""
    return {
        "type": "FunctionCallRequest",
        "functions": [
            {
                "id": "test-function-id",
                "name": "find_customer",
                "arguments": '{"customer_id": "CUST0001"}'
            }
        ]
    }


@pytest.fixture
def audio_data():
    """Sample audio data for testing."""
    import numpy as np
    
    # Generate sample audio data (1 second of 440Hz sine wave)
    sample_rate = 48000
    duration = 1.0
    frequency = 440.0
    
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio_samples = np.sin(2 * np.pi * frequency * t)
    
    # Convert to Int16 format
    audio_int16 = (audio_samples * 32767).astype(np.int16)
    
    return {
        "audio": audio_int16.tobytes(),
        "sampleRate": sample_rate
    }


@pytest.fixture
def mock_pyaudio():
    """Mock PyAudio for testing audio functionality."""
    with patch('pyaudio.PyAudio') as mock_audio:
        mock_instance = MagicMock()
        mock_audio.return_value = mock_instance
        
        # Mock device enumeration
        mock_instance.get_host_api_info_by_index.return_value = {"deviceCount": 2}
        mock_instance.get_device_info_by_host_api_device_index.side_effect = [
            {"name": "Test Microphone", "maxInputChannels": 1},
            {"name": "Test Speaker", "maxInputChannels": 0, "maxOutputChannels": 2}
        ]
        
        # Mock audio stream
        mock_stream = MagicMock()
        mock_instance.open.return_value = mock_stream
        
        yield mock_instance


@pytest.fixture
def environment_variables():
    """Set up environment variables for testing."""
    original_env = os.environ.copy()
    
    # Set test environment variables
    test_env = {
        "DEEPGRAM_API_KEY": "test-deepgram-key",
        "FLASK_ENV": "testing",
        "TESTING": "true"
    }
    
    os.environ.update(test_env)
    
    yield test_env
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def temp_mock_data_file():
    """Create a temporary mock data file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        test_data = {
            "customers": [],
            "appointments": [],
            "orders": [],
            "sample_data": []
        }
        json.dump(test_data, f)
        temp_file = f.name
    
    yield temp_file
    
    # Clean up
    if os.path.exists(temp_file):
        os.unlink(temp_file)


@pytest.fixture
def mock_file_operations():
    """Mock file operations for testing."""
    with patch('builtins.open', create=True) as mock_open:
        with patch('os.path.exists') as mock_exists:
            with patch('pathlib.Path.mkdir') as mock_mkdir:
                mock_exists.return_value = True
                yield {
                    'open': mock_open,
                    'exists': mock_exists,
                    'mkdir': mock_mkdir
                }


# Async test utilities
@pytest.fixture
def async_mock():
    """Create an async mock for testing async functions."""
    return AsyncMock()


# Performance testing fixtures
@pytest.fixture
def performance_timer():
    """Timer for performance testing."""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
        
        @property
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
    
    return Timer()


# Database testing fixtures (for future use)
@pytest.fixture
def mock_database():
    """Mock database connection for testing."""
    with patch('sqlite3.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        yield {
            'connection': mock_conn,
            'cursor': mock_cursor
        }


# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Automatically clean up temporary files after each test."""
    yield
    
    # Clean up any temporary files created during testing
    temp_patterns = [
        "test_*.json",
        "mock_data_test_*.json",
        "*.tmp"
    ]
    
    for pattern in temp_patterns:
        import glob
        for file in glob.glob(pattern):
            try:
                os.unlink(file)
            except OSError:
                pass


# Markers for different test types
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "audio: marks tests that require audio hardware"
    )
    config.addinivalue_line(
        "markers", "api: marks tests that require external API access"
    )


# Skip tests based on environment
def pytest_collection_modifyitems(config, items):
    """Modify test collection based on environment."""
    if not os.environ.get("DEEPGRAM_API_KEY"):
        skip_api = pytest.mark.skip(reason="DEEPGRAM_API_KEY not set")
        for item in items:
            if "api" in item.keywords:
                item.add_marker(skip_api)
    
    # Skip audio tests in CI environment
    if os.environ.get("CI"):
        skip_audio = pytest.mark.skip(reason="Audio tests skipped in CI")
        for item in items:
            if "audio" in item.keywords:
                item.add_marker(skip_audio)