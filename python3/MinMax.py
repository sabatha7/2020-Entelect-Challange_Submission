from Player import Player
from Position import Position
from Enums import BlockObject, State, Commands, Direction
from AStar import AStar
from Tree import Tree
import copy

def itemize_command(command):
    if command == Commands.USE_BOOST: return "BOOST"
    if command == Commands.USE_OIL: return "OIL"
    if command == Commands.USE_TWEET: return "TWEET"
    if command == Commands.USE_LIZARD: return "LIZARD"
    if command == Commands.USE_EMP: return "EMP"
    return None

speeds = {}
speeds[0]=Tree(None, 3)
speeds[3]=Tree(0, 5)
speeds[5]=Tree(3, 6)
speeds[6]=Tree(5, 8)
speeds[8]=Tree(6, 9)
speeds[9]=Tree(8, None)

speed_bracket = {}
speed_bracket[5]= 0
speed_bracket[4]= 3
speed_bracket[3]= 6
speed_bracket[2]= 8
speed_bracket[1]= 9
speed_bracket[0]= 15

# TODO:: here and there and keep pushing
class MinMax:
    def __init__(self):pass

    def compute_wall_damages(self, obstacles, player_info):

        speed = 0 + player_info.speed
        for i in obstacles:
            
            player_info.damage += 1 if not player_info.damage >= 5 else 0
            if i == BlockObject.OIL_SPILL:score -= 4
            if i == BlockObject.MUD:
                player_info.boosting = False
                s = speed
                prev_speed = speeds[speed].left
                speed = 3 if not prev_speed else prev_speed
            if i == BlockObject.WALL:
                player_info.boosting = False
                speed = 3
                player_info.damage += 1 if not player_info.damage >= 5 else 0

            if not i == BlockObject.WALL and not i == BlockObject.MUD and not i == BlockObject.OIL_SPILL:
                player_info.damage += 1 if not player_info.damage >= 5 else 0
                speed = 3

        player_info.speed = speed
        return 0

    def compute_fix(player_info):
        
        max_ = speed_bracket[player_info.damage]
        if player_info.damage > 0:

            return 15 - max_

        return -25
            

    def fix(self
            , action
            , game_map
            , player_info):

        if action == Commands.FIX:

            y = player_info.position.y
            if not y in game_map.keys():
                return {"player_info": player_info
                        , "game_map": game_map
                        , "progression": False
                        , "additional_score": -10000}

            additional_score = -10000 if player_info.damage == 0 else self.compute_fix(player_info)
            
            damage = player_info.damage - 2 if player_info.damage > 1 else 0
            player_info.damage = damage
            x = player_info.position.x + player_info.speed - 1
            progress = True
            
            if not x in game_map[y].keys():
                progress = False
                return {"player_info": player_info
                        , "game_map": game_map
                        , "progression": progress
                        , "additional_score": additional_score}
            
            return {"player_info": player_info
                    , "game_map": game_map
                    , "progression": progress
                    , "additional_score": additional_score}


    def do_nothing(self
                   , action
                   , game_map
                   , player_info):
        
        if action == Commands.NOTHING:

            max_ = speed_bracket[player_info.damage]
            y = player_info.position.y
            x = player_info.position.x + player_info.speed
            progress = True # goes deeper into the game tree?
            if not x in game_map[y].keys():
                x = [i for i in game_map[y].keys()][-1]
                progress = False
            a = AStar()
            path = a.forward(player_info.position, Position(y, x), game_map)

            p_speed = 0 # plaussible speeds
            if not player_info.boosting:
                if "BOOST" in player_info.power_ups:
                    p_speed = max_ - player_info.speed
            else:
                n_speed = 15 if player_info.boosting else speeds[player_info.speed].right
                p_speed = n_speed if n_speed else player_info.speed

            score = 0

            score -= abs((player_info.position.x + player_info.speed) - (player_info.position.x + p_speed))
            score -= abs((player_info.position.x + player_info.speed) - [i for i in game_map[y].keys()][-1])

            # walking the paths to collect damages/speed-deduction and points
            path_walk = self.walk_path(path, game_map, is_lizard=False)
            score += len(path_walk["powerups"]) *4 # <-- actually using of powerups will justify this more
            score += self.compute_wall_damages(path_walk["obstacles"], player_info)
            player_info.power_ups+=path_walk["powerups"]
            
            if progress:player_info.position=Position(y, x)
            return {"player_info": player_info
                    , "game_map": game_map
                    , "progression": progress
                    , "additional_score": score}


    def use_boost(self
                  , action
                  , game_map
                  , player_info):

        max_ = speed_bracket[player_info.damage]
        if action == Commands.USE_BOOST:

            if not itemize_command(action) in player_info.power_ups:
                
                return {"player_info": player_info
                    , "game_map": game_map
                    , "progression": False
                    , "additional_score": -1000}
            score = 0
            if max_ < 15: score -= (15 - max_)*5 # <-- soup
            if True:
                
                score+= 4
                if player_info.boosting: score -= 4
                player_info.power_ups.remove(itemize_command(action))
                player_info.speed = 15
                player_info.boosting = True
            y = player_info.position.y
            x = player_info.position.x + player_info.speed
            progress = True # goes deeper into the game tree?
            if not x in game_map[y].keys():
                x = [i for i in game_map[y].keys()][-1]
                progress = False
            a = AStar()
            path = a.forward(player_info.position, Position(y, x), game_map)

            p_speed = max_ # plaussible speeds

            score -= abs((player_info.position.x + player_info.speed) - (player_info.position.x + p_speed))
            score -= abs((player_info.position.x + player_info.speed) - [i for i in game_map[y].keys()][-1])

            # walking the paths to collect damages/speed-deduction and points
            path_walk = self.walk_path(path, game_map, is_lizard=False)
            score += len(path_walk["powerups"]) *4 # <-- actually using of powerups will justify this more
            score += self.compute_wall_damages(path_walk["obstacles"], player_info)
            player_info.power_ups+=path_walk["powerups"]
            
            if progress:player_info.position=Position(y, x)
            return {"player_info": player_info
                    , "game_map": game_map
                    , "progression": progress
                    , "additional_score": score}

    def use_lizard(self
                   , action
                   , game_map
                   , player_info):

        max_ = speed_bracket[player_info.damage]
        if action == Commands.USE_LIZARD:

            if not itemize_command(action) in player_info.power_ups:
                
                return {"player_info": player_info
                    , "game_map": game_map
                    , "progression": False
                    , "additional_score": -1000}

            y = player_info.position.y
            x = player_info.position.x + player_info.speed
            progress = True # goes deeper into the game tree?
            if not x in game_map[y].keys():
                x = [i for i in game_map[y].keys()][-1]
                progress = False
            a = AStar()
            path = a.forward(player_info.position, Position(y, x), game_map)

            p_speed = 0 # plaussible speeds
            if not player_info.boosting:
                if "BOOST" in player_info.power_ups:
                    p_speed = max_ - player_info.speed
            else:
                n_speed = max_ if player_info.boosting else speeds[player_info.speed].right
                p_speed = n_speed if n_speed else player_info.speed

            score = 0

            if True:
                
                score+= 4
                player_info.power_ups.remove(itemize_command(action))

            score -= abs((player_info.position.x + player_info.speed) - (player_info.position.x + p_speed))
            score -= abs((player_info.position.x + player_info.speed) - [i for i in game_map[y].keys()][-1])

            # walking the paths to collect damages/speed-deduction and points
            path_walk = self.walk_path(path, game_map, is_lizard=True)
            score += len(path_walk["powerups"]) *4 # <-- actually using of powerups will justify this more
            score += self.compute_wall_damages(path_walk["obstacles"], player_info)
            player_info.power_ups+=path_walk["powerups"]
            
            if progress:player_info.position=Position(y, x)
            return {"player_info": player_info
                    , "game_map": game_map
                    , "progression": progress
                    , "additional_score": score}

    def turn_left(self
                  , action
                  , game_map
                  , player_info):

        max_ = speed_bracket[player_info.damage]
        if action == Commands.TURN_LEFT:

            y = player_info.position.y - 1
            if not y in game_map.keys() or max_ == 0:
                return {"player_info": player_info
                        , "game_map": game_map
                        , "progression": False
                        , "additional_score": -10000}
            x = player_info.position.x + player_info.speed - 1
            progress = True
            if not x in game_map[y].keys():
                x = [i for i in game_map[y].keys()][-1]
                progress = False
            a = AStar()
            path = a.forward(player_info.position, Position(y, x), game_map)

            p_speed = 0 # plaussible speeds
            if not player_info.boosting:
                if "BOOST" in player_info.power_ups:
                    p_speed = max_ - player_info.speed - 1
            else:
                n_speed = max_ if player_info.boosting else speeds[player_info.speed].right
                p_speed = n_speed - 1 if n_speed else player_info.speed - 1

            score = 0

            score -= abs((player_info.position.x + player_info.speed) - (player_info.position.x + p_speed))
            score -= abs((player_info.position.x + player_info.speed) - [i for i in game_map[y].keys()][-1])

            # walking the paths to collect damages/speed-deduction and points
            path_walk = self.walk_path(path, game_map, is_lizard=False)
            score += len(path_walk["powerups"]) *4 # <-- actually using of powerups will justify this more
            score += self.compute_wall_damages(path_walk["obstacles"], player_info)
            player_info.power_ups+=path_walk["powerups"]
            
            if progress:player_info.position=Position(y, x)
            return {"player_info": player_info
                    , "game_map": game_map
                    , "progression": progress
                    , "additional_score": score}

    def turn_right(self
                  , action
                  , game_map
                  , player_info):

        max_ = speed_bracket[player_info.damage]
        if action == Commands.TURN_RIGHT:

            y = player_info.position.y + 1
            if not y in game_map.keys() or max_ == 0:
                return {"player_info": player_info
                        , "game_map": game_map
                        , "progression": False
                        , "additional_score": -10000}
            x = player_info.position.x + player_info.speed - 1
            progress = True
            if not x in game_map[y].keys():
                x = [i for i in game_map[y].keys()][-1]
                progress = False
            a = AStar()
            path = a.forward(player_info.position, Position(y, x), game_map)

            p_speed = 0 # plaussible speeds
            if not player_info.boosting:
                if "BOOST" in player_info.power_ups:
                    p_speed = max_ - player_info.speed - 1
            else:
                n_speed = max_ if player_info.boosting else speeds[player_info.speed].right
                p_speed = n_speed - 1 if n_speed else player_info.speed - 1

            score = 0

            score -= abs((player_info.position.x + player_info.speed) - (player_info.position.x + p_speed))
            score -= abs((player_info.position.x + player_info.speed) - [i for i in game_map[y].keys()][-1])

            # walking the paths to collect damages/speed-deduction and points
            path_walk = self.walk_path(path, game_map, is_lizard=False)
            score += len(path_walk["powerups"]) *4 # <-- actually using of powerups will justify this more
            score += self.compute_wall_damages(path_walk["obstacles"], player_info)
            player_info.power_ups+=path_walk["powerups"]
            
            if progress:player_info.position=Position(y, x)
            return {"player_info": player_info
                    , "game_map": game_map
                    , "progression": progress
                    , "additional_score": score}

    def accelerate(self
                  , action
                  , game_map
                  , player_info):

        max_ = speed_bracket[player_info.damage]
        if action == Commands.ACCELERATE:

            n_speed = None
            if not player_info.boosting:
                n_speed = speeds[player_info.speed].right
            if player_info.boosting or not n_speed or n_speed > max_:
                
                return {"player_info": player_info
                    , "game_map": game_map
                    , "progression": None
                    , "additional_score": -1000}
            player_info.speed = n_speed
            y = player_info.position.y
            x = player_info.position.x + n_speed
            progress = True # goes deeper into the game tree?
            if not x in game_map[y].keys():
                
                x = [i for i in game_map[y].keys()][-1]
                progress = False
            a = AStar()
            path = a.forward(player_info.position, Position(y, x), game_map)

            p_speed = 0 # plaussible speeds
            if not player_info.boosting:
                if "BOOST" in player_info.power_ups:
                    p_speed = max_ - player_info.speed
            else: p_speed = n_speed

            score = 0

            score -= abs((player_info.position.x + n_speed) - (player_info.position.x + p_speed))
            score -= abs((player_info.position.x + n_speed) - [i for i in game_map[y].keys()][-1])

            # walking the paths to collect damages/speed-deduction and points
            path_walk = self.walk_path(path, game_map, is_lizard=False)
            score += len(path_walk["powerups"]) *4 # <-- actually using of powerups will justify this more
            score += self.compute_wall_damages(path_walk["obstacles"], player_info)
            player_info.power_ups+=path_walk["powerups"]
            
            if progress:player_info.position=Position(y, x)
            return {"player_info": player_info
                    , "game_map": game_map
                    , "progression": progress
                    , "additional_score": score}

    def decelerate(self
                  , action
                  , game_map
                  , player_info):

        max_ = speed_bracket[player_info.damage]
        if action == Commands.DECELERATE:

            prev_speed = None
            if not player_info.boosting:
                prev_speed = speeds[player_info.speed].left
            if player_info.boosting or not prev_speed or player_info.damage > 0:
                
                return {"player_info": player_info
                    , "game_map": game_map
                    , "progression": None
                    , "additional_score": -1000}
            y = player_info.position.y
            x = player_info.position.x + prev_speed
            progress = True # goes deeper into the game tree?
            if not x in game_map[y].keys():
                
                x = [i for i in game_map[y].keys()][-1]
                progress = False
            a = AStar()
            path = a.forward(player_info.position, Position(y, x), game_map)

            p_speed = 0 # plaussible speeds
            if not player_info.boosting:
                if "BOOST" in player_info.power_ups:
                    p_speed = max_ - prev_speed
            else:
                n_speed = speeds[player_info.speed].right
                p_speed = n_speed - prev_speed if n_speed else player_info.speed
            player_info.speed = prev_speed

            score = 0

            score -= abs((player_info.position.x + prev_speed) - (player_info.position.x + p_speed))
            score -= abs((player_info.position.x + prev_speed) - [i for i in game_map[y].keys()][-1])

            # walking the paths to collect damages/speed-deduction and points
            path_walk = self.walk_path(path, game_map, is_lizard=False)
            score += len(path_walk["powerups"]) *4 # <-- actually using of powerups will justify this more
            score += self.compute_wall_damages(path_walk["obstacles"], player_info)
            player_info.power_ups+=path_walk["powerups"]
            
            if progress:player_info.position=Position(y, x)
            return {"player_info": player_info
                    , "game_map": game_map
                    , "progression": progress
                    , "additional_score": score}

    def new_virtual_actions(self
                          , action
                          , game_map
                          , player_info, depth):
        
        if player_info.speed == 0 or depth >= 2:
            
            y = player_info.position.y
            x = player_info.position.x
            dist = abs(x - [i for i in game_map[y].keys()][-1])
            return {"player_info": player_info
                    , "game_map": game_map
                    , "progression": False
                    , "additional_score": -dist}

        if action == Commands.NOTHING: return self.do_nothing(action, game_map, player_info)
        if action == Commands.ACCELERATE: return self.accelerate(action, game_map, player_info)
        if action == Commands.DECELERATE: return self.decelerate(action, game_map, player_info)
        if action == Commands.USE_BOOST: return self.use_boost(action, game_map, player_info)
        if action == Commands.USE_LIZARD: return self.use_lizard(action, game_map, player_info)
        if action == Commands.TURN_LEFT: return self.turn_left(action, game_map, player_info)
        if action == Commands.TURN_RIGHT: return self.turn_right(action, game_map, player_info)
        if action == Commands.FIX: return self.fix(action, game_map, player_info)

        return {"player_info": player_info
                , "game_map": game_map
                , "progression": False
                , "additional_score": -10000}

    def walk_path(self, path, game_map, is_turning=False, is_lizard=False):
        
        result = {}
        result["powerups"] = []
        result["obstacles"] = []
        result["dodged"] = {}
        result["dodged"]["obstacles"] = []
        result["dodged"]["powerups"] = []
        
        path = path.reverse() if is_turning else path
        size = len(path)
        count = 0
        for i in path:

            count += 1
            if is_lizard and count < size:

                if BlockObject(game_map[i.y][i.x]["surfaceObject"]).value>4:
                    result["dodged"]["powerups"].append(
                        BlockObject(game_map[i.y][i.x]["surfaceObject"]))
                if 1>BlockObject(game_map[i.y][i.x]["surfaceObject"]).value<5:
                    result["dodged"]["obstacles"].append(
                        BlockObject(game_map[i.y][i.x]["surfaceObject"]))
                continue #<-- soup
            if BlockObject(game_map[i.y][i.x]["surfaceObject"]).value>4:
                result["powerups"].append(
                    BlockObject(game_map[i.y][i.x]["surfaceObject"]))
            if 1>BlockObject(game_map[i.y][i.x]["surfaceObject"]).value<5:
                result["obstacles"].append(
                    BlockObject(game_map[i.y][i.x]["surfaceObject"]))
        return result

        
    def forward(self, game_map, player_info, action, depth=0):

        #best_score = -10000
        info = copy.deepcopy(player_info)

        result = self.new_virtual_actions(action, game_map, info, depth)
        return result
