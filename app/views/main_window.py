from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, 
    QLabel, QFrame, QStackedWidget, QApplication
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon
from app.utils.styles import Styles

class MainWindow(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setup_ui()
        
    def setup_ui(self):
       
        self.setStyleSheet("background-color: #282c34;")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.resize(1000, 600)
        self.center_window()

# ----------------- LAYOUT PRINCIPAL --------------------
        main_layout = QVBoxLayout(self) 
        content_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)  
        main_layout.setSpacing(0)             
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        
# -------------------------- BARRA SUPERIOR ---------------------
        title_bar = QWidget(self)
        title_bar.setFixedHeight(50)
        title_bar.setStyleSheet(Styles.TITLE_BAR)

        # Botones derecha 
        icon_exit = QIcon(r"D:\Documentos\TRABAJOS_YO\UAEH\Proyecto Doctora Rosa\INTERFAZ_v1\data\assets\icons\cil-x.png")
        icon_minimize= QIcon(r"D:\Documentos\TRABAJOS_YO\UAEH\Proyecto Doctora Rosa\INTERFAZ_v1\data\assets\icons\icon_minimize.png")
        icon_maximize = QIcon(r"D:\Documentos\TRABAJOS_YO\UAEH\Proyecto Doctora Rosa\INTERFAZ_v1\data\assets\icons\icon_maximize.png")
       
       
        self.btn_close = QPushButton()
        self.btn_close.setIcon(icon_exit)
        self.btn_close.clicked.connect(self.close)
        
        self.btn_min = QPushButton()
        self.btn_min.setIcon(icon_minimize)
        self.btn_min.clicked.connect(self.showMinimized)
         
        self.btn_max = QPushButton()
        self.btn_max.setIcon(icon_maximize)
        self.btn_max.clicked.connect(self.toggle_max_restore)

        # Aplicar estilo a los botones de control
    
        self.btn_close.setStyleSheet(Styles.CONTROL_BUTTON)
        self.btn_min.setStyleSheet(Styles.CONTROL_BUTTON)
        self.btn_max.setStyleSheet(Styles.CONTROL_BUTTON)

        # Layout de la barra
        h_layout = QHBoxLayout(title_bar)  
        h_layout.setContentsMargins(10, 0, 10, 0)
        h_layout.setSpacing(15)

        # Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap(r"data\assets\logo\logo.png")  # ruta relativa
        logo_pixmap = logo_pixmap.scaled(45, 45, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("background-color: transparent;")
        h_layout.addWidget(logo_label)

        # Título
        title = QLabel("Organizador ML")
       
        title.setAlignment(Qt.AlignVCenter)
        title.setStyleSheet(Styles.TITLE_BAR)
        h_layout.addWidget(title)

       
        h_layout.addStretch()

        # Botones de control
        h_layout.addWidget(self.btn_min)
        h_layout.addWidget(self.btn_max)
        h_layout.addWidget(self.btn_close)

        main_layout.addWidget(title_bar)

# --------------------- PANEL LATERAL ----------------
        sidebar = QFrame()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("background-color: #76749c; color: white;")
        sidebar_layout = QVBoxLayout(sidebar)
        
        # Botones menú
        
        font_menu = QFont("Segoe UI Semibold", 18, QFont.Bold)
        

        icon_btnAgrupar = QIcon(r"data\assets\icons\icon_group.png")
        icon_btnClasificar = QIcon(r"data\assets\icons\icon_classify.png")
        icon_btnHome = QIcon(r"data\assets\icons\hogar.png")
        icon_btnVer = QIcon(r"data\assets\icons\ver.png")
        
        self.btn_home = QPushButton("Home")
        self.btn_home.setIcon(icon_btnHome)
         
        self.btn_group = QPushButton("Agrupar")
        self.btn_group.setIcon(icon_btnAgrupar)    
        
        self.btn_classify = QPushButton("Clasificar")
        self.btn_classify.setIcon(icon_btnClasificar)
       
        self.btn_train = QPushButton("Entrenar Modelo")
        #self.btn_train.setIcon(icon_btnClasificar)
        
        self.btn_models_overview = QPushButton("Ver modelos")
        self.btn_models_overview.setIcon(icon_btnVer)
       

        for btn in [self.btn_home, self.btn_group, self.btn_classify, self.btn_train, self.btn_models_overview]:
            btn.setStyleSheet(Styles.BUTTON_HOME)
            btn.setIconSize(Styles.ICON_MEDIUM_SIZE)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()
        sidebar_layout.addWidget(QLabel("⚙️ Configuración", alignment=Qt.AlignCenter))

        # --- Área central con páginas ---
        self.stack = QStackedWidget()  
        content_layout.addWidget(sidebar)
        content_layout.addWidget(self.stack) 
        main_layout.addLayout(content_layout)

    # ----------------------- FUNCIONES -------------------------
    
    def center_window(self):
        frame_gm = self.frameGeometry()  # geometría de la ventana
        screen = QApplication.primaryScreen().availableGeometry().center()  # centro de la pantalla
        frame_gm.moveCenter(screen)      # movemos la ventana al centro
        self.move(frame_gm.topLeft())  
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.pos().y() <= 40:  # dentro de la barra
            self.dragPos = event.globalPos()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self, 'dragPos'):
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()
    
    def add_page(self, widget, index):
        self.stack.insertWidget(index, widget)

    def set_current_page(self, index):
        self.stack.setCurrentIndex(index)
        
    def toggle_max_restore(self):
        if self.is_maximized:
            self.showNormal()
            self.is_maximized = False
        else:
            self.showMaximized()
            self.is_maximized = True