"""
Auteur: Yacine BOUKARI
Date: Du 11 au 14 avril 2021

Un jeu du type jeu d’évasion (escape game) dans lequel le joueur commande au clavier les déplacements d’un personnage
au sein d’un « château » représenté en plan. Le château est constitué de cases vides (pièces, couloirs), de murs,
de portes (que le personnage ne pourra franchir qu’en répondant à des questions), d’objets à ramasser (qui l’aideront à
trouver les réponses à ces questions) et de la case de sortie du château. Le but du jeu est d’atteindre cette dernière.
"""

import turtle
from CONFIGS import *
from math import sqrt

position = list(POSITION_DEPART)        # Pour connaître la position du personnage en temps réel.
text_write = (POINT_AFFICHAGE_ANNONCES[0] + 2, POINT_AFFICHAGE_ANNONCES[1] - 30)  # Position des annonces dans leur zone
tiret = [POINT_AFFICHAGE_INVENTAIRE[0] + 40, POINT_AFFICHAGE_INVENTAIRE[1] - 20]  # Position où écrire dans l'inventaire
number = [0]    # La longueur de cette liste donne le numéro de l'objet ramassé (initialement 1).
portes = {}     # Dictionnaire ayant comme clés les coordonnées de chaque porte et comme valeur les question/réponse.
objets = {}     # Dictionnaire ayant comme clés les coordonnées de chaque objet et comme valeur le nom de l'objet.

# L'instruction a, b = eval(line) permet de récupérer une chaîne du type '(x, y), (c1, c2)' de sorte que a=(x, y) de
# type Tuple et b=(c1, c2) de type Tuple aussi.
with open(fichier_questions, encoding="utf-8") as doors:
    for line in doors:
        a, b = eval(line)
        portes[a] = b

with open(fichier_objets, encoding="utf-8") as objects:
    for line in objects:
        a, b = eval(line)
        objets[a] = b


def lire_matrice(fichier):
    """
    :param fichier: le fichier contenant le plan du chateau
    :return: une matrice représentant les cases du plan suivant les lignes horizontales
    """
    castle = []
    with open(fichier, encoding="utf-8") as plan:
        for ligne in plan:
            cases = ligne.strip().split(" ")
            castle.append(cases)
    return castle


matrix = lire_matrice(fichier_plan)         # Matrice représentant le plan.


def calculer_pas(matrice):
    """
    :param matrice: la matrice représentant le plan du chateau
    :return: la largeur à donner à chaque case
    """
    aire_chateau = (ZONE_PLAN_MAXI[0] - ZONE_PLAN_MINI[0]) * (ZONE_PLAN_MAXI[1] - ZONE_PLAN_MINI[1])
    nb_cases = 0
    for i in range(len(matrice)):
        for j in range(len(matrice[i])):
            nb_cases += 1
    aire_case = aire_chateau / nb_cases
    cote_case = int(sqrt(aire_case))
    return cote_case


def coordonnes(case, pas):
    """
    :param case: case définie par ses coordonnées (numéros de ligne et de colonne).
    :param pas: côté d'une case
    :return: coordonnées en pixels turtle du coin inférieur gauche de la case
    """
    location = (ZONE_PLAN_MINI[0] + pas * case[1], ZONE_PLAN_MAXI[1] - pas * (case[0] + 1))     # Formule générale
    # déduite de l'étude des coordonnées sur la fenêtre Turtle et de la position dans la matrice de certaines cases
    # extrêmes.
    return location


def tracer_carre(dimension):
    """
    :param dimension: côté de la case en pixels turtle
    :return None
    """
    for i in range(4):
        turtle.forward(dimension)
        turtle.left(90)


def tracer_case(case, couleur, pas):
    """
    Trace un carré d’une certaine couleur et taille à un certain endroit.
    :param case: couple de coordonnées en indice dans la matrice
    :param couleur: couleur à donner à la case
    :param pas: côté de la case
    :return: None
    """
    turtle.up()
    turtle.goto(case)
    turtle.down()
    turtle.color(COULEUR_CASES, couleur)
    turtle.begin_fill()
    tracer_carre(pas)
    turtle.end_fill()


def afficher_plan(matrice):
    """
    Trace le chateau en traçant chaque case à l’emplacement et dans une couleur correspondant à ce que dit la matrice.
    :param matrice: plan du château
    :return:  None
    """
    for i in range(len(matrice)):
        for j in range(len(matrice[i])):
            if int(matrice[i][j]) == 0:
                tracer_case(coordonnes((i, j), calculer_pas(matrix)), COULEUR_COULOIR,
                            calculer_pas(matrix))
            elif int(matrice[i][j]) == 1:
                tracer_case(coordonnes((i, j), calculer_pas(matrix)), COULEUR_MUR,
                            calculer_pas(matrix))
            elif int(matrice[i][j]) == 2:
                tracer_case(coordonnes((i, j), calculer_pas(matrix)), COULEUR_OBJECTIF,
                            calculer_pas(matrix))
            elif int(matrice[i][j]) == 3:
                tracer_case(coordonnes((i, j), calculer_pas(matrix)), COULEUR_PORTE,
                            calculer_pas(matrix))
            elif int(matrice[i][j]) == 4:
                tracer_case(coordonnes((i, j), calculer_pas(matrix)), COULEUR_OBJET,
                            calculer_pas(matrix))
    # Écrire le titre "Inventaire" dans la zone de l'inventaire
    turtle.up()
    turtle.goto(tiret[0], tiret[1])
    turtle.color("Black")
    turtle.down()
    turtle.write("Inventaire:", align="center")
    # Mise à jour de "tiret" pour que les prochains objets soient écris sur une autre ligne dans la zone d'inventaire.
    tiret[0] -= 25
    tiret[1] -= 30


def tracer_personnage(locate):
    """
    Dessine le personnage
    :param locate: l'endroit où sera tracé le personnage
    :return: None
    """
    current = coordonnes(locate, calculer_pas(matrix))      # Récupère les coordonnes de la case.
    centre = (current[0] + calculer_pas(matrix) // 2, current[1] + calculer_pas(matrix) // 2)   # Milieu de la case.
    turtle.up()
    turtle.goto(centre)
    turtle.down()
    turtle.dot(calculer_pas(matrix) * RATIO_PERSONNAGE, COULEUR_PERSONNAGE)


def afficher_message(message, locate):
    """
    Écrit un message dans la fenêtre turtle.
    :param message: Le message à afficher.
    :param locate: L'endroit où afficher le message.
    :return None
    """
    current = turtle.pos()          # Enregistre la position actuelle de la tortue.
    # Retrace la zone d'affichage des annonces en la remplissant de blanc, ce qui permet d'effacer un texte déjà écrit.
    turtle.up()
    turtle.goto(POINT_AFFICHAGE_ANNONCES)
    turtle.down()
    turtle.color(COULEUR_EXTERIEUR)
    turtle.setheading(0)
    turtle.begin_fill()
    for i in range(2):
        turtle.forward(400)
        turtle.right(90)
        turtle.forward(30)
        turtle.right(90)
    turtle.end_fill()
    # Écriture du message.
    turtle.up()
    turtle.goto(locate)
    turtle.color("Black")
    turtle.down()
    turtle.write(message, align='left')
    # Retour à la position initiale.
    turtle.up()
    turtle.goto(current)
    turtle.down()


def afficher_objet(thing):
    """
    Écrit le nom de l'objet récupéré dans la zone d'inventaire
    :param thing: Nom de l'objet
    :return: None
    """
    current = turtle.pos()      # Enregistre la position actuelle de la tortue.
    # Écriture du nom de l'objet.
    turtle.up()
    turtle.goto(tiret[0], tiret[1])
    turtle.color("Black")
    turtle.down()
    turtle.write("N°" + str(len(number)) + ": " + thing, align='left')
    # Retour à la position initiale
    turtle.up()
    turtle.goto(current)
    turtle.down()
    tiret[1] -= 20      # Mise à jour de "tiret" (saut à la ligne)
    number.append(0)         # Augmentation de la taille de la liste


def quiz(locate):
    """
    Pose la question relative à la porte rencontrée et évalue la réponse.
    :param locate: position d'une case de la matrice correspondant à une porte.
    :return: True si la bonne réponse est donnée, False sinon.
    """
    question = portes[locate][0]
    answer = portes[locate][1]
    saisie = turtle.textinput("Question", question)
    if saisie == answer:
        return True
    else:
        return False


def one_move(function, direction, locate):
    """
    Mouvement du personnage d'une case vers une autre
    :param function: la fonction à assigner à la touche utilisée
    :param direction: sens du déplacement du personnage
    :param locate: case vers laquelle se dirige le personnage
    :return: None
    """
    tracer_case(coordonnes(position, calculer_pas(matrix)), COULEUR_VUE, calculer_pas(matrix))
    tracer_personnage(locate)
    turtle.onkeypress(function, direction)


def case_porte(function, direction, locate):
    """
    Actions à effectuer lorsque le personnage devant une porte.
    :param function: la fonction à assigner à la touche utilisée
    :param direction: sens du déplacement du personnage
    :param locate: case vers laquelle se dirige le personnage
    :return: None
    """
    afficher_message("Cette porte est fermée.", text_write)
    if quiz(locate):
        matrix[locate[0]][locate[1]] = str(0)       # Remplace la case par une case vide dans la matrice.
        afficher_message("Bonne réponse! La porte s'ouvre.", text_write)
        turtle.listen()
        one_move(function, direction, locate)
        position[0], position[1] = locate[0], locate[1]     # Mise à jour de la position de la tortue.
    else:
        afficher_message("Mauvaise réponse! La porte reste fermée.", text_write)
        deplacer_perso()


def case_objet(function, direction, locate):
    """
    Actions à effectuer lorsque le personnage devant un objet.
    :param function: la fonction à assigner à la touche utilisée
    :param direction: sens du déplacement du personnage
    :param locate: case vers laquelle se dirige le personnage
    :return: None
    """
    one_move(function, direction, locate)
    position[0], position[1] = locate[0], locate[1]
    afficher_message("Vous avez trouvé un objet: " + objets[(position[0], position[1])], text_write)
    afficher_objet(objets[(position[0], position[1])])
    matrix[locate[0]][locate[1]] = str(0)


def case_win(function, direction, locate):
    """
    Actions à effectuer lorsque le personnage atteint l'objectif.
    :param function: la fonction à assigner à la touche utilisée
    :param direction: sens du déplacement du personnage
    :param locate: case vers laquelle se dirige le personnage
    :return: None
    """
    one_move(function, direction, locate)
    position[0], position[1] = locate[0], locate[1]
    afficher_message("Bravo! Vous avez gagné.", text_write)
    turtle.done()


def deplacer_haut():
    """
    Actions à effectuer à l'appui de la touche directionnelle 'haut'.
    :return: None
    """
    turtle.onkeypress(None, "Up")       # Désactivation temporaire de la touche pour éviter l'exécution en cascade.
    target = (position[0] - 1, position[1])         # Case vers laquelle se dirige le personnage.
    if int(matrix[target[0]][target[1]]) == 0:      # Cas d'un couloir.
        one_move(deplacer_haut, "Up", target)
        position[0] -= 1
    elif int(matrix[target[0]][target[1]]) == 1:    # Cas d'un mur ou d'une sortie des limites du château.
        deplacer_perso()
    elif int(matrix[target[0]][target[1]]) == 2:    # Cas de la case finale.
        case_win(deplacer_haut, "Up", target)
    elif int(matrix[target[0]][target[1]]) == 3:    # Cas d'une porte.
        case_porte(deplacer_haut, "Up", target)
    elif int(matrix[target[0]][target[1]]) == 4:    # Cas d'un objet.
        case_objet(deplacer_haut, "Up", target)


def deplacer_bas():
    """
    Actions à effectuer à l'appui de la touche directionnelle 'bas'.
    :return: None
    """
    turtle.onkeypress(None, "Down")
    target = (position[0] + 1, position[1])
    if int(matrix[target[0]][target[1]]) == 0:
        one_move(deplacer_bas, "Down", target)
        position[0] += 1
    elif int(matrix[target[0]][target[1]]) == 1:
        deplacer_perso()
    elif int(matrix[target[0]][target[1]]) == 2:
        case_win(deplacer_bas, "Down", target)
    elif int(matrix[target[0]][target[1]]) == 3:
        case_porte(deplacer_bas, "Down", target)
    elif int(matrix[target[0]][target[1]]) == 4:
        case_objet(deplacer_bas, "Down", target)


def deplacer_droite():
    """
    Actions à effectuer à l'appui de la touche directionnelle 'droit'.
    :return: None
    """
    turtle.onkeypress(None, "Right")
    target = (position[0], position[1] + 1)
    if int(matrix[target[0]][target[1]]) == 0:
        one_move(deplacer_droite, "Right", target)
        position[1] += 1
    elif int(matrix[target[0]][target[1]]) == 1:
        deplacer_perso()
    elif int(matrix[target[0]][target[1]]) == 2:
        case_win(deplacer_droite, "Right", target)
    elif int(matrix[target[0]][target[1]]) == 3:
        case_porte(deplacer_droite, "Right", target)
    elif int(matrix[target[0]][target[1]]) == 4:
        case_objet(deplacer_droite, "Right", target)


def deplacer_gauche():
    """
    Actions à effectuer à l'appui de la touche directionnelle 'gauche'.
    :return: None
    """
    turtle.onkeypress(None, "Left")
    target = (position[0], position[1] - 1)
    if int(matrix[target[0]][target[1]]) == 0:
        one_move(deplacer_gauche, "Left", target)
        position[1] -= 1
    elif int(matrix[target[0]][target[1]]) == 1:
        deplacer_perso()
    elif int(matrix[target[0]][target[1]]) == 2:
        case_win(deplacer_gauche, "Left", target)
    elif int(matrix[target[0]][target[1]]) == 3:
        case_porte(deplacer_gauche, "Left", target)
    elif int(matrix[target[0]][target[1]]) == 4:
        case_objet(deplacer_gauche, "Left", target)


def deplacer_perso():
    """
    Gère les déplacements du personnage.
    :return: None
    """
    turtle.listen()
    turtle.onkeypress(deplacer_bas, "Down")
    turtle.onkeypress(deplacer_haut, "Up")
    turtle.onkeypress(deplacer_droite, "Right")
    turtle.onkeypress(deplacer_gauche, "Left")
    turtle.mainloop()


turtle.tracer(False)        # Permet une exécution instantanée de toutes les actions de la tortue.
afficher_plan(matrix)       # Construit le château.
tracer_personnage(POSITION_DEPART)      # Initialise le personnage.
deplacer_perso()           # Active les commandes de déplacement du personnage.
