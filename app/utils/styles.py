from PyQt5.QtCore import QSize

class Styles:
    
    # ----------------------------- MAIN WINDOW -----------------------
    
    #barra superior de controles
    
    TITLE_BAR =  """
            QWidget {
                background-color: #21252b; 
                color: white;
                border-style: none;
                border-bottom: 2px solid rgb(44, 49, 60);
                font-family: 'Segoe UI Semibold';
                font-size: 14pt;
                
            }
        """
        
    CONTROL_BUTTON = """
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-weight: bold;
                padding: 5px;
                min-width: 20px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 3px;
            }
        """
    
    # menu lateral
    
    ICON_MEDIUM_SIZE = QSize(32, 32)

    BUTTON_HOME = """
        QPushButton {
                    font-family: 'Segoe UI Semibold';
                    font-size: 14pt;
                    background-color: transparent;
                    border: none;
                    padding:10px;  
                    margin: 10px 0 20px 0;
                    color: white;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background-color: #B388FF;
                }
            
    """
    
    # --------------------- VISTAS SECUNDARIAS --------------
    
    TITLES = """
            QLabel{
                color: white;
                font-family: 'Segoe UI Semibold';
                font-size: 16pt;
            }
    """
    
    BUTTON_VIEWS = """
        QPushButton {
            background-color: #76749C;
            color: white;
            font-family: 'Segoe UI Semibold';
            font-size: 12pt;
            border-radius: 8px;
            padding: 8px 15px;
            
        }
        QPushButton:hover {
            background-color: #6272a4;
        }
        QPushButton:pressed {
            background-color: #44475a;
            border: 2px solid #bd93f9;
        }
    """
    
    LIST = """
            QListWidget {
            border: 2px dashed #434D66;
            border-radius: 10px;
            padding: 10px;
            background-color: transparent;
            margin-bottom: 20px;
            color:white;
            font-family: 'Segoe UI Semibold';
            font-size: 12pt;
            }
           
        """
    

    LABEL = """
        QLabel {
            color: white;
            font-size: 12pt;
        }
    """
    
    



        