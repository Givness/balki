#Яблонский С1 пример

from structures import *

nodes = [
    Node(0, 0),
    Node(2, 0),
    Node(4, 2),
    Node(6, 2)
]

nodes[0].add_support(Support(270, 0, 0, 0, True, True, True))

segments = [
    BeamSegment(nodes[0], nodes[1]),
    BeamSegment(nodes[1], nodes[2]),
    BeamSegment(nodes[2], nodes[3])
]

segments[1].add_force(Force(5000, 315, 0, 1, False))
segments[1].add_torque(Torque(8000, 1, False))
segments[2].add_force(Force(1200, 270, 1, 2, False))

beam = Beam(segments)
#beam.save_to_file()
print(beam.solve())