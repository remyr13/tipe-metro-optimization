import numpy as np
import matplotlib.pyplot as plt

## les types de donnes

# coordones = {station:(coordonee_x,coordonee_y,poids)}
# lignes    = {ligne:[liste_des_lignes]}
# adjacents = {station:{ligne:(les_2_stations_adjacentes,None pour le deuxieme si terminus)}}

## plusieurs fonctions utiles

def creer_reseau_vide(coordonnees): return(Reseau2(coordonnees,{},33,None))

## Principal

class Reseau2():

    ''' il faut que les stations n'apparaissent qu'une seule fois par ligne . Sauf dans le cas d'une ligne circulaire où la station est la premiere et la dernière de la ligne'''

    def __init__(self,coordonnees,lignes,transfere = 1.863,ctes_inneficacite = None,cte_stop = 0.181):
        # anciennes en udp -> transfere = 33, cte_stop = 3

        self.coordonnees = coordonnees
        self.lignes = lignes
        self.adjacents = self.cree_adjacents()

        self.transfere = transfere
        self.cte_stop = cte_stop
        #print(self.transfere)

        if ctes_inneficacite == None:

            # il faudrait que les ctes soient fixes pour une même "toile", et même nb de ligne...

            self.cte_distance = None
            self.cte_longueur = None

        else:

            self.cte_distance = ctes_inneficacite[0]
            self.cte_longueur = ctes_inneficacite[1]


    def cree_adjacents(self):

        adjacents = { sommet: {} for sommet in self.coordonnees }
        for ligne in self.lignes:

            lst_ligne = self.lignes[ligne]

            adjacents = self.ajoute_ligne_adjacents(ligne,lst_ligne,adjacents)

        return adjacents

    def copy(self):

        coordonnees = self.coordonnees.copy()
        lignes = self.lignes.copy()

        return(Reseau2(coordonnees,lignes,self.transfere,(self.cte_distance,self.cte_longueur)))



    def est_connexe(self):

        distances = self.mini_recherche_distance_total()

        for station1 in distances:
            for station2 in distances:

                if distances[station1][station2] == -1:
                    return False
        return True


    def ajoute_ligne_adjacents(self,nom_ligne,lst_ligne,adjacents,lst_ligne_dep = []):

        for station in lst_ligne_dep:
            adjacents[station][nom_ligne] = (None,None)

        if len(lst_ligne) > 2:

            if lst_ligne[0] == lst_ligne[-1]:
                adjacents[lst_ligne[0]][nom_ligne] = (lst_ligne[1],lst_ligne[-2])

            else:
                adjacents[lst_ligne[0]][nom_ligne] = (None,lst_ligne[1])
                adjacents[lst_ligne[-1]][nom_ligne] = (None,lst_ligne[-2])

            for k in range(1,len(lst_ligne)-1):

                # print(k,lst_ligne,nom_ligne)

                if lst_ligne[k-1] == lst_ligne[k]:

                    precedent = adjacents[lst_ligne[k-1]][nom_ligne][0]

                    adjacents[lst_ligne[k]][nom_ligne] = (precedent,lst_ligne[k+1])

                else: adjacents[lst_ligne[k]][nom_ligne] = (lst_ligne[k-1],lst_ligne[k+1])

        elif len(lst_ligne) == 2:

            if lst_ligne[0] != lst_ligne[1]:
                adjacents[lst_ligne[0]][nom_ligne] = (lst_ligne[1],None)
                adjacents[lst_ligne[1]][nom_ligne] = (lst_ligne[0],None)

        return adjacents




    def ajoute_ligne_tot(self,ligne_nom,ligne_lst):

        if ligne_nom in self.lignes:
            self.adjacents = self.ajoute_ligne_adjacents(ligne_nom,ligne_lst,self.adjacents,self.lignes[ligne_nom])

        else:
            self.adjacents = self.ajoute_ligne_adjacents(ligne_nom,ligne_lst,self.adjacents)

        self.lignes[ligne_nom] = ligne_lst


    def ajoute_station_ligne(self,nom_ligne,station):

        if nom_ligne not in self.lignes:

            self.lignes[nom_ligne] = [station]

        else:

            self.lignes[nom_ligne].append(station)
            self.adjacents = self.ajoute_ligne_adjacents(nom_ligne,self.lignes[nom_ligne],self.adjacents)


    def suppr_stations_ligne(self,nom_ligne,station):

        nouvelle_ligne = []

        for station1 in self.lignes[nom_ligne]:

            if station != station1:

                nouvelle_ligne.append(station1)

        if len(self.lignes[nom_ligne])>2:
            if len(nouvelle_ligne) > 0:
                if self.lignes[nom_ligne][0] == self.lignes[nom_ligne][-1] and nouvelle_ligne[0] != nouvelle_ligne[-1]: # on verifie que la ligne est circulaire, donc on veut qu'elle le reste
                    nouvelle_ligne.append(nouvelle_ligne[0])
                    # l'autre cas est le cas ou il n'y a plus rien dans "nouvelle_ligne" donc en fait cette ligne n'existe plus...

        self.adjacents = self.ajoute_ligne_adjacents(nom_ligne,nouvelle_ligne,self.adjacents,self.lignes[nom_ligne])
        self.lignes[nom_ligne] = nouvelle_ligne.copy()


    def distance_fun(point1,point2):
        x1,x2,y1,y2 = point1[0],point2[0],point1[1],point2[1]
        #dist = np.sqrt((x1 - x2)**2+(y1 - y2)**2)
        return float(np.sqrt((x1 - x2)**2 + (y1 - y2)**2))


    def cherche_distance(self,origine):

        # c'est le Dijkstra adapté

        def distance_fun(point1,point2):
            x1,x2,y1,y2 = point1[0],point2[0],point1[1],point2[1]
            #dist = np.sqrt((x1 - x2)**2+(y1 - y2)**2)
            return float(np.sqrt((x1 - x2)**2 + (y1 - y2)**2))

        def min_dico_pos(dico):
            mini = (None,-1)
            for key in dico:
                if dico[key] < mini[1] or mini[1] == (-1): mini = (key,dico[key])
            return mini

        def remplace_ssi_si(a_explorer,station_fils,ligne_adj,distance):

            if (station_fils,ligne_adj) in a_explorer: # si la nouvelle station est déja dans a_explorer
                if a_explorer[(station_fils,ligne_adj)] > distance:
                    a_explorer[(station_fils,ligne_adj)] = distance

            else:
                a_explorer[(station_fils,ligne_adj)] = distance



        recherche = {} # dico de dico; enregiste la distance depuis la station de départ vers les stations pour toutes les lignes sur lesquelles elles sont; ce sont les plus petites distances déja trouvées.
        a_explorer = {} # dico -> tuple : distance

        for station in self.coordonnees: recherche[station] = {}

        for ligne in self.adjacents[origine]: #sert a initialiser

            recherche[origine][ligne] = 0

            for station in self.adjacents[origine][ligne]:

                if station != None :
                    #print(self.coordonnees[origine])
                    #print(self.coordonnees[station])


                    distance = distance_fun(self.coordonnees[origine],self.coordonnees[station])


                    a_explorer[(station,ligne)] = distance

        # print(a_explorer,"\n",recherche,"\n","\n")

        while a_explorer:

            # print(a_explorer,"\n",recherche,"\n","\n")

            minimum = min_dico_pos(a_explorer)
            station_or = minimum[0][0]
            ligne = minimum[0][1]
            distance = minimum[1]

            # print(a_explorer)
            # print(minimum)
            # print(recherche,'\n')

            a_explorer.pop((station_or,ligne))

            explore = True

            if ligne in recherche[station_or]: # si on a déja essayé d'obtenir cette station par cette ligne.

                if recherche[station_or][ligne] <= distance:
                    explore = False
                    # le chemin trouvé est plus long qu'un autre déja trouvé
                    # print('False')

                else:
                    recherche[station_or][ligne] = distance
                    # print('remplace')

            else: # si on a pas encore essayé d'obtenir cette station par cette ligne.
                recherche[station_or][ligne] = distance
                # print('ligne_ajoutée')

            if explore:
                for ligne_adj in self.adjacents[station_or]:
                    # on regarde vers où peut-on explorer ensuite a partir de cette station...

                    if ligne_adj != ligne:

                        remplace_ssi_si(a_explorer,station_or,ligne_adj,distance + self.transfere)
                        # on tente d'explorer vers un changement de ligne mais avec la meme station
                        # print('transfert')

                    else:
                        for station_fils in self.adjacents[station_or][ligne_adj]:

                            if station_fils != None :

                                distance_adj = distance_fun(self.coordonnees[station_or],self.coordonnees[station_fils]) + distance + self.cte_stop
                                # print(self.coordonnees[station_or])
                                # print(self.coordonnees[station_fils])
                                # print(distance_adj)

                                remplace_ssi_si(a_explorer,station_fils,ligne_adj,distance_adj)

            # print('\n\n\n')

        return recherche




    def mini_recherche_distance_total(self):

        def mini_dico_pos_val(dico):
            mini = np.inf
            for key in dico:
                if dico[key] < mini : mini = dico[key]
            return mini

        distances = {}

        for station_or in self.coordonnees:

            recherche = self.cherche_distance(station_or)
            # print(station_or)
            # print(recherche,'\n\n')

            distances[station_or] = {}

            for station_arr in self.coordonnees:

                distance = mini_dico_pos_val(recherche[station_arr])

                distances[station_or][station_arr] = distance

        return(distances)


    def distances_totales(self):

        somme_distances = 0
        poids_tot = 0

        distances = self.mini_recherche_distance_total()

        for station_or in distances:

            if len(self.coordonnees[station_or]) > 2 : poids = self.coordonnees[station_or][2]
            else : poids = 1

            poids_tot += poids

            for station_arr in distances:

                if distances[station_or][station_arr] != -1:

                    somme_distances += (poids)*distances[station_or][station_arr]


        return(somme_distances/poids_tot)


    def longueurs_totale(self):

        def distance_fun(point1,point2):
            x1,x2,y1,y2 = point1[0],point2[0],point1[1],point2[1]
            #dist = np.sqrt((x1 - x2)**2+(y1 - y2)**2)
            return float(np.sqrt((x1 - x2)**2 + (y1 - y2)**2))

        l_tot = 0

        for ligne in self.lignes:

            lst_ligne = self.lignes[ligne]

            for k in range(len(self.lignes[ligne]) -1):

                #lst_ligne = self.lignes[ligne]

                l_tot += distance_fun(self.coordonnees[lst_ligne[k]],self.coordonnees[lst_ligne[k+1]])

        return l_tot

    def inefficacite1(self):

        distance_totale = self.distances_totales()
        longueur_totale = self.longueurs_totale()

        # print(distance_totale,longueur_totale)

        return (distance_totale*longueur_totale)

    #il faudrait utiliser une autre formule d'inefficacité, plutôt basé sur une distance (euclidienne ou non...) avec une forme de inn ^= ((dist_totale/cte1)**2 + (long_tot/cte2)**2 )**(1/2)

    def inefficacite(self):

        if self.cte_distance == None: return(self.inefficacite1())

        else:

            distance_totale = (self.distances_totales()/self.cte_distance)**2
            longueur_totale = (self.longueurs_totale()/self.cte_longueur)**2

            return (((distance_totale + longueur_totale)**(1/2))*(1/(2**(1/2))))


    def distance_floyd_warshall(self):

        # premiere étape : créer les matrices initiales

        adjacence, precedent = {} , {}
        # adjacence = { (station,ligne) : { (station,ligne): distance } }
        # precedent = { (station,ligne) : { (station,ligne): station_pour_y_aller } }

        for ligne in self.lignes:
            for station in self.lignes[ligne]:
                adjacence[(station,ligne)], precedent[(station,ligne)] = {} , {}

        for station in adjacence:

            adjacence[station] = { station2 : np.inf for station2 in adjacence }
            precedent[station] = {station2 : None for station2 in adjacence }

        for ligne in self.lignes:

            ligne_lst = self.lignes[ligne]

            for k in range(len(ligne_lst)-1):

                adjacence[(ligne_lst[k],ligne)][(ligne_lst[k+1],ligne)] = ( distance_fun(self.coordonnees[ligne_lst[k]], self.coordonnees[ligne_lst[k+1]]) + self.cte_stop )
                precedent[(ligne_lst[k],ligne)][(ligne_lst[k+1],ligne)] = (ligne_lst[k],ligne)

                adjacence[(ligne_lst[k+1],ligne)][(ligne_lst[k],ligne)] = ( distance_fun(self.coordonnees[ligne_lst[k+1]],self.coordonnees[ligne_lst[k]]) + self.cte_stop)
                precedent[(ligne_lst[k+1],ligne)][(ligne_lst[k],ligne)] = (ligne_lst[k+1],ligne)

        for station in self.coordonnees:

            for ligne1 in self.lignes:

                for ligne2 in self.lignes:

                    if ligne1 != ligne2 and (station,ligne1) in adjacent and (station,ligne2) in adjacent:
                        adjacence[(station,ligne1)][(station,ligne2)] = self.transfere
                        precedent[(station,ligne1)][(station,ligne2)] = (station,ligne1)

                        adjacence[(station,ligne2)][(station,ligne1)] = self.transfere
                        precedent[(station,ligne2)][(station,ligne1)] = (station,ligne2)


        # maintenant c'est le programme a proprement parler
        for station in adjacence:

            for station1 in adjacence:

                if station1 != station:

                    for station2 in adjacence:

                        if station2 != station and station2 != station1:

                            distance_or = adjacence[station1][station2]
                            distance_new = adjacence[station1][station] + adjacence[station][station2]

                            if distance_new != np.inf:

                                if distance_new < distance_or :

                                    adjacence[station1][station2] = distance_new
                                    precedent[station1][station2] = station

        return(adjacence,precedent)


    def trouve_distance_floyd_warshall(self,station1,station2):

        adjacence, precedent = distance_floyd_warshall(self)

        distance = np.inf
        min = ((None,None),(None,None))

        for ligne1 in lignes:

            if (station1,ligne1) in adjacence:

                for ligne2 in lignes:

                    if (station2,ligne2) in adjacence:

                        if adjacence[(station1,ligne1),(station2,ligne2)] < distance:

                            distance = adjacence[(station1,ligne1),(station2,ligne2)]
                            min = ((station1,ligne1),(station2,ligne2))

        chemin = [min[1]]

        station_inter = precedent[min[0],min[1]]
        chemin.append(station_inter)

        while station_inter[0] != station1:

            station_inter = precedent[min[0],station_inter]
            chemin.append(station_inter)

        chemin_inverse = [ chemin[-k] for k in range(1,len(chemin)+1)]

        return (distance,chemin_inverse)



    def dessine_reseau(self,affiche_nom_stations=False):

        avec_lignes = plt.figure()

        tab_couleur = {'rouge':'red','vert':'green','bleu':'blue','violet':'purple','orange':'orange',
                       'rose':'pink','cyan':'cyan','marron':'brown'}

        # pour changer l'épaisseur de la ligne, il faut utiliser linewidth

        epaisseur = 5

        for ligne in self.lignes:

            les_x, les_y = [] , []

            for station in self.lignes[ligne]:

                x,y = self.coordonnees[station][0], self.coordonnees[station][1]
                les_x.append(x)
                les_y.append(y)

                if ligne in tab_couleur:
                    plt.plot(les_x,les_y, color = tab_couleur[ligne], linewidth = epaisseur)
                    # epaisseur -= 0.2

                else: plt.plot(les_x,les_y,linewidth = epaisseur)

            epaisseur -= 0.3


        for station in self.coordonnees:

            x,y = self.coordonnees[station][0] , self.coordonnees[station][1]

            plt.plot(x,y,marker = "o", color = "k")
            if affiche_nom_stations : plt.text(x + 0.06, y + 0.02, station, fontsize = 10)

        sans_lignes = plt.figure()

        for station in self.coordonnees:

            x,y = self.coordonnees[station][0] , self.coordonnees[station][1]

            plt.plot(x,y,marker = "o", color = "k")
            if affiche_nom_stations : plt.text(x + 0.3, y + 0.3, round(self.coordonnees[station][2],4), fontsize = 10)

        plt.show()














