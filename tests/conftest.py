"""Pytest fixtures for tests."""

import pytest
from pathlib import Path
from typing import Generator

from fastapi.testclient import TestClient


@pytest.fixture
def test_client() -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI app."""
    from src.main import app

    with TestClient(app) as client:
        yield client


@pytest.fixture
def sample_markdown() -> str:
    """Sample Markdown content for testing."""
    return """# API Documentation

## Overview

This document describes the User API.

## Endpoints

### GET /api/users

Get all users.

**Response:**
```json
{
  "users": []
}
```

### POST /api/users

Create a new user.

| Field | Type | Required |
|-------|------|----------|
| name | string | Yes |
| email | string | Yes |
"""


@pytest.fixture
def sample_api_spec() -> str:
    """Sample API specification content."""
    return """# User Service API

## GET /api/users/{id}

Get user by ID.

### Parameters

- `id` (path): User ID

### Response

```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com"
}
```

## POST /api/users

Create a new user.

### Request Body

| Field | Type | Description |
|-------|------|-------------|
| name | string | User's name |
| email | string | User's email |
"""


@pytest.fixture
def temp_upload_dir(tmp_path: Path) -> Path:
    """Create a temporary upload directory."""
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    return upload_dir
