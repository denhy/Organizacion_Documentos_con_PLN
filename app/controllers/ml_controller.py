from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import QTimer
from app.views.param_dialog import ParamsDialog 
from app.ml_processor.extract_text import *
from app.ml_processor.cluster_documents import ClusterDocuments
from app.controllers.worker_controller import ProcessWorker 
from PyQt5.QtCore import  pyqtSignal,  QObject 
from datetime import datetime
from app.ml_processor.training import build_dataset, save_model_bundle, accuracy_score, train_mlp
from app.ml_processor.classify_documents import load_model_bundle, classify_documents, save_predictions_csv
from app.ml_processor.cluster_documents import create_topic_folders_and_organize

class MLController(QObject):
    progress_changed = pyqtSignal(int) 
    status_changed = pyqtSignal(str)
    finished = pyqtSignal(bool, object)  

    def __init__(self, view=None):
        super().__init__()
        self.view = view
        self._worker = None

    # Ajusta a tu implementación real
    # def get_files_dialog(self):
       
    #     return [], ""

    # def open_parameters_dialog(self):
    #     pass

    # ---------- JOB FUNCTION para clustering  ----------
    @staticmethod
    def _cluster_job(progress_cb, status_cb,
                     file_paths: List[Tuple[str, str]],
                     output_base_dir: str):
      
        status_cb("Preprocesando documentos y generando embeddings…")
        progress_cb(5)

        cluster_model = ClusterDocuments()

        text_list, embeddings_list = preprocess_documents(file_paths, 
                                                     encoder=cluster_model.model_embeddings,  
                                                     progress_cb=progress_cb,
                                                     status_cb=status_cb)
        progress_cb(40)

        status_cb("Calculando tópicos con BERTopic…")
        topics, probs, topic_model = cluster_model.get_clusters(text_list, embeddings_list)
        progress_cb(70)

        status_cb("Organizando documentos en carpetas…")
        mapping = create_topic_folders_and_organize(
            output_base_dir, text_list, topics, topic_model )
        progress_cb(100)
        status_cb("Proceso completado.")
        
        return {"output_dir": output_base_dir, "num_docs": len(mapping)}

   
    def cluster_process(self, file_paths, output_base_dir="Documentos_Organizados"):
       
        if self._worker and self._worker.isRunning():
            return

        self._worker = ProcessWorker(
            self._cluster_job,
            file_paths,
            output_base_dir=output_base_dir
        )

  
        self._worker.progress.connect(self.progress_changed.emit)
        self._worker.status.connect(self.status_changed.emit)
        self._worker.done.connect(self._on_worker_done)

        self._worker.start()

    
    def _on_worker_done(self, ok: bool, payload_or_exc):
        if ok:
         
            output_dir = payload_or_exc.get("output_dir", "")
            self.finished.emit(True, output_dir)
        else:
            # payload_or_exc es la Exception
            self.finished.emit(False, str(payload_or_exc))
            
    def auto_classify():
        pass
    
    def manual_classify(): 
        
        pass
    
    @staticmethod
    def _train_job(progress_cb, status_cb, file_paths, model_name, models_base_dir="data/models"):
       
        if not model_name or not model_name.strip():
            raise ValueError("Debes proporcionar un nombre de modelo.")

        status_cb("Generando Embeddigns")
        progress_cb(5)

        
        cluster_model = ClusterDocuments()
        text_list, X, y, le = build_dataset(
            file_paths,
            encoder=cluster_model.model_embeddings,
            progress_cb=progress_cb,   
            status_cb=status_cb
        )

        if len(set(y)) < 2:
            raise ValueError("Se requieren al menos 2 clases para entrenar el MLP.")

        status_cb("Entrenando Perceptrón Multicapa")
        progress_cb(70)
        clf, metrics = train_mlp(X, y, status_cb=status_cb)

        status_cb("Guardando resultados del modelo…")
        progress_cb(90)
        out_dir = save_model_bundle(
            model_name=model_name,
            base_dir=models_base_dir,
            classifier=clf,
            label_encoder=le,
            metadata={
                "num_docs": len(text_list),
                "classes": list(le.classes_),
                "metrics": metrics
            }
        )
        progress_cb(100)
        status_cb(f"Entrenamiento completado. Modelo guardado en: {out_dir}")
        return {"output_dir": out_dir, "metrics": metrics }

    
    def train_process(self, file_paths, model_name):
        if self._worker and self._worker.isRunning():
            return
        self._worker = ProcessWorker(
            self._train_job,
            file_paths,
            model_name=model_name
        )
        self._worker.progress.connect(self.progress_changed.emit)
        self._worker.status.connect(self.status_changed.emit)
        self._worker.done.connect(self._on_worker_done)
        self._worker.start()
    
    

    # --- JOB: clasificación ---
    @staticmethod
    def _classify_job(progress_cb, status_cb, file_paths, model_dir):
        status_cb("Cargando modelo…")
        progress_cb(5)
        bundle = load_model_bundle(model_dir)

        status_cb("Extrayendo texto y generando embeddings…")
        progress_cb(15)
        results = classify_documents(
            file_paths=file_paths,
            encoder=bundle["encoder"],
            classifier=bundle["classifier"],
            label_encoder=bundle["label_encoder"],
            progress_cb=progress_cb,
            status_cb=status_cb,
            base_progress=15,
            span_progress=80  # 15→95%
        )

        progress_cb(100)
        status_cb("Clasificación completada.")
        # devolvemos resultados crudos para mostrarlos en la vista
        return {"results": results, "model_dir": model_dir}

    def classify_process(self, file_paths, model_dir):
        if self._worker and self._worker.isRunning():
            return
        self._worker = ProcessWorker(self._classify_job, file_paths, model_dir=model_dir)
        self._worker.progress.connect(self.progress_changed.emit)
        self._worker.status.connect(self.status_changed.emit)
        self._worker.done.connect(self._on_classify_done)
        self._worker.start()

    def _on_classify_done(self, ok: bool, payload_or_exc):
        if ok:
            # Pasamos todo el payload para que la vista lo abra en tabla
            self.finished.emit(True, payload_or_exc)
        else:
            self.finished.emit(False, str(payload_or_exc))
            
            def apply_params():
                pass
            def set_params():
                pass
            
        def open_params(): pass