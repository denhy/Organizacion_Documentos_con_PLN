# models/text_extraction.py
import os
import shutil
from typing import List, Tuple, Dict
from pdfminer.high_level import extract_text
from pdf2image import convert_from_path
import pytesseract 
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def _detect_poppler_path():
    # Intenta usar PATH del sistema si está disponible
    if shutil.which("pdftoppm") and shutil.which("pdftocairo"):
        return None  
    
    return None

def has_selectable_text(pdf_path: str) -> bool:
    try:
        text = extract_text(pdf_path) or ""
        clean_text = text.strip()
        return len(clean_text) > 50
    except Exception as e:
        print(f"⚠️ Error analizando PDF: {e}")
        return False

def extract_text_from_pdf(pdf_path: str, status_cb=None) -> str:
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"No se encontró el archivo: {pdf_path}")

    if has_selectable_text(pdf_path):
        if status_cb: status_cb("Texto seleccionable (sin OCR)…")
        try:
            return (extract_text(pdf_path) or "").strip()
        except Exception as e:
            if status_cb: status_cb(f"Error con pdfminer: {e}")


    if status_cb: status_cb("Aplicando OCR con Tesseract…")
    images = convert_from_path(pdf_path, dpi=300, poppler_path=_detect_poppler_path())

    parts = []
    for i, img in enumerate(images, start=1):
        try:
            txt = pytesseract.image_to_string(img, lang="spa")
        except Exception as e:
            if status_cb: status_cb(f"OCR falló en página {i}: {e}")
            txt = ""
        parts.append(f"--- Página {i} ---\n{txt}")

    return "\n\n".join(parts).strip()

def preprocess_documents(file_paths, encoder, progress_cb=None, status_cb=None):

    text_list = []
    texts = []

    n = max(1, len(file_paths))
    for i, (folder_name, file) in enumerate(file_paths, start=1):
        if status_cb: status_cb(f"Extrayendo texto ({i}/{n})…")
        txt = extract_text_from_pdf(file, status_cb=status_cb) or ""
        text_list.append({'file_path': file, 'folder_name': folder_name, 'texto': txt})
        texts.append(txt)
        if progress_cb:
            base, span = 5, 30  # 5→35%
            progress_cb(base + int(span * i / n))

    if status_cb: status_cb("Generando embeddings…")

    embeddings = encoder.encode(
        texts,
        batch_size=16,                 
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False
    )  

   
    if embeddings.ndim == 1:
        embeddings = embeddings.reshape(1, -1)

    if progress_cb:
        progress_cb(40)  # cerramos la fase de preproceso

    return text_list, embeddings