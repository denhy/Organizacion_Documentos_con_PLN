# models/cluster_documents.py
import os
import shutil
from typing import List, Tuple, Dict
from bertopic import BERTopic
from umap import UMAP
from hdbscan import HDBSCAN
from data.models import embeddigns

class ClusterDocuments:
    def __init__(self):
        self.model_embeddings = embeddigns.get_model()
        self.umap_model = UMAP(
            n_components=5,
            n_neighbors=15,
            min_dist=0.1,
            random_state=42
        )
        self.hdbscan = HDBSCAN(
            min_cluster_size=2,
            min_samples=2,
            cluster_selection_epsilon=0.1
        )

    def get_clusters(self, text_list, embeddings_list):
       
        topic_model = BERTopic(
            embedding_model=None,
            umap_model=self.umap_model,
            hdbscan_model=self.hdbscan,
            verbose=True
        )
        topics, probs = topic_model.fit_transform(
            [d['texto'] for d in text_list],
            embeddings=embeddings_list
        )
        return topics, probs, topic_model
    
    
def create_topic_folders_and_organize(base_output_dir: str,
                                    text_list: List[Dict],
                                    topics: List[int],
                                    topic_model: BERTopic):
    os.makedirs(base_output_dir, exist_ok=True)
    topic_info = topic_model.get_topic_info()  

    document_topic_mapping = []
    for i, (doc_info, topic) in enumerate(zip(text_list, topics)):
        document_topic_mapping.append({
            'original_index': i,
            'file_path': doc_info['file_path'],
            'folder_name': doc_info['folder_name'],
            'topic': topic,
            'topic_name': f"Topic_{topic}" if topic != -1 else "Outliers"
        })

    for doc_info in document_topic_mapping:
        topic_name = doc_info['topic_name']
        topic_folder = os.path.join(base_output_dir, topic_name)
        os.makedirs(topic_folder, exist_ok=True)

        original_filename = os.path.basename(doc_info['file_path'])
        new_file_path = os.path.join(topic_folder, original_filename)
        try:
            shutil.copy2(doc_info['file_path'], new_file_path)
            print(f"Copiado: {original_filename} -> {topic_folder}/")
        except Exception as e:
            print(f"Error copiando {original_filename}: {e}")

    return document_topic_mapping
