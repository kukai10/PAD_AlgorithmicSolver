import sys
import os
import time
import pygame
import pyautogui as auto

scriptpath, filepath = os.path.realpath(__file__), "" # Get the file path to the screenshot image to analize 
for i in range(1,len(scriptpath)+1):
    if scriptpath[-i] == "\\":
        scriptpath = scriptpath[0:-i]
        break
if os.getcwd() != scriptpath: filepath = scriptpath + "\\"

def virtual_game_loop():
    quit_game = False
    FPS, dt = 10/10, 0
    create_board(board_dimension)
    draw_vector("darkorange1", [2,1], [0,0])
    pygame.display.update()
    clock = pygame.time.Clock()
    while not quit_game:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    quit_game = True
        pygame.display.update()
        clock.tick(FPS)
        dt+=1/FPS
        if dt>2: quit_game = True
    pygame.quit()
    quit()

def create_vector(orb_color, final_pos):
    sources, destinations = find_aggregate_shortest_path(orb_color, final_pos)
    find_combined_path(sources, destinations)

def draw_vector(color, starting_coor, end_coor):
    vect_thick = 15
    start_x, start_y = starting_coor[0], starting_coor[1]
    end_x, end_y = end_coor[0], end_coor[1]
    vect_x, vect_y = start_x-end_x , start_y - end_y
    if vect_x != 0 and vect_y != 0:
        pygame.draw.rect(boardscreen, pygame.Color(color), [(start_x+0.4)*vis_orbsize, (start_y+0.4)*vis_orbsize, -vect_x*vis_orbsize, vect_thick])
        pygame.draw.rect(boardscreen, pygame.Color(color), [(start_x+0.4-vect_x)*vis_orbsize,(start_y+0.4)*vis_orbsize+vect_thick-1, vect_thick, -vect_y*vis_orbsize])
    elif vect_x != 0:
        pygame.draw.rect(boardscreen, pygame.Color(color), [(start_x+0.4)*vis_orbsize, (start_y+0.4)*vis_orbsize, -vect_x*vis_orbsize, vect_thick])
    elif vect_y != 0:
        pygame.draw.rect(boardscreen, pygame.Color(color), [(start_x+0.4)*vis_orbsize, (start_y+0.4)*vis_orbsize, vect_thick, (vect_y)*vis_orbsize])

def create_board(board_size):
    color_dict = {"red": "red3", "blue":"turquoise1", "green":"green3", "light": "goldenrod2", "dark": "darkorchid4", "heart": "violetred1"}
    for i in range(height):
        for j in range(width):
            if((i+j)%2==0):# makes a checker pattern with light and dark brown
                pygame.draw.rect(boardscreen, (54,32,34), (j*vis_orbsize+vis_padding, i*vis_orbsize+vis_padding, vis_orbsize-2*vis_padding, vis_orbsize-2*vis_padding))
            else:# background color (54,32,34), (102,60,48)
                pygame.draw.rect(boardscreen, (102,60,48), (j*vis_orbsize+vis_padding, i*vis_orbsize+vis_padding, vis_orbsize-2*vis_padding, vis_orbsize-2*vis_padding))
            color_for_vis = color_dict[board[i][j]] #[0]**************************************************
            pygame.draw.circle(boardscreen, pygame.Color(color_for_vis), ((j*vis_orbsize)+vis_center,(i*vis_orbsize)+vis_center), vis_radius)
    pygame.display.flip()


#### main function   #########
screen_x, screen_y = auto.size()
print(screen_x, screen_y)
width, height = 6, 5
#### visualize with pygame #####
visualize = True
vis_orbsize, vis_padding = 100, 2
vis_center = int(vis_orbsize/2)
vis_radius = int(vis_center*0.8)
print(vis_center, vis_radius)
board = [[ "green", "dark",  "light", "dark",  "light", "dark" ],
         [ "light", "heart", "red",   "green", "green", "light"],
         [ "light", "heart", "light", "heart", "green", "heart"],
         [ "dark",  "light", "red",   "heart", "light", "red"  ],
         [ "red",   "dark",  "light", "red",   "dark",  "blue" ]]
board1 = [["green", "dark",  "light", "dark",  "light", "dark",  "red"  ],
         [ "light", "heart", "red",   "green", "green", "light", "blue" ],
         [ "light", "heart", "light", "heart", "green", "heart", "green"],
         [ "dark",  "light", "red",   "heart", "light", "red",   "dark" ],
         [ "red",   "dark",  "light", "red",   "dark",  "blue",  "light"],
         [ "red",   "dark",  "light", "red",   "blue",  "red",   "light"]]
if True:
    board = board1
    width, height = 7, 6
visualize=False
if visualize:
        pygame.init()
        board_dimension = [width*vis_orbsize, height*vis_orbsize]
        boardscreen = pygame.display.set_mode(board_dimension)
        boardscreen.fill(pygame.Color("black"))
        pygame.display.set_caption("PAD solver visualized")
        virtual_game_loop()
