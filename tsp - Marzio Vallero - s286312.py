# -*- coding: utf-8 -*-
"""
Original copyright notice on which the code is based:

Copyright **`(c)`** 2021 Giovanni Squillero `<squillero@polito.it>`  
[`https://github.com/squillero/computational-intelligence`](https://github.com/squillero/computational-intelligence)  
Free for personal or classroom use; see 'LICENCE.md' for details.
"""

from math import sqrt
from typing import Any
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

class Tsp:

    def __init__(self, num_cities: int, seed: Any = None) -> None:
        if seed is None:
            seed = num_cities
        self._num_cities = num_cities
        self._graph = nx.DiGraph()
        np.random.seed(seed)
        for c in range(num_cities):
            self._graph.add_node(c, pos=(np.random.random(), np.random.random()))

    def distance(self, n1, n2) -> int:
        pos1 = self._graph.nodes[n1]['pos']
        pos2 = self._graph.nodes[n2]['pos']
        return round(1_000_000 / self._num_cities * sqrt((pos1[0] - pos2[0])**2 +
                                                         (pos1[1] - pos2[1])**2))

    def evaluate_solution(self, solution: np.array) -> float:
        total_cost = 0
        tmp = solution.tolist() + [solution[0]]
        for n1, n2 in (tmp[i:i + 2] for i in range(len(tmp) - 1)):
            total_cost += self.distance(n1, n2)
        return total_cost

    def plot(self, path: np.array = None) -> None:
        if path is not None:
            self._graph.remove_edges_from(list(self._graph.edges))
            tmp = path.tolist() + [path[0]]
            for n1, n2 in (tmp[i:i + 2] for i in range(len(tmp) - 1)):
                self._graph.add_edge(n1, n2)
        plt.figure(figsize=(12, 5))
        nx.draw(self._graph,
                pos=nx.get_node_attributes(self._graph, 'pos'),
                with_labels=True,
                node_color='pink')
        if path is not None:
            plt.title(f"Current path: {self.evaluate_solution(path):,}")
        plt.show()

    def get_partial_solution(self, solution: np.array) -> np.array:
      new_solution = solution.copy()
      for pos in range(NUM_CITIES):
          current_best = None
          tmp = new_solution.tolist()
          for n2 in (tmp[i] for i in range(pos+1, len(tmp))):
              candidate = self.distance(tmp[pos], n2)
              if current_best == None or (candidate < current_best) :
                current_best = n2
          if(current_best != None):
            new_solution[pos] = current_best
      return new_solution

    @property
    def graph(self) -> nx.digraph:
        return self._graph

NUM_CITIES = 42

problem = Tsp(NUM_CITIES)
problem.plot()

def tweak(solution: np.array, *, pm: float = 1/NUM_CITIES) -> np.array:
    new_solution = solution.copy()
    p = None
    iter = 0
    while p is None or p < pm:
        i1 = np.random.randint(0, NUM_CITIES)
        i2 = np.random.randint(0, NUM_CITIES)
        temp = new_solution[i1]
        new_solution[i1] = new_solution[i2]
        new_solution[i2] = temp
        p = np.random.random()
    return new_solution


def hybridTweak(solution: np.array, *, pm: float = 1/NUM_CITIES) -> np.array:
    new_solution = solution.copy()
    p = None
    while p is None or p < pm:
        i1 = np.random.randint(0, NUM_CITIES)
        i2 = np.random.randint(0, NUM_CITIES)
        mi = min(i1, i2)
        ma = max(i1, i2)
        if(ma - mi == 0):
            p = 0
        elif (ma - mi == 1):
            temp = new_solution[i1]
            new_solution[i1] = new_solution[i2]
            new_solution[i2] = temp
            p = np.random.random()
        else:
            temp = new_solution[mi+1:ma]
            revs = temp[::-1]
            temp2 = new_solution[ma]
            new_solution[mi+2:mi+2+len(revs)] = revs
            new_solution[mi+1] = temp2
            p = np.random.random()
    return new_solution

def plot_history(history):
    plt.figure(figsize=(12, 5))
    x, y = zip(*history)
    plt.plot(x, y)
    plt.xlabel("# Steps")
    plt.ylabel("Cost")
    plt.show()

STEADY_STATE = 1000

solution = np.array(range(NUM_CITIES))
np.random.shuffle(solution)
solution_cost = problem.evaluate_solution(solution)
problem.plot(solution)
history = [(0, solution_cost)]
steady_state = 0
step = 0
while steady_state < STEADY_STATE:
    step += 1
    steady_state += 1
    new_solution = hybridTweak(solution)
    new_solution_cost = problem.evaluate_solution(new_solution)
    if new_solution_cost < solution_cost:
        solution = new_solution
        solution_cost = new_solution_cost
        history.append((step, solution_cost))
        steady_state = 0
problem.plot(solution)
plot_history(history)
