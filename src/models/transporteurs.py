print("Loading numpy : ...")
import numpy as np
print("Loading numpy : DONE")
print("Loading utils : ...")
from utils.utils import partitions_count, tarif_par_masse,set_new_tarif
print("Loading utils : DONE")
print("Loading C : ...")
from bin.c import find_best_config as c_find_best_config
from bin.c import set_new_tarif as c_set_new_tarif
print("Loading C : DONE")
from utils.utils import read_csv_file_with_headers
from collections import Counter



class Transporteur:
    def __init__(self, nom, fichier_tarifs,options):
        self.VERBOSE = True
        self.warning_callback = None  # Add this to your class
        if self.VERBOSE:
            print(f"[INFO] Initializing {nom} : ...")
        self.nom = nom
        self.fichier_tarifs = fichier_tarifs
        self.options = dict(options)
        self.header, self.columns_labels, self.csv = self.charger_tarifs()
        self.available_countries = None
        self.charger_liste_pays_disponible()
        if self.VERBOSE:
            print(f"[INFO] Initializing {nom} : DONE")
            print(f"----------------------------------")

        def optimiser_colis(panier, max_weight, columns_labels, csv):
            initial_panier = panier[:]
            items = [float(article['poids']) for article in panier]
            items_label = [article["nom"] for article in panier]
            items,items_label = sort_and_permute(items,items_label)
            n = len(items)
            number_of_partitions = partitions_count(n)
            capture_message(f"[INFO] Compacting shopping cart while calculation is too expensive: Cart = {panier}")
    
            compacting_count = 0
            while number_of_partitions > self.options["SEUIL_WARNING_ITERATIONS"]:
                compacting_count+=1
                self.options['SEUIL_COMPACTAGE']+=1
                self.options['SEUIL_ARTICLE_LEGER']+=1
                panier_compact = self.compact_shopping_cart(panier)
                items = [float(article['poids']) for article in panier_compact]
                items_label = [article["nom"] for article in panier_compact]
                items,items_label = sort_and_permute(items,items_label)
                n = len(items)
                capture_message(f"[INFO] cart len {n}")
                number_of_partitions = partitions_count(n)
                if self.options['SEUIL_COMPACTAGE']>=self.options["POIDS_MAX_COLIS_DPD"] or self.options['SEUIL_ARTICLE_LEGER']>=self.options["POIDS_MAX_COLIS_DPD"]:
                    return {'error':'Cannot compact cart enough'}

            capture_message(f"[INFO] Cart have been compacted {compacting_count} times.")
            # Generates the set of all possible partitions
            # weights = list(tarif_par_kg[:,0])
            capture_message(f"{columns_labels=}")
            weights = csv[columns_labels[0]]
            prices = csv[columns_labels[1]]
            
            # prices = list(tarif_par_kg[:,1])
            # Trick to handle max weight : over max : price = inf
            set_new_tarif(weights,prices, max_weight)
            set_new_tarif(weights,prices, max_weight)
            try :
                result = find_best_config(items)
            except IndexError as e: 
                raise IndexError(f'[ERROR] Could not find best config on {items}. \n panier = {panier} \n  Initial panier ={initial_panier} \n items = {items} \n Error = {e}')
            best_price = result['price']
            best_config = result['config']
            # from best config retrieve corresponding labels 
            best_config_labels=[]
            for group in best_config:
                current_group_labels=[]
                for article in group:
                    if article not in items:
                        raise ValueError("Article not found")
                    current_group_labels.append(items_label[items.index(article)])
                best_config_labels.append(current_group_labels)
                    
            print(f"\t [INFO] C + python - price : {best_price}\n For config : {best_config}")

            if self.VERBOSE:
                print(f"\t[INFO] Minimum cost : {best_price}€")
                print(f"\t[INFO] Best partition : {best_config}")
                print("[INFO] Calculating tarif for DPD : DONE\n")
            return {
                "best_price":best_price,
                "best_config": best_config,
                "best_config_labels" : best_config_labels,
                "compacting_count" : compacting_count,
            } 
    



    def set_warning_callback(self, callback):
        self.warning_callback = callback
    
    def set_options(self,options):
        self.options = dict(options)

    def charger_tarifs(self):
        if self.VERBOSE:
            print(f"\t[INFO] Loading tarifs {self.nom} : ...")
        if self.fichier_tarifs not in [self.options["DPD_PATH"], self.options["SCHENKER_PALETTE_PATH"], self.options["SCHENKER_MESSAGERIE_PATH"]]:
            raise ValueError("Fichier tarifs invalide")
        header, columns_labels, csv = {},[],{}
        try :
            if self.nom == self.options["DPD"]:
                header, columns_labels, csv = read_csv_file_with_headers(self.fichier_tarifs,col_types=[int,float])
            if self.nom == self.options["SCHENKER_PALETTE"]:

                # with open(self.fichier_tarifs) as f:
                #     lignes = f.readlines()[2:]
                #     last_departement = None
                #     for ligne in lignes:
                #         departement,tarif1,tarif2,tarif3,tarif4,tarif5 = ligne.strip().split(',')
                #         departement = departement[0:2]
                #         if departement == last_departement:
                #             departement = departement + "_"
                #         tarifs[departement] = [float(tarif1), float(tarif2), float(tarif3), float(tarif4), float(tarif5)]
                #         last_departement = departement
                header, columns_labels, csv = read_csv_file_with_headers(self.fichier_tarifs,col_types=[str,float,float,float,float,float])
                last_departement = '00'
                for line_index in range(len(csv[columns_labels[0]])-1,-1,-1):
                    departement_complet = csv[columns_labels[0]][line_index]
                    departement_chiffres = departement_complet[0:2]
                    csv[columns_labels[0]][line_index] = departement_chiffres
                    # Two consecutives departemetn = localite speciale, on supprime 
                    if last_departement == departement_chiffres:
                        for key,value in csv.items():
                            value.pop(line_index+1)
                    last_departement = departement_chiffres
            elif self.nom == self.options["SCHENKER_MESSAGERIE"]:
                # with open(self.fichier_tarifs) as f:
                #     lignes = f.readlines()
                #     zone1 , zone2, zone3, zone4 = lignes[1].strip().split(':')[1].split(','), lignes[2].strip().split(':')[1].split(','), lignes[3].strip().split(':')[1].split(','), lignes[4].strip().split(':')[1].split(',')
                #     tarifs["zone1"], tarifs["zone2"], tarifs["zone3"], tarifs["zone4"] = zone1, zone2, zone3, zone4
                #     kgs =[]
                #     tarifs_zone1, tarifs_zone2, tarifs_zone3, tarifs_zone4 = [], [], [], []

                #     for ligne in lignes[6:]:
                #         kg, tarif_zone1, tarif_zone2, tarif_zone3, tarif_zone4 = ligne.strip().split(',')
                #         kgs.append(float(kg))
                #         tarifs_zone1.append(float(tarif_zone1))
                #         tarifs_zone2.append(float(tarif_zone2))
                #         tarifs_zone3.append(float(tarif_zone3))
                #         tarifs_zone4.append(float(tarif_zone4))
                #     tarifs["kgs"] = kgs
                #     tarifs["tarifs_zone1"] = tarifs_zone1
                #     tarifs["tarifs_zone2"] = tarifs_zone2
                #     tarifs["tarifs_zone3"] = tarifs_zone3
                #     tarifs["tarifs_zone4"] = tarifs_zone4
                header, columns_labels, csv = read_csv_file_with_headers(self.fichier_tarifs,col_types=[int,float,float,float,float],list_in_header=True)

        except FileNotFoundError as e :
            print(f"Erreur lors de l'initiallisation des tarifs...\n{e}")
            print("Appuyer sur entree pour terminer le programme...")
            _ = input()
        if self.VERBOSE:
            print(f"\t[INFO] Loading tarifs {self.nom} : DONE\n")
        return header, columns_labels, csv

    def charger_liste_pays_disponible(self):
        try :
            if self.VERBOSE:
                print('\t[INFO] Loading country list : ...')

            # with open(self.options["COUNTRY_AVAILABLE_PATH"]) as f: 
            #     lines = f.readlines()
            #     columns = [ c.strip().lower() for c in lines[0].strip().split(",")]
            #     if self.nom not in columns:
            #         raise ValueError(f"{self.nom} not a column in {self.options['COUNTRY_AVAILABLE_PATH']} ")
            #     csv_data = {  c.strip().lower():[] for c in columns }
            #     #skip header
            #     lines = lines[2:]
            #     for line in lines :
            #         line_cells = line.strip().split(',')
            #         for row_index, cell_content in enumerate(line_cells):
            #             csv_data[columns[row_index]].append(cell_content.strip().lower())
            header, col_label, csv = read_csv_file_with_headers(self.options["COUNTRY_AVAILABLE_PATH"])
            self.available_countries = csv[col_label[col_label.index(self.nom)]]
            if self.VERBOSE:
                print('\t[INFO] Loading country list : DONE')   
                print(f'\t[INFO] Country List : {self.available_countries}')   
        except Exception as e:
            print(f"[ERROR] Unhandled error during loading of country list : {e}")
            return -1     
        return 0
    
    def is_country_available(self, country):
        try :
            if country.lower().strip() in self.available_countries:
                return True
            else :
                return False
        except Exception as e:
            print(f"[ERROR] Unhandled error during checking of available country : {e}")
            return -1
        

    def calculer_tarif(self, panier, options):

        if self.is_country_available(options["country"]):
            if self.nom == self.options["DPD"]:
                ret =  self.calculer_tarif_dpd(panier, options)
            elif self.nom == self.options["SCHENKER_PALETTE"]:
                ret = self.calculer_tarif_schenker_palette(panier, options)
            elif self.nom == self.options["SCHENKER_MESSAGERIE"]:
                ret = self.calculer_tarif_schenker_messagerie(panier, options)
            else:
                ret = {'error': "Unknown name"}
            if ret is not None :
                return ret 
            else : 
                ret = {"error" : "cannot calculate"}
        else :
            return {'error' : "Country not available"}
    
    def calculer_tarif_dpd(self, panier, options):
        if self.VERBOSE:
            print("[INFO] Calculating tarif for DPD : ...")
        departement = options['departement']
        # Check if the weight of an article is greater than the maximum weight of the colis
        for element in panier:
            if element['poids'] >= self.options["POIDS_MAX_COLIS_DPD"]:
                if self.VERBOSE:
                    print(f"\t[ERROR] Poids de l'article {element['nom']} superieur au poids maximum du colis")
                    print(f"\t[ERROR] Poids de l'article {element['nom']} : {element['poids']} kg")
                    print("\t[WARNING] Calculating tarif for DPD : ERROR")
                    return {'error' : 'excessive mass'}
        
        def sort_and_permute(list1, list2):
            # Combine both lists into a list of tuples
            combined = list(zip(list1, list2))
            
            # Sort the combined list based on the first list
            combined_sorted = sorted(combined, key=lambda x: x[0])
            
            # Unzip the combined sorted list back into two lists
            sorted_list1, permuted_list2 = zip(*combined_sorted)
            
            # Convert the result back to lists (since zip returns tuples)
            return list(sorted_list1), list(permuted_list2)
        
        def optimiser_colis(items, items_label, max_weight, columns_labels,csv):
            items,items_label = sort_and_permute(items,items_label)
            n = len(items)
            number_of_partitions = partitions_count(n)
            if self.VERBOSE:
                print("\t[INFO] Optimizing colis arrangement...")
                print(f"\t[INFO] Number of partitions : {number_of_partitions}")
            if number_of_partitions > self.options["SEUIL_WARNING_ITERATIONS"]:
                if self.VERBOSE:
                    print(f"\t[WARNING] Number of partitions : {number_of_partitions}")
                    print(f"\t[WARNING] This may take a while...")
                try :
                    message = f"Le calcul peut etre long pour DPD. Temps estimé supérieur à : {3e-6*number_of_partitions:.2f}s.\n Voulez vous proceder ?"
                    should_continue = self.warning_callback(message)
                    if not should_continue:
                        print("\t[INFO] Prompt response : No. Aborting DPD calculation.")
                        return float('inf'),None
                    print("\t[INFO] Prompt response : OK. Continuing calculation.")
                except Exception as e: 
                    print(e)
            # Generates the set of all possible partitions
            # weights = list(tarif_par_kg[:,0])
            print(f"{columns_labels=}")
            weights = csv[columns_labels[0]]
            prices = csv[columns_labels[1]]
            
            # prices = list(tarif_par_kg[:,1])
            # Trick to handle max weight : over max : price = inf
            c_set_new_tarif(weights,prices, max_weight)
            set_new_tarif(weights,prices, max_weight)
            result = c_find_best_config(items)
            best_price = result['price']
            if best_price > 10_000:
                return {'error','best_price > 10 000euros'}
            best_config = result['config']
            # from best config retrieve corresponding labels 
            best_config_labels=[]
            for group in best_config:
                current_group_labels=[]
                for article in group:
                    if article not in items:
                        raise ValueError("Article not found")
                    current_group_labels.append(items_label[items.index(article)])
                best_config_labels.append(current_group_labels)
                    
            print(f"\t [INFO] C + python - price : {best_price}\n For config : {best_config}")

            if self.VERBOSE:
                print(f"\t[INFO] Minimum cost : {best_price}€")
                print(f"\t[INFO] Best partition : {best_config}")
                print("[INFO] Calculating tarif for DPD : DONE\n")
            return best_price, (best_config,best_config_labels)

        poids_articles = [article['poids'] for article in panier]
        nom_articles = [article["nom"] for article in panier]

        total_cost, colis = optimiser_colis(poids_articles, nom_articles, self.options["POIDS_MAX_COLIS_DPD"], self.columns_labels, self.csv)
        if colis is not None:
            colis_masses, colis_labels = colis
            prix_colis = [ tarif_par_masse(sum(colis)) for colis in colis_masses ]
            total_masses_colis = [ sum(colis) for colis in colis_masses ]
            if self.VERBOSE:
                print(f"\t[INFO] Total cost for DPD: {total_cost}€")
                print(f"\t[INFO] Colis distribution: {colis_masses}")
                print(f"\t[INFO] Colis distribution: {colis_labels}")
            
            return {"prix": total_cost,
                    "arrangement (masses)":colis_masses,
                    "arrangement (labels)": colis_labels,
                    "prix_colis":prix_colis,
                        "masses colis":total_masses_colis}
        else :
            if self.VERBOSE:
                print(f"\t[INFO] Total cost for DPD: NOT CALCULATED")
                print(f"\t[INFO] Colis distribution: NOT CALCULATED")
                print(f"\t[INFO] Colis distribution: NOT CALCULATED")     
            return {'error': 'colis is None'}     
    
    def calculer_tarif_schenker_palette(self, panier, options, nbre_palette = 1, verbose=False):
        poids_total = 0
        if self.VERBOSE:
            print("[INFO] Calculating tarif for Schenker palette : ...")
        departement = options['departement']
        for article in panier:
            poids_total += article['poids']
        if self.VERBOSE:
            print("\t[INFO] Poids total", poids_total)
        if poids_total <= self.options["SEUIL_PALETTE_SCHENKER_MESSAGERIE"]:
            if self.VERBOSE:
                print("\t[WARNING] Poids total inferieur au seuil de palette")
                print(f"\t[INFO] Poids total {poids_total} kg.")

        if len(departement) == 1:
            departement = "0" + departement
        if len(departement)==2 and departement[-1]=="_":
            departement = "0" + departement
        if self.VERBOSE:
            print("\t[INFO] Departement ", departement)
        # indentifying tarifs corresponding to departement
        dpt_list = self.csv[self.columns_labels[0]]
        # print(f"\t[INFO]{dpt_list}")
        try:
            index_dpt = dpt_list.index(departement)
        except:
            print(f"[ERROR] Departement {departement} not on list {dpt_list}")
            raise ValueError(f"[ERROR] Departement {departement} not on list {dpt_list}")
        print(f"\t[INFO]{index_dpt=}")
        tarifs_dpt = [ self.csv[col_label][index_dpt] for col_label in self.columns_labels[1:]]
        print(f"\t[INFO]{tarifs_dpt=}")
        if self.VERBOSE:
            print("\t[INFO] Tarifs du departement ", tarifs_dpt)
        # identifying tarif for the matching nbre_palette
        try :
            tarif = tarifs_dpt[nbre_palette-1]
            if self.VERBOSE:
                print(f"\t[INFO] Tarif pour {nbre_palette} palettes : {tarif}€")
                print(f"[INFO] Calculating tarif for Schenker palette : DONE\n")
            return {"prix" : tarif}
        except IndexError:
            print("[ERROR] Nombre de palettes invalide\n")
            return {'error':"[ERROR] Nombre de palettes invalide"}
            
    def calculer_tarif_schenker_messagerie(self, panier, options):
        if self.VERBOSE:
            print("[INFO] Calculating tarif for Schenker messagerie : ...")
        departement = options['departement']
        
        tarif = 0
        poids_total = 0
        for article in panier:
            poids_total += article['poids']
        if not (poids_total > self.options["POIDS_MAX_COLIS_DPD"]  and poids_total <= self.options["SEUIL_PALETTE_SCHENKER_MESSAGERIE"]):
            if self.VERBOSE:
                print(f"\t[WARNING] Poids total {poids_total} kg. Poids doit etre compris entre {self.options['POIDS_MAX_COLIS_DPD']} et {self.options['SEUIL_PALETTE_SCHENKER_MESSAGERIE']} kg") 
        if self.VERBOSE:
            print("\t[INFO] Poids total :", poids_total)
        # identifying the corresponding zone for the departement
        if len(departement) == 1:
            departement = "0" + departement
        elif len(departement)==2 and departement[-1]=="_":
            departement = "0" + departement
        if departement[-1] == "_":
            if self.VERBOSE:
                print("\t[INFO] Departement zone speciale (corse monaco ou station) TO BE DONE :", departement)
                print("\t[INFO] Calculating tarif for Schenker messagerie : NOT VALID YET")
            return {"error":"localite speciale non gerees pour le moment"}
        # if departement in self.csv["zone1"]:
        #     zone = 1
        # elif departement in self.csv["zone2"]:
        #     zone = 2
        # elif departement in self.csv["zone3"]:
        #     zone = 3
        # elif departement in self.csv["zone4"]:
        #     zone = 4
        zone = None
        for key,value in self.header.items():
            if key.startswith('zone') and type(value) == list:
                if departement in value:
                    zone = key
                    break
        

        if zone is None:
            if self.VERBOSE:
                print("\t[INFO] Departement invalide :", departement)
                print("[INFO] Calculating tarif for Schenker messagerie : ERROR")
            raise ValueError("Departement invalide")
        
        tarif_zone = self.csv[zone]
        kgs = self.csv[self.columns_labels[0]]

        if self.VERBOSE:
            print("\t[INFO] Zone ", zone)
            print(f"\t[INFO] Tarif zone {zone} : ", tarif_zone)
        if poids_total < self.options["SEUIL_PRIX_AU_KG_MESSAGERIE_SCHENKER"]:
            # calculating the tarif
            if self.VERBOSE:
                print(f'\t[INFO] Tarification par tranches (>{self.options["SEUIL_PRIX_AU_KG_MESSAGERIE_SCHENKER"]} kg)')
            for i in range(len(kgs)):
                if poids_total <= kgs[i]:
                    tarif = tarif_zone[i]
                    if self.VERBOSE:
                        print(f"\t[INFO] Tarif pour {poids_total} kg : {tarif}€")
                        print(f"[INFO] Calculating tarif for Schenker messagerie : DONE\n")
                    return {"prix" : tarif}
        else :
            if poids_total>self.options["MAX_POIDS_MESSAGERIE_SCHENKER"]:
                if self.VERBOSE:
                    print(f'\t[ERROR] Poids total {poids_total} kg. Poids doit etre inferieur a {self.options["MAX_POIDS_MESSAGERIE_SCHENKER"]} kg')
                    print("[ERROR] Calculating tarif for Schenker messagerie : poids total trop eleve\n")
                return {"error": "Poids total trop eleve"}
            else:
                if self.VERBOSE:
                    print(f"\t[INFO] Tarification par tranche de 100 kg")
                for i in range(len(kgs)):
                    if poids_total <= kgs[i]:
                        tarif_aux_100kg = tarif_zone[i]
                        if self.VERBOSE:
                            print(f"\t[INFO] Tarif aux 100 kg : {tarif_aux_100kg}€ pour {poids_total//100} tranches de 100 kg")
                        tarif = tarif_aux_100kg * (poids_total//100)
                        if self.VERBOSE:
                            print(f"\t[INFO] Tarif pour {poids_total} kg : {tarif}€")
                            print(f"[INFO] Calculating tarif for Schenker messagerie : DONE\n")
                        return {"prix" : tarif}