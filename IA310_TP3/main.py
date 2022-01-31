import enum
import math
import random
import uuid
from enum import Enum

import mesa
import numpy as np
from collections import defaultdict

import mesa.space
from mesa import Agent, Model
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation
from mesa.visualization.ModularVisualization import VisualizationElement, ModularServer
from mesa.visualization.modules import ChartModule

MAX_ITERATION = 100
PROBA_CHGT_ANGLE = 0.01


def move(x, y, speed, angle):
    return x + speed * math.cos(angle), y + speed * math.sin(angle)


def go_to(x, y, speed, dest_x, dest_y):
    if np.linalg.norm((x - dest_x, y - dest_y)) < speed:
        return (dest_x, dest_y), 2 * math.pi * random.random()
    else:
        angle = math.acos((dest_x - x)/np.linalg.norm((x - dest_x, y - dest_y)))
        if dest_y < y:
            angle = - angle
        return move(x, y, speed, angle), angle


class MarkerPurpose(Enum):
    DANGER = enum.auto(),
    INDICATION = enum.auto()


class ContinuousCanvas(VisualizationElement):
    local_includes = [
        "./js/simple_continuous_canvas.js",
    ]

    def __init__(self, canvas_height=500,
                 canvas_width=500, instantiate=True):
        VisualizationElement.__init__(self)
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.identifier = "space-canvas"
        if (instantiate):
            new_element = ("new Simple_Continuous_Module({}, {},'{}')".
                           format(self.canvas_width, self.canvas_height, self.identifier))
            self.js_code = "elements.push(" + new_element + ");"

    def portrayal_method(self, obj):
        return obj.portrayal_method()

    def render(self, model):
        representation = defaultdict(list)
        for obj in model.schedule.agents:
            portrayal = self.portrayal_method(obj)
            if portrayal:
                portrayal["x"] = ((obj.x - model.space.x_min) /
                                  (model.space.x_max - model.space.x_min))
                portrayal["y"] = ((obj.y - model.space.y_min) /
                                  (model.space.y_max - model.space.y_min))
            representation[portrayal["Layer"]].append(portrayal)
        for obj in model.mines:
            portrayal = self.portrayal_method(obj)
            if portrayal:
                portrayal["x"] = ((obj.x - model.space.x_min) /
                                  (model.space.x_max - model.space.x_min))
                portrayal["y"] = ((obj.y - model.space.y_min) /
                                  (model.space.y_max - model.space.y_min))
            representation[portrayal["Layer"]].append(portrayal)
        for obj in model.markers:
            portrayal = self.portrayal_method(obj)
            if portrayal:
                portrayal["x"] = ((obj.x - model.space.x_min) /
                                  (model.space.x_max - model.space.x_min))
                portrayal["y"] = ((obj.y - model.space.y_min) /
                                  (model.space.y_max - model.space.y_min))
            representation[portrayal["Layer"]].append(portrayal)
        for obj in model.obstacles:
            portrayal = self.portrayal_method(obj)
            if portrayal:
                portrayal["x"] = ((obj.x - model.space.x_min) /
                                  (model.space.x_max - model.space.x_min))
                portrayal["y"] = ((obj.y - model.space.y_min) /
                                  (model.space.y_max - model.space.y_min))
            representation[portrayal["Layer"]].append(portrayal)
        for obj in model.quicksands:
            portrayal = self.portrayal_method(obj)
            if portrayal:
                portrayal["x"] = ((obj.x - model.space.x_min) /
                                  (model.space.x_max - model.space.x_min))
                portrayal["y"] = ((obj.y - model.space.y_min) /
                                  (model.space.y_max - model.space.y_min))
            representation[portrayal["Layer"]].append(portrayal)
        return representation


class Obstacle:  # Environnement: obstacle infranchissable
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r

    def portrayal_method(self):
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Layer": 1,
                     "Color": "black",
                     "r": self.r}
        return portrayal


class Quicksand:  # Environnement: ralentissement
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r

    def portrayal_method(self):
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Layer": 1,
                     "Color": "olive",
                     "r": self.r}
        return portrayal


class Mine:  # Environnement: élément à ramasser
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def portrayal_method(self):
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Layer": 2,
                     "Color": "black",
                     "r": 2}
        return portrayal


class Marker:  # La classe pour les balises
    def __init__(self, x, y, purpose, direction=None):
        self.x = x
        self.y = y
        self.purpose = purpose
        if purpose == MarkerPurpose.INDICATION:
            if direction is not None:
                self.direction = direction
            else:
                raise ValueError("Direction should not be none for indication marker")

    def portrayal_method(self):
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Layer": 2,
                     "Color": "red" if self.purpose == MarkerPurpose.DANGER else "green",
                     "r": 2}
        return portrayal


class Robot(Agent):  # La classe des agents
    def __init__(self, unique_id: int, model: Model, x, y, speed, sight_distance, angle=0.0):
        super().__init__(unique_id, model)
        self.x = x
        self.y = y
        self.speed = speed
        self.sight_distance = sight_distance
        self.angle = angle
        self.counter = 0
        self.max_speed = speed
        self.counter = 0

    def step(self):
        # TODO L'intégralité du code du TP peut être ajoutée ici.
        if self.counter>0:
            self.counter-=1
    
        #DETRUIRE UNE MINE - NIVEAU 0
        defused = False
        mines = [mine for mine in self.model.mines if (self.x,self.y)==(mine.x,mine.y)]
        if len(mines)>0:
            self.model.mines.remove(mines[0])
            self.model.defused_mines+=1
            defused = True


        #CAS DE SABLES MOUVANTS
        quicksands = [quicksand for quicksand in self.model.quicksands if np.linalg.norm((self.x-quicksand.x,self.y-quicksand.y))<quicksand.r]
        if len(quicksands)==0:
            if self.speed != self.max_speed:              
                # Déposer une balise DANGER
                self.model.markers.append(Marker(self.x,self.y,MarkerPurpose.DANGER))
                self.counter=self.max_speed//2
            self.speed = self.max_speed

        else:
            self.speed = self.max_speed//2
            self.model.steps_in_quicksands += 1


        #Se diriger vers une balise - NIVEAU 4
        to_marker = False
        markers =[]
        if self.counter==0:
            markers = [marker for marker in self.model.markers if np.linalg.norm((self.x-marker.x,self.y-marker.y))<self.sight_distance and (self.x,self.y)!=(marker.x,marker.y)]
        if len(markers)>0:
            (x_next,y_next),self.angle = go_to(self.x,self.y,self.speed,markers[0].x,markers[0].y)
            to_marker = True
        # Collecter une balise + Se déplacer suivant l'indication de la balise collectée - NIVEAU 3
        markers=[]
        if self.counter == 0:
            markers = [marker for marker in self.model.markers if (self.x,self.y)==(marker.x,marker.y)]
        if len(markers)>0:
            marker = markers[0]
            if marker.purpose == MarkerPurpose.DANGER:
                self.angle+= math.pi
            elif marker.purpose == MarkerPurpose.INDICATION:
                self.angle = marker.direction + math.pi/2
            self.model.markers.remove(marker)
            self.counter = 0
        #SE DEPLACER (CHANGER L'ANGLE) - NIVEAU 5
        elif random.random() < PROBA_CHGT_ANGLE and not to_marker:
            self.angle = 2*math.pi*random.random()


        #SE DIRIGER VERS UNE MINE - NIVEAU 2
        mines = [ mine for mine in self.model.mines if np.linalg.norm((self.x-mine.x ,self.y-mine.y )) < self.sight_distance]

        if len(mines)>0:
            (x_next,y_next),self.angle = go_to(self.x,self.y,self.speed,mines[0].x,mines[0].y)
        elif not to_marker:
            x_next,y_next = move(self.x,self.y,self.speed,self.angle)

        
        robots = [robot for robot in self.model.schedule.agents if np.linalg.norm((self.x-robot.x,self.y-robot.y))<self.sight_distance and (self.x,self.y)!=(robot.x,robot.y)]
        while True:
            isPossibleCollision = False
            #EVITER UN AUTRE ROBOT
            for robot in robots:               
                v_robot_to_next = np.array([x_next-self.x,y_next-self.y])
                v_robot_to_robot = np.array([robot.x-self.x,robot.y-self.y])
                norm_robot_to_next = np.linalg.norm(v_robot_to_next)
                norm_robot_to_robot = np.linalg.norm(v_robot_to_robot)
                if norm_robot_to_next!= 0:
                    e = v_robot_to_next/norm_robot_to_next
                    dot_ = np.dot(e,v_robot_to_robot)
                    v=e*abs(dot_)
                    colision_distance = np.linalg.norm(v_robot_to_robot-v)
                    if  dot_ < 0:
                        colision_distance = norm_robot_to_robot
                else:
                    colision_distance = norm_robot_to_robot
                
                if colision_distance < self.max_speed:
                    isPossibleCollision = True
                    break
            #EVITER UN OBSTACTE / LES BORDS DE L'ENVIRONNEMENT - NIVEAU 1
            obstacles = [obstacle for obstacle in self.model.obstacles if np.linalg.norm((x_next-obstacle.x,y_next-obstacle.y))<obstacle.r]
            if len(obstacles)==0 and x_next<self.model.space.x_max and x_next>self.model.space.x_min and y_next<self.model.space.y_max and y_next>self.model.space.y_min and not isPossibleCollision:
                break

            self.angle = 2*math.pi *random.random()
            x_next,y_next = move(self.x,self.y,self.speed,self.angle)

        # Déposer une balise INDICATION - NIVEAU 0
        if defused: 
            self.model.markers.append(Marker(self.x,self.y,MarkerPurpose.INDICATION,self.angle))
            self.counter=self.max_speed//2

        self.x,self.y = x_next,y_next


    def portrayal_method(self):
        portrayal = {"Shape": "arrowHead", "s": 1, "Filled": "true", "Color": "Red", "Layer": 3, 'x': self.x,
                     'y': self.y, "angle": self.angle}
        return portrayal


class MinedZone(Model):
    collector = DataCollector(
        model_reporters={"Mines": lambda model: len(model.mines),
                         "Danger markers": lambda model: len([m for m in model.markers if
                                                          m.purpose == MarkerPurpose.DANGER]),
                         "Indication markers": lambda model: len([m for m in model.markers if
                                                          m.purpose == MarkerPurpose.INDICATION]),
                         "Defused mines": lambda model:model.defused_mines,       
                         "Steps in quicksands":lambda model:model.steps_in_quicksands,                          
                         },
        agent_reporters={})

    def __init__(self, n_robots, n_obstacles, n_quicksand, n_mines, speed):
        Model.__init__(self)
        self.space = mesa.space.ContinuousSpace(600, 600, False)
        self.schedule = RandomActivation(self)
        self.mines = []  # Access list of mines from robot through self.model.mines
        self.markers = []  # Access list of markers from robot through self.model.markers (both read and write)
        self.obstacles = []  # Access list of obstacles from robot through self.model.obstacles
        self.quicksands = []  # Access list of quicksands from robot through self.model.quicksands
        for _ in range(n_obstacles):
            self.obstacles.append(Obstacle(random.random() * 500, random.random() * 500, 10 + 20 * random.random()))
        for _ in range(n_quicksand):
            self.quicksands.append(Quicksand(random.random() * 500, random.random() * 500, 10 + 20 * random.random()))
        for _ in range(n_robots):
            x, y = random.random() * 500, random.random() * 500
            while [o for o in self.obstacles if np.linalg.norm((o.x - x, o.y - y)) < o.r] or \
                    [o for o in self.quicksands if np.linalg.norm((o.x - x, o.y - y)) < o.r]:
                x, y = random.random() * 500, random.random() * 500
            self.schedule.add(
                Robot(int(uuid.uuid1()), self, x, y, speed,
                      2 * speed, random.random() * 2 * math.pi))
        for _ in range(n_mines):
            x, y = random.random() * 500, random.random() * 500
            while [o for o in self.obstacles if np.linalg.norm((o.x - x, o.y - y)) < o.r] or \
                    [o for o in self.quicksands if np.linalg.norm((o.x - x, o.y - y)) < o.r]:
                x, y = random.random() * 500, random.random() * 500
            self.mines.append(Mine(x, y))
        self.datacollector = self.collector
        self.defused_mines = 0
        self.steps_in_quicksands = 0

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        if not self.mines:
            self.running = False


def run_single_server():
    chart = ChartModule([{"Label": "Mines",
                          "Color": "Orange"},
                         {"Label": "Danger markers",
                          "Color": "Red"},
                         {"Label": "Indication markers",
                          "Color": "Green"},
                         { "Label": "Defused mines",
                          "Color":"Blue"},
                        {"Label":"Steps in quicksands",
                            "Color":"Black"}
                     
                         ],
                        data_collector_name='datacollector')
    server = ModularServer(MinedZone,
                           [ContinuousCanvas(),
                            chart],
                           "Deminer robots",
                           {"n_robots": mesa.visualization.
                            ModularVisualization.UserSettableParameter('slider', "Number of robots", 7, 3,
                                                                       15, 1),
                            "n_obstacles": mesa.visualization.
                            ModularVisualization.UserSettableParameter('slider', "Number of obstacles", 5, 2, 10, 1),
                            "n_quicksand": mesa.visualization.
                            ModularVisualization.UserSettableParameter('slider', "Number of quicksand", 5, 2, 10, 1),
                            "speed": mesa.visualization.
                            ModularVisualization.UserSettableParameter('slider', "Robot speed", 15, 5, 40, 5),
                            "n_mines": mesa.visualization.
                            ModularVisualization.UserSettableParameter('slider', "Number of mines", 15, 5, 30, 1)})
    server.port = 8521
    server.launch()


if __name__ == "__main__":
    run_single_server()
