from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from models.schemas import SessionRequest
from services.orchestrator import run_session
import json

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok", "service": "STEM Mentor Society"}


@router.post("/ask")
async def ask(req: SessionRequest):
    """REST endpoint — collects full session and returns all messages."""
    messages = []
    async for msg in run_session(req.question, req.student_level):
        messages.append(json.loads(msg))
    return JSONResponse({"messages": messages})


@router.websocket("/ws/session")
async def websocket_session(websocket: WebSocket):
    """WebSocket endpoint — streams agent messages in real time."""
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        question = data.get("question", "").strip()
        student_level = data.get("student_level", "high_school")

        if not question:
            await websocket.send_json({"error": "No question provided"})
            await websocket.close()
            return

        async for msg in run_session(question, student_level):
            await websocket.send_text(msg)

        await websocket.send_json({"done": True})
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"error": str(e)})
        except Exception:
            pass
