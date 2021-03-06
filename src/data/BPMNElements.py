class ProcessModel:

    def __init__(self):
        self.nodes = []
        self.edges = []

    def get_successors(self, node):
        edges = [edge.target for edge in self.edges if edge.source == node]
        return edges

    def get_predecessors(self, node):
        edges = [edge.source for edge in self.edges if edge.target == node]
        return edges

    def remove_node(self, node):
        if node in self.nodes:
            self.nodes.remove(node)

        for pnode in self.nodes:
            if isinstance(pnode, Cluster) and node in pnode.process_nodes:
                pnode.process_nodes.remove(node)

        for edge in self.edges:
            if edge.source == node or edge.target == node:
                self.edges.remove(edge)


""" 
    Tree structure
    
    - SequenceFlow (edge)
    - FlowObject (node)
        - Activity
            - Task
        - Event
        - Gateway
    - Cluster
        - Lane
        - Pool
"""


class SequenceFlow:

    def __init__(self, source, target):
        self.source = source
        self.target = target


class FlowObject:

    def __init__(self, element):
        self.element = element


class Cluster:

    def __init__(self, actor=None, name=None, pool=None):
        self.process_nodes = []
        self.element = actor
        self.name = name
        self.pool = pool


class Lane(Cluster):
    pass


class Pool(Cluster):
    pass


class Event(FlowObject):

    def __init__(self, element, event_type="", sub_type=""):
        super().__init__(element)
        self.class_type = event_type
        self.class_sub_type = sub_type
        self.class_spec = None


class Gateway(FlowObject):

    def __init__(self, element):
        super().__init__(element)
        self.type = None


class Task(FlowObject):
    pass
