import networkx as nx

debug = nx.Graph()

debug.add_node("Thousand Oaks", continent="California", color="red")
debug.add_node("San Francisco", continent="California", color="red")
debug.add_node("Sacramento", continent="California", color="red")
debug.add_node("Provo", continent="Utah", color="blue")
debug.add_node("South Jordan", continent="Utah", color="blue")

debug.add_edge("South Jordan", "Provo")
debug.add_edge("South Jordan", "San Francisco")
debug.add_edge("Thousand Oaks", "San Francisco")
debug.add_edge("Provo", "San Francisco")
debug.add_edge("San Francisco", "Sacramento")
debug.add_edge("Sacramento", "Thousand Oaks")
debug.add_edge("Sacramento", "Provo")
