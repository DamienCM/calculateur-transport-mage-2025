from typing import Dict, List
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QSpinBox
)




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
