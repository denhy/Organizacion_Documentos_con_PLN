from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton, QHBoxLayout
from PyQt5.QtGui import QFont
from app.utils.styles import Styles

class ModelReportDialog(QDialog):
    
    def __init__(self, model_name: str, report_text: str, classes, accuracy, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Reporte del modelo: {model_name}")
        self.resize(800, 520)
        self.setStyleSheet(Styles.DIALOG_RESULTS)

        layout = QVBoxLayout(self)

        # Encabezado con clases y accuracy
        head = QLabel(self._header_text(classes, accuracy))
        head.setWordWrap(True)
        layout.addWidget(head)

        # Reporte monoespaciado
        self.txt = QTextEdit()
        self.txt.setReadOnly(True)
        mono = QFont("Consolas")
        mono.setStyleHint(QFont.Monospace)
        self.txt.setFont(mono)
        self.txt.setText(report_text or "(sin reporte)")
        layout.addWidget(self.txt)

        # Botonera
        row = QHBoxLayout()
        row.addStretch(1)
        btn_close = QPushButton("Cerrar")
        btn_close.clicked.connect(self.accept)
        row.addWidget(btn_close)
        layout.addLayout(row)

    def _header_text(self, classes, accuracy):
        classes_str = ", ".join(map(str, classes or []))
        acc_str = "" if accuracy is None else f"{float(accuracy):.4f}"
        return f"<b>Clases:</b> {classes_str}<br><b>Accuracy:</b> {acc_str}"
