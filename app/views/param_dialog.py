from PyQt5.QtWidgets import QDialog, QSpinBox, QPushButton, QFormLayout

class ParamsDialog(QDialog):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Hiperparámetros")
        layout = QFormLayout(self)

        self.spin_clusters = QSpinBox()
        self.spin_clusters.setRange(2, 20)
        self.spin_clusters.setValue(5)

        layout.addRow("Número de clusters:", self.spin_clusters)

        btn_apply = QPushButton("Aplicar")
        btn_apply.clicked.connect(self.apply_params)
        layout.addWidget(btn_apply)

    def apply_params(self):
        if self.controller:
            self.controller.set_parameters(self.spin_clusters.value())
        self.accept()