from tkinter import *
from Generator import *
from Functii_aux import *
from tkinter import *
import time

'''
TODO
gigel nu are mereu next_move (map[i][j] cica e wall cand nu e..)



mai putini gardieni

sa genereza grafice din ce ?


euristica portal -> reward la portal ?


pdf prezentare
'''

args = parse_arguments()

#elemente pentru vizualizarea utilitatii    -> triunghiuletele care s coloreaza
triangle_size = 0.2     #marime triunghiurilor
cell_score_min = -0.4
cell_score_max = 0.4
cell_scores = {}

Width = 40  #latime patratelor


actions = ["up", "down", "left", "right"]


(lines, cols) = (args.map_size_n, args.map_size_m)    #minim 15,15
RAZA_PLAYER = ((lines + cols) / 2) / 20
RAZA_DEVIL = ((lines + cols) / 2) / 15
NUMAR_OBIECTE = (lines + cols) / 3
epsilon = args.epsilon
sleep = args.sleep
restart_sleep = 0.01
fix_map = args.fix_map
learn_rate = args.learn_rate
discount = args.discount

master = Tk()
canvas = Canvas(master, width=lines * Width, height=cols * Width)
canvas.grid(row=0, column=0)

#initializare imagini (depidn de master TK)
player_img = PhotoImage(file='images/player.gif')
devil_img = PhotoImage(file='images/devil.gif')
star_img = PhotoImage(file='images/star.gif')
portal1_img = PhotoImage(file='images/p1.gif')
portal2_img = PhotoImage(file='images/p2.gif')
portal3_img = PhotoImage(file='images/p3.gif')


if fix_map == 0:

    #face peretii si returneaza i lista cu coordonatele lor + o matrice
    walls, map = gen_walls(lines, cols)

    #creaza obiecte care nu se suprapun si actualizeaza map
    objects, map = spawn_objects(map, canvas, walls, lines, cols, Width, args)
else:
    walls, map, objects = read_map("map.txt", canvas, Width)
    pass


#pentru fiecare casuta un tringhiulet ce semnfica utilitatea actiunii de  aalege directa indicata
def create_triangle(i, j, action):




    #down i + 1         down <-> right
    if action == actions[3]:


        return objects["board"]["canvas"].create_polygon((i+0.5-triangle_size)*Width,
                                                         (j+1-triangle_size)*Width,
                                                         (i+0.5+triangle_size)*Width,
                                                         (j+1-triangle_size)*Width,
                                                         (i+0.5)*Width, (j+1)*Width,
                                                         fill="white", width=1)

    #right j + 1        right <-> down
    if action == actions[1]:


        return objects["board"]["canvas"].create_polygon((i+1-triangle_size)*Width, (j+0.5-triangle_size)*Width,
                                    (i+1-triangle_size)*Width, (j+0.5+triangle_size)*Width,
                                    (i+1)*Width, (j+0.5)*Width,
                                    fill="white", width=1)


    #up i - 1        up <-> left
    if action == actions[2]:


        return objects["board"]["canvas"].create_polygon((i+0.5-triangle_size)*Width,
                                                         (j+triangle_size)*Width,
                                                         (i+0.5+triangle_size)*Width,
                                                         (j+triangle_size)*Width,
                                                         (i+0.5)*Width,
                                                         j*Width,
                                    fill="white", width=1)


        # left j - 1    left <-> up
    if action == actions[0]:

        return objects["board"]["canvas"].create_polygon((i + triangle_size) * Width, (j + 0.5 - triangle_size) * Width,
                                                         (i + triangle_size) * Width, (j + 0.5 + triangle_size) * Width,
                                                         i * Width, (j + 0.5) * Width,
                                                         fill="white", width=1)


#desenare harta
def render_grid():

    global walls, Width, lines, cols


    #creaza patratele albe
    for i in range(lines):
        for j in range(cols):
            canvas.create_rectangle(i * Width, j * Width, (i + 1) * Width, (j + 1) * Width, fill="white", width=1)

            temp = {}
            for action in actions:
                temp[action] = create_triangle(i, j, action)
            cell_scores[(i, j)] = temp




    #deseneaza exit
    for exit in objects["exit"]:
        (i, j) = exit["coords"]
        canvas.create_oval(i * Width + PORTAL_WIDTH / 2, j * Width + PORTAL_WIDTH / 2,
                           (i + 1) * Width - PORTAL_WIDTH / 2, (j + 1) * Width - PORTAL_WIDTH / 2,
                           outline=exit["color"], width=PORTAL_WIDTH)
    #desenam portale
    for portal in objects["portals"]:
        (i, j) = portal["start"]
        portal ["outline"] = canvas.create_oval(i * Width + PORTAL_WIDTH / 2, j * Width + PORTAL_WIDTH / 2, (i + 1) * Width - PORTAL_WIDTH / 2, (j + 1) * Width - PORTAL_WIDTH / 2, outline=portal["color"], width=PORTAL_WIDTH)

    # desenam pereti
    for (i, j) in walls:
        canvas.create_rectangle(i * Width, j * Width, (i + 1) * Width, (j + 1) * Width, fill="GRAY", width=1)

    # cream player
    for player in objects["player"]:
        (i, j) = player["coords"]
        player["fill"] = canvas.create_oval(i * Width + Width * 2 / 10, j * Width + Width * 2 / 10,
                                            i * Width + Width * 8 / 10, j * Width + Width * 8 / 10, fill=player["color"],
                                            width=1)
        player["outline"] = canvas.create_oval((i - RAZA_PLAYER) * Width, (j - RAZA_PLAYER) * Width,
                                               (i + 1 + RAZA_PLAYER) * Width, (j + 1 + RAZA_PLAYER) * Width,
                                               outline=player["color"], width=OUTLINE_WIDTH + 1)

    # cream devili
    for devil in objects["devils"]:
        (i, j) = devil["coords"]
        devil["fill"] = canvas.create_image(i * Width, j * Width, image=devil_img, anchor=NW)
        devil["outline"] = canvas.create_oval((i - RAZA_DEVIL) * Width, (j - RAZA_DEVIL) * Width,
                                              (i + 1 + RAZA_DEVIL) * Width, (j + 1 + RAZA_DEVIL) * Width,
                                              outline=devil["color"], width=OUTLINE_WIDTH)

    # cream recompensele
    for star in objects["stars"]:
        (i, j) = star["coords"]
        star["fill"] = canvas.create_image(i * Width, j * Width, image=star_img, anchor=NW)

# configureaza culoarea sagetii catre o stare in urma unei actiuni
# in functie de award rosu sau verde
def set_cell_score(state, action, val):

    global cell_score_min, cell_score_max

    triangle = cell_scores[state][action]

    green_dec = int(min(255, max(0, (val - cell_score_min) * 255.0 / (cell_score_max - cell_score_min))))
    green = hex(green_dec)[2:]
    red = hex(255 - green_dec)[2:]
    if len(red) == 1:
        red += "0"
    if len(green) == 1:
        green += "0"
    color = "#" + red + green + "00"


    objects["board"]["canvas"].itemconfigure(triangle, fill=color)


#pentru miscarea manual a jucatorului
# dar dierctia dupa (x,y) un fel de (j,i)
def call_up(event):
    for player in objects["player"]:
        player["direction"] = (0 ,-1)


def call_down(event):
    for player in objects["player"]:
        player["direction"] = (0, 1)


def call_left(event):
    for player in objects["player"]:
        player["direction"] = (-1 ,0)


def call_right(event):
    for player in objects["player"]:
        player["direction"] = (1 ,0)

def call_space(event):
    global sleep, restart_sleep
    if objects["board"]["draw"] == 0:
        objects["board"]["draw"] = 1
        sleep = SLEEP_FINAL_GAME
        restart_sleep = 1.01
        print("===================TOGGLE DRAW ON===================")

    else:
        objects["board"]["draw"] = 0
        sleep = 0
        restart_sleep = 0.01

        print("===================TOGGLE DRAW OFF===================")






#redeseneaza jocul in starea initiala (prin modificarea coordonatelor
def restart_game():

    #denumire mai scurta
    player = objects["player"][0]
    player["score"] = 1

    #relocare player
    player["coords"] = player["start_coords"]
    (i, j) = player["coords"]
    canvas.coords(player["fill"], i * Width + Width * 2 / 10, j * Width + Width * 2 / 10,
                  i * Width + Width * 8 / 10, j * Width + Width * 8 / 10)
    canvas.coords(player["outline"], (i - RAZA_PLAYER) * Width, (j - RAZA_PLAYER) * Width,
                  (i + 1 + RAZA_PLAYER) * Width, (j + 1 + RAZA_PLAYER) * Width)

    #relocare devili
    for devil in objects["devils"]:
        devil["coords"] = devil["start_coords"]

        (i, j) = devil["coords"]
        canvas.coords(devil["fill"], i * Width, j * Width)
        canvas.coords(devil["outline"], (i - RAZA_DEVIL) * Width, (j - RAZA_DEVIL) * Width,
                      (i + 1 + RAZA_DEVIL) * Width, (j + 1 + RAZA_DEVIL) * Width)


    #reactiare portal si recompense
    for star in objects["stars"]:
            star["active"] = 1


    for portal in objects["portals"]:
            portal["active"] = 1





render_grid()
master.title("Tema 1 ML")

master.bind("<Up>", call_up)
master.bind("<Down>", call_down)
master.bind("<Right>", call_right)
master.bind("<Left>", call_left)
master.bind("<space>", call_space)

def start_game():
    master.mainloop()


