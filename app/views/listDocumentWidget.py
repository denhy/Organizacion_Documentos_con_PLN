
import os
from pathlib import Path
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QFileDialog, QLabel
from PyQt5.QtGui import QPixmap, QIcon, QFont
from app.utils.styles import Styles

class DocumentListWidget(QWidget):


    filesChanged = pyqtSignal(list)  # lista de rutas absolutas

    def __init__(self, parent=None):
        super().__init__(parent)

        # --- rutas a íconos (usa rutas relativas robustas) ---
        self._assets = Path(__file__).resolve().parents[2] / "data" / "assets" / "icons"
        self._icon_pdf = self._assets / "archivo-pdf.png"
        self._icon_doc = self._assets / "word.png"
        self._icon_img = self._assets / "image.png"
        self._icon_file = self._assets / "file.png"
        self._icon_upload = self._assets / "subir-archivo.png"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 0, 0)

        # ---------- LISTA PRINCIPAL ----------
        self.list_docs = QListWidget()
        self.list_docs.setStyleSheet(Styles.LIST)
        self.list_docs.setFixedSize(700, 300)

        # Importante: el DnD debe manejarlo el propio widget que recibe el drop
        self.list_docs.setAcceptDrops(True)
        self.list_docs.setDragDropMode(QListWidget.DropOnly)

        layout.addWidget(self.list_docs)

        # ---------- PLACEHOLDER (overlay) ----------
        self.placeholder = QWidget(self.list_docs)
        # Que el placeholder NO bloquee los clicks del usuario
        self.placeholder.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.placeholder.setStyleSheet("QWidget { color: white; }")

        placeholder_layout = QVBoxLayout(self.placeholder)
        placeholder_layout.setAlignment(Qt.AlignCenter)

        img_label = QLabel()
        up_px = QPixmap(str(self._icon_upload))
        if not up_px.isNull():
            img_label.setPixmap(up_px.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        placeholder_layout.addWidget(img_label, alignment=Qt.AlignCenter)

        text_label = QLabel("Arrastra o haz doble clic para subir documentos")
        text_label.setFont(QFont("Segoe UI", 12))
        text_label.setStyleSheet("color: #aaa;")
        text_label.setAlignment(Qt.AlignCenter)
        placeholder_layout.addWidget(text_label, alignment=Qt.AlignCenter)

        self.placeholder.show()

        # ---------- CONEXIONES ----------
        # Cuando la lista cambie (agreguen/quiten filas), actualizamos placeholder y emitimos filesChanged
        self.list_docs.model().rowsInserted.connect(self._on_rows_changed)
        self.list_docs.model().rowsRemoved.connect(self._on_rows_changed)

        # Doble clic en área vacía -> abrir diálogo
        self.list_docs.mouseDoubleClickEvent = self._list_double_click_event

        # Drag & drop: sobreescribimos en el widget list_docs
        self.list_docs.dragEnterEvent = self._list_drag_enter
        self.list_docs.dropEvent = self._list_drop

        # Ajustar overlay al tamaño de la lista
        self.list_docs.resizeEvent = self._list_resize_event
        self._resize_placeholder()

    # -------------------- API PÚBLICA --------------------
    def get_file_paths(self):
        """Devuelve las rutas absolutas de los ítems en la lista."""
        paths = []
        for i in range(self.list_docs.count()):
            item = self.list_docs.item(i)
            # Guardamos la ruta en el DataRole de Qt
            p = item.data(Qt.UserRole)
            if p:
                paths.append(p)
        return paths

    def clear(self):
        self.list_docs.clear()
        self._update_placeholder()
        self.filesChanged.emit([])

    def add_file_item(self, file_path: str):
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            icon_path = self._icon_pdf
        elif ext in (".doc", ".docx"):
            icon_path = self._icon_doc
        elif ext in (".jpg", ".jpeg", ".png"):
            icon_path = self._icon_img
        else:
            icon_path = self._icon_file

        icon = QIcon(str(icon_path))
        item = QListWidgetItem(icon, os.path.basename(file_path))
        # Guardamos ruta completa en UserRole y además en tooltip
        item.setData(Qt.UserRole, file_path)
        item.setToolTip(file_path)
        self.list_docs.addItem(item)

    # -------------------- Internos / eventos --------------------
    def _on_rows_changed(self, *args, **kwargs):
        self._update_placeholder()
        self.filesChanged.emit(self.get_file_paths())

    def _update_placeholder(self):
        self.placeholder.setVisible(self.list_docs.count() == 0)

    def _resize_placeholder(self):
        list_size = self.list_docs.size()
        margin = 15
        new_width = list_size.width() - (2 * margin)
        new_height = list_size.height() - (3 * margin)
        new_x = margin
        new_y = margin
        self.placeholder.setGeometry(new_x, new_y, new_width, new_height)

    # Eventos en la lista (no en el contenedor)
    def _list_resize_event(self, event):
        self._resize_placeholder()
        super(QListWidget, self.list_docs).resizeEvent(event)

    def _list_drag_enter(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def _list_drop(self, event):
        urls = event.mimeData().urls()
        for u in urls:
            p = u.toLocalFile()
            if os.path.isfile(p):
                self.add_file_item(p)
        event.acceptProposedAction()

    def _list_double_click_event(self, event):
        # Si está vacío (placeholder visible), abrir diálogo
        if self.list_docs.count() == 0:
            files, _ = QFileDialog.getOpenFileNames(
                self, "Seleccionar documentos", "", "PDF (*.pdf);;Todos los archivos (*.*)"
            )
            for f in files:
                self.add_file_item(f)
        # Llamar al handler original por si el usuario hace doble clic en un item
        super(QListWidget, self.list_docs).mouseDoubleClickEvent(event)
