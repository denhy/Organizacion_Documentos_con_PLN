
import os
from pathlib import Path
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QFileDialog, QLabel, QMenu, QPushButton
)
from PyQt5.QtGui import QPixmap, QIcon, QFont, QCursor
from app.utils.styles import Styles

class DocumentListWidget(QWidget):
    filesChanged = pyqtSignal(list)  # rutas absolutas

    def __init__(self, parent=None):
        super().__init__(parent)

        self._assets = Path(__file__).resolve().parents[2] / "data" / "assets" / "icons"
        self._icon_pdf = self._assets / "archivo-pdf.png"
        self._icon_doc = self._assets / "word.png"
        self._icon_img = self._assets / "image.png"
        self._icon_file = self._assets / "file.png"
        self._icon_upload = self._assets / "subir-archivo.png"

        root = QVBoxLayout(self)
        root.setContentsMargins(5, 5, 5, 0)
        root.setSpacing(6)

        # ---- barra de acciones ----
        actions = QHBoxLayout()
        self.btn_add_files = QPushButton("Agregar archivos")
        self.btn_add_folder = QPushButton("Agregar carpeta")
        for b in (self.btn_add_files, self.btn_add_folder):
            b.setStyleSheet(Styles.BUTTON_VIEWS)
            b.setFixedHeight(34)
        self.btn_add_files.clicked.connect(self._add_files_dialog)
        self.btn_add_folder.clicked.connect(self._add_folder_dialog)
        actions.addWidget(self.btn_add_files)
        actions.addWidget(self.btn_add_folder)
        actions.addStretch(1)
        root.addLayout(actions)

        # ---- lista ----
        self.list_docs = QListWidget()
        self.list_docs.setStyleSheet(Styles.LIST)
        self.list_docs.setFixedSize(700, 300)
        self.list_docs.setAcceptDrops(True)
        self.list_docs.setDragDropMode(QListWidget.DropOnly)
        self.list_docs.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_docs.customContextMenuRequested.connect(self._context_menu)
        root.addWidget(self.list_docs)

        # ---- placeholder overlay ----
        self.placeholder = QWidget(self.list_docs)
        # ¡que no bloquee el mouse!
        self.placeholder.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        phl = QVBoxLayout(self.placeholder); phl.setAlignment(Qt.AlignCenter)
        img_label = QLabel()
        px = QPixmap(str(self._icon_upload))
        if not px.isNull():
            img_label.setPixmap(px.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        phl.addWidget(img_label, alignment=Qt.AlignCenter)
        text_label = QLabel("Arrastra archivos/carpeta o haz doble clic para agregar")
        text_label.setFont(QFont("Segoe UI", 12)); text_label.setStyleSheet("color:#aaa;")
        text_label.setAlignment(Qt.AlignCenter)
        phl.addWidget(text_label, alignment=Qt.AlignCenter)
        self._resize_placeholder()
        self.placeholder.show()

        # eventos lista
        self.list_docs.model().rowsInserted.connect(self._on_rows_changed)
        self.list_docs.model().rowsRemoved.connect(self._on_rows_changed)
        self.list_docs.resizeEvent = self._list_resize_event
        self.list_docs.mouseDoubleClickEvent = self._list_double_click_event
        self.list_docs.dragEnterEvent = self._list_drag_enter
        self.list_docs.dropEvent = self._list_drop

        # recordar última carpeta usada
        self._last_dir = str(Path.home())

    # -------- API pública --------
    def get_file_paths(self):
        paths = []
        for i in range(self.list_docs.count()):
            item = self.list_docs.item(i)
            p = item.data(Qt.UserRole)
            if p:
                paths.append(p)
        return paths

    def clear(self):
        self.list_docs.clear()
        self._update_placeholder()
        self.filesChanged.emit([])

    # -------- helpers internos --------
    def _context_menu(self, pos):
        menu = QMenu(self)
        act_add_files = menu.addAction("Agregar archivos…")
        act_add_folder = menu.addAction("Agregar carpeta…")
        menu.addSeparator()
        act_remove_sel = menu.addAction("Quitar seleccionados")
        act_clear = menu.addAction("Vaciar lista")
        action = menu.exec_(self.mapToGlobal(pos))
        if action == act_add_files:
            self._add_files_dialog()
        elif action == act_add_folder:
            self._add_folder_dialog()
        elif action == act_remove_sel:
            for item in self.list_docs.selectedItems():
                self.list_docs.takeItem(self.list_docs.row(item))
        elif action == act_clear:
            self.clear()

    def _add_files_dialog(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Selecciona documentos",
            self._last_dir,
            "PDF (*.pdf);;Word (*.doc *.docx);;Imágenes (*.jpg *.jpeg *.png);;Todos (*.*)"
        )
        if files:
            self._last_dir = str(Path(files[0]).parent)
            self.add_paths(files)

    def _add_folder_dialog(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecciona carpeta", self._last_dir)
        if folder:
            self._last_dir = folder
            files = self._walk_dir_for_files(folder)
            self.add_paths(files)

    def _walk_dir_for_files(self, folder):
        exts = {".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png"}
        found = []
        for root, _, files in os.walk(folder):
            for f in files:
                if Path(f).suffix.lower() in exts:
                    found.append(str(Path(root) / f))
        return found

    def add_paths(self, paths):
        """Agrega múltiples rutas, evitando duplicados."""
        existing = set(self.get_file_paths())
        added = 0
        for p in paths:
            p = str(Path(p).resolve())
            if p in existing or not os.path.isfile(p):
                continue
            self._add_file_item(p)
            existing.add(p)
            added += 1
        if added:
            self.filesChanged.emit(self.get_file_paths())

    def _add_file_item(self, file_path):
        ext = Path(file_path).suffix.lower()
        if ext == ".pdf":
            icon_path = self._icon_pdf
        elif ext in (".doc", ".docx"):
            icon_path = self._icon_doc
        elif ext in (".jpg", ".jpeg", ".png"):
            icon_path = self._icon_img
        else:
            icon_path = self._icon_file

        item = QListWidgetItem(QIcon(str(icon_path)), Path(file_path).name)
        item.setData(Qt.UserRole, file_path)
        item.setToolTip(file_path)
        self.list_docs.addItem(item)

    # -------- eventos lista --------
    def _on_rows_changed(self, *args, **kwargs):
        self._update_placeholder()
        # no emitimos aquí; ya lo hace add_paths/remove/clear

    def _update_placeholder(self):
        self.placeholder.setVisible(self.list_docs.count() == 0)

    def _resize_placeholder(self):
        s = self.list_docs.size(); m = 15
        self.placeholder.setGeometry(m, m, s.width() - 2*m, s.height() - 3*m)

    def _list_resize_event(self, event):
        self._resize_placeholder()
        super(QListWidget, self.list_docs).resizeEvent(event)

    def _list_drag_enter(self, event):
        md = event.mimeData()
        if md.hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def _list_drop(self, event):
        paths = []
        for url in event.mimeData().urls():
            p = Path(url.toLocalFile())
            if p.is_dir():
                paths.extend(self._walk_dir_for_files(str(p)))
            elif p.is_file():
                paths.append(str(p))
        if paths:
            self.add_paths(paths)
        event.acceptProposedAction()

    def _list_double_click_event(self, event):
        # siempre permite agregar más (aunque ya haya elementos)
        self._add_files_dialog()