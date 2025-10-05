from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, 
    QListWidget, QProgressBar
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer, Qt
from app.utils.styles import Styles
from app.views.listDocumentWidget import DocumentListWidget


class TrainModel(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.docs = []
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        layout.setContentsMargins(50, 50, 50, 50)  
        layout.setSpacing(25) 

        self.lbl = QLabel("Entrena un modelo")
        self.lbl.setStyleSheet(Styles.TITLES)
        layout.addWidget(self.lbl)

        # Lista de documentos
        self.list_docs = DocumentListWidget()  
        layout.addWidget(self.list_docs)

        # Botones de opciones
        self.btn_train = QPushButton("Entrenar Modelo")
        self.btn_train.clicked.connect(self.train_documents)
        self.btn_train.setStyleSheet(Styles.BUTTON_VIEWS)
        self.btn_train.setEnabled(False)
        self.btn_train.setFixedSize(280, 50)
        layout.addWidget(self.btn_train, alignment=Qt.AlignCenter)



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

    def train_documents(self):
        self.controller.process_documents(self.docs)

    def update_progress(self, value):
        self.progress.show()
        self.progress.setValue(value)
        if value >= 100:
            self.lbl.setText("✅ Documentos agrupados con éxito")

    def open_params(self):
        self.controller.open_parameters_dialog()