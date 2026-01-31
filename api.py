from fastapi import FastAPI
from pydantic import BaseModel

from src.inference.predict_emotion_v2 import predict_emotion_v2
from src.chatbot.reply_manager import generate_reply

app = FastAPI()

class ChatRequest(BaseModel):
    anon_id: str
    text: str
    conversation_context: dict | None = None
    conversation_history: list | None = None
    timestamp: str | None = None

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/chat")
def chat(req: ChatRequest):
    emotion_result = predict_emotion_v2({
        "user_id": req.anon_id,
        "text": req.text,
        "timestamp": req.timestamp
    })

    emotion = emotion_result.get("emotion", "neutral")
    decision = emotion_result.get("decision", {})

    reply = generate_reply(
        anon_id=req.anon_id,
        emotion=emotion,
        decision=decision,
        text=req.text,
        conversation_context=req.conversation_context,
        conversation_history=req.conversation_history,
        timestamp=req.timestamp
    )

    return {
        "emotion": emotion,
        "reply": reply
    }
