import time
import os
import pyBotController

print("Starting")

controller = pyBotController.pyBotController()

print("interface initialized")

controlMode = 0

lastStartPress = time.time()

try:
    #Valid connect may require joystick input to occur
    print "Waiting for Joystick to connect"
    while not controller.joy.connected():
        time.sleep(0.10)
    print "Joystick Connected"
        
    while controller.runInterface():
        pass            
    

finally:
    #Always close out so that xboxdrv subprocess ends
    controller.joy.close()
    os.system('pkill -9 xboxdrv')
    print "Done."
