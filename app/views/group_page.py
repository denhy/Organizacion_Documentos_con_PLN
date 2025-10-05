
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QProgressBar
)
import os
from PyQt5.QtCore import Qt
from app.utils.styles import Styles
from app.views.listDocumentWidget import DocumentListWidget

class GroupPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.docs = []  
        self.setup_ui()
        self._wire_signals()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(25)

        self.lbl = QLabel("Agrupamiento de documentos")
        self.lbl.setStyleSheet(Styles.TITLES)
        layout.addWidget(self.lbl)

        self.list_docs = DocumentListWidget()
        layout.addWidget(self.list_docs) 
        
        self.list_docs.filesChanged.connect(self._on_files_changed)

        # Botones
        self.btn_auto = QPushButton("Agrupar automáticamente")
        self.btn_auto.setStyleSheet(Styles.BUTTON_VIEWS)
        self.btn_auto.setEnabled(False)
        self.btn_auto.setFixedSize(280, 50)
        self.btn_auto.clicked.connect(self.group_documents)

        self.btn_params = QPushButton("Visualizar hiperparámetros")
        self.btn_params.setStyleSheet(Styles.BUTTON_VIEWS)
        self.btn_params.setEnabled(False)
        self.btn_params.setFixedSize(280, 50)
        self.btn_params.clicked.connect(self.open_params)

        for btn in [self.btn_auto, self.btn_params]:
            layout.addWidget(btn, alignment=Qt.AlignCenter)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.hide()
        layout.addWidget(self.progress)
        layout.addStretch()
        self.list_docs.filesChanged.connect(self._on_files_changed)

    def _wire_signals(self):
        self.controller.progress_changed.connect(self.update_progress)
        self.controller.status_changed.connect(self.update_status)
        self.controller.finished.connect(self.on_finished)


    def upload_docs(self):
        files, _ = self.controller.get_files_dialog()
        if files:
            for f in files:
                self.list_docs.add_file_item(f)  # esto disparará filesChanged

    def _on_files_changed(self, paths):

        def to_pair(path):
            return (os.path.basename(os.path.dirname(path)), path)

        self.docs = [to_pair(p) for p in paths]
        has_docs = len(self.docs) > 0
        self.btn_auto.setEnabled(has_docs)
        self.btn_params.setEnabled(has_docs)

    def group_documents(self):
        print("tocando boton")
        if not self.docs:
            return
        self.progress.setValue(0)
        self.progress.show()
        self.lbl.setText("Procesando documentos…")
        self.controller.cluster_process(self.docs)

    def update_progress(self, value: int):
        self.progress.show()
        self.progress.setValue(value)

    def update_status(self, msg: str):
        self.lbl.setText(msg)

    def on_finished(self, ok: bool, out_dir: str):
        if ok:
            self.lbl.setText(f" Documentos agrupados con éxito ✅")
        else:
            self.lbl.setText("❌ Ocurrió un error durante el procesamiento")
        self.progress.hide()

    def open_params(self):
        self.controller.open_parameters_dialog()
        
    def _on_files_changed(self, paths):
        import os
        def to_pair(p): return (os.path.basename(os.path.dirname(p)), p)
        self.docs = [to_pair(p) for p in paths]
        has_docs = bool(self.docs)
        self.btn_auto.setEnabled(has_docs)
        self.btn_params.setEnabled(has_docs)
