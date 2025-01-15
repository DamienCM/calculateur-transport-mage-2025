from dataclasses import dataclass



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
