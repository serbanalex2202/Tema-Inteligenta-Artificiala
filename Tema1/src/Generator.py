
import numpy
from Variabile import *
import random
import World


# daca vrem sa facem p analiza de performanta terbuie sa avem
# mereu aceasi configuratie de harta, pe care o citim dintr-un fisier cu aceasta functie
def read_map(map_name, canvas, width):


    objects = {}
    objects['player'] = []  # lista de players poate implementam mai multi jucatori
    objects['devils'] = []
    objects['stars'] = []
    objects['portals'] = []
    objects['exit'] = []  # poate adaugam mai multe iesiri
    objects['board'] = {}  # asta e direct dictionar ca e un singur element

    walls = []

    matrix = numpy.loadtxt(map_name)
    print(matrix)

    (lines, cols)= matrix.shape


    loc1 = 0
    loc2 = 0
    loc3 = 0
    loc4 = 0
    loc5 = 0
    loc6 = 0

    #citim matrice
    for i in range(0, lines):
        for j in range (0, cols):
            if matrix[i][j] == PLAYER:
                objects['player'].append(
                    {"active": 1, "start_coords": (i,j), "coords": (i,j), "direction": (0, 0), "score": 1,
                     "reward": WALK_REWARD, "color": "green"})  # c1

            if matrix[i][j] == DEVIL:
                objects['devils'].append(
                    {"active": 1, "type": "t_devil", "start_coords": (i,j), "coords": (i,j), "direction": (0, 0),
                     "reward": DEVIL_REWARD, "color": "red"})  # c1

            if matrix[i][j] == STAR:
                objects['stars'].append(
                    {"active": 1, "type": "t_star", "coords": (i,j), "reward": STAR_REWARD, "color": "gold"})  # c1

            if matrix[i][j] == EXIT:
                objects['exit'].append(
                    {"active": 1, "type": "t_exit", "coords": (i,j), "reward": EXIT_REWARD, "color": "green"})  # c4

            if matrix[i][j] == WALL:
                walls.append((i,j))


            if matrix[i][j] == PORTAL1:

                if loc1 == 0:
                    loc1 = (i, j)
                else:
                    loc2 = (i, j)

            if matrix[i][j] == PORTAL2:

                if loc3 == 0:
                    loc3 = (i, j)
                else:
                    loc4 = (i, j)

            if matrix[i][j] == PORTAL3:

                if loc5 == 0:
                    loc5 = (i, j)
                else:
                    loc6 = (i, j)

    objects['portals'].append({"active": 1, "start": loc1, "end": loc2, "color": "blue", "visited": 0})
    objects['portals'].append({"active": 1, "start": loc2, "end": loc1, "color": "blue", "visited": 0})
    objects['portals'].append({"active": 1, "start": loc3, "end": loc4, "color": "purple", "visited": 0})
    objects['portals'].append({"active": 1, "start": loc4, "end": loc3, "color": "purple", "visited": 0})

    objects['portals'].append({"active": 1, "start": loc5, "end": loc6, "color": "cyan", "visited": 0})
    objects['portals'].append({"active": 1, "start": loc6, "end": loc5, "color": "cyan", "visited": 0})


    objects['board'] = {"canvas": canvas, "width": width, "map": matrix, "lines": lines, "cols": cols,
                                "walls": walls, "draw": 1}

    if World.args.show_final == 1:
        objects["board"]["draw"] = 0

    return walls, matrix, objects





#verifica daca se poate aseza obstacolul in labirint conditia pentru a il aseza este
#  sa nu obtureze caile de acces din jurul lui si sa nu se suprapuna cu alt zid
def try_put_wall(game, x_start, y_start, x_end, y_end):

    for i in range(x_start - 1, x_end + 2):
        for j in range(y_start - 1, y_end + 2):
            if (game[i][j] == WALL) or (game[i][j] == WALL): #daca e zid nu putem pune
                return 0



    for i in range (x_start, x_end + 1):
        for j in range(y_start, y_end + 1):
            game[i][j] = WALL

    return 1

#genereaza harta si intoarce perechi de coordonate pentru fiecare perete
# si intoarce si o matrice in care sunt salvati peretii
#feicare harta o genereaza cu dimensiuni aleatoare mutand centrul
def gen_walls(lines, cols):

    #nu o mai folosesc ca se genreaza in alte cadrane obiecele
    (deplasare_i) =  1  #random.randint(0, 3)
    (deplasare_j) =  1  #random.randint(0, 3)

    map = numpy.zeros((lines, cols));

    #genereaza contur plus granita intre harti
    # in functie de cat a fost generata deplasarea =>
    #  zidul va fi mai in fata sau mai in spate

    for i in range(0, lines):

        map[i][0] = WALL
        map[i][int(cols / 2) + deplasare_j - 1] = WALL
        map[i][cols - 1] = WALL



    for j in range(0, cols):
        map[0][j] = WALL
        map[int(lines / 2) + deplasare_i - 1][j] = WALL
        map[lines - 1][j] = WALL



    # incearca sa pui suficiente obiecte, raportat la dimensiunea hartii
    obiecte_puse = 0
    incercari = 0   #fail safe, sa se termine in caz ca s-au setat prea multe obiecte
    while obiecte_puse < World.NUMAR_OBIECTE:

        # 3 tipuri de forme zis vertival, orizontal, patrat
        tip_forma = random.randint(0, 3)

        # alege random centrul formei
        x = random.randint(3, lines - 3)
        y = random.randint(3, cols - 3)



        # zid orizontal -
        if tip_forma == 0:
            obiecte_puse += try_put_wall(map, x - 1, y, x + 1, y)

        if tip_forma == 1:
            obiecte_puse += try_put_wall(map, x, y - 1, x, y + 1)

        if tip_forma == 2:
            obiecte_puse += try_put_wall(map, x - 1, y - 1, x + 1, y + 1)

        incercari += 1

        if incercari > INCERCARI:
            print("nu au incaput toate obiectele")
            break

    walls = []
    for i in range(0 ,lines):
        for j in range(0, cols):
            if map[i][j] != 0:
                walls.append((i,j))

    #a nu se schimba ordinea
    return walls, map


#returneaza 1 doar daca pentru locatia de spawn aleasa exsita spatiu in jur
#exista spatiu daca nu exista un devil
def space_around(map, i_c, j_c):

    for i in range (i_c - 1, i_c + 2):
        for j in range(j_c - 1, j_c + 2):
            if map[i][j] == DEVIL:
                return 0
    return 1



#returneaza o locatie de spawn pentru jucatori infunctie de cadranul dat
#se alege random un punct de start (x,y) de la care se cauta un loc disponibil
#de spawn care nu se afla in proximitatea unui gardian
def spawn_location(map, from_i, to_i, from_j, to_j, nr_iteratii):

    #sa fim siguri ca se opreste
    if nr_iteratii == 100:
        return

    start_i = random.randint(from_i, int(to_i))
    start_j = random.randint(from_j, int(to_j))

    for i in range(start_i, to_i - 1):
        for j in range(start_j, to_j - 1):
            if map[i][j] == SPACE and space_around(map, i, j) == 1:  #daca nu e zid si daca are spatiu in jur
                return (i,j)    #aici iese din recurenta cu un loc de spawn

    #NU AM GASIT loc de SPAWN => facem din nou si recursiv va gasi pana la urma
    return spawn_location(map, from_i, to_i, from_j, to_j, nr_iteratii + 1)



#intoarce o harta noua pe care sunt obiectele
def put_objects(map, objects):


    #pentru fiecare portal din lista ii setam start in functie de culoare
    for portal in objects['portals']:
        (x, y) = portal["start"]
        if portal["color"] == "blue":
            map[x][y] = PORTAL1
        if portal["color"] == "purple":
            map[x][y] = PORTAL2
        if portal["color"] == "cyan":
            map[x][y] = PORTAL3

    for star in objects['stars']:
        (x, y) = star["coords"]
        map[x][y] = STAR

    for exit in objects['exit']:
        (x, y) = exit["coords"]
        map[x][y] = EXIT


    for devil in objects['devils']:
        (x, y) = devil["coords"]
        map[x][y] = DEVIL


    for player in objects['player']:
        (x, y) = player["coords"]
        map[x][y] = PLAYER

    return map


#curata harta ce nu e SPACE devine SPACE
def remove_objects(map):
    (lines, cols) = map.shape
    for i in range(0, lines):
        for j in range(0, cols):
            if map[i][j] != WALL and map[i][j] != WALL:
                map[i][j] = SPACE


#cream un dictionar cu obiecte, fiecare cheie duce la o lista de tupluri
#tuplurile sunt coordonate
def spawn_objects(map, canvas, walls, lines, cols, width, args):

    (i, j) = map.shape


    objects = {}
    #toate sa fie lista de dictionare, pentru a putea adauga camputi noi

    objects['player'] = []  #lista de players poate implementam mai multi jucatori
    objects['devils'] = []
    objects['stars'] = []
    objects['portals'] = []
    objects['exit'] = []    #poate adaugam mai multe iesiri
    objects['board'] = {}   #asta e direct dictionar ca e un singur element

    #cadran1 : 1 - i/2      1 - j/2
    #cadran2 : 1 - i/2      j/2 - j
    #cadran3 : i/2 - i      1 - j/2
    #cadran4 : i/2 - i      j/2 - j


    # generam maxim 4 devils (in fiecare cadran cate 1)
    loc1 = spawn_location(map, 1, int(i / 2), 1, int(j / 2), 0)  # c1
    loc2 = spawn_location(map, 1, int(i / 2), int(j / 2), j, 0)  # c2
    loc3 = spawn_location(map, int(i / 2), i, 1, int(j / 2), 0)  # c3
    loc4 = spawn_location(map, int(i / 2), i, int(j / 2), j, 0)  # c4
    for loc in loc1, loc2, loc3, loc4:
        if random.randint(0, 2) == 1:
            objects['devils'].append({"active" : 1, "type": "t_devil", "start_coords": loc, "coords": loc,"direction" : (0 ,0), "reward": DEVIL_REWARD, "color": "red"})  # c1

    #punem devils pentru a putea aseza obiectele not_near_devils
    map = put_objects(map, objects)

    # player sa fie mereu undeva prin cadaranul 1
    loc1 = spawn_location(map, 1, int(i / 2), 1, int(j / 2), 0)  # c1
    objects['player'].append({"active" : 1, "start_coords": loc1, "coords": loc1,"direction" : (0 ,0),"score" : 1,  "reward": WALK_REWARD, "color": "green"})   #c1
    map = put_objects(map, objects)

    # generam 4 stars (in fiecare cadran cate 1)
    loc1 = spawn_location(map, 1, int(i / 2), 1, int(j / 2), 0)  # c1
    loc2 = spawn_location(map, 1, int(i / 2), int(j / 2), j, 0)  # c2
    loc3 = spawn_location(map, int(i / 2), i, 1, int(j / 2), 0)  # c3
    loc4 = spawn_location(map, int(i / 2), i, int(j / 2), j, 0)  # c4
    objects['stars'].append({"active" : 1, "type": "t_star", "coords": loc1, "reward": STAR_REWARD, "color": "gold"})  # c1
    objects['stars'].append({"active" : 1, "type": "t_star", "coords": loc2, "reward": STAR_REWARD, "color": "gold"})  # c2
    objects['stars'].append({"active" : 1, "type": "t_star", "coords": loc3, "reward": STAR_REWARD, "color": "gold"})  # c3
    objects['stars'].append({"active" : 1, "type": "t_star", "coords": loc4, "reward": STAR_REWARD, "color": "gold"})  # c4
    map = put_objects(map, objects)

    #exist sa fie mereu undeva prin cadranul 4
    loc4 = spawn_location(map, int(i / 2), i, int(j / 2), j, 0)  # c4
    objects['exit'].append({"active" : 1, "type": "t_exit", "coords": loc4, "reward": EXIT_REWARD, "color": "green"})  # c4
    map = put_objects(map, objects)


    # portalele sunt lista de dictionare
    #[portal1, portal2, {"start" : (x1, y1) ,"end" : (x2, y2) , "color" : RED}]

    #generam primele 4 portale (in fiecare cadran cate 1)
    loc1 = spawn_location(map, 1, int(i / 2), 1, int(j / 2), 0)  # c1
    loc2 = spawn_location(map, 1, int(i / 2), int(j / 2), j, 0)  # c2
    loc3 = spawn_location(map, int(i / 2), i, 1, int(j / 2), 0)  # c3
    loc4 = spawn_location(map, int(i / 2), i, int(j / 2), j, 0)  # c4
    # a nu se schimba ordinea asta
    objects['portals'].append({"active" : 1, "start": loc1 ,"end": loc2 , "color": "blue", "visited" : 0})
    objects['portals'].append({"active" : 1, "start": loc2, "end": loc1, "color": "blue", "visited" : 0})
    objects['portals'].append({"active" : 1, "start": loc3, "end": loc4, "color": "purple", "visited" : 0})
    objects['portals'].append({"active" : 1, "start": loc4, "end": loc3, "color": "purple", "visited" : 0})

    #le punem pe harta pentru a nu se suprapune urmatoarele
    map = put_objects(map, objects)

    loc5 = spawn_location(map, 1, int(i / 2), int(j / 2), j, 0) #c2
    loc6 = spawn_location(map, int(i/2), i, 1, int(j/2), 0)     #c3
    objects['portals'].append({"active" : 1, "start": loc5, "end": loc6, "color": "cyan", "visited" : 0})
    objects['portals'].append({"active" : 1, "start": loc6, "end": loc5, "color": "cyan", "visited" : 0})

    map = put_objects(map, objects)

    objects['board'] = {"canvas": canvas, "width" : width, "map" : map, "lines" : lines, "cols" : cols, "walls" : walls, "draw" : 1}

    if args.show_final == 1:
        objects["board"]["draw"] = 0


    #cream fisier map.txt
    out = ""

    for i in range(lines):
        for j in range(cols):
            out += str(map[i][j]) + " "
        out += "\n"

    with open("map.txt", "wt") as file:
        file.write(out)

    return objects, map


