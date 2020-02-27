def makeboard(height, width):
        "initailize the board as a double array, and each entry is first filled with 1"
        return [[0, for _ in range(width)] for _ in range(height)]
        """
        board = []
        for i in range(height):
            a = []
            for j in range(width): a.append(0)
            board.append(a)
        return board
        """

def printboard(board): # specialized function that prints the current state of the board
        for row in board:
            pint([row[i][0] for i in range(len(row))])
        print("*"*10)

def search_by_distance(x,y, steps, board): #returns the orbs within a certain radius
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

def getcolor(x,y, board): #self-explanitory
    return board[y][x][0]