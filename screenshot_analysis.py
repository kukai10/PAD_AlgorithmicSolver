import cv2
import os
import imutils

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

def open_new_board(filepath, filename):
    board_image = cv2.imread(filepath+filename)
    board_image_gray = cv2.cvtColor(board_image, cv2.COLOR_BGR2GRAY)
    return board_image_gray
    
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

def locate_on_screen(board_image, board_image_gray, visualize, name_of_template, prov_ratio1 = None, prov_ratio2 = None, icon = None): # finds template image in the screen shot 
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
    30 --> 6 * 5
    
    32
    16
    8
    4
    2
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
    



if __name__ == "__main__":
    temp_main()