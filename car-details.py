from pygame import *
import math
import car-ai as cai

class Car:
    MAX_CAR_SPEED = 100
    MAX_CAR_TURN = 20
    DEFAULT_WIDTH = 10
    DEFAULT_LENGTH = 30
    STARTING_NETWORK = None

    def __init__(self,
                 width: int,
                 length: int,
                 startXPos: int,
                 startYPos: int,
                 startRotation: float):
        self.width = width
        self.length = length
        self.pos = [startXPos, startYPos] # pos refers to the center of the car
        self.rotation = startRotation
        self.speed = 0
        self.turnSpeed = 0
    
    def move(self):
        self.pos = [self.pos + self.speed * math.cos(self.rotation),
                    self.pos + self.speed * math.sin(self.rotation)]
        self.rotation += self.turnSpeed
        self.rotation %= 2 * math.pi

class Obstacle:
    def __init__(self, xpos, ypos):
        self.xpos = xpos
        self.ypos = ypos


class ParkedCar(Obstacle):
    def __init__(self, xpos, ypos, width, length):
        self.xpos = xpos
        self.ypos = ypos
        self.width = width
        self.length = length

        super().__init__(xpos, ypos)

    def isColliding(self, car):
        """Checks for collision between two rotated rectangles"""

        #TODO: Properly orient car with rotation + complex nums

        newXpos = self.xpos
        newYpos = self.ypos

        distx = abs(self.xpos - car.xpos)
        disty = abs(self.ypos - car.ypos)

        return True

    def update(self, screen):
        draw.rect(screen, (200, 200, 200), (self.xpos - self.width//2, self.ypos-self.length//2, self.width, self.length), 0)


class LightPost(Obstacle):
    def __init__(self, xpos, ypos, radius):
        self.xpos = xpos
        self.ypos = ypos
        self.radius = radius
        super().__init__(xpos, ypos)

    def isColliding(self, car):
        """Checks for collision between circle and rotated rectangle"""

        #TODO: Properly orient car with rotation + complex nums

        newXpos = self.xpos
        newYpos = self.ypos

        distx = abs(newXpos - car.xpos)
        disty = abs(newYpos - car.ypos)

        if distx > (car.width/2 + self.radius):
            return False
        if disty > (car.length/2 + self.radius):
            return False

        if distx <= car.width/2:
            return True
        if disty <= car.length:
            return True

        cornerDist = (distx - car.width/2)**2 + (disty - car.length/2)**2

        return cornerDist <= self.radius**2


    def update(self, screen):
        draw.circle(screen, (200, 200, 200), (self.xpos. self.ypos), self.radius, 0)


class Curb(Obstacle):
    def __init__(self, xpos, ypos, width, length):
        self.xpos = xpos
        self.ypos = ypos
        self.width = width
        self.length = length

    def isColliding(self, car):

        #Properly orient car with rotation + complex nums
        newXpos = self.xpos
        newYpos = self.ypos

        distx = abs(self.xpos - car.xpos)
        disty = abs(self.ypos - car.ypos)

        return True

    def update(self, screen):
        draw.rect(screen, (200, 200, 200), (self.xpos - self.width//2, self.ypos-self.length//2, self.width, self.length), 0)















