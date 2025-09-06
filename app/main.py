import sys
from PyQt5.QtWidgets import (

QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, 
    QHBoxLayout, QStackedWidget, QFrame, QFileDialog, QProgressBar,
    QListWidget, QDialog, QSpinBox, QFormLayout
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt 

from views.main_window import MainWindow
from views.group_page import GroupPage
from views.classify_page import ClassifyPage
from views.train_model_page import TrainModel
from controllers.ml_controller import MLController

def main():
    app = QApplication(sys.argv)
    
    # Crear controlador primero
    ml_controller = MLController(None)
    
    # Crear ventana principal
    main_window = MainWindow(ml_controller)
    ml_controller.view = main_window  # Conectar vista al controlador
    
    # Crear páginas
    home_widget = QWidget()
    layout = QVBoxLayout(home_widget)
    layout.setAlignment(Qt.AlignCenter)

    # Logo
    logo_label = QLabel()
    logo_pixmap = QPixmap(r"D:\Documentos\TRABAJOS_YO\UAEH\Proyecto Doctora Rosa\INTERFAZ_v1\data\assets\view\logo_fondo.png")
    logo_pixmap = logo_pixmap.scaled(280, 280, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    logo_label.setPixmap(logo_pixmap)
    logo_label.setAlignment(Qt.AlignCenter)

    # Texto
    text_label = QLabel("Bienvenido 👋\nSelecciona una opción en el menú")
    text_label.setFont(QFont("Segoe UI Semibold", 14))
    text_label.setStyleSheet("color: white; background-color: transparent;")
    text_label.setAlignment(Qt.AlignCenter)

    layout.addWidget(logo_label)
    layout.addWidget(text_label)

    
    group_page = GroupPage(ml_controller)
    classify_page = ClassifyPage(ml_controller)
    train_page = TrainModel(ml_controller)
    
    # Agregar páginas al stack
    main_window.add_page(home_widget, 0)
    main_window.add_page(group_page, 1)
    main_window.add_page(classify_page, 2)
    main_window.add_page(train_page, 3)
    
    # Conectar botones del menú
    main_window.btn_home.clicked.connect(lambda: main_window.set_current_page(0))
    main_window.btn_group.clicked.connect(lambda: main_window.set_current_page(1))
    main_window.btn_classify.clicked.connect(lambda: main_window.set_current_page(2))
    main_window.btn_train.clicked.connect(lambda: main_window.set_current_page(3))
    
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()