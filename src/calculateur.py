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

from itertools import combinations

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
        
        def tarif_par_masse(masse, tarif_par_kg):
            if masse in tarif_par_kg:
                return tarif_par_kg[masse]
            else:
                return tarif_par_kg[max(tarif_par_kg.keys())]

        def optimiser_colis(items, max_weight, tarif_par_kg):
            n = len(items)
            items = sorted(items, reverse=True)
            dp = {}

            def solve(remaining_items):
                if not remaining_items:
                    return 0, []
                key = tuple(sorted(remaining_items))
                if key in dp:
                    return dp[key]
                
                min_cost = float('inf')
                best_combination = []

                for i in range(1, len(remaining_items) + 1):
                    for subset in combinations(remaining_items, i):
                        if sum(subset) <= max_weight:
                            cost_colis = tarif_par_masse(sum(subset), tarif_par_kg)
                            remaining = list(remaining_items)
                            for item in subset:
                                remaining.remove(item)
                            
                            cost_remaining, combination = solve(remaining)
                            total_cost = cost_colis + cost_remaining

                            if total_cost < min_cost:
                                min_cost = total_cost
                                best_combination = [list(subset)] + combination
                
                dp[key] = (min_cost, best_combination)
                return dp[key]

            total_cost, colis = solve(items)
            return total_cost, colis

        poids_articles = [article['poids'] for article in panier]
        tarif_par_kg = self.tarifs
        max_weight = POIDS_MAX_COLIS_DPD
        total_cost, colis = optimiser_colis(poids_articles, max_weight, tarif_par_kg)
        if self.VERBOSE:
            print(f"[INFO]Total cost for DPD: {total_cost}€")
            print(f"[INFO]Colis distribution: {colis}")
        return total_cost
    
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