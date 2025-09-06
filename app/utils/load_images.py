# app/utils/image_loader.py
import os
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QSize, Qt

class ImageLoader:
    @staticmethod
    def load_pixmap(image_name, subfolder="", size=None):
        
        base_path = "data/assets"
        if subfolder:
            path = os.path.join(base_path, subfolder, image_name)
        else:
            path = os.path.join(base_path, image_name)
        
        if os.path.exists(path):
            pixmap = QPixmap(path)
            if size and isinstance(size, QSize):
                pixmap = pixmap.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            return pixmap
        return QPixmap() 