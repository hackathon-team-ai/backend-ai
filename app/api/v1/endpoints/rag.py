import os
import uuid
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.api.v1.endpoints.auth import get_current_user
from app.core.config import settings
from app.schemas.rag import DocumentUploadResponse, DocumentQueryRequest, DocumentQueryResponse, DocumentSearchResult
from app.services.rag_service import rag_service
from app.services.gemini_service import gemini_service

router = APIRouter()
IN_MEMORY_DOCS = []

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf", ".docx", ".doc", ".txt"]:
        raise HTTPException(status_code=400, detail="Unsupported document type. Upload PDF, DOCX, or TXT.")

    file_id = uuid.uuid4().hex[:10]
    filepath = os.path.join(settings.UPLOAD_DIR, f"{file_id}_{file.filename}")

    with open(filepath, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    doc_info = await rag_service.process_and_index_document(filepath, file.filename, user_id)
    resp = DocumentUploadResponse(
        id=doc_info["id"],
        filename=doc_info["filename"],
        file_type=doc_info["file_type"],
        file_size_kb=doc_info["file_size_kb"],
        num_chunks=doc_info["num_chunks"],
        uploaded_at=doc_info["uploaded_at"]
    )
    IN_MEMORY_DOCS.append(resp)
    return resp

@router.post("/query", response_model=DocumentQueryResponse)
async def query_documents(
    req: DocumentQueryRequest,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]
    similar_chunks = rag_service.search_similar_chunks(req.query, user_id=user_id, top_k=req.top_k)

    sources = [
        DocumentSearchResult(
            chunk_id=c["chunk_id"],
            document_id=c["document_id"],
            filename=c["filename"],
            text=c["text"],
            score=c["score"],
            metadata=c["metadata"]
        ) for c in similar_chunks
    ]

    context = "\n\n".join([f"Source [{c['filename']}]: {c['text']}" for c in similar_chunks])
    answer = await gemini_service.generate_response(
        user_prompt=req.query,
        category="Knowledge Base QA",
        context=context
    )

    return DocumentQueryResponse(
        answer=answer,
        sources=sources
    )

@router.get("/documents", response_model=List[DocumentUploadResponse])
async def list_user_documents(current_user: dict = Depends(get_current_user)):
    return IN_MEMORY_DOCS
