print("Loading tk UI : ...")
from ui import initialiser_interface_tk
print("Loading tk UI : DONE")
print("Loading Calulator : ...")
from calculateur import CalculateurFraisLivraison
print("Loading Calulator : DONE")
print("Loading qt UI  : ... ")
from ui_qt import initialiser_interface_qt
print("Loading qt UI  : DONE ")


if __name__ == "__main__":
    print("Welcome to Transport Calculator 2025 !")
    calculateur = CalculateurFraisLivraison()
    initialiser_interface_qt(calculateur)
    initialiser_interface_tk(calculateur)
