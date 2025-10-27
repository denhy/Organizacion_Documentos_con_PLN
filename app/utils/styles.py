from PyQt5.QtCore import QSize

class Styles:

    TITLE_BAR = """
        QWidget {
            background-color: #0C1A1A; 
            color: #FFFFFF;
            border-style: none;
           
            font-family: 'Segoe UI Semibold';
            font-size: 14pt;
        }
    """

    CONTROL_BUTTON = """
        QPushButton {
            background-color: transparent;
            color: #FFFFFF;
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

    # --------------------- MENÚ LATERAL ---------------------

    ICON_MEDIUM_SIZE = QSize(32, 32)

    BUTTON_HOME = """
        QPushButton {
            font-family: 'Segoe UI Semibold';
            font-size: 14pt;
            background-color: transparent;
            border: none;
            padding: 10px;
            margin: 10px 0 20px 0;
            color: #FFFFFF;
            border-radius: 10px;
        }
        QPushButton:hover {
            background-color: rgba(255, 255, 255, 0.25);
        }
    """

    MENU_LATERAL = """
        QWidget {
            background-color: #6ACFC7;
            color: #FFFFFF;
            border: none;
        }
    """

    # --------------------- VISTAS SECUNDARIAS ---------------------

    TITLES = """
        QLabel {
            color: #6ACFC7;
            font-family: 'Segoe UI Semibold';
            font-size: 20pt;
            font-weight: bold;
        }
    """

    BUTTON_VIEWS = """
        QPushButton {
            background-color: #6ACFC7;
            color: #FFFFFF;
            font-family: 'Segoe UI Semibold';
            font-size: 12pt;
            border-radius: 8px;
            padding: 8px 15px;
            border: none;
        }
        QPushButton:hover {
            background-color: #58B8B0;
        }
        QPushButton:pressed {
            background-color: #4AA29B;
        }
    """

    BUTTON_FILES = """
        QPushButton {
            background-color: #6ACFC7;
            color: #FFFFFF;
            font-family: 'Segoe UI Semibold';
            font-size: 10pt;
            border-radius: 8px;
            padding: 8px 8px;
            margin-bottom: 10px;
            border: none;
        }
        QPushButton:hover {
            background-color: #58B8B0;
        }
        QPushButton:pressed {
            background-color: #4AA29B;
        }
    """

    LIST = """
        QListWidget {
            border: 2px dashed #9CA1A1;
            border-radius: 10px;
            padding: 10px;
            background-color: #FFFFFF;
            margin-bottom: 20px;
            color: #0C1A1A;
            font-family: 'Segoe UI Semibold';
            font-size: 12pt;
        }
    """

    Q_LINE = """
        QLineEdit {
            background-color: #FFFFFF;
            border: 2px solid #6ACFC7;
            border-radius: 8px;
            padding: 6px 10px;
            font-size: 14px;
            color: #0C1A1A;
        }

        QLineEdit::placeholder {
            color: #8DD9D3;
        }

        QLineEdit:focus {
            border: 2px solid #4AA29B;
        }
    """

    DIALOG_NAME_MODEL = """ 
        QInputDialog {
            background-color: #FFFFFF;
            color: #0C1A1A;
            font-family: 'Segoe UI Semibold';
            font-size: 14pt;
        }

        QLabel {
            color: #0C1A1A;
            font-size: 14pt;
            font-family: 'Segoe UI Semibold';
        }

        QLineEdit {
            background-color: #FFFFFF;
            color: #0C1A1A;
            border: 2px solid #6ACFC7;
            border-radius: 4px;
            padding: 4px;
            font-family: 'Segoe UI Semibold';
            font-size: 14pt;
        }

        QPushButton {
            background-color: #6ACFC7;
            color: #FFFFFF;
            border: none;
            border-radius: 4px;
            padding: 6px 12px;
            font-family: 'Segoe UI Semibold';
            font-size: 12pt;
        }

        QPushButton:hover {
            background-color: #58B8B0;
        }

        QPushButton:pressed {
            background-color: #4AA29B;
        }
    """

    LABEL = """
        QLabel {
            color: #0C1A1A;
            font-size: 12pt;
            font-family: 'Segoe UI';
        }
    """

    COMBO_BOX = """ 
        QComboBox {
            background-color: #FFFFFF;
            color: #0C1A1A;
            border: 1px solid #6ACFC7;
            border-radius: 6px;
            padding: 6px 8px;
            font-family: 'Segoe UI Semibold';
            font-size: 13pt;
            selection-background-color: #6ACFC7;
            selection-color: #FFFFFF;
        }

        QComboBox:focus {
            border: 2px solid #4AA29B;
        }

        QComboBox::drop-down {
            border: none;
            width: 25px;
            background-color: #FFFFFF;
        }

        QComboBox::down-arrow {
            image: url(:/qt-project.org/styles/commonstyle/images/arrowdown-16.png);
            width: 12px;
            height: 12px;
        }

        QComboBox QAbstractItemView {
            background-color: #FFFFFF;
            color: #0C1A1A;
            selection-background-color: #6ACFC7;
            selection-color: #FFFFFF;
            border: 1px solid #6ACFC7;
            outline: 0;
        }
    """ 

    DIALOG_RESULTS = """
        QDialog {
            background-color: #FFFFFF;
            color: #0C1A1A;
            font-family: 'Segoe UI Semibold';
            font-size: 12pt;
        }

        QLabel {
            color: #0C1A1A;
            font-size: 13pt;
            font-family: 'Segoe UI Semibold';
        }

        QPushButton {
            background-color: #6ACFC7;
            color: #FFFFFF;
            border: none;
            border-radius: 6px;
            padding: 6px 12px;
            font-family: 'Segoe UI Semibold';
            font-size: 11pt;
        }

        QPushButton:hover {
            background-color: #58B8B0;
        }

        QPushButton:pressed {
            background-color: #4AA29B;
        }

        QTableWidget {
            background-color: #FFFFFF;
            gridline-color: #6ACFC7;
            color: #0C1A1A;
            border: 1px solid #6ACFC7;
            selection-background-color: #6ACFC7;
            selection-color: #FFFFFF;
            alternate-background-color: #EAF9F8;
        }

        QHeaderView::section {
            background-color: #EAF9F8;
            color: #0C1A1A;
            font-weight: bold;
            border: 1px solid #6ACFC7;
            padding: 6px;
        }

        QScrollBar:vertical {
            background: #EAF9F8;
            width: 10px;
            margin: 0px;
        }

        QScrollBar::handle:vertical {
            background: #6ACFC7;
            border-radius: 4px;
            min-height: 20px;
        }

        QScrollBar::handle:vertical:hover {
            background: #4AA29B;
        }

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0;
        }
    """
