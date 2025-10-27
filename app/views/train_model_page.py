from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, 
    QListWidget, QProgressBar, QInputDialog, QMessageBox, QLineEdit, QSizePolicy
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
        self.list_docs.filesChanged.connect(self._on_files_changed)   # ya lo tenías
        self.list_docs.clearClicked.connect(self.clear_page)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(18)

        # Título (lo dejamos fijo; no lo usaremos para status)
        self.lbl = QLabel("Entrenar modelo por carpetas")
        self.lbl.setStyleSheet(Styles.TITLES)
        self.lbl.setWordWrap(True)  # por si el estilo mete breaklines
        layout.addWidget(self.lbl)

        # Lista de documentos
        self.list_docs = DocumentListWidget()
        layout.addWidget(self.list_docs)

        # Nombre del modelo
        name_row = QHBoxLayout()
        self.txt_model_name = QLineEdit()
        self.txt_model_name.setPlaceholderText("Nombre del modelo")
        self.txt_model_name.setStyleSheet(Styles.Q_LINE)

        # Evitar que se estire de forma absurda:
        self.txt_model_name.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.txt_model_name.setMinimumWidth(220)
        self.txt_model_name.setMaximumWidth(420)  # <- límites razonables

        

        # No uses stretch=1 si estás limitando máximos; mejor sin stretch
        name_row.addWidget(self.txt_model_name)
        layout.addLayout(name_row)

        # Botón entrenar
        self.btn_train = QPushButton("Entrenar modelo")
        self.btn_train.setStyleSheet(Styles.BUTTON_VIEWS)
        self.btn_train.setEnabled(False)
        self.btn_train.setFixedSize(280, 46)
        self.btn_train.clicked.connect(self.train_model)
        layout.addWidget(self.btn_train, alignment=Qt.AlignCenter)

       

        # Progreso
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.hide()
        layout.addWidget(self.progress)

        # NUEVO: Label de estado (independiente del título)
        self.lbl_status = QLabel("")
        self.lbl_status.setWordWrap(True)
        self.lbl_status.setStyleSheet("color:#888;")
        self.lbl_status.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        layout.addWidget(self.lbl_status)

        layout.addStretch()

        # eventos
        self.list_docs.filesChanged.connect(self._on_files_changed)
        self.txt_model_name.textChanged.connect(self._update_train_enabled)
        

    def _wire_signals(self):
        self.controller.progress_changed.connect(self.update_progress)
        self.controller.status_changed.connect(self.update_status)
        self.controller.finished.connect(self.on_finished)

    def _prompt_model_name(self):
        name, ok = QInputDialog.getText(self, "Nombre del modelo", "Escribe un nombre:")
        if ok and name.strip():
            self.txt_model_name.setText(name.strip())

    def _on_files_changed(self, paths):
        import os
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
        # NO volver a tocar el título: usa el status
        self.update_status("Entrenando…")
        self.controller.train_process(self.docs, name)

    def update_progress(self, v:int):
        self.progress.show()
        self.progress.setValue(v)

    def update_status(self, msg:str):
        # mantener fijo el título; usa lbl_status para feedback
        self.lbl_status.setText(msg or "")

    def on_finished(self, ok: bool, out_dir: str):
        if ok:
            self.update_status("Modelo entrenado con éxito ✅")
        else:
            self.update_status(f"❌ Error: {out_dir}")
        self.progress.hide()
        
    def clear_page(self):
    # 1) La lista YA se vació por el widget
        self.docs = []

        # 2) Limpia campos del entrenamiento
        if hasattr(self, "txt_model_name"):
            self.txt_model_name.clear()
        if hasattr(self, "btn_train"):
            self.btn_train.setEnabled(False)

        # 3) Reset progreso/estado
        self.progress.setValue(0)
        self.progress.hide()
        self.lbl.setText("Entrenar modelo por carpetas")

        # 4) Si tenías un label de estado
        if hasattr(self, "lbl_status"):
            self.lbl_status.setText("")

        # 5) (Opcional) limpiar estado en el controlador
        if hasattr(self.controller, "reset_state_for_train"):
            self.controller.reset_state_for_train()

    