import xbox
import socket
import pyBotServo
import time
###from pyBot import pressTime



print("Global Interface")

sockOut = socket.socket(socket.AF_INET , socket.SOCK_STREAM)

sockArgs = ('192.168.4.1' , 1234)

joy = xbox.Joystick()


motorRight = 0;
motorLeft = 0;

BASE = 0
SHOULDER = 1
ELBOW = 2
WRIST = 3
ROTATE = 4
GRIP = 5

# servoPositions = [90, 65, 65, 170, 90, 120]

armServos = [pyBotServo.pyBotServo("base", 90, 0, 180), pyBotServo.pyBotServo("shoulder" , 65, 20, 170), pyBotServo.pyBotServo("elbow" , 65, 20, 170), pyBotServo.pyBotServo("wrist" , 170, 30, 180), pyBotServo.pyBotServo("rotate", 90, 0, 180), pyBotServo.pyBotServo("grip", 120, 110, 180)]






def init():
    
    sockOut.connect(sockArgs)
    return


def driveMode():
    
    global motorLeft
    global motorRight
    
    
    leftY = joy.leftY()
    rightY = joy.rightY()
    
    
    if (leftY > 0) :
        motorLeft = 1
    elif (leftY < 0) :
        motorLeft = -1;
    else: 
        motorLeft = 0    
    
    if rightY > 0 :
        motorRight = 1
    elif rightY < 0 :
        motorRight = -1;
    else: 
        motorRight = 0
        
    
    commandString = ""
    commandString += "<"
    commandString += "MR"
    commandString += ","
    commandString += str(motorRight)
    commandString += ">"
    sockOut.send(commandString)
    print commandString
    
    commandString = ""
    commandString += "<"
    commandString += "ML"
    commandString += ","
    commandString += str(motorLeft)
    commandString += ">"
    sockOut.send(commandString)
    print commandString   
        
    return

def armModeHelper(stickPosition , servo):
    
    if(stickPosition > 0):
        armServos[servo].increase()
        armCommandSender(servo)
    elif(stickPosition < 0):
        armServos[servo].decrease()
        armCommandSender(servo)
    else:
        return False
    return True

def armCommandSender(servo):
    commandString = ""
    commandString += "<S"
    commandString += str(servo)
    commandString += ","
    commandString += str(armServos[servo].position)
    commandString += ">"
    sockOut.send(commandString)
    print(commandString)
    
    return

lastXPushTime = time.time() 
    
def armMode():
    
    if joy.X():
        pressTime = time.time()
        if(pressTime - lastXPushTime >= 1):
            sockOut.send("<R>")
        lastXPushTime = pressTime
                    
    
    leftX = joy.leftX();
    leftY = joy.leftY();
    rightX = joy.rightX();
    rightY = joy.rightY();
    leftBump = joy.leftBumper()
    rightBump = joy.rightBumper()
    leftTrigger = joy.leftTrigger()
    rightTrigger = joy.rightTrigger()
    
    armModeHelper(leftX, ROTATE)
    armModeHelper(leftY, WRIST)
    armModeHelper(rightX, SHOULDER)
    armModeHelper(rightY, ELBOW)
    armModeHelper(rightTrigger - leftTrigger, GRIP)
    if(leftBump):
        armServos[BASE].decrease()
        armCommandSender(BASE)
    elif(rightBump):
        armServos[BASE].increase()
        armCommandSender(BASE)
    
    return
    
    
    
    
    
    
    