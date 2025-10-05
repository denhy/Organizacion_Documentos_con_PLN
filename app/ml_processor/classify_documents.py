import os
import csv
from pathlib import Path
import joblib
import numpy as np
from typing import List, Dict, Any, Optional
from app.ml_processor.extract_text import extract_text_from_pdf
from data.models import embeddigns  


def load_model_bundle(model_dir: str):
    model_dir = Path(model_dir)
    clf = joblib.load(model_dir / "model.pkl")
    le = joblib.load(model_dir / "label_encoder.pkl")
 
    encoder = embeddigns.get_model()
    return {"classifier": clf, "label_encoder": le, "encoder": encoder, "dir": model_dir}

def classify_documents(file_paths: List[str],
                       encoder,
                       classifier,
                       label_encoder,
                       progress_cb=None,
                       status_cb=None,
                       base_progress: int = 15,
                       span_progress: int = 70) -> List[Dict[str, Any]]:
    texts = []
    n = max(1, len(file_paths))
    for i, f in enumerate(file_paths, start=1):
        if status_cb: status_cb(f"Extrayendo texto ({i}/{n})…")
        txt = extract_text_from_pdf(f) or ""
        texts.append(txt)
        if progress_cb:
            progress_cb(base_progress + int(span_progress * 0.5 * i / n))  # ~hasta 50% de la fase

    if status_cb: status_cb("Generando embeddings…")
    X = encoder.encode(
        texts,
        batch_size=16,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False
    )
    if X.ndim == 1:
        X = X.reshape(1, -1)
    if progress_cb:
        progress_cb(base_progress + int(span_progress * 0.9))  # casi termina la fase

    preds = classifier.predict(X)
    try:
        proba = classifier.predict_proba(X)
        conf = np.max(proba, axis=1).tolist()
    except Exception:
        conf = [None] * len(preds)

    labels = label_encoder.inverse_transform(preds)
    results = []
    for f, y, c in zip(file_paths, labels, conf):
        results.append({"file_path": f, "predicted_label": y, "confidence": c})
    return results

def save_predictions_csv(model_dir: str, results: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
    model_dir = Path(model_dir)
    out_dir = model_dir / "predictions"
    out_dir.mkdir(parents=True, exist_ok=True)
    fname = filename or "predictions.csv"
    out_csv = out_dir / fname
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["file_path", "predicted_label", "confidence"])
        w.writeheader()
        for r in results:
            w.writerow(r)
    return str(out_csv)
