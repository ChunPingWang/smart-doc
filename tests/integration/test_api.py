"""Integration tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_root_endpoint(self, test_client: TestClient):
        """Test root endpoint returns app info."""
        response = test_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert data["name"] == "System Doc RAG"

    def test_health_endpoint(self, test_client: TestClient):
        """Test health endpoint."""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_admin_health(self, test_client: TestClient):
        """Test admin health endpoint."""
        response = test_client.get("/api/admin/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "components" in data


class TestDocumentEndpoints:
    """Tests for document API endpoints."""

    def test_list_documents_empty(self, test_client: TestClient):
        """Test listing documents when none exist."""
        response = test_client.get("/api/documents")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data

    def test_upload_invalid_file_type(self, test_client: TestClient):
        """Test uploading unsupported file type."""
        files = {"file": ("test.txt", b"content", "text/plain")}
        response = test_client.post("/api/documents/upload", files=files)
        assert response.status_code == 400

    def test_upload_markdown(self, test_client: TestClient, sample_markdown: str):
        """Test uploading a markdown file."""
        files = {"file": ("test.md", sample_markdown.encode(), "text/markdown")}
        response = test_client.post("/api/documents/upload", files=files)
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert "document_id" in data["data"]

    def test_get_nonexistent_document(self, test_client: TestClient):
        """Test getting a document that doesn't exist."""
        response = test_client.get("/api/documents/nonexistent_id")
        assert response.status_code == 404


class TestQueryEndpoints:
    """Tests for query API endpoints."""

    def test_search_empty(self, test_client: TestClient):
        """Test search with no indexed documents."""
        response = test_client.post(
            "/api/query/search",
            json={"query": "test query"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "results" in data["data"]

    def test_ask_empty(self, test_client: TestClient):
        """Test ask with no indexed documents."""
        response = test_client.post(
            "/api/query/ask",
            json={"question": "What is the API?"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "answer" in data["data"]
