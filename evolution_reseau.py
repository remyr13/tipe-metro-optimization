from reseau2 import*
from creation_du_reseau import *
import random
from time import perf_counter_ns
import numpy as np

# objectif de ce code : faire des fonctions qui permettent de partir d'un reseau
# mauvais (ou aucun reseau) et de l'ameliorer (jusqu'a obtenir un reseau ideal)


def trouve_moy(max_x,max_y,nb_point):

    somme = 0
    for k in range(500):
        coordonnees = cree_coordonnees_random(max_x,max_y,3,nb_point)
        proto = cree_proto_reseau_connexe(coordonnees,3)
        somme += proto.inefficacite()
    return (somme/500)


def insert_station_ligne(position,station,ligne_nom,meilleur,reseau,est_circ = False):

    reseau_test = reseau.copy()
    max = len(reseau_test.lignes[ligne_nom])
    if est_circ:
        max -= 1 # on veux enlever la derniere station qui permet de faire boucler la ligne

    ligne_lst = reseau_test.lignes[ligne_nom][:max]
    nlle_ligne = ligne_lst[:position] + [station] + ligne_lst[position:]

    if est_circ : nlle_ligne.append(nlle_ligne[0])
    reseau_test.ajoute_ligne_tot(ligne_nom,nlle_ligne)
    inefficacite_test = reseau_test.inefficacite()
    if inefficacite_test < meilleur[1] :
        meilleur = (reseau_test, inefficacite_test)
    return(meilleur)


def evolution_glouton1(reseau):


    inefficacite_dep = reseau.inefficacite()
    meilleur = (reseau,inefficacite_dep)
    for ligne in reseau.lignes:
        ligne_lst = reseau.lignes[ligne]
        nb_station = len(reseau.lignes[ligne])

        # test sur le suppr de station
        for station in ligne_lst:
            reseau_test = reseau.copy()
            reseau_test.suppr_stations_ligne(ligne,station)
            if reseau_test.est_connexe():
                if reseau_test.inefficacite() < meilleur[1]:
                    inefficacite_test = reseau_test.inefficacite()
                    meilleur = ( reseau_test, inefficacite_test)

        # test sur l'ajout de station
        for position in range(1,nb_station):
            for station in reseau.coordonnees:
                if station != ligne_lst[position] and station != ligne_lst[position -1]:
                    meilleur = insert_station_ligne(position,station,ligne,meilleur,reseau)
        for station in reseau.coordonnees:
            if len(ligne_lst) > 0:
                if station != ligne_lst[0]:
                    meilleur = insert_station_ligne(0,station,ligne,meilleur,reseau)
                if station != ligne_lst[-1]:
                    meilleur = insert_station_ligne(nb_station + 1,station,ligne,
                            meilleur,reseau)
    return meilleur


def evolution_glouton2(reseau):

    # ici, une meilleure maniere de rajouter des stations dans les lignes...

    inefficacite_dep = reseau.inefficacite()
    meilleur = (reseau,inefficacite_dep)
    for ligne in reseau.lignes:
        ligne_lst = reseau.lignes[ligne]
        nb_station = len(reseau.lignes[ligne])

        # test sur le suppr de station
        for station in ligne_lst:
            reseau_test = reseau.copy()
            reseau_test.suppr_stations_ligne(ligne,station)
            if reseau_test.est_connexe():
                if reseau_test.inefficacite() < meilleur[1]:
                    inefficacite_test = reseau_test.inefficacite()
                    meilleur = ( reseau_test, inefficacite_test)

        # test sur l'ajout de station
        for position in range(0,nb_station+1):
            for station in reseau.coordonnees:
                if station not in reseau.lignes[ligne]:
                    meilleur = insert_station_ligne(position,station,ligne,meilleur,reseau)
    return meilleur


def test_suppr_station(reseau,ligne,meilleur):

    # test sur le suppr de station
    for station in reseau.lignes[ligne]:
        reseau_test = reseau.copy()
        reseau_test.suppr_stations_ligne(ligne,station)
        if reseau_test.est_connexe():
            inefficacite = reseau_test.inefficacite()
            if inefficacite < meilleur[1]:
                inefficacite_test = inefficacite
                meilleur = ( reseau_test, inefficacite_test)
        return meilleur


def test_ajout_station(reseau,ligne,meilleur):

    est_circulaire = ((reseau.lignes[ligne][0] == reseau.lignes[ligne][-1])
            and len(reseau.lignes[ligne]) > 2)
            # true si c'est une ligne circulaire false sinon
    cte = 1
    if est_circulaire : cte = 0
    for position in range(0,len(reseau.lignes[ligne])+cte):
        for station in reseau.coordonnees:
            if station not in reseau.lignes[ligne]:
                meilleur = insert_station_ligne(position,station,ligne,meilleur,
                        reseau,est_circulaire)
    return meilleur

def evolution_glouton3(reseau):

    # la difference avec glouton 2, c'est que la on peut echanger des stations
    # dans une ligne, ces deux stations doivent etre a cote
    inefficacite_dep = reseau.inefficacite()
    meilleur = (reseau,inefficacite_dep)
    for ligne in reseau.lignes:
        ligne_lst = reseau.lignes[ligne]

        # test sur le suppr de station
        meilleur = test_suppr_station(reseau,ligne,meilleur)

        # test sur l'ajout de station
        meilleur = test_ajout_station(reseau,ligne,meilleur)

        # test sur l'inversion de stations
        est_circ = False
        if len(ligne_lst) > 2:
            if ligne_lst[0] == ligne_lst[-1]:
                est_circ = True
                ligne_lst = ligne_lst[:-1]
            for position in range(len(ligne_lst)-1):
                nlle_ligne = ligne_lst[:position] + [ligne_lst[position+1],
                        ligne_lst[position]] + ligne_lst[position+2:]
                if est_circ :
                    nlle_ligne.append(nlle_ligne[0])
                reseau_test = reseau.copy()
                reseau_test.ajoute_ligne_tot(ligne,nlle_ligne)
                inefficacite_test = reseau_test.inefficacite()
                if inefficacite_test < meilleur[1] :
                    meilleur = (reseau_test, inefficacite_test)
        est_circ = False
    return meilleur


def evolution_glouton4(reseau):

    # la difference avec glouton3 c'est que la, on teste tous les echangements
    # possibles de stations sur une ligne.
    inefficacite_dep = reseau.inefficacite()
    meilleur = (reseau,inefficacite_dep)
    for ligne in reseau.lignes:
        ligne_lst = reseau.lignes[ligne]

        # test sur le suppr de station
        meilleur = test_suppr_station(reseau,ligne,meilleur)

        # test sur l'ajout de station
        meilleur = test_ajout_station(reseau,ligne,meilleur)

        # test sur l'inversion de stations
        est_circ = False
        if len(ligne_lst) > 2:
            if ligne_lst[0] == ligne_lst[-1] :
                ligne_lst = ligne_lst[:-1]
                est_circ = True
            for position1 in range(len(ligne_lst)-1):
                for position2 in range(position1 + 1,len(ligne_lst)):
                    nlle_ligne = ligne_lst[:position1] + [
                            ligne_lst[position2]] + ligne_lst[position1 +
                            1:position2] + [ligne_lst[position1]] + ligne_lst[position2+1:]
                    if est_circ :
                        nlle_ligne.append(nlle_ligne[0])

                    reseau_test = reseau.copy()
                    reseau_test.ajoute_ligne_tot(ligne,nlle_ligne)
                    inefficacite_test = reseau_test.inefficacite()
                    if inefficacite_test < meilleur[1] :
                        meilleur = (reseau_test, inefficacite_test)
        est_circ = False
    return meilleur


def evolution_pas_a_pas(reseau1,file_name = '',version=3):

    if not version in [1,2,3,4] : print("la version choisie n'existe pas")
    tic = perf_counter_ns()
    inefficacite1 = 0
    inefficacite2 = reseau1.inefficacite()
    generation = 0
    if file_name != '':
        fichier = open(file_name,'w')
        fichier.write(f"{reseau1.coordonnees}\n\n\n")
        print(f"\n\n\{reseau1.lignes}\n\n\n")
    while inefficacite1 != inefficacite2:
        print('test1')
        inefficacite1 = inefficacite2
        if version == 1 : reseau1, inefficacite2 = evolution_glouton1(reseau1)
        if version == 2 : reseau1, inefficacite2 = evolution_glouton2(reseau1)
        if version == 3 : reseau1, inefficacite2 = evolution_glouton3(reseau1)
        if version == 4 : reseau1, inefficacite2 = evolution_glouton4(reseau1)
        print(inefficacite2)
        print(reseau1.lignes)
        print(generation)
        generation += 1
        if file_name != '':
            fichier.write(f"{inefficacite2}\n{reseau1.lignes}\n{generation}\n\n")
    reseau1.dessine_reseau()
    toc = perf_counter_ns()
    if file_name != '':
        fichier.write(f"{toc-tic}")
        fichier.close()
    return(reseau1)


def mix_evolutions_pas_a_pas(reseau1,file_name = '',liste_versions = [3]):

    tic = perf_counter_ns()
    inefficacite1 = 0
    inefficacite2 = reseau1.inefficacite()
    generation = 0
    if file_name != '':
        fichier = open(file_name,'w')
        fichier.write(f"{reseau1.coordonnees}\n{reseau1.transfere}\n\n")
    for version in liste_versions:
        while inefficacite1 != inefficacite2:
            if not version in [1,2,3,4] : print("la version choisie n'existe pas")
            inefficacite1 = inefficacite2
            if version == 1 : reseau1, inefficacite2 = evolution_glouton1(reseau1)
            if version == 2 : reseau1, inefficacite2 = evolution_glouton2(reseau1)
            if version == 3 : reseau1, inefficacite2 = evolution_glouton3(reseau1)
            if version == 4 : reseau1, inefficacite2 = evolution_glouton4(reseau1)
            generation += 1
            if file_name != '':
                fichier.write(f"{inefficacite2} {reseau1.distances_totales()}"
                              f"{reseau1.longueurs_totale()}\n{reseau1.lignes}"
                              f"\n{generation}\n\n")
        if generation == 1 or generation == 0 : print('Nul!')
    toc = perf_counter_ns()
    if file_name != '':
        fichier.write(f"{toc-tic}")
        fichier.close()
    return(reseau1)


def evolution_totale(file_name,version,nb_ligne,coordonnees):

    proto = cree_proto_reseau_connexe_random(coordonnees,nb_ligne)
    reseau_final = evolution_pas_a_pas(proto,file_name,version)
    return(reseau_final)


def trouver_boucle(reseau,ligne):

    lst_pb = []
    # une liste ou on enregistre sous forme de 2-uplet les  emplacements ou
    # ca croise
    # le premier indice est l'indice de la station AVANT la boucle et le
    # deuxieme est celui de la derniere station encore DANS la boucle
    coord_segments = {}
    # un dico qui enregistre les (m,p,a,b) des coordonees des segments [a,b] y = m.x + p

    ligne_lst = reseau.lignes[ligne].copy()
    if len(ligne_lst) > 1:
        for k in range(len(ligne_lst)-1):
            a,b = reseau.coordonnees[ligne_lst[k]] , reseau.coordonnees[ligne_lst[k+1]]
            if (b[0]-a[0]) == 0 : m = (b[1]-a[1])/1e-5
            else :                m = (b[1]-a[1])/(b[0]-a[0])
            p = a[1] - m*a[0]
            coord_segments[k] = (m,p,a,b)
            for j in range(k-1):
                # on calcule l'abscisse d'intersection pour tous les couples
                # possibles (mais pas un segment qui touche...) et on regardera
                # si cet abscisse est dans l'un des deux segments...
                m_j,p_j = coord_segments[j][0] , coord_segments[j][1]
                a_j,b_j = coord_segments[j][2] , coord_segments[j][3]
                x_inter = (p_j-p)/(m-m_j)
                if x_inter > min(a[0],b[0]) and x_inter < max(a[0],b[0]):
                    if x_inter > min(a_j[0],b_j[0]) and x_inter < max(a_j[0],b_j[0]):
                        lst_pb.append((j,k,x_inter))
    return lst_pb


def demeler(reseau,portion_lst):

    def prod_scalaire(vect1,vect2): return(vect1[0]*vect2[0]+vect1[1]*vect2[1])

    def return_mini_dico(dico):

        mini = (np.inf,'')
        for key in dico:
            if dico[key] < mini[0]: mini = (dico[key],key)
        return mini[1]

    # on donne un portion de la liste on va demeler (enlever la boucle de) cette portion...
    station_or , station_arr = portion_lst[0], portion_lst[-1]
    vecteur = (reseau.coordonnees[station_arr][0] - reseau.coordonnees[station_or][0],
               reseau.coordonnees[station_arr][1] - reseau.coordonnees[station_or][1])
    projections = {}
    for station in portion_lst:
        vect_station = (reseau.coordonnees[station][0]-reseau.coordonnees[station_or][0],
                        reseau.coordonnees[station][1]-reseau.coordonnees[station_or][1])
        projections[station] = prod_scalaire(vecteur,vect_station)
    # projections = { station : prod_scalaire(vecteur,reseau.coordonnees[station])
    # for station in portion_lst[1:-1] }
    new_portion_lst = []
    while projections:
        mini = return_mini_dico(projections)
        del projections[mini]
        new_portion_lst.append(mini)
    return new_portion_lst


def inverser_ordre(portion_lst):

    new_portion = [ portion_lst[-k] for k in range(1,len(portion_lst)+1) ]
    return new_portion


def demeler_reseau_tot(reseau):

    reseau_mod = reseau.copy()
    for ligne in reseau.lignes:
        continuer = False
        essai = 0
        while (not continuer) and (essai<100):
            reseau2 = reseau_mod.copy()
            ligne_lst = reseau2.lignes[ligne]
            coords_boucles = trouver_boucle(reseau2,ligne)
            if coords_boucles != []:

                a_demeler = ligne_lst[ coords_boucles[0][0] + 1 :
                        coords_boucles[0][1] + 1 ]
                new_portion = inverser_ordre(a_demeler)
                new_ligne = ligne_lst[:coords_boucles[0][0] +1
                        ] + new_portion + ligne_lst[coords_boucles[0][1]+1:]
                reseau2.ajoute_ligne_tot(ligne,new_ligne)
            else : continuer = True
            reseau_mod = reseau2.copy()
            essai+=1
    return reseau2
