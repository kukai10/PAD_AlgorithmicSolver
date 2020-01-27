unit_length = 120
screen_aspect_ratio = [[16, 9], [16, 10], [21, 9], [4, 3], [5, 4]]
pad_ratio = [[1,2], [1, 3], [9, 16], [3,4]]
for sc in screen_aspect_ratio:
    for pd in pad_ratio:
        num = int((sc[1]/pd[1])*pd[0]*unit_length)
        print(sc, pd, "x =", num, ", left over = ", sc[0]*unit_length-num, ", half = ", sc[0]*unit_length/2)

print(720/40)
#2 = 9
#1   x