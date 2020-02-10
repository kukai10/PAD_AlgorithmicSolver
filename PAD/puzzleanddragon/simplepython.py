import pyautogui as auto
auto.FAILSAFE = True
print("this code ran")
#auto.mouseDown(x=None, y=None, button="left")
#auto.mouseUp(x=None,y=None, button="left")
"""
pyautogui.position()
pyautogui.moveTo(100, 200)
pyautogui.click()
print('Press Ctrl-C to quit.')
"""
try:
    while True:
        x, y = auto.position()
        positionStr = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)
        print(positionStr, end='')
        print('\b' * len(positionStr), end='', flush=True)
except KeyboardInterrupt:
    print('\n')

"""
def tamadora():
    pyautogui.moveTo(100, 200)
    pyautogui.click()
"""