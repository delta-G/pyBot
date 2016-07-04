import math


class pyBotServo:
    
    def __init__(self, name, initial, minimum, maximum):
        
        self.name = name
        self.minimum = minimum
        self.maximum = maximum
        self.target = initial
        self.position = initial
        self.incrementSpeed = 10
        
        return
    
    def scalePosition(self):
        if self.position > self.maximum:
            self.position = self.maximum
        elif self.position < self.minimum:
            self.position = self.minimum
        return
    
    def scaleTarget(self):
        if self.target > self.maximum:
            self.target = self.maximum
        elif self.target < self.minimum:
            self.target = self.minimum
        return
        
    def moveTo(self, posit):
        self.target = posit
        self.scaleTarget()
        return
    
    def moveToImmediate(self, posit):
        self.position = posit
        self.scalePosition()
        return
    
    def increase(self):
        self.position = self.position + 1
        self.scalePosition()
        return
    
    def decrease(self):
        self.position = self.position - 1
        self.scalePosition()
        return
    
    def increment(self, stickPosition):
        amt = self.incrementSpeed * stickPosition        
        self.moveToImmediate(int(self.position + amt))
        return
    
    