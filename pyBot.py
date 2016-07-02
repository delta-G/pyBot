import xbox
import time
import pyBotInterface
import os

print("Starting")

pyBotInterface.init()

print("interface initialized")

controlMode = 0

lastStartPress = time.time()

try:
    #Valid connect may require joystick input to occur
    print "Waiting for Joystick to connect"
    while not pyBotInterface.joy.connected():
        time.sleep(0.10)
        
    while not pyBotInterface.joy.Back() and pyBotInterface.joy.connected():
        
        if(pyBotInterface.joy.Start()):
            
            pressTime = time.time()
            
            if (pressTime - lastStartPress >= 1):
                controlMode += 1
                controlMode %= 2
            lastStartPress = pressTime
            if(controlMode == 0):
                print("Drive Mode Activated")
            elif(controlMode == 1):
                print("Arm Mode Activated")
            
        


    #    Read our inputs and send commands
        if(controlMode == 0):
            pyBotInterface.driveMode()
        elif(controlMode == 1):
            pyBotInterface.armMode()
        time.sleep(0.02)
            
    

finally:
    #Always close out so that xboxdrv subprocess ends
    pyBotInterface.joy.close()
    os.system('pkill -9 xboxdrv')
    print "Done."
