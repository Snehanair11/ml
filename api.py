from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict, List
import traceback

from inference.predict_emotion import predict_emotion
from chatbot.reply_manager import generate_reply

app = FastAPI()


class ChatRequest(BaseModel):
    anon_id: str
    text: str
    conversation_context: Optional[Dict] = None
    conversation_history: Optional[List[str]] = None
    timestamp: Optional[str] = None


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat(req: ChatRequest):
    try:
        # ---------- EMOTION ----------
        emotion_result = predict_emotion({
            "user_id": req.anon_id,
            "text": req.text,
            "timestamp": req.timestamp
        })

        if not isinstance(emotion_result, dict):
            raise ValueError("predict_emotion did not return a dict")

        emotion = emotion_result.get("emotion", "neutral")
        decision = emotion_result.get("decision", {})

        # ---------- REPLY ----------
        reply = generate_reply(
            anon_id=req.anon_id,
            emotion=emotion,
            decision=decision,
            text=req.text,
            conversation_context=req.conversation_context or {},
            conversation_history=req.conversation_history or [],
            timestamp=req.timestamp
        )

        return {
            "emotion": emotion,
            "reply": reply
        }

    except Exception as e:
        # 🔴 THIS IS THE IMPORTANT PART
        # Instead of silent 500, we return the real error
        return {
            "error": str(e),
            "trace": traceback.format_exc()
        }
