import numpy as np
from reseau2 import *
from creation_du_reseau import *

def distance(p1,p2): return(np.sqrt( (p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 ))

coordonees_lyon = {'Charpennes': (63.39370228921304, 70.33327308867854), 'Brotteaux': (59.29327674397289, 67.01741375781722), 'Gare Part-Dieu V.Merle': (58.28600856241728, 61.5334335280906), 'Place Guichard': (47.595635365275335, 59.503657277936384), 'Debourg': (33.851906688497024, 31.559125338048943), 'Mermoz - Pinel': (87.20152260639847, 30.296944422680383,), 'Grange Blanche': (78.20359651148311, 42.970688517726785), 'Monplaisir Lumière': (71.03937948313188, 45.69896239456028), 'Sans Souci': (64.57099314329096, 47.930068560695815), 'Garibaldi': (53.4655289143231, 51.426200315297876), 'Saxe - Gambetta': (46.64516830202281, 54.1086169515026), 'Guillotière Gabriel Péri': (42.39422848817043, 55.62901679824961), 'Vieux Lyon': (26.338335844521055, 59.98375893346264), 'République Villeurbanne': (73.11615709595375, 70.63829886737949), 'Gratte Ciel': (81.65450649712992, 69.20605767113841), 'Flachet': (90.06353126902233, 67.64287918080925), 'Cusset': (99.88064418605802, 65.83556981601646), 'Laurent Bonnevay': (108.84697740689919, 64.02216013796647), 'Vaulx-en-Velin La Soie': (121.4775025542334, 61.091347338177115), 'Laënnec': (86.78513113089093, 38.362675061868856), 'Perrache': (26.879932326510314, 49.9705846516747), 'Ampère - Victor Hugo': (29.04121333216203, 53.03808853719971), 'Bellecour': (31.839954654625302, 57.04263173378621), 'Cordeliers': (35.680666603886024, 62.8030084889275), 'Hôtel de Ville L. Pradel': (35.93557742591358, 66.9391363928824), 'Foch': (44.09277977233916, 68.80917580387091), 'Masséna': (52.9090017663707, 69.61387314417777), 'Hénon': (27.65931495104823, 79.11305667516899), 'Cuire': (32.4065549193735, 85.04582155203622), 'Gare de Vénissieux': (88.00658927933381, 6.138421126721028), 'Jean Macé': (42.90088518914281, 46.740197111617476), 'Place Jean Jaurès': (37.71180367895788, 38.01942205721076), 'Stade de Gerland Le LOU': (31.253811967125067, 27.155419845790618), 'Croix-Paquet': (36.30513665419066, 70.84048397056364), 'Croix-Rousse': (32.04228251370278, 74.46610288663891), 'Parilly': (87.41333790860928, 19.618741757831515), 'Gorge de Loup': (5.516935487100305, 66.77160843486973), 'Valmy': (5.169988935394443, 75.20479009058789),'Gare de Vaise': (4.172937981866909, 79.78611414764458), 'Oullins Centre': (5.653092736491061, 14.44598327640989), 'St-Genis-Laval Hôp. Sud': (4.669902521987623, 1.1965448150093039), "Gare d'Oullins": (14.344647575954994, 16.541514138801006)}


lignes_lyon = {
"rouge" : ['Perrache', 'Ampère - Victor Hugo', 'Bellecour', 'Cordeliers', 'Hôtel de Ville L. Pradel', 'Foch', 'Masséna', 'Charpennes', 'République Villeurbanne','Gratte Ciel', 'Flachet', 'Cusset', 'Laurent Bonnevay', 'Vaulx-en-Velin La Soie'],
"bleu":['St-Genis-Laval Hôp. Sud','Oullins Centre', "Gare d'Oullins", 'Stade de Gerland Le LOU', 'Debourg', 'Place Jean Jaurès', 'Jean Macé', 'Saxe - Gambetta', 'Place Guichard', 'Gare Part-Dieu V.Merle', 'Brotteaux', 'Charpennes' ],
"orange": ['Cuire', 'Hénon', 'Croix-Rousse', 'Croix-Paquet', 'Hôtel de Ville L. Pradel'],
"vert":['Gare de Vaise', 'Valmy', 'Gorge de Loup', 'Vieux Lyon','Bellecour', 'Guillotière Gabriel Péri', 'Saxe - Gambetta', 'Garibaldi', 'Sans Souci', 'Monplaisir Lumière', 'Grange Blanche', 'Laënnec', 'Mermoz - Pinel', 'Parilly', 'Gare de Vénissieux']}

lyon_reel = Reseau2(coordonees_lyon,lignes_lyon,44)

densite_surfacique = 120 * 80 / 42

def find_center():

    center = [0,0]

    for station in coordonees_lyon:
        center[0] += coordonees_lyon[station][0]
        center[1] += coordonees_lyon[station][1]

    center = (center[0]/42,center[1]/42)

    return center

center = find_center()

def update_coord_poids():

    coords = {}

    for station in coordonees_lyon:

        x, y = coordonees_lyon[station][0],coordonees_lyon[station][1]
        coords[station] = (x,y, 1/(distance((x,y),center)))

    return coords

new_coordonees_lyon = update_coord_poids()

print(center)
lyon_updated = Reseau2(new_coordonees_lyon, lignes_lyon, transfere = 33,ctes_inneficacite = None,cte_stop = 3)
# lyon_updated.dessine_reseau()
print(lyon_updated.inefficacite())
ctes = get_constantes_coord(new_coordonees_lyon,4)
lyon_le_vrai = Reseau2(new_coordonees_lyon, lignes_lyon, lyon_updated.transfere, ctes)
print(lyon_le_vrai.inefficacite())
print(round(lyon_le_vrai.distances_totales()),round(lyon_le_vrai.longueurs_totale()))