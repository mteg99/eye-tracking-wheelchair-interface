import pyautogui
from frontend.button import Button
from frontend.window import Window
from frontend.user_interface import UserInterface

window = Window('User Interface Test')
screen_width, screen_height = pyautogui.size()
forward = Button(x=screen_width/2, y=screen_height/5, radius=screen_width/10, color=(0, 255, 0), command='f')
left = Button(x=screen_width/8, y=screen_height*(2/3), radius=screen_width/10, color=(0, 0, 255), command='l')
right = Button(x=screen_width*(7/8), y=screen_height*(2/3), radius=screen_width/10, color=(0, 0, 255), command='r')
ui = UserInterface([forward, left, right], debug_mode=True)

while True:
    frame = ui.render(window.blank_frame())
    window.display(frame)
    x, y = pyautogui.position()
    ui.update_cursor(x, y)
