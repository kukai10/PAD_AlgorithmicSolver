import sys
import time
import math
import pyautogui as auto
from itertools import product

import os
# Get the file path to the screenshot image to analize
scriptpath, filepath = os.path.realpath(__file__), "" 
for i in range(1,len(scriptpath)+1):
    if scriptpath[-i] == "\\":
        scriptpath = scriptpath[0:-i]
        break
if os.getcwd() != scriptpath: filepath = scriptpath + "\\"
################################### board array functions ################################
def printboard(b):
        "prints the current board as a double array and numbers 1~6 represents orbs, * for jammer, # for poison"
        num = True if b[0][0] == 0 else False
        for i in b:
                print("[", end ="")
                for index, item in enumerate(i): 
                        if num: print("{0:2}".format(str(item)), end="")
                        else: print(item[0][:2], end = "")
                        if index != board_width-1: print(", ", end = "")
                print("]")        
        print("*"*10)

def makeboard(board):
        "initailize the board as a double array, and each entry is first filled with 1"
        for i in range(board_height): 
                board.append([])
                for j in range(board_width): board[i].append(i*board_width+j)

def changerow(row, arr):
        "converts the board by each row"
        for i, item in enumerate(arr): row[i] = item

def change_board(x,y, nx, ny):
        "switch the position of the orbs when moved"
        global board
        board[ny][nx], board[y][x] = board[y][x], board[ny][nx]
###################################### move functions #####################################
sleep_time = 0.001
move_pixel, move_time = 80, 0.05#0.2
#move_pixel, move_time = 90, 0.005
def moveup():
    auto.moveRel(0,-move_pixel,move_time)
    time.sleep(sleep_time)

def movedown():
    auto.moveRel(0,move_pixel,move_time)
    time.sleep(sleep_time)

def moveright():
    auto.moveRel(move_pixel,0,move_time)
    time.sleep(sleep_time)

def moveleft():
    auto.moveRel(-move_pixel,0,move_time)
    time.sleep(sleep_time)

#################################### screenshot functions #################################
def search_orb(orb_string, extra_arg):
        "search for the HP bar's heart to narrow down the position to check"
        arr = []
        for pngname in orb_string:
                try:    
                        for pos in auto.locateAll(filepath+"orbs\{0}{1}.png".format(pngname, extra_arg), filepath+filename,limit=10000, region=(heartloc[0], heartloc[1],screen_x-heartloc[0], screen_y-heartloc[1]), step=1, confidence = 0.96):
                                        arr.append([pngname, pos])
                except: print("orb not found")
        return arr

def check_duplicate_orb(arr):
        "check the array called arr which holds the position of the orbs, and see if same orb was counted twice due to some mistake in the searching phase,it deletes orbs that are placed within the same area with 5 pixel degree of freedom"
        temp_list2 = []
        for p in range(len(arr)-1):
                        for k in range(p+1,len(arr)):
                                if (arr[p][1][0] < arr[k][1][0]+5 and arr[p][1][0] > arr[k][1][0]-5) and (arr[p][1][1] < arr[k][1][1]+5 and arr[p][1][1] > arr[k][1][1]-5):
                                        temp_list2.append(k)
        if temp_list2 != []:
                for s in reversed(temp_list2): del arr[s]
        return arr

########## moving orb and transformation of virtual board functions ########################
def initialize_partition_count_dic(board):
        "find how many orbs of the same color are on the board, then it will partition them in groups of 3, 4 and remainder"
        orb_dic, orb_dic_count, orb_dic_par, counter, max_combo = {}, {}, {}, 0, 0
        for row in board: 
                for orbs in row:
                        orb_dic_count[orbs[0]] = orb_dic_count.get(orbs[0], 0) + 1  #{"red": 3, "blue": 4, etc} has the count
                        orb_dic[counter] = orb(orbs[0], orbs[1][0], orbs[1][1]) #{0:orb(), 1: orb(), etc} has the object
                        counter += 1
        for i, orbnum in orb_dic_count.items():
                if orbnum >= board_height*board_width - 3: pass # majority is one color
                elif orbnum < 3: orb_dic_par[i] = [orbnum]
                else: 
                        string = "" if orbnum%3 == 0 else str(orbnum%3)
                        orb_dic_par[i] = list(map(int, [char for char in "3"*(orbnum//3)+string] ))
        color_list = ["none"]
        if "heart_column" in priorities: color_list = ["heal"]
        for color, count in orb_dic_count.items():
                if color == color_list[0]: 
                        count-= 5
                        max_combo+=1     
                max_combo+=count//3
        print(orb_dic_count, max_combo)
        return [orb_dic, orb_dic_count, orb_dic_par, max_combo]

def reset_orb(board, orb_dic):
        "when the board is moved and erased, the newboard over-writes the orb dictionary"
        counter= 0
        for row in board: 
                for orbs in row:
                        orb_dic[counter]._initialize(orbs[0], orbs[1][0], orbs[1][1])
                        counter += 1
        return orb_dic

def find_moving_orb():
        "from the orbs tries to find a potential candidate for the orb to hold on to, mainly prefers the one orb that doesn't have a match"
        potential_orb = [None, None, None]
        for i, j in orb_dic_par.items():
                for h in j:
                        if h == 1: potential_orb[0] = i
                        elif h == 2 and potential_orb[h-1] == None: potential_orb[h-1] = i
                        elif h == 3 and i not in color_priorities and potential_orb[h-1] == None: potential_orb[h-1] = i
        return next(i for i in potential_orb if i != None)

def move_target_orb(pos_arr, current_pos_arr, shape):
        "Given the position of the the orbs to be moved and the position to place them, the orbs will be moved until they're in the right position"
        global movement
        #movement+="*"
        if len(pos_arr) == 2:
                orb1, orb2 = [find_id_from_num(i[0]) for i in [j for j in current_pos_arr]]
                finished, orb_arr = True, [orb1, orb2]
                if shape == "V":
                        px, py = get_xy(pos_arr[0])
                        mirror = 1 if px == 0 or (pos_arr[0]-1 in finished_position and px != 0) else -1
                for u in range(2):
                        if set([find_num_from_id(i) for i in orb_arr]) == set(pos_arr): break
                        if shape == "V" and u == 1: 
                                move_orb_to_pos(find_num_from_id(orb_arr[u]),pos_arr[0]+mirror,orb_arr, pos_arr, "V")
                                if moving-1 == find_num_from_id(orb_arr[u]): move(mirror, 0)
                                [px, py], [mx, my ] = get_xy(pos_arr[1]), get_xy(moving)
                                move_multiple([0,py-my], [px-mx, 0], [0, -1], [mirror,0])
                        else: move_orb_to_pos(find_num_from_id(orb_arr[u]), pos_arr[u], orb_arr, pos_arr,shape)
                        finished_position.append(pos_arr[u])
                        #movement+="*"               
        elif len(pos_arr) == 3:
                #print(current_pos_arr)
                orb1, orb2, orb3 = [find_id_from_num(i[0]) for i in [j for j in current_pos_arr]]
                finished, orb_arr = True, [orb1, orb2, orb3]
                sent_to_check(orb_arr, pos_arr,shape)
                if shape == "V" and pos_arr[0]%board_width >= board_height-1-3 :
                        #print("flipped")
                        orb_arr, pos_arr = [orb3, orb2, orb1], [i for i in reversed(pos_arr)]
                for u in range(3):
                        if set([find_num_from_id(i) for i in orb_arr]) == set(pos_arr): break
                        move_orb_to_pos(find_num_from_id(orb_arr[u]), pos_arr[u], orb_arr, pos_arr,shape)
                        #movement+="*"
                        finished_position.append(pos_arr[u])
                        sent_to_check(orb_arr, pos_arr, shape) 
        for i in pos_arr:
                if i not in finished_position: finished_position.append(i)
        if set(pos_arr) != set([find_num_from_id(i) for i in orb_arr]): print("need checks in place")

def sent_to_check(orb_arr, pos_arr, shape):
        "if two out of three orbs are in their position, the third orb might have trouble getting in place if it can't move the previously organized orbs"
        global movement
        new_orb = [find_num_from_id(i) for i in orb_arr]
        a, b = set(new_orb), set(pos_arr)
        finished_orb = a&b
        if len(finished_orb) == 2:
                #movement+="["
                #print("check", movement)
                t_orb, leftover_pos = a-b, b-a
                val, f_val1, f_val2, pos3 = t_orb.pop(), finished_orb.pop(), finished_orb.pop(), leftover_pos.pop()
                val_id = find_id_from_num(val)
                [vx, vy], [tx, ty], [mx, my]  = get_xy(val), get_xy(pos3), get_xy(moving)
                if set([find_num_from_id(i) for i in orb_arr]) == set(pos_arr): return
                if shape == "H":
                        if abs(f_val1- f_val2) != 1:
                                #print("yolo")
                                if f_val1+1 == val or f_val2+1 == val:
                                        
                                        num = 1 if vx < tx else -1
                                        num1 = 0
                                        if moving+num == val: num1 = 1
                                        move_multiple([0, num1], [tx-mx, 0], [0,(ty-my)-num1], [-num,0], [0,1])
                                elif pos3-board_width==val: 
                                        num = 1 if ty-my < 0 else -1
                                        if ty-my == 0: num = 0
                                        move_multiple([0,(ty-my)+num], [tx-mx,0], [0,1])
                                        sent_to_check(orb_arr, pos_arr, shape)
                                elif ((vx < mx and vx < tx) or (vx > mx and vx > tx)) and vy<ty and f_val1-board_width != val and f_val2-board_width != val:
                                      
                                        num = 1 if vx > mx else -1
                                        if my == ty: up()
                                        move_orb_to_pos(val, pos3+num-board_width, orb_arr, pos_arr, shape)
                                       
                                        sent_to_check(orb_arr, pos_arr, shape)
                                else:
                                        
                                        if f_val1 > f_val2: f_val2, f_val1 = f_val1, f_val2
                                        num = 1 if tx < vx else -1
                                        num1 = 1 if ty == my else 0 
                                        move_multiple([0,-num1],[tx-mx, 0], [0, ty-my+num1], [num,0])
                                        sent_to_check(orb_arr, pos_arr, shape)
                        else:
                                if moving == pos3 and moving-board_width == val: up()
                                elif tx == 0 and moving == pos3:
                                        up()
                                        if f_val1 > f_val2: f_val2, f_val1 = f_val1, f_val2
                                        move_orb_to_pos(val, f_val1-board_width,orb_arr, pos_arr, shape)
                                        sent_to_check(orb_arr,pos_arr, shape) 
                        if set([find_num_from_id(i) for i in orb_arr]) == set(pos_arr): return
                        if (val == f_val1-board_width or val == f_val2-board_width):
                                num = -1 if moving+1 == val else 0
                                move_multiple([0, num], [tx-mx, 0], [0, (ty-my)-num], [-(tx-vx), 0], [0, -1])
                        elif tx != board_width-1 and tx !=0 and pos3+1 not in finished_position: 
                                move_orb_to_pos(val, pos3, orb_arr, pos_arr, shape)
                        elif tx == 0: 
                                move_orb_to_pos(val, pos3+1-board_width, orb_arr, pos_arr, shape)
                                sent_to_check(orb_arr,pos_arr, shape) 
                        elif tx == board_width-1 and pos3-1 in finished_position:
                                move_multiple([0,vy-my+1],[vx-mx,0])
                                if f_val1 > f_val2: f_val2, f_val1 = f_val1, f_val2
                                move_orb_to_pos(val, f_val2-board_width,orb_arr, pos_arr, shape)
                                sent_to_check(orb_arr,pos_arr, shape) 
                        else:
                                if f_val1 > f_val2: f_val2, f_val1 = f_val1, f_val2
                                if moving == pos3: up()
                                move_orb_to_pos(val, f_val2-board_width,orb_arr, pos_arr, shape)
                                sent_to_check(orb_arr,pos_arr, shape)   
                if shape == "V":
                        mirror = 1 if (tx == 0 or (pos3 - 1 in finished_position and tx > 0)) else -1
                        inverse = -1 if pos3 < f_val1 and pos3 < f_val2 else 1 
                        if abs(f_val1 - f_val2)!= board_width: # if two spots in the designated row are separated
                                if f_val1 + mirror == val or f_val2 + mirror == val:
                                     
                                        if my > vy > ty or my < vy< ty: move_multiple([mirror, 0], [0, ty-my], [-mirror + (tx-mx), 0], [0,ty-vy], [mirror, 0])
                                        else: move_multiple([0, ty-my], [tx-mx, 0], [0, vy-ty], [mirror, 0])
                                elif f_val1//board_width == vy or f_val2//board_width == vy and tx+mirror != vx:
                                        
                                        move_orb_to_pos(val, val+(tx-vx)+mirror, orb_arr, pos_arr, shape)  
                                        sent_to_check(orb_arr, pos_arr, shape)    
                                else:
                                        move_multiple([tx-mx+mirror, 0], [0, ty-my])
                                        if f_val1 > f_val2 and pos3 < (board_height*board_width-1)/2: f_val1, f_val2 = f_val2, f_val1
                                        elif f_val1 < f_val2 and pos3 > (board_height*board_width-1)/2: f_val1, f_val2 = f_val2, f_val1
                                        mirror_a = 1 if pos3 < (board_height*board_width-1)/2 else -1
                                        move_orb_to_pos(f_val2, f_val1+mirror_a*board_width,orb_arr, pos_arr,shape)
                                        sent_to_check(orb_arr, pos_arr,shape)
                        elif abs(val-f_val1) == 1 or abs(val-f_val2) == 1:
                                num = 1 if tx == 0 or f_val1-1 in finished_position else -1
                                if moving+board_width*inverse == val: move(num, 0)
                                if set([find_num_from_id(i) for i in orb_arr]) == set(pos_arr): return
                                move_multiple([0, (ty-my)], [(tx-mx), 0], [0, (vy-ty)], [num, 0])
                        else:
                                #print("efwffefw", movement)
                                #printboard(board)
                                if pos3 + board_width not in finished_position and f_val1 < pos3 and f_val2 < pos3 and ty != board_height-1:
                                        #print("if")
                                        move((vx-mx)+(1 if vx-mx < 0 else -1), 0)
                                        if set([find_num_from_id(i) for i in orb_arr]) == set(pos_arr): return
                                        move_orb_to_pos(val, pos3, orb_arr, pos_arr,shape)
                                elif (pos3 < f_val1 and pos3 < f_val2 and pos3-board_width not in finished_position) or (pos3 > f_val1 and pos3 > f_val2 and pos3+board_width not in finished_position):
                                        num2 = 1 if pos3 < f_val1 else -1
                                        #print(f_val1, f_val2, val,  pos3+mirror+num2*board_width)
                                        move_orb_to_pos(find_num_from_id(val_id), pos3+mirror+num2*board_width, orb_arr, pos_arr, shape)
                                        mx, my = get_xy(moving)
                                        vx, vy = get_xy(find_num_from_id(val_id))
                                        #printboard(board)
                                        #print("hello")
                                        if mx == vx:
                                               #print("hellow v2")
                                                move_multiple([-mirror,0],[0,ty-my],[tx-mx+mirror,0],[0,num2],[vx-tx,0])
                                                #printboard(board)
                                        else: 
                                               #print("hellow v3")
                                                move_multiple([0,ty-my], [tx-mx,0], [0,num2], [vx-tx,0])
                                                #printboard(board)

                                        #sent_to_check(orb_arr, pos_arr, shape_)
                                        
                                else:
                                        print("else")
                                        if moving + 1 == val and moving == pos3 and mx != board_width-1: right()
                                        elif moving-1 == val and moving == pos3 and mx != 0:left()
                                        else:
                                                if f_val1 < f_val2 and pos3 < f_val2 and pos3 < f_val1: f_val2, f_val1 = f_val1, f_val2
                                                elif f_val1 > f_val2 and f_val1 < pos3 and f_val2 < pos3: f_val2, f_val1 = f_val1, f_val2
                                                if moving == pos3: move(mirror, 0)
                                                move_orb_to_pos(val, f_val2+mirror, orb_arr, pos_arr,shape)
                                                #printboard(board)
                                                sent_to_check(orb_arr, pos_arr, shape)
                #movement+="]"
                               
def move_orb_to_pos(orbnum, target, id_arr, pos_arr, shape):
        if orbnum == target: 
                pass
                #print("already finished", orbnum, target)
        else: 
                if set([find_num_from_id(i) for i in id_arr]) == set(pos_arr): return
                [tx, ty],[mx, my], [ox, oy], orb_id = get_xy(target), get_xy(moving), get_xy(orbnum), find_id_from_num(orbnum)   
                x_direction, y_direction, dx, dy = tx-ox, ty-oy, ox-mx, oy-my
                if moving == target and x_direction == 0 and y_direction == 1:up()
                elif moving == target and x_direction == 0 and y_direction == -1:down()
                elif moving == target and x_direction == 1 and y_direction == 0:left()
                elif moving == target and x_direction == -1 and y_direction == 0:right()
                else:
                        if x_direction == 0:move_orb_to_pos_y(find_num_from_id(orb_id), target, id_arr, pos_arr, shape)
                        elif y_direction == 0:move_orb_to_pos_x(find_num_from_id(orb_id), target, id_arr, pos_arr, shape)
                        else:
                                if orbnum+x_direction in finished_position:
                                        move_orb_to_pos_y(find_num_from_id(orb_id), target, id_arr, pos_arr, shape)
                                        move_orb_to_pos_x(find_num_from_id(orb_id), target, id_arr, pos_arr, shape)
                                elif orbnum+board_width*y_direction in finished_position:
                                        move_orb_to_pos_x(find_num_from_id(orb_id), target, id_arr, pos_arr, shape)
                                        move_orb_to_pos_y(find_num_from_id(orb_id), target, id_arr, pos_arr, shape)
                                else:
                                        for i in range(dx):
                                                if moving+i in finished_position:
                                                        if moving-board_width not in finished_position:up()
                                                        elif moving+board_width not in finished_position: down()
                                                        num = 1 if dx<0 else -1
                                                        move(dx+num, 0)
                                                        break
                                        move_orb_to_pos_x(find_num_from_id(orb_id), target, id_arr, pos_arr, shape) 
                                        if  len(set([find_num_from_id(i) for i in id_arr])&set(pos_arr)) == 2 and shape == "H": 
                                                #print("hfwefe")
                                                sent_to_check(id_arr, pos_arr, shape)
                                        else: move_orb_to_pos_y(find_num_from_id(orb_id), target, id_arr, pos_arr, shape)
                                                 
def move_orb_to_pos_x(orbnum, target, id_arr, pos_arr,shape): 
        global movement
        #movement+=">>"
        #print("x")
        [tx, ty], [ox, oy], [mx, my]= get_xy(target), get_xy(orbnum), get_xy(moving)
        x_direction, dx, dy= tx-ox, ox-mx, oy-my
        if set([find_num_from_id(i) for i in id_arr]) == set(pos_arr): return
        if x_direction != 0:
                if ox != board_width-1: #by default position on the right
                        if ox == mx:
                                num_a = 1 if mx < tx else -1
                                if moving-1 in finished_position and mx != 0:  move_multiple([1, 0], [0, dy])
                                elif (moving+num_a in finished_position):
                                     
                                        num = 1 if dy > 0 else -1
                                        move_multiple([-1, 0], [0, dy+num], [dx+1, 0], [0, -num])
                                else:
                                        if orbnum+1 in finished_position:
                                                move_multiple([-1,0], [0, dy], [1, 0])
                                                x_direction+=1
                                        else: move_multiple([1, 0], [0, dy])
                        elif oy == my and mx < ox and tx < ox: 
                                move(dx-1, 0)
                                x_direction+=1
                        elif oy == my and ox < mx and ox < tx: move(dx,0)
                        elif moving+(oy-my)*board_width in finished_position: move_multiple([dx, 0], [0, dy])
                        else: #ox != mx
                                printboard(board)
                                
                                if x_direction == -1 and shape == "H" and mx < ox:
                                       
                                        move_multiple([0,oy-my], [ox-mx, 0])
                                        x_direction+=1
                                else:
                                        movement+=":"
                                        numdy = 1 if dy < 0 else -1
                                        numdx = 1 if dx < 0 else -1
                                        num_dis = 1 if x_direction > 0 else -1
                                        if dy+numdy == 0:
                                                num1 = 0
                                                if moving+dx in finished_position: 
                                                        print("tjsafa")
                                                        printboard(board)
                                                        move_multiple([0, dy], [dx+numdx,0])
                                                        if orbnum < moving <= target: move_multiple([-1,0])
                                                        elif orbnum > moving >= target: move_multiple([1,0])
                                                else: move_multiple([0, dy+numdy], [dx,0])
                                        else:
                                                move_multiple([0,dy+numdy], [dx,0])
                                        
                                        ndx = -1 if x_direction < 0 else 1
                                        if moving-numdx in finished_position:
                                                printboard(board)
                                                print([0,-numdy], [ndx,0], [0, numdy], [-ndx,0])
                                                if moving-numdx in pos_arr: move_multiple([0,-numdy], [ndx,0], [0, numdy], [-ndx,0])
                                                print("else", remove_extra_movement(movement))
                                                printboard(board)
                                                quit()
                                        else: move_multiple([ndx,0],[0,-numdy])
                                        movement+="*"
                                        printboard(board)
                                        print("fin", x_direction)              
                        if set([find_num_from_id(i) for i in id_arr]) == set(pos_arr): return
                        if x_direction < 0:
                                while True:
                                        right()
                                        x_direction+=1
                                        if x_direction >= 0: break  
                                        horizontal_bracket("left")     
                        elif x_direction > 0:
                                while True:
                                        left()
                                        x_direction-=1
                                        if x_direction <= 0: break
                                        horizontal_bracket("right")
                else:# this is to move to the left
                        if ox == mx: left()
                        if moving+board_width in finished_position: move_multiple([dx-1, 0], [0,dy], [1, 0])
                        else: move_multiple([0,dy], [dx,0])
                        if ox == mx: right()
                        x_direction+=1
                        if set([find_num_from_id(i) for i in id_arr]) == set(pos_arr): return
                        if x_direction != 0:
                                while True:
                                        horizontal_bracket("left")
                                        right()
                                        if set([find_num_from_id(i) for i in id_arr]) == set(pos_arr): return
                                        if x_direction == -1: break
                                        x_direction+=1
        
def move_orb_to_pos_y(orbnum, target, id_arr, pos_arr,shape):
        global movement
        #movement+="^^"
        if set([find_num_from_id(i) for i in id_arr]) == set(pos_arr): return
        [tx, ty], [ox, oy], [mx, my] = get_xy(target), get_xy(orbnum), get_xy(moving) 
        y_direction, dx, dy = ty-oy, ox-mx, oy-my
        #print("y")
        if oy != 0: # if the object is not on top edge, move up or down
                if y_direction > 0:
                        if ox == mx:
                                if dy > 0: move(0, dy-1)
                                elif dy < 0:
                                        move(0, dy)
                                        y_direction-=1
                        elif ox> mx and ((orbnum-1)+ board_width in finished_position and orbnum != 0): 
                                move_multiple([dx-1, 0], [0,dy-1], [1, 0])
                        elif ox<mx and ((orbnum+1)+board_width in finished_position and orbnum != board_width-1): 
                                move_multiple([dx+1, 0], [0, dy-1], [-1, 0])
                        else:
                                num, y_direction = 1, y_direction-1
                                if moving+board_width not in finished_position: 
                                        move_multiple([0,dy+num], [dx,0], [0, -num])
                                        if set([find_num_from_id(i) for i in id_arr]) == set(pos_arr): return
                                else:
                                        num1 = 1 if dx < 0 else -1
                                        move_multiple([dx+num1, 0], [0,dy+1], [-num1, 0], [0, -1]) 
                        if set([find_num_from_id(i) for i in id_arr]) == set(pos_arr): return     
                        if y_direction > 0: # down
                                while True:
                                        vertical_bracket("down")
                                        up()
                                        if set([find_num_from_id(i) for i in id_arr]) == set(pos_arr): return
                                        """
                                        if y_direction == 1 and ((target%board_width == board_width-1 and target-1 in finished_position) or (target%board_width < board_width-1 and target+1 in finished_position)):
                                                move_multiple([-1, 0], [0, 1], [1, 0], [0, 1], [-1, 0], [0, -1])
                                        """
                                        if y_direction==1: break
                                        y_direction-=1
                
                elif y_direction < 0:
                        dx, dy = ox-mx, (oy-my)-1
                        if ox == mx:
                                if my < oy: move(0, dy)
                                else:
                                        num = 1 if ox == 0 or (orbnum-1 in finished_position and ox != 0) else -1
                                        move_multiple([num, 0], [0, dy], [-num, 0])
                        else:       
                                num = 1 if moving+dy*board_width in finished_position else 0
                                mirror = -1 if tx == board_width or (target+1 in finished_position and tx != board_width) else 1
                                move_multiple([num*mirror, 0], [0,dy], [dx-num*mirror,0])
                        if set([find_num_from_id(i) for i in id_arr]) == set(pos_arr): return
                        if y_direction < 0: #up
                                while True:
                                        down()
                                        if set([find_num_from_id(i) for i in id_arr]) == set(pos_arr): return
                                        y_direction+=1
                                        if y_direction >= 0: break
                                        vertical_bracket("up")          
        elif y_direction != 0: #this is to move down
                dx, dy = ox-mx, oy-my+1
                if moving+board_width in finished_position:
                        num = -1 if dx > 0 else (0 if dx == 0 else 1)
                        move_multiple([dx+num, 0], [0, dy], [-num, 0])
                else: move_multiple([0,dy], [dx,0])
                if set([find_num_from_id(i) for i in id_arr]) == set(pos_arr): return
                while True:
                        up()
                        if set([find_num_from_id(i) for i in id_arr]) == set(pos_arr): return
                        y_direction-=1
                        """
                        if y_direction == 1 and shape == "H" and target-1 in finished_position and (target%board_width == board_width-1 or target+1 in finished_position):
                                move_multiple([-1, 0], [0, 1], [1, 0], [0, 1], [-1, 0], [0, -1])
                                print("end loop")
                                break
                        """
                        if y_direction <= 0: break                                
                        vertical_bracket("down")
######################## functions that return informations ###############################

def simulation(original_orb_dic, moving, original_board):
        pass

def get_closest_color(orb_dict, x, y, width, height, wanted_color = [], unwanted_color = []):
        global previous_color, current_color
        dummy_color = ""
        color_dic, blacklist, arr_color, additional_check = {}, [], [[] for i in range(width*height)], 1
        for s in range(min(board_width, board_height)*2):
                counter1 = 0
                for i in range(height):
                        for j in range(width): 
                                dummy_arr = get_array_in_step(j+x,i+y, s)
                                for k in dummy_arr: #k = [25, 8]
                                        orb_color = orb_dict[k[0]].color()
                                        arr_color[counter1].append([k,orb_color])
                                        if k[0] not in blacklist: #check unique position and get the color
                                                blacklist.append(k[0])
                                                color_dic[orb_color] = color_dic.get(orb_color, 0) + 1
                                counter1+=1
                # keeps on checking until one color meets the number required
                # arr_check store position and distance
                best_sum, best_combination = 100, ()
                for color, item in color_dic.items():
                        if item>= width*height and additional_check > 0:
                                additional_check -=1
                                break
                        if item >= width*height and (wanted_color==[] or (wanted_color!=[] and color == wanted_color)) and (unwanted_color==[] or (color not in unwanted_color)):
                                arr_check =  [[] for i in range(width*height)]
                                for index, possible_assignment in enumerate(arr_color):
                                        for info in possible_assignment:
                                                if info[1] == color:  arr_check[index].append(info[0])
                                perm = list(product(*arr_check))
                                for combination in perm:
                                        dummy, path_sum, breaker = [], 0, False
                                        for info in combination:
                                                if info[0] in dummy or path_sum >= best_sum: 
                                                        breaker = True
                                                        break
                                                else:
                                                        dummy.append(info[0])
                                                        path_sum +=info[1]
                                        if path_sum < best_sum and not breaker:
                                                dummy_color = color
                                                best_sum, best_combination = path_sum, combination
                                                if best_sum == s: break
                if best_sum < 100: 
                        if current_color != "": previous_color, current_color, current_color, dummy_color

                        orb_info = best_combination[0][0]
                        print(board[orb_info//board_width][orb_info%board_width][0], "best combination is ", best_combination)
                        return best_combination
   
def get_array_in_step(x,y,step):
        if step == 0:
                return [[x+board_width*y, 0]] if x+board_width*y != moving else [] 
        else:   
                arr, new_y, x_step= [], y-step, 1
                up_val, down_val= x+ board_width*new_y, x+ board_width*(y+step)
                if 0<= new_y < board_height and up_val not in finished_position and up_val != moving: arr.append([up_val, step])
                if 0<= y+step < board_height and down_val not in finished_position and down_val != moving: arr.append([down_val, step])
                for dummy in range(step*2 -1):
                        new_y+=1
                        if 0<= new_y < board_height:
                                new_val, new_val1 = x+x_step + board_width* new_y, x-x_step + board_width* new_y
                                if 0 <= x+ x_step < board_width and new_val not in finished_position and new_val != moving: arr.append([new_val, step])
                                if 0 <= x- x_step < board_width and new_val1 not in finished_position and new_val1 != moving: arr.append([new_val1, step])
                        if new_y < y: x_step+=1
                        else: x_step-=1
                return arr

def remove_extra_movement(move):
        new_move=move
        while True:
                len_a= len(new_move)
                for char in ["lr", "rl", "ud", "du"]:
                        new_move = new_move.replace(char,"")
                if len_a == len(new_move): break
        return new_move

def find_num_from_id(id_num):
        for i, row in enumerate(board):
                for j, column in enumerate(row):
                        if column[2] == id_num: return i*board_width+j

def find_id_from_num(orbnum):
        return board[orbnum//board_width][orbnum%board_width][2]

def get_xy(orbnum):
        return [orbnum%board_width, orbnum//board_width]

def return_xy_range(arr):
        x_list, y_list = [], []
        for a in arr:
                x, y = a%board_width, a//board_width
                if x not in x_list: x_list.append(x)
                if y not in y_list: y_list.append(y)
        return[x_list, y_list]

def get_distance(list_pos):
        rn_sum = 0
        for i in list_pos:
                rn_sum+=i[1]
        return rn_sum
                
def copy_board(board):
        new = [[] for i in board]
        for i, k in enumerate(board):
                new[i] = k[:]
        return new
########################### set of predefined movements #####################################
def vertical_bracket(direction):# left or right, up or down
        [x, y], scale, num1,num = get_xy(moving), -2 if direction == "up" else 2, -2 if direction == "up" else 2 , 1
        if x == board_width-1 or (x<board_width-1 and (moving+1 in finished_position or moving+1+ scale*board_width in finished_position)): num = 1
        elif x == 0 or (x > 0 and (moving-1 in finished_position or moving-1 + scale*board_width in finished_position)): num = -1
        move_multiple([-num, 0], [0, num1], [num, 0])

def horizontal_bracket(direction):# up or down, and left or right direction
        [x, y], num1 = get_xy(moving), -2 if direction == "left" else 2
        num = 1 if (y == 0 or moving-board_width in finished_position or moving+num1-board_width in finished_position) else -1
        move_multiple([0, num], [num1,0], [0, -num]) 

def up():
        global moving, movement
        orb_dic[moving]._swap(orb_dic[moving-board_width], moving, moving-board_width)
        moving -= board_width
        movement += "u"

def down():
        global moving, movement
        orb_dic[moving]._swap(orb_dic[moving+board_width], moving, moving+board_width) 
        moving += board_width
        movement+="d"
        
def left():
        global moving, movement
        orb_dic[moving]._swap(orb_dic[moving-1], moving, moving-1)
        moving -=1
        movement+="l"

def right():
        global moving, movement
        orb_dic[moving]._swap(orb_dic[moving+1], moving, moving+1)
        moving +=1
        movement+="r"

def move_multiple(*moves):
        for i in list(moves):
                move(i[0], i[1])

def move(x, y):
        if x == 0 and y == 0: pass
        elif y != 0:
                for dummy in range(abs(y)):
                        if y < 0: up()
                        if y > 0: down()
        elif x != 0:
                for dummy in range(abs(x)):
                        if x < 0: left()
                        if x > 0: right()
#################################################################################################
class orb():
        def __init__(self, color, x, y):
                self._color, self._x, self._y = color, x, y

        def _save_init(self):
                self._perm_color, self._perm_x, self._perm_y = self._color, self._x, self._y

        def _position(self):
                return [self._x, self._y]

        def _initialize(self):
                self._color, self._x, self._y = self._perm_color, self._perm_x, self._perm_y

        def color(self):
                return self._color

        def _swap(self, other, num1, num2):
                x,y = get_xy(num1)
                nx, ny = get_xy(num2)
                change_board(x,y,nx,ny)
                self._x, self._y,self._color, other._color, other._x, other._y= x,y,other._color, self._color, nx,ny         

############################################ main ###############################################
screen_x, screen_y = auto.size()
filename = "puzzleanddragonboard.png" #"puzzle.png",
#image = auto.screenshot(filename ,region=(600,0,screen_x-1200,screen_y))# left, top, width, height
color_drop, irr_drop = ["red", "blue", "green", "light", "dark", "heal"], [ "poison", "poison_ex", "bomb", "jammer"]
specialshapes, gimic = ["L_shape", "cross","VDP", "2way", "L_heart", "row", "heart_column", "VDP_heart"], ["darkness", "super_darkness"]
leaderspec, enemyspec = ["combo", "drop_connect", "color", "shape", "type"], ["resolve", "damage_absorb", "VD", "color_absorb"]
orbs, priorities,color_priorities, board, original_board, numboard, finished_position, arr = [], [], [], [], [], [], [], []
num_of_battle, timemovable, movement, play, current_color, previous_color = 0, 8, "", False, "", ""
maxmove, board_height, board_width = timemovable*6, 5, 6
try:   # tries to locate the HP bar
        print(filepath, filename)
        heartloc = auto.locate(filepath+"heart.png", filepath+filename, grayscale=True, confidence = 0.9)
        if heartloc != None: play = True
        else: print("heart.png not located on screen")
except: print("board or image not found")
makeboard(numboard)
printboard(numboard)
makeboard(original_board)
#play = False
if play:   # looks for the board  , [color_drop, "_lock"], , [color_drop, "_plus"], [irr_drop, ""]]
        for y in [[color_drop, ""]]:
                arr += check_duplicate_orb(search_orb(y[0], y[1]))
                if len(arr) == board_width*board_height: break
        # each element in arr looks like ['heal', Box(left=277, top=727, width=70, height=68)]
        for index, item in enumerate(arr): item.append(index) #adds an index value to each orb, looks like ['heal', Box(left=277, top=727, width=70, height=68), index value]
        arr.sort(key = lambda entry: entry[1][1])# sorts the orbs by height

        for r in range(board_height): #look at arr and convert array board
                temp_arr = []
                for c in range(6): temp_arr.append(arr[c+(board_width*r)])
                temp_arr.sort(key = lambda entry: entry[1][0])# sort by distance from the left
                if r == 0: temp_x, temp_y = temp_arr[0][1][0], temp_arr[0][1][1]
                if r == board_height-1: temp_x1, temp_y1 = temp_arr[1][1][0], temp_arr[1][1][1]
                for index, item in enumerate(temp_arr): item[1] = [index, r]
                changerow(original_board[r], temp_arr)
        original_orb_dic, orb_dic_count, orb_dic_par, max_combo = initialize_partition_count_dic(original_board)
        moving = next(x for x in range(board_height*board_width) if original_orb_dic[x].color() == find_moving_orb())
        x_coor, y_coor = get_xy(moving)
        movement+= str(moving)
        printboard(original_board)
        board = copy_board(original_board)
        VDcolor, heart_color= "light", "heal"
        priorities = {"VD":VDcolor, "heart_column":heart_color}
        if "VD" in priorities and "heart_column" in priorities and False:
                if orb_dic_count[heart_color] >= board_height:
                        if board_height == 4:
                                move_target_orb([19], get_closest_color(orb_dic, board_width-1,board_height-1,1,1, heart_color), "V")
                                move_target_orb([4,9,14], get_closest_color(orb_dic, board_width-1,0,1,3, heart_color), "V")
                        elif board_height == 5: 
                                sum_a, sum_b, list_e, num_a = get_distance(get_closest_color(orb_dic, 0,0, 1, 5, heart_color)), get_distance(get_closest_color(orb_dic, board_width-1, 0, 1, 5, heart_color)), [], 0
                                list_c, list_d = [[23,29],[5,11,17], [12, 18, 24],[13, 19, 25], [26,27, 28], [20,21, 22], [4, 10, 16], [3,9,15]], [[18,24], [0, 6, 12], [17,23,29], [16,22,28], [25,26,27], [19,20,21], [1,7,13], [2,8,14]] 
                                [list_e, num_a, num_u] = [list_d, [5,4,1,2], [0,1]] if sum_a <= sum_b else [list_c, [0, 1,4,3], [2,5]] 
                                move_target_orb(list_e[0], get_closest_color(orb_dic, num_u[0],board_height-2,1,2, heart_color), "V")
                                move_target_orb(list_e[1], get_closest_color(orb_dic, num_u[0],0,1,3, heart_color), "V")
                                if max_combo >= 2:
                                        for i in range(min(max_combo-2, 2)): move_target_orb(list_e[i+2], get_closest_color(orb_dic,num_a[i],2,1,3), "V")
                                if max_combo >= 4:
                                        for i in range(min(max_combo-4, 2)): move_target_orb(list_e[i+4], get_closest_color(orb_dic,num_u[1],board_height-(i+1),3,1), "H")
                                if max_combo >= 6:
                                        for i in range(min(max_combo-6, 2)): move_target_orb(list_e[i+6], get_closest_color(orb_dic,num_a[i+2],0,1,3), "V")
                        elif board_height == 6:
                                move_target_orb([27,34,41], get_closest_color(orb_dic, board_width-1,board_height-3,1,3, heart_color), "V")
                                move_target_orb([6,13,20], get_closest_color(orb_dic, board_width-1,0,1,3, heart_color), "V")
                else: print("not enough heal orbs for heart column")
        elif "VD" in priorities and False:
                if orb_dic_count[VDcolor] >= 9: pass
                else: print("not enough orbs for VDP")
        else:
                a, b, c, d = [27,28,29], [24,25,26], [21,22,23], [18,19,20]
                best_movement, initial_pos = "", moving
                orb_dic = dict(original_orb_dic)
                for i in orb_dic:
                        orb_dic[i]._save_init()
                for k, j in enumerate([[b,d,a,c], [a,c,b,d], [a,b,c,d], [a,b,d,c], [b,a,c,d], [b,a,d,c]]):
                        print("restart >>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                        board = copy_board(original_board)
                        for i in orb_dic:
                                orb_dic[i]._initialize()
                        movement, moving, finished_position ="", initial_pos, []
                        if k <= 5:
                                for i in range(min(max_combo, 4)): 
                                        move_target_orb(j[i], get_closest_color(orb_dic,j[i][0]%board_width ,j[i][0]//board_width,3,1), "H")
                                range_a, range_b, step = 0, min(max_combo-4,5), 1
                                if moving%board_width > board_width/2 -1: range_a, range_b, step = range_b+1, range_a, -step
                                print(range_a, range_b)
                                for i in range(range_a, range_b, step): 
                                        if i == range_b-step: break
                                        if i == range_b-2*step:
                                                startpos = 0 if range_a != 0 else board_width-1
                                                if get_distance(get_closest_color(orb_dic,startpos , 0,1,3)) < get_distance(get_closest_color(orb_dic,i,0,1,3)):
                                                        move_target_orb([startpos, startpos+board_width, startpos+2*board_width], get_closest_color(orb_dic,startpos,0,1,3), "V")
                                                else: move_target_orb([0+i,6+i,12+i], get_closest_color(orb_dic, i, 0, 1,3), "V")
                                        else: move_target_orb([0+i,6+i,12+i], get_closest_color(orb_dic, i, 0, 1,3), "V")
                        else:
                                for i in range(min(max_combo, 2)):
                                        move_target_orb
                        printboard(board)
                        movement = remove_extra_movement(movement)
                        print(movement, len(movement))
                        #break
                if best_movement == "": best_movement = movement
                elif movement < best_movement: best_movement = movement
                

        #printboard(board)
        #movement = remove_extra_movement(best_movement)
        #print(best_movement, len(best_movement), max_combo)

        #printboard(original_board)
        xxx = x_coor*85 + temp_x +35 + 600
        yyy = y_coor*85 + temp_y +35
        print(xxx, yyy)

        #time.sleep(2)

        #auto.mouseDown(xxx, yyy,button="left")

auto.mouseDown(x=None, y=None, button="left")
#movement = remove_extra_movement(movement)
for i in range(len(movement)):
        #if i == 1:break
        letter = movement[i]
        if letter == "u": moveup()
        elif letter == "d": movedown()
        elif letter == "l": moveleft()
        elif letter == "r": moveright()
        #if i == 50: break
auto.mouseUp(x=None,y=None, button="left")