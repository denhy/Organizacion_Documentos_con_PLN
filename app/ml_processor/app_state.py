# app/state/app_state.py
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import numpy as np

@dataclass
class AppState:
    file_pairs: List[Tuple[str, str]] = field(default_factory=list)
    X: Optional[np.ndarray] = None
    doc_names: Optional[List[str]] = None
    doc_texts: Optional[List[str]] = None
    hdbscan_preset: Optional[dict] = None
    kmeans_preset: Optional[dict] = None                        # hiperparámetros elegidos
