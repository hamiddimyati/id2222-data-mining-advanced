import numpy as np
import random
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict

class edges:
    def __init__(self):
        self.edge_list = set()
        self.neighbour_list = {}
        self.n_edges = 0
        
    def insert(self, u, v):
        if u in self.neighbour_list.keys():
            self.neighbour_list[u].append(v)
        else:
            self.neighbour_list[u] = [v]
        
        if v in self.neighbour_list.keys():
            self.neighbour_list[v].append(u)
        else:
            self.neighbour_list[v] = [u]
        
        self.edge_list.add((u,v))
        self.n_edges += 1
        
    def delete(self, u, v):
        self.neighbour_list[u].remove(v)
        neighbour_u = self.neighbour_list[u]
        if len(neighbour_u) == 0:
            del self.neighbour_list[u]

        self.neighbour_list[v].remove(u)
        neighbour_v = self.neighbour_list[v]
        if len(neighbour_v) == 0:
            del self.neighbour_list[v]

        self.edge_list.remove((u,v))
        self.n_edges -= 1

class triestBase:
    def __init__(self, memory):
        self.memory = memory
        self.S = edges()
        self.global_counter = 0
        self.local_counter = defaultdict(lambda:0)
        
    def fit(self, graph_streaming):
        t = 0
        with open(graph_streaming) as f:
            next(f)
            lines = f.read().splitlines()
            for line in lines:
                u, v = sorted([int(e) for e in line.split(',')])
                t += 1
                if self.sample(t, u, v):
                    self.S.insert(u, v)
                    self.update_counter('+', u, v)
                    
        global_triangles = self.estimate_global_counter(t)
        
        return int(global_triangles)
                
    def sample(self, t, u, v):
        if t <= self.memory:
            return True
        else:
            if self.flip_coin(t):
                n_edges = self.S.n_edges
                index = random.randint(0, n_edges-1)
                u, v = random.sample(self.S.edge_list, 1)[0]
                self.S.delete(u,v)
                self.update_counter('-', u, v)
                return True
            else:
                return False
            
    def flip_coin(self, t):
        p_head = self.memory/t
        p = random.random()
        if p <= p_head:
            return True
        else:
            return False
        
    def update_counter(self, operation, u, v):
        vertices = self.S.neighbour_list.keys()
        if (u not in vertices) or (v not in vertices):
            return
        u_neighbours = self.S.neighbour_list[u]
        v_neighbours = self.S.neighbour_list[v]
        
        shared_neighbours = list(set(u_neighbours) & set(v_neighbours))
        n_shared_neighbours = len(shared_neighbours)
        
        if n_shared_neighbours == 0:
            return
        
        if operation == '+':
            self.global_counter +=  n_shared_neighbours
            self.local_counter[u] +=  n_shared_neighbours
            self.local_counter[v] +=  n_shared_neighbours

            for c in shared_neighbours:
                self.local_counter[c] += 1
        
        if operation == '-':
            self.global_counter -= n_shared_neighbours

            self.local_counter[u] -= n_shared_neighbours
            if self.local_counter[u] == 0:
                del self.local_counter[u]

            self.local_counter[v] -= n_shared_neighbours
            if self.local_counter[v] == 0:
                del self.local_counter[v]

            for c in shared_neighbours:
                self.local_counter[c] -= 1
            if self.local_counter[c] == 0:
                del self.local_counter[c]
                
    def estimate_global_counter(self, t):
        M = self.memory
        estimator = np.max([1, (t*(t-1)*(t-2))/(M*(M-1)*(M-2))])
        return estimator * self.global_counter

class triestImprove:
    def __init__(self, memory):
        self.memory = memory
        self.S = edges()
        self.global_counter = 0
        self.local_counter = defaultdict(lambda:0)
        self.t = 0
        
    def fit(self, graph_streaming):
        with open(graph_streaming) as f:
            next(f)
            lines = f.read().splitlines()
            for line in lines:
                u, v = sorted([int(e) for e in line.split(',')])
                self.t += 1
                #changes #1: moving update_counter before if block 
                self.update_counter('+', u, v)
                if self.sample(u, v):
                    self.S.insert(u, v)
                    
        global_triangles = self.global_counter
        
        return float(global_triangles)
                
    def sample(self, u, v):
        if self.t <= self.memory:
            return True
        else:
            if self.flip_coin():
                n_edges = self.S.n_edges
                index = random.randint(0, n_edges-1)
                u, v = random.sample(self.S.edge_list, 1)[0]
                self.S.delete(u,v)
                #changes #2: removing update_counter when an edge is removed from S 
                #self.update_counter('-', u, v)
                return True
            else:
                return False
            
    def flip_coin(self):
        p_head = self.memory/self.t
        p = random.random()
        if p <= p_head:
            return True
        else:
            return False
        
    def update_counter(self, operation, u, v):
        vertices = self.S.neighbour_list.keys()
        if (u not in vertices) or (v not in vertices):
            return
        u_neighbours = self.S.neighbour_list[u]
        v_neighbours = self.S.neighbour_list[v]
        
        shared_neighbours = list(set(u_neighbours) & set(v_neighbours))
        n_shared_neighbours = len(shared_neighbours)
        
        if n_shared_neighbours == 0:
            return
        
        #changes #3: performs a weighted increase of the counters 
        operator = int(max(1, ((self.t - 1) * (self.t - 2)) / (self.memory * (self.memory - 1))))
        
        for c in shared_neighbours:
            self.global_counter   += operator
            self.local_counter[u] += operator
            self.local_counter[v] += operator
            self.local_counter[c] += operator

if __name__ == '__main__':
    random.seed(333)
    filename = 'data/musae_git_edges.csv'
    
    def baseloop(M):
        graph_streaming = triestBase(M)
        global_triangles = graph_streaming.fit(filename)
        return global_triangles
    
    def improveloop(M):
        graph_streaming = triestImprove(M)
        global_triangles = graph_streaming.fit(filename)
        return global_triangles
    
    x=[int(element * 289003/10) for element in list(range(1,11))]
    #x = [1000*i for i in range(1,4)]
    y1=[]
    y2=[]
    for i in x:
        y1.append(baseloop(i))
        y2.append(improveloop(i))
        
    df=pd.DataFrame({'x': x, 'y1' : y1, 'y2' : y2})
    plt.plot('x', 'y1', '', data=df, marker='', color='skyblue', linewidth=2)
    plt.plot('x', 'y2', '', data=df, marker='', color='olive', linewidth=2)
    plt.legend()