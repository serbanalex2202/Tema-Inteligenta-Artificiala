import math
from Variabile import *
import random
import World
from argparse import ArgumentParser
from tkinter import *



#calculeaza distanta euclidiana
def distance(p0, p1):
    return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)


#verifica daca 2 puncte date sunt in acelasi cadran
def in_cadran(map, p1, p2):

    (lines, cols) = map.shape
    (i_1, j_1) = p1
    (i_2, j_2) = p2

    #cadran 1 0 lines/2
            ##0 col/2
    if 0 < i_1 < lines/2 and 0 < j_1 < cols/2 and 0 < i_2 < lines/2 and 0 < j_2 < cols/2:
        return 1    #da
    #cadran 2
    if 0 < i_1 < lines/2 and cols/2 < j_1 < cols and 0 < i_2 < lines/2 and cols/2 < j_2 < cols:
        return 1    #da

    #CADRAN3
    if lines/2 < i_1 < lines and 0 < j_1 < cols/2 and lines/2 < i_2 < lines and 0 < j_2 < cols/2:
        return 1    #da

    #cadran4
    if lines/2 < i_1 < lines and cols/2 < j_1 < cols and lines/2 < i_2 < lines and cols/2 < j_2 < cols:
        return 1    #da

    return 0



#verifica daca player se aflua pe un portal, daca da returneaza noile coordonate ale lui player
def teleport(player, objects):

    for p in objects["portals"]:
        if player == p["start"]:
            if World.args.player_strategy != 5:
                return p["end"]
            else:
                if p["active"] == 1:

                    p["active"] = 0 #dezactiveaza portalul dupa ce il folosesti

                    #si dezactiva si capatul
                    for p2 in objects["portals"]:
                        if p2["start"] == p["end"]:
                            p2["active"] = 0

                    return p["end"]


    return player



#returneaza 1 daca este liber culuarul pana la jucator (liber : fara portale recompense, ziduri
def path_clear(map, p_devil, p_player):
    (i_devil, j_devil) = p_devil
    (i_player, j_player) = p_player

    if (i_devil == i_player):   #sunt pe aceasi linie => ne miscam pe coloane
        #in functie de care e mai mica facem alta parcurgere
        if (j_devil < j_player):
            for j in range (j_devil, j_player):
                if map[i_devil][j] != SPACE:
                    return 0

        else:
            for j in range (j_player, j_devil):
                if map[i_devil][j] != SPACE:
                    return 0


    if (j_devil == j_player): #sunt pe aceasi coloana => ne miscam pe linii
        #in functie de care este mai mica facem alta parcurgere
        if (i_devil < i_player):
            for i in range (i_devil, i_player):
                if map[i][j_devil] != SPACE:
                    return 0

        else:
            for i in range (i_player, i_devil):
                if map[i][j_devil] != SPACE:
                    return 0

    return 1


def in_map(map, p):
    if map[p[0]][p[1]] == WALL:
        return 0
    else:
        return 1

#muta devil daca player este vizibil si daca este in raza de actiune
def next_move_devil_on_sight(map, p_devil, p_player):



    #daca suntem suficient de aproape
    if distance(p_devil, p_player) <= World.RAZA_DEVIL: #and in_cadran(map, p_player, p_devil) == 1:

            (i_devil, j_devil) = p_devil
            (i_player, j_player) = p_player

            if path_clear(map, p_devil, p_player ) == 1:


                # daca suntem pe aceasi linie -> il miscam pe coloane (j)
                if (i_devil == i_player):



                    if(j_devil < j_player):
                        j_devil += 1
                    else:
                        j_devil -= 1

                #daca sun pe aceasi coloana -> miscam pe linii (i)
                if (j_devil == j_player):
                    if (i_devil < i_player):
                        i_devil += 1
                    else:
                        i_devil -= 1



            if in_map(map, (i_devil, j_devil)) == 1:
                return (i_devil, j_devil)

    return p_devil


#devil se va misca in directia ce ii confera o distanta mai mica catre player
#devil va vedea playerul doar in cadranul sau si la o distanta mai mica de raza_devil
def next_move_devil_on_distance(map, p_devil, p_player):

    (i_devil, j_devil) = p_devil
    (i_player, j_player) = p_player

    #daca e in cadranul meu si la distanta mai mica de size/4
    distanta_curenta = distance((i_devil,j_devil), (i_player, j_player))

    diferenta_minima = 9000
    next_i_devil = i_devil
    next_j_devil = j_devil

    r = random.random()
    #cu probabilitate mare fa asta, altfel ramai pe loc ca sa nu se blocheze jocul ?
    if  distanta_curenta < World.RAZA_DEVIL and in_cadran(map, p_player, p_devil) and r < 0.9:

        #try RIGHT
        if map[i_devil][j_devil + 1] in [SPACE, STAR, PLAYER]:
            distanta_r = distance((i_devil, j_devil + 1), (i_player, j_player))
            if distanta_r - distanta_curenta < diferenta_minima:
                next_i_devil = i_devil
                next_j_devil = j_devil + 1
                diferenta_minima = distanta_r - distanta_curenta

        #try LEFT
        if map[i_devil][j_devil - 1] in [SPACE, STAR, PLAYER]:
            distanta_l = distance((i_devil, j_devil - 1), (i_player, j_player))
            if distanta_l - distanta_curenta < diferenta_minima:
                next_i_devil = i_devil
                next_j_devil = j_devil - 1
                diferenta_minima = distanta_l - distanta_curenta

        #try UP
        if map[i_devil + 1][j_devil] in [SPACE, STAR, PLAYER]:
            distanta_u = distance((i_devil + 1, j_devil), (i_player, j_player))
            if distanta_u - distanta_curenta < diferenta_minima:
                next_i_devil = i_devil + 1
                next_j_devil = j_devil
                diferenta_minima = distanta_u - distanta_curenta

        #try DOWN
        if map[i_devil - 1][j_devil] in [SPACE, STAR, PLAYER]:
            distanta_d = distance((i_devil - 1, j_devil), (i_player, j_player))
            if distanta_d - distanta_curenta < diferenta_minima:
                next_i_devil = i_devil - 1
                next_j_devil = j_devil

    #daca nu avem next move ramane pe loc
    return (next_i_devil, next_j_devil) #next_random_move(map, i_devil, j_devil)

#retruneaza o pozitie random
def next_random_move(map, i, j):

    incercari = 0
    while incercari < INCERCARI:

        direction = random.randint(0, 5)

        #jos
        if direction == 0:
            if map[i + 1][j] != WALL:
                return (i + 1, j)
        #dreapta
        if direction == 1:
            if map[i][j + 1] != WALL:
                return (i, j+1)

        #sus
        if direction == 2:
            if map[i - 1][j] != WALL:
                return (i - 1, j)

        #stanga
        if direction == 3:
            if map[i][j - 1] != WALL:
                return (i, j - 1)

        #stai pe loc
        if direction == 4:
            return (i, j)

        incercari += 1


    print("nu am gasit casuta libera ?!")
    return (i, j)

def next_move_player_e_greedy(map, i_player, j_player, i, j):

    r = random.random()

    if r < World.args.epsilon:
        #print("next_move__player e greedey : r : ", r, "=> RANDOM")
        return next_random_move(map,i_player, j_player)
    else:
        #print("next_move__player e greedey : r : ", r)
        return next_move_player_max_first(map, i_player, j_player, i, j)

#returneaza urmatoarea pozitie pentru player daca se poate muta in directia aia
def next_move_player_max_first(map, i_player, j_player, to_i, to_j):

    if map[i_player + to_i][ j_player + to_j] != WALL:
        return (i_player + to_i, j_player + to_j)

    return (i_player, j_player)


def try_move(map, p_player):

    (i,j) = p_player
    (add_i, add_j) = p_player["direction"]
    if map[i + add_i][j + add_j] != WALL:
        p_player["direction"] = (0,0)
        return (i + add_i, j + add_j)
    else:
        p_player["direction"] = (0, 0)
        return (i,j)



#alege o strategie de joc in functei de argumentele primite
def move_player(map, coords_player, max_first_move_direction):


    (i_player, j_player) = coords_player
    (i, j) = max_first_move_direction

    # 0 sta pe loc
    if World.args.player_strategy == 0:
        return (i_player, j_player)

    # 1 max first
    if World.args.player_strategy == 1:
        return next_move_player_max_first(map, i_player, j_player, i, j)

    # 2 random
    if World.args.player_strategy == 2:
        return next_random_move(map, i_player, j_player)

    # 3 epsilon greedy
    if World.args.player_strategy == 3:
        return next_move_player_e_greedy(map, i_player, j_player, i, j)

    # 4 Manual pentru debug
    if World.args.player_strategy == 4:
        return try_move(map, coords_player)

    # Smart Portal mark - nu o ia si inapoi prin portale
    if World.args.player_strategy == 5:
        return next_move_player_max_first(map, i_player, j_player, i, j)

    #daca nu e selectata nicio obtiune player sta pel loc
    return (i_player, j_player)

#in functie de argumentele primite alege o decizie
def move_devil(map,p_devil, p_player):


    # 0 sta pe loc
    if World.args.devil_strategy == 0:
        return p_devil

    # 1 random dar nu e ok ca nu invata nimic player
    if World.args.devil_strategy == 1:
        return next_random_move(map, p_devil[0], p_devil[1])

    # 2 se misca daca il vede in raza de actiune
    if World.args.devil_strategy == 2:
        return next_move_devil_on_sight(map, p_devil, p_player)

    # 3 se misca spre player in raza de actiune
    if World.args.devil_strategy == 3:
        return next_move_devil_on_distance(map, p_devil, p_player)

    #nicio obtiune aleasa sta pe loc
    return  p_devil

#relocheaza obiecte
def board_redraw(objects):

        canvas = objects["board"]["canvas"]
        Width = objects["board"]["width"]
        for player in objects["player"]:

            #e (j i) pentru ca le ia ca coordonate x y
            (i, j) = player["coords"]
            canvas.coords(player["fill"], i * Width + Width * 2 / 10, j * Width + Width * 2 / 10,
                          i * Width + Width * 8 / 10, j * Width + Width * 8 / 10)
            canvas.coords(player["outline"], (i - World.RAZA_PLAYER) * Width, (j - World.RAZA_PLAYER) * Width,
                     (i + 1 + World.RAZA_PLAYER) * Width, (j + 1 + World.RAZA_PLAYER) * Width)


        for devil in objects["devils"]:
            # e (j i) pentru ca le ia ca coordonate x y
            (i, j) = devil["coords"]
            canvas.coords(devil["fill"], i * Width, j * Width)
            canvas.coords(devil["outline"], (i - World.RAZA_DEVIL) * Width, (j - World.RAZA_DEVIL) * Width,
                         (i + 1 + World.RAZA_DEVIL) * Width, (j + 1 + World.RAZA_DEVIL) * Width)

        for star in objects["stars"]:
            if star["active"] == 1:
                # vizibil
                canvas.itemconfigure(star["fill"], state = NORMAL)
            else:
                # not vizibil
                canvas.itemconfigure(star["fill"], state=HIDDEN)

        for portal in objects["portals"]:
            if portal["active"]:
                canvas.itemconfigure(portal["outline"], outline=portal["color"])
            else:
                canvas.itemconfigure(portal["outline"], outline="GRAY")


def parse_arguments():
    parser = ArgumentParser()

    # Map
    parser.add_argument("--map_size_n", type=int, default=15,
                        help="Dimensiunea hartii n - linii")
    parser.add_argument("--map_size_m", type=int, default=15,
                        help="Dimensiunea hartii m - coloane")


    # Meta-parameters
    parser.add_argument("--learn_rate", type=float, default=0.1,
                        help="Learning rate")
    parser.add_argument("--discount", type=float, default=0.3,
                        help="Value for the discount factor")
    parser.add_argument("--epsilon", type=float, default=0.01,
                        help="Probability to choose a random action.")


    # Training and evaluation episodes
    parser.add_argument("--train_episodes", type=int, default=100,
                        help="Number of episodes")
    parser.add_argument("--eval_every", type=int, default=10,
                        help="Evaluate policy every ... games.")
    parser.add_argument("--eval_episodes", type=float, default=10,
                        help="Number of games to play for evaluation.")


    # Display
    parser.add_argument("--plot", type=int, default=1,
                        help="Plot scores in the end")
    parser.add_argument("--sleep", type=float, default=0.0001,        #SLEEEEEEEEP
                        help="Seconds to 'sleep' between moves.")
    parser.add_argument("--show_final", type=int, default=1,        #FINAAAAAAAl
                        help="1 arata direct meciul final, 0 arata toate meciurile")
    parser.add_argument("--fix_map", type=int, default=1,   #mapa fixa pentru teste
                        help="Setam fix_map 1 pentru a genera mereu aceasi harta")

    # Move Strategies
    parser.add_argument("--player_strategy", type=int, default=2,
                        help="Strategia de joc a lui player : "
                             "0 Sta pe loc"
                             "1 Max First"
                             "2 Random"
                             "3 Egreedy"
                             "4 Manual"
                             "5 Smart mark portals")

    parser.add_argument("--devil_strategy", type=int, default=0,
                        help="Strategia de joc a lui devil :"
                             "0 sta pe loc"
                             "1 Random"
                             "2 On sight - doar sus stanga"
                             "3 On distance")


    return parser.parse_args()
