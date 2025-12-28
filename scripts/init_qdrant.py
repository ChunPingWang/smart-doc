#!/usr/bin/env python3
"""Initialize Qdrant collection with proper schema."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from src.config import get_settings


def init_qdrant():
    """Initialize Qdrant collection."""
    settings = get_settings()

    print(f"Connecting to Qdrant at {settings.qdrant_host}:{settings.qdrant_port}")
    client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)

    collection_name = settings.qdrant_collection

    # Check if collection exists
    collections = client.get_collections().collections
    collection_names = [c.name for c in collections]

    if collection_name in collection_names:
        print(f"Collection '{collection_name}' already exists")
        info = client.get_collection(collection_name)
        print(f"  Vectors count: {info.vectors_count}")
        print(f"  Points count: {info.points_count}")
        return

    # Create collection
    print(f"Creating collection '{collection_name}'...")
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=1024,  # bge-large dimension
            distance=Distance.COSINE,
        ),
    )

    # Create payload indexes
    print("Creating payload indexes...")
    from qdrant_client.http import models as qdrant_models

    client.create_payload_index(
        collection_name=collection_name,
        field_name="document_id",
        field_schema=qdrant_models.PayloadSchemaType.KEYWORD,
    )
    client.create_payload_index(
        collection_name=collection_name,
        field_name="doc_type",
        field_schema=qdrant_models.PayloadSchemaType.KEYWORD,
    )
    client.create_payload_index(
        collection_name=collection_name,
        field_name="tags",
        field_schema=qdrant_models.PayloadSchemaType.KEYWORD,
    )

    print("Qdrant collection initialized successfully!")


if __name__ == "__main__":
    init_qdrant()
