#!/usr/bin/env python3
"""Health check script for Docker container."""

import sys

import httpx


def check_health():
    """Check if the API is healthy."""
    try:
        response = httpx.get("http://localhost:8000/health", timeout=5.0)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                print("Health check passed")
                sys.exit(0)
        print(f"Health check failed: {response.status_code}")
        sys.exit(1)
    except Exception as e:
        print(f"Health check error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    check_health()
