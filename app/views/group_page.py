from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, 
    QListWidget, QProgressBar
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer, Qt
from utils.styles import Styles
from views.listDocumentWidget import DocumentListWidget


class GroupPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.docs = []
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        layout.setContentsMargins(50, 50, 50, 50)  
        layout.setSpacing(25) 

        self.lbl = QLabel("Agrupamiento de documentos")
        self.lbl.setStyleSheet(Styles.TITLES)
        layout.addWidget(self.lbl)

        # Lista de documentos
        self.list_docs = DocumentListWidget()  
        layout.addWidget(self.list_docs)

        # Botones de opciones
        self.btn_auto = QPushButton("Agrupar automáticamente")
        self.btn_auto.clicked.connect(self.group_documents)

        self.btn_params = QPushButton("Visualizar hiperparámetros")
        self.btn_params.clicked.connect(self.open_params) 
        
        for btn in [self.btn_auto, self.btn_params]:
            btn.setStyleSheet(Styles.BUTTON_VIEWS)
            btn.setEnabled(False)
            btn.setFixedSize(280, 50)
            layout.addWidget(btn, alignment=Qt.AlignCenter)
      

        # Barra de progreso
        self.progress = QProgressBar()
        self.progress.hide()
        layout.addWidget(self.progress)

        layout.addStretch()

    def upload_docs(self):
        files, _ = self.controller.get_files_dialog()
        if files:
            self.docs = files
            self.list_docs.addItems(files)
            self.btn_auto.setEnabled(True)
            self.btn_params.setEnabled(True)

    def group_documents(self):
        self.controller.process_documents(self.docs)

    def update_progress(self, value):
        self.progress.show()
        self.progress.setValue(value)
        if value >= 100:
            self.lbl.setText("✅ Documentos agrupados con éxito")

    def open_params(self):
        self.controller.open_parameters_dialog()