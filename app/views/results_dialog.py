
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QAbstractItemView, QFileDialog, QMessageBox
)
from app.utils.styles import Styles
import csv
from typing import List, Dict, Any

class ResultsDialog(QDialog):
  
    def __init__(self, results: List[Dict[str, Any]], parent=None, title="Resultados de clasificación"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(900, 500)
        self.setStyleSheet(Styles.DIALOG_RESULTS)
        self.results = results
        

        layout = QVBoxLayout(self)

        header = QHBoxLayout()
        header.addWidget(QLabel(f"{len(results)} documentos clasificados"))
        header.addStretch()
        self.btn_export = QPushButton("Exportar CSV")
        self.btn_export.clicked.connect(self._export_csv)
        header.addWidget(self.btn_export)
        layout.addLayout(header)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["file_path", "predicted_label", "confidence"])
        self.table.setSortingEnabled(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._fill_table(results)
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        buttons = QHBoxLayout()
        buttons.addStretch()
        btn_close = QPushButton("Cerrar")
        btn_close.clicked.connect(self.accept)
        buttons.addWidget(btn_close)
        layout.addLayout(buttons)

        # Habilitar copiar al portapapeles con Ctrl+C
        self.table.keyPressEvent = self._key_press_with_copy(self.table.keyPressEvent)

    def _fill_table(self, rows: List[Dict[str, Any]]):
        self.table.setRowCount(len(rows))
        for r, obj in enumerate(rows):
            self.table.setItem(r, 0, QTableWidgetItem(str(obj.get("file_path", ""))))
            self.table.setItem(r, 1, QTableWidgetItem(str(obj.get("predicted_label", ""))))
            conf = obj.get("confidence", None)
            self.table.setItem(r, 2, QTableWidgetItem("" if conf is None else f"{conf:.4f}"))

    def _export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Guardar CSV", "predictions.csv", "CSV (*.csv)")
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=["file_path", "predicted_label", "confidence"])
                w.writeheader()
                for row in self.results:
                    w.writerow({
                        "file_path": row.get("file_path", ""),
                        "predicted_label": row.get("predicted_label", ""),
                        "confidence": row.get("confidence", "")
                    })
            QMessageBox.information(self, "Exportado", f"Resultados guardados en:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo exportar:\n{e}")

    def _key_press_with_copy(self, original_event):
        
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtGui import QKeySequence
        def handler(event):
            if event.matches(QKeySequence.Copy):
                sel = self.table.selectedIndexes()
                if sel:
                    rows = sorted(set(i.row() for i in sel))
                    cols = self.table.columnCount()
                    lines = []
                    header = [self.table.horizontalHeaderItem(c).text() for c in range(cols)]
                    lines.append("\t".join(header))
                    for r in rows:
                        vals = []
                        for c in range(cols):
                            it = self.table.item(r, c)
                            vals.append("" if it is None else it.text())
                        lines.append("\t".join(vals))
                    QApplication.clipboard().setText("\n".join(lines))
                    return
            return original_event(event)
        return handler
