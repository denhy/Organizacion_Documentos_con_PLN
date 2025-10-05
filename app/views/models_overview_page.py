# views/models_overview_page.py
from pathlib import Path
import json
from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QAbstractItemView,
    QFileDialog, QMessageBox
)

from app.utils.styles import Styles
from app.views.models_report_dialog import ModelReportDialog


class ModelResultsPage(QWidget):
 
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller  
        self._rows_model_dir = {}     
        self._setup_ui()
        
        self._load_models()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(16)

        title = QLabel("Modelos entrenados")
        title.setStyleSheet(Styles.TITLES)
        layout.addWidget(title)

        # Barra de acciones
        actions = QHBoxLayout()
        self.btn_refresh = QPushButton("Actualizar")
        self.btn_open_dir = QPushButton("Abrir carpeta del modelo…")
        self.btn_export = QPushButton("Exportar tabla a CSV…")

        for b in (self.btn_refresh, self.btn_open_dir, self.btn_export):
            b.setStyleSheet(Styles.BUTTON_VIEWS)
            b.setFixedHeight(36)

        self.btn_refresh.clicked.connect(self._load_models)
        self.btn_open_dir.clicked.connect(self._open_selected_dir)
        self.btn_export.clicked.connect(self._export_csv)

        actions.addWidget(self.btn_refresh)
        actions.addWidget(self.btn_open_dir)
        actions.addWidget(self.btn_export)
        actions.addStretch(1)
        layout.addLayout(actions)

        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.setStyleSheet(Styles.DIALOG_RESULTS)
        self.table.setHorizontalHeaderLabels([
            "modelo", "num_docs", "num_clases", "clases", "accuracy", "actualizado", "ruta"
        ])
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setSortingEnabled(True)
        self.table.doubleClicked.connect(self._open_report_dialog)
        layout.addWidget(self.table)

        layout.addStretch()

    # ---------- Helpers ----------
    def _models_base_dir(self) -> Path:
        # views/models_overview_page.py -> subir dos niveles: app/ -> data/models
        return Path(__file__).resolve().parents[2] / "data" / "models"

    def _load_models(self):
        base = self._models_base_dir()
        self.table.setRowCount(0)
        self._rows_model_dir.clear()

        if not base.exists():
            QMessageBox.information(self, "Sin modelos", f"No existe la carpeta:\n{str(base)}")
            return

        rows = []
        for d in sorted(p for p in base.iterdir() if p.is_dir()):
            md_path = d / "metadata.json"
            if not md_path.exists():
                continue
            try:
                data = json.loads(md_path.read_text(encoding="utf-8"))
            except Exception as e:
                print(f"⚠️ Error leyendo {md_path}: {e}")
                continue

            model_name = d.name
            num_docs = data.get("num_docs", "")
            classes = data.get("classes", [])
            n_classes = len(classes)
            classes_str = ", ".join(map(str, classes)) if classes else ""
            acc = data.get("metrics", {}).get("accuracy", None)
            acc_str = "" if acc is None else f"{float(acc):.4f}"
            mtime = datetime.fromtimestamp(md_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            rows.append((model_name, num_docs, n_classes, classes_str, acc_str, mtime, str(d)))

        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                # alinear números a la derecha
                if c in (1, 2) or (c == 4 and row[4] != ""):
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(r, c, item)
            # mapear fila -> ruta
            self._rows_model_dir[r] = Path(row[6])

        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)

    def _selected_model_dir(self) -> Path:
        sel = self.table.selectionModel().selectedRows()
        if not sel:
            return None
        row = sel[0].row()
        return self._rows_model_dir.get(row, None)

    def _open_selected_dir(self):
        model_dir = self._selected_model_dir()
        if not model_dir:
            QMessageBox.information(self, "Selecciona un modelo", "Elige una fila primero.")
            return
        # Solo mostramos un file dialog apuntando a la carpeta (para evitar dependencias de OS)
        QFileDialog.getOpenFileName(self, "Carpeta del modelo", str(model_dir))

    def _export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Exportar tabla a CSV", "model_registry.csv", "CSV (*.csv)")
        if not path:
            return
        try:
            import csv
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                headers = ["modelo", "num_docs", "#clases", "clases", "accuracy", "actualizado", "ruta"]
                w.writerow(headers)
                for r in range(self.table.rowCount()):
                    row = [self.table.item(r, c).text() if self.table.item(r, c) else "" for c in range(self.table.columnCount())]
                    w.writerow(row)
            QMessageBox.information(self, "Exportado", f"Tabla guardada en:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo exportar:\n{e}")

    def _open_report_dialog(self):
        """Doble clic: abre el diálogo con el classification_report del modelo."""
        model_dir = self._selected_model_dir()
        if not model_dir:
            return
        md_path = model_dir / "metadata.json"
        try:
            data = json.loads(md_path.read_text(encoding="utf-8"))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo leer metadata.json:\n{e}")
            return

        model_name = model_dir.name
        report = data.get("metrics", {}).get("report", "")
        classes = data.get("classes", [])
        acc = data.get("metrics", {}).get("accuracy", None)

        dlg = ModelReportDialog(
            model_name=model_name,
            report_text=report,
            classes=classes,
            accuracy=acc,
            parent=self
        )
        dlg.exec_()
