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
    
    BUTTON_FILES = """
        QPushButton {
            background-color: #76749C;
            color: white;
            font-family: 'Segoe UI Semibold';
            font-size: 10pt;
            border-radius: 8px;
            padding: 8px 8px;
            margin-bottom: 10px;
            
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
        
    Q_LINE = """
            QLineEdit {
                background-color: #f9f9f9;     
                border: 2px solid #cccccc;     
                border-radius: 8px;            
                padding: 6px 10px;            
                font-size: 14px;              
                color: #333333;              
            }



            QLineEdit::placeholder {
                color: #999999;             
            }
            """
    
    DIALOG_NAME_MODEL = """ 
    
        QInputDialog {
            background-color: #21252b;
            color: white;
            font-family: 'Segoe UI Semibold';
            font-size: 14pt;
        }

        QLabel {
            color: white;
            font-size: 14pt;
            font-family: 'Segoe UI Semibold';
        }

        QLineEdit {
            background-color: #21252b;
            color: white;
            border-style: none;
            border-bottom: 2px solid rgb(44, 49, 60);
            padding: 4px;
            font-family: 'Segoe UI Semibold';
            font-size: 14pt;
        }

        QPushButton {
            background-color: #2b2f36;
            color: white;
            border: 1px solid rgb(44, 49, 60);
            border-radius: 4px;
            padding: 6px 12px;
            font-family: 'Segoe UI Semibold';
            font-size: 12pt;
        }

        QPushButton:hover {
            background-color: #3a3f47;
            border: 1px solid #0078d7;
        }

        QPushButton:pressed {
            background-color: #0078d7;
        } 
    """ 
    

    LABEL = """
        QLabel {
            color: white;
            font-size: 12pt;
        }
    """
    
    COMBO_BOX = """ 
    
    QComboBox {
        background-color: #21252b;
        color: white;
        border: none;
        border-bottom: 2px solid rgb(44, 49, 60);
        padding: 6px 8px;
        font-family: 'Segoe UI Semibold';
        font-size: 13pt;
        selection-background-color: #0078d7;
    }

    QComboBox:focus {
        border-bottom: 2px solid #0078d7;
    }

    /* Flecha desplegable */
    QComboBox::drop-down {
        border: none;
        width: 25px;
        background-color: #2b2f36;
    }

 
    QComboBox::down-arrow {
        image: url(:/qt-project.org/styles/commonstyle/images/arrowdown-16.png);
        width: 12px;
        height: 12px;
    }


    QComboBox QAbstractItemView {
        background-color: #2b2f36;
        color: white;
        selection-background-color: #0078d7;
        selection-color: white;
        border: 1px solid rgb(44, 49, 60);
        outline: 0;
    } """ 
    
    DIALOG_RESULTS = """
            QDialog {
                background-color: #21252b;
                color: white;
                font-family: 'Segoe UI Semibold';
                font-size: 12pt;
            }

            QLabel {
                color: white;
                font-size: 13pt;
                font-family: 'Segoe UI Semibold';
            }

            QPushButton {
                background-color: #2b2f36;
                color: white;
                border: 1px solid rgb(44, 49, 60);
                border-radius: 6px;
                padding: 6px 12px;
                font-family: 'Segoe UI Semibold';
                font-size: 11pt;
            }

            QPushButton:hover {
                background-color: #3a3f47;
                border: 1px solid #0078d7;
            }

            QPushButton:pressed {
                background-color: #0078d7;
            }

            QTableWidget {
                background-color: #2b2f36;
                gridline-color: #444;
                color: white;
                border: 1px solid rgb(44, 49, 60);
                selection-background-color: #0078d7;
                selection-color: white;
                alternate-background-color: #252931;
            }

            QHeaderView::section {
                background-color: #1f2329;
                color: white;
                font-weight: bold;
                border: 1px solid #3a3f47;
                padding: 6px;
            }

            QScrollBar:vertical {
                background: #2b2f36;
                width: 10px;
                margin: 0px;
            }

            QScrollBar::handle:vertical {
                background: #444;
                border-radius: 4px;
                min-height: 20px;
            }

            QScrollBar::handle:vertical:hover {
                background: #0078d7;
            }

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """
    



        