print("Loading UI : ...")
from ui import initialiser_interface
print("Loading UI : DONE")
print("Loading Calulator : ...")
from calculateur import CalculateurFraisLivraison
print("Loading Calulator : DONE")

if __name__ == "__main__":
    print("Welcome to Transport Calculator 2025 !")
    calculateur = CalculateurFraisLivraison()
    initialiser_interface(calculateur)
