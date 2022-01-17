import math
import random
import uuid
from collections import defaultdict

import mesa
import tornado, tornado.ioloop
from mesa import space
from mesa.time import RandomActivation
from mesa.visualization.ModularVisualization import ModularServer, VisualizationElement, UserSettableParameter
from mesa.datacollection import DataCollector
from mesa.visualization.modules import ChartModule
from mesa.batchrunner import BatchRunner,BatchRunnerMP


class Village(mesa.Model):

    def __init__(self, n_villagers, n_lycanthropes,n_clerics,n_hunters):
        mesa.Model.__init__(self)
        self.space = mesa.space.ContinuousSpace(600, 600, False)
        self.schedule = RandomActivation(self)
        for _ in range(n_villagers):
            self.schedule.add(Villager(random.random() * 500, random.random() * 500, 10, int(uuid.uuid1()), self))
        for _ in range(n_lycanthropes):
            self.schedule.add(Villager(random.random() * 500, random.random() * 500, 10, int(uuid.uuid1()), self,lycanthrope=True))
        for _ in range(n_clerics):
            self.schedule.add(Cleric(random.random()*500,random.random()*500,10, int(uuid.uuid1()),self))
        for _ in range(n_hunters):
            self.schedule.add(Hunter(random.random()*500,random.random()*500,10, int(uuid.uuid1()),self))

        self.datacollector = DataCollector(
                model_reporters={
                    "Population" : lambda module : len(module.schedule.agents), 
                    "Werewolves" : lambda model : len([agent for agent in model.schedule.agents if type(agent)==Villager and agent.transforme]),
                    "Humains": lambda model: len([agent for agent in model.schedule.agents if type(agent)!=Villager or not(agent.lycanthrope) ]),
                    "lycanthropes" : lambda model : len([agent for agent in model.schedule.agents if type(agent)==Villager and agent.lycanthrope]),
                }
        )
        self.datacollector.collect(self)
                


    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)
        if self.schedule.steps >= 1000:
            self.running = False


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
                portrayal["x"] = ((obj.pos[0] - model.space.x_min) /
                                  (model.space.x_max - model.space.x_min))
                portrayal["y"] = ((obj.pos[1] - model.space.y_min) /
                                  (model.space.y_max - model.space.y_min))
            representation[portrayal["Layer"]].append(portrayal)
        return representation


def wander(x, y, speed, model):
    r = random.random() * math.pi * 2
    new_x = max(min(x + math.cos(r) * speed, model.space.x_max), model.space.x_min)
    new_y = max(min(y + math.sin(r) * speed, model.space.y_max), model.space.y_min)

    return new_x, new_y


class Villager(mesa.Agent):
    def __init__(self, x, y, speed, unique_id: int, model: Village, lycanthrope=False):
        super().__init__(unique_id, model)
        self.pos = (x, y)
        self.speed = speed
        self.model = model
        self.lycanthrope = lycanthrope
        self.transforme = False


    def portrayal_method(self):
        color = "blue"
        r = 3
        if self.lycanthrope:
            color = "red"
        if self.transforme:
            r = 6
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Layer": 1,
                     "Color": color,
                     "r": r}
        return portrayal

    def step(self):
        if self.lycanthrope and random.random() < 0.1 and not(self.transforme):        
            self.transforme = True
        if self.transforme:
            attacked = [  other for other in self.model.schedule.agents if 
                type(other)==Villager and not(other.transforme) and
                math.sqrt( 
                    (other.pos[0]-self.pos[0])**2 + (other.pos[1]-self.pos[1])**2
                )<= 40
            ]
            if len(attacked) >0:
                idx = random.randint(0,len(attacked)-1)
                attacked[idx].lycanthrope = True


        self.pos = wander(self.pos[0], self.pos[1], self.speed, self.model)

class Cleric(mesa.Agent):
    def __init__(self, x, y, speed, unique_id: int, model: Village):
        super().__init__(unique_id, model)
        self.pos = (x, y)
        self.speed = speed
        self.model = model
    def portrayal_method(self):
        color = "green"
        r = 3
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Layer": 1,
                     "Color": color,
                     "r": r}
        return portrayal
    def step(self):
        soin = [other for other in self.model.schedule.agents 
        if type(other)==Villager and not(other.transforme) and other.lycanthrope
        and math.sqrt((other.pos[0]-self.pos[0])**2+(other.pos[1]-self.pos[1])**2)<30 
        ]
        if len(soin) >0:
            idx = random.randint(0,len(soin)-1)
            soin[idx].lycanthrope =True

        self.pos = wander(self.pos[0], self.pos[1], self.speed, self.model)

class Hunter(mesa.Agent):
    def __init__(self, x, y, speed, unique_id: int, model: Village):
        super().__init__(unique_id, model)
        self.pos = (x, y)
        self.speed = speed
        self.model = model
    def portrayal_method(self):
        color = "black"
        r = 3
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Layer": 1,
                     "Color": color,
                     "r": r}
        return portrayal
    def step(self):
        hunted = [other for other in self.model.schedule.agents 
            if type(other)==Villager and other.transforme 
            and math.sqrt((other.pos[0]-self.pos[0])**2+(other.pos[1]-self.pos[1])**2)<40
        ]
        if len(hunted)>0:
            idx = random.randint(0,len(hunted)-1)
            self.model.schedule.remove(hunted[idx])
        self.pos = wander(self.pos[0], self.pos[1], self.speed, self.model)


def run_single_server():
    server = ModularServer(Village,
                           [ContinuousCanvas(),
                           ChartModule(
                                    [   {"Label":"Humains","Color":"blue"},
                                        {"Label":"Werewolves","Color":"red"},
                                        {"Label":"lycanthropes","Color":"orange"},
                                        {"Label":"Population","Color":"yellow"}
                                    ],
                                    data_collector_name="datacollector"
                                    ),
                           
                           ],
                           "Village",
                           {"n_villagers":  UserSettableParameter('slider','Nombre initial de villageois sains',22,15,50,1),
                           "n_lycanthropes":UserSettableParameter('slider','Nombre initial de lycanthropes',5,2,10,1),
                           "n_clerics":UserSettableParameter('slider','Nombre initial de apothicaires',1,1,10,1),
                           "n_hunters":UserSettableParameter('slider','Nombre initial de chasseurs',2,2,10,1),
                           })
    server.port = 8521
    server.launch()
    tornado.ioloop.IOLoop.current().stop()
def run_batch():
    var_params = {
        "n_clerics": range(0,6,1),
    }
    fix_params= {"n_villagers":50,"n_lycanthropes":5,"n_hunters":1}
    batchrunner = BatchRunner(  model_cls=Village, 
                                variable_parameters=var_params,
                                fixed_parameters=fix_params,
                                iterations=1,
                                model_reporters={
                                                "Humains": lambda model: len([agent for agent in model.schedule.agents if type(agent)==Villager and not(agent.lycanthrope) ]),
                                                "Werewolves" : lambda model : len([agent for agent in model.schedule.agents if type(agent)==Villager and agent.transforme]),
                                                "lycanthropes" : lambda model : len([agent for agent in model.schedule.agents if type(agent)==Villager and agent.lycanthrope]),
                                                "Population" : lambda module : len(module.schedule.agents), 
                                            }
                            )
    batchrunner.run_all()
    df = batchrunner.get_model_vars_dataframe()
    df.to_csv('experience.csv')
    print(df)
    return df
def run_batchMP():
    var_params = {
        "n_clerics": list(range(0,6,1)),
        "n_villagers": list(range(20,50,5)),
        "n_lycanthropes": list(range(2,10,1)),
        "n_hunters": list(range(1,10,1))

    }
    batchrunner = BatchRunner(  model_cls=Village,
                                variable_parameters=var_params,
                                fixed_parameters=None,
                                iterations=1,
                                model_reporters={
                                                "Humains": lambda model: len([agent for agent in model.schedule.agents if type(agent)==Villager and not(agent.lycanthrope) ]),
                                                "Werewolves" : lambda model : len([agent for agent in model.schedule.agents if type(agent)==Villager and agent.transforme]),
                                                "lycanthropes" : lambda model : len([agent for agent in model.schedule.agents if type(agent)==Villager and agent.lycanthrope]),
                                                "Population" : lambda module : len(module.schedule.agents), 
                                            }
                            )
    batchrunner.run_all()
    df = batchrunner.get_model_vars_dataframe()
    df.to_csv('experience2.csv')
    print(df)
    return df






if __name__ == "__main__":
    run_single_server()
    # run_batch()
    #run_batchMP()
