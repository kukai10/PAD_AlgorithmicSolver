import sys
import time
import math
import pyautogui as auto
from itertools import product, combinations, permutations
import os
from collections import deque
import imutils
import functools
import cv2
import numpy as np
import pygame

def clock(func): # version 2, page 203 - 205
    @functools.wraps(func)
    def clocked(*args, **kwargs):
        t0 = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - t0
        arg_lst = [] #name = func.__name__
        if args:
            arg_lst.append(', '.join(repr(arg) for arg in args))
        if kwargs:
            pairs = ["%s=%r" % (k,w) for k, w in sorted(kwargs.items())]
            arg_lst.append(", ".join(pairs))
        arg_str = ", ".join(arg_lst)
        print("[%0.8fs] %s(%s) -> %r " % (elapsed, func.__name__, arg_str, result))
        return result
    return clocked

def main():  
    maxMoveStep = 140 #max number of moves teh algorithm will take
    puzzleMoveTime, sleepTime = 8.5, 0.001 #seconds
    movePixel, moveTime= None, puzzleMoveTime/maxMoveStep
    visualize = True # option to visualize the actions occuring between the start to the end
    visualize = False
    move_mouse = False
    mouse_dic = {"u": [0,-1], "d": [0,1], "l": [-1,0], "r": [1,0]}
    screen_x, screen_y = auto.size()
    ########################    main     ###########################
    movement = ""
    board_image, board_image_gray = None, None
    height, width = None, None
    orb_position = search_for_orbs(visualize)
    finished_on_board = []
    top_left_pos, bottom_right_pos = orb_position[0][0][1], orb_position[height-1][width-1][2]
    [board_pixel_x, board_pixel_y] = [abs(a-b) for a, b in zip(top_left_pos, bottom_right_pos)]
    move_pixel =  board_pixel_x//width # the orb is a square so the height is the same
    norm_orb_position = normalize_pos(orb_position)
    board = norm_orb_position[:]
    printboard(norm_orb_position)
    pt_mover  = None
    orb_count_dic, potential_mover = find_potential_mover(norm_orb_position)
    print("orb dictionary: ", orb_count_dic, "\n potential movers: ", potential_mover)
    #create_patterns(orb_count_dic)
    switch_orb((0,0),(0,1))
    orb_dis_size = 100
    
    if visualize:
            pygame.init()
            board_dimension = [width*orb_dis_size, height*orb_dis_size]
            boardscreen = pygame.display.set_mode(board_dimension)
            boardscreen.fill(pygame.Color("black"))
            pygame.display.set_caption("PAD solver visualized")
            virtual_game_loop()

def movemouse(letter): # inputs are u, d, l, or r; which moves the mouse by the distance between two orbs 
    vector = mouse_dic[letter]
    auto.moveRel(move_pixel*vector[0], move_pixel*vector[1] ,move_time)
    time.sleep(sleep_time)

def locate_on_screen(visualize, name_of_template, prov_ratio1 = None, prov_ratio2 = None, icon = None): # finds template image in the screen shot 
    #print("looking for ", name_of_template, " given the ratio", prov_ratio1, prov_ratio2)
    foldername = "ImageFile\\" if icon == "Orb" else ""
    if icon == "Orb": max_factor = [5,6]
    elif icon == "screen_elements": max_factor = [7, 10]
    else: max_factor = [4,4]
    # get template image and convert to gray scale
    template = cv2.imread(filepath+foldername+name_of_template, cv2.IMREAD_GRAYSCALE)
    template_gray = cv2.Canny(template, 50, 200)
    template_w_org, template_h_org = template_gray.shape[::-1] # initial height and width of template image 
    found, threshold, maxVal = None, 0.5, 0 # prameters that affect the searching process
    scale2 = np.linspace(0.5,1.0, 20)[::-1] if (prov_ratio2 == None) else np.linspace(min((1/prov_ratio2)-0.1, 0.8), min((1/prov_ratio2)+0.1, 1), 3)
    scale1 = np.linspace(0.2, 1.0, 20)[::-1] if (prov_ratio1 == None) else np.linspace(min((1/prov_ratio1)-0.1,0.8), min((1/prov_ratio1)+0.1, 1), 3)
    
    # the following loops, chnages the scale of both screen shot and template, then it keeps the ratio that gave the highest matching percentage
    # need two scale because templates can be sometimes too small to beign with, for example playing with a 2048x2048 pixel screen
    for rescaleFactor1 in scale2:
        resized_template = imutils.resize(template_gray, width = int(template_w_org*rescaleFactor1)) #keeps aspect ratio
        template_w, template_h = resized_template.shape[::-1]
        ratio2 = template_w_org/float(resized_template.shape[1])
        for rescaleFactor in scale1:
            resized = imutils.resize(board_image_gray, width = int(board_image_gray.shape[1] * rescaleFactor)) # resize screenshot
            ratio1 = board_image_gray.shape[1] / float(resized.shape[1]) 
            if resized.shape[0] < template_h*max_factor[0] or resized.shape[1] < template_w*max_factor[1]: break # break if template is bigger than scaled screenshot
            edged = cv2.Canny(resized,50, 200)
            result = cv2.matchTemplate(edged, resized_template, cv2.TM_CCOEFF_NORMED)#############template
            (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result) #we only care about the min val and locqq
            if visualize: # if visualize is true show orginal image with borders around the things matching from the templates
                    clone = np.dstack([edged, edged, edged])
                    cv2.rectangle(clone, (maxLoc[0], maxLoc[1]), (maxLoc[0] +template_w, maxLoc[1] + template_h), (0, 0, 255), 2)
                    cv2.imshow("Visualize", clone)
                    cv2.waitKey(50) # stops for 0.5 seconds
            if found is None or maxVal > found[0]:
                found, location = (maxVal, maxLoc, ratio1, ratio2), np.where(result>=0.4)
                if maxVal > threshold: 
                    #print("max val is greater than ", threshold)
                    break 
        if maxVal > threshold: break
    (_, maxLoc, ratio1, ratio2), positions = found, []
    # end of loop
    for pt in zip(*location[::-1]): # loop through the position of found templates and make a list with required fields
        start_loc, end_loc =(int(pt[0]*ratio1), int(pt[1]*ratio1)), (int((pt[0]*ratio1)+(template_w_org*ratio1/ratio2)), int((pt[1]*ratio1)+(template_h_org*ratio1/ratio2)))
        positions.append([list(start_loc), list(end_loc)])
        cv2.rectangle(board_image,start_loc, end_loc , (0,0,255), 2)
    if positions == []: return (None, None, None) # if nothing was found
    if visualize == True:
        cv2.imshow("board_image", board_image)
        cv2.waitKey(100)
    return (ratio1, ratio2, filter_pos(positions)) # return the ratios with highest threshold and the position of the templates

def filter_pos(arr): 
    # from a list of position arrays, remove items that are overcounted, my method of looping over two scaling ratios can cause same objects to be overcounted
    # this function is really just a safety measure, this function rarely finds overlapping objects
    temp_list = []
    for p in range(len(arr)-1):
                    for k in range(p+1,len(arr)):
                        if abs(arr[p][0][0]-arr[k][0][0]) < 5 and abs(arr[p][0][1]-arr[k][0][1]) < 5:
                                if k not in temp_list: temp_list.append(k)
    if temp_list != []:
        for s in reversed(sorted(temp_list)): del arr[s] # a bit of soring and organizing
    return arr
        
def search_for_orbs(visualize):
    open_new_board()
    list_priority = [["heart", "red", "blue", "green", "light", "dark"], 
    ["poison_EX", "poison", "jammer"], 
    ["heart_plus", "red_plus", "blue_plus", "green_plus", "light_plus", "dark_plus" ], 
    ["heart_lock", "red_lock", "blue_lock", "green_lock", "light_lock", "dark_lock"],
    ["heart_plus_lock", "red_plus_lock", "blue_plus_lock", "green_plus_lock", "light_plus_lock", "dark_plus_lock"]]
    
    orb_pos_list, temp_list = [], []
    current_ratio1, current_ratio2 = None, None
    for orb_filename in list_priority[0]:
        ratio_position = locate_on_screen(visualize, orb_filename+".png", current_ratio1, current_ratio2, "Orb")
        if current_ratio1 == None and ratio_position[0] != None:
            current_ratio1, current_ratio2 = ratio_position[0], ratio_position[1]
        if ratio_position[0] != None:
            for object_location in ratio_position[2]: 
                temp_list.append([orb_filename, object_location[0], object_location[1]])
    list_len, arr = len(temp_list), []
    print("code found", len(temp_list), "orbs on screen")
    if list_len in [20, 30, 42]:
        height, width = math.floor(list_len**.5) , math.ceil(list_len**.5)
    else:print("cannot find all orbs or is mistaking something on the screen") 
    temp_list.sort(key = lambda entry: entry[1][1])
    for i in range(height):
        temp_a = [temp_list[k] for k in range(i*width, width*(i+1))]
        temp_a.sort(key = lambda entry: entry[1][0])
        arr.append(temp_a)
    return arr

def open_new_board(): 
    global board_image, board_image_gray
    board_image = cv2.imread(filepath+filename)
    board_image_gray = cv2.cvtColor(board_image, cv2.COLOR_BGR2GRAY)

def normalize_pos(temp_list): # get array with pixel position, convert it to a board shape with consecutive integer values to represent x, y; ex (502, 490)  --> (1,0)
    for i in range(height):
        for j in range(width):
            temp_list[i][j] = [orb_position[i][j][0], (j, i)]
    return temp_list

def printboard(board): # specialized function that prints the current state of the board
    for i in board:
        print("[ ", end ="")
        for j, jth_item in enumerate(i):
            print(jth_item[0][:2], end = "")
            if j != width - 1: print(end = ", ")
        print("]")
    print("*"*10)    

def makeboard(height, width):
    "initailize the board as a double array, and each entry is first filled with 1"
    board = []
    for i in range(height):
        a = []
        for j in range(width): a.append(0)
        board.append(a)
    return board

def getcolor(x,y): #self-explanitory
    return board[y][x][0]

def search_by_distance(x,y, steps): #returns the orbs within a certain radius
    if steps == 0: return [board[y][x]]
    temp_arr = []
    for i in range(steps):#find orbs greater than or equal to its x axis
        if -1 < (y+i) < height:
            temp_arr.append([board[y+i][x+(steps-i)]])
            temp_arr.append([board[y+i][x-(steps-i)]])
    for i in range(1,steps):# finds orbs that have x values less than its x value
        if -1 < y-i:
            temp_arr.append([board[y-i][x+(steps-i)]])
            temp_arr.append([board[y-i][x-(steps-i)]])
    return temp_arr

def find_potential_mover(orb_position):# from the list of orbs, we find potential orbs that we will move
    orb_count, potential_mover = {}, [[], [], []]
    for rows in orb_position:
        for orb_info in rows:# this counts how many of the same colored orbs are on the board, creates a dictionary, (color ==> count)
            orb_count[orb_info[0]] = orb_count.get(orb_info[0], 0) + 1
    for key, value in orb_count.items(): # key is color and value is the number of orbs
        temp_val = (value-1)%3
        potential_mover[temp_val].append(key)  
    return [orb_count, potential_mover]

def create_partitions(total, num, remainder, input_list): # recursive function, return all posible way to partition the integer input and all sequeneces are monotonically decreasing
    # total is the number we have left, num is the next value that we will extract from totals, remainder, input list is the sequence we have so far
    if total == num == remainder == 0: return [input_list] #returns the sequence if all parameters reach the ground state
    if (num < 1) or (num == 1 and total > 3) or (num == 2 and total > 5): return []#prevents sequeneces with more than three 1s and more than two 2s  
    if num < remainder:
            if input_list != []: return create_partitions(total-num, num, remainder-num, input_list + [num]) # extract the number from the remaining number and restarts the process
            else: return create_partitions(total-num, num, remainder-num, input_list + [num]) + create_partitions(total, num-1, remainder+1, input_list) #first entry point of recursion
    # called if num >= remainder, meaning the number we want to extract is greater than or equal to the remaninder 
    return create_partitions(total-num, remainder, 0, input_list+[num]) + create_partitions(total, num-1, remainder+1, input_list) #skips by two to be able to have two recursive calls

#not finished       
def simulator(pt_mover):
    numboard = makeboard(height, width)
    for orb in list_of_orb:
        numboard[orb[1]][orb[0]] = 1
    numboard[ini_moving[1], ini_moving[0]] = 2
    printboard(numboard)
        
def check_invariance():
    pass

def search_board(orb_color): #returns the position of orbs of a certain color
    x = []
    for i in range(height):
        for j in range(width):
            if board[i][j][0] == orb_color: x.append(board[i][j][1])
    return x

def draw_vector(color, starting_coor, end_coor):# draws a red vector that show the horizontal and vertical components of the path from the starting to the end coordinate
    vect_thick = 15
    start_x, start_y, end_x, end_y = starting_coor[0], starting_coor[1], end_coor[0], end_coor[1]
    vect_x, vect_y = start_x-end_x , start_y - end_y
    if vect_x != 0 and vect_y != 0: #if there are both vertical and horizontal components
        pygame.draw.rect(boardscreen, pygame.Color(color), [(start_x+0.4)*orb_dis_size, (start_y+0.4)*orb_dis_size, -vect_x*orb_dis_size, vect_thick])
    elif vect_x != 0: # if there is only the horizontal component
        pygame.draw.rect(boardscreen, pygame.Color(color), [(start_x+0.4)*orb_dis_size, (start_y+0.4)*orb_dis_size, -vect_x*orb_dis_size, vect_thick])
    elif vect_y != 0: # if there is only the vertical component
        pygame.draw.rect(boardscreen, pygame.Color(color), [(start_x+0.4)*orb_dis_size, (start_y+0.4)*orb_dis_size, vect_thick, (vect_y)*orb_dis_size])

def draw_boundary(color, top_left, bottom_right):
    pass

def find_combined_path(S_list, D_list):
    for destination in D_list:
        pass

def switch_orb(coor_a, coor_b):
    printboard(board)
    c1, c2 = getcolor(coor_a[0], coor_a[1]), getcolor(coor_b[0], coor_b[1])
    board[coor_a[1]][coor_a[0]][0] = c2
    board[coor_b[1]][coor_b[0]][0] = c1
    printboard(board)
    
def find_aggregate_shortest_path(orb_color, final_pos):
    """first find the shortest distance from one point to another, the output is two arrays, the current position and final position.
    the same index of the two list represents the initial position and final position of the SAME orb."""
    final_pos = [(0,0), (1,0), (2,0)]
    current_position = search_board(orb_color)
    global_best = 100
    for perm_array in list(permutations([arr_index for arr_index in range(len(final_pos))])):#iterate over all permutation of final_position
        local_best, local_path = 0, [None]*len(final_pos)
        for endpoint_index in perm_array:# for each end point, find the closest position
            short_dis = 100
            for startPoint in list(set(current_position)-(set(local_path + finished_on_board))):# from the set of position closest to the end position
                if (abs(final_pos[endpoint_index][0]-startPoint[0])+abs(final_pos[endpoint_index][1]-startPoint[1])) < short_dis:
                    short_dis,short_path = abs(final_pos[endpoint_index][0]-startPoint[0])+abs(final_pos[endpoint_index][1]-startPoint[1]), startPoint
            local_best += short_dis
            local_path[endpoint_index] = short_path
        if local_best < global_best:
            global_best, global_path = local_best, local_path
    print("fill position:", final_pos, "using", orb_color, "from the following position:",global_path)    
    return [global_path, final_pos]
        
def main_loop():
    pass

def virtual_game_loop(): #main pygame loop that oversees the searching and solving process 
    pass
def create_board(board_size):
    pass

if __name__=="__main__":
    heartname, filename = "heart.png", "TestFile/puzzleanddragonboard.png"
    scriptpath, filepath = os.path.realpath(__file__), "" # Get the file path to the screenshot image to analize 
    for i in range(1,len(scriptpath)+1):
        if scriptpath[-i] == "\\":
            scriptpath = scriptpath[0:-i]
            break
    if os.getcwd() != scriptpath: filepath = scriptpath + "\\" #current path, relative to root direcotory or C drive
    main()