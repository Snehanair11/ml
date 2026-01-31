from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict, List
import traceback
import os
import nltk

# ======================================================
# 🔥 CRITICAL: FIX NLTK PATH FOR RENDER
# ======================================================
NLTK_DATA_DIR = "/opt/render/nltk_data"
os.makedirs(NLTK_DATA_DIR, exist_ok=True)
nltk.data.path.append(NLTK_DATA_DIR)

try:
    nltk.data.find("corpora/wordnet")
except LookupError:
    nltk.download("wordnet", download_dir=NLTK_DATA_DIR)
    nltk.download("omw-1.4", download_dir=NLTK_DATA_DIR)

# ======================================================
# ✅ IMPORTS AFTER NLTK FIX
# ======================================================
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
        emotion_result = predict_emotion(req.text)

        if not isinstance(emotion_result, dict):
            raise ValueError("predict_emotion must return a dict")

        emotion = emotion_result.get("emotion", "neutral")
        score = emotion_result.get("score")
        decision = emotion_result.get("decision", {})
        conversation_context = emotion_result.get("conversation_context")

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
            "score": score,
            "reply": reply,
            "conversation_context": conversation_context
        }

    except Exception as e:
        # 🔴 Return REAL error instead of silent 500
        return {
            "error": str(e),
            "trace": traceback.format_exc()
        }
