from itertools import combinations


def tarif_par_masse(masse, tarif_par_kg):
    """
    Retourne le tarif en fonction de la masse d'un colis.
    Si la masse dépasse les clés disponibles, retourne le tarif maximal défini.
    """
    if masse in tarif_par_kg:
        return tarif_par_kg[masse]
    else:
        return tarif_par_kg[max(tarif_par_kg.keys())]


def optimiser_colis(items, max_weight, tarif_par_kg):
    """
    Optimise la répartition des articles dans des colis pour minimiser les frais de livraison.
    :param items: Liste de masses des articles
    :param max_weight: Masse maximale d'un colis
    :param tarif_par_kg: Dictionnaire des tarifs par masse
    :return: Coût total minimal et répartition des colis
    """
    n = len(items)
    items = sorted(items, reverse=True)  # Trier par masse décroissante pour efficacité

    # Initialisation de la DP : dp[masse][articles_restants] = coût minimal
    dp = {}

    def solve(remaining_items):
        if not remaining_items:
            return 0, []
        key = tuple(sorted(remaining_items))
        if key in dp:
            return dp[key]
        
        min_cost = float('inf')
        best_combination = []

        print(f"=== Résolution pour les articles restants : {remaining_items} ===")
        
        # Essayer toutes les combinaisons possibles d'un colis
        for i in range(1, len(remaining_items) + 1):
            for subset in combinations(remaining_items, i):
                if sum(subset) <= max_weight:
                    # Calculer le coût pour ce colis
                    cost_colis = tarif_par_masse(sum(subset), tarif_par_kg)
                    remaining = list(remaining_items)
                    for item in subset:
                        remaining.remove(item)
                    
                    # Résolution pour les articles restants
                    cost_remaining, combination = solve(remaining)
                    total_cost = cost_colis + cost_remaining

                    print(f"   Test colis : {subset} (masse={sum(subset)}, coût={cost_colis})")
                    print(f"      Restants : {remaining} -> Coût total estimé = {total_cost}")

                    # Mémoriser la meilleure solution
                    if total_cost < min_cost:
                        min_cost = total_cost
                        best_combination = [list(subset)] + combination
        
        print(f"==> Meilleure combinaison pour {remaining_items} : {best_combination} (coût={min_cost})\n")
        dp[key] = (min_cost, best_combination)
        return dp[key]

    # Résoudre pour tous les articles
    total_cost, colis = solve(items)
    return total_cost, colis

# Exemple d'utilisation
articles = [14, 14, 3, 12]
tarif_par_kg = {
    1: 7.27,
    2: 7.39,
    3: 7.51,
    4: 7.63,
    5: 7.76,
    6: 8.00,
    7: 8.23,
    8: 8.48,
    9: 8.71,
    10: 8.97,
    11: 10.30,
    12: 10.30,
    13: 10.30,
    14: 10.30,
    15: 10.30,
    16: 11.51,
    17: 11.51,
    18: 11.51,
    19: 11.51,
    20: 11.51,
    21: 13.93,
    22: 13.93,
    23: 13.93,
    24: 13.93,
    25: 13.93,
    26: 15.14,
    27: 15.14,
    28: 15.14,
    29: 15.14,
    30: 15.14,
}  # Exemple de tarifs
max_weight = 30

total_cost, colis = optimiser_colis(articles, max_weight, tarif_par_kg)
print("===============", total_cost)
print("Coût total :", total_cost)
print("Répartition des colis :", colis)
