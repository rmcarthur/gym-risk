import random
from gym_risk.agents.base_agent import BaseAgent
from gym_risk.board import Board

class GreedyAgent(BaseAgent):
    '''
    A Greedy agent
    '''

    def make_attack_decision(self,board: Board) -> (str, str):
        attack_nodes = board.get_all_possible_attacks()
        if len(attack_nodes > 0):
            attack_edge = random.shuffle(attack_nodes)[0]
        return attack_edge


