from fastapi import FastAPI
from inference.predict_emotion import predict_emotion

app = FastAPI()

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/predict")
def predict(payload: dict):
    text = payload.get("text", "")
    return predict_emotion(text)
