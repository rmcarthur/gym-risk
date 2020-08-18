import random
import json
from pathlib import Path
import networkx as nx

class Map():
    metadata = {}

    def __init__(self, board='us_cont'):
        # read in graph
        graph_path = Path(__file__).parent / f"assets/{board}_graph.json"
        with graph_path.open() as json_file: 
            graph_data = json.load(json_file) 

        #Load in map
        self.graph = nx.node_link_graph(graph_data)
        
        # randomize and assign player map
        self.graph.nodes = self.initialize_player_assignment()
        pass


    def initialize_player_assignment(self,players=['red','blue']):
        """Randomly assigns each player a country until there are none left"""
        graph_nodes = self.graph.nodes
        random.shuffle(graph_nodes)
        player_list = ['red', 'blue']
        for j,i in enumerate(graph_nodes):
            graph_nodes[i]['player'] = player_list[j%len(player_list)]
            graph_nodes[i]['units'] = 3
        return graph_nodes
     
    def change_ownership(self, payload):
        """Change ownership of a country
        Params: payload (dict) {node:player}
        """
        nx.set_node_attributes(self.graph, payload, "player")
        pass
