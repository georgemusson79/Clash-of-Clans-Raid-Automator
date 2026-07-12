import ctypes
from email import utils
from enum import Enum
import random


import pygetwindow
from dataclasses import dataclass
import tkinter as tk
from rapidocr_onnxruntime import RapidOCR
import numpy as np
from screeninfo import get_monitors
from PIL import ImageGrab, Image, ImageTk
import pyautogui
import time


from utils import CardInfo, fetchCardBoundingBoxes, moveMouseToCanvasPos, readText, findAndCClickreturnButton
from utils import Box
from utils import RGB

class Position(Enum):
    TOP_LEFT=1
    TOP_RIGHT=2
    BOTTOM_LEFT=3
    BOTTOM_RIGHT=4




window=None
engine=RapidOCR()
measuredHeight=776
measuredWidth=1306

mainMonitor=get_monitors()[0]
monitorWidth=mainMonitor.width
monitorHeight=mainMonitor.height



cardMeasuredY=666
cardMeasuredWidth=75
cardMeasuredHeight=100
minorGap=6 #px between card of same type
majorGap=20 #px between card of different type eg troop hero spell siege machine
#firstCardDims=CardInfo(cardMeasuredX,cardMeasuredY,cardMeasuredWidth,cardMeasuredHeight,minorGap,majorGap, troopsCount=2, heroesCount=3, spellsCount=2)
try:
    cocWindow="Clash of Clans - ShoutingBiology87"
    window=pygetwindow.getWindowsWithTitle(cocWindow)[0]
except:
    print("unable to locate coc window")
additionalMarginY=0 #44
additionalMarginX=0 #17
autoDims: Box=window.box
dims=Box(autoDims.left,autoDims.top,autoDims.width-additionalMarginX,autoDims.height-additionalMarginY)






root=tk.Tk()
root.overrideredirect(True)



troopCount = 2
heroCount = 3
spellCount = 2






root.geometry("{width}x{height}+{left}+{top}".format(width=dims.width, height=dims.height, left=dims.left, top=dims.top))
root.attributes("-alpha",0)
canvas = tk.Canvas(
    root, 
    width=dims.width, 
    height=dims.height, 
    bd=0, 
    highlightthickness=0
)
canvas.pack()
img_open=Image.open("placement_mask.png")
img_open=img_open.resize((dims.width,dims.height),Image.Resampling.NEAREST)
img_arr=np.array(img_open)

y,x=np.where(img_arr==1)
mid_y = img_arr.shape[0] // 2
mid_x = img_arr.shape[1] // 2

tl_mask = (y < mid_y) & (x < mid_x)
tr_mask = (y < mid_y) & (x >= mid_x)
bl_mask = (y >= mid_y) & (x < mid_x)
br_mask = (y >= mid_y) & (x >= mid_x)

x_tl, y_tl = x[tl_mask], y[tl_mask]
x_tr, y_tr = x[tr_mask], y[tr_mask]
x_bl, y_bl = x[bl_mask], y[bl_mask]
x_br, y_br = x[br_mask], y[br_mask]

tl=list(zip(x_tl, y_tl))
tr=list(zip(x_tr, y_tr))
bl=list(zip(x_bl, y_bl))
br=list(zip(x_br, y_br))

placements={
    Position.TOP_LEFT: tl,
    Position.TOP_RIGHT: tr,
    Position.BOTTOM_LEFT: bl,
    Position.BOTTOM_RIGHT: br
}



# for x_val, y_val in tl:
#     canvas.create_rectangle(x_val, y_val, x_val + 1, y_val + 1, outline="blue", width=1, fill="blue")

print("done")

def moveMouseToRandomPlacement(placement: Box):
    x=random.randint(int(placement.left),int(placement.left+placement.width))
    y=random.randint(int(placement.top),int(placement.top+placement.height))
    moveMouseToCanvasPos(x,y,dims)



def play_match():
    cards=fetchCardBoundingBoxes(window)
    rand_placement_direction=random.choice([tl,tr,bl,br])
    if (len(cards)==0):
         print("no cards found")
    for card in cards:
        card.hoverAndClick(dims)
        if card.isHero:
            x,y=random.choice(rand_placement_direction)
            moveMouseToCanvasPos(x,y,dims)
            pyautogui.click()
            time.sleep(0.4)
            continue
        #TODO: if is spell place anywhere on the map
        failsafe_counter=0
        while not card.getIsEmpty(dims) and failsafe_counter<30:
            if card.isSpell:
                x,y=random.choice(rand_placement_direction)
                moveMouseToCanvasPos(x,y,dims)
                pyautogui.click()
                time.sleep(0.2)
                failsafe_counter += 1
                continue
            x,y=random.choice(rand_placement_direction)
            moveMouseToCanvasPos(x,y,dims)
            pyautogui.click()
            time.sleep(0.2)
            failsafe_counter += 1
        

    returned=False
    while not returned:
        returned=findAndCClickreturnButton(dims)
        time.sleep(2)
     

def find_match(dims: Box):

    attack_button_x=dims.width*0.02
    attack_button_y=dims.height*0.83
    attack_button_width=dims.width*0.07
    attack_button_height=attack_button_width
    attack_btn_box=Box(attack_button_x,attack_button_y,attack_button_width,attack_button_height)
    moveMouseToRandomPlacement(attack_btn_box)
    pyautogui.click()
    time.sleep(1)


    find_match_button_y=dims.height*0.67
    find_match_button_x=dims.width*0.06
    find_match_button_width=dims.width*0.15
    find_match_button_height=dims.height*0.05
    find_match_btn_box=Box(find_match_button_x,find_match_button_y,find_match_button_width,find_match_button_height)
    moveMouseToRandomPlacement(find_match_btn_box)
    pyautogui.click()
    time.sleep(1)

    attack_button2_x=dims.width*0.76
    attack_button2_y=dims.height*0.82
    attack_button2_width=dims.width*0.15
    attack_button2_height=dims.height*0.05
    moveMouseToRandomPlacement(Box(attack_button2_x,attack_button2_y,attack_button2_width,attack_button2_height))
    pyautogui.click()
    time.sleep(4)
    play_match()
    root.after(5000, find_match, dims)
    



    
    
    
root.after(2000, find_match, dims)
#root.after(2000, play_match)







root.mainloop()


    