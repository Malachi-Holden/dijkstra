This package simulates a network of devices. Each device needs to know how to communicate with the others in the network and it already knows which devices it is already connected to. (In real life it would discover this by flooding and getting replies)

Each node figures out the best paths for communicating to all other nodes on the graph.

The router files are tell each node which other nodes they are adjacent to.

run 'linkstate.py router_name port' in the terminal
for instance $linkstate.py A 10000

do this on up to 4 different terminals with the following names and port numbers

A 10000
B 10010
C 10020
D 10030

Each terminal simulates a router on the network.

Feel free to rewrite the router files with your own terminals, and have as many nodes as you want -- just make sure to keep the files consistent. For instance, A_config.txt says that the route from A to B has a weight of 1. If you look at B_config.txt it says that the route to A has a weight of 1. This needs to be the same and consistent across all the files.

Try drawing the network as a weighted graph before writing the files.





