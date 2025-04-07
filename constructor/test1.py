#https://isopromat.ru/tehmeh/reshenie-zadach/opredelenie-reakcij-opor-balki-sila-pod-uglom

from structures import *

nodes = [
    Node(-17, 0),
    Node(-11, 0),
    Node(-1, 0)
]

nodes[1].add_support(Support(0, 0, 0, 0, True, True, False))
nodes[2].add_support(Support(0, 0, 0, 0, False, True, False))

segments = [
    BeamSegment(nodes[0], nodes[1]),
    BeamSegment(nodes[1], nodes[2])
]

segments[0].add_force(Force(10, 215, 0, 1, False))
segments[1].add_torque(Torque(8, 0, False))
segments[1].add_force(Force(4, 270, 2.5, 5, False))

beam = Beam(segments)
print(beam.solve())