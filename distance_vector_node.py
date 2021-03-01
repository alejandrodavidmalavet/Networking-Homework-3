from simulator.node import Node
import json


class Distance_Vector_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        # sequence number for latency management
        self.sequence_number = 0

        self.distance_vectors = {
            self.id: {
                'path': [],
                'cost': 0
            }
        }

        self.nodes = {}

    def __str__(self):
        return ""

    def link_has_been_updated(self, neighbor, latency):
        # latency = -1 if delete a link
        if latency > -1:
            if neighbor in self.nodes:
                # update node data
                self.nodes[neighbor]['cost'] = latency
            else:
                # initialize node data
                self.nodes[neighbor] = {
                    'cost': latency,
                    'sequence_number': -1,
                }
        else:
            del self.nodes[neighbor]

        self.handleDistanceVectorUpdate()

    def process_incoming_routing_message(self, m):
        senderId, sequence_number, distance_vector = json.loads(m)
        # Received message should be the newest one
        if not senderId in self.nodes:
            return
        elif sequence_number >= self.nodes[senderId]['sequence_number']:
            # update sequence_number
            self.nodes[senderId
                       ]['sequence_number'] = sequence_number
            self.nodes[senderId
                       ]['distance_vector'] = distance_vector
            self.handleDistanceVectorUpdate()

    def get_next_hop(self, destination):
        key = str(destination)
        if key in self.distance_vectors:
            distance_vector = self.distance_vectors[key]
            return distance_vector['path'][0]
        else:
            return -1

    def handleDistanceVectorUpdate(self):

        hasBeenModified = False

        distance_vector_new = {
            self.id: {
                'path': [],
                'cost': 0,
            }
        }

        for nodeObject in self.nodes.items():
            nodeId, nodeData = nodeObject

            if 'distance_vector' in nodeData:

                for Vertex, distanceObject in nodeData['distance_vector'].items():

                    if not self.id in distanceObject['path']:

                        alt = distanceObject['cost'] + nodeData['cost']

                        if not Vertex in distance_vector_new:

                            distance_vector_new[str(Vertex)] = {
                                'cost': alt,
                                'path': [nodeId] + distanceObject['path'],
                            }

                        else:

                            curr = distance_vector_new[Vertex]['cost']

                            if alt < curr:
                                distance_vector_new[str(Vertex)] = {
                                    'cost': alt,
                                    'path': [nodeId] + distanceObject['path'],
                                }

            else:

                distance_vector_new[str(nodeId)] = {
                    'cost': nodeData['cost'],
                    'path': [nodeId],
                }

        for k in distance_vector_new:

            if k in self.distance_vectors:
                new_cost = distance_vector_new[k]['cost']
                old_cost = self.distance_vectors[k]['cost']

                # change in cost
                if old_cost != new_cost:
                    hasBeenModified = True
                    break

                new_path = distance_vector_new[k]['path']
                old_path = self.distance_vectors[k]['path']

                # change in path
                if old_path != new_path:
                    hasBeenModified = True
                    break

            else:
                hasBeenModified = True
                break

        if hasBeenModified:

            self.distance_vectors = distance_vector_new
            self.send_to_neighbors(
                json.dumps((self.id, self.sequence_number, self.distance_vectors)))
            self.sequence_number += 1
