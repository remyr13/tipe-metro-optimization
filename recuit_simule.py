from reseau2 import*
import random
from time import perf_counter_ns
import numpy as np
from creation_du_reseau import *

# ici c'est pour faire la 2eme partie avec du recuit simule car on est arrive au
# bout des capacites de la logique gloutonne...

# il faut dans un premier temps faire une fonction qui genere un nombre aleatoire
# et qui y associe une modification du reseau...


def est_circ (ligne_lst) :

    if len(ligne_lst)>1:
        return(ligne_lst[0] == ligne_lst[-1])
    else : return(False)


def modif_suppr(reseau):

    nb_stations_lignes = 0
    for ligne in reseau.lignes:
        if est_circ(ligne):
            nb_stations_lignes += (len(reseau.lignes[ligne])-1)
        else:
            nb_stations_lignes += len(reseau.lignes[ligne])
    essai = 0
    while essai < 10000:
        r = int(random.random()*nb_stations_lignes)
        reseau_test = reseau.copy()

        for ligne in reseau.lignes:
            epsilon = 0
            if est_circ(ligne) : epsilon = 1
            if r < len(reseau.lignes[ligne]) - epsilon and r >= 0 :
                reseau_test = reseau.copy()
                reseau_test.suppr_stations_ligne(ligne,reseau.lignes[ligne][r])
                if reseau_test.est_connexe():
                    return reseau_test
            else : r -= (len(reseau.lignes[ligne]) - epsilon)
        essai += 1
        # print('aucune station trouvee ne permet de supprimer une station')
        return reseau


def modif_ajout(reseau):

    ''' la philosophie de cet algo est de choisir une station aleatoirement, de
    choisir un emplacement entre deux stations reliees. Enfin, on verifie si
    l ajout de la station a cet emplacement respecte les regles d un reseau (la
    station ne doit pas etre deja sur la ligne '''

    nb_places_lignes = 0
    for ligne in reseau.lignes:
        if est_circ(reseau.lignes[ligne]):
            nb_places_lignes += (len(reseau.lignes[ligne])) - 1
        else : nb_places_lignes += ((len(reseau.lignes[ligne]))+1)
    test = 0
    while test < 500:
        place_random = int(random.random()*nb_places_lignes)
        station_random = int(random.random() * (len(reseau.coordonnees)))
        station = list(reseau.coordonnees)[station_random]

        for ligne in reseau.lignes:
            ligne_lst_or = reseau.lignes[ligne].copy() # or pour original
            if est_circ(ligne_lst_or):
                if (place_random >= 0 and place_random < len(ligne_lst_or) - 1
                        and station not in reseau.lignes[ligne]):
                    reseau_test = reseau.copy()
                    ligne_lst = ligne_lst_or[:place_random +1] + [station] + ligne_lst_or[place_random+1:]
                    reseau_test.ajoute_ligne_tot(ligne,ligne_lst)
                    return reseau_test

                else : place_random -= (len(ligne_lst_or) - 1)
            else:
                if (place_random >= 0 and place_random < len(ligne_lst_or) + 1
                        and station not in reseau.lignes[ligne]):
                    reseau_test = reseau.copy()
                    ligne_lst = ligne_lst_or[:place_random] + [
                            station] + ligne_lst_or[place_random:]
                    reseau_test.ajoute_ligne_tot(ligne,ligne_lst)
                    return reseau_test
                else : place_random -= (len(ligne_lst_or) + 1)
        test += 1
    # print("trop d'essais pour essayer de rajouter une station a une ligne")
    return reseau


def modif_echange(reseau):

    essai = 0
    while essai < 1000:
        ligne_random = list(reseau.lignes)[int(random.random() * (len(reseau.lignes)))]
        ligne_lst = reseau.lignes[ligne_random].copy()
        if len(ligne_lst) > 1:
            circ = est_circ(ligne_lst)
            ligne_lst_test = ligne_lst.copy()
            if circ : ligne_lst_test = ligne_lst_test[:-1]
            station1_rng = int(random.random() * (len(ligne_lst_test)))
            station2_rng = int(random.random() * (len(ligne_lst_test)))
            if station2_rng != station1_rng :
                station1 = min(station1_rng,station2_rng)
                station2 = max(station1_rng,station2_rng)
                stat1_n, stat2_n = ligne_lst_test[station1],ligne_lst_test[station2]
                ligne_lst_test = ligne_lst_test[:station1] + [
                        ligne_lst_test[station2]] + ligne_lst_test[station1+1:
                        station2] + [ligne_lst_test[station1]] + ligne_lst_test[
                        station2+1:]
                if circ : ligne_lst_test.append(ligne_lst_test[0])
                reseau_test = reseau.copy()
                reseau_test.ajoute_ligne_tot(ligne_random,ligne_lst_test)
                return(reseau_test)
        essai += 1
    print("probleme ? car toutes les lignes sont reduites a des singletons")


def modification(reseau,suppr = 1,ajout = 1,interchange = 1):

    ''' il y a des parametres pour gerer dans quelle proportion chaque
    modifications sera faite'''

    r = random.random() * (suppr+ajout+interchange)
    if r <= suppr:
        nouveau_reseau = modif_suppr(reseau)
    elif r <= suppr+ajout:
        nouveau_reseau = modif_ajout(reseau)
    else:
        nouveau_reseau = modif_echange(reseau)
    return nouveau_reseau


def evolution_rs1(reseau,file_name = '',nb_gen = 100,nb_essai = 100):

    tic = perf_counter_ns()
    if file_name != '':
        fichier = open(file_name,'w')
        fichier.write(f"{reseau.coordonnees}\n{reseau.transfere}\n\n")
    reseau_mod = reseau.copy()
    inefficacite_mod = reseau_mod.inefficacite()
    mini = (inefficacite_mod,reseau_mod.copy())

    for k in range(nb_gen):
        modifie1 = modification(reseau_mod)
        inefficacite1 = modifie1.inefficacite()
        for i in range(nb_essai):
            modifie2 = modification(reseau_mod)
            inefficacite2 = modifie2.inefficacite()
            if inefficacite2 < inefficacite1:
                modifie1 = modifie2.copy()
                inefficacite1 = inefficacite2
        reseau_mod = modifie1.copy()
        inefficacite_mod = inefficacite1
        if mini[0] > inefficacite1:
            mini = (inefficacite_mod,reseau_mod.copy())
        if file_name != '':
            fichier.write(f"{inefficacite_mod} {reseau_mod.distances_totales()}"
                          f"{reseau_mod.longueurs_totale()}\n"
                          f"{reseau_mod.lignes}\n{k}\n\n")
    toc = perf_counter_ns()

    if file_name != '':
        fichier.write(f"{toc-tic}")
        fichier.close()
    return (epurer_reseau(reseau_mod),epurer_reseau(mini[1]))


def evolution_rs2(reseau,nb_essais = 300,pertes = 0.99,nb_modifications = 1):

    reseau_mod = reseau.copy()
    inefficacite = reseau_mod.inefficacite()
    energie = (1.4)*inefficacite
    fini = False

    while not fini:
        energie *= pertes
        essai = 0
        reussi = False
        while essai < nb_essais:
            test2 = reseau_mod.copy()
            for k in range(nb_modifications):
                # possibilite de faire plusieurs modifications sur une seule
                # generation pour plus de transformation
                test1 = modification(test2)
                test2 = test1.copy()
            if test2.inefficacite() < energie:
                reseau_mod = test2.copy()
                inefficacite = test2.inefficacite()
                essai += nb_essais
                reussi = True
            else : essai += 1
        if not reussi : fini = True
    return(epurer_reseau(reseau_mod))


def evolution_vrai_rs(reseau,nb_essais = 300,limite_temperature = 0,
        debut_temperature = 0.00001,  pertes = 0.99, arret_auto = 0):

    ''' arret_auto est pour que le programme s arrete quand il y a trop d essais
    sans changer le reseau d affile, pour economiser du temps.
    arret_auto : int tq on ne depasse pas le nombre indique de generations sans
    changer. 0 pour dire que la fonctionnalite n est pas utilisee'''

    reseau_mod = reseau.copy()
    inefficacite_mod = reseau_mod.inefficacite()
    meilleur = (reseau_mod,inefficacite_mod)
    temperature = debut_temperature
    termine = False
    essai = 0
    nb_tests = 0
    inefficacites = []
    generations = []
    nb_total_tests = []
    ratio = debut_temperature/limite_temperature

    while not termine:

        test = modification(reseau_mod)
        inefficacite_test = test.inefficacite()
        delta_inefficacite = inefficacite_test - inefficacite_mod

        if inefficacite_test < inefficacite_mod :
            reseau_mod = test.copy()
            inefficacite_mod = inefficacite_test
            if abs(delta_inefficacite) > 1e-4 :
                nb_total_tests.append(nb_tests)
                nb_tests = 0
            if inefficacite_mod < meilleur[1]:
                meilleur = (reseau_mod,inefficacite_mod)
        else:
            proba = random.random()
            coef = np.exp(-delta_inefficacite/temperature)
            if proba < coef:
                reseau_mod = test.copy()
                inefficacite_mod = inefficacite_test
                if abs(delta_inefficacite) > 1e-4 :
                    nb_total_tests.append(nb_tests)
                    nb_tests = 0

        temperature *= pertes
        essai += 1
        nb_tests += 1

        if nb_essais != 0 :
            if essai%10 == 0 : print(essai/nb_essais,inefficacite_mod)
            if essai > nb_essai : termine = True
        if limite_temperature != 0 :
            if essai%20 == 0 :
                t = temperature/limite_temperature
                print(t,float(inefficacite_mod[1]), np.log(t)/np.log(ratio))
            if temperature < limite_temperature :  termine = True
        if limite_temperature == nb_essais == 0 and essai % 200 == 0:
            print(essai,inefficacite_test,meilleur[1],nb_tests,temperature)
        inefficacites.append(float(inefficacite_mod))
        generations.append(essai)
        if arret_auto > 0:
            if nb_tests >= arret_auto: termine = True
    return (meilleur,inefficacites,nb_total_tests)


def est_conforme(reseau):

    for ligne in reseau.lignes:
        liste_ligne = reseau.lignes[ligne].copy()
        rencontre = {}
        for i in range(len(liste_ligne)-1):
            if liste_ligne[i] in rencontre:
                print(i, liste_ligne[i], ligne)
                print(reseau.lignes)
                reseau.dessine_reseau()
                return False
            rencontre[liste_ligne[i]] = True
        if len(liste_ligne) != 0:
            if liste_ligne[-1] in rencontre and liste_ligne[-1] != liste_ligne[0]:
                print(ligne, liste_ligne)
                reseau.dessine_reseau()
                return False
    return True
