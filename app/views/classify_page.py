from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QProgressBar
from PyQt5.QtGui import QFont 
from utils.styles import Styles
from PyQt5.QtCore import Qt
from views.listDocumentWidget import DocumentListWidget

class ClassifyPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)  
        layout.setSpacing(25) 

        lbl = QLabel("Clasificación de documentos")
        lbl.setStyleSheet(Styles.TITLES)
        layout.addWidget(lbl)

        # Lista de documentos
        self.list_docs = DocumentListWidget()  
        layout.addWidget(self.list_docs)
        
        # Botones de opciones
        
        btn_auto = QPushButton("Clasificar automáticamente")
        btn_manual = QPushButton("Decidir carpeta manualmente")

        for btn in [btn_auto, btn_manual]:
            btn.setStyleSheet(Styles.BUTTON_VIEWS)
            btn.setEnabled(False)
            btn.setFixedSize(280, 50)
            layout.addWidget(btn, alignment=Qt.AlignCenter)
        
       
        # Conectar a controlador
        btn_auto.clicked.connect(self.controller.auto_classify)
        btn_manual.clicked.connect(self.controller.manual_classify)

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
       
        

  