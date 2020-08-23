from enum import Enum
from typing import Optional, List
import gym

from gym_risk.agents.base_agent import BaseAgent
from gym_risk.board import Board


class RiskEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, 
                num_players: int=2,
                agents: Optional[List[BaseAgent]]=None):

        self.num_players = num_players
        self.board = Board(agents=agents, num_players=self.num_players)
        self.phase = Phase.TURN_IN_CARDS
        self.current_player_id = 0
        pass

    def take_turn(self):
        """
        Parameters
        ----------
        action :

        Returns
        -------
        ob, reward, episode_over, info : tuple
            ob (object) :
                an environment-specific object representing your observation of
                the environment.
            reward (float) :
                amount of reward achieved by the previous action. The scale
                varies between environments, but the goal is always to increase
                your total reward.
            episode_over (bool) :
                whether it's time to reset the environment again. Most (but not
                all) tasks are divided up into well-defined episodes, and done
                being True indicates the episode has terminated. (For example,
                perhaps the pole tipped too far, or you lost your last life.)
            info (dict) :
                 diagnostic information useful for debugging. It can sometimes
                 be useful for learning (for example, it might contain the raw
                 probabilities behind the environment's last state change).
                 However, official evaluations of your agent are not allowed to
                 use this for learning.
        """
        current_agent = self.board.agents[self.current_player_id]

        self.turn_in_cards_phase(current_agent)
        self.reinforce_phase(current_agent)
        self.attack_phase(current_agent)
        self.tactical_move_phase(current_agent)
        self.draw_card_phase(current_agent)

    def attack_phase(self,agent):
        while self.phase == Phase.ATTACK:
            attack = agent.make_attack_decision(self.board)
            if attack is not None:
                country_1 = self.board.graph.nodes[attack[0]]
                country_2 = self.board.graph.nodes[attack[1]]
                self.board.try_attack(country_1, country_2, agent.id)
            else:
                self.phase = Phase.TACTICAL_MOVE
        pass

    def reinforce_phase(self, agent):
        self.phase = Phase.ATTACK
        pass

    def turn_in_cards_phase(self, agent):
        self.phase = Phase.REINFORCE
        pass

    def tactical_move_phase(self, agent):
        self.phase = Phase.DRAW_CARD
        pass

    def draw_card_phase(self, agent):
        self.current_player_id = (self.current_player_id + 1 % self.num_players)
        self.phase = Phase.TURN_IN_CARDS
        pass

    def reset(self):
        pass

    def render(self, mode='human', close=False):
        pass

    def take_action(self, action):
        pass

    def get_reward(self):
        """ Reward is given for XY. """
        return 0

# creating enumerations using class 
class Phase(Enum): 
    TURN_IN_CARDS = 1 
    REINFORCE = 2
    ATTACK = 3
    TACTICAL_MOVE = 4
    DRAW_CARD = 5