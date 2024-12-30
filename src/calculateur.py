DPD_PATH = '../data/dpd.csv'
SCHENKER_PALETTE_PATH = '../data/schenker_palette.csv'
SCHENKER_MESSAGERIE_PATH = '../data/schenker_messagerie.csv'

DPD = 'dpd'
SCHENKER_PALETTE = 'schenker_palette'
SCHENKER_MESSAGERIE = 'schenker_messagerie'

POIDS_MAX_COLIS_DPD = 30 # kg
SEUIL_PALETTE_SCHENKER_MESSAGERIE = 200 # kg
# SEUIL_PALETTE_SCHENKER_MESSAGERIE = 200 # kg
SEUIL_PRIX_AU_KG_MESSAGERIE_SCHENKER = 100 # kg
MAX_POIDS_MESSAGERIE_SCHENKER = 1000 # kg
SEUIL_WARNING_ITERATIONS = 10000

import timeit
from itertools import combinations
from tqdm import tqdm
import numpy as np

from utils import partitions_count, partitions_list_numpy, partitions_array, partitions_list

class CalculateurFraisLivraison:
    def __init__(self):
        self.transporteurs = {
            'dpd': Transporteur(DPD, DPD_PATH),
            'schenker_palette': Transporteur(SCHENKER_PALETTE, SCHENKER_PALETTE_PATH),
            'schenker_messagerie': Transporteur(SCHENKER_MESSAGERIE, SCHENKER_MESSAGERIE_PATH)
        }

    def calculer(self, panier, departement):
        resultats = {}
        for nom, transporteur in self.transporteurs.items():
            tarif = transporteur.calculer_tarif(panier, departement)
            if tarif is not None:
                resultats[nom] = tarif
        return resultats


class Transporteur:
    def __init__(self, nom, fichier_tarifs):
        self.VERBOSE = True
        if self.VERBOSE:
            print(f"[INFO]Initializing {nom} : ...")
        self.nom = nom
        self.fichier_tarifs = fichier_tarifs
        self.tarifs = self.charger_tarifs()
        if self.VERBOSE:
            print(f"[INFO]Initializing {nom} : DONE")
            print(f"----------------------------------")

    def charger_tarifs(self):
        if self.VERBOSE:
            print(f"\t[INFO]Loading tarifs {self.nom} : ...")
        if self.fichier_tarifs not in [DPD_PATH, SCHENKER_PALETTE_PATH, SCHENKER_MESSAGERIE_PATH]:
            raise ValueError("Fichier tarifs invalide")
        tarifs = {}
        if self.nom == DPD:
            with open(self.fichier_tarifs) as f:
                # Ignorer les deux premières lignes
                lignes = f.readlines()[2:]
                for ligne in lignes:
                    poids, tarif = ligne.strip().split(',')
                    tarifs[float(poids)] = float(tarif)
        elif self.nom == SCHENKER_PALETTE:
            with open(self.fichier_tarifs) as f:
                lignes = f.readlines()[2:]
                last_departement = None
                for ligne in lignes:
                    departement,tarif1,tarif2,tarif3,tarif4,tarif5 = ligne.strip().split(',')
                    departement = departement[0:2]
                    if departement == last_departement:
                        departement = departement + "_"
                    tarifs[departement] = [float(tarif1), float(tarif2), float(tarif3), float(tarif4), float(tarif5)]
                    last_departement = departement
        elif self.nom == SCHENKER_MESSAGERIE:
            with open(self.fichier_tarifs) as f:
                lignes = f.readlines()
                zone1 , zone2, zone3, zone4 = lignes[1].strip().split(':')[1].split(','), lignes[2].strip().split(':')[1].split(','), lignes[3].strip().split(':')[1].split(','), lignes[4].strip().split(':')[1].split(',')
                tarifs["zone1"], tarifs["zone2"], tarifs["zone3"], tarifs["zone4"] = zone1, zone2, zone3, zone4
                kgs =[]
                tarifs_zone1, tarifs_zone2, tarifs_zone3, tarifs_zone4 = [], [], [], []

                for ligne in lignes[6:]:
                    kg, tarif_zone1, tarif_zone2, tarif_zone3, tarif_zone4 = ligne.strip().split(',')
                    kgs.append(float(kg))
                    tarifs_zone1.append(float(tarif_zone1))
                    tarifs_zone2.append(float(tarif_zone2))
                    tarifs_zone3.append(float(tarif_zone3))
                    tarifs_zone4.append(float(tarif_zone4))
                tarifs["kgs"] = kgs
                tarifs["tarifs_zone1"] = tarifs_zone1
                tarifs["tarifs_zone2"] = tarifs_zone2
                tarifs["tarifs_zone3"] = tarifs_zone3
                tarifs["tarifs_zone4"] = tarifs_zone4
        if self.VERBOSE:
            print(f"\t[INFO]Loading tarifs {self.nom} : DONE\n")
        return tarifs

    def calculer_tarif(self, panier, departement):
        if self.nom == DPD:
            return self.calculer_tarif_dpd(panier, departement)
        elif self.nom == SCHENKER_PALETTE:
            return self.calculer_tarif_schenker_palette(panier, departement)
        elif self.nom == SCHENKER_MESSAGERIE:
            return self.calculer_tarif_schenker_messagerie(panier, departement)
        else:
            return None
    
    def calculer_tarif_dpd(self, panier, departement):
        if self.VERBOSE:
            print("[INFO]Calculating tarif for DPD : ...")
        
        # Check if the weight of an article is greater than the maximum weight of the colis
        for element in panier:
            if element['poids'] > POIDS_MAX_COLIS_DPD:
                if self.VERBOSE:
                    print(f"\t[ERROR]Poids de l'article {element['nom']} superieur au poids maximum du colis")
                    print(f"\t[ERROR]Poids de l'article {element['nom']} : {element['poids']} kg")
                    print("[WARNING]Calculating tarif for DPD : ERROR")
                    return {"prix": "ERROR","arrangement":"ERROR"}

        def tarif_par_masse(masse, tarif_par_kg):
            if masse in tarif_par_kg:
                return tarif_par_kg[masse]
            else:
                return tarif_par_kg[max(tarif_par_kg.keys())]
            

        def optimiser_colis(items, max_weight, tarif_par_kg):
            items = sorted(items, reverse=True)
            n = len(items)
            number_of_partitions = partitions_count(n)

            if self.VERBOSE:
                print("\t[INFO]Optimizing colis arrangement...")
                print(f"\t[INFO]Number of partitions : {number_of_partitions}")
            if number_of_partitions > SEUIL_WARNING_ITERATIONS:
                if self.VERBOSE:
                    print(f"\t[WARNING]Number of partitions : {number_of_partitions}")
                    print(f"\t[WARNING]This may take a while...")
            # Generates the set of all possible partitions
            all_partitions = partitions_list(items)
            if self.VERBOSE:
                print(f"\t[INFO]List of partitions generated")
                if number_of_partitions <= 6 :
                    print(f"[INFO]Partitions : \n{all_partitions}")
                else:
                    # only prints the partitions_to_print first and last partitions
                    partitions_to_print = 5
                    print("\t[INFO]Partitions :")
                    for i in range(partitions_to_print):
                        print(f" {i+1}:") 
                        print(f"{all_partitions[i]}")
                    print("...")
                    for i in range(number_of_partitions-partitions_to_print, number_of_partitions):
                        print(f" {i+1}:")
                        print(f"{all_partitions[i]}")


            min_cost = float('inf')
            best_partition = None
            debug_list_main = []
            i=0
            for partition in tqdm(all_partitions, desc="Progress", disable=not self.VERBOSE):
            # for partition in all_partitions:
                # i+=1
                # debug_list_sub = []
                partition_cost = 0
                # if total weight of one of the partition elements is greater than the maximum weight of the colis, skip
                for subset in partition:
                    subset_weight = sum(subset)
                    if subset_weight>max_weight:
                        partition_cost = float('inf')
                        # print(f"skipped partition {i} because of subset {subset}, subset weight {subset_weight} > max weight {max_weight}")
                        # debug_list_sub.append(partition_cost)
                        break
                    tarif_subset = tarif_par_masse(subset_weight, tarif_par_kg)
                    # debug_list_sub.append(tarif_subset)
                    partition_cost += tarif_subset
                if partition_cost < min_cost:
                    min_cost = partition_cost
                    best_partition = partition
                # debug_list_main.append([i,f"prix des colis {debug_list_sub}", f"total prix partition : {sum(debug_list_sub)}"])
            if self.VERBOSE:
                # print(f"\t[INFO]Debug list :")
                # for i in range(len(debug_list_main)):
                    # print(f"\t{debug_list_main[i]}")
                print(f"\t[INFO]Minimum cost : {min_cost}€")
                print(f"\t[INFO]Best partition : {best_partition}")
                print("[INFO]Calculating tarif for DPD : DONE\n")
            return min_cost, best_partition



        poids_articles = [article['poids'] for article in panier]

        total_cost, colis = optimiser_colis(poids_articles, POIDS_MAX_COLIS_DPD, self.tarifs)
        if self.VERBOSE:
            print(f"[INFO]Total cost for DPD: {total_cost}€")
            print(f"[INFO]Colis distribution: {colis}")
        
        return {"prix": total_cost,"arrangement":colis}
    
    def calculer_tarif_schenker_palette(self, panier, departement, nbre_palette = 1, verbose=False):
        poids_total = 0
        if self.VERBOSE:
            print("[INFO]Calculating tarif for Schenker palette : ...")
        for article in panier:
            poids_total += article['poids']
        if self.VERBOSE:
            print("\t[INFO]Poids total", poids_total)
        if poids_total <= SEUIL_PALETTE_SCHENKER_MESSAGERIE:
            if self.VERBOSE:
                print("\t[WARNING] Poids total inferieur au seuil de palette")
                print(f"\t[INFO]Poids total {poids_total} kg.")

        if len(departement) == 1:
            departement = "0" + departement
        if len(departement)==2 and departement[-1]=="_":
            departement = "0" + departement
        if self.VERBOSE:
            print("\t[INFO]Departement", departement)
        # indentifying tarifs corresponding to departement
        tarifs_dpt = self.tarifs[departement]
        if self.VERBOSE:
            print("\t[INFO]Tarifs du departement ", tarifs_dpt)
        # identifying tarif for the matching nbre_palette
        try :
            tarif = tarifs_dpt[nbre_palette-1]
            if self.VERBOSE:
                print(f"\t[INFO]Tarif pour {nbre_palette} palettes : {tarif}€")
                print(f"[INFO]Calculating tarif for Schenker palette : DONE\n")
            return tarif
        except IndexError:
            print("[ERROR]Nombre de palettes invalide\n")
            return None
            
    def calculer_tarif_schenker_messagerie(self, panier, departement):
        if self.VERBOSE:
            print("[INFO]Calculating tarif for Schenker messagerie : ...")
        tarif = 0
        poids_total = 0
        for article in panier:
            poids_total += article['poids']
        if not (poids_total > POIDS_MAX_COLIS_DPD  and poids_total <= SEUIL_PALETTE_SCHENKER_MESSAGERIE):
            if self.VERBOSE:
                print(f"\t[WARNING] Poids total {poids_total} kg. Poids doit etre compris entre {POIDS_MAX_COLIS_DPD} et {SEUIL_PALETTE_SCHENKER_MESSAGERIE} kg") 
        if self.VERBOSE:
            print("\t[INFO]Poids total :", poids_total)
        # identifying the corresponding zone for the departement
        if len(departement) == 1:
            departement = "0" + departement
        elif len(departement)==2 and departement[-1]=="_":
            departement = "0" + departement
        if departement[-1] == "_":
            if self.VERBOSE:
                print("\t[INFO]Departement zone speciale (corse monaco ou station) TO BE DONE :", departement)
                print("\t[INFO]Calculating tarif for Schenker messagerie : NOT VALID YET")
            return None
        if departement in self.tarifs["zone1"]:
            zone = 1
        elif departement in self.tarifs["zone2"]:
            zone = 2
        elif departement in self.tarifs["zone3"]:
            zone = 3
        elif departement in self.tarifs["zone4"]:
            zone = 4
        else:
            if self.VERBOSE:
                print("\t[INFO]Departement invalide :", departement)
                print("[INFO]Calculating tarif for Schenker messagerie : ERROR")
            raise ValueError("Departement invalide")
        if self.VERBOSE:
            print("\t[INFO]Zone", zone)
            print(f"\t[INFO]Tarif zone {zone} : ", self.tarifs[f"tarifs_zone{zone}"])
        if poids_total < SEUIL_PRIX_AU_KG_MESSAGERIE_SCHENKER:
            # calculating the tarif
            if self.VERBOSE:
                print(f"\t[INFO]Tarification par tranches (>{SEUIL_PRIX_AU_KG_MESSAGERIE_SCHENKER} kg)")
            for i in range(len(self.tarifs["kgs"])):
                if poids_total <= self.tarifs["kgs"][i]:
                    tarif = self.tarifs[f"tarifs_zone{zone}"][i]
                    if self.VERBOSE:
                        print(f"\t[INFO]Tarif pour {poids_total} kg : {tarif}€")
                        print(f"[INFO]Calculating tarif for Schenker messagerie : DONE\n")
                    return tarif
        else :
            if poids_total>MAX_POIDS_MESSAGERIE_SCHENKER:
                if self.VERBOSE:
                    print(f"\t[ERROR]Poids total {poids_total} kg. Poids doit etre inferieur a {MAX_POIDS_MESSAGERIE_SCHENKER} kg")
                    print("[ERROR]Calculating tarif for Schenker messagerie : poids total trop eleve\n")
                return None
            else:
                if self.VERBOSE:
                    print(f"\t[INFO]Tarification par tranche de 100 kg")
                for i in range(len(self.tarifs["kgs"])):
                    if poids_total <= self.tarifs["kgs"][i]:
                        tarif_aux_100kg = self.tarifs[f"tarifs_zone{zone}"][i]
                        if self.VERBOSE:
                            print(f"\t[INFO]Tarif aux 100 kg : {tarif_aux_100kg}€ pour {poids_total//100} tranches de 100 kg")
                        tarif = tarif_aux_100kg * (poids_total//100)
                        if self.VERBOSE:
                            print(f"\t[INFO]Tarif pour {poids_total} kg : {tarif}€")
                            print(f"[INFO]Calculating tarif for Schenker messagerie : DONE\n")
                        return tarif
                    


if __name__ == "__main__":
    calculateur = CalculateurFraisLivraison()
    config = 1
    if config==1 :
        panier = [
            {"nom": "Article 1", "poids": 5},
            {"nom": "Article 2", "poids": 10},
            {"nom": "Article 3", "poids": 15},
            {"nom": "Article 4", "poids": 20},
            {"nom": "Article 5", "poids": 25},
            {"nom": "Article 6", "poids": 22},
            {"nom": "Article 7", "poids": 3},
            {"nom": "Article 8", "poids": 12},
            {"nom": "Article 9", "poids": 18},
            {"nom": "Article 10", "poids": 7},
            {"nom": "Article 11", "poids": 9},
            ]
        execution_time = timeit.timeit(lambda: calculateur.calculer(panier, "75"), number=5)
        print(f"Execution time: {execution_time:.2f} seconds")
    
    elif config==2:
        panier = [
            {"nom": "Article 1", "poids": 5},
            {"nom": "Article 2", "poids": 10},
            {"nom": "Article 3", "poids": 15},
        ]
        calculateur.calculer(panier, "75")