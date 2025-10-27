
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QProgressDialog
from app.ml_processor.cluster_documents import ClusterDocuments
from app.controllers.worker_controller import ProcessWorker 


from app.ml_processor.training import build_dataset, save_model_bundle, accuracy_score, train_mlp
from app.ml_processor.classify_documents import load_model_bundle, classify_documents
from app.ml_processor.cluster_documents import create_topic_folders_and_organize
from app.ml_processor.app_state import AppState


from app.ml_processor.extract_text import preprocess_documents
from app.views.hiperparametros_dialog import ClusteringHyperparamsDialog
from typing import List, Tuple, Optional, Dict
import numpy as np
from data.models import embeddigns

from app.ml_processor.cluster_documents import (
    ClusterDocuments,
    create_topic_folders_and_organize,
)




class MLController(QObject):
    progress_changed = pyqtSignal(int)
    status_changed   = pyqtSignal(str)
    finished         = pyqtSignal(bool, object)
    goto_explorer    = pyqtSignal()   # si lo usas luego
    hparams_updated =  pyqtSignal(object) 

    def __init__(self, view=None):
        super().__init__()
        self.view = view
        self._worker: Optional[ProcessWorker] = None
        self.state = AppState()
        self._explorer_page = None

    # ---------------- worker helper ----------------
    def _show_loading(self, parent, text="Cargando…"):
        try:
            dlg = QProgressDialog(text, None, 0, 0, parent)
            dlg.setWindowTitle("Por favor espera")
            dlg.setWindowModality(2)  # ApplicationModal
            dlg.setMinimumDuration(0)
            dlg.setAutoClose(False)
            dlg.setCancelButton(None)
            dlg.show()
            self._loading = dlg
        except Exception:
            self._loading = None

    def _hide_loading(self):
        if self._loading is not None:
            try:
                self._loading.close()
            except Exception:
                pass
        self._loading = None

    # ======= CLUSTERING principal (Agrupar) =======
    @staticmethod
    def _cluster_job(progress_cb, status_cb,
                     file_paths: List[Tuple[str, str]],
                     output_base_dir: str,
                     hdbscan_params: Optional[dict] = None):
        status_cb("Preprocesando documentos y generando embeddings…")
        progress_cb(5)

        cluster_model = ClusterDocuments(hdbscan_params=hdbscan_params)
        encoder = cluster_model.model_embeddings

        text_list, embeddings_list = preprocess_documents(
            file_paths,
            encoder=encoder,
            progress_cb=progress_cb,
            status_cb=status_cb
        )
        progress_cb(40)

        status_cb("Calculando tópicos con BERTopic…")
        topics, probs, topic_model = cluster_model.get_clusters(text_list, embeddings_list)
        progress_cb(70)

        status_cb("Organizando documentos en carpetas…")
        mapping = create_topic_folders_and_organize(
            output_base_dir, text_list, topics, topic_model
        )
        progress_cb(100)
        status_cb("Proceso completado.")
        return {"output_dir": output_base_dir, "num_docs": len(mapping)}

    def cluster_process(self, file_paths, output_base_dir="Documentos_Organizados"):
        # Usa preset si el usuario ya eligió algo en el diálogo
        hparams = None
        if self.state.hdbscan_preset:
            hparams = self.state.hdbscan_preset.get("params", None) if self.state.hdbscan_preset.get("algorithm") == "HDBSCAN" else None

        self._start_worker(
            self._cluster_job,
            _done_slot=self._on_cluster_done,
            file_paths=file_paths,
            output_base_dir=output_base_dir,
            hdbscan_params=hparams
        )

    def _on_cluster_done(self, ok: bool, payload_or_exc):
        if ok:
            output_dir = payload_or_exc.get("output_dir", "")
            self.finished.emit(True, output_dir)
        else:
            self.finished.emit(False, str(payload_or_exc))

    # ======= worker wrapper =======
    def _start_worker(self, job_fn, _done_slot=None, **job_kwargs):
        if self._worker and self._worker.isRunning():
            self.status_changed.emit("Ya hay un proceso en ejecución.")
            return
        self._worker = ProcessWorker(job_fn, **job_kwargs)
        self._worker.progress.connect(self.progress_changed.emit)
        self._worker.status.connect(self.status_changed.emit)
        if _done_slot is not None:
            self._worker.done.connect(_done_slot)
        else:
            self._worker.done.connect(self._on_worker_done)
        self._worker.start()

    def _on_worker_done(self, ok: bool, payload_or_exc):
        if ok:
            self.finished.emit(True, payload_or_exc)
        else:
            self.finished.emit(False, str(payload_or_exc))

     # =============== EXPLORADOR DE HIPERPARÁMETROS =================

    # =============== EXPLORADOR DE HIPERPARÁMETROS ===============
    def open_hparams_from_group(self, parent_widget, file_pairs):
        """
        Llamado por GroupPage.open_params(): genera embeddings (si hace falta)
        y abre el diálogo de Visualizar Hiperparámetros cuando terminan.
        """
        if not file_pairs:
            self.status_changed.emit("Selecciona documentos primero.")
            return

        # Guarda selección actual (por si la necesitas después)
        self.state.file_pairs = file_pairs

        # Dispara el job que extrae texto y crea embeddings (barra de progreso de la página se usa)
        self.status_changed.emit("Preparando embeddings para visualizar hiperparámetros…")
        self.progress_changed.emit(5)

        self._start_worker(
            self._emb_job,
            _done_slot=lambda ok, payload: self._on_emb_for_dialog_done(ok, payload, parent_widget),
            file_paths=file_pairs
        )

    def _emb_job(self, progress_cb, status_cb, file_paths):
        """Job en hilo: extrae textos y genera embeddings para el diálogo."""
        status_cb("Extrayendo texto y generando embeddings…")
        text_list, embeddings = preprocess_documents(
            file_paths,
            encoder=embeddigns.get_model(),
            progress_cb=progress_cb,
            status_cb=status_cb
        )
        X = np.asarray(embeddings, dtype="float32")
        names = [d["file_path"] for d in text_list]
        texts = [d["texto"] for d in text_list]
        progress_cb(100)
        return {"X": X, "names": names, "texts": texts}

    def _on_emb_for_dialog_done(self, ok: bool, payload_or_exc, parent_widget):
        """Cuando termina _emb_job: guarda en estado y abre el diálogo."""
        if not ok:
            self.status_changed.emit(f"❌ Error al generar embeddings: {payload_or_exc}")
            return
        payload = payload_or_exc or {}
        self.state.X = payload.get("X")
        self.state.doc_names = payload.get("names") or []
        self.state.docs_texts = payload.get("texts") or []

        if self.state.X is None:
            self.status_changed.emit("❌ No se recibieron embeddings.")
            return

        self.status_changed.emit("Abriendo explorador de hiperparámetros…")
        self.progress_changed.emit(100)
        self._open_hparams_dialog(parent_widget)

    def _open_hparams_dialog(self, parent_widget):
        """Crea y muestra el QDialog con la tabla y los plots."""
        from app.views.hiperparametros_dialog import ClusteringHyperparamsDialog
        dlg = ClusteringHyperparamsDialog(
            X=self.state.X,
           
            docs_texts=self.state.docs_texts,
            parent=parent_widget
        )
        dlg.params_selected.connect(self._on_hparams_selected)
        dlg.exec_()

    def _on_hparams_selected(self, payload: dict):
        """Recibe {'algorithm': 'HDBSCAN'|'KMEANS', 'params': {...}} desde el diálogo."""
        algo = (payload.get("algorithm") or "HDBSCAN").upper()
        if algo == "HDBSCAN":
            self.state.hdbscan_preset = payload
            self.state.kmeans_preset = None
        else:
            self.state.kmeans_preset = payload
            self.state.hdbscan_preset = None
        # Notifica a GroupPage para que muestre el recordatorio en la derecha
        self.hparams_updated.emit(payload)

    # Si no la tenías:
    def _on_worker_done(self, ok: bool, payload_or_exc):
        if ok:
            self.finished.emit(True, payload_or_exc)
        else:
            self.finished.emit(False, str(payload_or_exc))
    # ---------------- ENTRENAR MLP ----------------
    @staticmethod
    def _train_job(progress_cb, status_cb, file_paths, model_name, models_base_dir="data/models"):
        if not model_name or not model_name.strip():
            raise ValueError("Debes proporcionar un nombre de modelo.")

        status_cb("Generando embeddings…")
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

        status_cb("Entrenando Perceptrón Multicapa…")
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
        return {"output_dir": out_dir, "metrics": metrics}

    def train_process(self, file_paths, model_name):
        self._start_worker(self._train_job, self._on_worker_done,
                           file_paths=file_paths, model_name=model_name)
        
    def reset_state_for_train(self):
        """Limpia cualquier estado que uses durante entrenamiento."""
        try:
            # Si guardas algo específico para la página de entrenamiento, límpialo aquí
            self.progress_changed.emit(0)
            self.status_changed.emit("")
        except Exception:
            pass


    # ---------------- CLASIFICAR ----------------
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
            span_progress=80
        )

        progress_cb(100)
        status_cb("Clasificación completada.")
        return {"results": results, "model_dir": model_dir}

    def classify_process(self, file_paths, model_dir):
        self._start_worker(self._classify_job, self._on_classify_done,
                           file_paths=file_paths, model_dir=model_dir)

    def _on_classify_done(self, ok: bool, payload_or_exc):
        if ok:
            self.finished.emit(True, payload_or_exc)
        else:
            self.finished.emit(False, str(payload_or_exc))
            
            
