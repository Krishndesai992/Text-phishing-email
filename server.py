"""
FastAPI Server for Phishing Email Classification Frontend.
Serves REST API endpoints and static web application assets.
"""

import os
import threading
import time
from typing import Optional, List
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from predictor import predictor
from samples import SAMPLE_EMAILS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = FastAPI(
    title="Phishing Email ML Classifier API",
    description="Cybersecurity Email Threat Intelligence & Multi-Model Machine Learning Classifier",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Re-training state
retrain_state = {
    "is_training": False,
    "progress": 0,
    "status_message": "Idle",
    "last_trained": predictor.dataset_stats.get("timestamp", "N/A"),
    "error": None
}

class EmailAnalysisRequest(BaseModel):
    text: str
    sender: Optional[str] = None
    recipient: Optional[str] = None
    subject: Optional[str] = None

class BatchItem(BaseModel):
    id: Optional[str] = None
    text: str
    sender: Optional[str] = None
    recipient: Optional[str] = None
    subject: Optional[str] = None

class BatchAnalysisRequest(BaseModel):
    emails: List[BatchItem]

class RetrainRequest(BaseModel):
    half_limit: Optional[int] = 400

@app.get("/api/status")
def get_status():
    return {
        "status": "online",
        "models_loaded": len(predictor.models),
        "dataset_stats": predictor.dataset_stats,
        "feature_count": len(predictor.feature_names),
        "available_classifiers": [
            "Random Forest", "Gradient Boosting", "Logistic Regression",
            "Linear SVM", "Decision Tree", "Naive Bayes"
        ],
        "feature_sets": ["TF-IDF Only", "Properties Only", "TF-IDF + Properties"]
    }

@app.get("/api/samples")
def get_samples():
    return {"samples": SAMPLE_EMAILS}

@app.post("/api/analyze")
def analyze_email(req: EmailAnalysisRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Email body or text cannot be empty.")
    try:
        result = predictor.analyze_email(
            raw_input=req.text,
            sender=req.sender,
            recipient=req.recipient,
            subject=req.subject
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")

@app.post("/api/batch-analyze")
def batch_analyze(req: BatchAnalysisRequest):
    if not req.emails:
        raise HTTPException(status_code=400, detail="Empty email list.")
    
    results = []
    phishing_count = 0
    clean_count = 0
    total_risk = 0.0

    for idx, item in enumerate(req.emails):
        try:
            res = predictor.analyze_email(
                raw_input=item.text,
                sender=item.sender,
                recipient=item.recipient,
                subject=item.subject
            )
            item_id = item.id or f"email_{idx+1}"
            res["id"] = item_id
            if res["is_phishing"]:
                phishing_count += 1
            else:
                clean_count += 1
            total_risk += res["risk_score"]
            results.append(res)
        except Exception as e:
            results.append({
                "id": item.id or f"email_{idx+1}",
                "error": str(e),
                "verdict": "ERROR",
                "risk_score": 0
            })

    total = len(req.emails)
    avg_risk = round(total_risk / total, 1) if total > 0 else 0

    return {
        "total_analyzed": total,
        "phishing_detected": phishing_count,
        "legitimate_detected": clean_count,
        "average_risk_score": avg_risk,
        "phishing_rate_percent": round((phishing_count / total) * 100, 1) if total > 0 else 0,
        "results": results
    }

@app.get("/api/metrics")
def get_metrics():
    metrics_file = os.path.join(BASE_DIR, "metrics_summary.json")
    if os.path.exists(metrics_file):
        import json
        with open(metrics_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "dataset_stats": predictor.dataset_stats,
        "benchmarks": predictor.benchmarks,
        "roc_data": predictor.roc_data,
        "feature_importances": [
            {
                "feature": fi["feature"],
                "importance": float(fi["importance"]),
                "is_structural": bool(fi["is_structural"])
            }
            for fi in predictor.feature_importances
        ],
        "feature_names": predictor.feature_names
    }

def run_retrain_worker(half_limit: int):
    global retrain_state
    try:
        retrain_state["is_training"] = True
        retrain_state["progress"] = 15
        retrain_state["status_message"] = f"Loading dataset ({half_limit} emails/class)..."
        retrain_state["error"] = None

        from train_and_cache import train_and_save
        retrain_state["progress"] = 40
        retrain_state["status_message"] = "Extracting text & 14 structural features..."

        train_and_save(half_limit=half_limit)
        
        retrain_state["progress"] = 90
        retrain_state["status_message"] = "Reloading model bundle into memory..."
        
        predictor.load()

        retrain_state["progress"] = 100
        retrain_state["status_message"] = "Retraining complete! Models active."
        retrain_state["last_trained"] = predictor.dataset_stats.get("timestamp", "N/A")
    except Exception as e:
        retrain_state["error"] = str(e)
        retrain_state["status_message"] = f"Retraining failed: {str(e)}"
    finally:
        retrain_state["is_training"] = False

@app.post("/api/retrain")
def trigger_retrain(req: RetrainRequest, background_tasks: BackgroundTasks):
    global retrain_state
    if retrain_state["is_training"]:
        raise HTTPException(status_code=409, detail="A retraining session is already in progress.")

    limit = max(100, min(1000, req.half_limit or 400))
    background_tasks.add_task(run_retrain_worker, limit)
    return {
        "message": f"Retraining initiated in background with {limit} emails per category.",
        "status": "started"
    }

@app.get("/api/retrain-status")
def get_retrain_status():
    return retrain_state

# Serve ROC plot images directly
@app.get("/api/plots/{plot_name}")
def get_plot(plot_name: str):
    valid_plots = {
        "roc_properties_only.png": os.path.join(BASE_DIR, "roc_properties_only.png"),
        "roc_tf-idf_only.png": os.path.join(BASE_DIR, "roc_tf-idf_only.png"),
        "roc_tf-idf_plus_properties.png": os.path.join(BASE_DIR, "roc_tf-idf_plus_properties.png"),
    }
    path = valid_plots.get(plot_name)
    if path and os.path.exists(path):
        return FileResponse(path, media_type="image/png")
    raise HTTPException(status_code=404, detail="Plot not found")

# Mount static directory for frontend
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8050))
    print("\n========================================================")
    print("  PHISHING EMAIL CLASSIFIER - WEB APPLICATION")
    print(f"  Server launching at: http://localhost:{port}")
    print("========================================================\n")
    uvicorn.run("server:app", host="127.0.0.1", port=port, reload=False)
