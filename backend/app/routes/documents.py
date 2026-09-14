from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile

from ..database import (
    create_document,
    get_document,
    get_document_chunks,
)
from ..extractors.registry import ExtractorRegistry
from ..services.processor import DocumentProcessor


router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)

registry = ExtractorRegistry()
processor = DocumentProcessor(registry)


@router.post("", status_code=202)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    filename = file.filename or ""

    if not filename:
        raise HTTPException(
            status_code=400,
            detail="A filename is required",
        )

    try:
        registry.get_extractor(filename)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="The uploaded document is empty",
        )

    document_id = str(uuid4())
    file_type = Path(filename).suffix.lower().lstrip(".")

    create_document(
        document_id=document_id,
        filename=filename,
        file_type=file_type,
    )

    background_tasks.add_task(
        processor.process,
        document_id,
        filename,
        file_bytes,
    )

    return {
        "id": document_id,
        "filename": filename,
        "status": "processing",
    }


@router.get("/{document_id}")
def document_status(document_id: str):
    document = get_document(document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return document


@router.get("/{document_id}/content")
def document_content(document_id: str):
    document = get_document(document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    if document["status"] != "completed":
        raise HTTPException(
            status_code=409,
            detail=f"Document is currently {document['status']}",
        )

    return {
        "document_id": document_id,
        "chunks": get_document_chunks(document_id),
    }