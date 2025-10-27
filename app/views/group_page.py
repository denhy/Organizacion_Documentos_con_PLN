# app/views/group_page.py

from app.utils.styles import Styles
from app.views.listDocumentWidget import DocumentListWidget
# app/views/group_page.py
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, QProgressBar, QHBoxLayout, QFrame,
                             QGroupBox, QFormLayout, QGridLayout)
from PyQt5.QtCore import Qt 


class GroupPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.docs = []
        self.setup_ui()
        self._wire_signals()
        self.list_docs.filesChanged.connect(self._on_files_changed)   # ya lo tenías
        self.list_docs.clearClicked.connect(self.clear_page)  

    def setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(50, 50, 50, 50)
        root.setSpacing(25)

        self.lbl = QLabel("Agrupamiento de documentos")
        self.lbl.setStyleSheet(Styles.TITLES)
        root.addWidget(self.lbl)


        # ====== Zona central dividida: Izq (lista) / Der (recordatorio) ======
        mid = QHBoxLayout()
        mid.setSpacing(24)

        # --- IZQUIERDA: lista de documentos + botones
        left = QVBoxLayout()
        self.list_docs = DocumentListWidget()
        left.addWidget(self.list_docs)

        self.list_docs.filesChanged.connect(self._on_files_changed)
        
        

        btns = QHBoxLayout()
        self.btn_auto = QPushButton("Agrupar automáticamente")
        self.btn_auto.setStyleSheet(Styles.BUTTON_VIEWS)
        self.btn_auto.setEnabled(False)
        self.btn_auto.setFixedSize(280, 50)
        self.btn_auto.clicked.connect(self.group_documents)
        btns.addWidget(self.btn_auto)

        self.btn_params = QPushButton("Visualizar hiperparámetros")
        self.btn_params.setStyleSheet(Styles.BUTTON_VIEWS)
        self.btn_params.setEnabled(False)
        self.btn_params.setFixedSize(280, 50)
        self.btn_params.clicked.connect(self.open_params)
        btns.addWidget(self.btn_params)

        left.addLayout(btns)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.hide()
        left.addWidget(self.progress)

        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet("color:#bbb;")
        self.lbl_status.setWordWrap(True)
        left.addWidget(self.lbl_status)

        left.addStretch()
        root.addLayout(left, stretch=3)

        # --- DERECHA: recordatorio de hiperparámetros elegidos
        right = QVBoxLayout()
        box = QGroupBox("Hiperparámetros activos")
        grid = QGridLayout(box)

        self.lbl_hparams = QLabel("Aún no has seleccionado hiperparámetros.")
        self.lbl_hparams.setWordWrap(True)
        grid.addWidget(self.lbl_hparams, 0, 0)
      

        right.addWidget(box)
        right.addStretch()
        root.addLayout(right, stretch=2)


    def _wire_signals(self):
        self.controller.progress_changed.connect(self.update_progress)
        self.controller.status_changed.connect(self.update_status)
        self.controller.finished.connect(self.on_finished)
     
        self.controller.hparams_updated.connect(self.set_hparams_reminder)

    def _on_files_changed(self, paths):
        def to_pair(path):
            return (os.path.basename(os.path.dirname(path)), path)
        self.docs = [to_pair(p) for p in paths]
        has_docs = len(self.docs) > 0
        self.btn_auto.setEnabled(has_docs)
        self.btn_params.setEnabled(has_docs)

    def group_documents(self):
        if not self.docs:
            return
        self.progress.setValue(0)
        self.progress.show()
        self.lbl.setText("Procesando documentos…")
        self.controller.cluster_process(self.docs)

    def open_params(self):
        if not self.docs:
            self.update_status("Selecciona documentos primero.")
            return
        # Usar la barra de progreso/label del propio GroupPage
        self.progress.setValue(0)
        self.progress.show()
        self.update_status("Preparando explorador de hiperparámetros…")
        # El controlador generará embeddings y abrirá el diálogo (sin “loading dialog” aparte)
        self.controller.open_hparams_from_group(self, self.docs)

    def update_progress(self, value: int):
        self.progress.show()
        self.progress.setValue(value)

    def update_status(self, msg: str):
        self.lbl.setText(msg)

    def on_finished(self, ok: bool, out_dir: str):
        if ok:
            self.lbl.setText(" Documentos agrupados con éxito ✅")
        else:
            self.lbl.setText("❌ Ocurrió un error durante el procesamiento")
        self.progress.hide()

    # === Recordatorio lateral de hiperparámetros ===
    def set_hparams_reminder(self, payload: dict):
        """payload viene del dialog: {'algorithm': 'HDBSCAN'|'KMEANS', 'params': {...}}"""
        if not payload:
            self.lbl_hparams.setText("Hiperparámetros seleccionados: —")
            return

        algo = str(payload.get("algorithm", "")).upper()
        params = payload.get("params", {}) or {}

        # Construye un texto bonito (HTML) o en texto plano. Aquí uso HTML simple.
        lines = [f"<b>Algoritmo:</b> {algo}"]

        if algo == "HDBSCAN":
            lines.append(f"min_cluster_size: {params.get('min_cluster_size', '-')}")
            lines.append(f"min_samples: {params.get('min_samples', '-')}")
            lines.append(f"cluster_selection_epsilon: {params.get('cluster_selection_epsilon', '-')}")
            lines.append(f"metric: {params.get('metric', '-')}")
            # opcional: método de selección si lo manejas
            if 'cluster_selection_method' in params:
                lines.append(f"cluster_selection_method: {params.get('cluster_selection_method')}")
        elif algo == "KMEANS":
            lines.append(f"n_clusters: {params.get('n_clusters', '-')}")
            lines.append(f"init: {params.get('init', 'k-means++')}")
            lines.append(f"n_init: {params.get('n_init', '-')}")
            lines.append(f"max_iter: {params.get('max_iter', '-')}")
            lines.append(f"random_state: {params.get('random_state', 42)}")
        else:
            # Fallback genérico
            for k, v in params.items():
                lines.append(f"{k}: {v}")

        # UNE a un solo string → esto arregla el TypeError
        html = "<br>".join(lines)
        self.lbl_hparams.setText(html) 
        
    def clear_page(self):
        # 1) La lista YA se vació porque el widget lo hizo y emitió filesChanged([])
        self.docs = []

        # 2) Reset de botones
        self.btn_auto.setEnabled(False)
        self.btn_params.setEnabled(False)

        # 3) Reset de progreso / estado / títulos
        self.progress.setValue(0)
        self.progress.hide()
        self.lbl.setText("Agrupamiento de documentos")
        if hasattr(self, "lbl_status"):
            self.lbl_status.setText("")
        if hasattr(self, "lbl_hparams"):
            self.lbl_hparams.setText("Aún no has seleccionado hiperparámetros.")

        # 4) (Opcional) pide al controlador limpiar su estado para esta página
        if hasattr(self.controller, "reset_state_for_group"):
            self.controller.reset_state_for_group()
            
   