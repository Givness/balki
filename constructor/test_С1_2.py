#https://www.youtube.com/watch?v=Jed7uLL7xr8

from structures import *

nodes = [
    Node(-3, 0),
    Node(3, 0),
]

nodes[0].add_support(Support(0, 0, 0, 0, True, True, False))
nodes[1].add_support(Support(0, 0, 0, 0, False, True, False))

segments = [
    BeamSegment(nodes[0], nodes[1])
]

segments[0].add_force(Force(10000, 270, 1, 2, False))
segments[0].add_torque(Torque(20000, 0, False))
segments[0].add_force(Force(30000, 270, 4, 1, False))

beam = Beam(segments)
#beam.save_to_file()
print(beam.solve())