from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
import os
import json
import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, pipeline

MODEL_DIR = "./model_output"

# Global variables for models
tokenizer = None
model = None
id2label = {}
sentiment_pipeline = None

def load_models():
    global tokenizer, model, id2label, sentiment_pipeline
    
    print("Loading models on startup...")
    
    if not os.path.exists(MODEL_DIR):
        print(f"WARNING: Model directory {MODEL_DIR} not found. Please run distilbert_classifier.py first.")
    else:
        try:
            tokenizer = DistilBertTokenizer.from_pretrained(MODEL_DIR)
            model = DistilBertForSequenceClassification.from_pretrained(MODEL_DIR)
            model.eval()
            
            with open(os.path.join(MODEL_DIR, "label_mapping.json"), "r") as f:
                mapping = json.load(f)
                id2label = {int(k): v for k, v in mapping["id2label"].items()}
                
            print("Category model loaded successfully.")
        except Exception as e:
            print(f"Error loading DistilBERT model: {e}")
            
    try:
        # Using a fast, standard sentiment model
        sentiment_pipeline = pipeline("sentiment-analysis")
        print("Sentiment pipeline loaded successfully.")
    except Exception as e:
        print(f"Error loading sentiment pipeline: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_models()
    yield

app = FastAPI(
    title="News Classifier API",
    description="Real-time category prediction using DistilBERT and Sentiment Analysis",
    version="1.0",
    lifespan=lifespan
)



class PredictRequest(BaseModel):
    text: str

class PredictResponse(BaseModel):
    headline: str
    category: str
    confidence: float
    sentiment: str
    sentiment_score: float
    all_scores: dict[str, float]

# load_models and lifespan are now defined above

@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    if not request.text:
        raise HTTPException(status_code=400, detail="Empty text provided")
        
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Category model is not loaded. Please train the model first.")
        
    # Predict Category
    inputs = tokenizer(request.text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    with torch.no_grad():
        outputs = model(**inputs)
        
    logits = outputs.logits
    probs = torch.nn.functional.softmax(logits, dim=-1)
    
    confidence, predicted_class = torch.max(probs, dim=-1)
    category = id2label.get(predicted_class.item(), "UNKNOWN")
    
    all_scores = {}
    for i, prob in enumerate(probs[0]):
        all_scores[id2label.get(i, f"UNKNOWN_{i}")] = float(prob.item())
    
    # Predict Sentiment
    sentiment_result = "UNKNOWN"
    sentiment_score = 0.0
    if sentiment_pipeline:
        res = sentiment_pipeline(request.text[:512])[0] # Truncate for sentiment
        sentiment_result = res['label']
        sentiment_score = res['score']
        
    return PredictResponse(
        headline=request.text,
        category=category,
        confidence=confidence.item(),
        sentiment=sentiment_result,
        sentiment_score=sentiment_score,
        all_scores=all_scores
    )

@app.get("/health")
def health_check():
    return {"status": "ok", "model_loaded": model is not None}
