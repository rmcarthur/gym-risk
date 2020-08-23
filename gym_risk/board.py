import random
import json
from pathlib import Path
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

    # Get all possible moves
    def get_all_possible_attacks(self):
        player_owned_nodes = [i[0] for i in self.graph.nodes(data='player') if i[1] == 'blue']
        units = [i[0] for i in self.graph.nodes(data='units') if i[1] > 1]
        player_possible_attack_nodes = [node for node in player_owned_nodes if node in units] 
        attack_edges = [i for i in self.graph.edges(player_possible_attack_nodes) if i[1] not in player_owned_nodes]
        return attack_edges

    def try_attack(self, attack_id: str, defend_id: str, player_id: int):
        # Validate move is legal
        attack_units = self.graph.nodes[attack_id]['units']
        defend_units = self.graph.nodes[defend_id]['units']
        try:
            assert self.graph.nodes[attack_id]['player_id'] == player_id
            assert self.graph.nodes[defend_id]['player_id'] != player_id
            assert attack_units > 1
            assert defend_units > 0
        except AssertionError:
            raise AssertionError(f"Not a valid move")
        attack_loss, defend_loss = single_roll(attack_units-1 , defend_units)
        #TODO: Institute a logger here
        print(f"Attacker loses {attack_loss} unit(s), Defender loses {defend_loss} unit(s)")
        self.graph.nodes[attack_id]['units'] -= attack_loss 
        self.graph.nodes[defend_id]['units'] -= defend_loss 
        if self.graph.nodes[defend_id]['units'] == 0:
            print(f"Attacker takes {defend_id}")

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
