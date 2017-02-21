
import pyBotController
import math


###  We need to generate a frame of reference
###  Let's define the Z axis obviously going stright up and down through the center of rotation of the arm
###  Let's place the deck of the bot at the 0 position in the Z direction.
###  Let's make the X axis go horizontal across the bot so that the main rotation servo works from 0 to 180
###  That leaves Y to go fore to aft on the bot where the arm base is at 90 degrees.  

###  When looking at the arm, the entire arm exists in a single 2D plane
###  So we can define the arm in terms of a 2D plane with 
###  the xy plane of the bot becoming the x axis and the z axis of the bot becoming the y axis
###  The joint angles can be scaled so that 0 is in the same direction as the base angle and 180 is opposite
###  Once we have defined the position based on that plane, we can use the base angle to place the 
###  point in the original 3D reference frame. 



class pyBotKinetics:
    
    def __init__(self):
        ### height in mm above the 0 plane of the deck of the bot to the plane the shoulder joint passes through.  
        self.rotationHeightZ = 66.675
        
        ### distance from the center of rotation to the center of the shoulder joint.
        self.shoulderOffset = 14.2875

        self.armLength = 103.98125

        self.forearmLength = 98.425

        self.handLength = 165.1

        self.armWidth = 80.9625
        
        return
    
    
    def microsToRads(self, aMicro):
        
        return (((aMicro - 544.0) / (2400.0 - 544.0)) * math.pi)
    
    
    def getAngles(self):
        
        self.baseAngle = (self.microsToRads(pyBotController.armServos[0].position)) 
        self.shoulderAngle = (self.microsToRads(pyBotController.armServos[1].position))
        self.elbowAngle = (self.microsToRads(pyBotController.armServos[2].position) -(math.pi / 2) + self.shoulderAngle)
        self.wristAngle = (self.microsToRads(pyBotController.armServos[3].position) - (math.pi / 2) + self.elbowAngle)
        self.rotationAngle = (self.microsToRads(pyBotController.armServos[4].position) )
        self.gripAngle = (self.microsToRads(pyBotController.armServos[5].position) )
        
        return
    
    def calculateShoulderPosition(self):
        
        self.getAngles()
        
        xPosition = self.shoulderOffset * math.cos(self.baseAngle)
        yPosition = self.shoulderOffset * math.sin(self.baseAngle)
        zPosition = self.rotationHeightZ
        
        
        return (xPosition, yPosition, zPosition)
    
    
    
    def calculateElbowPosition(self):
        
        shoulderPosition = self.calculateShoulderPosition()                
        
        ###Calculate position relative to shoulder
        
        zPosition = self.armLength * math.sin(self.shoulderAngle)
        xyDist = self.armLength * math.cos(self.shoulderAngle)
        yPosition = xyDist * math.sin(self.baseAngle)
        xPosition = xyDist * math.cos(self.baseAngle)
        
        zPosition += shoulderPosition[2]
        yPosition += shoulderPosition[1]
        xPosition += shoulderPosition[0]
        
        return (xPosition, yPosition, zPosition)
    
    
    def calculateWristPosition(self):
        
        elbowPosition = self.calculateElbowPosition()
        
        ###Calculate position relative to elbow
        
        zPosition = self.forearmLength * math.sin(self.elbowAngle)
        xyDist = self.forearmLength * math.cos(self.elbowAngle)
        yPosition = xyDist * math.sin(self.baseAngle)
        xPosition = xyDist * math.cos(self.baseAngle)
        
        zPosition += elbowPosition[2]
        yPosition += elbowPosition[1]
        xPosition += elbowPosition[0]
        
        return (xPosition, yPosition, zPosition)
                
        
    def calculateTipPosition(self):
        
        wristPosition = self.calculateWristPosition()
        
        ###Calculate position relative to wrist
        
        zPosition = self.handLength * math.sin(self.wristAngle)
        xyDist = self.handLength * math.cos(self.wristAngle)
        yPosition = xyDist * math.sin(self.baseAngle)
        xPosition = xyDist * math.cos(self.baseAngle)
        
        zPosition += wristPosition[2]
        yPosition += wristPosition[1]
        xPosition += wristPosition[0]
        
        return (xPosition, yPosition, zPosition)
    
    ###  Finds angle C given a triangle with sides a, b, and c
    def lawOfCosinesForAngle(self, a, b, c):
        
        interm = ((a*a)+(b*b)-(c*c)) / (2*a*b)
        
        angleC = math.acos(interm)
        
        return angleC
    
    def findServoPositions(self, ba, sa, ea, wa, ra, ga):
        
        bn = ba
        sn = sa
        en = ea + ((math.pi / 2) - sa)
        wn = wa + ((math.pi / 2) - ea)
        rn = ra 
        gn = ga       
        
        
        
        return (bn, sn, en, wn, rn, gn)
    
    
    def reverseCalculateArm(self, (xp, yp, zp)):
        
        self.getAngles()   ### make sure we know where we are now
        
        ### Calculate Base and find shoulder
        
        newBase = math.atan(yp/xp)
        
        syp = self.shoulderOffset * math.sin(newBase)
        sxp = self.shoulderOffset * math.cos(newBase)
        szp = self.rotationHeightZ
        
        ###  Find wrist from tip
        ###  Keep wrist angle the same        
        ### First find tip relative to wrist
        tiprelZ = self.handLength * math.sin(self.wristAngle)
        tiprelxy = self.handLength * math.cos(self.wristAngle)
        tiprelY = tiprelxy * math.sin(newBase)
        tiprelX = tiprelxy * math.cos(newBase)
        
        wyp = yp - tiprelY
        wxp = xp - tiprelX
        wzp = zp - tiprelZ
        
        ###  Now we have the wrist and shoulder positions
        ###  Solve the triangle for the shoulder and elbow angles.
        
        ### the distance from the wrist to the shoulder gives the elbow angle
        s2wDistXY = math.sqrt(((wxp - sxp) * (wxp - sxp)) + ((wyp - syp) * (wyp - syp)))
        s2wDistZ = wzp - szp
        
        s2wDist = math.sqrt((s2wDistXY * s2wDistXY) + (s2wDistZ * s2wDistZ))
        
        elAngRel = self.lawOfCosinesForAngle(self.armLength, self.forearmLength, s2wDist)
        
        ### There are two triangles involved in finding the total shoulder angle
        ###  The angle from the deck to the bottom of the triangle shoulder to wrist to elbow
        shAngRelOne = math.asin(s2wDistZ / s2wDist)
        ###  And the shoulder part of the angle in the shoulder wrist elbow triangle
        shAngRelTwo = self.lawOfCosinesForAngle(self.armLength, s2wDist, self.forearmLength)
        
        newShoulder = shAngRelOne + shAngRelTwo
        
        # Shoulder angle relative to elbow.  180 degrees out from shoulder angle.  
        nsRel = newShoulder + math.pi
        
        ###  angle of forearm with relation to the deck.  
        newElbow = nsRel + elAngRel

        return (newShoulder , newElbow)
    
    
        