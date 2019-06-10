# Malachi Holden
# run 'linkstate.py router_name port' in the terminal
# for instance $linkstate.py A 10000
# do this on multiple terminals with different names and port numbers
# just make sure to keep the port numbers consistant with the config files,
# which are stored in the directory called 'router_files'

# I avoid overflooding by using the algorithm from A8

# run the program on each terminal and let run until each 'router' has gotten a
# packet from each other router and all routers have calculated paths. Then type
# 'stop' to see the results


import sys
import select
import socket
import time
from Dijkstra import *

class Router:
    UDP_IP = '127.0.0.1'
    router_name = sys.argv[1]
    UDP_PORT = int(sys.argv[2])
    hop_limit = 3
    buf_size = 8192
    UPDATE_INTERVAL = 4
    ROUTE_UPDATE_INTERVAL = 8

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Make the socket reusable
        self.socket.setblocking(False) # Set socket to non-blocking mode
        self.socket.bind((self.UDP_IP, self.UDP_PORT))
        print("Accepting data on port:", self.UDP_PORT)

        self.num_neighbors = 0
        self.neighbors = set() # a set of neighbor's information. This is a set
        # of tuples, each tuple in the form (name, weight, port)
        # for instance, if this node had a neighbor called 'B' and the weight of the
        # edge to B was 7, and B was on port 8000, self.neighbors would contain
        # the tuple ('B', 7, 8000)
        filename = "router_files/" + self.router_name + "_config.txt"
        self.get_neighbors(filename) # sets up self.neighbors
        source = Node(self.router_name, self.UDP_PORT)
        self.nodes = {self.UDP_PORT:source} # this will contain all nodes in the network
        self.topology = None
        self.setupnodes()
        self.topology = WeightedGraph(source, set(self.nodes.values()))
        self.dead_lsps = {} # contains entries of the form src_port: stamp,
        # where src_port is the port of the router that sent the lsp and stamp is the timestamp

    def get_neighbors(self, filename):
        """reads the config file and collects the information about the neighbors of self"""
        f = open(filename, 'r')
        self.num_neighbors = int(f.readline())
        line = f.readline()
        while line:
            data = line.split(',')
            neighbor = (data[0], int(data[1]), int(data[2]))
            self.neighbors.add(neighbor)
            line = f.readline()
        f.close()

    def setupnodes(self):
        """puts the neighbors as a set of nodes"""
        for neighbor in self.neighbors:
            name = neighbor[0]
            weight = neighbor[1]
            port = neighbor[2]
            source = self.nodes[self.UDP_PORT]

            self.add(name, port)

            nd = self.nodes[port]
            nd.add(source, weight)
            source.add(nd, weight)

    def lsp(self):
        """constructs an lsp. the final result is a string that looks like:
        TTL,timestamp,srcname, srcport,weight dstport,dstname weight dstport, ...,dstname weight dstport
        for instance:
            3,1540777836.8037152,C,10020,A 1 10000,B 7 10010"""
        result = (str(self.hop_limit) + ',')
        result += (str(time.time()) + ',')
        result += (str(self.router_name) + ',')
        result += (str(self.UDP_PORT) + ',')
        for neighbor in self.neighbors:
            nei = neighbor[0] + ' ' + str(neighbor[1]) + ' ' +str(neighbor[2]) # looks like 'B' 7 8000
            result += (nei + ',')
        return result[:-1]

    def read_lsp(self, msg):
        """given an lsp msg from another router, records the information and
        returns a new lsp with an update ttl
        lsp example: 3,1540777836.8037152,C,10020,1 10000,7 10010"""
        data = msg.split(',')
        TTL = int(data[0])-1
        from_port = int(data[3])
        from_name = data[2]
        if from_port not in self.nodes:
            self.add(from_name, from_port)
        from_vertex = self.nodes[from_port]

        for i in range(4, len(data)):
            nei = data[i].split(' ')
            name = nei[0]
            weight = int(nei[1])
            port = int(nei[2])
            if port not in self.nodes:
                self.add(name, port)
            neiv = self.nodes[port]
            from_vertex.add(neiv, weight)
            neiv.add(from_vertex, weight)
        data[0] = str(TTL)
        result = ','.join(data)
        return result

    def send_lsp(self, port, msg):
        """safely sends an lsp, checking if the ttl has run out"""
        ttl = msg.split(',')[0]
        if int(ttl) > 0:
            self.send(msg, port)

    def flood(self, msg):
        """sends an lsp out to all non-redundant neighbors
        lsp example: 3,1540777836.8037152,C,10020,1 10000,7 10010"""

        data = msg.split(',')

        from_port = int(data[3])
        stamp = float(data[1])
        if from_port not in self.dead_lsps:
            self.dead_lsps[from_port] = 0
        if self.dead_lsps[from_port] < stamp:

            self.dead_lsps[from_port] = stamp
            flooded = "sent lsp at time {0} from {1} to: ".format(data[1], str(from_port))
            for nd in self.neighbors:
                to_port = nd[2]
                if from_port != to_port:
                    self.send_lsp(to_port,msg)
                    flooded += (str(to_port)+',')
            print(flooded[:-1]+'\n\n')


    def mainloop(self):
        """periodically floods and calculates shortest paths
        lsp example: 3,1540777836.8037152,C,10020,1 10000,7 10010"""
        start = time.time()
        update = start
        update_route = start + self.ROUTE_UPDATE_INTERVAL
        print("Type stop to end loop.")
        user_input = self.getline()
        while user_input !="stop":
            message = self.rec()
            if message:
                address = message.split(',')[3]
                print (address, "> ", message)
                data = self.read_lsp(message)
                self.flood(data)
            now = time.time()
            if now >= update:
                self.flood(self.lsp())
                update += self.UPDATE_INTERVAL
            if now >= update_route:
                self.topology.dijkstra()
                print("calculating shortest paths. Repeating in {0} seconds".format(self.ROUTE_UPDATE_INTERVAL))
                update_route += self.ROUTE_UPDATE_INTERVAL
            user_input = self.getline()

    def send(self, msg, port):
        self.socket.sendto(msg.encode('ASCII'), (self.UDP_IP, port))

    def rec(self):
        i, o, e = select.select([self.socket],[],[],0.0001)
        for r in i:
            if r == self.socket:
                msg = self.socket.recv(8192)
                return msg.decode('ASCII')
        return False

    def getline(self):
        # Using select for non blocking reading from sys.stdin
        i,o,e = select.select([sys.stdin],[],[],0.0001)
        for s in i:
            if s == sys.stdin:
                user_input = sys.stdin.readline()
                return user_input[:-1]
        return False

    def add(self, name, port):
        nd = Node(name, port)
        self.nodes[port] = nd
        if self.topology:
            self.topology.add(nd)

    def __str__(self):
        result = ""
        for key in N.nodes:
            result += (str(N.nodes[key]) + '\n')
        return result[:-1]










if __name__ == '__main__':
    N = Router()
    N.mainloop()
    print("topology:")
    print(N)
    print("\n_________________\n")
    for v in N.topology.vertices:
        print("shortest path from {0} to {1} is {2}, with a cost of {3}".format(N.router_name, v.name, v.shortest_path(), v.dist))









# ______________
