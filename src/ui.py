import tkinter as tk
from tkinter import messagebox
from calculateur import CalculateurFraisLivraison

calculateur =None

def ajouter_article(event=None):
    row = len(entries) + 2  # Ajuster la ligne pour ne pas chevaucher les boutons
    label = tk.Label(root, text=f"Poids de l'article {row - 1} (kg):")
    label.grid(row=row, column=0)
    entry = tk.Entry(root)
    entry.grid(row=row, column=1)
    entries.append((label, entry))
    entry.focus_set()  # Positionner le curseur dans la nouvelle case
    # root.geometry(f"400x{100 + 30 * len(entries)}")  # Ajuster la hauteur de la fenêtre

def supprimer_article(event=None):
    if entries and not entries[-1][1].get():
        label, entry = entries.pop()
        label.destroy()
        entry.destroy()

def calculer_frais():
    try:
        panier = [{'nom': f'article{i+1}', 'poids': float(entry.get())} for i, (label, entry) in enumerate(entries) if entry.get()]
        departement = '01'
        resultats = calculateur.calculer(panier, departement)
        messagebox.showinfo("Résultats", f"Frais de livraison: {resultats}")
    except ValueError as e:
        messagebox.showerror("Erreur", f"Veuillez entrer des poids valides : {e}")

def initialiser_interface(input_calculateur):
    global root, entries, calculateur
    calculateur = input_calculateur
    root = tk.Tk()
    root.title("Calculateur de Frais de Livraison")
    # root.geometry("400x150")  # Taille initiale de la fenêtre

    entries = []
    ajouter_article()  # Ajouter le premier article par défaut

    tk.Button(root, text="Ajouter un article", command=ajouter_article).grid(row=0, columnspan=2)
    tk.Button(root, text="Calculer", command=calculer_frais).grid(row=1, columnspan=2)

    root.bind('<Return>', ajouter_article)  # Lier la touche Entrée à la fonction ajouter_article
    root.bind('<BackSpace>', supprimer_article)  # Lier la touche Retour arrière à la fonction supprimer_article

    root.mainloop()
