import numpy as np

class Force:
    def __init__(self, value, angle, node1_dist, length=1):
        self.value = value
        self.angle = angle
        self.node1_dist = node1_dist
        self.length = length

    def __repr__(self):
        return f"Force(value={self.value}, angle={self.angle}, node1_dist={self.node1_dist}, length={self.length})"

class Torque:
    def __init__(self, value, direction, node1_dist):
        self.value = value
        self.direction = direction
        self.node1_dist = node1_dist

    def __repr__(self):
        return f"Torque(value={self.value}, node1_dist={self.node1_dist})"

class BeamSegment:
    def __init__(self, node1, node2):
        self.node1 = node1
        self.node1.add_beam_segment(self)
        self.node2 = node2
        self.node2.add_beam_segment(self)
        self.forces = []
        self.torques = []
    
    def add_force(self, force):
        self.forces.append(force)

    @property
    def length(self):
        return np.sqrt((self.node1.x - self.node2.x) ** 2 + (self.node1.y - self.node2.y) ** 2)

    def __repr__(self):
        return f"BeamSegment(from={self.node1}, to={self.node2}, forces={self.forces})"

class Beam:
    def __init__(self, segments=[]):
        self.segments = segments
        self.nodes = set()
        for s in segments:
            self.nodes.add(s.node1)
            self.nodes.add(s.node2)
        self.nodes = list(self.nodes)
        self.base_node = None

    def add_segment(self, segment):
        self.segments.append(segment)

    def solve(self):
        fx = np.array([])
        fy = np.array([])
        t = np.array([])

        for n in self.nodes:
            if n.support != None and (n.support.v_force < 0 or n.support.h_force < 0 or n.support.torque < 0):
                self.base_node = n
                break

        for n in self.nodes:
            if n.support != None:
                if n.support.v_force > 0:
                    force_part = n.support.v_force * np.cos(np.deg2rad(n.support.angle + 90))
                    fx = np.append(fx, force_part)
                    t = np.append(t, force_part * (n.y - self.base_node.y))

                    force_part = n.support.v_force * np.sin(np.deg2rad(n.support.angle + 90))
                    fy = np.append(fy, force_part)
                    t = np.append(t, force_part * (n.x - self.base_node.x))

                if n.support.h_force > 0:
                    force_part = n.support.h_force * np.cos(np.deg2rad(n.support.angle + 180))
                    fx = np.append(fx, force_part)
                    t = np.append(t, force_part * (n.y - self.base_node.y))

                    force_part = n.support.h_force * np.sin(np.deg2rad(n.support.angle + 180))
                    fy = np.append(fy, force_part)
                    t = np.append(t, force_part * (n.x - self.base_node.x))

                if n.support.torque> 0:
                    if n.support.torq_dir:
                        t = np.append(t, n.support.torque)
                    else:
                        t = np.append(t, -n.support.torque)

        for s in self.segments:
            for f in s.forces:
                force_part = f.value * np.cos(np.deg2rad(f.angle))
                fx = np.append(fx, force_part)
                t = np.append(t, force_part * (s.node1.y + f.node1_dist * (s.node2.y - s.node1.y) / s.length - self.base_node.y))

                force_part = f.value * np.sin(np.deg2rad(f.angle))
                fy = np.append(fy, force_part)
                t = np.append(t, force_part * (s.node1.x + f.node1_dist * (s.node2.x - s.node1.x) / s.length - self.base_node.x))
            for torq in s.torques:
                if torq.direction:
                    t = np.append(t, torq.value)
                else:
                    t = np.append(t, -torq.value)
        temp = np.round(-np.sum(fx), 5)
        print(f"Вертикальная реакция опоры:", temp if temp != 0 else 0.0)
        temp = np.round(-np.sum(fy), 5)
        print(f"Горизонтальная реакция опоры:", temp if temp != 0 else 0.0)
        temp = np.round(np.sum(t), 5)
        print(f"Момент реакции опоры:", temp if temp != 0 else 0.0)

    def __repr__(self):
        return f"Beam(segments={self.segments})"
    
class Support:
    def __init__(self, angle, v_force, h_force, torque, torq_dir=False):
        self.angle = angle
        self.v_force = v_force
        self.h_force = h_force
        self.torque = torque
        self.torq_dir = torq_dir

    def __repr__(self):
        return f"Support(angle={self.angle}, v_force={self.v_force}, h_force={self.h_force}, torque={self.torque})"

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.beam_segments = []
        self.support = None

    def add_beam_segment(self, beam_segment):
        self.beam_segments.append(beam_segment)

    def add_support(self, support):
        self.support = support

    def __repr__(self):
        return f"Node(coords=({self.x}, {self.y}), support={self.support})"