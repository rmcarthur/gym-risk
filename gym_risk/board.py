import logging
import random
import json
from pathlib import Path
from collections import Counter
import networkx as nx
from typing import List,Optional
from matplotlib import pyplot as plt
import shapely as shp
import geopandas as gpd

from gym_risk.attack_utils import COLOR_MAP, single_roll 
from gym_risk.agents.base_agent import BaseAgent

class Board():
    metadata = {}
    def __init__(self, 
                agents: Optional[List[BaseAgent]]=None, 
                board: str='us_cont', 
                num_players: int=2):

        # Setup Agents
        self.agents = []  
        if agents is None:
            for i in range(num_players):
                self.agents.append(BaseAgent(id=i,color=COLOR_MAP[i]))
        else: 
            self.agents = agents
        assert len(self.agents) == num_players

        # read in graph
        graph_path = Path(__file__).parent / f"assets/{board}_graph.json"
        with graph_path.open() as json_file: 
            graph_data = json.load(json_file) 

        #Load in board
        self.graph = nx.node_link_graph(graph_data)
        
        # randomize and assign player board
        self.initialize_player_assignment()
        pass


    def initialize_player_assignment(self, starting_units=3):
        """Randomly assigns each player a country until there are none left"""
        num_players = len(self.agents)
        graph_nodes = list(self.graph.nodes)
        random.shuffle(graph_nodes)
        for j,i in enumerate(graph_nodes):
            self.graph.nodes[i]['player_id'] = self.agents[j%num_players].id
            self.graph.nodes[i]['player_color'] = self.agents[j%num_players].color
            self.graph.nodes[i]['units'] = starting_units
            self.graph.nodes[i]['id'] = i
     
    def change_ownership(self, payload):
        """Change ownership of a country
        Params: payload (dict) {node:player}
        """
        nx.set_node_attributes(self.graph, payload, "player")
        pass

    def get_all_player_nodes(self, agent_id: int):
        player_owned_nodes = [i[0] for i in self.graph.nodes(data='player_id') if i[1] == agent_id]
        return player_owned_nodes

    def get_all_bordering_nodes(self,agent_id: int):
        player_owned_nodes = self.get_all_player_nodes(agent_id)
        bordering_nodes = [i[0] for i in self.graph.edges(player_owned_nodes) if i[1] not in player_owned_nodes]
        return bordering_nodes
    
    def get_territory_counts(self):
        territory_counter = Counter()
        for i in self.graph.nodes(data='player_id'):
            territory_counter[i[1]] +=1
        return territory_counter

    def game_over(self):
        territory_counter = self.get_territory_counts()
        logging.info(f"Territory Counter: {territory_counter}")
        if max(territory_counter.values()) == self.graph.number_of_nodes():
            game_over = True
            winner = list(territory_counter.keys())[0]
        else: 
            game_over = False
            winner = None
        return game_over, winner


    # Get all possible moves
    def get_all_player_attacks(self,agent_id: int):
        player_owned_nodes = self.get_all_player_nodes(agent_id)
        units = [i[0] for i in self.graph.nodes(data='units') if i[1] > 1]
        player_possible_attack_nodes = [node for node in player_owned_nodes if node in units] 
        attack_edges = [i for i in self.graph.edges(player_possible_attack_nodes) if i[1] not in player_owned_nodes]
        return attack_edges

    def get_all_possible_attacks(self):
        player_owned_nodes = self.graph.nodes(data='player_id')
        units = [i[0] for i in self.graph.nodes(data='units') if i[1] > 1]
        player_possible_attack_nodes = [node[0] for node in player_owned_nodes if node[0] in units] 
        all_attacks = [i for i in self.graph.edges(player_possible_attack_nodes) if player_owned_nodes[i[0]] != player_owned_nodes[i[1]]]
        return all_attacks

    def try_attack(self, attack_id: str, defend_id: str, agent: BaseAgent):
        # Validate move is legal
        player_id = agent.id
        logging.info(f"Attack_id: {attack_id}")
        logging.info(f"Defend_id: {defend_id}")
        logging.info(f"Player_id: {player_id}")
        attack_units = self.graph.nodes[attack_id]['units']
        defend_units = self.graph.nodes[defend_id]['units']
        defender_player_id = self.graph.nodes[defend_id]['player_id']
        try:
            assert self.graph.nodes[attack_id]['player_id'] == player_id
            assert defender_player_id != player_id
            assert attack_units > 1
            assert defend_units > 0
        except AssertionError:
            raise AssertionError(f"Not a valid move")
        logging.info(f"{attack_id} is controlled by {player_id} and has {attack_units} Units")
        logging.info(f"{defend_id} is controlled by {defender_player_id} and has {defend_units} Units")
        attack_loss, defend_loss = single_roll(attack_units-1 , defend_units)
        #TODO: Institute a logger here
        logging.info(f"Attacker loses {attack_loss} unit(s), Defender loses {defend_loss} unit(s)")
        self.graph.nodes[attack_id]['units'] -= attack_loss 
        self.graph.nodes[defend_id]['units'] -= defend_loss 
        if self.graph.nodes[defend_id]['units'] == 0:
            logging.info(f"Attacker takes {defend_id}")
            self.graph.nodes[defend_id]['player_id'] = agent.id
            self.graph.nodes[defend_id]['player_color'] = agent.color
            self.graph.nodes[defend_id]['units'] = self.graph.nodes[attack_id]['units']
            self.graph.nodes[attack_id]['units'] = 1


    def show_board(self):
        graph_json = nx.node_link_data(self.graph)
        gdf = gpd.GeoDataFrame(graph_json['nodes'])
        gdf = gdf.set_geometry(gdf.geometry.apply(lambda x: shp.wkt.loads(x)))
        gdf['geo_center'] = gdf.geo_center.apply(lambda x: shp.wkt.loads(x))
        gdf['centroid_lat'] = gdf.geo_center.apply(lambda pt: pt.y)
        gdf['centroid_lng'] = gdf.geo_center.apply(lambda pt: pt.x)

        f, ax = plt.subplots(1, figsize=(15, 15))
        gdf.plot(column='region',ax=ax, cmap='Pastel2',categorical='True')
        plt.scatter(gdf.centroid_lng, gdf.centroid_lat, s=200,c=gdf.player_color,alpha=.5)
        for j,i in gdf.iterrows():
            plt.annotate(str(i.units), (i.centroid_lng-.3,i.centroid_lat-.2))
        ax.set_xlim([-125, -67])
        ax.set_ylim([24, 50])
        plt.show()
