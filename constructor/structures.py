from ids import IDNumerator
from enum import Enum
import numpy as np
import sympy as sp
import mpmath

class Force(IDNumerator):
    def __init__(self, value: np.float64, angle: np.float64, node1_dist: np.float64, length: np.float64=1, unknown: bool=False):
        super().__init__()
        self.value: np.float64 = value
        self.angle: np.float64 = angle % 360
        self.node1_dist: np.float64 = node1_dist
        self.length: np.float64 = length
        self.unknown: bool = unknown

    @property
    def part_x(self) -> np.float64:
        if self.angle == 0: return self.value * self.length
        elif self.angle == 180: return -self.value * self.length
        elif self.angle == 90 or self.angle == 270: return 0
        else: return np.cos(np.deg2rad(self.angle)) * self.value * self.length

    @property
    def part_y(self) -> np.float64:
        if self.angle == 0 or self.angle == 180: return 0
        elif self.angle == 90: return self.value * self.length
        elif self.angle == 270: return -self.value * self.length
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
        else: return Force.Type.OTHER

class Torque(IDNumerator):
    def __init__(self, value: np.float64, node1_dist: np.float64, unknown: bool=False):
        super().__init__()
        self.value: np.float64 = value
        self.node1_dist: np.float64 = node1_dist
        self.unknown: bool = unknown

    def __repr__(self):
        return f"Torque(value={self.value}, node1_dist={self.node1_dist}, unknown={self.unknown})"

class Support(IDNumerator):
    def __init__(self, angle: np.float64, force_x: np.float64, force_y: np.float64, torque: np.float64, unknown_fx: bool, unknown_fy: bool, unknown_t: bool):
        super().__init__()
        self.angle: np.float64 = angle % 360
        self.horizontal_force: Force = Force(force_x, angle, 0, 1, unknown_fx)
        self.vertical_force: Force = Force(force_y, angle + 90, 0, 1, unknown_fy)
        self.torque: Torque = Torque(torque, 0, unknown_t)

    def __repr__(self):
        return f"Support(angle={self.angle}, force_x={self.horizontal_force}, force_y={self.vertical_force}, torque={self.torque})"

class Node(IDNumerator):
    def __init__(self, x: np.float64, y: np.float64):
        super().__init__()
        self.x: np.float64 = x
        self.y: np.float64 = y
        self.support: Support = None

    def add_support(self, support: Support):
        self.support: Support = support

    def __repr__(self):
        return f"Node(coords=({self.x}, {self.y}), support={self.support})"

class BeamSegment(IDNumerator):
    def __init__(self, node1: Node, node2: Node):
        super().__init__()
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
        super().__init__()
        self.segments: list[BeamSegment] = segments
        self.nodes: list[Node] | set[Node] = set()
        for s in segments:
            self.nodes.add(s.node1)
            self.nodes.add(s.node2)
        self.nodes = list(self.nodes)

    def add_segment(self, segment: BeamSegment):
        self.segments.append(segment)

    def solve(self):
        fx_dict: dict[str: str | np.float64] = {}
        fy_dict: dict[str: str | np.float64] = {}
        t_dict: dict[str: str | np.float64] = {}

        self.base_node: Node = Node(0, 0)

        def add_force_parts(obj_name: str, force: Force, x: np.float64, y: np.float64):
            if force.get_type != Force.Type.VERTICAL:
                force_part = force.part_x
                fx_dict[f'{obj_name}_part_x'] = '?' if force.unknown else force_part
                delta_y = y - self.base_node.y
                if delta_y == 0:
                    t_dict[f'{obj_name}_part_x_torque'] = 0
                else:
                    t_dict[f'{obj_name}_part_x_torque'] = f'{delta_y} * {obj_name}_part_x' if force.unknown else force_part * delta_y
            if force.get_type != Force.Type.HORIZONTAL:
                force_part = force.part_y
                fy_dict[f'{obj_name}_part_y'] = '?' if force.unknown else force_part
                delta_x = x - self.base_node.x
                if delta_x == 0:
                    t_dict[f'{obj_name}_part_x_torque'] = 0
                else:
                    t_dict[f'{obj_name}_part_y_torque'] = f'{delta_x} * {obj_name}_part_y' if force.unknown else force_part * delta_x

        for node_number, node in enumerate(self.nodes):
            if node.support:
                if node.support.vertical_force:
                    add_force_parts(f'node_{node_number}_vertical_force', node.support.vertical_force, node.x, node.y)

                if node.support.horizontal_force:
                    add_force_parts(f'node_{node_number}_horizontal_force', node.support.horizontal_force, node.x, node.y)

                if node.support.torque:
                    t_dict[f'node_{node_number}_torque'] = '?' if node.support.torque.unknown else node.support.torque.value

        for segment_number, segment in enumerate(self.segments):
            for force_number, force in enumerate(segment.forces):
                x = segment.node1.x + force.node1_dist * (segment.node2.x - segment.node1.x) / segment.length
                y = segment.node1.y + force.node1_dist * (segment.node2.y - segment.node1.y) / segment.length
                add_force_parts(f'segment_{segment_number}_force_{force_number}', force, x, y)

            for torque_number, torque in enumerate(segment.torques):
                t_dict[f'segment_{segment_number}_torque_{torque_number}'] = '?' if torque.unknown else torque.value

        # print(fx_dict)
        # print(fy_dict)
        # print(t_dict)

        eqs: list[sp.Eq] = [
            sp.Eq(sp.simplify(' + '.join(fx_dict.keys())), 0),
            sp.Eq(sp.simplify(' + '.join(fy_dict.keys())), 0),
            sp.Eq(sp.simplify(' + '.join(t_dict.keys())), 0)
        ]

        secondary_eqs: list[sp.Eq] = []
        unknowns: list[str] = []
        all_symbols: list[str] = []

        for d in (fx_dict, fy_dict, t_dict):
            for key, val in d.items():
                if val == '?':
                    unknowns.append(key)
                else:
                    secondary_eqs.append(
                        sp.Eq(sp.Symbol(key), sp.simplify(val))
                    )
                all_symbols.append(key)

        print('Eqs:')
        for eq in eqs + secondary_eqs:
            print(eq)

        print('Unknowns:')
        for u in unknowns:
            print(u)
        
        solution: dict = sp.solve(eqs + secondary_eqs, sp.symbols(all_symbols))
        print('Solution:')
        for key, val in solution.items():
            print(f'{key} = {val}')

        answer = {key: val for key, val in solution.items() if str(key) in unknowns}
        print(f"Answer: {answer}")

        # temp = np.round(fx, 5)
        # result = f"Горизонтальная реакция опоры: {temp if temp != 0 else 0.0}\n"
        # temp = np.round(fy, 5)
        # result += f"Вертикальная реакция опоры: {temp if temp != 0 else 0.0}\n"
        # temp = np.round(t, 5)
        # result += f"Момент реакции опоры: {temp if temp != 0 else 0.0}"
        # return result

    def __repr__(self):
        return f"Beam(segments={self.segments})"