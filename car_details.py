from pygame import *
import math
import car_ai as cai


def doLinesIntersect(l1, l2):
    """Checks if two line segments intersect, returns False if not otherwise returns intersection point"""
    if l1[1][0] == l1[0][0]: #If l1 is vertical
        if l2[1][0] == l2[0][0]: #If l2 is also vertical
            return False
        else: #if l1 is vertical and l2 isn't
            m2 = (l2[1][1] - l2[0][1]) / (l2[1][0] - l2[0][0])
            b2 = l2[0][1] - m2 * l2[0][0]
            y = m2 * l1[0][0] + b2
            if min(l1[0][1], l1[1][1]) <= y <= max(l1[0][1], l1[1][1]):
                return [l1[1][0], y]
            else:
                return False
    if l2[1][0] == l2[0][0]: #if l2 is vertical and l1 isn't
        m1 = (l1[1][1] - l1[0][1]) / (l1[1][0] - l1[0][0])
        b1 = l1[0][1] - m1 * l1[0][0]
        y = m1 * l2[0][0] + b1
        if min(l2[0][1], l2[1][1]) <= y <= max(l2[0][1], l2[1][1]):
            return [l2[1][0], y]
        else:
            return False
    #neither line is vertical, use y=mx+b normally
    m1 = (l1[1][1] - l1[0][1]) / (l1[1][0] - l1[0][0])
    m2 = (l2[1][1] - l2[0][1]) / (l2[1][0] - l2[0][0])
    b1 = l1[0][1] - m1 * l1[0][0]
    b2 = l2[0][1] - m2 * l2[0][0]
    if m1 == m2: #Parallel lines
        return False
    else:
        x = (b2 - b1) / (m1 - m2)
        if max(min(l1[0][0], l1[1][0]), min(l2[0][0], l2[1][0])) <= x <= min(max(l1[0][0], l1[1][0]), max(l2[0][0], l2[1][0])):
            return [x, m1*x+b1]
        else:
            return False

def getRectCoords(xpos, ypos, width, length, angle):
    return [(xpos + math.cos(angle) * length / 2 + math.sin(angle) * width / 2,
                    ypos + math.sin(angle) * length / 2 - math.cos(angle) * width / 2),
                   (xpos - math.cos(angle) * length / 2 + math.sin(angle) * width / 2,
                    ypos - math.sin(angle) * length / 2 - math.cos(angle) * width / 2),
                   (xpos - math.cos(angle) * length / 2 - math.sin(angle) * width / 2,
                    ypos - math.sin(angle) * length / 2 + math.cos(angle) * width / 2),
                    (xpos + math.cos(angle) * length / 2 - math.sin(angle) * width / 2,
                     ypos + math.sin(angle) * length / 2 + math.cos(angle) * width / 2)]


class Car:
    MAX_CAR_FORWARD_SPEED = 10
    MAX_CAR_BACKWARD_SPEED = -5
    MAX_CAR_TURN = 0.3
    DEFAULT_WIDTH = 10
    DEFAULT_LENGTH = 30
    STARTING_NETWORK = None
    CAR_ACCELERATION = 0.01
    CAR_DECELERATION = -0.01
    FRICTION = 0.002

    def __init__(self,
                 width: int,
                 length: int,
                 startXPos: float,
                 startYPos: float,
                 startRotation: float = 0,
                 startNetwork = STARTING_NETWORK):
        self.width = width
        self.length = length
        self.pos = [startXPos, startYPos] # pos refers to the center of the car
        self.wheelAngle = 0
        self.rotation = startRotation
        self.speed = 0
        self.collisionModifier = [0,0]
        self.network = startNetwork
        self.vertices = getRectCoords(self.pos[0], self.pos[1], self.width, self.length, self.rotation)
    
    def getVision(obstacleList):
        """ Get distance of obstacles from car in 8 directions for use in the neural network """
        raise NotImplementedError

    def getNetworkOutput(obstacleList):
        """ Input current car parameters as well as vision, get acceleration and turn speed """
        raise NotImplementedError

    def gas(self, val):
        #val is -1 to 1 (brake to gas)
        if val > 0:
            self.speed = min(Car.MAX_CAR_FORWARD_SPEED, self.speed + Car.CAR_ACCELERATION * val)
        elif val < 0:
            self.speed = max(Car.MAX_CAR_BACKWARD_SPEED, self.speed - Car.CAR_DECELERATION * val)


    def turn(self, val):
        #val is -1 - 1
        self.wheelAngle = min(max(val, -1), 1)

    def wip(self):
        # Modify car velocity based on network
        acceleration, turnSpeed = self.getNetworkOutput()

        self.speed = max(Car.MAX_CAR_BACKWARD_SPEED, min(self.speed + acceleration, Car.MAX_CAR_FORWARD_SPEED))
        self.rotation += turnSpeed
        self.rotation %= 2 * math.pi

    def move(self):
        """ Process car movement for a single frame """

        self.pos[0] += self.collisionModifier[0]
        self.pos[1] += self.collisionModifier[1]
        self.collisionModifier = [0, 0]

        if self.speed > 0:
            self.speed = max(self.speed - Car.FRICTION, 0)
        if self.speed < 0:
            self.speed = min(self.speed + Car.FRICTION, 0)

        self.rotation += self.wheelAngle * Car.MAX_CAR_TURN * (self.speed/Car.MAX_CAR_FORWARD_SPEED)
        
        # Change car position based on velocity
        self.pos = [self.pos[0] + self.speed * math.cos(self.rotation),
                    self.pos[1] + self.speed * math.sin(self.rotation)]

        # Update the vertices of the car rectangle
        self.vertices = getRectCoords(self.pos[0], self.pos[1], self.width, self.length, self.rotation)
    
    def getNetwork(self):
        """ Return network for use in future iterations """
        raise NotImplementedError

    def update(self, screen):
        """ Display the driving car to the screen """
        draw.polygon(screen, (255, 0, 0), self.vertices, 0)

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
        self.coords = getRectCoords(self.xpos, self.ypos, self.width, self.length, self.angle)


        super().__init__(xpos, ypos)

    def isColliding(self, car):
        """Checks for collision between two rotated rectangles"""

        carDelta = [car.speed*math.cos(car.rotation), car.speed*math.sin(car.rotation)]

        flag = False
        intersectionPointPairs = []
        for i in range(4):
            v1 = (self.coords[i], self.coords[(i+1)%4]) #Edge of parked car
            for j in range(4):

                v2 = ((car.vertices[j][0] - carDelta[0], car.vertices[j][1] - carDelta[1]), car.vertices[j]) #Movement vector of one vertex of driving car
                print(carDelta, car.vertices)
                poi = doLinesIntersect(v1, v2)

                if poi:
                    #find intersection point between v1 and v2
                    intersectionPointPairs.append([poi, car.vertices[j]])
                    flag = True

        if flag == False:
            return False

        self.resolveCollision(intersectionPointPairs, carDelta, car)

        return True


    def resolveCollision(self, intersectionPointPairs, carDelta, car):
        """If a collision has occurred, moves the moving car out of the parked car"""

        curMax = -1
        for pair in intersectionPointPairs:
            dist = ((pair[1][0] - pair[0][0])**2 + (pair[1][1] - pair[0][1])**2)**0.5
            if dist > curMax:
                curMax = dist

        deltaMag = (carDelta[0]**2 + carDelta[1]**2)**2

        if deltaMag == 0:
            return

        direction = (carDelta[0]/deltaMag, carDelta[1]/deltaMag)

        correction = (-direction[0]*curMax, -direction[1]*curMax)

        car.collisionModifier = correction

        #TODO: Correct car position by correction



    def update(self, screen):
        draw.polygon(screen, (200, 200, 200), self.coords, 0)

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

        flag = False
        intersectionPointPairs = []
        for i in range(4):
            v1 = (self.coords[i], self.coords[(i+1)%4]) #Edge of parked car
            for j in range(4):
                v2 = ((car.coords[j][0] - carDelta[0], car.coords[j][1] - carDelta[1]), car.coords[j]) #Movement vector of one vertex of driving car
                poi = doLinesIntersect(v1, v2)
                if poi:
                    #find intersection point between v1 and v2
                    intersectionPointPairs.append([poi, car.coords[j]])
                    flag = True

        self.resolveCollision(intersectionPointPairs, carDelta, car)

        return flag


    def resolveCollision(self, intersectionPointPairs, carDelta, car):
        """If a collision has occurred, moves the moving car out of the parked car"""

        curMax = -1
        for pair in intersectionPointPairs:
            dist = ((pair[1][0] - pair[0][0])**2 + (pair[1][1] - pair[0][1])**2)**0.5
            if dist > curMax:
                curMax = dist

        deltaMag = (carDelta[0]**2 + carDelta[1]**2)**2
        direction = (carDelta[0]/deltaMag, carDelta[1]/deltaMag)

        correction = (-direction[0]*curMax, -direction[1]*curMax)

        #TODO: Correct car position by correction

    def update(self, screen):
        draw.rect(screen, (200, 200, 200), (self.xpos - self.width//2, self.ypos-self.length//2, self.width, self.length), 0)

class Simulation:
    def __init__(self, mapFile, doVisualization, fpsFactor,  neuralNet, isTest = True):
        #mapDetails = open(mapFile, "r")
        self.fps = fpsFactor
        self.obstacleList = []
        self.visualize = doVisualization
        self.isTest = isTest

    def run(self):
        init()
        running = True
        clock = time.Clock()
        WIDTH, HEIGHT = 1280, 720
        screen = display.set_mode((WIDTH, HEIGHT))

        a = ParkedCar(600, 600, 80, 200, 1)
        b = ParkedCar(800, 600, 80, 200, 1)
        c = Car(80, 200, 400, 300, 0, None)

        while running:
            keys = key.get_pressed()
            mx, my = mouse.get_pos()
            for action in event.get():
                if action.type == QUIT:
                    running = False
                    break

            if keys[K_w]:
                c.gas(1)
            elif keys[K_s]:
                c.gas(-1)
            c.turn((mx//(WIDTH//10)-5)*0.1)

            a.isColliding(c)
            b.isColliding(c)
            c.move()

            screen.fill((255, 255, 255))
            c.update(screen)
            a.update(screen)
            b.update(screen)

            display.flip()
            clock.tick(self.fps)
        quit()














