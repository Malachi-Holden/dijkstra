


class Vertex:
    def __init__(self):
        """nears is a dictionary with entries of the form:
        v:weight
        where v is a vertex near self, and weight is the weight between v and self"""
        self.nears = {}
        self.dist = -1
        self.prev = None

    def add(self, near, weight):
        self.nears[near] = weight

class Node(Vertex):
    """for use in the linkstate program"""
    def __init__(self, name, port):
        Vertex.__init__(self)
        self.port = port
        self.name = name

    def shortest_path(self):
        if self.prev == None:
            return self.name
        else:
            return self.prev.shortest_path()+self.name

    def __str__(self):
        result = ""
        result+=(str(self.port)+': ')
        for v in self.nears:
            result+=(str(v.port)+' '+ str(self.nears[v])+',')
        return result[:-1]


class WeightedGraph:
    def __init__(self, source, vertices):
        """vertices is a set of Vertex objects"""
        self.vertices = vertices # a set of Vertex objects, necessarily including source
        self.source = source # a vertex, the source of the graph
        assert(self.source in self.vertices)

    def add(self, v):
        self.vertices.add(v)

    def dijkstra(self):
        un = set()
        for ver in self.vertices:
            un.add(ver)

        self.source.dist = 0

        while len(un) != 0:
            next = self._min(un)
            un.remove(next)
            for neighbor in next.nears:
                weight = next.nears[neighbor]
                alt = next.dist+weight
                if (alt < neighbor.dist) or (neighbor.dist<0):
                    neighbor.dist = alt
                    neighbor.prev = next

    def _min(self, vertices):
        """finds the vertex in vertices with the shortest positive distance to source"""
        dist = -1
        current = None
        for v in vertices:
            current = v # set current to a random vertex
            break
        for v in vertices:
            if v.dist >=0:
                if (dist < 0) or (v.dist<dist):
                    current = v
                    dist = v.dist
        return current


if __name__ == '__main__':
    # code for testing
    A = Node('A',0)
    B = Node('B',1)
    C = Node('C',2)
    A.add(B, 7)
    A.add(C, 1)
    B.add(A, 7)
    B.add(C, 3)
    C.add(A, 1)
    C.add(B, 3)
    W = WeightedGraph(A, {A,B,C})
    W.dijkstra()
    for v in W.vertices:
        print("the shortest path to {0} is:".format(v.name), v.shortest_path())


















        #_____________
