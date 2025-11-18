from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from grammar_corrector import GrammarCorrector

app = FastAPI(title="English Tutor API - Local")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

corrector = GrammarCorrector()

class CorrectionRequest(BaseModel):
    text: str
    difficulty: str = "intermediate"

class CorrectionResponse(BaseModel):
    original_text: str
    corrected_text: str
    explanation: str
    confidence: float
    status: str
    is_correct: bool
    suggestions: List[str]
    difficulty_used: str

@app.get("/")
def home():
    return {"message": "English Tutor API running locally! 🚀"}

@app.post("/correct", response_model=CorrectionResponse)
def correct_grammar(request: CorrectionRequest):
    result = corrector.correct_grammar(request.text, request.difficulty)
    return CorrectionResponse(**result)

@app.get("/health")
def health():
    return {"status": "healthy", "service": "grammar_correction"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)