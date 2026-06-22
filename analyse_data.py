from recuit_simule import *
from creation_du_reseau import *
from evolution_reseau import *
import numpy as np
from time import perf_counter_ns


def moyenne(lstlst):

    moyennes = []
    max_length = 0
    for lst in lstlst:
        max_length = max(max_length,len(lst))
    for j in range(max_length):
        m = 0
        for i in range(len(lstlst)):
            if len(lstlst[i])> j :
                m+=lstlst[i][j]
            else:
                m+=lstlst[i][-1]
        moyennes.append(m/len(lstlst))
    return moyennes


def faire_1_test(nb_stations, nb_droite, nb_circ , densite = 2.5,
        generation_max = 800, T0 = 1e-5 , pertes = 0.99, affichage = True):

    '''la densite devrait etre entre 0.857km^-2 et 4.458km^-2 '''

    coordonnees1 = cree_coord_poids_centre(nb_stations,np.sqrt(nb_stations/(densite*np.pi)))
    test = cree_proto_reseau_etoile(coordonnees1,nb_droite,nb_circ,True,True)
    print(test.inefficacite())
    if affichage : test.dessine_reseau()
    etoile = demeler_reseau_tot(test)
    print(etoile.inefficacite())
    if affichage : etoile.dessine_reseau()
    print("------------------------")

    tic = perf_counter_ns()
    final_tot, inefficacites, nb_tests_total = evolution_vrai_rs(etoile, 0, 0,
            T0, pertes, generation_max)
    toc = perf_counter_ns()
    final = final_tot[0]
    print(final.inefficacite())
    if affichage : final.dessine_reseau()
    print("------------------------")

    if affichage:
        inefficacites_pour_gen = plt.figure()
        plt.plot(inefficacites)
        plt.plot([1]*(len(inefficacites)),'r--')
        nb_tests = plt.figure()
        plt.plot(nb_tests_total)
        plt.show()

    final2 = demeler_reseau_tot(final)
    print(final2.inefficacite())
    if affichage : final2.dessine_reseau()
    return(final_tot, final2 ,inefficacites, nb_tests_total, toc-tic)


def faire_n_tests(nb_tests ,nb_stations, nb_droite, nb_circ, densite = 2.5,
        generation_max = 800, T0 = 1e-5 , pertes = 0.99):

    file_name = input('nom pour fichier ')
    test = 0
    inefficacites_tot = []
    if file_name != '' :
        fichier = open(file_name,'w')
    while test < nb_tests:
        print(test,'/',nb_tests)
        meilleur, final2 ,inefficacites, nb_tests_total, temps = faire_1_test(
                nb_stations, nb_droite, nb_circ, densite, generation_max, T0,
                pertes, False)
        if file_name != '':
            fichier.write(f"{meilleur[0].coordonnees}\n"
                          f"\n{inefficacites}\n\n{temps}\n\n\n\n\n")
        inefficacites_tot.append(inefficacites)
        test +=1
    if file_name != '':
        fichier.close()
    inefficacites_pour_generation = plt.figure()
    for inefficacites in inefficacites_tot:
        plt.plot(inefficacites)
    plt.plot([1]*(len(inefficacites_tot[0])),'r--')
    nb_tests = plt.figure()
    plt.plot(nb_tests_total)
    plt.show()


def tester_effet_nb_lignes(max_nb_lignes_drtes, nb_essais, nb_stations,nb_circ,
        densite = 2.5):

    inefficacites_tot, inefficacites_etoiles_tot = [],[]
    x = [ i+1 for i in range(max_nb_lignes_drtes)]
    for essai in range(nb_essais):
        coordonnees1 = cree_coord_poids_centre(nb_stations,
                np.sqrt(nb_stations/(densite*np.pi)))
        inefficacites, inefficacites_etoiles = [],[]
        for nb_droite in range(max_nb_lignes_drtes):
            test = cree_proto_reseau_etoile(coordonnees1, nb_droite + 1,
                    nb_circ, True,True)
            print(test.inefficacite())
            etoile = demeler_reseau_tot(test)
            print(etoile.inefficacite())
            print("------------------------")
            inefficacites.append(test.inefficacite())
            inefficacites_etoiles.append(etoile.inefficacite())
        inefficacites_tot.append(inefficacites)
        inefficacites_etoiles_tot.append(inefficacites_etoiles)
        print("------------------------")
    fig, (ax1, ax2) = plt.subplots(1, 2, constrained_layout=True, sharey=True)
    ax1.set_title('avec noeuds')
    ax1.set_xlabel('nombre de lignes droites')
    ax1.set_ylabel('Inefficacite')

    ax2.set_xlabel('nombre de lignes droites')
    ax2.set_title('sans neuds')

    for inefficacites in inefficacites_tot:
        ax1.plot(x,inefficacites,color = 'blue', linewidth = 1)
    for inefficacites_etoiles in inefficacites_etoiles_tot:
        ax2.plot(x,inefficacites_etoiles,color = 'blue', linewidth = 1)

    moyennes_tests = moyenne(inefficacites_tot)
    moyennes_etoiles = moyenne(inefficacites_etoiles_tot)

    ax1.plot(x,moyennes_tests,color = 'red', linewidth = 2)
    ax2.plot(x,moyennes_etoiles,color = 'red', linewidth = 2)

    plt.show()


def tester_nb_ligne_rs(nb_lignes_drt_max, nb_essais, nb_stations, nb_circ,
        nb_lignes_drt_min = 1, densite = 2.5, generation_max = 800, T0 = 1e-5 ,
        pertes = 0.99):

    # file_name = input('quel nom de fichier? ')
    file_name = f"s{nb_stations}_circ{nb_circ}"
    if file_name != '' : fichier = open(file_name,'w')

    ''' l idee est de determiner le dico des inefficacites avec en cle le nombre
    de lignes droites et en valeur la liste des inefficacites (ou plutot la
    liste de listes car il y aura plusieurs essais) '''

    ineff_tot = {i : [] for i in range(nb_lignes_drt_min,nb_lignes_drt_max+1)}

    ineff_dep, ineff_fin = [], []

    for essai in range(nb_essais):

        coordonnees1 = cree_coord_poids_centre(nb_stations,
                np.sqrt(nb_stations/(densite*np.pi)))

        if file_name != '':
            fichier.write(f"{coordonnees1}\n\n")

        for nb_drt in range(nb_lignes_drt_min,nb_lignes_drt_max+1):

            print(f"{nb_drt+(essai)*nb_lignes_drt_max}/{nb_lignes_drt_max*nb_essais}")

            test = cree_proto_reseau_etoile(coordonnees1,nb_drt,nb_circ,True,True)
            print(test.inefficacite())
            ineff_dep.append(test.inefficacite())
            etoile = demeler_reseau_tot(test)
            print(etoile.inefficacite())
            print("------------------------")

            tic = perf_counter_ns()
            final_tot,inefficacites,nb_tests_total = evolution_vrai_rs(etoile,
                    0, 0, T0, pertes, generation_max)
            toc = perf_counter_ns()
            final = final_tot[0]
            print(final.inefficacite())
            print("------------------------")

            final2 = demeler_reseau_tot(final)
            print(final2.inefficacite())
            ineff_tot[nb_drt].append(inefficacites)
            if file_name != '':
                fichier.write(f"{inefficacites}\n\n{toc-tic}\n\n\n\n\n")
    ineff_moy = {i : [] for i in range(nb_lignes_drt_min,nb_lignes_drt_max+1)}
    for nb_lgn_drt in ineff_tot:
        ineff_moy[nb_lgn_drt] = moyenne(ineff_tot[nb_lgn_drt])

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    Z = [ ineff_moy[nb_lgn_drt] for nb_lgn_drt in ineff_moy ]
    max_length = max([len(Z[i]) for i in range(len(Z))])
    for i in range(len(Z)):
        for j in range(max_length-len(Z[i])) :
            # Z[i].append(Z[i][-1])
            Z[i].append(np.nan)
    if file_name != '':
        fichier.write(f"{Z}")
        fichier.close()
    Z = np.array(Z)
    y = [ i for i in range(nb_lignes_drt_min,nb_lignes_drt_max+1) ]
    x = [ i for i in range(len(Z[0])) ]
    X, Y = np.meshgrid(x, y)
    surf = ax.plot_surface(X, Y, Z , cmap='viridis', alpha=1, color = 'black')
    ax.set_xlabel('generations $\\xi$')
    ax.set_ylabel('nombre de lignes Droites')
    ax.set_zlabel('Inefficacite (moyenne)')
    ax.set_title(f'Inefficacite pour un reseau de {nb_stations}'
                 f'stations et {nb_circ} ligne(s) circulaire(s)')
    fig.colorbar(surf, ax=ax, shrink=0.4, label='inefficacite')
    plt.tight_layout()
    plt.show()


def affiche_ineff(s,nb_stations):

    y = [ i for i in range(len(s))]
    x = [ i for i in range(len(s[0]))]
    X, Y = np.meshgrid(x, y)
    Z = np.array(s)
    fig, ax = plt.subplots()
    cf = ax.contourf(X, Y, Z, levels=150, cmap='viridis')
    cs = ax.contour(X, Y, Z, levels=15, colors='white', linewidths=0.5, alpha=0.4)
    fig.colorbar(cf, ax=ax, label='inefficacite')
    ax.set_xlabel('nombre de lignes droites')
    ax.set_ylabel('nombre de lignes circulaires')
    ax.set_title(f'Inefficacite pour un reseau de {nb_stations} stations')
    plt.show()








