from pygame import *
import math
import car_ai as cai

class Car:
    MAX_CAR_FORWARD_SPEED = 100
    MAX_CAR_BACKWARD_SPEED = -50
    MAX_CAR_TURN = 20
    DEFAULT_WIDTH = 10
    DEFAULT_LENGTH = 30
    STARTING_NETWORK = None

    def __init__(self,
                 width: int,
                 length: int,
                 startXPos: int,
                 startYPos: int,
                 startRotation: float = 0,
                 startNetwork = STARTING_NETWORK):
        self.width = width
        self.length = length
        self.pos = [startXPos, startYPos] # pos refers to the center of the car
        self.rotation = startRotation
        self.speed = 0
        self.collisionModifier = [0,0]
        self.network = startNetwork
    
    def getVision(obstacleList):
        """ Get distance of obstacles from car in 8 directions for use in the neural network """
        raise NotImplementedError

    def getNetworkOutput(obstacleList):
        """ Input current car parameters as well as vision, get acceleration and turn speed """
        raise NotImplementedError

    def move(self):
        """ Process car movement for a single frame """

        # Modify car velocity based on network
        acceleration, turnSpeed = self.getNetworkOutput()

        self.speed = max(Car.MAX_CAR_BACKWARD_SPEED, min(self.speed + acceleration, Car.MAX_CAR_FORWARD_SPEED))
        self.rotation += turnSpeed
        self.rotation %= 2 * math.pi
        
        # Change car position based on velocity
        self.pos = [self.pos + self.speed * math.cos(self.rotation),
                    self.pos + self.speed * math.sin(self.rotation)]
    
    def getNetwork(self):
        """ Return network for use in future iterations """
        raise NotImplementedError

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

class Simulation:
    def __init__(self, mapFile, doVisualization, fpsFactor, neuralNet):
        mapDetails = open(mapFile, "r")
        self.fps = fpsFactor
        self.obstacleList = []
        self.visualize = doVisualization













