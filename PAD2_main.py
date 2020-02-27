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

def find_potential_mover(orb_position):# from the list of orbs, we find potential orbs that we will move
    orb_count, potential_mover = {}, [[], [], []]
    for rows in orb_position:
        for orb_info in rows:# this counts how many of the same colored orbs are on the board, creates a dictionary, (color ==> count)
            orb_count[orb_info[0]] = orb_count.get(orb_info[0], 0) + 1
    for key, value in orb_count.items(): # key is color and value is the number of orbs
        temp_val = (value-1)%3
        potential_mover[temp_val].append(key)  
    return [orb_count, potential_mover]
    
def movemouse():
    auto.moveRel(10, 10,0.2)

def create_partitions(total, num, remainder, input_list): # recursive function, return all posible way to partition the integer input and all sequeneces are monotonically decreasing
    # total is the number we have left, num is the next value that we will extract from totals, remainder, input list is the sequence we have so far
    if total == num == remainder == 0: return [input_list] #returns the sequence if all parameters reach the ground state
    if (num < 1) or (num == 1 and total > 3) or (num == 2 and total > 5): return []#prevents sequeneces with more than three 1s and more than two 2s  
    if num < remainder:
            if input_list != []: return create_partitions(total-num, num, remainder-num, input_list + [num]) # extract the number from the remaining number and restarts the process
            else: return create_partitions(total-num, num, remainder-num, input_list + [num]) + create_partitions(total, num-1, remainder+1, input_list) #first entry point of recursion
    # called if num >= remainder, meaning the number we want to extract is greater than or equal to the remaninder 
    return create_partitions(total-num, remainder, 0, input_list+[num]) + create_partitions(total, num-1, remainder+1, input_list) #skips by two to be able to have two recursive calls

def main():
    pass



if __name__=="__main__":    
    main()
