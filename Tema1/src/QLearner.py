import World
import threading
import time
from Variabile import *
from Functii_aux import *
import matplotlib.pyplot as plt

#initializari


#astea se modifica dupa apelarea init_variables()

actions = World.actions
directions = {"up" : (-1, 0), "down" : (1, 0), "left" : (0, -1), "right" : (0 , 1)}

states = []     #starile = pozitile map[i][j]
Q = {}
val_scor_restart = 0

scoruri_finale = []
episoade = 0
play_last_game = 0
actiuni = 0

exit = World.objects["exit"][0]
player = World.objects["player"][0]
map = World.objects["board"]["map"]


def plot_exit():
        #da eroare la plot in pycharm (nu stiu de ce)
        print("scoruri_finale",scoruri_finale)

        plt.plot(scoruri_finale)

        plt.ylim([-81, 81])

        plt.xlabel("Episode")
        plt.ylabel("Final score")

        plt.show()



##actiunea maxima si valoarea ei
def max_Q(s):
    val = None
    act = None
    for a, q in Q[s].items():
        if val is None or (q > val):
            val = q
            act = a
    return act, val


def inc_Q(s, a, alpha, inc):
    Q[s][a] *= 1 - alpha
    Q[s][a] += alpha * inc

    World.set_cell_score(s, a, Q[s][a])


def init_states_and_Q():
    for i in range(World.lines):
        for j in range(World.cols):
            states.append((i, j))

    for state in states:
        temp = {}
        for action in actions:      #up down left right
            temp[action] = 0.1
            #World.set_cell_score(state, action, temp[action])
        Q[state] = temp


        # seteaza in matricea Q awardul primit
        # # seteaza scorul pentru o anumita stare/matrice pe baza caruia desenez rosu-verde utilitatea catre acea casuta
    for awards_type in World.objects["devils"], World.objects["exit"], World.objects["stars"]:
        for award in awards_type:
            (i, j) = award["coords"]
            for action in actions:
                pass
                #Q[(i, j)][action] = award["reward"] #TODO nu mai trebuie ca se misca balaurul
                #World.set_cell_score((i, j), action, award["reward"])



def init_variables():
    global START_SLEEP


    START_SLEEP = 1


# primeste actiunea optima si incearca sa o execute
# returneaza starea1/locatia initiala, actiunea primita, status de restart(r) si starea2
def do_action(action):
    global val_scor_restart, scoruri_finale


    r = -player["score"]

    # move devils
    if World.args.devil_strategy != 0:  #daca e 0 devils stau pe loc
        for devil in World.objects["devils"]:
            devil["coords"] = move_devil(map, devil["coords"], player["coords"])

    #draw game and sleep to see it
    if World.objects["board"]["draw"] == 1:
        board_redraw(World.objects)
        time.sleep(World.sleep)

    #check game end
    for devil in World.objects["devils"]:
        if devil["coords"] == player["coords"]:
            val_scor_restart = -1
            player["score"] += devil["reward"]
            s2 = player["coords"]
            r += player["score"]

            return action, r, s2  # returneaza


    #---------------------------
    #move player
    player["coords"] = move_player(map, player["coords"], directions[action])



    player["score"] += WALK_REWARD

    for star in World.objects["stars"]:
        if star["coords"] == player["coords"] and star["active"] == 1:
            player["score"] -= WALK_REWARD  # nu mai contorizam walk cost
            player["score"] += star["reward"]
            star["active"] = 0


    # teleport player if on portal
    player["coords"] = teleport(player["coords"], World.objects)  # schimba pozitia playeurlui daca se afla pe un portal activ


    # draw game and sleep to see it
    if World.objects["board"]["draw"] == 1:
        board_redraw(World.objects)
        #time.sleep(World.sleep)

    if exit["coords"] == player["coords"]:
        val_scor_restart = 1    #WIN
        player["score"] -= WALK_REWARD  #nu mai contorizam walk cost
        player["score"] += exit["reward"]


    s2 = player["coords"]
    r += player["score"] # + val_scor_restart
    return action, r, s2     #returneaza


#functia rulata de thread
def run():
    global actiuni, val_scor_restart, episoade, play_last_game, scoruri_finale, sleep
    time.sleep(START_SLEEP) #sleep de inceput
    alpha = 1
    t = 1

    player = World.objects["player"][0]

    while True:


        s = player["coords"]

        #alege actiunea cu utilitatea cea mai mare
        max_act, max_val = max_Q(s)




        #executa actiunea
        (a, r, s2) = do_action(max_act)


        actiuni += 1

        # Update Q
        max_act, max_val = max_Q(s2)


        inc_Q(s, a, alpha, r + World.discount * max_val)

        t += 1.0

        if actiuni > 200:

            print("actiuni > 200 ", actiuni)
            print("scor", player["score"])
            print("episod : ", episoade)
            print("")

            World.restart_game()
            val_scor_restart = 0
            actiuni = 0
            time.sleep(World.restart_sleep)  # sa apuce sa faca restart

        # Check if the game has restarted
        if val_scor_restart in [1, -1]:

            print("episod : ", episoade)
            print("scor : ", player["score"])
            print("")
            scoruri_finale.append(player["score"])
            World.restart_game()
            actiuni = 0
            val_scor_restart = 0
            time.sleep(World.restart_sleep)    #sa apuce sa faca restart

            t = 1.0

            episoade += 1
            print("episode : ", episoade)
            if play_last_game == 1:
                World.objects["board"]["draw"] = 1
                sleep = SLEEP_FINAL_GAME #setam sleep mai mare ca sa putem vedea




        #------------------------terminare joc
        #dupa un numar maixim de episoade ne oprim
        if episoade >= World.args.train_episodes:
            play_last_game = 1


        # Update the learning rate
        alpha = pow(t, -World.learn_rate)

        if World.args.plot == 1 and play_last_game == 1:
            plot_exit()
            play_last_game = 2


        time.sleep(World.sleep)




init_states_and_Q()
init_variables()


# creaza un nou thred care ruleaza jocul
t = threading.Thread(target=run)
t.daemon = True
t.start()

World.start_game()

