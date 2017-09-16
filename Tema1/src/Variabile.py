RED   = "\033[1;31m"
GREEN = "\033[0;32m"
DARK_YELLOW   = "\033[1;33m"
GRAY  = "\033[1;37m"
BLACK  = "\033[1;38m"

#a nu se schimba ordinea asta
BLUE  = "\033[1;34m"
PURPLE = "\033[0;35m"
CYAN  = "\033[1;36m"

GREEN_B = "\033[42m"
GRAY_B = "\033[47m"
BLACK_B = "\033[100m"
RED_B = "\033[41m" \
        ""
L_RED_B = "\033[1;101m"
L_GREEN_B = "\033[1;102m"

RESET = "\033[0;0m"
BOLD    = "\033[;1m"
REVERSE = "\033[;7m"


#pentru matricea de desen
SPACE = 0
WALL = 1
PLAYER = 2
PLAYER_CONTUR = 2.1
DEVIL = 3
DEVIL_CONTUR = 3.1
STAR = 4
EXIT = 5

#a nu se schimba ordinea asta
PORTAL1 = 6
PORTAL2 = 7
PORTAL3 = 8



INCERCARI = 100     #fail safe daca se incearca punerea a mai mult de 9000 de obiecte
OUTLINE_WIDTH = 2   #grosime de desenare a conturului
PORTAL_WIDTH = 8
EXIT_WIDTH = 8

MAX_ITERATII = 10000

START_SLEEP = 1
SLEEP_FINAL_GAME = 0.4  #sleep de la sfarsit ca sa putem vedea ce a invatat


DEVIL_REWARD = -1
EXIT_REWARD = 1
WALK_REWARD = -0.04
STAR_REWARD = 0.84      #TODO

WIN_SCORE = 1
LOST_SCORE = -1