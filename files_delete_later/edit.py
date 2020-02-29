
def movemouse(letter, pixel_val, (move_time, sleep_time)): # inputs are u, d, l, or r; which moves the mouse by the distance between two orbs 
    # mouse_dic = {"u": [0,-1], "d": [0,1], "l": [-1,0], "r": [1,0]}
    vector = mouse_dic[letter]
    auto.moveRel(pixel_val*vector[0], pixel_val*vector[1] ,move_time)
    time.sleep(sleep_time)

def main():          
    def normalize_pos(temp_list): 
        """
        get array with pixel position, convert it's position value into consecutive integers 
        so that the representation of the position matches the index of the array; ex (color, 502, 490) --> (color, 1,0)
        """
        for i in range(height):
            for j in range(width):
                temp_list[i][j] = [orb_position[i][j][0], (j, i)]
        return temp_list

    heartname, filename = "heart.png", "TestFile/puzzleanddragonboard.png"
    maxMoveStep = 140 #max number of moves teh algorithm will take
    puzzleMoveTime, sleepTime = 8.5, 0.001 #seconds
    movePixel, moveTime= None, puzzleMoveTime/maxMoveStep
    visualize = True # option to visualize the actions occuring between the start to the end
    visualize = False
    move_mouse = False
  
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
    print(norm_orb_position)
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





#not finished       
def simulator(pt_mover):
    numboard = makeboard(height, width)
    for orb in list_of_orb:
        numboard[orb[1]][orb[0]] = 1
    numboard[ini_moving[1], ini_moving[0]] = 2
    printboard(numboard)
        
def check_invariance():
    pass

def search_board(board, orb_color): #returns the position of orbs of a certain color
    x = []
    for row in board:
        for orbs in row:
            if orbs[0] == orb_color: x.append(orbs[1])
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

def switch_orb(coor_a, coor_b): # dont know if this works
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