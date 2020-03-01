from time import sleep
from win32 import win32gui
import pytesseract
import numpy as np
import threading
from pynput.keyboard import Key, Controller, Listener
from PIL import ImageGrab,Image, ImageOps,ImageEnhance,ImageFilter
from directkeys import pressKey,releaseKey,DIK_E,DIK_ARROW_UP,DIK_ARROW_DOWN,DIK_PAGE_UP
import autoit
import re

def on_press(key):
    if key == Key.end:
        global startScript,inputBet,inputColor
        if inputBet != None and inputColor != None:
            startScript = not startScript
            if startScript:
                hwnd = win32gui.FindWindow(None, r'Grand Theft Auto V')
                win32gui.SetForegroundWindow(hwnd)
                win32gui.MoveWindow(hwnd, 0, 0, 1336, 797, True)
            print("\n\nScript status: ", startScript,"\n\n")
def ocr_core(img):
    text = pytesseract.image_to_string(img, lang='eng', config='--psm 10 --oem 3')
    return text

def CalcPos(procent,maxrez):
    return (procent/100)*maxrez

def getFrame():
    hwnd = win32gui.FindWindow(None, r'Grand Theft Auto V')
    win32gui.SetForegroundWindow(hwnd)
    dimensions = win32gui.GetWindowRect(hwnd)
    pressKey(DIK_E)
    pressKey(DIK_PAGE_UP)
    sleep(1)
    image = ImageGrab.grab(dimensions)
    return image
def releaseFrame():
    releaseKey(DIK_PAGE_UP)
    releaseKey(DIK_E)
    finished_betting = False
    frame = None
    time = None
    center_frame = None
    lastcolor = None
def get_current_Money(img):
    left = CalcPos(88,img.size[0])
    top = CalcPos(5.01,img.size[1])
    right = CalcPos(99.8,img.size[0])
    bottom = CalcPos(8.78,img.size[1])
    crop = ImageOps.invert(img).convert('LA').crop(( left, top, right, bottom ))
    crop = ImageEnhance.Brightness(crop).enhance(2.0)
    crop = ImageEnhance.Contrast(crop).enhance(2.0)
    ocr = ocr_core(crop)
    money = int(re.search(r'\d+', ocr[1:]).group())
    return money

def get_time(img):
    try:
        left = CalcPos(93.10,img.size[0])
        top = CalcPos(79.67,img.size[1])
        right = CalcPos(98.10,img.size[0])
        bottom = CalcPos(82.81,img.size[1])
        crop = ImageOps.invert(img.crop( ( left, top, right, bottom ))).convert('LA')
        time = ocr_core(crop).split(':')
        time[0] = int(re.search(r'\d+', time[0]).group())
        time[1] = int(re.search(r'\d+', time[1]).group())
        if time[1] < 10:
            time[1] = 0
        secconds = time[1]+(time[0]*60)
    except:
        secconds = 0
    return secconds

def get_current_Bet(img):
    left = CalcPos(93.00,img.size[0])
    top = CalcPos(87.82,img.size[1])
    right = CalcPos(98.10,img.size[0])
    bottom = CalcPos(90.6,img.size[1])
    crop =  ImageOps.invert(img.crop( ( left, top, right, bottom ))).convert('LA')
    crop = ImageEnhance.Brightness(crop).enhance(2.0)
    crop = ImageEnhance.Contrast(crop).enhance(2.0)
    bet = int(re.search(r'\d+', ocr_core(crop)).group())
    return bet
def get_last_color(img):
    left = int(CalcPos(11.346,img.size[0]))
    top = int(CalcPos(5.9,img.size[1]))
    right = int(CalcPos(11.420,img.size[0]))
    bottom = int(CalcPos(6.1,img.size[1]))
    npimg = np.array(img)[top:bottom,left:right]
    color = ""
    if np.array_equal(npimg[0][0], [155,0,0]):
        color = "red"
    elif np.array_equal(npimg[0][0], [27,27,27]):
        color = "black"
    elif np.array_equal(npimg[0][0], [0,138,138]):
        color = "green"
    return color

startScript = False
inputColor = None
inputBet = None
def mainThread():
    global inputBet,inputColor
    print("\n\n\nWelcome to the gta casino roulette autobet bot. Please put your game in Windowed mode")
    inputBet = int(input("Enter base bet (ex. 1500): "))
    inputColor = input("Enter bet color (ex. red, black, green): ")
    print("\nPress 'END' to toggle the script ON/OFF \n\n\n")
    bet_color = inputColor
    small_bet = inputBet
    betting_target = inputBet
    finished_betting = False
    lastmoney = 0
    lastcolor = ""
    rounds_played = 0
    increased = False
    bet_list= [100,500,1000,5000,10000]
    while True:
        if startScript:
            frame = getFrame()
            time = get_time(frame)
            if time != 0:
                if finished_betting == False:
                    print("Current time: ",time)
                    current_money = get_current_Money(frame)
                    current_bet = get_current_Bet(frame)
                    currentColor = get_last_color(frame)
                    center_frame = [frame.size[0]/2,frame.size[1]/2]
                    if  current_money < lastmoney and rounds_played != 0 and increased == False:
                        print("bet target increased")
                        betting_target *= 2
                        increased = True
                    elif current_money >= lastmoney:
                        betting_target = small_bet
                    if  current_bet == betting_target:
                        rounds_played += 1
                        print("\n\n")
                        print("Rounds played: ",rounds_played)
                        print("Current color: ",currentColor)
                        print("Last color: ",lastcolor)
                        print("Current money: ",current_money)
                        print("Current bet: ",current_bet)
                        print("Current target: ",betting_target)
                        print("\n\n")
                        lastmoney = current_money
                        lastcolor = currentColor
                        finished_betting = True
                    else:
                        #increment bet
                        for i in range(5):
                            pressKey(DIK_ARROW_DOWN)
                            sleep(0.07)
                            releaseKey(DIK_ARROW_DOWN)
                        if bet_color == "red":
                            autoit.mouse_move(int(center_frame[0]-90), int(center_frame[1]+330))
                        elif bet_color == "black":
                            autoit.mouse_move(int(center_frame[0]+90), int(center_frame[1]+330))
                        elif bet_color == "green":
                            autoit.mouse_move(int(center_frame[0]-550), int(center_frame[1])-75)
                        for k in reversed(bet_list):
                            temp = (betting_target - current_bet) - k
                            if temp >= 0:
                                for x in range(bet_list.index(k)):
                                    pressKey(DIK_ARROW_UP)
                                    sleep(0.09)
                                    releaseKey(DIK_ARROW_UP)
                                autoit.mouse_down("left")
                                sleep(0.15)
                                autoit.mouse_up("left")
                                break
            else:
                finished_betting = False
                increased = False
        else:
            releaseFrame()

_mainThread = threading.Thread(target=mainThread, args=())
_mainThread.start()
listener = Listener(on_press=on_press)
listener.start()
