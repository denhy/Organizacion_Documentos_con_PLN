from sentence_transformers import SentenceTransformer
import torch

_model = None  # <-- variable global privada

def get_model():
    global _model
    if _model is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _model = SentenceTransformer("hiiamsid/sentence_similarity_spanish_es", device=device)
    return _model