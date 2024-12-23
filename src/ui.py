import tkinter as tk
from calculateur import CalculateurFraisLivraison

calculateur = None
result_text = None
ajouter_article_button = None

def ajouter_article(event=None): 
    global ajouter_article_button
    row = len(entries) + 1  # Ajuster la ligne pour ne pas chevaucher les boutons
    ajouter_article_button.grid(row=row+1, columnspan=2)  # Déplacer le bouton en bas
    label = tk.Label(input_frame, text=f"Poids de l'article {row} (kg):")
    label.grid(row=row, column=0)
    entry = tk.Entry(input_frame)
    entry.grid(row=row, column=1)
    entries.append((label, entry))
    entry.focus_set()  # Positionner le curseur dans la nouvelle case

def supprimer_article(event=None):
    if entries and not entries[-1][1].get():
        label, entry = entries.pop()
        label.destroy()
        entry.destroy()

def calculer_frais():
    try:
        panier = [{'nom': f'article{i+1}', 'poids': float(entry.get())} for i, (label, entry) in enumerate(entries) if entry.get()]
        departement = departement_entry.get()
        resultats = calculateur.calculer(panier, departement)
        
        prix_dpd = float(resultats['dpd']['prix'])
        prix_schenker_palette = float(resultats['schenker_palette'])
        prix_schenker_messagerie = float(resultats['schenker_messagerie'])
        
        results_text_dpd.set(f"Prix dpd : {prix_dpd:.2f}€")
        arrangement_text_dpd.set(f"Arrangement dpd : {resultats['dpd']['arrangement']}")
        results_text_schenker_palette.set(f"Prix Schenker palette : {prix_schenker_palette:.2f}€")
        results_text_schenker_messagerie.set(f"Prix Schenker messagerie : {prix_schenker_messagerie:.2f}€")
        
        min_prix = min(prix_dpd, prix_schenker_palette, prix_schenker_messagerie)
        result_text.set(f"Resultats : \n")
        
        # Highlight the lowest price in red
        if min_prix == prix_dpd:
            result_label_dpd.config(fg="red")
            arrangement_label_dpd.config(fg="red")
            result_label_schenker_palette.config(fg="black")
            result_label_schenker_messagerie.config(fg="black")
        elif min_prix == prix_schenker_palette:
            result_label_dpd.config(fg="black")
            arrangement_label_dpd.config(fg="black")
            result_label_schenker_palette.config(fg="red")
            result_label_schenker_messagerie.config(fg="black")
        else:
            result_label_dpd.config(fg="black")
            arrangement_label_dpd.config(fg="black")
            result_label_schenker_palette.config(fg="black")
            result_label_schenker_messagerie.config(fg="red")
    except ValueError as e:
        result_text.set(f"Erreur: Veuillez entrer des poids valides : {e}")
    except Exception as e:
        result_text.set(f"Erreur: {e}")

def initialiser_interface(input_calculateur):
    global root, entries, calculateur, input_frame, button_frame, result_text, results_text_schenker_palette, results_text_schenker_messagerie, results_text_dpd, arrangement_text_dpd, departement_entry, result_label_dpd, arrangement_label_dpd, result_label_schenker_palette, result_label_schenker_messagerie
    calculateur = input_calculateur
    root = tk.Tk()
    root.title("Calculateur de Frais de Livraison")

    # Create frames for inputs, buttons, and results
    input_frame = tk.Frame(root, padx=10, pady=10)
    input_frame.grid(row=0, column=0, sticky="nsew")
    button_frame = tk.Frame(root, padx=10, pady=10)
    button_frame.grid(row=0, column=1, sticky="nsew")
    result_frame = tk.Frame(root, padx=10, pady=10)
    result_frame.grid(row=0, column=2, sticky="nsew")

    # Département input
    tk.Label(button_frame, text="Département:").grid(row=0, column=0)
    departement_entry = tk.Entry(button_frame)
    departement_entry.grid(row=0, column=1)

    # Buttons
    tk.Button(button_frame, text="Calculer", command=calculer_frais).grid(row=1, columnspan=2)

    entries = []
    global ajouter_article_button
    ajouter_article_button = tk.Button(input_frame, text="Ajouter un article", command=ajouter_article)
    ajouter_article_button.grid(row=2, columnspan=2)
    ajouter_article()  # Ajouter le premier article par défaut


    root.bind('<Return>', ajouter_article)  # Lier la touche Entrée à la fonction ajouter_article
    root.bind('<BackSpace>', supprimer_article)  # Lier la touche Retour arrière à la fonction supprimer_article

    # Result display
    result_text = tk.StringVar(value="Resultats : \n")
    results_text_schenker_palette = tk.StringVar(value="Prix Schenker palette : ")
    results_text_schenker_messagerie = tk.StringVar(value="Prix Schenker messagerie: ")
    results_text_dpd = tk.StringVar(value="Resultats dpd : ")
    arrangement_text_dpd = tk.StringVar(value="Arrangement dpd : ")

    result_label = tk.Label(result_frame, textvariable=result_text, wraplength=300)
    result_label.grid(row=0, column=0, sticky="nsew")
    result_label_schenker_palette = tk.Label(result_frame, textvariable=results_text_schenker_palette, wraplength=300)
    result_label_schenker_palette.grid(row=1, column=0, sticky="nsew")
    result_label_schenker_messagerie = tk.Label(result_frame, textvariable=results_text_schenker_messagerie, wraplength=300)
    result_label_schenker_messagerie.grid(row=2, column=0, sticky="nsew")
    result_label_dpd = tk.Label(result_frame, textvariable=results_text_dpd, wraplength=300)
    result_label_dpd.grid(row=3, column=0, sticky="nsew")
    arrangement_label_dpd = tk.Label(result_frame, textvariable=arrangement_text_dpd, wraplength=300)
    arrangement_label_dpd.grid(row=4, column=0, sticky="nsew")

    root.mainloop()
