"""Document management API routes."""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile, status

from src.api.schemas import (
    APIResponse,
    DocType,
    DocumentMetadata,
    DocumentResponse,
    DocumentUploadResponse,
    IndexStatus,
    PaginatedDocuments,
)
from src.config import get_settings

router = APIRouter()
settings = get_settings()

# Temporary in-memory storage (will be replaced with proper service)
_documents: dict[str, DocumentResponse] = {}


@router.post(
    "/upload",
    response_model=APIResponse[DocumentUploadResponse],
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    doc_type: Optional[DocType] = Form(None),
    tags: Optional[str] = Form(None),
) -> APIResponse[DocumentUploadResponse]:
    """
    Upload a document and create index.

    Supported formats: .md, .docx, .xlsx
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )

    # Validate file extension
    allowed_extensions = {".md", ".docx", ".xlsx"}
    file_ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}",
        )

    # Validate file size
    content = await file.read()
    if len(content) > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {settings.max_file_size_mb}MB",
        )

    # Generate document ID
    document_id = f"doc_{uuid4().hex[:12]}"

    # Auto-detect document type if not provided
    if doc_type is None:
        doc_type = DocType.GENERAL

    # Parse tags
    tag_list = [t.strip() for t in tags.split(",")] if tags else []

    # TODO: Actual document processing will be implemented in DocumentService
    # For now, create placeholder response
    now = datetime.utcnow()
    metadata = DocumentMetadata(
        api_endpoints=[],
        table_names=[],
        entity_names=[],
    )

    # Store document info
    doc_response = DocumentResponse(
        document_id=document_id,
        filename=file.filename,
        doc_type=doc_type,
        chunks_count=0,
        file_size=len(content),
        status=IndexStatus.PENDING,
        tags=tag_list,
        metadata=metadata,
        created_at=now,
        updated_at=now,
    )
    _documents[document_id] = doc_response

    upload_response = DocumentUploadResponse(
        document_id=document_id,
        filename=file.filename,
        doc_type=doc_type,
        chunks_count=0,
        metadata=metadata,
        created_at=now,
    )

    return APIResponse(status="success", data=upload_response)


@router.get("", response_model=APIResponse[PaginatedDocuments])
async def list_documents(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    doc_type: Optional[DocType] = None,
) -> APIResponse[PaginatedDocuments]:
    """List all indexed documents with pagination."""
    # Filter documents
    docs = list(_documents.values())
    if doc_type:
        docs = [d for d in docs if d.doc_type == doc_type]

    # Pagination
    total = len(docs)
    pages = (total + size - 1) // size
    start = (page - 1) * size
    end = start + size
    items = docs[start:end]

    return APIResponse(
        status="success",
        data=PaginatedDocuments(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages,
        ),
    )


@router.get("/{document_id}", response_model=APIResponse[DocumentResponse])
async def get_document(document_id: str) -> APIResponse[DocumentResponse]:
    """Get document details by ID."""
    if document_id not in _documents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document not found: {document_id}",
        )

    return APIResponse(status="success", data=_documents[document_id])


@router.delete("/{document_id}", response_model=APIResponse[None])
async def delete_document(document_id: str) -> APIResponse[None]:
    """Delete a document and its index."""
    if document_id not in _documents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document not found: {document_id}",
        )

    del _documents[document_id]
    # TODO: Also delete from vector store

    return APIResponse(status="success", message="Document deleted successfully")
