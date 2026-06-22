import random
from time import perf_counter_ns
import numpy as np
from reseau2 import *

# ce code est la pour traiter tout ce qui est en rapport avec la creation
# prealable du reseau


def distance_eu(p1,p2): return(np.sqrt( (p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 ))


def cree_coordonees_random(nb_station = 15, x_max = 10, y_max = 10, poids_max=3):

    coordonnees = {}
    for k in range(nb_station):
        nom = f"{k}"
        x = random.uniform(0,x_max)
        y = random.uniform(0,y_max)
        if poids_max > 0 : poids = random.uniform(0,poids_max)
        else : poids = 1
        coordonnees[nom] = (x,y,poids)
    return coordonnees


def cree_coord_centre(nb_station,dist_max,para_poids = (1,True)):

    ''' explication de para_poids :
    para_poids[0] est le poids max , fixe a 0 si on ne veux pas de variation du
    poids
    para_poids[1] pour si on veux que le poids soit inversement proportionne a
    la distance au centre, ce qui semble raisonnable... '''

    coord = {}
    for k in range(nb_station):
        nom = f"{k}"
        alpha = random.uniform(0,2*np.pi)
        r = random.uniform(0,dist_max)
        x = r * np.cos(alpha)
        y = r * np.sin(alpha)
        poids = 1
        if para_poids[0] != 0:
            if para_poids[1]: poids = para_poids[0]/r
            else : poids = random.uniform(0,para_poids[0])
        coord[nom] = (x,y,poids)
    return coord


def cree_coord_poids_centre(nb_station,max_range,a=1):

    # k est l'argument pour maitriser a quel point quand on s'eloigne, le poids diminue.
    coord = {}
    K = 0.5
    for i in range(nb_station):
        nom = f"{i}"
        dist = max_range + 1
        while dist > max_range:
            x = random.uniform(-max_range,max_range)
            y = random.uniform(-max_range,max_range)
            dist = np.sqrt(x**2 + y**2)
        p = a*np.exp(-K*dist)
        coord[nom] = (float(x),float(y),float(p))
    return coord


def cherche_station_centre(coordonnees):

    # on cherche le "centre" du graphe

    somme_x , somme_y , poids_total = 0,0,0
    for station in coordonnees:
        poids = 1
        if len(coordonnees[station]) == 3: poids = coordonnees[station][2]
        somme_x += coordonnees[station][0]*poids
        somme_y += coordonnees[station][1]*poids
        poids_total += poids

    moyenne_x, moyenne_y =  somme_x / poids_total , somme_y / poids_total

    min = (-1,'')
    for station in coordonnees:
        if min[0] == -1 :
            min = (distance_eu((moyenne_x,moyenne_y),coordonnees[station]) ,station)
        else:
            if min[0] > distance_eu((moyenne_x,moyenne_y),coordonnees[station]):
                min = ( distance_eu((moyenne_x,moyenne_y),
                        coordonnees[station]) ,station)
    return (min[1],(moyenne_x,moyenne_y))


def cart2polaire(coordonnees,centre):

    coord_pol = {}
    for station in coordonnees:
        r = distance_eu(centre,coordonnees[station])
        if coordonnees[station] == centre : theta = 0
        # on fixe la convention que un point au centre sera d'angle 0
        else:
            cte = 0
            if coordonnees[station][0] < centre[0] :
                if coordonnees[station][1] > centre[1]: cte = + np.pi
                else : cte = -np.pi
            theta = np.arctan((coordonnees[station][1] -
                    centre[1])/(coordonnees[station][0] - centre[0])) + cte

        if len(coordonnees[station]) == 3 : poids = coordonnees[station][2]
        else: poids = 1
        coord_pol[station] = (r,theta,poids)
    return coord_pol


def recherche_min_dico_coord_polaire(dico,grandeur = 1):

    ''' grandeur =  1 si on cherche le minimum des r
    OU 2 si on cherche le minimum des theta '''

    min = ('',-10,-10)
    for key in dico:
        if min[grandeur] == -10 : min = (key,dico[key][0],dico[key][1])
        elif dico[key][grandeur-1] < min[grandeur]:
            min = (key,dico[key][0],dico[key][1])
    return min


def fusion_lignes(lignes):
    # finalement on va directement fusionner dans le code principal
    # ici c'est pour refusionner les lignes

    tab_num_2_couleur = {0:'rouge',1:'vert',2:'bleu',3:'violet',
                         4:'orange',5:'rose',6:'cyan',7:'marron'}

    nouvelles_lignes = {}
    n = len(lignes)
    i = 0
    for ligne in lignes:
        if i < n/2 :
            m,signe = i, 1
        else :
            m,signe = n-i-1, -1

        if m >= len(tab_num_2_couleur) : nom_ligne = f"{m}"
        else : nom_ligne = tab_num_2_couleur[m]

        if signe == 1 :
            nouvelles_lignes[nom_ligne] = []
            for k in range(1,len(lignes[ligne])):
                nouvelles_lignes[nom_ligne].append(lignes[ligne][-k])
        else :
            for k in range(len(lignes[ligne])):
                nouvelles_lignes[nom_ligne].append(lignes[ligne][k])
        i+=1
    return nouvelles_lignes


def creer_lignes_droites_pour_etoile(coord_pol,nb_lignes_droites,station_centre):

    coord_pol_a_vider = coord_pol.copy()
    lignes = {}
    for k in range(nb_lignes_droites):
        nom_ligne1 = f"{k}a"
        nom_ligne2 = f"{k}b"
        lignes[nom_ligne1], lignes[nom_ligne2] = [station_centre], [station_centre]
    del coord_pol_a_vider[station_centre]

    while len(coord_pol_a_vider) != 0 :
        # on choisi la station avec le rayon avec le centre le plus petit
        mini = (-1,'')
        for station in coord_pol_a_vider:
            if mini[0] == -1 : mini = (coord_pol[station][0],station)
            elif coord_pol[station][0] < mini[0] :
                mini = (coord_pol[station][0],station)
        station_choisie = (coord_pol[mini[1]][0],coord_pol[mini[1]][1], mini[1])
        # maintenant on va chercher ou va la station avec le rayon le plus petit.
        mini = (-1,'')

        for ligne in lignes:
            terminus_nom = lignes[ligne][-1]
            terminus = (coord_pol[terminus_nom][0],coord_pol[terminus_nom][1])
            mini_delta_theta = min(np.abs( station_choisie[1] - terminus[1]),10,
                    np.abs(station_choisie[1] + 2*np.pi - terminus[1]),
                    np.abs(station_choisie[1] - 2*np.pi - terminus[1]))

            if mini[0] == -1 : mini = (mini_delta_theta,ligne)
            elif mini_delta_theta < mini[0] : mini = (mini_delta_theta,ligne)
        ligne_choisie = mini[1]
        lignes[ligne_choisie].append(station_choisie[2])
        del coord_pol_a_vider[station_choisie[2]]
    return(fusion_lignes(lignes))
    # ca c'est un algo pour fusionner toutes les lignes, on va plutot faire un
    # algo qui fusionne que les lignes specifique qu on lui a dit (ca evitera
    # d'avoir plein de lignes vides)


def creer_lignes_circulaires_pour_etoile(coord_pol,nb_lignes_circulaire, nb_lignes_droites):

    ligne = []
    coord_pol_a_vider = coord_pol.copy()
    mini0 = (-10,'')
    for station in coord_pol_a_vider:
        if mini0[0] == -10 or mini0[0] > coord_pol_a_vider[station][1]:
                mini0 = (coord_pol_a_vider[station][1],station)
    ligne = [mini0[1]]
    del coord_pol_a_vider[mini0[1]]
    while len(coord_pol_a_vider) != 0 :
        mini = (-10,'')
        for station in coord_pol_a_vider:
            if mini[0] == -10 or mini[0] > coord_pol_a_vider[station][1] :
                 mini = (coord_pol_a_vider[station][1],station)
        ligne.append(mini[1])
        del coord_pol_a_vider[mini[1]]
    ligne.append(mini0[1])
    tab_num_2_couleur = {0:'rouge',1:'vert',2:'bleu',3:'violet',
                         4:'orange',5:'rose',6:'cyan',7:'marron'}
    lignes = {}
    for num in range(nb_lignes_droites,nb_lignes_droites + nb_lignes_circulaire):
        if num >= len(tab_num_2_couleur) : nom_ligne = f"{num}"
        else : nom_ligne = tab_num_2_couleur[num]
        lignes[nom_ligne] = ligne.copy()
    return lignes

# l'idee est de faire plus des sortes d anneaux, on range les stations par ordre
# croissant de rayon puis on prends arbitrairement que une certaine partie
# predefinie. En fait l'idee serai de trier ces stations puis apres de pouvoir
# en recpuperer que UNE PARTIE pour pouvoir consistuer notre ligne circulaire


def creer_lignes_circ_bis(coord_pol,nb_circ,nb_droit,anneau_ext = True,anneau_int = True):

    coord_pol_a_vider = coord_pol.copy()
    liste_triee = []
    while coord_pol_a_vider:
        mini = recherche_min_dico_coord_polaire(coord_pol_a_vider,1)
        # on trie par r
        liste_triee.append(mini[0])
        del coord_pol_a_vider[mini[0]]

    if anneau_ext : nb_circ += 1
    # anneau_X est True si en effet, on ne le met pas et False si en fait il y est
    if anneau_int : nb_circ += 1
    # anneau_ext pour celui a l'exterieur et anneau_int pour celui a l'interieur

    nb_station = len(liste_triee)/nb_circ
    lignes = {}
    premier = 0
    if anneau_int : premier = 1
    for k in range(nb_circ):
        stations_r_select = {}
        liste_triee2 = []
        for i in range(int(k*nb_station),int((k+1)*nb_station)):
            stations_r_select[liste_triee[i]] = coord_pol[liste_triee[i]]
        while stations_r_select:
            mini = recherche_min_dico_coord_polaire(stations_r_select,2)
            # parmis les stations de la "tranche" qui nous interesse, on les
            # tries en fonction de leur angle
            liste_triee2.append(mini[0])
            del stations_r_select[mini[0]]

        if k > premier:
            lignes[k-1].append(liste_triee2[0])
        if k>= premier:
            lignes[k] = liste_triee2.copy()

    lignes_f = {}
    if anneau_ext: nb_circ -= 1
    tab_num_2_couleur = {0:'rouge',1:'vert',2:'bleu',3:'violet',
                         4:'orange',5:'rose',6:'cyan',7:'marron'}
    for k in range(premier,nb_circ):
        if k+nb_droit < len(tab_num_2_couleur) :
            nom_ligne = tab_num_2_couleur[k+nb_droit]
        else:
            nom_ligne = f"{k}"
        lignes_f[nom_ligne] = lignes[k] + [lignes[k][0]]
    return lignes_f


def proto_reseau_etoile(coordonnees,nb_lignes_droites,nb_lignes_circulaire = 0,
        anneau_ext = False , anneau_int = False):

    station_centre, centre = cherche_station_centre(coordonnees)
    station_centre_coord = coordonnees[station_centre]
    coord_pol = cart2polaire(coordonnees,station_centre_coord)

    # partie creation des lignes droites
    lignes_finales_droites = creer_lignes_droites_pour_etoile(coord_pol,
            nb_lignes_droites,station_centre)

    # puis creation des lignes circulaires
    if nb_lignes_circulaire != 0:
        lignes_circulaires_finales = creer_lignes_circ_bis(coord_pol,
                nb_lignes_circulaire,nb_lignes_droites,anneau_ext,anneau_int)
    else : lignes_circulaires_finales = {}

    lignes_finales = lignes_finales_droites.copy()
    for ligne in lignes_circulaires_finales:
        lignes_finales[ligne] = lignes_circulaires_finales[ligne].copy()
    return(lignes_finales)


def cree_proto_reseau_connexe(coordonnees,nb_ligne):

    proto = creer_reseau_vide(coordonnees)
    premiere_ligne = [ station for station in coordonnees ]
    tab_num_2_couleur = {0:'rouge',1:'vert',2:'bleu',3:'violet',
                         4:'orange',5:'rose',6:'cyan',7:'marron'}
    for k in range(0,nb_ligne):
        if k >= len(tab_num_2_couleur) : nom_ligne = f"{k}"
        else : nom_ligne = tab_num_2_couleur[k]
        proto.ajoute_ligne_tot(nom_ligne,premiere_ligne)
    lignes_cte = proto_reseau_etoile(coordonnees,len(proto.lignes),0)
    reseau_cte = Reseau2(coordonnees,lignes_cte)
    ctes = (reseau_cte.distances_totales(),reseau_cte.longueurs_totale())
    return Reseau2(coordonnees,proto.lignes,proto.transfere,ctes)


def get_constantes_coord(coordonnees,nb_lignes):

    # lignes_cte = proto_reseau_etoile(coordonnees,nb_lignes,0) # autre possibilite
    lignes_cte = proto_reseau_etoile(coordonnees,1,0)
    reseau_cte = Reseau2(coordonnees,lignes_cte)
    ctes = (reseau_cte.distances_totales(),reseau_cte.longueurs_totale())
    return ctes


def creer_reseau_avec_lignes(coordonees,lignes):

    ctes = get_constantes_coord(coordonees,len(lignes))
    proto = Reseau2({},{})
    reseau = Reseau2(coordonees,lignes,proto.transfere,ctes)
    return reseau


def cree_proto_reseau_etoile(coordonnees,nb_lignes_drt,nb_lignes_circ,
        anneau_ext = False,anneau_int = False):

    # il est interdit de prendre aucune ligne droite, ca ne marche pas

    proto = creer_reseau_vide(coordonnees)
    ctes = get_constantes_coord(coordonnees,nb_lignes_drt+nb_lignes_circ)
    lignes = proto_reseau_etoile(coordonnees,nb_lignes_drt,nb_lignes_circ,
            anneau_ext,anneau_int)
    return(Reseau2(coordonnees,lignes,proto.transfere,ctes))


def creer_lignes_pour_cadrillage(coordonees,nb_lignes,maxi,mini,etat):

    # etat = 0 pour les lignes horizontales etat = 1 pour les lignes verticales

    def trier_croiss_ligne(lst):

        etat_a_trier = 0
        if etat == 0 : etat_a_trier = 1
        triee = []
        while lst != []:
            mini = (coordonees[lst[0]][etat_a_trier],0)
            for k in range(len(lst)):
                if mini[0] > coordonees[lst[k]][etat_a_trier]:
                    mini = (coordonees[lst[k]][etat_a_trier],k)
            elt = lst.pop(mini[1])
            triee.append(elt)
        return triee

    delta = (maxi + 1 - mini)/nb_lignes
    print(delta,mini,maxi)
    lignes = { k:[] for k in range(nb_lignes) }
    print(lignes)

    # dans un premier temps, on met toutes les stations dans la bonne ligne

    for station in coordonees:
        coord = coordonees[station][etat] - mini
        ligne = int(coord/delta)
        print(coord,ligne)
        lignes[ligne].append(station)

    # maintenant que toutes les stations sont dans leur ligne correspondante,
    # il faut trier ces stations par x croissant

    for ligne in lignes: lignes[ligne] = trier_croiss_ligne(lignes[ligne])
    return lignes


def creer_lignes_tot_cadrillage(coordonees,nb_lignes_drt):

    # nouvelle maniere de faire un proto reseau qui evite le probleme de la
    # station centrale
    # on va essayer de repartir correctement entre horizontal et vertical
    # les lignes pour eviter

    if nb_lignes_drt != 1:
        mini_hor , maxi_hor , mini_vert , maxi_vert = np.inf , - np.inf , np.inf , - np.inf

        for station in coordonees:
            if coordonees[station][0] > maxi_hor : maxi_hor = coordonees[station][0]
            if coordonees[station][0] < mini_hor : mini_hor = coordonees[station][0]
            if coordonees[station][1] > maxi_vert : maxi_vert = coordonees[station][1]
            if coordonees[station][1] < mini_vert : mini_vert = coordonees[station][1]
        ratio = round((maxi_vert - mini_vert) / (maxi_hor - mini_hor) )
        nb_hor = nb_lignes_drt / (1+ ratio)
        if nb_hor < 1: nb_hor,nb_vert = 1, nb_lignes_drt -1
        elif nb_hor > nb_lignes_drt - 1 : nb_vert, nb_hor = 1, nb_lignes_drt -1
        else:
            nb_hor = round(nb_hor)
            nb_vert = nb_lignes_drt - nb_hor
        print(nb_hor,nb_vert)
        lignes_hor = creer_lignes_pour_cadrillage(coordonees,nb_hor,
                maxi_hor,mini_hor,0)
        lignes_vert = creer_lignes_pour_cadrillage(coordonees,nb_vert,maxi_vert,
                mini_vert,1)
        lignes_tot = { ligne:lignes_hor[ligne] for ligne in lignes_hor }

        for ligne in lignes_vert: lignes_tot[ligne + nb_hor] = lignes_vert[ligne]

        lignes_finales = {}
        tab_num_2_couleur = {0:'rouge',1:'vert',2:'bleu',3:'violet',
                             4:'orange',5:'rose',6:'cyan',7:'marron'}
        for ligne in lignes_tot:
            if ligne < len(tab_num_2_couleur) :
                lignes_finales[tab_num_2_couleur[ligne]] = lignes_tot[ligne]
            else : lignes_finales[ligne] = lignes_tot[ligne]
    return lignes_finales


def creer_reseau_cadrillage(coordonnees,nb_lignes):

    proto = creer_reseau_vide(coordonnees)
    lignes = creer_lignes_tot_cadrillage(coordonnees,nb_lignes)
    ctes = get_constantes_coord(coordonnees,nb_lignes)
    return(Reseau2(coordonnees,lignes,proto.transfere,ctes))

def epurer_reseau(reseau):

    lignes = reseau.lignes
    lignes_finales = {}
    for ligne in lignes:
        lst_or = lignes[ligne]
        if lst_or != []:
            lst_final = [lst_or[0]]
            for station in lst_or:
                if lst_final[-1] != station:
                    lst_final.append(station)
            lignes_finales[ligne] = lst_final
    res = Reseau2(reseau.coordonnees,lignes_finales,reseau.transfere,
            (reseau.cte_distance,reseau.cte_longueur),reseau.cte_stop)
    return res
