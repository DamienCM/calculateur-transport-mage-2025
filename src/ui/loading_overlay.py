from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel
)
from PyQt5.QtCore import Qt
from ui.loading_spinner import LoadingSpinner



class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Make the overlay stay on top
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Style the overlay and its components
        self.setStyleSheet("""
            LoadingOverlay {
                background-color: rgba(0, 0, 0, 0);  /* Tranperent for main overlay */
            }
            QLabel {
                color: black;
                font-size: 16px;
                font-weight: bold;
                background-color: rgba(0, 0, 0, 0);  /* Tranparent */
                padding: 5px;
            }
            QWidget#container {
                background-color: rgba(0, 0, 0, 0);  /* Light gray */
                border-radius: 10px;
            }
        """)
        
        # Create container widget with a unique object name for styling
        self.container = QWidget(self)
        self.container.setObjectName("container")
        self.container.setFixedSize(200, 200)  # Fixed size for the container
        
        # Container layout
        container_layout = QVBoxLayout(self.container)
        container_layout.setSpacing(20)
        container_layout.setContentsMargins(20, 20, 20, 20)
        
        # Create and add spinner
        self.spinner = LoadingSpinner(centerOnParent=False)
        self.spinner.setFixedSize(100, 100)  # Fixed size for the spinner
        container_layout.addWidget(self.spinner, 0, Qt.AlignHCenter)
        
        # Create and add loading text
        self.label = QLabel("Calcul en cours...")
        self.label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(self.label, 0, Qt.AlignHCenter)

    def showEvent(self, event):
        super().showEvent(event)
        self.updatePosition()
        self.spinner.start()
        
    def hideEvent(self, event):
        super().hideEvent(event)
        self.spinner.stop()
    
    def updatePosition(self):
        if self.parent():
            # Get parent center coordinates
            parent_center_x = self.parent().width() // 2
            parent_center_y = self.parent().height() // 2
            
            # Get container center offsets
            container_center_x = self.container.width() // 2
            container_center_y = self.container.height() // 2
            
            # Calculate top-left position for container to be centered
            container_x = parent_center_x - container_center_x
            container_y = parent_center_y - container_center_y
            
            # Move container to centered position
            self.container.move(container_x, container_y)