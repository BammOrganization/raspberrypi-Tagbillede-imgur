from RPi import GPIO
from time import sleep
import picamera
from datetime import datetime

import pyimgur

BROADCAST_TO_PORT = 7000
import time
from socket import *
from datetime import datetime


clk = 15
dt = 14

GPIO.setmode(GPIO.BCM)
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
dBCounter = 40
clkLastState = GPIO.input(clk)

countOneSecond = 0
countOnlyTakePictureEveryFive = 5

def TakePicture():
    presentime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    PATH = "/home/pi/Pictures" + "/" + presentime +".jpg"
    print("About to take a picture.")
    with picamera.PiCamera() as camera:
        camera.capture(PATH)
    print("Picture taken.")
    
    CLIENT_ID = "fc65e40de16806a"    
    im = pyimgur.Imgur(CLIENT_ID)
    uploaded_image = im.upload_image(PATH, title="Uploaded with PyImgur")  #, album="yzX2w"
    print(uploaded_image.title)
    print(uploaded_image.link)
    print(uploaded_image.size)
    print(uploaded_image.type)
    ImgurLink = uploaded_image.link
    return ImgurLink



s = socket(AF_INET, SOCK_DGRAM)
#s.bind(('', 14593))     # (ip, port)
# no explicit bind: will bind to default IP + random port
s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

while True:
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
                #print (dBCounter)

            sleep(0.01)
            countOneSecond += 1
            if countOneSecond == 100:                      # 1 second (100 milisecond)                                                            
                if dBCounter >= 50:                        # over 50 dB
                    if countOnlyTakePictureEveryFive == 5:  # take picture every 5th time
                        LinkImgur = TakePicture()
                        dataPicTaken = "Current time " + str(datetime.now()) + " dBCounter: " + str(dBCounter) + " Link Imgur: " + LinkImgur
                        s.sendto(bytes(dataPicTaken, "UTF-8"), ('<broadcast>', BROADCAST_TO_PORT))
                        print(dataPicTaken)
                        countOnlyTakePictureEveryFive = 0                        
                    else:
                        countOnlyTakePictureEveryFive += 1
                        data = "Current time " + str(datetime.now()) + " dBCounter: " + str(dBCounter)
                        s.sendto(bytes(data, "UTF-8"), ('<broadcast>', BROADCAST_TO_PORT))
                        print(data)
                        print("Waiting a little to take picture")
                    

                else:                                      # under 50 dB
                    data = "Current time " + str(datetime.now()) + " dBCounter: " + str(dBCounter)
                    s.sendto(bytes(data, "UTF-8"), ('<broadcast>', BROADCAST_TO_PORT))
                    print(data)
                countOneSecond = 0                        

    finally:
        GPIO.cleanup()
        

        




