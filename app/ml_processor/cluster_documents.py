# models/cluster_documents.py
import os
import shutil
from typing import List, Dict, Optional, Tuple

import numpy as np

try:
    import hdbscan
except Exception:
    hdbscan = None

from bertopic import BERTopic

# Ojo: este es el mismo módulo que usas en otros lados (typo intencional si así lo tienes)
# Debe exponer un método get_model() que devuelva un encoder de Sentence-Transformers
from data.models import embeddigns

def _safe_hdbscan_params(n_docs: int, params: Optional[Dict] = None) -> Dict:
    """
    Ajusta HDBSCAN para que no truene con pocos documentos:
    - min_samples <= n_docs
    - min_cluster_size <= n_docs
    """
    params = dict(params or {})
    min_samples = int(params.get("min_samples", 5) or 5)
    min_cluster_size = int(params.get("min_cluster_size", 5) or 5)

    min_samples = max(1, min(min_samples, n_docs))
    min_cluster_size = max(2, min(min_cluster_size, n_docs))

    out = {
        "min_cluster_size": min_cluster_size,
        "min_samples": min_samples,
        "cluster_selection_epsilon": float(params.get("cluster_selection_epsilon", 0.0)),
        "metric": params.get("metric", "euclidean")
    }
    # Permite pasar opcionalmente cluster_selection_method
    if "cluster_selection_method" in params:
        out["cluster_selection_method"] = params["cluster_selection_method"]
    return out


class ClusterDocuments:
    """
    Orquestador de clustering con BERTopic usando embeddings externos (ya calculados).
    """

    def __init__(self, hdbscan_params: Optional[Dict] = None):
        # Modelo de embeddings para preprocess_documents
        self.model_embeddings = embeddigns.get_model()

        # HDBSCAN seguro para pocos documentos
        self._hdbscan_params_raw = hdbscan_params or {}

    def get_clusters(
        self,
        text_list: List[Dict],
        embeddings_list: np.ndarray,
        verbose: bool = True
    ) -> Tuple[np.ndarray, np.ndarray, BERTopic]:
        """
        Aplica BERTopic sobre textos + embeddings fijos.
        Devuelve: topics, probabilities, topic_model
        """
        if hdbscan is None:
            raise ImportError("El paquete 'hdbscan' no está instalado.")

        docs = [d["texto"] for d in text_list]
        n_docs = len(docs)
        if n_docs == 0:
            raise ValueError("No hay documentos para clusterizar.")

        # Parámetros seguros según el tamaño del dataset
        safe_params = _safe_hdbscan_params(n_docs, self._hdbscan_params_raw)
        hdbscan_model = hdbscan.HDBSCAN(**safe_params)

        topic_model = BERTopic(
            embedding_model=None,      # ya traemos embeddings calculados
            hdbscan_model=hdbscan_model,
            verbose=verbose
        )

        topics, probs = topic_model.fit_transform(docs, embeddings=embeddings_list)
        return topics, probs, topic_model


def create_topic_folders_and_organize(
    base_output_dir: str,
    text_list: List[Dict],
    topics: List[int],
    topic_model: BERTopic
) -> List[Dict]:
    """
    Crea carpetas por tópico y copia ahí los documentos originales.
    Devuelve un mapeo documento->tópico.
    """
    os.makedirs(base_output_dir, exist_ok=True)

    # Puedes usar topic_model.get_topic_info() si luego quieres nombres más “bonitos”
    # pero aquí se deja un nombre simple por id de tópico.
    document_topic_mapping: List[Dict] = []
    for i, (doc_info, topic) in enumerate(zip(text_list, topics)):
        document_topic_mapping.append({
            "original_index": i,
            "file_path": doc_info["file_path"],
            "folder_name": doc_info["folder_name"],
            "topic": int(topic),
            "topic_name": f"Topic_{topic}" if topic != -1 else "Outliers"
        })

    for doc_info in document_topic_mapping:
        topic_name = doc_info["topic_name"]
        topic_folder = os.path.join(base_output_dir, topic_name)
        os.makedirs(topic_folder, exist_ok=True)

        original_filename = os.path.basename(doc_info["file_path"])
        new_file_path = os.path.join(topic_folder, original_filename)

        try:
            shutil.copy2(doc_info["file_path"], new_file_path)
            print(f"Copiado: {original_filename} -> {topic_folder}/")
        except Exception as e:
            print(f"Error copiando {original_filename}: {e}")

    return document_topic_mapping


__all__ = [
    "ClusterDocuments",
    "create_topic_folders_and_organize",
]