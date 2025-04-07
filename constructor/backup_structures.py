from ids import IDNumerator
from enum import Enum
import numpy as np
import sympy as sp
import mpmath

class Force(IDNumerator):
    def __init__(self, value: np.float64, angle: np.float64, node1_dist: np.float64, length: np.float64=1, unknown: bool=False):
        super().__init__()
        self.value: np.float64 = value
        self.angle: np.float64 = angle
        self.node1_dist: np.float64 = node1_dist
        self.length: np.float64 = length
        self.unknown: bool = unknown

    @property
    def part_x(self) -> np.float64:
        if self.angle == 0 or self.angle == 180: return self.value * self.length
        elif self.angle == 90 or self.angle == 270: return 0
        else: return np.cos(np.deg2rad(self.angle)) * self.value * self.length

    @property
    def part_y(self) -> np.float64:
        if self.angle == 0 or self.angle == 180: return 0
        elif self.angle == 90 or self.angle == 270: return self.value * self.length
        else: return np.sin(np.deg2rad(self.angle)) * self.value * self.length

    def __repr__(self):
        return f"Force(value={self.value}, angle={self.angle}, node1_dist={self.node1_dist}, length={self.length}, unknown={self.unknown})"
    
    class Type(Enum):
        OTHER = 0
        VERTICAL = 1
        HORIZONTAL = 2

    @property
    def get_type(self):
        if self.angle == 0 or self.angle == 180: return Force.Type.HORIZONTAL
        elif self.angle == 90 or self.angle == 270: return Force.Type.VERTICAL
        else: Force.Type.OTHER

class Torque(IDNumerator):
    def __init__(self, value: np.float64, node1_dist: np.float64, unknown: bool=False):
        self.value: np.float64 = value
        self.node1_dist: np.float64 = node1_dist
        self.unknown: bool = unknown

    def __repr__(self):
        return f"Torque(value={self.value}, node1_dist={self.node1_dist}, unknown={self.unknown})"

class Support(IDNumerator):
    def __init__(self, angle: np.float64, force_x: np.float64, force_y: np.float64, torque: np.float64, unknown_fx: bool, unknown_fy: bool, unknown_t: bool):
        self.angle: np.float64 = angle
        self.force_x: Force = Force(force_x, angle, 0, 1, unknown_fx)
        self.force_y: Force = Force(force_y, angle + 90, 0, 1, unknown_fy)
        self.torque: Torque = Torque(torque, 0, unknown_t)

    def __repr__(self):
        return f"Support(angle={self.angle}, force_x={self.force_x}, force_y={self.force_y}, torque={self.torque})"

class Node(IDNumerator):
    def __init__(self, x: np.float64, y: np.float64):
        self.x: np.float64 = x
        self.y: np.float64 = y
        self.support: Support = None

    def add_support(self, support: Support):
        self.support: Support = support

    def __repr__(self):
        return f"Node(coords=({self.x}, {self.y}), support={self.support})"

class BeamSegment(IDNumerator):
    def __init__(self, node1: Node, node2: Node):
        self.node1: Node = node1
        self.node2: Node = node2
        self.forces: list[Force] = []
        self.torques: list[Torque] = []
    
    def add_force(self, force: Force):
        self.forces.append(force)

    def add_torque(self, torque: Torque):
        self.torques.append(torque)

    @property
    def length(self):
        return np.sqrt((self.node1.x - self.node2.x) ** 2 + (self.node1.y - self.node2.y) ** 2)

    def __repr__(self):
        return f"BeamSegment(from={self.node1}, to={self.node2}, forces={self.forces}, torques={self.torques})"

class Beam(IDNumerator):
    def __init__(self, segments: list[BeamSegment]=[]):
        self.segments: list[BeamSegment] = segments
        self.nodes: list[Node] = set()
        for s in segments:
            self.nodes.add(s.node1)
            self.nodes.add(s.node2)
        self.nodes = list(self.nodes)

    def add_segment(self, segment: BeamSegment):
        self.segments.append(segment)

    def solve(self):
        fx: sp.Eq = 0
        fy: sp.Eq = 0
        t: sp.Eq = 0

        self.base_node: Node = Node(0, 0)

        self.na_forces: list[Force] = []
        self.na_torques: list[Torque] = []

        for n in self.nodes:
            if n.support != None:
                if n.support.force_y != None:
                    if n.support.force_y.unknown:
                        self.na_forces.append(n.support.force_y)
                    elif n.support.force_y.value > 0:
                        force_part = n.support.force_y.part_x
                        fx += force_part
                        t += force_part * (self.base_node.y - n.y)

                        force_part = n.support.force_y.part_y
                        fy += force_part
                        t += force_part * (self.base_node.x - n.x)

                if n.support.force_x != None:
                    if n.support.force_x.unknown:
                        self.na_forces.append(n.support.force_x)
                    elif n.support.force_x.value > 0:
                        force_part = n.support.force_x.part_x
                        fx += force_part
                        t += force_part * (self.base_node.y - n.y)

                        force_part = n.support.force_x.part_y
                        fy += force_part
                        t += force_part * (self.base_node.x - n.x)

                if n.support.torque != None:
                    if n.support.torque.unknown:
                        self.na_torques.append(n.support.torque)
                    elif n.support.torque.value != 0:
                        t += n.support.torque.value

        for s in self.segments:
            for f in s.forces:
                if f.unknown:
                    self.na_forces.append(f)
                elif f.value > 0:
                    force_part = f.part_x
                    fx += force_part
                    t += force_part * (self.base_node.y - (s.node1.y + f.node1_dist * (s.node2.y - s.node1.y) / s.length))

                    force_part = f.part_y
                    fy += force_part
                    t += force_part * (self.base_node.x - (s.node1.x + f.node1_dist * (s.node2.x - s.node1.x) / s.length))

            for torq in s.torques:
                if torq.unknown:
                    self.na_torques.append(torq)
                elif torq.value != 0:
                    t += torq.value

        temp = np.round(fx, 5)
        result = f"Горизонтальная реакция опоры: {temp if temp != 0 else 0.0}\n"
        temp = np.round(fy, 5)
        result += f"Вертикальная реакция опоры: {temp if temp != 0 else 0.0}\n"
        temp = np.round(t, 5)
        result += f"Момент реакции опоры: {temp if temp != 0 else 0.0}"
        return result

    def __repr__(self):
        return f"Beam(segments={self.segments})"