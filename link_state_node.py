from simulator.node import Node
import json
# py sim.py LINK_STATE demo.event

class Link_State_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        self.neighbors = set()
        self.graph = dict()
        self.sequence_numbers = dict()
        


    # Return a string
    def __str__(self):
        return "Rewrite this function to define your node dump printout"



    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):

        self.neighbors.add(neighbor) if latency >= 0 else self.neighbors.remove(neighbor)

        sequence_number = self.sequence_numbers[neighbor] + 1 if neighbor in self.sequence_numbers else 0

        self.sequence_numbers[neighbor] = sequence_number

        edge = frozenset([self.id,neighbor])

        self.add_edge(edge,latency,sequence_number)

        message = json.dumps((  list(edge), 
                                latency, 
                                sequence_number))

        self.send_to_neighbors(message)
    


    def process_incoming_routing_message(self, m):

        edge, latency, sequence_number = json.loads(m)

        edge = frozenset(edge)

        if edge not in self.graph or self.graph[edge]['sequence_number'] < sequence_number:

            self.add_edge(edge,latency,sequence_number)

            for edge in self.graph:

                message = json.dumps((  list(edge), 
                                        self.graph[edge]['latency'], 
                                        self.graph[edge]['sequence_number']))
                                        
                self.send_to_neighbors(message)

            self.debug_print()



    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        return -1



    def debug_print(self):
        print('======================')
        print('Node:',self.id, '\nNeighbors:',list(self.neighbors))
        print('======================')
        for edge in self.graph:
            nodes = list(edge)
            print('     Edge:', nodes[0], '&', nodes[1])
            print('     Latency:', self.graph[edge]['latency'])
            print('     Sequence Number:', self.graph[edge]['sequence_number'])
            print('     ------------')



    def add_edge(self,edge,latency,sequence_number):
        self.graph[edge] = {
            'latency': latency,
            'sequence_number': sequence_number
        }