import random
import networkx as nx

from maps.debug import debug

class Map():
    metadata = {}

    def __init__(self):
        self.graph = None
        pass

    def initialize_player_assignment(self):
        """Randomly assigns each player a country until there are none left"""


        pass
     
    def change_ownership(self, payload):
        """Change ownership of a country
        Params: payload (dict) {node:player}
        """
        nx.set_node_attributes(self.graph, payload, "owner")
        pass
