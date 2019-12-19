import sys
import os
import time
import pygame




scriptpath, filepath = os.path.realpath(__file__), "" # Get the file path to the screenshot image to analize 
for i in range(1,len(scriptpath)+1):
    if scriptpath[-i] == "\\":
        scriptpath = scriptpath[0:-i]
        break
if os.getcwd() != scriptpath: filepath = scriptpath + "\\"

def virtual_game_loop():
    quit_game = False
    FPS = 10/10    
    board_dimension = [width*orb_dis_size, height*orb_dis_size]
    create_board(board_dimension)
    #create_vector("red", [])           #####################################################
    pygame.display.update()
    #cv2.waitKey(8000)
    #"""
    dt = 0
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
        if dt>3: break
    #"""
    pygame.quit()
    quit()

def create_vector(orb_color, final_pos):
    sources, destinations = find_aggregate_shortest_path(orb_color, final_pos)
    find_combined_path(sources, destinations)
    """
    stack = deque()
    for i in range(len(final_pos))
        stack.append()
    lst = {0: "white", 1: "royalblue", 2:"hotpink", 3:"darkgray",4:"indianred" }
    pygame.draw.rect(boardscreen, pygame.Color("antiquewhite3"), [(sp[0]-vect[0]+0.4)*orb_dis_size, (sp[1]-vect[1]+0.4)*orb_dis_size, 30, 30])
    pygame.draw.rect(boardscreen, pygame.Color("ivory4"), [(sp[0]+0.4)*orb_dis_size, (sp[1]+0.4)*orb_dis_size, 30, 30])
    """

def draw_vector(color, starting_coor, end_coor):
    vect_thick = 15
    start_x, start_y = starting_coor[0], starting_coor[1]
    end_x, end_y = end_coor[0], end_coor[1]
    vect_x, vect_y = start_x-end_x , start_y - end_y
    if vect_x != 0 and vect_y != 0:
        pygame.draw.rect(boardscreen, pygame.Color(color), [(start_x+0.4)*orb_dis_size, (start_y+0.4)*orb_dis_size, -vect_x*orb_dis_size, vect_thick])
    elif vect_x != 0:
        pygame.draw.rect(boardscreen, pygame.Color(color), [(start_x+0.4)*orb_dis_size, (start_y+0.4)*orb_dis_size, -vect_x*orb_dis_size, vect_thick])
    elif vect_y != 0:
        pygame.draw.rect(boardscreen, pygame.Color(color), [(start_x+0.4)*orb_dis_size, (start_y+0.4)*orb_dis_size, vect_thick, (vect_y)*orb_dis_size])

def create_board(board_size):
    color_dict = {"red": "red2", "blue":"royalblue", "green":"forestgreen", "light": "gold1", "dark": "darkviolet", "heart": "lightsalmon1"}
    #red1,2,3,4, indianred
    #royalblue, steelblue1, blue4, deepskyblue
    #springgreen, darkgreen, forestgreen
    #darkviolet, darkgray
    #lightsalmon, hotpink, pink, lightpink
    for i in range(5):
        for j in range(6):
            color_for_vis = color_dict[board[i][j][0]]
            pygame.draw.rect(boardscreen, pygame.Color(color_for_vis), (j*100 + 2, i*100 + 2,  96, 96))
    pygame.display.flip()

width, height = 6, 5
orb_dis_height = 100
orb_dis_size = 100
visualize = True

board = [[ "green", "dark", li, "dark", li, "dark"],
[ li, he, re, gr, gr, li],
[ li, he, li, he, gr, he],
[ "dark", li, re, he, li, re],
[ re, "dark", li, re, "dark", bl]]



if visualize:
        pygame.init()
        board_dimension = [width*orb_dis_size, height*orb_dis_size]
        boardscreen = pygame.display.set_mode(board_dimension)
        boardscreen.fill(pygame.Color("black"))
        pygame.display.set_caption("PAD solver visualized")
        virtual_game_loop()
