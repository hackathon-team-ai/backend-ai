import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.chat import ChatRequest, ChatResponse, ChatMessage, ChatSessionResponse
from app.services.gemini_service import gemini_service
from app.services.rag_service import rag_service
from app.services.voice_service import voice_service
from app.database.mongodb import get_database

router = APIRouter()
IN_MEMORY_SESSIONS = {}

@router.post("/message", response_model=ChatResponse)
async def send_chat_message(
    req: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]
    session_id = req.session_id or str(uuid.uuid4())
    db = get_database()

    # RAG context lookup if requested
    context = ""
    sources = []
    if req.use_rag:
        rag_res = rag_service.search_similar_chunks(req.message, user_id=user_id, top_k=3)
        if rag_res:
            context = "\n\n".join([f"Source ({r['filename']}): {r['text']}" for r in rag_res])
            sources = rag_res

    # Generate response via Gemini API or Agronomy engine
    assistant_text = await gemini_service.generate_response(
        user_prompt=req.message,
        category=req.category,
        context=context
    )

    # Audio synthesis
    audio_path = await voice_service.text_to_speech(assistant_text, lang=req.language or "en")

    asst_msg = ChatMessage(
        id=str(uuid.uuid4()),
        sender="assistant",
        content=assistant_text,
        category=req.category,
        audio_url=audio_path,
        sources=sources,
        timestamp=datetime.utcnow()
    )

    user_msg = ChatMessage(
        id=str(uuid.uuid4()),
        sender="user",
        content=req.message,
        category=req.category,
        timestamp=datetime.utcnow()
    )

    # Save to Session DB or In-memory store
    if session_id not in IN_MEMORY_SESSIONS:
        IN_MEMORY_SESSIONS[session_id] = {
            "id": session_id,
            "user_id": user_id,
            "title": req.message[:40] + "...",
            "category": req.category or "General",
            "messages": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

    IN_MEMORY_SESSIONS[session_id]["messages"].extend([user_msg.dict(), asst_msg.dict()])
    IN_MEMORY_SESSIONS[session_id]["updated_at"] = datetime.utcnow()

    # Suggested followups based on topic
    suggested = [
        "What is the recommended NPK fertilizer dosage for this crop?",
        "How can I prevent pest attacks organically?",
        "What weather conditions are best for harvesting?"
    ]

    return ChatResponse(
        session_id=session_id,
        message=asst_msg,
        suggested_followups=suggested
    )

@router.get("/sessions", response_model=List[ChatSessionResponse])
async def list_chat_sessions(
    current_user: dict = Depends(get_current_user),
    search: Optional[str] = Query(None)
):
    user_id = current_user["id"]
    user_sessions = [s for s in IN_MEMORY_SESSIONS.values() if s["user_id"] == user_id]

    if search:
        q = search.lower()
        user_sessions = [
            s for s in user_sessions
            if q in s["title"].lower() or any(q in m["content"].lower() for m in s["messages"])
        ]

    user_sessions.sort(key=lambda x: x["updated_at"], reverse=True)
    return user_sessions

@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    if session_id in IN_MEMORY_SESSIONS:
        del IN_MEMORY_SESSIONS[session_id]
        return {"message": "Chat session deleted successfully."}
    raise HTTPException(status_code=404, detail="Session not found.")
