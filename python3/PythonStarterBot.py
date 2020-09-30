# -*- coding: utf-8 -*-
"""
Entelect StarterBot for Python3
"""
import copy
import math
import json
import os
import logging
import random
import numpy as np
from Lane import Lane
from Player import Player
from Position import Position
from Enums import BlockObject, State, Commands, Direction
from MinMax import MinMax
from ComplexEncoder import ComplexEncoder

logging.basicConfig(filename='sample_python_bot.log', filemode='w', level=logging.DEBUG)
logger = logging.getLogger(__name__)

seen_paths = {} # seen_path[hash]['obstacle_score']['powerup_score']
# aim _ to see who can get out of bounds towards the finish first with the most
# score and least amount of steps

class BFTree:
    def __init__(self, commands=[]):
        self.children = commands

    def append_result(self, existing, pending, depth=1):

        existing["bestAt{}".format(depth)] = pending
        return existing
        
    def solve(self, game_map, player_info, came_from=[], depth=0):
        
        agent = MinMax()
        result = {}
        result['anything-that-unsolved'] = []
        best = -10000
        action = None
        parent = None
        if len(came_from):
            
            for j in came_from:
                state = j

                for i in self.children:
                    v = agent.forward(game_map, state['pinfo'], i, depth)

                    if v['progression']:
                        result['anything-that-unsolved'].append({'pinfo':
                                                                 v['player_info'],
                                                                 'action': i})

                    if v['additional_score'] > best:
                        best = v['additional_score']
                        action = i
                        parent = j

            result['best'] = {'points': best,
                              'parent': parent,
                              'action': action
                              }
        else:
            
            for i in self.children:
                v = agent.forward(game_map, player_info, i)
                
                if v['progression']:
                    result['anything-that-unsolved'].append({'pinfo':
                                                             v['player_info'],
                                                             'action': i})

                if v['additional_score'] > best:
                    best = v['additional_score']
                    action = i
                    
            result['best'] = {'points': best,
                              'parent': None,
                              'action': action
                              }
        return result
                
                  
class StarterBot:

    def __init__(self, debug_mode=False):
        self.debug_mode = debug_mode
        """
        Initialize Bot .
        """
        self.max_speed = 9
        self.random_list = [-1, 1]

        self.current_round = None
        self.max_rounds = None
        self.command = ''
        self.map = None  # Array of lanes
        self.player_info = None  # Player object
        self.game_state = None
        self.raw_lanes = []
        self.raw_player = None

    def get_current_round_details(self):
        """
        Reads in all relevant information required for the tick.
        """
        path = os.path.join('JsonMap.json')
        true_path = os.path.join('rounds', str(self.current_round), 'state.json')
        state_location = path if self.debug_mode else true_path
        self.game_state = self.load_state_json(state_location)

        self.command = ''

        self.raw_lanes = self.game_state['worldMap']
        self.map = self.get_lanes()

        self.raw_player = self.game_state['player']
        self.player_info = self.get_player()

        self.current_round = self.game_state['currentRound']
        self.max_rounds = self.game_state['maxRounds']

        return None

    def get_player(self):
        player = Player(pid=self.raw_player['id'],
                        speed=self.raw_player['speed'],
                        state=State[self.raw_player['state']],
                        position=Position(self.raw_player['position']['y'],
                                          self.raw_player['position']['x']),
                        power_ups=self.raw_player['powerups'],
                        boosting=self.raw_player['boosting'],
                        boost_counter=self.raw_player['boostCounter'])
        return player

    def get_lanes(self):

        raw_lanes = {}
        for lane in self.raw_lanes:
            for cell in lane:
                
                raw_position = cell['position']
                if not raw_position['y'] in raw_lanes.keys():
                    raw_lanes[raw_position['y']] = {}
                raw_lanes[raw_position['y']][raw_position['x']] = cell

        return raw_lanes
    
    def get_list_map_structure(self):
        game_map = {}
        total_lanes = len(self.map)
        last_lane = self.map[total_lanes - 1]

        map_height = last_lane.position.lane
        map_width = int(total_lanes/map_height)

        for lane in range(1, map_height+1):
            blocks = []
            for block in range(0, map_width):
                blocks.append(self.map[((lane - 1) * map_width) + block])

            game_map[lane] = blocks

        return game_map
    
    def get_next_blocks(self, lane, block, max_speed):
        game_map = self.get_list_map_structure()
        block_types = []
        start_block = self.map[0].position.block
        lane_list = game_map[lane]

        for block in range(block - start_block, np.minimum(block - start_block + max_speed, len(lane_list))):
            if lane_list[block] is None:
                break
            block_types.append(lane_list[block].object)

        return block_types

    @staticmethod
    def change_lane_command(lane_indicator):
        direction = Direction.LEFT.value
        if lane_indicator == 1:
            direction = Direction.RIGHT.value
        return direction

    def starter_bot_logic(self):
        """
        Currently implemented logic :
        If there is a mud block in front of you, turn. Otherwise, accelerate.
        """
        next_blocks = self.get_next_blocks(self.player_info.position.lane, self.player_info.position.block, self.max_speed)

        if BlockObject.MUD in next_blocks:
            self.command = Commands.TURN.value + self.change_lane_command(random.choice(self.random_list))
        else:
            self.command = Commands.ACCELERATE.value

        return self.command

    def new_bot_logic(self):

        agent = MinMax()
        moves = [i for i in Commands]
        tree = BFTree(moves)
        # new new bot login
        c = copy.deepcopy(self.player_info)
        result = tree.solve(self.map
                            , c) # <-- soup
        r = 1
        while len(result['anything-that-unsolved']):
            temp = result['anything-that-unsolved']
            result = tree.append_result(result
                                        , BFTree(moves).solve(self.map, None, result['anything-that-unsolved']), r)
            r += 1
            result['anything-that-unsolved'] = [i for i in result['anything-that-unsolved'] if not i in temp]

        #print(result["best"]["action"])
                
        #print("{}|{}".format(result, i))          
        #self.command = Commands.NOTHING.value
        self.command = result["best"]["action"]
        return self.command

    def write_action(self):
        """
        command in form : C;<round number>;<command>
        """
        print(f'C;{self.current_round};{self.command}')
        logger.info(f'Writing command : C;{self.current_round};{self.command};')

        return None

    @staticmethod
    def load_state_json(state_location):
        """
        Gets the current Game State json file.
        """
        json_map = {}
        try:
            json_map = json.load(open(state_location, 'rt'))
        except IOError:
            logger.error("Cannot load Game State")
        return json_map

    @staticmethod
    def wait_for_round_start(debug_mode):
        round_no = 1
        next_round = round_no if debug_mode else int(input())
        return next_round

    def run_bot(self):
        logger.info("Bot has started Running")
        if self.debug_mode:
            for i in range(0, 1):
                logger.info('Waiting for next round.')
                next_round_number = self.wait_for_round_start(self.debug_mode)
                logger.info('Starting Round : ' + str(next_round_number))
                self.current_round = next_round_number
                self.get_current_round_details()
                logger.info('Beginning StarterBot Logic Sequence')
                #self.starter_bot_logic()
                self.new_bot_logic()
                self.write_action()
        else:
            while True: 
                logger.info('Waiting for next round.')
                next_round_number = self.wait_for_round_start(self.debug_mode)
                logger.info('Starting Round : ' + str(next_round_number))
                self.current_round = next_round_number
                self.get_current_round_details()
                logger.info('Beginning StarterBot Logic Sequence')
                #self.starter_bot_logic()
                self.new_bot_logic()
                self.write_action()

# dont forget unset debug_mode
if __name__ == '__main__':
    bot = StarterBot(False)
    bot.run_bot()
