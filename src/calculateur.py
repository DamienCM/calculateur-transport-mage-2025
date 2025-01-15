from collections import Counter
from models.transporteurs import Transporteur

class CalculateurFraisLivraison:
    def __init__(self):
        self.options = {
            "SEUIL_COMPACTAGE" : 2, #kg seuil des groupements d'articles legers 
            "SEUIL_ARTICLE_LEGER" : 1,#kg en dessosus on considere l'article comme leger
            "MAX_POIDS_MESSAGERIE_SCHENKER" : 1000, # kg
            "POIDS_MAX_COLIS_DPD" : 30, # kg
            "DPD_PATH" : '../data/dpd.csv',
            "SCHENKER_PALETTE_PATH" : '../data/schenker_palette.csv',
            "SCHENKER_MESSAGERIE_PATH" : '../data/schenker_messagerie.csv',
            "COUNTRY_AVAILABLE_PATH" : '../data/country_supported.csv',

            "DPD" : 'dpd',
            "SCHENKER_PALETTE" : 'schenker_palette',
            "SCHENKER_MESSAGERIE" : 'schenker_messagerie',

            "SEUIL_PALETTE_SCHENKER_MESSAGERIE" : 200, # kg
            # SEUIL_PALETTE_SCHENKER_MESSAGERIE = 200, # kg
            "SEUIL_PRIX_AU_KG_MESSAGERIE_SCHENKER" : 100, # kg
            "SEUIL_WARNING_ITERATIONS" : 10000,
        }

        self.transporteurs = {
            'dpd': Transporteur(self.options["DPD"], self.options["DPD_PATH"],self.options),
            'schenker_palette': Transporteur(self.options["SCHENKER_PALETTE"], self.options["SCHENKER_PALETTE_PATH"],self.options),
            'schenker_messagerie': Transporteur(self.options["SCHENKER_MESSAGERIE"], self.options["SCHENKER_MESSAGERIE_PATH"],self.options)
        }


    def set_options(self,options):
        for key,value in options.items():
            self.options[key] = value
        for key,trans in self.transporteurs.items():
            trans.set_options(self.options)
        return 0

    def calculer(self, panier, options):
        resultats = {}
        for nom, transporteur in self.transporteurs.items():
            results_transporteur = transporteur.calculer_tarif(panier, options)
            resultats[nom] = results_transporteur
        return resultats

    def compact_shopping_cart(self,panier):
        """ Tweaking method to reduce calculation time : regroup small articles """
        light_articles = []
        panier_sorted = []
        for article in panier :
            mass = float(article['poids'])
            if mass < self.options["SEUIL_ARTICLE_LEGER"]:
                light_articles.append(article)
            else :
                panier_sorted.append(article)
        current_group = []
        current_mass = 0
        light_groups = []
        for article in light_articles:
            current_group.append(article['nom'])
            current_mass += float(article['poids'])
            if current_mass > self.options["SEUIL_COMPACTAGE"] :
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
    



                    
                    
# if __name__ == "__main__":
#     calculateur = CalculateurFraisLivraison()
#     config = 3
#     if config==1 :
#         panier = []
#         execution_times = []
#         for i in range(13):
#             print(f"Number of article : {i}")
#             panier.append({"nom": f"Article {i}", "poids": i})
#             execution_time = timeit.timeit(lambda: calculateur.calculer(panier, "75"), number=1)
#             execution_time = execution_time / 3
#             execution_times.append(execution_time)
#         length = np.array(range(9,13))
#         execution_times = np.array(execution_times[9:])
#         iterations_count = np.array([partitions_count(i) for i in length])
#         time_per_iter = execution_times/iterations_count
#         # Régression
#         # params = regression_exponentielle(length, execution_times)
#         # a, b = params
#         # a = 6.0042e-08
#         # b= 1.6403e+00
#         # a =  1.4113e-11
#         # b = 2.4184e+00
#         plt.plot(length,time_per_iter,label="measure")
#         length = np.linspace(length[0],length[-1])
#         # plt.plot(length, a * np.exp(b * length), 'r-', label=f'Régression: {a:.2f}*exp({b:.2f}x)')
#         plt.xlabel("taille panier")
#         plt.ylabel("Exec time par iter")
#         plt.legend()
#         # print(f"Équation trouvée: y = {a:.4e} * exp({b:.4e} * x)")
#         plt.show()
#         # panier = [
#         #     {"nom": "Article 1", "poids": 5},
#         #     {"nom": "Article 2", "poids": 7},
#         #     {"nom": "Article 3", "poids": 15},
#         #     {"nom": "Article 4", "poids": 6},
#         #     {"nom": "Article 5", "poids": 7},
#         #     {"nom": "Article 6", "poids": 4},
#         #     {"nom": "Article 7", "poids": 3},
#         #     {"nom": "Article 8", "poids": 6},
#         #     {"nom": "Article 9", "poids": 12},
#         #     {"nom": "Article 10", "poids": 2},
#         #     {"nom": "Article 11", "poids": 9},
#         #     # {"nom": "Article 12", "poids": 9},
#         #     ]
#         print(f"Execution time: {execution_time:.2f} seconds")
    
#     elif config==2:
#         panier = [
#             {"nom": "Article 1", "poids": 5},
#             {"nom": "Article 2", "poids": 10},
#             {"nom": "Article 3", "poids": 15},
#             {"nom": "Article 3", "poids": 20},
#         ]
#         calculateur.calculer(panier, "75")

#     elif config==3:
#         panier = [
#             {"nom": "Article 1", "poids": 5},
#             {"nom": "Article 2", "poids": 10},
#             {"nom": "Article 3", "poids": 15},
#             {"nom": "Article 4", "poids": 20},
#             {"nom": "Article 5", "poids": 20},
#             {"nom": "Article 6", "poids": 20},
#             {"nom": "Article 7", "poids": 20},
#             {"nom": "Article 8", "poids": 20},
#             {"nom": "Article 9", "poids": 20},
#             {"nom": "Article 10", "poids": 20},
#             {"nom": "Article 11", "poids": 20},
#             {"nom": "Article 12", "poids": 20},
#         ]
#         calculateur.calculer(panier, "75")