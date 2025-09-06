from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QTimer
from models.ml_processor import MLProcessor
from views.param_dialog import ParamsDialog

class MLController:
    def __init__(self, view):
        self.view = view
        self.ml_processor = MLProcessor()
        


    def process_documents(self, file_paths):
        # Simulación de proceso (aquí iría tu lógica real de ML)
        self.simulate_processing(file_paths)

    def simulate_processing(self, file_paths):
        timer = QTimer()
        progress = 0
        
        def update():
            nonlocal progress
            progress += 20
            if progress <= 100:
                # Actualizar vista a través del controlador
                current_page = self.view.stack.currentWidget()
                if hasattr(current_page, 'update_progress'):
                    current_page.update_progress(progress)
            else:
                timer.stop()
                
        timer.timeout.connect(update)
        timer.start(300)

    def open_parameters_dialog(self):
        dialog = ParamsDialog(self.view, self)
        dialog.exec_()

    def set_parameters(self, n_clusters):
        print(f"Parámetros establecidos: {n_clusters} clusters")
        # Aquí configurarías los parámetros en tu modelo ML

    def train_model(self):
        print("Iniciando entrenamiento del modelo...")

    def auto_classify(self):
        print("Clasificación automática...")

    def manual_classify(self):
        print("Clasificación manual...")