import cv2
import os
import imutils
import math
import time
import numpy as np
import functools


"""
The purpose of this file is to store the functions that will be needed to analyze the screenshot of the board
When the main function in PAD2_main.py access this file's function it will only access the open_new_board function

    main() --> search_for_orbs()   ------------------> filter_pos() ---> return board to main()           
                | <---> locate_on_screen()
"""
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

def get_new_board(filepath, filename):
    board_color = cv2.imread(filepath+filename)
    return board_color, cv2.cvtColor(board_color, cv2.COLOR_BGR2GRAY)

def get_cd():
    """
    uses the os.path function to get the filename and the absolute path to the current directory
    Also does a primative check to see if the path is correct, there has been instances where the CD was different, hence the check.
    """
    scriptpath, filepath = os.path.realpath(__file__), "" # Get the file path to the screenshot image to analize 
    for i in range(1,len(scriptpath)+1):
        if scriptpath[-i] == "\\":
            scriptpath = scriptpath[0:-i]#current path, relative to root direcotory or C drive
            break
    if os.getcwd() != scriptpath: filepath = scriptpath + "\\"
    return scriptpath, filepath

@clock
def search_for_orbs(filepath, filename, visualize):
    """
    function that locates the orbs that is (assumed to be) in the screenshot, and return a list of positions.
    The function will search many variations of the orbs based on the frequency of its appearance, going from high to low frequency.
    If the total number of orbs is consistent with the number of a n x n+1 grid, i.e. 24, 30, 42, then the search is complete.
    if the number of orbs is not 24, 30, or 42, then the function wasn't able to locate an orb or the board is not completely in the screenshot.
    """
    # store an object of the gray and colored version of the screenshot
    board_color, board_gray = get_new_board(filepath, filename)
    # list_priority is a 2d array that stores the name of the file excluding the format (.png)
    # first array has the highest priority, meaning it stores the orbs that are most likely to be on the screensht image
    # then as we go to the 2nd list and 3rd list and so on, the probability of those orbs showing up will decrease 
    list_priority = [["heart", "red", "blue", "green", "light", "dark"], 
    ["poison_EX", "poison", "jammer"], 
    ["heart_plus", "red_plus", "blue_plus", "green_plus", "light_plus", "dark_plus" ], 
    ["heart_lock", "red_lock", "blue_lock", "green_lock", "light_lock", "dark_lock"],
    ["heart_plus_lock", "red_plus_lock", "blue_plus_lock", "green_plus_lock", "light_plus_lock", "dark_plus_lock"]]
    
    # initializing the variables
    orb_pos_list, temp_list = [], []
    current_ratio1, current_ratio2 = None, None
    height, width = 5, 6

    # for each item in list_priority, we use the locate_on_screen function to find the specific object in the picture
    for orb_filename in list_priority[0]:
        ratio_position = locate_on_screen(filepath, orb_filename+".png", board_color, board_gray, visualize, current_ratio1, current_ratio2, "Orb")
        if current_ratio1 == None and ratio_position[0] != None:
            current_ratio1, current_ratio2 = ratio_position[0], ratio_position[1]
        if ratio_position[0] != None:
            for object_location in ratio_position[2]: 
                temp_list.append([orb_filename, object_location[0], object_location[1]])
    list_len, arr = len(temp_list), [[] for i in range(height)]
    print("code found", len(temp_list), "orbs on screen")
    
    if list_len in [20, 30, 42]:
        height, width = math.floor(list_len**.5) , math.ceil(list_len**.5)
    else:print("cannot find all orbs or is mistaking something on the screen") 
    # sort the list by the height of the orbs, then (for a 5x6 board) the orbs stored in index 0-5, 6-11, 12-17, ... will be grouped by their heights
    temp_list.sort(key = lambda entry: entry[1][1])
    # then for each row, we will sort them by their x value so that the orbs are stored in the same position as the screenshot
    for i in range(height):
        temp_a = [temp_list[k] for k in range(i*width, width*(i+1))]
        temp_a.sort(key = lambda entry: entry[1][0])
        arr[i] = temp_a
    return arr

def locate_on_screen(filepath, filename, board_img, board_gray_img, visualize=False, prov_ratio1 = None, prov_ratio2 = None, icon = None): 
    """
    finds small image in the screenshot, the search is using edge detection which gives a similarity probability
    if the similarity is above the threshold probability, then that collection of pixels is very similar to 

    the search consists of using the matchTemplate funcion from openCV2, and two scaling factors to accomodate different screen sizes
    Since the matchTemplate() in CV2 doesn't automatically look for the scaled version of the template, we need to scale the template for the search
    the main idea behind the two ratio values is that there's two value both between [0, 1] that scales the template and the board_image 
    this function will first have "None" as its two ratio values, and on the first iteration, it tries many ratios and stores the best ratio for next time
    
    this will output the provided ratios, which allows the function to speed up in later searches
    """
    #print("looking for ", filename, " given the ratio: ", prov_ratio1, prov_ratio2)
    foldername = "\ImageFile\\" if icon == "Orb" else ""
    max_factor = [5,6] if icon == "Orb" else ( [7, 10] if icon == "screen_elements" else [4, 4])

    # get template image and convert to gray scale
    template_gray = cv2.Canny(cv2.imread(filepath+foldername+filename, cv2.IMREAD_GRAYSCALE),
    
    template_w_org, template_h_org = template_gray.shape[::-1] # initial height and width of original template image 
    found, threshold = None, 0.5 # prameters that affect the searching process
    maxVal = 0 # the current known highest match value 
    # making a list of scaling factors to loop over, if there's a provided ratio, it makes a list that consists of scaling factors close to that value
    scale2 = np.linspace(0.5,1.0, 20)[::-1] if (prov_ratio2 == None) else np.linspace(min((1/prov_ratio2)-0.1, 0.8), min((1/prov_ratio2)+0.1, 1), 3)
    scale1 = np.linspace(0.2, 1.0, 20)[::-1] if (prov_ratio1 == None) else np.linspace(min((1/prov_ratio1)-0.1,0.8), min((1/prov_ratio1)+0.1, 1), 3)
    
    # need two scale because templates can be sometimes too small to beign with, for example looking for an image on a screen larger than 1920x1080 pixels
    for rescaleFactor1 in scale2:
        #resize image but keeps aspect ratio
        resized_template = imutils.resize(template_gray, width = int(template_w_org*rescaleFactor1))
        template_w, template_h = resized_template.shape[::-1] #new height and width
        ratio2 = template_w_org/template_w # ratio between the original width and the new resized width

        for rescaleFactor in scale1:
            # resize screenshot, reason for imutils' resize function instead of cv2's resize is because aspect ratio preservation is built in
            resized_img = imutils.resize(board_gray_img, width = int(board_gray_img.shape[1] * rescaleFactor))
            ratio1 = board_gray_img.shape[1] / float(resized_img.shape[1]) 
            if resized_img.shape[0] < template_h*max_factor[0] or resized_img.shape[1] < template_w*max_factor[1]: 
                break # break if template is bigger than the resized screenshot, meaning there's no way template > screenshot
            edged = cv2.Canny(resized_img,50, 200) # gets the edges of the image
            result = cv2.matchTemplate(edged, resized_template, cv2.TM_CCOEFF_NORMED) # the function that finds the template in the image
            (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result) #we only care about the min val and loc
            if visualize: # if visualize is true show orginal image with borders around the things matching from the templates
                    
                    clone = np.dstack([edged, edged, edged])
                    cv2.rectangle(clone, (maxLoc[0], maxLoc[1]), (maxLoc[0] +template_w, maxLoc[1] + template_h), (0, 0, 255), 2)
                    cv2.imshow("Visualize", clone) #show clone
                    cv2.waitKey(50) # stops for 0.5 seconds
            if found is None or maxVal > found[0]:
                found, location = (maxVal, maxLoc, ratio1, ratio2), np.where(result>=0.4)
                if maxVal > threshold: break 
        if maxVal > threshold: break #exit the search if the currently used ratios provides a reasonably good match
    (_, maxLoc, ratio1, ratio2), positions = found, []
    # end of loop
    for pt in zip(*location[::-1]): # loop through the position of found templates and make a list with required fields
        start_loc, end_loc =(int(pt[0]*ratio1), int(pt[1]*ratio1)), (int((pt[0]*ratio1)+(template_w_org*ratio1/ratio2)), int((pt[1]*ratio1)+(template_h_org*ratio1/ratio2)))
        positions.append([list(start_loc), list(end_loc)])
        cv2.rectangle(board_img, start_loc, end_loc, (0,0,255), 2)
    if positions == []: return (None, None, None) # if nothing was found
    if visualize: # if you want to see the final search
        cv2.imshow("board_image", board_img)
        cv2.waitKey(100)
    return (ratio1, ratio2, filter_pos(positions)) # return the ratios with highest threshold and the position of the templates

def filter_pos(arr): 
    """
    from a list of position arrays, remove items that are overcounted, my method of looping over two scaling ratios can cause same objects to be overcounted
    this function is really just a safety measure, this function rarely finds overlapping objects
    
    instead of looking at n*(n+1)/2 combinations and cheking if theres an overlap 186
    we can first sort the 30 coordinates by their y coordinates and make a set of points that are +-10 pixels of each other, then sort each element in the set by their X value
    if the number of "found" orbs is greater than the number per row, then we know that something was overcounted
    then look for the orb that is within +-10 pixels of each other

    since this sort does O(n*log(n) then it itrates over each y value and checks if the length is correct, if there is an overcounted orb, then it corrects the row
    since searching for overlap takes O(r^2) 
    Worst case senario: n*m* log(n*m) + n*(m*log(m)) , where n, m are the number of rows and columns
    ==> 30*log(30) + 30*log(5) ==> 30*(log 30 * 5)
    best case scenario n*m* log(n*m)
    """
    sorted_list = []
    temp_list = []
    for p in range(len(arr)-1):
                    for k in range(p+1,len(arr)):
                        if abs(arr[p][0][0]-arr[k][0][0]) < 5 and abs(arr[p][0][1]-arr[k][0][1]) < 5:
                                if k not in temp_list: temp_list.append(k)
    if temp_list != []:
        for s in reversed(sorted(temp_list)): del arr[s] # a bit of soring and organizing
    return arr

def temp_main():
    cd, pf = get_cd()
    filename = "/TestFile/puzzleanddragonboard.png"
    visualize = False
    temp = search_for_orbs(cd, filename, visualize)
    # below is what temp looks like, a (n x n+1) 2d array that stores the color and the top_left and bottom right pixel of each orb
    #temp = [
    #       [['light', [60, 572], [154, 666]], ..., ['light', [432, 572], [526, 666]], ['dark', [526, 571], [619, 666]]],
    #       [['green', [59, 663], [152, 758]], ..., ['green', [431, 663], [524, 758]], ['light', [525, 665], [619, 759]]], 
    #       [['light', [60, 758], [154, 852]], ..., ['green', [431, 756], [524, 851]], ['heart', [524, 759], [617, 851]]], 
    #       [['dark', [60, 850], [153, 945]],  ..., ['light', [432, 851], [526, 945]], ['red', [524, 850], [617, 945]]],
    #       [['red', [59, 943], [152, 1038]],  ..., ['dark', [432, 943], [525, 1038]], ['blue', [524, 942], [617, 1037]]]
    #       ]
    top_left_px, bottom_right_px = 



if __name__ == "__main__":
    temp_main()