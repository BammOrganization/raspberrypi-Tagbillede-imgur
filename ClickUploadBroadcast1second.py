from RPi import GPIO
from time import sleep
from datetime import datetime
import picamera
import pyimgur
from socket import *

clk = 15
dt = 14

GPIO.setmode(GPIO.BCM)
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

clkLastState = GPIO.input(clk)
BROADCAST_TO_PORT = 7000
dBCounter = 40
dBSumFiveSeconds = 0
dBAverage = 0
countOneSecond = 0
countFiveSeconds = 0

s = socket(AF_INET, SOCK_DGRAM)
s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)


def TakePicture():
    presentime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    PATH = "/home/pi/Pictures" + "/" + presentime +".jpg"
    print("About to take a picture.")
    with picamera.PiCamera() as camera:
        camera.capture(PATH)
    print("Picture taken.")
    
    CLIENT_ID = "fc65e40de16806a"    
    im = pyimgur.Imgur(CLIENT_ID)
    uploaded_image = im.upload_image(PATH, title="Uploaded with PyImgur")
    print(uploaded_image.title)
    print(uploaded_image.link)
    print(uploaded_image.size)
    print(uploaded_image.type)
    ImgurLink = uploaded_image.link
    return ImgurLink


def SendData(link):
    data = "Current time " + str(datetime.now()) + " dBAverage: " + str(dBAverage)
    if len(link) > 0:
        data = data + " Link Imgur: " + link        
    s.sendto(bytes(data, "UTF-8"), ('<broadcast>', BROADCAST_TO_PORT))
    print(data)


try:
    while True:         
        clkState = GPIO.input(clk)
        dtState = GPIO.input(dt)
            
        if clkState != clkLastState:                
            if dtState != clkState:
                dBCounter += 1
            else:
                dBCounter -= 1
            clkLastState = clkState 

        sleep(0.01)
        countOneSecond += 1
        if countOneSecond == 100:                        # 1 second (100 * 0.01 sleep)
             countOneSecond = 0 
             countFiveSeconds += 1
             dBSumFiveSeconds += dBCounter
             print("dBCounter: "+ str(dBCounter))
             
             if countFiveSeconds == 5:
                 countFiveSeconds = 0                 
                 dBAverage = dBSumFiveSeconds // 5
                 dBSumFiveSeconds = 0
                   
                 if dBAverage >= 50:                         # over 50 dB  
                    LinkImgur = TakePicture()
                    SendData(LinkImgur)                   
                 else:
                    SendData("")
             
                 

finally:    
    GPIO.cleanup()
        
        

        




