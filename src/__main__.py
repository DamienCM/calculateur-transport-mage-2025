print("Loading tk UI : ...")
from ui import initialiser_interface_tk
print("Loading tk UI : DONE")
print("Loading Calulator : ...")
from calculateur import CalculateurFraisLivraison
print("Loading Calulator : DONE")
print("Loading qt UI  : ... ")
from ui_qt import initialize_qt_interface
print("Loading qt UI  : DONE ")


if __name__ == "__main__":
    print("Welcome to Transport Calculator 2025 !")
    calculateur = CalculateurFraisLivraison()
    initialize_qt_interface(calculateur)
    initialiser_interface_tk(calculateur)
