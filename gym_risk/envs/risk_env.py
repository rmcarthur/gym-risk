import logging
from enum import Enum
from typing import Optional, List
import gym

from gym_risk.agents.base_agent import BaseAgent
from gym_risk.board import Board

logging.basicConfig(filename='riskLog.log', level=logging.INFO,filemode='w')

global MAX_ROUNDS
MAX_ROUNDS = 10000
class RiskEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, 
                num_players: int=2,
                agents: Optional[List[BaseAgent]]=None):

        self.num_players = num_players
        self.agents = agents
        self.episode_over = False
        self.board = Board(agents=self.agents, num_players=self.num_players)
        self.phase = Phase.TURN_IN_CARDS
        self.current_player_id = 0
        self.current_round = 0
        self.current_stage_count = 0
        self.reinforce_min = 3
        self.territory_counts = []
        logging.info("Began Env")
        pass

    def step(self):
        """
        Parameters
        ----------
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
        reward = 0
        info = {}
        while not self.episode_over:
            self.current_round += 1
            logging.info(f"Beginning round {self.current_round}")
            self.debug = False 
            if self.debug:
                self.board.show_board()
            for agent in self.agents:
                ## Check if game is over
                game_over, winner = self.board.game_over()
                if game_over:
                    self.episode_over = True
                    continue
                self.take_turn(agent)
            
            if self.current_round % 100 == 0:
                logging.info(f"On round {self.current_round}")
            # End after MAX_ROUNDS
            if self.current_round >= MAX_ROUNDS:
                self.episode_over = True

        info['rounds_played'] = self.current_round
        info['winner'] = winner
        return self.board.graph, reward, self.episode_over, info

    def take_turn(self, current_agent):
        logging.info(f"Begining Turn {self.current_round} for Player {self.current_player_id}")

        self.turn_in_cards_phase(current_agent)
        self.reinforce_phase(current_agent)
        self.attack_phase(current_agent)
        self.tactical_move_phase(current_agent)
        self.draw_card_phase(current_agent)

    def attack_phase(self,agent):
        logging.info("Beginning attack")
        self.current_stage_count = 0
        while self.phase == Phase.ATTACK:
            attack = agent.make_attack_decision(self.board, self.current_stage_count)
            logging.info(f"Attacking {attack}")
            if attack is not None:
                country_1 = self.board.graph.nodes[attack[0]]['id']
                country_2 = self.board.graph.nodes[attack[1]]['id']
                self.board.try_attack(country_1, country_2, agent)
                self.current_stage_count += 1 
            else:
                self.phase = Phase.TACTICAL_MOVE
        pass

    def reinforce_phase(self, agent):
        logging.info("Reinforcing")
        ## Get Total territories count
        nodes_controlled = len([i for i in self.board.graph.nodes(data='player_id') if i[1] == agent.id])
        bonus = max(3, nodes_controlled // 3)
        logging.info(f"Player {agent.id} has {nodes_controlled} territories and will receive {bonus} reinforcements")
        bonus_territories = agent.make_reinforce_decision(self.board, bonus)
        for t in bonus_territories:
            # Verify ownership
            assert self.board.graph.nodes[t]['player_id'] == agent.id
            logging.info(f"Adding 1 unit to {t} for player {agent.id}")
            self.board.graph.nodes[t]['units'] += 1
            logging.info(f"New total on {t} is {self.board.graph.nodes[t]['units']}")
        self.phase = Phase.ATTACK
        pass

    def turn_in_cards_phase(self, agent):
        logging.info("Turning in Cards")
        self.phase = Phase.REINFORCE
        pass

    def tactical_move_phase(self, agent):
        logging.info("Tactical Move")
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