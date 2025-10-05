from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, 
    QListWidget, QProgressBar, QInputDialog, QMessageBox, QLineEdit
)
import os
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer, Qt
from app.utils.styles import Styles
from app.views.listDocumentWidget import DocumentListWidget

class TrainPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.docs = []  # [(label, path)]
        self.setup_ui()
        self._wire_signals()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(18)

        self.lbl = QLabel("Entrenar modelo por carpetas")
        self.lbl.setStyleSheet(Styles.TITLES)
        layout.addWidget(self.lbl)

        self.list_docs = DocumentListWidget()
        layout.addWidget(self.list_docs)

        # nombre del modelo
        name_row = QHBoxLayout()
        self.txt_model_name = QLineEdit()
        self.txt_model_name.setPlaceholderText("Nombre del modelo")
        self.txt_model_name.setStyleSheet(Styles.Q_LINE)
        self.btn_name = QPushButton("Cambiar nombre…")
        for b in (self.btn_name,):
            b.setStyleSheet(Styles.BUTTON_VIEWS)
            b.setFixedHeight(36)
        name_row.addWidget(self.txt_model_name, stretch=1)
        name_row.addWidget(self.btn_name)
        layout.addLayout(name_row)

        # Botón entrenar
        self.btn_train = QPushButton("Entrenar modelo")
        self.btn_train.setStyleSheet(Styles.BUTTON_VIEWS)
        self.btn_train.setEnabled(False)
        self.btn_train.setFixedSize(280, 46)
        self.btn_train.clicked.connect(self.train_model)
        layout.addWidget(self.btn_train, alignment=Qt.AlignCenter)
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.hide()
        layout.addWidget(self.progress)
        layout.addStretch()

        # eventos
        self.list_docs.filesChanged.connect(self._on_files_changed)
        self.txt_model_name.textChanged.connect(self._update_train_enabled)
        self.btn_name.clicked.connect(self._prompt_model_name)

    def _wire_signals(self):
        self.controller.progress_changed.connect(self.update_progress)
        self.controller.status_changed.connect(self.update_status)
        self.controller.finished.connect(self.on_finished)

    def _prompt_model_name(self):
        name, ok = QInputDialog.getText(self, "Nombre del modelo", "Escribe un nombre:")
        if ok and name.strip():
            self.txt_model_name.setText(name.strip())

    def _on_files_changed(self, paths):
        def to_pair(p): return (os.path.basename(os.path.dirname(p)), p)
        self.docs = [to_pair(p) for p in paths]
        self._update_train_enabled()

    def _update_train_enabled(self):
        has_docs = bool(self.docs)
        has_name = bool(self.txt_model_name.text().strip())
        self.btn_train.setEnabled(has_docs and has_name)

    def train_model(self):
        if not self.docs:
            QMessageBox.warning(self, "Sin datos", "Agrega documentos primero.")
            return
        name = self.txt_model_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Nombre requerido", "Escribe un nombre para el modelo.")
            return
        self.progress.setValue(0)
        self.progress.show()
        self.lbl.setText("Entrenando…")
        self.controller.train_process(self.docs, name)

    def update_progress(self, v:int):
        self.progress.show()
        self.progress.setValue(v)

    def update_status(self, msg:str):
        self.lbl.setText(msg)

    def on_finished(self, ok: bool, out_dir: str):
        if ok:
            self.lbl.setText(f" Modelo entrenado con éxito ✅ ")
        else:
            self.lbl.setText(f"❌ Error: {out_dir}")
        self.progress.hide()