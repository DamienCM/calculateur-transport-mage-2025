print("Loading Qt5 : ...")
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame,
                           QSpacerItem, QSizePolicy, QMenuBar, QMenu, QAction,
                           QMessageBox,QComboBox, QSpinBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
print("Loading Qt5 : DONE")
import sys
from collections import Counter

PATH_ARTICLES_LIST = "../data/items.csv"
SEUIL_COMPACTAGE = 2 #kg seuil des groupements d'articles legers 
SEUIL_ARTICLE_LEGER = 1#kg en dessosus on considere l'article comme leger

class ShippingCalculator(QMainWindow):
    def __init__(self, calculateur):
        super().__init__()
        self.calculateur = calculateur
        self.entry_id = 0
        self.entries = []
        self.input_format = 'raw'
        self.articlesList = self.loadArticlesList()
        self.initUI()
    


    def setup_input_panel(self):
        """Set up the left panel for article inputs"""
        self.input_frame = QFrame()
        self.input_frame.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.input_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.input_frame.setMinimumWidth(350)
        
        # Set up layout
        self.input_layout = QVBoxLayout(self.input_frame)
        self.input_layout.setSpacing(0)
        self.input_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create container for entries
        self.entries_container = QWidget()
        self.entries_layout = QVBoxLayout(self.entries_container)
        self.entries_layout.setSpacing(0)
        self.entries_layout.setContentsMargins(0, 0, 0, 0)
        self.input_layout.addWidget(self.entries_container)
        
        # Add vertical spacer
        self.input_layout.addStretch(1)
        
        # Add article button
        self.ajouter_article_button = QPushButton("Ajouter un article")
        self.ajouter_article_button.clicked.connect(self.ajouter_article)
        self.input_layout.addWidget(self.ajouter_article_button)
        
        # Add first article by default
        self.ajouter_article()
        
        return self.input_frame

    def setup_control_panel(self):
        """Set up the middle panel for controls and inputs"""
        self.button_frame = QFrame()
        self.button_frame.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.button_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.button_frame.setMinimumWidth(350)
        
        button_layout = QVBoxLayout(self.button_frame)
        button_layout.setSpacing(0)
        button_layout.setContentsMargins(10, 10, 10, 10)
        
        # Department input
        dept_widget = QWidget()
        dept_layout = QHBoxLayout(dept_widget)
        dept_layout.addWidget(QLabel("Département:"))
        self.departement_entry = QLineEdit()
        self.departement_entry.setMaximumWidth(150)
        dept_layout.addWidget(self.departement_entry)
        button_layout.addWidget(dept_widget)
        
        # DPD max weight input
        dpd_max_widget = QWidget()
        dpd_layout = QHBoxLayout(dpd_max_widget)
        dpd_layout.addWidget(QLabel("Poids max dpd (kg):"))
        self.dpd_max_entry = QLineEdit()
        self.dpd_max_entry.setMaximumWidth(150)
        dpd_layout.addWidget(self.dpd_max_entry)
        button_layout.addWidget(dpd_max_widget)
        
        # Small package threshold input
        threshold_widget = QWidget()
        threshold_layout = QHBoxLayout(threshold_widget)
        threshold_layout.addWidget(QLabel("Seuil petit colis (kg):"))
        self.threshold_entry = QLineEdit()
        self.threshold_entry.setMaximumWidth(150)
        threshold_layout.addWidget(self.threshold_entry)
        button_layout.addWidget(threshold_widget)
        
        # Calculate button
        self.calc_button = QPushButton("Calculer")
        self.calc_button.clicked.connect(self.calculer_frais)
        button_layout.addWidget(self.calc_button)
        
        return self.button_frame

    def setup_result_panel(self):
        """Set up the right panel for displaying results"""
        self.result_frame = QFrame()
        self.result_frame.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.result_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.result_frame.setMinimumWidth(350)
        
        result_layout = QVBoxLayout(self.result_frame)
        result_layout.setSpacing(0)
        result_layout.setContentsMargins(10, 10, 10, 10)
        
        # Result labels
        self.result_label = QLabel("Panier : \n")
        self.result_schenker_palette = QLabel("Prix Schenker palette : ")
        self.result_schenker_messagerie = QLabel("Prix Schenker messagerie: ")
        self.result_dpd = QLabel("Resultats dpd : ")
        self.arrangement_dpd = QLabel("Arrangement dpd : ")
        
        result_layout.addWidget(self.result_label)
        result_layout.addWidget(self.result_schenker_palette)
        result_layout.addWidget(self.result_schenker_messagerie)
        result_layout.addWidget(self.result_dpd)
        result_layout.addWidget(self.arrangement_dpd)
        
        return self.result_frame

    def initUI(self):
        """Initialize the main UI"""
        self.setWindowTitle('Calculateur de Frais de Livraison')
        self.setWindowIcon(QIcon('../icons/Logo-MAGE-Application.ico'))
        
        # Create menu bar
        self.createMenuBar()
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        
        # Set up the three panels
        input_frame = self.setup_input_panel()
        button_frame = self.setup_control_panel()
        result_frame = self.setup_result_panel()
        
        # Add frames to main layout with equal stretch
        main_layout.addWidget(input_frame, 1)
        main_layout.addWidget(button_frame, 1)
        main_layout.addWidget(result_frame, 1)
        
        self.setGeometry(200, 200, 1200, 500)   #Load the dropdown content 
    def loadArticlesList(self):
        articles_list = []
        csv_structure = ["Ref", "Nom", "Designation", "Prix", "Masse (kg)"]

        try :
            with open(PATH_ARTICLES_LIST) as f:
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
    def createMenuBar(self):
        # Create menu bar
        menubar = self.menuBar()
        
        # File menu
        fileMenu = menubar.addMenu('Fichier')
        
        # New action
        newAction = QAction('Nouveau', self)
        newAction.setShortcut('Ctrl+N')
        newAction.triggered.connect(self.newCalculation)
        fileMenu.addAction(newAction)
        
        # Save action
        saveAction = QAction('Sauvegarder', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.triggered.connect(self.saveCalculation)
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
        clearAction.triggered.connect(self.clearAll)
        editMenu.addAction(clearAction)
        # Changing input format
        switchMenu = editMenu.addMenu("Changer le mode d'entrée")
        rawInput = QAction('Entrees par masse des articles',self)
        rawInput.triggered.connect(lambda: self.switchInputFormat('raw'))
        refInput = QAction('Entrees par ref',self)
        refInput.triggered.connect(lambda: self.switchInputFormat('ref'))
        designationInput = QAction('Entrees par designation',self)
        designationInput.triggered.connect(lambda: self.switchInputFormat('designation'))
        switchMenu.addAction(rawInput)
        switchMenu.addAction(refInput)
        switchMenu.addAction(designationInput)
        
        # Help menu
        helpMenu = menubar.addMenu('Aide')
        
        # About action
        aboutAction = QAction('À propos', self)
        aboutAction.triggered.connect(self.showAbout)
        helpMenu.addAction(aboutAction)

    def newCalculation(self):
        """Clear all entries and start fresh"""
        reply = QMessageBox.question(self, 'Nouveau calcul', 
                                   'Voulez-vous vraiment effacer tous les champs ?',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.clearAll()
    
    def saveCalculation(self):
        """Placeholder for save functionality"""
        QMessageBox.information(self, 'Sauvegarde', 
                              'Fonctionnalité de sauvegarde à implémenter.')
    
    def clearAll(self):
        """Clear all entries and results"""
        # Clear department
        self.departement_entry.clear()
        
        # Clear all article entries
        while len(self.entries) > 0:
            entry_data = self.entries[0]
            entry_data['widget'].deleteLater()
            self.entries.pop(0)
        
        # Reset results
        self.result_label.setText("Resultats : \n")
        self.result_schenker_palette.setText("Prix Schenker palette : ")
        self.result_schenker_messagerie.setText("Prix Schenker messagerie: ")
        self.result_dpd.setText("Resultats dpd : ")
        self.arrangement_dpd.setText("Arrangement dpd : ")
        
        # Add back one empty article entry
        self.ajouter_article()
    
    def switchInputFormat(self,input_format):
        """ Switch input between raw and dropdown """
        #Switch envireonnment variable
        print(f"[INFO] Switching input format to : {input_format}")
        self.input_format = input_format
        
        self.clearAll()        

        return 0

    def showAbout(self):
        """Show about dialog"""
        QMessageBox.about(self, 'À propos',
                         'Calculateur de Frais de Livraison\n\n'
                         'Version 1.0\n'
                         '© 2024 MAGE')

    def ajouter_article(self):
        # selon le mode
        if self.input_format =="raw":
            self.entry_id += 1
            current_id = self.entry_id
            
            # Create widget for article entry
            article_widget = QWidget()
            layout = QHBoxLayout(article_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            
            label = QLabel(f"Poids de l'article (kg):")
            entry = QLineEdit()
            suppr_button = QPushButton("X")
            suppr_button.setFixedWidth(30)
            suppr_button.clicked.connect(lambda: self.supprimer_article(current_id))
            
            layout.addWidget(label)
            layout.addWidget(entry)
            layout.addWidget(suppr_button)
            
            # Add new article widget to the entries container
            self.entries_layout.addWidget(article_widget)
            
            self.entries.append({
                'widget': article_widget,
                'entry': entry,
                'id': current_id
            })
            entry.setFocus()
        
        elif self.input_format == 'ref':
            if self.articlesList is None or self.articlesList==[]:
                raise ValueError("Article list is empty (may have not been loaded correctly)")
            
            self.entry_id += 1
            current_id = self.entry_id
            
            # Create widget for article entry
            article_widget = QWidget()
            layout = QHBoxLayout(article_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            
            label = QLabel(f"Article:")
            combobox = QComboBox()
            combobox.addItems([f"{article['id']}. {article['Ref']}" for article in self.articlesList])

            label_qty = QLabel(f"Quantité:")

            qty_box = QSpinBox()

            suppr_button = QPushButton("X")
            suppr_button.setFixedWidth(30)
            suppr_button.clicked.connect(lambda: self.supprimer_article(current_id))
            
            layout.addWidget(label)
            layout.addWidget(combobox)
            layout.addWidget(label_qty)
            layout.addWidget(qty_box)

            layout.addWidget(suppr_button)
            
            # Add new article widget to the entries container
            self.entries_layout.addWidget(article_widget)
            
            self.entries.append({
                'widget': article_widget,
                'combobox': combobox,
                "qty_box" : qty_box,
                'id': current_id,
            })
        
        elif self.input_format == 'designation':
            if self.articlesList is None or self.articlesList==[]:
                raise ValueError("Article list is empty (may have not been loaded correctly)")
            
            self.entry_id += 1
            current_id = self.entry_id
            
            # Create widget for article entry
            article_widget = QWidget()
            layout = QHBoxLayout(article_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            
            label = QLabel(f"Article:")
            combobox = QComboBox()
            combobox.addItems([f"{article['id']}. {article['Designation']}" for article in self.articlesList])

            label_qty = QLabel(f"Quantité:")

            qty_box = QSpinBox()

            suppr_button = QPushButton("X")
            suppr_button.setFixedWidth(30)
            suppr_button.clicked.connect(lambda: self.supprimer_article(current_id))
            
            layout.addWidget(label)
            layout.addWidget(combobox)
            layout.addWidget(label_qty)
            layout.addWidget(qty_box)

            layout.addWidget(suppr_button)
            
            # Add new article widget to the entries container
            self.entries_layout.addWidget(article_widget)
            
            self.entries.append({
                'widget': article_widget,
                'combobox': combobox,
                "qty_box" : qty_box,
                'id': current_id,
            })
        
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
                    for article in self.articlesList:
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

    def compact_shopping_cart(self,panier):
        """ Tweaking method to reduce calculation time : regroup small articles """
        light_articles = []
        panier_sorted = []
        for article in panier :
            mass = float(article['poids'])
            if mass < SEUIL_ARTICLE_LEGER:
                light_articles.append(article)
            else :
                panier_sorted.append(article)
        current_group = []
        current_mass = 0
        light_groups = []
        for article in light_articles:
            current_group.append(article['nom'])
            current_mass += float(article['poids'])
            if current_mass > SEUIL_COMPACTAGE :
                counts = Counter(current_group)
                label = " + ".join([f"{count}x {key}" for key, count in counts.items()])
                light_groups.append({"nom":label, 'poids':current_mass})
                current_mass=0
                current_group=[]
        if current_mass>0:
            counts = Counter(current_group)
            label = " + ".join([f"{count}x {key}" for key, count in counts.items()])
            light_groups.append({"nom":label, 'poids':current_mass})
        

        panier = panier_sorted + light_groups
        print(f'[INFO] Panier compacted : \n {panier}')
        return panier

    def calculer_frais(self):
        try:
            panier = self.create_shopping_cart()
            if panier == []:
                print('[WARNING] Panier is empty ! ')
            
            panier = self.compact_shopping_cart(panier)
            if len(panier)<10:
                label_articles = "\n".join([f"{article['poids']}kg --> {article['nom']}" for article in panier])
            else :
                label_articles = "\n".join([f"{article['poids']}kg --> {article['nom']}" for article in panier[:10]])
                label_articles+="\n ..."

            departement = self.departement_entry.text()
            
            resultats = self.calculateur.calculer(panier, departement)
            if resultats['dpd'] is not None:
                prix_dpd = float(resultats['dpd']['prix'])
                self.result_dpd.setText(f"Prix dpd : {prix_dpd:.2f}€")
            else:
                self.result_dpd.setText(f"Prix DPD : Non calculé")
                

            prix_schenker_palette = float(resultats['schenker_palette'])
            prix_schenker_messagerie = float(resultats['schenker_messagerie'])
            

            dpd_arrangement_string = "Arrangement des colis DPD : \n"
            if resultats['dpd'] is not None:
                for i in range(len(resultats['dpd']['arrangement (masses)'])):
                    dpd_arrangement_string += f"{resultats['dpd']['masses colis'][i]}kg ({resultats['dpd']['prix_colis'][i]}€) :\n"
                    for j in range(len(resultats['dpd']['arrangement (masses)'][i])):
                        if self.input_format == 'raw': 
                            dpd_arrangement_string+=f"\t{resultats['dpd']['arrangement (masses)'][i][j]}\n"
                        else:
                            dpd_arrangement_string+=f"\t{resultats['dpd']['arrangement (labels)'][i][j]} ({resultats['dpd']['arrangement (masses)'][i][j]} kg)\n"
            else:
                dpd_arrangement_string+="Non calculé"

            self.arrangement_dpd.setText(dpd_arrangement_string)
            self.result_schenker_palette.setText(f"Prix Schenker palette : {prix_schenker_palette:.2f}€")
            self.result_schenker_messagerie.setText(f"Prix Schenker messagerie : {prix_schenker_messagerie:.2f}€")
            
            if resultats['dpd'] is not None:
                min_prix = min(prix_dpd, prix_schenker_palette, prix_schenker_messagerie)
            else:
                min_prix = min(prix_schenker_palette, prix_schenker_messagerie)
                
            self.result_label.setText(f"Panier : \n{label_articles}")
            
            # Reset colors
            self.result_dpd.setStyleSheet("")
            self.arrangement_dpd.setStyleSheet("")
            self.result_schenker_palette.setStyleSheet("")
            self.result_schenker_messagerie.setStyleSheet("")
            
            # Highlight lowest price in red
            red_style = "color: red;"
            if resultats['dpd'] is not None:
                if min_prix == prix_dpd:
                    self.result_dpd.setStyleSheet(red_style)
                    self.arrangement_dpd.setStyleSheet(red_style)
            elif min_prix == prix_schenker_palette:
                self.result_schenker_palette.setStyleSheet(red_style)
            else:
                self.result_schenker_messagerie.setStyleSheet(red_style)
                
        except ValueError as e:
            self.result_label.setText(f"Erreur: Veuillez entrer des poids valides : {e}")
        # except Exception as e:
        #     self.result_label.setText(f"Erreur: {e}")

def initialiser_interface_qt(calculateur):
    app = QApplication(sys.argv)
    window = ShippingCalculator(calculateur)
    window.show()
    sys.exit(app.exec_())