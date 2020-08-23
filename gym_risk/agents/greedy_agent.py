import random
from gym_risk.agents.base_agent import BaseAgent
from gym_risk.board import Board

class GreedyAgent(BaseAgent):
    '''
    A Greedy agent
    '''

    def make_attack_decision(self,board: Board, attack_count: int) -> (str, str):
        attack_edges = board.get_all_player_attacks(self.id)
        if len(attack_edges) > 0:
            random.shuffle(attack_edges)
            return attack_edges[0]
        else: 
            pass

    def make_reinforce_decision(self, board: Board, bonus: int):    
        ### Dump all reinforcements into a single territory
        try:
            node_list = board.get_all_bordering_nodes(self.id)
            random.shuffle(node_list)
            return [node_list[0]] * bonus
        except IndexError:
            print(board.graph)
            print(bonus)
            print(node_list)
            board.show_board()


