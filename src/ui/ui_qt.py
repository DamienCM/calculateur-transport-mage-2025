"""
Shipping Calculator UI - A PyQt5 application for calculating shipping costs.
"""
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QMenu,
    QAction, QMessageBox, QComboBox, QSpinBox, QFormLayout,
    QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QColor, QIcon
from ui.article_entry import ArticleEntry
from ui.styles import StyleConstants
from ui.loading_overlay import LoadingOverlay
from models.calculation_errors import CalculationError
from models.calculator_thread import CalculatorThread

from utils.utils import read_csv_file_with_headers


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
        self.articles_headers, self.articles_structure, self.articles_list, = self._load_articles_list()
        self.country_list = self._load_country_list()
        self.entries_layout = None
        
        self.init_ui()
        self.apply_styles()
        
    def _load_articles_list(self) -> List[Dict[str, Any]]:
        """Load articles list from CSV file"""
        

        header, columns_labels, csv = read_csv_file_with_headers(self.PATH_ARTICLES_LIST)
        id_list = list(range(len(csv[columns_labels[0]])))
        columns_labels.insert(0,"id")
        csv['id'] = id_list
        try:
            pass
            # with open(self.PATH_ARTICLES_LIST) as f:
            #     # Skip first two rows
            #     lines = f.readlines()[2:]
            #     for index, line in enumerate(lines):
            #         line_splitted = line.split(',')
            #         article = {"id": index}
            #         for el, label in zip(line_splitted, csv_structure):
            #             article[label] = el.strip()
            #         articles_list.append(article)
                
            # print(f"Articles list loaded successfully: {len(articles_list)} items")
            # return articles_list
            
        except FileNotFoundError as e:
            print(f"Error: Could not find articles list file: {e}")
            return []
        except Exception as e:
            print(f"Error loading articles list: {e}")
            print(e.__traceback__())
            return []
        return header, columns_labels, csv
    
    def _load_country_list(self) -> List[str]:
        """Load articles list from CSV file"""
        country_list = []

        try:
            header, columns_labels, csv = read_csv_file_with_headers(self.PATH_COUNTRY_LIST)
            # with open(self.PATH_COUNTRY_LIST) as f:
            #     # Skip first two rows
            #     lines = f.readlines()[2:]
            #     for line in lines:
            #         country = line.strip()
            #         country_list.append(country)
                
            # print(f"Country list loaded successfully: {len(country_list)} countries")

            return csv[columns_labels[0]]
            
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
                         'd.cartier-millon@mage-application'
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
            qt_label = QLabel("Poids de l'article (kg):")
            entry = QLineEdit()
            entry.setPlaceholderText("Entrez le poids")
            
            layout.addWidget(qt_label)
            layout.addWidget(entry, 1)  # Give entry more stretch
            
            result = {'entry': entry}
            
        else:  # ref or designation modes
            # Reference or designation mode
            qt_label = QLabel("Article:")
            combobox = QComboBox()
            # field = 'Ref' if self.input_format == 'ref' else 'Designation'
            # combobox.addItems([f"{article['id']}. {article[field]}" for article in self.articles_list])
            # Try to find input_format in headers 
            index = None 
            for col_label in self.articles_structure:
                if self.input_format in col_label:
                    index = self.articles_structure.index(col_label)

            if index is not None:
                # input format found 
                article_list = [f"{self.articles_list[self.articles_structure[0]][i]}. {self.articles_list[self.articles_structure[index]][i]}" for i in range(len(self.articles_list[self.articles_structure[0]]))]
                print(f"[INFO] Article list = {article_list}")
                combobox.addItems(article_list)
            else: # Defaulting to index col 0 + 1 (inserted id col) for ref 
                if self.input_format == 'ref':
                    article_list = [f"{self.articles_list[self.articles_structure[0]][i]}. {self.articles_list[self.articles_structure[0]][i]}" for i in range(len(self.articles_list[self.articles_structure[0]]))]
                    combobox.addItems(article_list)
                elif self.input_format == 'designation':
                    article_list = [f"{self.articles_list[self.articles_structure[0]][i]}. {self.articles_list[self.articles_structure[1]][i]}" for i in range(len(self.articles_list[self.articles_structure[0]]))]
                    combobox.addItems(article_list)

            label_qty = QLabel("Quantité:")
            qty_box = QSpinBox()
            qty_box.setMinimum(1)
            qty_box.setMaximum(999)
            
            layout.addWidget(qt_label)
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
                    # for article in self.articles_list:
                    #     if article["id"]==article_id:
                    #         matching_weight=article["Masse (kg)"]
                    article_index = self.articles_list[self.articles_structure[0]].index(article_id)
                    for label in self.articles_structure:
                        if "masse" in label:
                            mass_col = self.articles_structure.index(label)
                        else :
                            mass_col = 5
                    matching_weight = self.articles_list[self.articles_structure[mass_col]][article_index]
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