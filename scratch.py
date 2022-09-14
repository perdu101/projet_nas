import os.path
import pickle
"""
f =open('res.txt', 'wb')
pickle.dump(a, f)
pickle.dump(b, f)
f.close()

f = open('res.txt', 'rb')
a = pickle.load(f)
b = pickle.load(f)
print (b)

f.close()
"""


import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog

try:
    f = open('res2.txt', 'rb')
    nom_pc = pickle.load(f)
    nom_dns_nas = pickle.load(f)
    lettre_lecteur_nas = pickle.load(f)
    ip_nas = pickle.load(f)
    mac_nas = pickle.load(f)
    autostart_emplacement = pickle.load(f)
    emplacement_a_copie= pickle.load(f)
    f.close()
    reglage_nas_ok = nom_pc and nom_dns_nas and lettre_lecteur_nas and ip_nas and mac_nas and autostart_emplacement and emplacement_a_copie != ""
except:
    reglage_nas_ok = False

print(reglage_nas_ok)
global folder_path

def configuration_nas():
    import os.path
    import re
    import socket
    import subprocess

    """variable fixe"""
    nom_pc = socket.gethostname()
    emplacement_utilisateur = (os.path.expanduser("~"))
    """variable gui?"""
    nom_dns_nas: str = "nas"

    cmd_ping_nas: str = "ping -4 " + nom_dns_nas # -4 forcing ipv4
    shell_cmd_ping_nas = subprocess.run(cmd_ping_nas, capture_output=True, text=True)
    ip_nas = shell_cmd_ping_nas.stdout
    print (ip_nas)
    ip_nas = ip_nas.split("[")[1].split("]")[0]

    cmd_mac_nas = "arp -a " + ip_nas
    shell_cmd_mac_nas = subprocess.run(cmd_mac_nas, capture_output=True, text=True)
    mac_nas = shell_cmd_mac_nas.stdout
    mac_nas = re.search('(([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2}))', mac_nas)
    mac_nas = (mac_nas[0])
    characters = "-"
    for x in range(len(characters)):
        mac_nas = mac_nas.replace(characters[x], ".")

    autostart_emplacement = emplacement_utilisateur + "\\" + "AppData" + "\\" + "Roaming" + "\\" + "Microsoft" + "\\" + "Windows" + "\\" + "Start Menu" + "\\" + "Programs" + "\\" + "Startup" + "\\"

    f = open('res2.txt', 'wb')
    pickle.dump(nom_pc, f)
    pickle.dump(nom_dns_nas, f)
    pickle.dump(lettre_lecteur_nas, f)
    pickle.dump(ip_nas, f)
    pickle.dump(mac_nas, f)
    pickle.dump(autostart_emplacement, f)
    pickle.dump(emplacement_a_copie, f)
    f.close()

fenetre = Tk()
fenetre.title("nas")
fenetre.geometry('500x300')
fenetre.minsize(400, 200)
"""
fenetre.iconbitmap("iconas.ico")
"""
fenetre.config(background="#DCFCFC")
if reglage_nas_ok == False:
    emplacement_a_copie = (os.path.expanduser("~"))




def on_now():
    from wol import send_magic_packet
    if reglage_nas_ok == True:
        send_magic_packet(mac_nas)


buttonon = Button(fenetre, text="ON", command=lambda: on_now())
buttonon.pack()


def save_now():

    import autostart


button3 = Button(fenetre, text="copier maintenant", command=lambda: save_now())
button3.pack()


def action(event):
    # Obtenir l'élément sélectionné
    global lettre_lecteur_nas

    lettre_lecteur_nas = listeCombo.get()
    print("Vous avez sélectionné : '", lettre_lecteur_nas, "'")


labelChoix = tk.Label(fenetre, text="lettre lecteur nas (par defaut b)", font=("Arial", 15), fg="black")
labelChoix.pack()

# 2) - créer la liste Python contenant les éléments de la liste Combobox
listeProduits = ["a", "b", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u",
                 "v", "w", "x", "y", "z"]

# 3) - Création de la Combobox via la méthode ttk.Combobox()
listeCombo = ttk.Combobox(fenetre, values=listeProduits)

# 4) - Choisir l'élément qui s'affiche par défaut
if reglage_nas_ok == True:
    print(lettre_lecteur_nas)
    listeCombo.current(listeProduits.index(lettre_lecteur_nas))
else:
    lettre_lecteur_nas = listeCombo.current(1)


listeCombo.pack()
listeCombo.bind("<<ComboboxSelected>>", action)


def browse_button():
    # Allow user to select a directory and store it in global var
    # called folder_path

    global emplacement_a_copie
    nom_dossier_sauv = filedialog.askdirectory()
    folder_path.set(nom_dossier_sauv)
    emplacement_a_copie = folder_path.get()
    folder_path.set("Emplacement à sauvegarder: " + folder_path.get())

button2 = Button(text="Parcourir", command=browse_button)
button2.pack(side=TOP, padx=50, pady=10)

folder_path = StringVar()

folder_path.set("Emplacement à sauvegarder: " + emplacement_a_copie)

lbl1 = Label(fenetre, textvariable=folder_path, font=("Arial", 15), fg="black")
lbl1.pack()


def auto_coonfig():
    configuration_nas()





button = Button(fenetre, text="config", command=lambda: auto_coonfig())
button.pack()

fenetre.mainloop()
