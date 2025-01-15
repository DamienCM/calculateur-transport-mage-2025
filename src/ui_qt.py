"""
Shipping Calculator UI - A PyQt5 application for calculating shipping costs.
"""
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QMenuBar, QMenu,
    QAction, QMessageBox, QComboBox, QSpinBox, QFormLayout,
    QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QColor, QPainter, QPen, QIcon
import math

from PyQt5.QtCore import QThread, pyqtSignal
from typing import Dict, List, Any


class CalculatorThread(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    warning = pyqtSignal(str, name='warning')
   
    def __init__(self, calculator, panier: List[Dict], options: Dict[str, Any]):
        super().__init__()
        self.calculator = calculator
        self.panier = panier
        self.options = options
        self.should_continue = True
       
        def warning_handler(message):
            print("Warning handler called with message:", message)
            self.warning.emit(message)
            while not hasattr(self, 'warning_response'):
                self.msleep(100)
            print("Got warning response:", self.warning_response)
            response = self.warning_response
            delattr(self, 'warning_response')
            return response
       
        transporteurs = list(self.calculator.transporteurs.values())
        for transporteur in transporteurs:
            transporteur.set_warning_callback(warning_handler)
   
    def run(self):
        try:
            print("Starting calculation...")
            results = self.calculator.calculer(self.panier, self.options)
            print("Calculation finished, results:", results)
            if results:  
                print("Emitting finished signal")
                self.finished.emit(results)
                print("Finished signal emitted")
        except Exception as e:
            print("Error in calculation:", str(e))
            self.error.emit(str(e))

class CalculationError(Exception):
    def __init__(self, messsage = "[ERROR] Unknown error happened during calculation"):
        self.message = messsage
        super().__init__(self.message)        

@dataclass
class StyleConstants:
    """Constants for UI styling"""
    # Colors
    PRIMARY_COLOR = "#2196F3"
    SECONDARY_COLOR = "#FFC107"
    DANGER_COLOR = "#F44336"
    BACKGROUND_COLOR = "#FFFFFF"
    PANEL_BACKGROUND = "#F5F5F5"
    TEXT_COLOR = "#212121"
    BUTTON_TEXT_COLOR = "#FFFFFF"
    BORDER_COLOR = "#E0E0E0"
    SHADOW_COLOR = "#888888"
    BUTTON_HOVER = "#1976D2"
    BUTTON_PRESSED = "#0D47A1"
    DELETE_BUTTON_HOVER = "#D32F2F"
    DELETE_BUTTON_BACKGROUND = "#B71C1C"
    
    # Dimensions
    BUTTON_HEIGHT = 40
    INPUT_HEIGHT = 20
    CORNER_RADIUS = 4
    PANEL_SPACING = 30
    WIDGET_SPACING = 20
    SECTION_SPACING = 10
    MIN_PANEL_WIDTH = 200
    MIN_PANEL_WIDTH_INPUT = 500
    SHADOW_BLUR = 10
    SHADOW_OFFSET = 3
    DELETE_BUTTON_WIDTH = 25
    DELETE_BUTTON_HEIGHT = 25
    
    # Fonts
    FONT_FAMILY = "Segoe UI"
    HEADER_FONT_SIZE = 14
    NORMAL_FONT_SIZE = 12
    
    # Defaults
    DEFAULT_DPD_MAX = "29"
    DEFAULT_THRESHOLD = "2"
    
    # Paths
    WINDOW_ICON = '../icons/Logo-MAGE-Application.ico'
    
    @classmethod
    def get_base_styles(cls) -> str:
        """Returns the base stylesheet for the application"""
        return f"""
            QMainWindow {{
                background-color: {cls.BACKGROUND_COLOR};
            }}
            QFrame {{
                background-color: {cls.PANEL_BACKGROUND};
                border-radius: {cls.CORNER_RADIUS}px;
                border: none;
            }}
            QLabel {{
                color: {cls.TEXT_COLOR};
                font-family: {cls.FONT_FAMILY};
                font-size: {cls.NORMAL_FONT_SIZE}px;
                padding: 5px;
            }}
            QLineEdit {{
                height: {cls.INPUT_HEIGHT}px;
                padding: 5px 10px;
                border: 1px solid {cls.BORDER_COLOR};
                border-radius: {cls.CORNER_RADIUS}px;
                background-color: white;
                font-family: {cls.FONT_FAMILY};
                font-size: {cls.NORMAL_FONT_SIZE}px;
            }}
            QPushButton#action-button {{  /* New specific style for action buttons */
                height: {cls.BUTTON_HEIGHT}px;
                background-color: {cls.PRIMARY_COLOR};
                color: {cls.BUTTON_TEXT_COLOR};
                border-radius: {cls.CORNER_RADIUS}px;
                font-family: {cls.FONT_FAMILY};
                font-size: {cls.NORMAL_FONT_SIZE}px;
                padding: 5px 15px;
            }}
            QPushButton#action-button:hover {{
                background-color: {cls.BUTTON_HOVER};
            }}
            QPushButton#action-button:pressed {{
                background-color: {cls.BUTTON_PRESSED};
            }}
            QPushButton#delete-button {{
                background-color: {cls.DANGER_COLOR};
                width: {cls.DELETE_BUTTON_WIDTH}px;
                height: {cls.DELETE_BUTTON_HEIGHT}px;
                border-radius: {cls.CORNER_RADIUS}px;
                font-family: {cls.FONT_FAMILY};
                padding: 0px;
                font-size: 15px;
                text-align: center;
                font-weight: bold;
            }}
            QPushButton#delete-button:hover {{
                background-color: {cls.DELETE_BUTTON_HOVER};
            }}
            QPushButton#delete-button:pressed {{
                background-color: {cls.DELETE_BUTTON_BACKGROUND};
            }}
            QComboBox, QSpinBox {{
                height: {cls.INPUT_HEIGHT}px;
                padding: 5px 10px;
                border: 1px solid {cls.BORDER_COLOR};
                border-radius: {cls.CORNER_RADIUS}px;
                background-color: white;
                font-family: {cls.FONT_FAMILY};
                font-size: {cls.NORMAL_FONT_SIZE}px;
            }}
            
            QComboBox::drop-down {{
                border: none;
                background-color: white;
            }}

            QComboBox::down-arrow {{
                /* Creates a custom dropdown arrow using borders */
                image: url(../icons/dropdown.svg);  /* Qt will use system default arrow */                border-left: 5px solid transparent;
                width:15px;
                height:15px;
                border-left: 8px solid transparent;   /* Increase these values to make bigger */
                border-right: 8px solid transparent;
                margin-right: 8px;
            }}

            QComboBox:on {{
                /* Removes bottom radius when dropdown is open */
                border-bottom-left-radius: 0;
                border-bottom-right-radius: 0;
            }}

            QComboBox QAbstractItemView {{
                /* Styles the dropdown menu */
                background-color: white;
                border: 1px solid {cls.BORDER_COLOR};
                border-top: none;
                selection-background-color: {cls.PRIMARY_COLOR};
                selection-color: white;
            }}

            QComboBox QAbstractItemView::item {{
                /* Styles individual items in the dropdown */
                min-height: {cls.INPUT_HEIGHT}px;
                padding: 5px 10px;
            }}

            QComboBox QAbstractItemView::item:hover {{
                /* Styles the hover state of items */
                background-color: {cls.PANEL_BACKGROUND};
            }}
                        
        """

class LoadingSpinner(QWidget):
    def __init__(self, parent=None, centerOnParent=True, disableParentWhenSpinning=True):
        super().__init__(parent)
        
        self.centerOnParent = centerOnParent
        self.disableParentWhenSpinning = disableParentWhenSpinning
        
        # Remove window modality as we're using an overlay
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Adjusted parameters for better visibility
        self.angleOffset = 30
        self.timerId = -1
        self.angle = 0
        self.delay = 80  # Slower rotation
        self.displayedWhenStopped = False
        self.color = QColor("#2196F3")  # Bright blue color
        
        self.roundness = 100.0
        self.minimumTrailOpacity = 40  # Higher minimum opacity
        self.trailFadePercentage = 90  # Less fade for better visibility
        self.numberOfLines = 12
        self.lineLength = 25  # Even longer lines
        self.lineWidth = 6    # Even thicker lines
        self.innerRadius = 25 # Even larger radius
        
        self.isSpinning = False
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.updateSize()
        self.updateTimer()
        self.hide()
        
        # Force a minimum size
        self.setMinimumSize(QSize(100, 100))

    def paintEvent(self, QPaintEvent):
        self.updatePosition()
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.transparent)
        painter.setRenderHint(QPainter.Antialiasing, True)
        
        if self.isSpinning:
            for i in range(0, self.numberOfLines):
                painter.save()
                painter.translate(self.innerRadius + self.lineLength, self.innerRadius + self.lineLength)
                rotateAngle = float(360 * i) / float(self.numberOfLines)
                painter.rotate(rotateAngle + self.angle)
                painter.translate(self.innerRadius, 0)
                distance = self.lineCountDistanceFromPrimary(i, self.numberOfLines, self.trailFadePercentage, 
                                                           self.minimumTrailOpacity, self.angle)
                color = self.currentLineColor(distance, self.minimumTrailOpacity, self.color)
                painter.setPen(QPen(color, self.lineWidth, Qt.SolidLine))
                painter.drawLine(0, 0, self.lineLength, 0)
                painter.restore()

    def start(self):
        self.isSpinning = True
        self.show()
        
        if self.parentWidget and self.disableParentWhenSpinning:
            self.parentWidget().setEnabled(False)
            
        if not self.timer.isActive():
            self.timer.start()
            self.angle = 0

    def stop(self):
        self.isSpinning = False
        self.hide()
        
        if self.parentWidget() and self.disableParentWhenSpinning:
            self.parentWidget().setEnabled(True)
            
        if self.timer.isActive():
            self.timer.stop()

    def rotate(self):
        self.angle = (self.angle + self.angleOffset) % 360
        self.update()

    def updateSize(self):
        size = (self.innerRadius + self.lineLength) * 2
        self.setFixedSize(size, size)

    def updateTimer(self):
        self.timer.setInterval(self.delay)

    def updatePosition(self):
        if self.parentWidget() and self.centerOnParent:
            parentRect = self.parentWidget().rect()
            self.move(
                parentRect.center().x() - self.width() / 2,
                parentRect.center().y() - self.height() / 2
            )

    def lineCountDistanceFromPrimary(self, current, primary, fadePerc, minOpacity, angleCurrent):
        distance = (primary - current) % primary
        if distance > primary / 2:
            distance = primary - distance
        return math.pow(distance / (primary / 2), fadePerc) * (1 - minOpacity / 100) + minOpacity / 100

    def currentLineColor(self, countDistance, minOpacity, colorinput):
        color = QColor(colorinput)
        color.setAlpha(round(minOpacity + ((255 - minOpacity) * countDistance)))
        return color

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
class ArticleEntry:
    """Represents a single article entry in the UI"""
    def __init__(self, parent: QWidget, entry_id: int, input_format: str, articles_list: List[Dict]):
        self.widget = QWidget(parent)
        self.widget.setObjectName("article-entry")
        self.layout = QHBoxLayout(self.widget)
        self.entry_id = entry_id
        self.input_format = input_format
        self.setup_ui(articles_list)
        
    def setup_ui(self, articles_list: List[Dict]) -> None:
        """Set up the UI components based on input format"""
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        
        if self.input_format == 'raw':
            self.setup_raw_input()
        else:
            self.setup_reference_input(articles_list)
            
    def setup_raw_input(self) -> None:
        """Set up UI for raw weight input"""
        label = QLabel("Poids de l'article (kg):")
        self.entry = QLineEdit()
        self.entry.setPlaceholderText("Entrez le poids")
        self.layout.addWidget(label)
        self.layout.addWidget(self.entry, 1)
        
    def setup_reference_input(self, articles_list: List[Dict]) -> None:
        """Set up UI for reference-based input"""
        label = QLabel("Article:")
        self.combobox = QComboBox()
        field = 'Ref' if self.input_format == 'ref' else 'Designation'
        self.combobox.addItems([f"{article['id']}. {article[field]}" for article in articles_list])
        
        label_qty = QLabel("Quantité:")
        self.qty_box = QSpinBox()
        self.qty_box.setRange(1, 999)
        
        self.layout.addWidget(label)
        self.layout.addWidget(self.combobox, 1)
        self.layout.addWidget(label_qty)
        self.layout.addWidget(self.qty_box)

class ShippingCalculator(QMainWindow):
    """Main window class for the shipping calculator application"""
    PATH_ARTICLES_LIST = Path("../data/items.csv")
    PATH_COUNTRY_LIST = Path("../data/country_list.csv")

    def __init__(self, calculator):
        super().__init__()
        self.calculator = calculator
        self.entry_id = 0
        self.entries: List[ArticleEntry] = []
        self.input_format = 'raw'
        self.articles_list = self._load_articles_list()
        self.country_list = self._load_country_list()
        self.entries_layout = None
        
        self.init_ui()
        self.apply_styles()
        
    def _load_articles_list(self) -> List[Dict[str, Any]]:
        """Load articles list from CSV file"""
        articles_list = []
        csv_structure = ["Ref", "Nom", "Designation", "Prix", "Masse (kg)"]

        try:
            with open(self.PATH_ARTICLES_LIST) as f:
                # Skip first two rows
                lines = f.readlines()[2:]
                for index, line in enumerate(lines):
                    line_splitted = line.split(',')
                    article = {"id": index}
                    for el, label in zip(line_splitted, csv_structure):
                        article[label] = el.strip()
                    articles_list.append(article)
                
            print(f"Articles list loaded successfully: {len(articles_list)} items")
            return articles_list
            
        except FileNotFoundError as e:
            print(f"Error: Could not find articles list file: {e}")
            return []
        except Exception as e:
            print(f"Error loading articles list: {e}")
            return []
    
    def _load_country_list(self) -> List[str]:
        """Load articles list from CSV file"""
        country_list = []

        try:
            with open(self.PATH_COUNTRY_LIST) as f:
                # Skip first two rows
                lines = f.readlines()[2:]
                for line in lines:
                    country = line.strip()
                    country_list.append(country)
                
            print(f"Country list loaded successfully: {len(country_list)} countries")
            return country_list
            
        except FileNotFoundError as e:
            print(f"Error: Could not find country list file: {e}")
            return []
        except Exception as e:
            print(f"Error loading country list : {e}")
            return []

    def init_ui(self) -> None:
        """Initialize the user interface"""
        self.setWindowTitle('Calculateur de Frais de Livraison')
        icon = QIcon('../icons/Logo-MAGE-Application.ico')
        self.setWindowIcon(icon)
        self.setGeometry(100, 100, 1600, 900)
        self.create_menu_bar()
        self.setup_central_widget()
        
    def apply_styles(self) -> None:
        """Apply global styles to the application"""
        self.setStyleSheet(StyleConstants.get_base_styles())
        
    def setup_central_widget(self) -> None:
        """Set up the main layout and panels"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        layout.setSpacing(StyleConstants.PANEL_SPACING)
        layout.setContentsMargins(
            StyleConstants.PANEL_SPACING,
            StyleConstants.PANEL_SPACING,
            StyleConstants.PANEL_SPACING,
            StyleConstants.PANEL_SPACING
        )
        
        layout.addWidget(self.create_input_panel(), 2)
        layout.addWidget(self.create_control_panel(), 1)
        layout.addWidget(self.create_result_panel(), 2)
        self.setup_loading_overlay()

    def create_menu_bar(self) -> None:
        """Create the application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('Fichier')
        self._add_menu_action(file_menu, 'Nouveau', 'Ctrl+N', self.new_calculation)
        self._add_menu_action(file_menu, 'Sauvegarder', 'Ctrl+S', self.save_calculation)
        file_menu.addSeparator()
        self._add_menu_action(file_menu, 'Quitter', 'Ctrl+Q', self.close)
        
        # Edit menu
        edit_menu = menubar.addMenu('Édition')
        self._add_menu_action(edit_menu, 'Effacer tout', shortcut=None, callback=self.clear_all)
        
        # Input format submenu
        switch_menu = edit_menu.addMenu("Changer le mode d'entrée")
        for format_name, display_name in [
            ('raw', 'Entrees par masse des articles'),
            ('ref', 'Entrees par ref'),
            ('designation', 'Entrees par designation')
        ]:
            self._add_menu_action(switch_menu, display_name, None,
                                lambda f=format_name: self.switch_input_format(f))
        
        # Help menu
        help_menu = menubar.addMenu('Aide')
        self._add_menu_action(help_menu, 'À propos', None, self.show_about)

    @staticmethod
    def _add_menu_action(menu: QMenu, name: str, shortcut: Optional[str], 
                        callback: callable) -> None:
        """Helper method to add menu actions"""
        action = QAction(name, menu)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(callback)
        menu.addAction(action)

    def create_styled_frame(self,panel="std") -> QFrame:
        """Create a styled QFrame with shadow effect"""
        frame = QFrame()
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        if panel =="std":
            frame.setMinimumWidth(StyleConstants.MIN_PANEL_WIDTH)
        elif panel =="input":
            frame.setMinimumWidth(StyleConstants.MIN_PANEL_WIDTH_INPUT)
        else :
            frame.setMinimumWidth(StyleConstants.MIN_PANEL_WIDTH)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setColor(QColor(StyleConstants.SHADOW_COLOR))
        shadow.setBlurRadius(StyleConstants.SHADOW_BLUR)
        shadow.setOffset(0, StyleConstants.SHADOW_OFFSET)
        frame.setGraphicsEffect(shadow)
        
        return frame
    
    def create_input_panel(self):
        """Create the left panel with improved styling"""
        self.input_frame = self.create_styled_frame(panel='input')
        layout = QVBoxLayout(self.input_frame)
        layout.setSpacing(StyleConstants.WIDGET_SPACING)
        layout.setContentsMargins(
            StyleConstants.WIDGET_SPACING,
            StyleConstants.WIDGET_SPACING,
            StyleConstants.WIDGET_SPACING,
            StyleConstants.WIDGET_SPACING
        )
        
        # Add header
        header = QLabel("Articles")
        header.setStyleSheet(f"""
            font-size: {StyleConstants.HEADER_FONT_SIZE}px;
            font-weight: bold;
            color: {StyleConstants.TEXT_COLOR};
        """)
        layout.addWidget(header)
        
        # Rest of the input panel setup...
        # [Previous input panel code remains the same]
        """Set up the left panel for article inputs"""
        
        # Create container for entries
        entries_container = QWidget()
        self.entries_layout = QVBoxLayout(entries_container)
        self.entries_layout.setSpacing(0)
        self.entries_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(entries_container)
        
        # Add vertical spacer
        layout.addStretch(1)
        
        # Add article button
        self.ajouter_article_button = QPushButton("Ajouter un article")
        self.ajouter_article_button.setObjectName('action-button')
        self.ajouter_article_button.setFixedHeight(StyleConstants.BUTTON_HEIGHT)
        self.ajouter_article_button.clicked.connect(self.ajouter_article)
        layout.addWidget(self.ajouter_article_button)
        
        # Add first article by default
        self.ajouter_article()
        return self.input_frame

    def create_control_panel(self):
        """Create the middle panel with improved styling"""
        self.control_frame = self.create_styled_frame()
        layout = QVBoxLayout(self.control_frame)
        layout.setSpacing(StyleConstants.WIDGET_SPACING)
        layout.setContentsMargins(
            StyleConstants.WIDGET_SPACING,
            StyleConstants.WIDGET_SPACING,
            StyleConstants.WIDGET_SPACING,
            StyleConstants.WIDGET_SPACING
        )
        
        # Add header
        header = QLabel("Paramètres de livraison")
        header.setStyleSheet(f"""
            font-size: {StyleConstants.HEADER_FONT_SIZE}px;
            font-weight: bold;
            color: {StyleConstants.TEXT_COLOR};
            margin-bottom: {StyleConstants.SECTION_SPACING}px;
        """)
        layout.addWidget(header)
        
        # Create form layout
        form = QFormLayout()
        form.setSpacing(StyleConstants.WIDGET_SPACING)
        
        # Add form fields with increased spacing
        self.departement_entry = QLineEdit()
        self.country_combobox = QComboBox()
        self.country_combobox.addItems(self.country_list)
        self.dpd_max_entry = QLineEdit(StyleConstants.DEFAULT_DPD_MAX)
        self.threshold_entry = QLineEdit(StyleConstants.DEFAULT_THRESHOLD)
        
        for widget in [self.departement_entry, self.dpd_max_entry, self.threshold_entry]:
            widget.setStyleSheet(widget.styleSheet() + f"margin-bottom: {StyleConstants.WIDGET_SPACING}px;")
        
        form.addRow("Département:", self.departement_entry)
        form.addRow("Pays :", self.country_combobox)
        form.addRow("Poids max dpd (kg):", self.dpd_max_entry)
        form.addRow("Seuil petit colis (kg):", self.threshold_entry)
        
        layout.addLayout(form)
        
        # Add stretch to push button to bottom
        layout.addStretch()
        
        # Calculate button with special styling - full width at bottom
        self.calc_button = QPushButton("Calculer")
        self.calc_button.setObjectName('action-button')
        # self.calc_button.setObjectName("calc_button")
        self.calc_button.clicked.connect(self.new_calculer_frais_wrapper)
        self.calc_button.setFixedHeight(StyleConstants.BUTTON_HEIGHT)
        layout.addWidget(self.calc_button)
        
        return self.control_frame

    def create_result_panel(self):
        """Create the right panel with improved styling"""
        self.result_frame = self.create_styled_frame()
        layout = QVBoxLayout(self.result_frame)
        layout.setSpacing(StyleConstants.SECTION_SPACING)  # Increased spacing between sections
        layout.setContentsMargins(
            StyleConstants.WIDGET_SPACING,
            StyleConstants.WIDGET_SPACING,
            StyleConstants.WIDGET_SPACING,
            StyleConstants.WIDGET_SPACING
        )
        
        # Add header
        header = QLabel("Résultats")
        header.setStyleSheet(f"""
            font-size: {StyleConstants.HEADER_FONT_SIZE}px;
            font-weight: bold;
            color: {StyleConstants.TEXT_COLOR};
            margin-bottom: {StyleConstants.SECTION_SPACING}px;
        """)
        layout.addWidget(header)
        
        # Create sections with headers
        sections = {
            'cart': {
                'title': 'Panier',
                'labels': ['basket']
            },
            'palette': {
                'title': 'Palette',
                'labels': ['schenker_palette']
            },
            'messagerie': {
                'title': 'Messagerie',
                'labels': ['schenker_messagerie']
            },
            'dpd': {
                'title': 'DPD',
                'labels': ['dpd_results', 'dpd_arrangement']
            }
        }
        
        # Create and style result labels
        self.result_labels = {
            'basket': QLabel("Panier : \n"),
            'schenker_palette': QLabel("Prix Schenker palette : "),
            'schenker_messagerie': QLabel("Prix Schenker messagerie: "),
            'dpd_results': QLabel("Resultats dpd : "),
            'dpd_arrangement': QLabel("Arrangement dpd : ")
        }
        
        # Add sections with their labels
        for section_name, section_data in sections.items():
            # Add section header
            section_header = QLabel(section_data['title'])
            section_header.setStyleSheet(f"""
                font-size: {StyleConstants.NORMAL_FONT_SIZE}px;
                font-weight: bold;
                color: {StyleConstants.TEXT_COLOR};
                padding: 5px 0;
            """)
            layout.addWidget(section_header)
            
            # Add section container with background
            section_container = QFrame()
            section_container.setStyleSheet(f"""
                background-color: white;
                border-radius: {StyleConstants.CORNER_RADIUS}px;
                border: 1px solid #EEEEEE;
            """)
            section_layout = QVBoxLayout(section_container)
            section_layout.setSpacing(StyleConstants.WIDGET_SPACING)
            section_layout.setContentsMargins(10, 10, 10, 10)
            
            # Add labels for this section
            for label_key in section_data['labels']:
                label = self.result_labels[label_key]
                label.setStyleSheet("""
                    padding: 5px;
                    border-bottom: 1px solid #EEEEEE;
                """)
                section_layout.addWidget(label)
            
            layout.addWidget(section_container)
            
        layout.addStretch()
        return self.result_frame

    def setup_loading_overlay(self):
        """Initialize the loading overlay"""
        self.loading_overlay = LoadingOverlay(self)
        self.loading_overlay.hide()
    
    def show_loading_overlay(self):
        """Show the loading overlay"""
        # Make sure overlay covers the entire parent
        self.loading_overlay.setGeometry(0, 0, self.width(), self.height())
        self.loading_overlay.show()
        self.loading_overlay.raise_()
    
    def hide_loading_overlay(self):
        """Hide the loading overlay"""
        self.loading_overlay.hide()

    def load_articles_list(self):
        articles_list = []
        csv_structure = ["Ref", "Nom", "Designation", "Prix", "Masse (kg)"]

        try :
            with open(self.PATH_ARTICLES_LIST) as f:
                lines = f.readlines()[2:] #skipping 2 first rows
                for index, line in enumerate(lines):
                    line_splitted= line.split(',')
                    article = {"id":index}
                    for el,label in zip(line_splitted,csv_structure):
                        el = el.strip()
                        article[label]=el
                    # print(article)
                    articles_list.append(article)
                
                print(f"articles list loaded : \n {articles_list}")
                return articles_list
        except FileNotFoundError as e:
            print(e)
            return None
        except Exception as e :
            print(e)
            return articles_list




        return articles_list
    
    # Create menu bar
    def create_menu_bar(self):
        # Create menu bar
        menubar = self.menuBar()
        
        # File menu
        fileMenu = menubar.addMenu('Fichier')
        
        # New action
        newAction = QAction('Nouveau', self)
        newAction.setShortcut('Ctrl+N')
        newAction.triggered.connect(self.new_calculation)
        fileMenu.addAction(newAction)
        
        # Save action
        saveAction = QAction('Sauvegarder', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.triggered.connect(self.save_calculation)
        fileMenu.addAction(saveAction)
        
        fileMenu.addSeparator()
        
        # Exit action
        exitAction = QAction('Quitter', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(exitAction)
        
        # Edit menu
        editMenu = menubar.addMenu('Édition')
        
        # Clear all action
        clearAction = QAction('Effacer tout', self)
        clearAction.triggered.connect(self.clear_all)
        editMenu.addAction(clearAction)
        # Changing input format
        switchMenu = editMenu.addMenu("Changer le mode d'entrée")
        rawInput = QAction('Entrees par masse des articles',self)
        rawInput.triggered.connect(lambda: self.switch_input_format('raw'))
        refInput = QAction('Entrees par ref',self)
        refInput.triggered.connect(lambda: self.switch_input_format('ref'))
        designationInput = QAction('Entrees par designation',self)
        designationInput.triggered.connect(lambda: self.switch_input_format('designation'))
        switchMenu.addAction(rawInput)
        switchMenu.addAction(refInput)
        switchMenu.addAction(designationInput)
        
        # Help menu
        helpMenu = menubar.addMenu('Aide')
        
        # About action
        aboutAction = QAction('À propos', self)
        aboutAction.triggered.connect(self.show_about)
        helpMenu.addAction(aboutAction)

    def new_calculation(self):
        """Clear all entries and start fresh"""
        reply = QMessageBox.question(self, 'Nouveau calcul', 
                                   'Voulez-vous vraiment effacer tous les champs ?',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.clear_all()
    
    def save_calculation(self):
        """Placeholder for save functionality"""
        QMessageBox.information(self, 'Sauvegarde', 
                              'Fonctionnalité de sauvegarde à implémenter.')
        
    def clear_all(self):
        """Clear all entries and results"""
        # Clear department
        self.departement_entry.clear()
        
        # Clear all article entries
        while len(self.entries) > 0:
            entry_data = self.entries[0]
            entry_data['widget'].deleteLater()
            self.entries.pop(0)
        
        # Reset results
        self.result_labels['basket'].setText("Resultats : \n")
        self.result_labels['schenker_palette'].setText("Prix Schenker palette : ")
        self.result_labels['schenker_messagerie'].setText("Prix Schenker messagerie: ")
        self.result_labels['dpd_results'].setText("Resultats dpd : ")
        self.result_labels['dpd_arrangement'].setText("Arrangement dpd : ")
        
        # Add back one empty article entry
        self.ajouter_article()
    
    def switch_input_format(self,input_format):
        """ Switch input between raw and dropdown """
        #Switch envireonnment variable
        print(f"[INFO] Switching input format to : {input_format}")
        self.input_format = input_format
        
        self.clear_all()        

        return 0

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, 'À propos',
                         'Calculateur de Frais de Livraison\n\n'
                         'Version 1.0\n'
                         '© 2024 MAGE')

    def ajouter_article(self):
        """Add a new article entry with modern styling"""
        # Increment entry counter
        self.entry_id += 1
        current_id = self.entry_id
        
        # Create widget using helper method, passing the current_id
        article_widget, components = self.setup_article_widget(current_id)

        # Add widget to layout
        self.entries_layout.addWidget(article_widget)

        if 'entry' in components:
            components['entry'].setFocus()
        
        # Create entry data with common fields
        entry_data = {
            'widget': article_widget,
            'id': current_id
        }
        
        # Add specific components based on input format
        if self.input_format == 'raw':
            entry_data['entry'] = components['entry']
        else:
            entry_data['combobox'] = components['combobox']
            entry_data['qty_box'] = components['qty_box']
        
        # Add to entries list
        self.entries.append(entry_data)

    def setup_article_widget(self, current_id):
        """Create a styled article entry widget"""
        article_widget = QWidget()
        article_widget.setObjectName("article-entry")
        layout = QHBoxLayout(article_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        if self.input_format == 'raw':
            # Raw input mode
            label = QLabel("Poids de l'article (kg):")
            entry = QLineEdit()
            entry.setPlaceholderText("Entrez le poids")
            
            layout.addWidget(label)
            layout.addWidget(entry, 1)  # Give entry more stretch
            
            result = {'entry': entry}
            
        else:  # ref or designation modes
            # Reference or designation mode
            label = QLabel("Article:")
            combobox = QComboBox()
            field = 'Ref' if self.input_format == 'ref' else 'Designation'
            combobox.addItems([f"{article['id']}. {article[field]}" for article in self.articles_list])
            
            label_qty = QLabel("Quantité:")
            qty_box = QSpinBox()
            qty_box.setMinimum(1)
            qty_box.setMaximum(999)
            
            layout.addWidget(label)
            layout.addWidget(combobox, 1)  # Give combobox more stretch
            layout.addWidget(label_qty)
            layout.addWidget(qty_box)
            
            result = {'combobox': combobox, 'qty_box': qty_box}

        # Delete button
        suppr_button = QPushButton("×")  # Using × instead of X for better appearance
        suppr_button.setObjectName("delete-button")
        suppr_button.clicked.connect(lambda: self.supprimer_article(current_id))
        layout.addWidget(suppr_button)

        return article_widget, result
         
    def supprimer_article(self, line_id):
        if len(self.entries) <= 1:
            return
            
        for i, entry_data in enumerate(self.entries):
            if entry_data['id'] == line_id:
                entry_data['widget'].deleteLater()
                self.entries.pop(i)
                break
    
    def create_shopping_cart(self):
        try :
            panier = []
            for entry_data in self.entries:
                if self.input_format == 'raw':
                    weight_text = entry_data['entry'].text()
                    if weight_text:
                        panier.append({
                            'nom': f'article{len(panier)+1}',
                            'poids': float(weight_text)
                        })
                elif self.input_format == 'designation' or self.input_format =='ref':
                    combobox_text = entry_data['combobox'].currentText().split('.')
                    article_id = int(combobox_text[0])
                    article_name_or_ref = "".join(combobox_text[1:])
                    matching_weight = None
                    for article in self.articles_list:
                        if article["id"]==article_id:
                            matching_weight=article["Masse (kg)"]
                    article_qty = int(entry_data['qty_box'].cleanText())
                    if matching_weight is not None:
                        for _ in range(article_qty):
                            panier.append({
                                'nom' : article_name_or_ref,
                                'poids' : float(matching_weight)
                            })
        except Exception as e :
            print(f"[ERROR] Could not load the create the cart from inputs : \n {e}")
        print(f"[INFO] Panier successfully parsed :\n {panier}")
        return panier

    @staticmethod
    def _is_valid_departement(departement : str) -> bool:
        if type(departement) is not str :
            return False
        if len(departement)>2:
            return False
        if departement.isdigit():
            return True
        else: 
            return False

    def get_input_options(self):
        max_dpd = self.dpd_max_entry.text()
        seuil_mini = self.threshold_entry.text()
        country = self.country_combobox.currentText()
        departement = self.departement_entry.text()

        if not self._is_valid_departement(departement):
            raise SyntaxError('Invalid departement entered')

        try :
            max_dpd = float(max_dpd)
            int(departement)
            seuil_mini = float(seuil_mini)
        except Exception as e :
            print("[ERROR] Unable to convert to float : {e}")
            return None
        print('[INFO] Input options parsed successfully')
        return {
            'POIDS_MAX_COLIS_DPD':max_dpd,
            'SEUIL_ARTICLE_LEGER':seuil_mini,
            "SEUIL_COMPACTAGE":seuil_mini,
            "country" : country,
            "departement" : departement,
        }

    def calculer_frais_wrapper(self): 
        try:
            self.calculer_frais()
        except CalculationError as e: 
            parent = QWidget()
            qm_result = QMessageBox.warning(
                        parent,
                        'Attention', 
                        f"Le calcul n'a pas pu etre effectué : \n {e}",
                        QMessageBox.Ok,
                        )
            print("[INFO] Error handled during calculation")
        except Exception as e: 
            parent = QWidget()
            qm_result = QMessageBox.critical(
                        parent,
                        'Error', 
                        f"Erreur critique durant le calcul. Le programme va se fermer. \n {e}",
                        QMessageBox.Ok,
                        )
            print(f"[ERROR] Erreur critique durant le calcul. Le programme va se fermer. \n {e}")
            quit()            

    # Remove the original calculer_frais_wrapper method
    def new_calculer_frais_wrapper(self):
        """Wrapper to handle calculation errors"""
        try:
            self.new_calculer_frais()
        except CalculationError as e:
            self.hide_loading_overlay()  # Make sure overlay is hidden
            parent = QWidget()
            QMessageBox.warning(
                parent,
                'Attention',
                f"Le calcul n'a pas pu etre effectué : \n {e}",
                QMessageBox.Ok,
            )
            print("[INFO] Error handled during calculation")
        except Exception as e:
            self.hide_loading_overlay()  # Make sure overlay is hidden
            parent = QWidget()
            QMessageBox.critical(
                parent,
                'Error',
                f"Erreur critique durant le calcul. \n {e}",
                QMessageBox.Ok,
            )
            print(f"[ERROR] Critical error during calculation: \n {e}")

    def calculer_frais(self):
        try:
            panier = self.create_shopping_cart()
            options = self.get_input_options()
            try:
                self.calculator.set_options(options)
            except Exception as e:
                print(f"[ERROR] Could not set options : {e}")
                raise CalculationError(f"[ERROR] Could not set options : {e}")
            if panier == []:
                print('[WARNING] Panier is empty ! ')
                raise CalculationError('[WARNING] Panier is empty ! ')
            
            panier = self.calculator.compact_shopping_cart(panier)
            if len(panier)<10:
                label_articles = "\n".join([f"{article['poids']}kg --> {article['nom']}" for article in panier])
            else :
                label_articles = "\n".join([f"{article['poids']}kg --> {article['nom']}" for article in panier[:10]])
                label_articles+="\n ..."

            # Show loading overlay and ensure it's displayed
            # self.loading_overlay.raise_()
            self.show_loading_overlay()
            # for _ in range(2):  # Process events multiple times to ensure display
            #     QApplication.processEvents()
            try:
                # Perform calculation
                resultats = self.calculator.calculer(panier, options)
                QApplication.processEvents()  # Process any pending events
            except Exception as e: 
                self.hide_loading_overlay()
                print(f"[ERROR] Error during calculation {e}")
                raise CalculationError(f"[ERROR] Error from calculator {e}")
            finally:
                # Hide loading overlay after calculation (even if there's an error)
                self.hide_loading_overlay()

            if not "error" in resultats['dpd'] :
                prix_dpd = float(resultats['dpd']['prix'])
                self.result_labels['dpd_results'].setText(f"Prix dpd : {prix_dpd:.2f}€")
            else:
                self.result_labels['dpd_results'].setText(f"Prix DPD : Non calculé : {resultats['dpd']['error']}")
                prix_dpd = float('inf')
                
            if not 'error' in resultats['schenker_palette']:
                prix_schenker_palette = float(resultats['schenker_palette']['prix'])
                self.result_labels['schenker_palette'].setText(f"Prix Schenker palette : {prix_schenker_palette:.2f}€")
            else : 
                prix_schenker_palette = 'Non calculé'
                self.result_labels['schenker_palette'].setText(f"Prix Schenker palette : {resultats['schenker_palette']['error']}")
                prix_schenker_palette = float('inf')


            if not 'error' in resultats['schenker_messagerie']:
                prix_schenker_messagerie = float(resultats['schenker_messagerie']['prix'])
                self.result_labels['schenker_messagerie'].setText(f"Prix Schenker messagerie : {prix_schenker_messagerie:.2f}€")

            else : 
                prix_schenker_messagerie = 'Non calculé'
                self.result_labels['schenker_messagerie'].setText(f"Prix Schenker messagerie : {resultats['schenker_messagerie']['error']}")
                prix_schenker_messagerie = float('inf')
            
            if 'error' in resultats['schenker_messagerie'] and  'error' in resultats['schenker_palette'] and 'error' in resultats['dpd']:
                raise CalculationError(
                    f"""
                    [ERROR] None could be calculated
                    - DPD : {resultats['dpd']['error']}
                    - schenker_messagerie : {resultats['schenker_messagerie']['error']}
                    - schenker_palette : {resultats['schenker_palette']['error']}
                    """
                )


            dpd_arrangement_string = "Arrangement des colis DPD : \n"
            if not 'error' in resultats['dpd']:
                for i in range(len(resultats['dpd']['arrangement (masses)'])):
                    dpd_arrangement_string += f"{resultats['dpd']['masses colis'][i]:2f}kg ({resultats['dpd']['prix_colis'][i]}€) :\n"
                    for j in range(len(resultats['dpd']['arrangement (masses)'][i])):
                        if self.input_format == 'raw': 
                            dpd_arrangement_string+=f"\t{resultats['dpd']['arrangement (masses)'][i][j]} kg\n"
                        else:
                            dpd_arrangement_string+=f"\t{resultats['dpd']['arrangement (labels)'][i][j]} ({resultats['dpd']['arrangement (masses)'][i][j]} kg)\n"

            self.result_labels['dpd_arrangement'].setText(dpd_arrangement_string)
            

            min_prix = min(prix_dpd,prix_schenker_messagerie,prix_schenker_palette)

                
            self.result_labels['basket'].setText(f"Panier : \n{label_articles}")
            
            # Reset colors
            self.result_labels['dpd_results'].setStyleSheet("")
            self.result_labels['dpd_arrangement'].setStyleSheet("")
            self.result_labels['schenker_palette'].setStyleSheet("")
            self.result_labels['schenker_messagerie'].setStyleSheet("")
            
            # Highlight lowest price in red
            red_style = "color: red;"
            if min_prix == prix_dpd:
                self.result_labels['dpd_results'].setStyleSheet(red_style)
                self.result_labels['dpd_arrangement'].setStyleSheet(red_style)
            elif min_prix == prix_schenker_palette:
                self.result_labels['schenker_palette'].setStyleSheet(red_style)
            else:
                self.result_labels['schenker_messagerie'].setStyleSheet(red_style)
                    
        except SyntaxError as e:
            self.result_labels['basket'].setText(f"Erreur: Departement invalide {e}")
            print(f"[WARNING] Synthax error in departement : {e}")
            raise CalculationError(f"[WARNING] Synthax error in departement : {e}")

        except ValueError as e:
            self.result_labels['basket'].setText(f"Erreur: poids invalides {e}")
            print(f"[WARNING] Value error calculating : {e}")
            raise CalculationError(f"[WARNING] Value error calculating : {e}")

    def new_calculer_frais(self):
        """Calculate shipping costs in a separate thread"""
        try:
            # Prepare data for calculation
            panier = self.create_shopping_cart()
            if not panier:
                raise CalculationError('[WARNING] Panier is empty!')
                
            options = self.get_input_options()
            if options is None:
                raise CalculationError('[WARNING] Invalid options!')

            # First do any pre-calculation checks in the main thread
            # This will show any warning messages from the calculator
            try:
                self.calculator.set_options(options)
                panier = self.calculator.compact_shopping_cart(panier)
                # If you have a method to check if calculation will be long, call it here
                if hasattr(self.calculator, 'check_calculation'):
                    should_continue = self.calculator.check_calculation(panier, options)
                    if not should_continue:
                        return
            except Exception as e:
                raise CalculationError(str(e))

            # Show loading overlay
            self.show_loading_overlay()
            
            # Create and configure calculator thread
            self.calc_thread = CalculatorThread(self.calculator, panier, options)
            
            # Connect signals - make sure these are properly connected
            print("Connecting signals...")
            self.calc_thread.finished.connect(self._handle_calculation_results)
            self.calc_thread.error.connect(self._handle_calculation_error)
            self.calc_thread.warning.connect(self._handle_warning)
            self.calc_thread.finished.connect(self.hide_loading_overlay)
            self.calc_thread.error.connect(self.hide_loading_overlay)
            
            print("Starting calculation thread")
            self.calc_thread.start()
            
        except Exception as e:
            print("Error in calculer_frais:", str(e))
            self.hide_loading_overlay()
            raise CalculationError(str(e))

    def _handle_calculation_results(self, resultats):
        """Handle the calculation results"""
        print("Handling calculation results:", resultats)
        try:
            # Update DPD results
            if "error" not in resultats['dpd']:
                prix_dpd = float(resultats['dpd']['prix'])
                self.result_labels['dpd_results'].setText(f"Prix dpd : {prix_dpd:.2f}€")
            else:
                self.result_labels['dpd_results'].setText(f"Prix DPD : Non calculé : {resultats['dpd']['error']}")
                prix_dpd = float('inf')
            
            # Update Schenker palette results
            if not 'error' in resultats['schenker_palette']:
                prix_schenker_palette = float(resultats['schenker_palette']['prix'])
                self.result_labels['schenker_palette'].setText(f"Prix Schenker palette : {prix_schenker_palette:.2f}€")
            else:
                self.result_labels['schenker_palette'].setText(f"Prix Schenker palette : {resultats['schenker_palette']['error']}")
                prix_schenker_palette = float('inf')
            
            # Update Schenker messagerie results
            if not 'error' in resultats['schenker_messagerie']:
                prix_schenker_messagerie = float(resultats['schenker_messagerie']['prix'])
                self.result_labels['schenker_messagerie'].setText(f"Prix Schenker messagerie : {prix_schenker_messagerie:.2f}€")
            else:
                self.result_labels['schenker_messagerie'].setText(f"Prix Schenker messagerie : {resultats['schenker_messagerie']['error']}")
                prix_schenker_messagerie = float('inf')
            
            # Check if all calculations failed
            if all('error' in resultats[key] for key in ['dpd', 'schenker_messagerie', 'schenker_palette']):
                error_msg = "\n".join([
                    f"- {key}: {resultats[key]['error']}" 
                    for key in ['dpd', 'schenker_messagerie', 'schenker_palette']
                ])
                raise CalculationError(f"[ERROR] None could be calculated\n{error_msg}")
            
            # Update DPD arrangement display
            dpd_arrangement_string = "Arrangement des colis DPD : \n"
            if "error" not in resultats['dpd']:
                for i, masses in enumerate(resultats['dpd']['arrangement (masses)']):
                    dpd_arrangement_string += f"{resultats['dpd']['masses colis'][i]:2f}kg ({resultats['dpd']['prix_colis'][i]}€) :\n"
                    for j, mass in enumerate(masses):
                        if self.input_format == 'raw':
                            dpd_arrangement_string += f"\t{mass} kg\n"
                        else:
                            dpd_arrangement_string += f"\t{resultats['dpd']['arrangement (labels)'][i][j]} ({mass} kg)\n"
            
            self.result_labels['dpd_arrangement'].setText(dpd_arrangement_string)
            
            # Highlight best price
            min_prix = min(prix_dpd, prix_schenker_messagerie, prix_schenker_palette)
            self._update_price_highlights(min_prix, prix_dpd, prix_schenker_messagerie, prix_schenker_palette)
            
            # Update basket display
            panier = self.create_shopping_cart()
            panier = self.calculator.compact_shopping_cart(panier)
            if len(panier) < 10:
                label_articles = "\n".join([f"{article['poids']}kg --> {article['nom']}" for article in panier])
            else:
                label_articles = "\n".join([f"{article['poids']}kg --> {article['nom']}" for article in panier[:10]])
                label_articles += "\n ..."
            self.result_labels['basket'].setText(f"Panier : \n{label_articles}")
            
            print("Finished handling results")
        except Exception as e:
            print("Error handling results:", str(e))
            self._handle_calculation_error(str(e))

    def _handle_calculation_error(self, error_msg):
        """Handle calculation errors"""
        self.hide_loading_overlay()
        raise CalculationError(error_msg)

    def _handle_warning(self, message):
        """Handle warnings from the calculator thread"""
        self.hide_loading_overlay()
        
        # Store the current application stylesheet
        current_stylesheet = QApplication.instance().styleSheet()
        
        # Temporarily remove application stylesheet
        QApplication.instance().setStyleSheet("")
        
        # Create message box
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle('Attention')
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        
        # Show dialog and get response
        qm_result = msg_box.exec_()
        
        # Restore application stylesheet
        QApplication.instance().setStyleSheet(current_stylesheet)
        
        # Send response back to thread
        self.calc_thread.warning_response = (qm_result == QMessageBox.Yes)
        
        if qm_result == QMessageBox.Yes:
            self.show_loading_overlay()

    def _update_price_highlights(self, min_prix, prix_dpd, prix_schenker_messagerie, prix_schenker_palette):
        """Update the highlighting of prices"""
        # Reset colors
        for label in ['dpd_results', 'dpd_arrangement', 'schenker_palette', 'schenker_messagerie']:
            self.result_labels[label].setStyleSheet("")
        
        # Highlight lowest price
        red_style = "color: red;"
        if min_prix == prix_dpd:
            self.result_labels['dpd_results'].setStyleSheet(red_style)
            self.result_labels['dpd_arrangement'].setStyleSheet(red_style)
        elif min_prix == prix_schenker_palette:
            self.result_labels['schenker_palette'].setStyleSheet(red_style)
        else:
            self.result_labels['schenker_messagerie'].setStyleSheet(red_style)
    

def initialize_qt_interface(calculator) -> None:
    """Initialize and run the Qt application"""
    app = QApplication(sys.argv)
    window = ShippingCalculator(calculator)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    # For testing purposes only
    class DummyCalculator:
        def calculate(self, *args): pass
    initialize_qt_interface(DummyCalculator())