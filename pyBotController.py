import xbox
import socket
import pyBotServo
import time
import errno
from __builtin__ import False
from _socket import MSG_DONTWAIT


class pyBotController:
    
    def __init__(self):
        
        self.socketConnected = False 
        
        print("Global Interface")


        self.sockOut = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
#         self.sockOut.setblocking(0)
        

        self.sockArgs = ('192.168.4.1' , 1234)

        self.joy = xbox.Joystick()
        
        print "Controller attached!"

        self.returnBuffer = ""


        self.motorRight = 0;
        self.motorLeft = 0;
        
        self.invertShoulder = False
        self.invertElbow = False
        self.invertWrist = False
        
        self.lastY = 0
        self.lastA = 0
        self.lastThumbR = 0
        self.lastThumbL = 0
        self.controlMode = 0
        self.lastRunTime = 0

        self.BASE = 0
        self.SHOULDER = 1
        self.ELBOW = 2
        self.WRIST = 3
        self.ROTATE = 4
        self.GRIP = 5
        self.armServos = [pyBotServo.pyBotServo("base", 1500, 544, 2400), pyBotServo.pyBotServo("shoulder" , 1214, 544, 2400), pyBotServo.pyBotServo("elbow" , 1215, 544, 2400), pyBotServo.pyBotServo("wrist" , 2000, 544, 2400), pyBotServo.pyBotServo("rotate", 1500, 544, 2400), pyBotServo.pyBotServo("grip", 2000, 1680, 2400)]
        
    
    def runInterface(self):
    
        
        
        if(self.joy.Start() and not self.socketConnected):
            print("Connecting to Robot")
            self.socketConnected = True
            self.sockOut.connect(self.sockArgs)
            print ("Connected to Robot")
        
        joyY = self.joy.Y()
        joyA = self.joy.A()
        
        
        if self.joy.Back() or not self.joy.connected():
            return False
        
        if time.time() - self.lastRunTime >= 0.02:
            if(joyA and not self.lastA):
                self.requestFromESP('B')
            self.lastA = joyA
        
            if (joyY and not self.lastY):
                self.controlMode += 1
                self.controlMode %= 2
                if(self.controlMode == 0):
                    print("Drive Mode Activated")
                elif(self.controlMode == 1):
                    print("Arm Mode Activated")
            self.lastY = joyY
            
            if(self.controlMode == 0):
                self.driveMode()
            elif(self.controlMode == 1):
                self.armMode()
                
            self.lastRunTime = time.time()
        
        self.listenForESP()
            
        return True
    
    
    def listenForESP(self):
        
        if self.socketConnected:
            try:
                c = self.sockOut.recvfrom(1024, MSG_DONTWAIT)
#                 while c != "":
#                     self.returnBuffer += c
#                     if c == '>':
#                         print self.returnBuffer
#                         self.returnBuffer = ""
#                     c = self.sockOut.recv(1)
                if c != "":
                    print c
        
            except socket.error, e:
                err = e.args[0]
                if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                    pass
                else:
                    # a REAL error occurred
                    print"Bad Error in linstenForESP"
                    print err
            else:
                print c
        return
    
    
    def requestFromESP(self, reqStr):
        
        commandString = ""
        commandString += "<"
        commandString += "R"
        commandString += reqStr
        commandString += ">"
        if self.socketConnected:
            self.sockOut.send(commandString)
        print commandString
        
        
        
        return
    
    
    
    
    
    def driveMode(self):
        
        leftBump = self.joy.leftBumper()
        rightBump = self.joy.rightBumper()
        leftTrigger = self.joy.leftTrigger()
        rightTrigger = self.joy.rightTrigger()
        
        self.armModeHelper(rightTrigger - leftTrigger, self.GRIP)
        if(leftBump):
            self.armServos[self.BASE].increment(-1.0)
            self.armCommandSender(self.BASE)
        elif(rightBump):
            self.armServos[self.BASE].increment(1.0)
            self.armCommandSender(self.BASE)
        
        leftY = self.joy.leftY()
        rightY = self.joy.rightY()
        
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
            
        if ml != self.motorLeft:
            self.motorLeft = ml
            commandString = ""
            commandString += "<"
            commandString += "ML"
            commandString += ","
            commandString += str(self.motorLeft)
            commandString += ">"
            if self.socketConnected:
                self.sockOut.send(commandString)
            print commandString
        
        if mr != self.motorRight:
            self.motorRight = mr
            commandString = ""
            commandString += "<"
            commandString += "MR"
            commandString += ","
            commandString += str(self.motorRight)
            commandString += ">"
            if self.socketConnected:
                self.sockOut.send(commandString)
            print commandString   
            
        return
    
    def armModeHelper(self, stickPosition , servo, invert = False):
        if stickPosition != 0:
            if invert:
                stickPosition = -stickPosition

            self.armServos[servo].increment(stickPosition)
#             if(stickPosition > 0):
#                 self.armServos[servo].increase()
#                 self.armCommandSender(servo)
#             elif(stickPosition < 0):
#                 self.armServos[servo].decrease()
            self.armCommandSender(servo)
                
            return True
        
        return False
    
    def armCommandSender(self, servo):
        commandString = ""
        commandString += "<S"
        commandString += str(servo)
        commandString += ","
        commandString += str(self.armServos[servo].position)
        commandString += ">"
        if self.socketConnected:
            self.sockOut.send(commandString)
        print(commandString)
        
        return
        
    def dpadMotor(self):
        
        ml = 0
        mr = 0
        
        dpad = ((self.joy.dpadDown() << 3) | (self.joy.dpadLeft() << 2) | (self.joy.dpadRight() << 1) | (self.joy.dpadUp()))
        
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
        
        
        if ml != self.motorLeft:
            self.motorLeft = ml
            commandString = ""
            commandString += "<"
            commandString += "ML"
            commandString += ","
            commandString += str(self.motorLeft)
            commandString += ">"
            if self.socketConnected:
                self.sockOut.send(commandString)
            print commandString
        
        if mr != self.motorRight:
            self.motorRight = mr
            commandString = ""
            commandString += "<"
            commandString += "MR"
            commandString += ","
            commandString += str(self.motorRight)
            commandString += ">"
            if self.socketConnected:
                self.sockOut.send(commandString)
            print commandString    
        
        return
        
    def armMode(self):
        
        self.dpadMotor()
        
        deadZ = 1000
            
        thumbR = self.joy.rightThumbstick()
        thumbL = self.joy.leftThumbstick()
        leftX = self.joy.leftX(deadZ);
        leftY = self.joy.leftY(deadZ);
        rightX = self.joy.rightX(deadZ);
        rightY = self.joy.rightY(deadZ);
        leftBump = self.joy.leftBumper()
        rightBump = self.joy.rightBumper()
        leftTrigger = self.joy.leftTrigger()
        rightTrigger = self.joy.rightTrigger()   
        
        
        self.armModeHelper(rightX, self.ROTATE)
        self.armModeHelper(rightY, self.WRIST, self.invertWrist)
        self.armModeHelper(leftX, self.SHOULDER, self.invertShoulder)
        self.armModeHelper(leftY, self.ELBOW, self.invertElbow)
        self.armModeHelper(rightTrigger - leftTrigger, self.GRIP)
        if(leftBump):
            self.armServos[self.BASE].increment(-0.1)
            self.armCommandSender(self.BASE)
        elif(rightBump):
            self.armServos[self.BASE].increment(0.1)
            self.armCommandSender(self.BASE)
        
        if thumbR and not self.lastThumbR:
            self.invertElbow = not self.invertElbow
            self.invertWrist = not self.invertWrist
        self.lastThumbR = thumbR
        
        if thumbL and not self.lastThumbL:
            self.invertShoulder = not self.invertShoulder
        self.lastThumbL = thumbL
        
        
        return
        
    
    
    
    
        
