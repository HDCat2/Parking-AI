from pygame import *
import math
import car_ai as cai


def doLinesIntersect(l1, l2):
    if l1[1][0] == l1[0][0]:
        if l2[1][0] == l2[0][0]:
            if l2[1][0] == l1[1][0]:
                return max(min(l1[0][1], l1[1][1]), min(l2[0][1], l2[1][1])) <= min(max(l1[0][1], l1[1][1]), max(l2[0][1], l2[1][1]))
            else:
                return False
        else:
            m2 = (l2[1][1] - l2[0][1]) / (l2[1][0] - l2[0][0])
            b2 = l2[0][1] - m2 * l2[0][0]
            y = m2 * l1[0][0] + b2
            return min(l1[0][1], l1[1][1]) <= y <= max(l1[0][1], l1[1][1])
    if l2[1][0] == l2[0][0]:
        m1 = (l1[1][1] - l1[0][1]) / (l1[1][0] - l1[0][0])
        b1 = l1[0][1] - m1 * l1[0][0]
        y = m1 * l2[0][0] + b1
        return min(l2[0][1], l2[1][1]) <= y <= max(l2[0][1], l2[1][1])
    m1 = (l1[1][1] - l1[0][1]) / (l1[1][0] - l1[0][0])
    m2 = (l2[1][1] - l2[0][1]) / (l2[1][0] - l2[0][0])
    b1 = l1[0][1] - m1 * l1[0][0]
    b2 = l2[0][1] - m2 * l2[0][0]
    if m1 == m2:
        if b1 == b2:
            return max(min(l1[0][0], l1[1][0]), min(l2[0][0], l2[1][0])) <= min(max(l1[0][0], l1[1][0]), max(l2[0][0], l2[1][0]))
        else:
            return False
    else:
        x = (b2 - b1) / (m1 - m2)
        return max(min(l1[0][0], l1[1][0]), min(l2[0][0], l2[1][0])) <= x <= min(max(l1[0][0], l1[1][0]), max(l2[0][0], l2[1][0]))



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
    def __init__(self, xpos, ypos, width, length, angle):
        self.xpos = xpos
        self.ypos = ypos
        self.width = width
        self.length = length
        self.angle = angle
        self.coords = [(self.xpos + math.cos(self.angle)*self.length/2 + math.sin(self.angle)*self.width/2, self.ypos + math.sin(self.angle)*self.length/2 - math.cos(self.angle)*self.width/2),
                       (self.xpos + math.cos(self.angle)*self.length/2 - math.sin(self.angle)*self.width/2, self.ypos + math.sin(self.angle)*self.length/2 + math.cos(self.angle)*self.width/2),
                       (self.xpos - math.cos(self.angle)*self.length/2 + math.sin(self.angle)*self.width/2, self.ypos - math.sin(self.angle)*self.length/2 - math.cos(self.angle)*self.width/2),
                       (self.xpos - math.cos(self.angle)*self.length/2 - math.sin(self.angle)*self.width/2, self.ypos - math.sin(self.angle)*self.length/2 + math.cos(self.angle)*self.width/2)]


        super().__init__(xpos, ypos)

    def isColliding(self, car):
        """Checks for collision between two rotated rectangles"""

        carDelta = [car.speed*math.cos(car.rotation), car.spped*math.sin(car.rotation)]

        for i in range(4):
            v1 = (self.coords[i], self.coords[(i+1)%4])
            for j in range(4):
                v2 = (car.coords[i]-carDelta, car.coords[i])
                if doLinesIntersect(v1, v2):
                    self.resolveCollision()
                    return True
        return False

    def resolveCollision(self):
        """If a collision has occurred, moves the moving car out of the parked car"""
        raise NotImplementedError

    def update(self, screen):
        draw.rect(screen, (200, 200, 200), (self.xpos - self.width//2, self.ypos-self.length//2, self.width, self.length), 0)

a = ParkedCar(100, 150, 20, 100, 0.5)
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
        """Checks for collision between two rotated rectangles"""

        carDelta = [car.speed*math.cos(car.rotation), car.spped*math.sin(car.rotation)]

        for i in range(4):
            v1 = (self.coords[i], self.coords[(i+1)%4])
            for j in range(4):
                v2 = (car.coords[i]-carDelta, car.coords[i])
                if doLinesIntersect(v1, v2):
                    self.resolveCollision()
                    return True
        return False

    def resolveCollision(self):
        """If a collision has occurred, moves the moving car out of the parked car"""
        raise NotImplementedError

    def update(self, screen):
        draw.rect(screen, (200, 200, 200), (self.xpos - self.width//2, self.ypos-self.length//2, self.width, self.length), 0)

class Simulation:
    def __init__(self, mapFile, doVisualization, fpsFactor, neuralNet):
        mapDetails = open(mapFile, "r")
        self.fps = fpsFactor
        self.obstacleList = []
        self.visualize = doVisualization













