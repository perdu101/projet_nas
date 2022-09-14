#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Sauvegarde incrémentale

Fait une sauvegarde incrémentale de rep1 sur rep2, c'est à dire ne
copie que les fichiers de rep1, nouveaux pour rep2 ou plus récents.

Plus option miroir: efface de rep2 les fichiers et sous-répertoires absents
de rep1
"""

import os
from shutil import copy2, rmtree
from datetime import datetime  # pour la date/heure de l'ordinateur
from time import perf_counter  # pour le calcul du temps de traitement


#############################################################################
def cejour():
    """Retourne la date et l'heure de l'ordinateur: jj/mm/aaaa hh:mm:ss
    """
    dt = datetime.today()
    return "{}/{}/{} {}:{}:{}".format(dt.day, dt.month, dt.year, dt.hour, dt.minute, int(dt.second))


#############################################################################
def secs2jhms(secs):
    """Convertit le délai secs (secondes) => jours, heures, minutes, secondes
        En retour, j, h et m sont des entiers. s est de type float
                et msgtps (présentation du délai pour affichage) est un str
    """
    m, s = divmod(float(secs), 60)
    m = int(m)
    h, m = divmod(m, 60)
    j, h = divmod(h, 24)
    if j > 0:
        msgtps = "{:d}j {:d}h {:d}m {:.6f}s".format(j, h, m, s)
    elif h > 0:
        msgtps = "{:d}h {:d}m {:.6f}s".format(h, m, s)
    elif m > 0:
        msgtps = "{:d}m {:.6f}s".format(m, s)
    else:
        msgtps = "{:.6f}s".format(s)

    return j, h, m, s, msgtps


#############################################################################
def copieincrementale(rep1, rep2, miroir=False, fnerreur=None, recursion=True,
                      suiviliens=False):
    """Fait une sauvegarde incrémentale de rep1 sur rep2, c'est à dire ne
       copie que les fichiers de rep1, nouveaux pour rep2 ou plus récents.
       - rep1: le répertoire à sauvegarder
       - rep2: le répertoire qui recevra les copies de rep1
       - miroir: si True: supprime les fichiers et répertoires de rep2 absents
                 de rep1
       - fnerreur: si != None: fonction callback pour les messages d'erreur
       - recursion: si True, traite aussi les sous-répertoires
       - suiviliens: si True, suit les liens symboliques
       Affiche  en console les mises à jours faites
    """
    # si None => quand la fonction fnerreur est appelée, elle ne fait rien
    fnerreur = (lambda x: None) if fnerreur is None else fnerreur

    # =========================================================================
    # normalise et rend absolues les adresses des répertoires donnés
    rep1 = os.path.abspath(os.path.expanduser(rep1))
    rep2 = os.path.abspath(os.path.expanduser(rep2))

    # =========================================================================
    # vérifie l'existence et l'accès à rep1
    if not os.path.exists(rep1):
        fnerreur("le répertoire source n'existe pas: {}".format(rep1))
        return  # sort de la fonction
    if not os.access(rep1, os.X_OK):
        fnerreur("Pas d'accès au contenu du répertoire source: {}".format(rep1))
        return  # sort de la fonction

    # =========================================================================
    # vérifie l'existence de rep2 et le crée si nécessaire
    if not os.path.exists(rep2):
        # rep2 n'existe pas: on le crée
        try:
            os.mkdir(rep2)
            print("Crée le répertoire 2: {}".format(rep2))
        except Exception:
            fnerreur("Impossible de créer le répertoire destination: {}".format(rep2))
            return  # sort de la fonction
    else:
        # rep2 existe déjà: on vérifie l'accès
        if not os.access(rep2, os.X_OK):
            fnerreur("Pas d'accès au contenu du répertoire destination: {}".format(rep2))
            return  # sort de la fonction

    # =========================================================================
    # fait la copie incrémentale
    for repert, reps, fics in os.walk(rep1, onerror=fnerreur, followlinks=suiviliens):
        for fic in fics:
            nfc1 = os.path.join(repert, fic)  # fic avec chemin sur rep1
            nfc1rel = os.path.relpath(nfc1, rep1)  # fic avec chemin relatif
            nfc2 = os.path.join(rep2, nfc1rel)  # fic avec chemin sur rep2
            if not os.path.exists(nfc2):
                # crée le chemin nécessaire pour copier le nouveau fichier
                chemin = os.path.dirname(nfc2)
                if not os.path.exists(chemin):
                    try:
                        os.makedirs(chemin)
                        print("Crée le nouveau répertoire: {}".format(chemin))
                    except Exception:
                        fnerreur("Impossible de créer le répertoire: {}".format(chemin))
                        continue  # => passer au fichier suivant
                # copie le nouveau fichier
                try:
                    copy2(nfc1, nfc2)
                    print("Copie le nouveau fichier: {}".format(nfc2))
                except Exception:
                    fnerreur("Impossible de copier le nouveau fichier: {}".format(nfc2))
                    # passe au fichier suivant
            else:
                # le fichier fic existe déjà sur rep2: on compare les dates
                try:
                    temps1, temps2 = os.path.getmtime(nfc1), os.path.getmtime(nfc2)
                except Exception:
                    fnerreur("Impossible de calculer les dates de mise à jour de {} et/ou de {}".format(nfc1, nfc2))
                    continue  # passe au fichier suivant
                try:
                    if temps1 > temps2:
                        # copie le fichier fic de rep1, plus récent que celui de rep2
                        copy2(nfc1, nfc2)
                        print("Copie le fichier plus récent: {}".format(nfc2))
                except Exception:
                    fnerreur("Impossible de copier le fichier plus récent: {}".format(nfc2))
                    # passe au fichier suivant

        if not recursion:
            break  # interrompt la boucle os.walk pour empêcher la récursion

    # =========================================================================
    # traite l'effet miroir s'il est demandé
    if miroir:
        # lecture de rep2
        for repert, reps, fics in os.walk(rep2, onerror=fnerreur, followlinks=suiviliens):
            # supprime les fichiers de rep2 absents de rep1
            for fic in fics:
                nfc2 = os.path.join(repert, fic)  # fic avec chemin sur rep2
                nfc2rel = os.path.relpath(nfc2, rep2)  # fic avec chemin relatif
                nfc1 = os.path.join(rep1, nfc2rel)  # fic avec chemin sur rep1
                if not os.path.exists(nfc1):
                    # le fichier fic de rep2 absent de rep1 => on le supprime
                    try:
                        os.remove(nfc2)
                        print("Miroir => supprime le fichier: {}".format(nfc2))
                    except Exception:
                        fnerreur("Impossible de supprimer le fichier {}".format(nfc2))

            # supprime les répertoires de rep2 absents de rep1
            for i in range(len(reps[:]) - 1, -1, -1):  # parcours à l'envers de reps
                nrc2 = os.path.join(repert, reps[i])  # rep avec chemin sur rep2
                nrc2rel = os.path.relpath(nrc2, rep2)  # rep avec chemin relatif
                nrc1 = os.path.join(rep1, nrc2rel)  # rep avec chemin sur rep1
                if not os.path.exists(nrc1):
                    # répertoire rep de rep2 absent de rep1 => on le supprime
                    try:
                        rmtree(nrc2)
                        print("Miroir => supprime le répertoire: {}".format(nrc2))
                        reps.pop(i)  # on retire rep[i] de l'exploration suivante
                    except Exception:
                        fnerreur("miroir: impossible de supprimer le répertoire {}".format(nrc2))






def copieincrementale(rep1, rep2, miroir=False, fnerreur=None, recursion=True,
                      suiviliens=False):
    """Fait une sauvegarde incrémentale de rep1 sur rep2, c'est à dire ne
       copie que les fichiers de rep1, nouveaux pour rep2 ou plus récents.
       - rep1: le répertoire à sauvegarder
       - rep2: le répertoire qui recevra les copies de rep1
       - miroir: si True: supprime fichiers et répert. de rep2 absents de rep1
       - fnerreur: si != None: fonction callback pour le message d'erreur
       - recursion: si True, traite aussi les sous-répertoires
       - suiviliens: si True, suit les liens symboliques
    """
    # =========================================================================
    # calcule les adresses absolues des répertoires donnés
    rep1 = os.path.abspath(os.path.expanduser(rep1))
    rep2 = os.path.abspath(os.path.expanduser(rep2))

    # =========================================================================
    # vérifie l'accès à rep1
    if not os.access(rep1, os.X_OK):
        if fnerreur is not None: fnerreur("Erreur accès à rep1")
        return  # impossible de rentrer dans rep1

    # =========================================================================
    # vérifie l'existence de rep2
    if not os.path.exists(rep2):
        # rep2 n'existe pas: on le crée
        try:
            os.mkdir(rep2)
        except Exception as msgerr:
            if fnerreur is not None: fnerreur(msgerr)
            return  # impossible de créer le répertoire destination rep2
    else:
        # rep2 existe déjà: on vérifie l'accès
        if not os.access(rep2, os.X_OK):
            if fnerreur is not None: fnerreur("Erreur accès à rep2")
            return  # impossible de rentrer dans rep2

    # =========================================================================
    # fait la copie incrémentale
    lgrep1, lgrep2 = len(rep1), len(rep2)  # nb de caractères de rep1 et rep2
    for repert, reps, fics in os.walk(rep1, onerror=fnerreur, followlinks=suiviliens):
        for fic in fics:
            nfc1 = os.path.join(repert, fic)  # fic avec son chemin sur rep1
            nfc2 = os.path.join(rep2, repert[lgrep1 + 1:], fic)  # avec chemin sur rep2
            if not os.path.exists(nfc2):
                # crée le chemin nécessaire pour copier le nouveau fichier
                chemin = os.path.dirname(nfc2)
                if not os.path.exists(chemin):
                    try:
                        os.makedirs(chemin)
                    except Exception as msgerr:
                        if fnerreur is not None: fnerreur(msgerr)
                        continue  # échec => passer au fic suivant
                # copie le nouveau fichier
                try:
                    copy2(nfc1, nfc2)
                    print("Copie le nouveau fichier: {}".format(nfc1))
                except Exception as msgerr:
                    if fnerreur is not None: fnerreur(msgerr)
            else:
                # le fichier fic existe déjà sur rep2: on compare les dates
                try:
                    if os.path.getmtime(nfc1) > os.path.getmtime(nfc2):
                        # copie le fichier fic de rep1 plus récent que celui de rep2
                        copy2(nfc1, nfc2)
                        print("Copie le fichier plus récent: {}".format(nfc1))
                except Exception as msgerr:
                    # erreur possible avec getmtime ou copy2
                    if fnerreur is not None: fnerreur(msgerr)

        if not recursion:
            break  # interrompt la boucle os.walk pour empêcher la récursion

    # =========================================================================
    # traite l'effet miroir
    if miroir:
        # lecture de rep2
        for repert, reps, fics in os.walk(rep2, onerror=fnerreur, followlinks=suiviliens):
            # supprime les fichiers de rep2 absents de rep1
            for fic in fics:
                nfc2 = os.path.join(repert, fic)
                nfc1 = os.path.join(rep1, repert[lgrep2 + 1:], fic)
                if not os.path.exists(nfc1):
                    # le fichier fic de rep2 absent de rep1 => on le supprime
                    try:
                        os.remove(nfc2)
                        print("Miroir => supprime le fichier: {}".format(nfc2))
                    except Exception as msgerr:
                        if fnerreur is not None: fnerreur(msgerr)

            # supprime les répertoires de rep2 absents de rep1
            for i in range(len(reps[:]) - 1, -1, -1):  # parcours à l'envers de reps
                nrc2 = os.path.join(repert, reps[i])  # rep avec chemin sur rep2
                nrc1 = os.path.join(rep1, repert[lgrep2 + 1:], reps[i])  # rep avec chemin sur rep1
                if not os.path.exists(nrc1):
                    # répertoire rep de rep2 absent de rep1 => on le supprime
                    try:
                        rmtree(nrc2)
                        print("Miroir => supprime le répertoire: {}".format(nrc2))
                        reps.pop(i)  # on retire rep[i] de l'exploration suivante
                    except Exception as msgerr:
                        if fnerreur is not None: fnerreur(msgerr)


#############################################################################
if __name__ == "__main__":

    # ========================================================================
    # récupération des données de traitement de la ligne de commande
    import argparse


    def str2bool(v):
        """Traduit les chaines de caractères en booléens
        """
        if v.lower() in ["o", "oui", "y", "yes", "t", "true"]:
            return True
        elif v.lower() in ["n", "non", "not", "f", "false"]:
            return False
        else:
            raise Exception("Erreur: valeur booléenne attendue pour {}".format(v))


    # création du parse des arguments
    parser = argparse.ArgumentParser(description="Sauvegarde incrémentale d'un répertoire")

    # déclaration et configuration des arguments
    parser.add_argument('-s', '--source', dest='source', type=str, required=True, action="store",
                        help="Répertoire source")
    parser.add_argument('-d', '--destination', dest='destination', type=str, required=True, action="store",
                        help="Répertoire destination")
    parser.add_argument('-m', '--miroir', dest="miroir", type=str2bool, choices=[True, False], default=False,
                        help="Si True, supprime les fichiers et répertoires destination absents de la source")
    parser.add_argument('-r', '--recursion', dest="recursion", type=str2bool, choices=[True, False], default=True,
                        help="Si True, explore les sous-répertoires")
    parser.add_argument('-l', '--suiviliens', dest="suiviliens", type=str2bool, choices=[True, False], default=False,
                        help="Si True, suit les liens symboliques")

    # dictionnaire des arguments passés au lancement
    dicoargs = vars(parser.parse_args())

    # Récupére les données de traitement
    source = dicoargs["source"]
    destination = dicoargs["destination"]
    miroir = dicoargs["miroir"]
    recursion = dicoargs["recursion"]
    suiviliens = dicoargs["suiviliens"]

    # ========================================================================
    # en-tête d'affichage
    print("SAUVEGARDE INCREMENTALE ({})".format(cejour()))
    print()

    print("Répertoire source: {}".format(source))
    print("Répertoire destination: {}".format(destination))
    print("Option miroir: {}".format(miroir))
    print("Recursion: {}".format(recursion))
    print("Suivi des liens symboliques: {}".format(suiviliens))
    print()

    # ========================================================================
    # Sauvegarde
    erreurs = []
    secs = perf_counter()
    copieincrementale(source, destination, miroir, erreurs.append, recursion, suiviliens)
    secs = perf_counter() - secs
    # ========================================================================
    # Affichage des erreurs s'il y en a
    if erreurs != []:
        print("Erreurs: {}".format(len(erreurs)))
        print()
        for erreur in erreurs:
            print(erreur)
        print()

        # ========================================================================
    _, _, _, _, msgtps = secs2jhms(secs)
    print("Sauvegarde terminée en {}".format(msgtps))