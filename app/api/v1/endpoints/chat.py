import logging
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

logger = logging.getLogger("krishimitra.chat")
router = APIRouter()
IN_MEMORY_SESSIONS = {}


async def _load_session_from_store(db, session_id: str, user_id: str):
    if db is None or not hasattr(db, "chat_history"):
        return None

    try:
        session_doc = await db.chat_history.find_one({"_id": session_id, "user_id": user_id})
    except Exception as exc:
        logger.warning("Failed to load chat session from MongoDB: %s", exc)
        return None

    if not session_doc:
        return None

    session_doc = dict(session_doc)
    session_doc["id"] = str(session_doc.pop("_id"))
    return session_doc


async def _save_session_to_store(db, session_id: str, session_payload: dict):
    if db is None or not hasattr(db, "chat_history"):
        return

    try:
        payload = dict(session_payload)
        payload["_id"] = session_id
        payload["id"] = session_id
        await db.chat_history.replace_one({"_id": session_id}, payload, upsert=True)
    except Exception as exc:
        logger.warning("Failed to save chat session to MongoDB: %s", exc)

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
        context=context,
        language=req.language or "en"
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

    # Persist chat session in MongoDB first, and mirror it in memory for quick access.
    session_payload = await _load_session_from_store(db, session_id, user_id)
    if not session_payload:
        session_payload = {
            "id": session_id,
            "user_id": user_id,
            "title": req.message[:40] + "...",
            "category": req.category or "General",
            "messages": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

    session_payload["messages"].extend([user_msg.dict(), asst_msg.dict()])
    session_payload["updated_at"] = datetime.utcnow()
    session_payload["title"] = session_payload.get("title") or (req.message[:40] + "...")
    session_payload["category"] = req.category or session_payload.get("category") or "General"

    IN_MEMORY_SESSIONS[session_id] = session_payload
    await _save_session_to_store(db, session_id, session_payload)

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
    db = get_database()
    user_sessions = []

    if db is not None and hasattr(db, "chat_history"):
        try:
            cursor = db.chat_history.find({"user_id": user_id}).sort("updated_at", -1)
            async for session_doc in cursor:
                session_doc = dict(session_doc)
                session_doc["id"] = str(session_doc.pop("_id"))
                user_sessions.append(session_doc)
        except Exception as exc:
            logger.warning("Failed to list chat sessions from MongoDB: %s", exc)

    if not user_sessions:
        user_sessions = [s for s in IN_MEMORY_SESSIONS.values() if s["user_id"] == user_id]

    if search:
        q = search.lower()
        user_sessions = [
            s for s in user_sessions
            if q in str(s.get("title", "")).lower() or any(q in str(m.get("content", "")).lower() for m in s.get("messages", []))
        ]

    user_sessions.sort(key=lambda x: x.get("updated_at") or datetime.utcnow(), reverse=True)
    return user_sessions

@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    db = get_database()
    if db is not None and hasattr(db, "chat_history"):
        try:
            await db.chat_history.delete_one({"_id": session_id})
        except Exception as exc:
            logger.warning("Failed to delete chat session from MongoDB: %s", exc)

    if session_id in IN_MEMORY_SESSIONS:
        del IN_MEMORY_SESSIONS[session_id]
        return {"message": "Chat session deleted successfully."}
    raise HTTPException(status_code=404, detail="Session not found.")
