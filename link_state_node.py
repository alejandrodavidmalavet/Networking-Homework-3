from simulator.node import Node
import json
# py sim.py LINK_STATE demo.event

class Link_State_Node(Node):

    def __init__(self, id):

        super().__init__(id)

        self.edges = dict()

        self.nodes = {self.id : 0}

        self.routing_table = {self.id : None}



    def __str__(self):
        return "Rewrite this function to define your node dump printout"



    def link_has_been_updated(self, neighbor, latency):

        edge = frozenset([neighbor,self.id])

        sequence_number = self.edges[edge]['sequence_number'] + 1 if edge in self.edges else 0

        self.link(edge,latency,sequence_number)

        

    def process_incoming_routing_message(self, m):

        edge, latency, sequence_number = json.loads(m)

        edge = frozenset(edge)

        if edge not in self.edges or (self.edges[edge]['sequence_number'] < sequence_number):

            self.link(edge,latency,sequence_number)



    def get_next_hop(self, destination):

        self.build_routing_table()

        while destination in self.routing_table and self.routing_table[destination] is not self.id:

            destination = self.routing_table[destination]

        return destination if destination in self.routing_table else -1



    def link(self,edge,latency,sequence_number):

        self.build_edge(edge,latency,sequence_number)
            
        for node in edge: 

            if node not in self.nodes:

                for edge in self.edges:
                    
                    self.send_to_neighbor(node,self.build_message(edge))

            self.nodes[node] = float('inf') if node != self.id else 0

        self.send_to_neighbors(self.build_message(edge))



    def build_edge(self,edge,latency,sequence_number):

        self.edges[edge] = {
            'latency': latency,
            'sequence_number': sequence_number
        }



    def build_message(self,edge):

        return json.dumps((list(edge),self.edges[edge]['latency'],self.edges[edge]['sequence_number']))



    def build_routing_table(self):

        dist = self.nodes.copy()

        nodes_copy = dict()

        while self.nodes:

            node = min(self.nodes, key=self.nodes.get)

            nodes_copy[node] = float('inf') if node != self.id else 0

            del self.nodes[node]

            for edge in self.edges:

                latency = self.edges[edge]['latency']

                if latency >= 0 and node in edge:

                    neighbor = self.get_neighbor(edge,node)

                    alt = dist[node] + latency

                    if alt < dist[neighbor]:

                        if neighbor in self.nodes: 
                            self.nodes[neighbor] = alt

                        dist[neighbor] = alt

                        self.routing_table[neighbor] = node

        self.nodes = nodes_copy
    


    def get_neighbor(self,edge,node):

        edge = set(edge)

        edge.remove(node)

        return edge.pop()