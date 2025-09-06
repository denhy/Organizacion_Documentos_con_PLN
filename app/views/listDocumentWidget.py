from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QLabel, QFileDialog, QListWidgetItem
)
from PyQt5.QtGui import QPixmap, QFont, QIcon, QBrush
from PyQt5.QtCore import Qt
import os
from utils.styles import Styles


class DocumentListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 0, 0)

        # ---------- LISTA PRINCIPAL ----------
        self.list_docs = QListWidget()
        self.list_docs.setStyleSheet(Styles.LIST)
        self.list_docs.setFixedSize(700, 300)
        self.list_docs.setAcceptDrops(True)
        self.list_docs.setDragDropMode(QListWidget.DropOnly)

        layout.addWidget(self.list_docs)

        # ---------- PLACEHOLDER ----------
        self.placeholder = QWidget(self.list_docs)
        self.placeholder.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.placeholder.setStyleSheet("""
                                       QWidget {
                                           color:white;
                                           }""")

        placeholder_layout = QVBoxLayout(self.placeholder)
        placeholder_layout.setAlignment(Qt.AlignCenter)

        img_label = QLabel()
        pixmap = QPixmap(r"..\data\assets\icons\subir-archivo.png")
        if not pixmap.isNull():
            img_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        placeholder_layout.addWidget(img_label, alignment=Qt.AlignCenter)

        text_label = QLabel("Arrastra o haz clic para subir documentos")
        text_label.setFont(QFont("Segoe UI", 12))
        text_label.setStyleSheet("color: #aaa;")
        text_label.setAlignment(Qt.AlignCenter)
        placeholder_layout.addWidget(text_label, alignment=Qt.AlignCenter)

        self.placeholder.show()

        # Conectar señales
        self.list_docs.model().rowsInserted.connect(self.update_placeholder)
        self.list_docs.model().rowsRemoved.connect(self.update_placeholder)

    # -------------------- DRAG & DROP --------------------
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.isfile(file_path):
                self.add_file_item(file_path)

    # -------------------- CLICK PARA ABRIR --------------------
    def mouseDoubleClickEvent(self, event):
        if self.placeholder.isVisible():
            files, _ = QFileDialog.getOpenFileNames(
                self, "Seleccionar documentos", "", "Todos los archivos (*.*)"
            )
            for f in files:
                
                self.add_file_item(f)
                
        super().mousePressEvent(event)

    # -------------------- AGREGAR ARCHIVO CON ÍCONO --------------------
    def add_file_item(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()

        if ext in [".pdf"]:
            icon_path = r"..\data\assets\icons\archivo-pdf.png"
        elif ext in [".doc", ".docx"]:
            icon_path = r"data\assets\icons\word.png"
        elif ext in [".jpg", ".jpeg", ".png"]:
            icon_path = r"data\assets\icons\image.png"
        else:
            icon_path = r"data\assets\icons\file.png"
        
        
        item = QListWidgetItem(QIcon(icon_path), os.path.basename(file_path))
       
        item.setToolTip(file_path) 
        self.list_docs.addItem(item)

    # -------------------- PLACEHOLDER --------------------
    def resizeEvent(self, event):
        list_size = self.list_docs.size()
        margin = 15
        new_width = list_size.width() - (2 * margin)
        new_height = list_size.height() - (3 * margin)
        new_x = margin
        new_y = margin
        self.placeholder.setGeometry(new_x, new_y, new_width, new_height)

        super().resizeEvent(event)

    def update_placeholder(self):
        if self.list_docs.count() > 0:
            self.placeholder.hide()
        else:
            self.placeholder.show()
