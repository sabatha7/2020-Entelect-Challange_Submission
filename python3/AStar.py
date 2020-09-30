from hashlib import sha256
from Position import Position
import math

directions = []
directions.append([1,0]) #go up by 1
directions.append([-1,0]) # go down by 1
directions.append([0,1]) # go right by 1
directions.append([0,-1]) # go left by 1

def compute_hash(obj):
    #string = json.dumps(obj.__dict__, cls=ComplexEncoder, sort_keys=True)
    string="{}{}".format(obj.y, obj.x)
    return sha256(string.encode()).hexdigest()

class AStar:
    def __init__(self):pass

    # heuristic cost estimate
    def h(self, start, goal):return abs(start.x - goal.x) + abs(start.y - goal.y)

    # distance between
    def d(self, start, goal):
        
        return math.sqrt(pow((start.x - goal.x),2) + pow((start.y - goal.y),2));

    def get_neigbors(self, position, game_map):
        
        n = [Position(position.y+i[0], position.x+i[1]) for i in directions]
        nn = []
        for i in n:
            if i.y in game_map.keys():
                if i.x in game_map[i.y].keys(): nn.append(i)
        return nn
        
    def get_min_by_f(self, a_set, f_score_set):
        
        min_ = a_set[0]
        for i in a_set:
            if (f_score_set[compute_hash(i)] < f_score_set[compute_hash(min_)]):
                min_ = i
        return min_ 
    
    def reconstruct_path(self, came_from, goal):
        
        total_path = []
        while compute_hash(goal) in came_from.keys():
            goal = came_from[compute_hash(goal)]
            total_path.append(goal)
        return total_path
            

    def forward(self, start, goal, game_map):

        open_set = [start]
        closed_set = []
        came_from = {}
        g_score = {} # the cost of going from start to start is zero
        g_score[compute_hash(start)] = 0 # measures from start to current location
        f_score = {}
        f_score[compute_hash(start)] = self.h(start, goal)
        #some soup
        last_visited = start

        while len(open_set) > 0:
            # the point in "open_set" having the lowest f_score value"
            current = self.get_min_by_f(open_set, f_score)
            if compute_hash(current) == compute_hash(goal):
                return self.reconstruct_path(came_from, current)
            open_set.remove(current)

            closed_set.append(compute_hash(current))
            for n in self.get_neigbors(current, game_map):
                if compute_hash(n) in closed_set: continue
                
                # d(current, n) is the weight of the edge from the current to
                # the neigbour
                # tentative_gScore is the distance from start to the neigbour
                # through current
                tg_score = g_score[compute_hash(current)] + self.d(current, n)
                # discover a new node
                if not n in open_set:open_set.append(n)
                # this is not a better path so ignore it
                elif tg_score > g_score[compute_hash(current)]:continue
                
                # this is the best path so record it
                came_from[compute_hash(n)] = current

                g_score[compute_hash(n)] = tg_score
                f_score[compute_hash(n)] = tg_score + self.h(n, goal)
        return self.reconstruct_path(came_from, last_visited)
