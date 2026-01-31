from fastapi import FastAPI
from pydantic import BaseModel

# ✅ FIXED IMPORTS (NO src, NO v2)
from inference.predict_emotion import predict_emotion
from chatbot.reply_manager import generate_reply

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
    # ✅ emotion prediction
    emotion_result = predict_emotion({
        "user_id": req.anon_id,
        "text": req.text,
        "timestamp": req.timestamp
    })

    emotion = emotion_result.get("emotion", "neutral")
    decision = emotion_result.get("decision", {})

    # ✅ chatbot reply
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
