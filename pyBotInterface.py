import xbox
import socket
import pyBotServo

SOCKACTIVE = False

print("Global Interface")

if SOCKACTIVE:
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

armServos = [pyBotServo.pyBotServo("base", 90, 0, 180), pyBotServo.pyBotServo("shoulder" , 65, 0, 180), pyBotServo.pyBotServo("elbow" , 65, 0, 180), pyBotServo.pyBotServo("wrist" , 170, 0, 180), pyBotServo.pyBotServo("rotate", 90, 0, 180), pyBotServo.pyBotServo("grip", 120, 110, 180)]






def init():
    if SOCKACTIVE:
        sockOut.connect(sockArgs)
    return


def driveMode():
    
    global motorLeft
    global motorRight
    
    
    leftY = joy.leftY()
    rightY = joy.rightY()
    
    ml = 0
    mr = 0
    
    
    if (leftY > 0) :
        ml = 1
    elif (leftY < 0) :
        ml = -1;
    else: 
        ml = 0    
    
    if rightY > 0 :
        mr = 1
    elif rightY < 0 :
        mr = -1;
    else: 
        mr = 0
        
    if ml != motorLeft:
        motorLeft = ml
        commandString = ""
        commandString += "<"
        commandString += "ML"
        commandString += ","
        commandString += str(motorLeft)
        commandString += ">"
        if SOCKACTIVE:
            sockOut.send(commandString)
        print commandString
    
    if mr != motorRight:
        motorRight = mr
        commandString = ""
        commandString += "<"
        commandString += "MR"
        commandString += ","
        commandString += str(motorRight)
        commandString += ">"
        if SOCKACTIVE:
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
    if SOCKACTIVE:
        sockOut.send(commandString)
    print(commandString)
    
    return
    
def dpadMotor():
    
    global motorLeft
    global motorRight
    
    ml = 0
    mr = 0
    
    dpad = ((joy.dpadDown() << 3) | (joy.dpadLeft() << 2) | (joy.dpadRight() << 1) | (joy.dpadUp()))
    
    if(dpad == 0):
        ml = 0
        mr = 0
    elif(dpad == 1):
        ml = 1
        mr  = 1
    elif(dpad == 2):
        ml = 1
        mr  = -1
    elif(dpad == 3):
        ml = 1
        mr  = 0
    elif(dpad == 4):
        ml = -1
        mr  = 1
    elif(dpad == 5):
        ml = 0
        mr  = 1
    elif(dpad == 8):
        ml = -1
        mr  = -1
    elif(dpad == 10):
        ml = -1
        mr  = 0
    elif(dpad == 12):
        ml = 0
        mr  = -1
    else:
        ml = 0
        mr = 0
    
    
    if ml != motorLeft:
        motorLeft = ml
        commandString = ""
        commandString += "<"
        commandString += "ML"
        commandString += ","
        commandString += str(motorLeft)
        commandString += ">"
        if SOCKACTIVE:
            sockOut.send(commandString)
        print commandString
    
    if mr != motorRight:
        motorRight = mr
        commandString = ""
        commandString += "<"
        commandString += "MR"
        commandString += ","
        commandString += str(motorRight)
        commandString += ">"
        if SOCKACTIVE:
            sockOut.send(commandString)
        print commandString    
    
    return
    
def armMode():
    
    dpadMotor()    
    
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
    
    
    
    
    
    
    