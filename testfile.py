def search_board(board, orb_color): #returns the position of orbs of a certain color
    x = []
    for row in board:
        for orbs in row:
            if orbs[0] == orb_color: x.append(orbs[1])
    return x

def search_board1(board, orb_color):
    x = [orbs[1] for row in board for orbs in row if orbs[0] == orb_color]
    return x

board = [[ "green", "dark",  "light", "dark",  "light", "dark" ],
         [ "light", "heart", "red",   "green", "green", "light"],
         [ "light", "heart", "light", "heart", "green", "heart"],
         [ "dark",  "light", "red",   "heart", "light", "red"  ],
         [ "red",   "dark",  "light", "red",   "dark",  "blue" ]]

b = [[['green', (0, 0)], ['dark',  (1, 0)], ['light', (2, 0)], ['dark',  (3, 0)], ['light', (4, 0)], ['dark',  (5, 0)]], 
     [['light', (0, 1)], ['heart', (1, 1)], ['red',   (2, 1)], ['green', (3, 1)], ['green', (4, 1)], ['light', (5, 1)]],
     [['light', (0, 2)], ['heart', (1, 2)], ['light', (2, 2)], ['heart', (3, 2)], ['green', (4, 2)], ['heart', (5, 2)]],
     [['dark',  (0, 3)], ['light', (1, 3)], ['red',   (2, 3)], ['heart', (3, 3)], ['light', (4, 3)], ['red',   (5, 3)]],
     [['red',   (0, 4)], ['dark',  (1, 4)], ['light', (2, 4)], ['red',   (3, 4)], ['dark',  (4, 4)], ['blue',  (5, 4)]]]

y = search_board(b, "red")

x = search_board1(b, "red")
print(y)
print(x)