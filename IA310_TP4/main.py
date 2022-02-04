import math
import random
from typing import List

import agentspeak
import agentspeak.runtime
import agentspeak.stdlib
from agentspeak import Literal
import os

actions = agentspeak.Actions(agentspeak.stdlib.actions)

N_RESOURCES = 2

@actions.add_function('.ucb',(float,int,int))
def ucb(mu, ni, n):
    if n == 0:
        return 200
    elif ni == 0:
        return 200
    else:
        return mu/n + math.log(2*n/ni)


class Resource:
    def __init__(self, mu_anis, mu_bardane, quantity):
        self.mu_anis = mu_anis
        self.mu_bardane = mu_bardane
        self.quantity_anis = quantity
        self.quantity_bardane = quantity

    def exploit(self):
        anis = min(self.quantity_anis, random.triangular(0, 1, self.mu_anis))
        bardane = min(self.quantity_bardane, random.triangular(0, 1, self.mu_bardane))
        self.quantity_anis = self.quantity_anis - anis
        self.quantity_bardane = self.quantity_bardane - bardane
        return anis, bardane

    def __str__(self):
        return str(self.__dict__)


class ResourceEnvironment(agentspeak.runtime.Environment):
    resources: List[Resource]

    def __init__(self):
        super().__init__()
        self.resources = []
        for i in range(N_RESOURCES):
            self.resources.append(Resource(random.random(), random.random(), 15 + 5 * random.random()))
    
    @actions.add(".collect_ressources", 1) 
    def collect_ressources(self, term, intention):
        num_reg = int(term.args[0].evaluate(intention.scope))
        reso = self.env.resources[num_reg]
        anis,bardane = reso.exploit()

        anis_b = list(self.beliefs[('anis', 1)])[0].args[0] + anis
        bardane_b = list(self.beliefs[('blardone', 1)])[0].args[0] + bardane
        self.beliefs[('anis',1)] = {Literal('anis',[anis_b,])}
        self.beliefs[('blardone',1)] = {Literal('blardone',[bardane_b,])}
        yield

    @actions.add(".iteration_suiv", 0)
    def iteration_suiv(self, term, intention):
        self.beliefs[('iteration', 1)] = { 
            Literal('iteration', 
            [list(self.beliefs[('iteration', 1)])[0].args[0] + 1]) 
            }
        yield
    

    
env = ResourceEnvironment()

with open(os.path.join(os.path.dirname(__file__), "agent.asl")) as source:
    agents = env.build_agents(source, 5, actions)
with open(os.path.join(os.path.dirname(__file__), "agent2.asl")) as source2:
        agents+=[env.build_agent(source2,actions)]
for agent in agents:
    for i in range(N_RESOURCES):
        agent.beliefs[('values_r', 4)].add(Literal('values_r', [i, 0, 0, 0]))


if __name__ == "__main__":
    random.seed(0)
    env.run()