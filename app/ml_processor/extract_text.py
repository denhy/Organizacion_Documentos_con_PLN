# models/text_extraction.py
import os
import shutil
from typing import List, Tuple, Dict
from pdfminer.high_level import extract_text
from pdf2image import convert_from_path
import pytesseract 
import numpy as np
from pdfminer.high_level import extract_text as pdfminer_extract_text
from app.ml_processor.text_clean import clean_text_es


pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# ------------------ Límites/constantes ------------------
MAX_PAGES = 3      # <- limitar a 3 páginas
MIN_CHARS = 50     # umbral para considerar que sí hay texto útil
# --------------------------------------------------------


def _detect_poppler_path():
    # Si tienes poppler en PATH, devolvemos None para que pdf2image lo use
    if shutil.which("pdftoppm") and shutil.which("pdftocairo"):
        return None
    return None  # Ajusta aquí si quieres poner una ruta fija


def _extract_text_pdfminer_first_n(pdf_path: str, n_pages: int = MAX_PAGES) -> str:
    """
    Extrae texto seleccionable SOLO de las primeras n páginas con pdfminer.
    """
    try:
        # pdfminer usa índices base-0 en page_numbers
        page_numbers = set(range(max(0, n_pages)))
        txt = pdfminer_extract_text(pdf_path, page_numbers=page_numbers) or ""
        return txt.strip()
    except Exception:
        return ""


def has_selectable_text(pdf_path: str) -> bool:
    """
    Revisa SOLO las primeras MAX_PAGES páginas para decidir si hay texto seleccionable.
    """
    try:
        text = _extract_text_pdfminer_first_n(pdf_path, n_pages=MAX_PAGES)
        clean_text = text.strip()
        return len(clean_text) > MIN_CHARS
    except Exception as e:
        print(f"⚠️ Error analizando PDF: {e}")
        return False


def extract_text_from_pdf(pdf_path: str, status_cb=None) -> str:
    """
    Extrae texto de las PRIMERAS MAX_PAGES páginas.
    1) Intenta con pdfminer (texto seleccionable limitado).
    2) Si no hay suficiente texto, intenta OCR en las PRIMERAS MAX_PAGES páginas.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"No se encontró el archivo: {pdf_path}")

    # 1) Texto seleccionable limitado
    if has_selectable_text(pdf_path):
        if status_cb:
            status_cb(f"Texto seleccionable (≤ {MAX_PAGES} páginas)…")
        try:
            return _extract_text_pdfminer_first_n(pdf_path, n_pages=MAX_PAGES)
        except Exception as e:
            if status_cb:
                status_cb(f"Error al extraer texto seleccionable: {e}")

    # 2) OCR limitado
    if status_cb:
        status_cb(f"Extrayendo texto por OCR (≤ {MAX_PAGES} páginas)…")
    try:
        images = convert_from_path(
            pdf_path,
            dpi=300,
            poppler_path=_detect_poppler_path(),
            first_page=1,
            last_page=MAX_PAGES  # <-- sólo primeras 3 páginas
        )
    except Exception as e:
        if status_cb:
            status_cb(f"Error al rasterizar para OCR: {e}")
        images = []

    parts = []
    for i, img in enumerate(images, start=1):
        try:
            txt = pytesseract.image_to_string(img, lang="spa")
        except Exception as e:
            if status_cb:
                status_cb(f"Extracción OCR falló en página {i}: {e}")
            txt = ""
        parts.append(f"--- Página {i} ---\n{txt}")

    return "\n\n".join(parts).strip()


def preprocess_documents(file_paths, encoder, progress_cb=None, status_cb=None):
    """
    Igual que tu versión, pero extract_text_from_pdf ya está limitada a MAX_PAGES.
    """
    text_list = []
    texts = []

    n = max(1, len(file_paths))
    for i, (folder_name, file) in enumerate(file_paths, start=1):
        if status_cb:
            status_cb(f"Extrayendo texto ({i}/{n})…") 
        
        raw_txt = extract_text_from_pdf(file, status_cb=status_cb) or ""
        clean_txt = clean_text_es(raw_txt)  # <-- LIMPIEZA AQUÍ
       
        text_list.append({'file_path': file, 'folder_name': folder_name, 'texto': clean_txt})
        texts.append(clean_txt)
        if progress_cb:
            base, span = 5, 30  # 5→35%
            progress_cb(base + int(span * i / n))

    if status_cb:
        status_cb("Generando embeddings…")

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