import os
from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton,
    QHBoxLayout, QProgressBar, QMessageBox
)
from PyQt5.QtCore import Qt
from app.utils.styles import Styles
from app.views.results_dialog import ResultsDialog
from app.views.listDocumentWidget import DocumentListWidget


        
class ClassifyPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.docs = []         
        self.model_dir = None   
        self.setup_ui()
        self._wire_signals()
        self._load_models()
        self.list_docs.filesChanged.connect(self._on_files_changed)   # ya lo tenías
        self.list_docs.clearClicked.connect(self.clear_page)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(18)

        self.lbl = QLabel("Clasificar documentos con un modelo entrenado")
        self.lbl.setStyleSheet(Styles.TITLES)
        layout.addWidget(self.lbl)

        # ---- fila de modelos ----
        row = QHBoxLayout()
        self.cmb_models = QComboBox()
        self.cmb_models.setStyleSheet(Styles.COMBO_BOX)
        self.cmb_models.setMinimumWidth(320)
        self.btn_refresh = QPushButton("Actualizar modelos")
        for b in (self.btn_refresh,):
            b.setStyleSheet(Styles.BUTTON_VIEWS)
            b.setFixedHeight(36)
        self.btn_refresh.clicked.connect(self._load_models)
        self.cmb_models.currentIndexChanged.connect(self._on_model_changed)
        row.addWidget(self.cmb_models)
        row.addWidget(self.btn_refresh)
        row.addStretch(1)
        layout.addLayout(row) 
        

        # ---- lista de documentos ----
        self.list_docs = DocumentListWidget()
        self.list_docs.filesChanged.connect(self._on_files_changed)
        layout.addWidget(self.list_docs)

  
        self.btn_classify = QPushButton("Clasificar automáticamente")
        #self.btn_manual = QPushButton("Decidir carpeta manualmente")

        for btn in [self.btn_classify]:
            btn.setStyleSheet(Styles.BUTTON_VIEWS)
            btn.setEnabled(False)
            btn.setFixedSize(280, 50)
            layout.addWidget(btn, alignment=Qt.AlignCenter)
        
        self.btn_classify.clicked.connect(self._on_classify_clicked)
        layout.addWidget(self.btn_classify, alignment=Qt.AlignCenter)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.hide()
        layout.addWidget(self.progress)

        layout.addStretch()

    def _wire_signals(self):
        self.controller.progress_changed.connect(self.update_progress)
        self.controller.status_changed.connect(self.update_status)
        self.controller.finished.connect(self.on_finished)

    # ---------- modelos ----------
    def _models_base_dir(self) -> Path:
   
        return Path(__file__).resolve().parents[2] / "data" / "models"

    def _load_models(self):
        self.cmb_models.blockSignals(True)
        self.cmb_models.clear()
        base = self._models_base_dir()
        if base.exists():
            # un modelo válido tiene al menos model.pkl y label_encoder.pkl
            for d in sorted(p.name for p in base.iterdir() if p.is_dir()):
                model_dir = base / d
                if (model_dir / "model.pkl").exists() and (model_dir / "label_encoder.pkl").exists():
                    self.cmb_models.addItem(d, userData=str(model_dir))
        self.cmb_models.blockSignals(False)
        self._on_model_changed(self.cmb_models.currentIndex())

    def _on_model_changed(self, idx: int):
        self.model_dir = self.cmb_models.itemData(idx) if idx >= 0 else None
        self._update_classify_enabled()

    # ---------- archivos ----------
    def _on_files_changed(self, paths):
        self.docs = paths[:]  # lista de rutas absolutas
        self._update_classify_enabled()

    def _update_classify_enabled(self):
        has_model = bool(self.model_dir)
        has_docs = len(self.docs) > 0
        self.btn_classify.setEnabled(has_model and has_docs)

    # ---------- acciones ----------
    def _on_classify_clicked(self):
        if not self.model_dir:
            QMessageBox.warning(self, "Modelo no seleccionado", "Elige un modelo.")
            return
        if not self.docs:
            QMessageBox.warning(self, "Sin documentos", "Agrega documentos para clasificar.")
            return
        self.progress.setValue(0)
        self.progress.show()
        self.lbl.setText("Clasificando…")
        # dispara el proceso
        self.controller.classify_process(self.docs, self.model_dir)

    # ---------- UI callbacks del controller ----------
    def update_progress(self, v: int):
        self.progress.show()
        self.progress.setValue(v)

    def update_status(self, msg: str):
        self.lbl.setText(msg)

    def on_finished(self, ok: bool, out):
        self.progress.hide()
        if not ok:
            self.lbl.setText(f" Error: {out}")
            return

        # Si llega un dict con 'results', mostramos el diálogo
        if isinstance(out, dict) and "results" in out:
            from app.views.results_dialog import ResultsDialog
            results = out["results"]
            self.lbl.setText(f"Clasificación completada · {len(results)} documentos")
            ResultsDialog(results, parent=self, title="Resultados de clasificación").exec_()
        else:
            # compat: por si viniera una cadena
            self.lbl.setText(str(out))
            
    def clear_page(self):
    # 1) La lista YA se vació por el widget
        self.docs = []

    
        if hasattr(self, "btn_classify"):
            self.btn_classify.setEnabled(False)

        # 3) Reset progreso/estado
        self.progress.setValue(0)
        self.progress.hide()
        self.lbl.setText("Clasificar documentos con un modelo entrenado")

   

        # 5) (Opcional) limpiar estado en el controlador
        if hasattr(self.controller, "reset_state_for_train"):
            self.controller.reset_state_for_train()
            
   