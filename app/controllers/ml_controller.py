from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import QTimer
from app.views.param_dialog import ParamsDialog 
from app.ml_processor.extract_text import *
from app.ml_processor.cluster_documents import ClusterDocuments
from app.controllers.worker_controller import ProcessWorker 
from PyQt5.QtCore import  pyqtSignal,  QObject 
from app.ml_processor.cluster_documents import create_topic_folders_and_organize

class MLController(QObject):
    progress_changed = pyqtSignal(int) 
    status_changed = pyqtSignal(str)
    finished = pyqtSignal(bool, str)  

    def __init__(self, view=None):
        super().__init__()
        self.view = view
        self._worker = None

    # Ajusta a tu implementación real
    def get_files_dialog(self):
       
        return [], ""

    def open_parameters_dialog(self):
        pass

    # ---------- JOB FUNCTION para clustering (reutiliza ProcessWorker genérico) ----------
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

        # Lo que retorne será el "payload" del worker
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
            # payload es dict con "output_dir"
            output_dir = payload_or_exc.get("output_dir", "")
            self.finished.emit(True, output_dir)
        else:
            # payload_or_exc es la Exception
            self.finished.emit(False, str(payload_or_exc))
            
    def auto_classify():
        pass
    
    def manual_classify(): 
        
        pass
    
    def train_documents():
        pass
    
    def apply_params():
        pass
    def set_params():
        pass
    
    def open_params(): pass