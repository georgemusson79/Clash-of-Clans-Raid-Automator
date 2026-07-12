from git import List
import pygetwindow
from dataclasses import dataclass
import tkinter as tk
from rapidocr_onnxruntime import RapidOCR
import numpy as np
from screeninfo import get_monitors
from PIL import ImageGrab
import pyautogui
import cv2



engine=RapidOCR()
measuredHeight=776
measuredWidth=1306

mainMonitor=get_monitors()[0]
monitorWidth=mainMonitor.width
monitorHeight=mainMonitor.height


cardMeasuredY=666
cardMeasuredX=195
cardMeasuredWidth=75
cardMeasuredHeight=95








@dataclass
class CardInfo:
        x: int
        y: int
        width: int
        height: int
        minorGap: int
        majorGap: int
        troopsCount: int
        heroesCount: int
        spellsCount: int

class ClashCard:
    def __init__(self, x, y, width, height, isHero, isSpell):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.isHero=isHero
        self.isSpell=isSpell
    def getAmount(self,dims):
        texts=readText(self.x,self.y,self.width,self.height/2,dims)
        if texts:
            txt=texts[0].lower()
            if "x" in txt:
                txt=txt.replace("x","").strip()
            if txt!=None and txt.isdigit():
                return int(txt)
            
            return 1
        
    def hoverAndClick(self, dims):
        moveMouseToCanvasPos(self.x+self.width//2, self.y+self.height//2, dims)
        pyautogui.click()

    def getAverageColor(self, dims):
        x,y=convertCanvasPosToScreenPos(self.x,self.y,dims)
        bbox=(x,y,x+self.width,y+self.height)
        img=ImageGrab.grab(bbox=bbox)
        img_arr=np.array(img)
        avg_color_per_row = np.average(img_arr, axis=0)
        avg_color = np.average(avg_color_per_row, axis=0)
        return RGB(int(avg_color[0]), int(avg_color[1]), int(avg_color[2]))
    
    def getIsEmpty(self, dims):
        #if image is grey card is used up
        x,y=convertCanvasPosToScreenPos(self.x,self.y,dims)
        bbox=(x,y,x+self.width,y+self.height)
        img=ImageGrab.grab(bbox=bbox)
        img=np.array(img)

        # Convert image to HSV
        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        # Get the saturation channel
        saturation = hsv[:,:,1]
        # Check if the image is grey (low saturation)
        is_grey = np.mean(saturation) < 13  
        return is_grey
    

@dataclass
class Box:
    left: int
    top: int
    width: int
    height: int

@dataclass
class RGB:
    r: int
    g: int
    b: int

def readText(x,y,w,h,dims):
    x,y=convertCanvasPosToScreenPos(x,y,dims)
    bbox=(x,y,x+w,y+h)

    img=ImageGrab.grab(bbox=bbox)
    img.save("result.png")
    img_arr=np.array(img)
    result, elapse = engine(img_arr)
    texts=[]
    if result:

        for box, text, score in result:
            print(f"Found: {text} (Confidence: {score})")
            texts.append(text)
            
    else:
        print("nothing found")
        return None
    return texts


def getIsImageGreyHSV(image):
    # Convert image to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # Get the saturation channel
    saturation = hsv[:,:,1]
    # Check if the image is grey (low saturation)
    is_grey = np.mean(saturation) < 13  
    return is_grey

def fetchCardBoundingBoxes(window,troopCount=2, heroCount=4, spellCount=2):
    actualFirstCardX = cardMeasuredX * window.width / measuredWidth
    actualFirstCardY = cardMeasuredY * window.height / measuredHeight
    cardWidth = cardMeasuredWidth * window.width / measuredWidth
    cardHeight = cardMeasuredHeight * window.height / measuredHeight
    minorGap=cardWidth/10
    majorGap=minorGap*2

    bbox = (
        window.left + int(actualFirstCardX),
        window.top + int(actualFirstCardY),
        window.left + int(actualFirstCardX) + int(cardWidth),
        window.top + int(actualFirstCardY) + int(cardHeight),
    )

    cards=[]

    x=actualFirstCardX
    for i in range (troopCount):
        card=ClashCard(x, actualFirstCardY, cardWidth, cardHeight,False,False)
        cardimage=ImageGrab.grab(bbox=(window.left + int(card.x), window.top + int(card.y), window.left + int(card.x) + int(card.width), window.top + int(card.y) + int(card.height)))
        cardimage.save(f"card_{i}.png")
        cards.append(card)
        x+=cardWidth+minorGap
    
    x+=majorGap
    for j in range (heroCount):
        card=ClashCard(x, actualFirstCardY, cardWidth, cardHeight,True,False)
        cardimage=ImageGrab.grab(bbox=(window.left + int(card.x), window.top + int(card.y), window.left + int(card.x) + int(card.width), window.top + int(card.y) + int(card.height)))
        cardimage.save(f"card_{i+j+troopCount}.png")
        cards.append(card)
        x+=cardWidth+minorGap

    for k in range (spellCount):
        card=ClashCard(x, actualFirstCardY, cardWidth, cardHeight,False,True)
        cardimage=ImageGrab.grab(bbox=(window.left + int(card.x), window.top + int(card.y), window.left + int(card.x) + int(card.width), window.top + int(card.y) + int(card.height)))
        cardimage.save(f"card_{i+j+k+troopCount}.png")
        cards.append(card)
        x+=cardWidth+minorGap


    return cards




def convertCanvasPosToScreenPos(x, y, dims):
    screen_x = dims.left + x
    screen_y = dims.top + y
    return screen_x, screen_y
    

def getCocWindow():
    try:
        cocWindow="Clash of Clans - ShoutingBiology87"
        window=pygetwindow.getWindowsWithTitle(cocWindow)[0]
    except:
        print("unable to locate coc window")
    additionalMarginY=44
    additionalMarginX=17
    autoDims: Box=window.box
    dims=Box(autoDims.left,autoDims.top,autoDims.width-additionalMarginX,autoDims.height-additionalMarginY)
    return window, dims

def moveMouseToCanvasPos(x,y,dims):
    screen_x, screen_y = convertCanvasPosToScreenPos(x, y, dims)
    pyautogui.moveTo(screen_x, screen_y)

def moveAndClickCanvasPos(x,y,dims):
    screen_x, screen_y = convertCanvasPosToScreenPos(x, y, dims)
    pyautogui.click(screen_x, screen_y)



def selectCard(index: int, dims: Box, firstCardDims: CardInfo):
    keyToCardIndex=["1","2","z","q","w","a","s"]
    if index<len(keyToCardIndex):
        pyautogui.press(keyToCardIndex[index])




def screenshotCoc(window):
    autoDims: Box=window.box
    region=(autoDims.left,autoDims.top,autoDims.width,autoDims.height)
    screenshot=pyautogui.screenshot(region=region)
    frame=np.array(screenshot)
    img=cv2.cvtColor(frame,cv2.COLOR_RGB2BGR)
    return img



def findAndCClickreturnButton(dims: Box):
    returnButtonMeasuredY=600
    returnButtonMeasuredHeight=180
    returnButtonMeasuredWidth=85
    returnButtonMeasuredX=(measuredWidth/2)-(returnButtonMeasuredWidth/2)
    actualReturnButtonX = returnButtonMeasuredX * dims.width / measuredWidth
    actualReturnButtonY = returnButtonMeasuredY * dims.height / measuredHeight
    returnButtonWidth = returnButtonMeasuredWidth * dims.width / measuredWidth
    returnButtonHeight = returnButtonMeasuredHeight * dims.height / measuredHeight

    txtList=readText(actualReturnButtonX, actualReturnButtonY, returnButtonWidth, returnButtonHeight, dims)
    if txtList==None:
        return False
    txt=" ".join(txtList).lower()
    if "return" in txt:
        moveMouseToCanvasPos(actualReturnButtonX+returnButtonWidth/2, actualReturnButtonY+returnButtonHeight/2, dims)
        pyautogui.click()
        return True
    

