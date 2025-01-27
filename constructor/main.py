from structures import *

n1 = Node(0, 0)
n2 = Node(5, 0)
bs1 = BeamSegment(n1, n2)
bs1.add_force(Force(2, 90, 2))

n3 = Node(-5, 0)
bs2 = BeamSegment(n1, n3)
bs2.add_force(Force(1, 90, 4))

n1.add_support(Support(-90, 1, 0, 5, True))
n2.add_support(Support(-90, -1, -1, -1))

b1 = Beam([bs1, bs2])
print(b1.solve())