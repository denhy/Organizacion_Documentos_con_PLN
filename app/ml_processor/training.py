
import os, json
from pathlib import Path
import joblib
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

from app.ml_processor.extract_text import extract_text_from_pdf

def build_dataset(file_paths, encoder, progress_cb=None, status_cb=None):
   
    texts, labels, text_list = [], [], []
    n = max(1, len(file_paths))
    for i, (label, fpath) in enumerate(file_paths, start=1):
        if status_cb: status_cb(f"Extrayendo texto ({i}/{n})…")
        txt = extract_text_from_pdf(fpath) or ""
        texts.append(txt)
        labels.append(label)
        text_list.append({"file_path": fpath, "folder_name": label, "texto": txt})

        if progress_cb:
            base, span = 5, 55  
            progress_cb(base + int(span * i / n))

    if status_cb: status_cb("Generando embeddings…")
    X = encoder.encode(
        texts,
        batch_size=16,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False
    )
    if X.ndim == 1:  # por si hay un solo doc
        X = X.reshape(1, -1)

    le = LabelEncoder()
    y = le.fit_transform(labels)
    return text_list, X, y, le

def train_mlp(X, y, status_cb=None):
    
    if status_cb: status_cb("Particionando train/val…")
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y if len(set(y))>1 else None)

    clf = MLPClassifier(
        hidden_layer_sizes=(256, 128),
        activation="relu",
        solver="adam",
        alpha=1e-4,
        batch_size=32,
        learning_rate_init=1e-3,
        max_iter=50,          
        random_state=42,
        verbose=False
    )
    clf.fit(Xtr, ytr)

    ypred = clf.predict(Xte) if len(Xte)>0 else ytr
    acc = accuracy_score(yte if len(Xte)>0 else ytr, ypred)
    report = classification_report(yte if len(Xte)>0 else ytr, ypred, target_names=None, zero_division=0)
    metrics = {"accuracy": float(acc), "report": report}
    if status_cb: status_cb(f"Accuracy: {acc:.3f}")
    return clf, metrics

def save_model_bundle(model_name, base_dir, classifier, label_encoder, metadata: dict):
   
    out_dir = Path(base_dir) / model_name
    out_dir.mkdir(parents=True, exist_ok=True)

    joblib.dump(classifier, out_dir / "model.pkl")
    joblib.dump(label_encoder, out_dir / "label_encoder.pkl")
    with open(out_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    return str(out_dir)
