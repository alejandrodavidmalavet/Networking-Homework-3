from simulator.node import Node
import json
# py sim.py LINK_STATE demo.event

class Link_State_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        self.edges = dict()
        self.nodes = {self.id : 0}
        self.dist = {self.id : 0}
        self.routing_table = {self.id : None}



    def __str__(self):
        return "Rewrite this function to define your node dump printout"



    def link_has_been_updated(self, neighbor, latency):

        edge = frozenset([neighbor,self.id])

        sequence_number = self.edges[edge]['sequence_number'] + 1 if edge in self.edges else 0

        self.link(edge,latency,sequence_number)

        self.build_routing_table()



    def process_incoming_routing_message(self, m):

        edge, latency, sequence_number = json.loads(m)

        edge = frozenset(edge)

        if edge not in self.edges or (self.edges[edge]['sequence_number'] < sequence_number):

            self.build_edge(edge,latency,sequence_number)

            for edge in self.edges:

                self.link(edge,self.edges[edge]['latency'],self.edges[edge]['sequence_number'])

            self.build_routing_table()



    def build_routing_table(self):

        self.dist = self.nodes.copy()

        nodes_copy = dict()

        while self.nodes:

            node = min(self.nodes, key=self.nodes.get)

            nodes_copy[node] = self.nodes[node]

            del self.nodes[node]

            for edge in self.edges:

                latency = self.edges[edge]['latency']

                if latency >= 0 and node in edge:

                    neighbor = self.get_neighbor(edge,node)

                    alt = self.dist[node] + latency

                    if alt < self.dist[neighbor]:

                        if neighbor in self.nodes: 
                            self.nodes[neighbor] = alt

                        self.dist[neighbor] = alt

                        self.routing_table[neighbor] = node

        self.nodes = nodes_copy



    def link(self,edge,latency,sequence_number):
        
        for node in edge: self.nodes[node] = float('inf') if node != self.id else 0

        self.build_edge(edge,latency,sequence_number)

        message = json.dumps((  list(edge), 
                                latency, 
                                sequence_number))

        self.send_to_neighbors(message)



    def build_edge(self,edge,latency,sequence_number):
        self.edges[edge] = {
            'latency': latency,
            'sequence_number': sequence_number
        }
    


    def get_neighbor(self,edge,node):
        edge = set(edge)
        edge.remove(node)
        return edge.pop()



    def debug(self):
        print("Node:", self.id, "Nodes:",list(self.nodes))
        for edge in self.edges:
            print('     Edge:',edge)
            print('     Latency:', self.edges[edge]['latency'])
            print('     Sequence Number:',self.edges[edge]['sequence_number'])



    def get_next_hop(self, destination):
        while destination in self.routing_table and self.routing_table[destination] is not self.id:
            destination = self.routing_table[destination]
        return destination if destination in self.routing_table else -1