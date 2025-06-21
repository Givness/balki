import json
import math
from enum import Enum
import networkx as nx
import sympy as sp
from errors import *
from ids import IDNumerator


class Force(IDNumerator):
    def __init__(self, value: float, angle: float, node1_dist: float, length: float = 1, unknown: bool = False, custom_id: int | None = None):
        super().__init__(custom_id)

        if value < 0: raise NegativeOrZeroValueError("Значение силы не может быть отрицательным!")
        self.value: float = value

        self.angle: float = angle % 360

        if node1_dist < 0: raise NegativeOrZeroValueError("Расстояние от края не может быть отрицательным!")
        self.node1_dist: float = node1_dist

        if length <= 0: raise NegativeOrZeroValueError("Длина действия силы должна быть положительной!")
        self.length: float = length

        self.unknown: bool = unknown

    @property
    def part_x(self):
        if self.angle in (0, 180):
            return self.value * self.length * (1 if self.angle == 0 else -1)
        elif self.angle in (90, 270):
            return 0
        else:
            return math.cos(math.radians(self.angle)) * self.value * self.length

    @property
    def part_y(self):
        if self.angle in (0, 180):
            return 0
        elif self.angle == 90:
            return self.value * self.length
        elif self.angle == 270:
            return -self.value * self.length
        else:
            return math.sin(math.radians(self.angle)) * self.value * self.length

    def __repr__(self):
        return f"Force(value={self.value}, angle={self.angle}, node1_dist={self.node1_dist}, length={self.length}, unknown={self.unknown})"

    class Type(Enum):
        OTHER = 0
        VERTICAL = 1
        HORIZONTAL = 2

    @property
    def get_type(self):
        if self.angle in (0, 180): return Force.Type.HORIZONTAL
        elif self.angle in (90, 270): return Force.Type.VERTICAL
        else: return Force.Type.OTHER

    def pretty_print(self, indent=0):
        pad = ' ' * indent
        return (f"{pad}Force#{self.id}: val={self.value}, angle={self.angle}°, "
                f"dist={self.node1_dist}, len={self.length}, unknown={'Y' if self.unknown else 'N'}")


class Torque(IDNumerator):
    def __init__(self, value: float, node1_dist: float, unknown: bool = False, custom_id: int | None = None):
        super().__init__(custom_id)

        self.value: float = value

        if node1_dist < 0: raise NegativeOrZeroValueError("Расстояние не может быть отрицательным!")
        self.node1_dist: float = node1_dist

        self.unknown: bool = unknown

    def __repr__(self):
        return f"Torque(value={self.value}, node1_dist={self.node1_dist}, unknown={self.unknown})"
    
    def pretty_print(self, indent=0):
        pad = ' ' * indent
        return (f"{pad}Torque#{self.id}: val={self.value}, dist={self.node1_dist}, unknown={'Y' if self.unknown else 'N'}")


class Support(IDNumerator):
    def __init__(self, angle: float, force_x: float, force_y: float, torque: float, unknown_fx: bool, unknown_fy: bool, unknown_t: bool, custom_id: int | None = None):
        super().__init__(custom_id)
        self.angle: float = angle % 360
        self.horizontal_force: Force = Force(force_x, angle, 0, 1, unknown_fx)
        self.vertical_force: Force = Force(force_y, angle + 90, 0, 1, unknown_fy)
        self.torque: Torque = Torque(torque, 0, unknown_t)

    def __repr__(self):
        return f"Support(angle={self.angle}, force_x={self.horizontal_force}, force_y={self.vertical_force}, torque={self.torque})"
    
    class Type(Enum):
        FIXED = 0
        PINNED = 1
        ROLLER = 2

    @property
    def get_type(self):
        if self.torque.value != 0 or self.torque.unknown: return Support.Type.FIXED
        elif self.horizontal_force.value != 0 or self.horizontal_force.unknown: return Support.Type.PINNED
        else: return Support.Type.ROLLER

    def pretty_print(self, indent=0):
        pad = ' ' * indent
        result = [f"{pad}Support#{self.id}: angle={self.angle}°"]
        result.append(self.horizontal_force.pretty_print(indent + 2))
        result.append(self.vertical_force.pretty_print(indent + 2))
        result.append(self.torque.pretty_print(indent + 2))
        return '\n'.join(result)


class Hinge(IDNumerator):
    def __init__(self, custom_id: int | None = None):
        super().__init__(custom_id)

class Node(IDNumerator):
    def __init__(self, x: float, y: float, custom_id: int | None = None):
        super().__init__(custom_id)
        self.x: float = x
        self.y: float = y
        self.support: Support = None
        self.hinge: Hinge = None

    def add_support(self, support: Support):
        self.support = support

    def add_hinge(self):
        self.hinge = Hinge()

    def __repr__(self):
        return f"Node(coords=({self.x}, {self.y}), support={self.support})"

    def __hash__(self):
        return hash((self.x, self.y, self.id))

    def __eq__(self, other):
        return isinstance(other, Node) and self.id == other.id
    
    def pretty_print(self, indent=0):
        pad = ' ' * indent
        lines = [f"{pad}Node#{self.id}: ({self.x}, {self.y})"]
        if self.support:
            lines.append(self.support.pretty_print(indent + 2))
        if self.hinge:
            lines.append(f"{' ' * (indent + 2)}Hinge#{self.hinge.id}")
        return '\n'.join(lines)


class BeamSegment(IDNumerator):
    def __init__(self, node1: Node, node2: Node, custom_id: int | None = None):
        super().__init__(custom_id)
        self.node1: Node = node1
        self.node2: Node = node2
        self.forces: list[Force] = []
        self.torques: list[Torque] = []

    def add_force(self, force: Force):
        if force.node1_dist > self.length:
            raise HighDistanceError("Отступ не может быть больше длины сегмента!")
        self.forces.append(force)

    def add_torque(self, torque: Torque):
        if torque.node1_dist > self.length:
            raise HighDistanceError("Отступ не может быть больше длины сегмента!")
        self.torques.append(torque)

    @property
    def length(self):
        return math.hypot(self.node1.x - self.node2.x, self.node1.y - self.node2.y)

    def __repr__(self):
        return f"BeamSegment(from={self.node1}, to={self.node2}, forces={self.forces}, torques={self.torques})"
    
    def pretty_print(self, indent=0):
        pad = ' ' * indent
        lines = [f"{pad}Segment#{self.id}: from Node#{self.node1.id} to Node#{self.node2.id}"]
        for force in self.forces:
            lines.append(force.pretty_print(indent + 2))
        for torque in self.torques:
            lines.append(torque.pretty_print(indent + 2))
        return '\n'.join(lines)


class Beam(IDNumerator):
    def __init__(self, segments: list[BeamSegment] = [], custom_id: int | None = None):
        super().__init__(custom_id)
        self.graph = nx.Graph()
        for s in segments:
            self.add_segment(s)

    def add_node(self, node: Node):
        for existing_node in self.graph.nodes:
            if existing_node.x == node.x and existing_node.y == node.y:
                return existing_node

        self.graph.add_node(node)
        return node

    def add_segment(self, segment: BeamSegment) -> BeamSegment:
        node1 = self.add_node(segment.node1)
        node2 = self.add_node(segment.node2)

        if node1.x == node2.x and node1.y == node2.y:
            raise DotBeamError("Балка не может начинаться и заканчиваться в одной точке!")

        if self.graph.has_edge(node1, node2):
            return self.graph[node1][node2]['object']

        self.graph.add_edge(node1, node2, object=segment)
        return segment

    def get_segments(self):
        return [data['object'] for _, _, data in self.graph.edges(data=True)]

    def get_nodes(self):
        return list(self.graph.nodes)

    def reassign_ids(self):
        for cls in [Node, BeamSegment, Force, Torque, Support]:
            cls._next_id = 1
            cls._used_ids.clear()

        for idx, node in enumerate(self.get_nodes(), start=1):
            node.id = idx
            if node.support:
                node.support.id = Support._next_id
                Support._used_ids.add(Support._next_id)
                Support._next_id += 1

                node.support.horizontal_force.id = Force._next_id
                Force._used_ids.add(Force._next_id)
                Force._next_id += 1

                node.support.vertical_force.id = Force._next_id
                Force._used_ids.add(Force._next_id)
                Force._next_id += 1

                node.support.torque.id = Torque._next_id
                Torque._used_ids.add(Torque._next_id)
                Torque._next_id += 1

        for idx, segment in enumerate(self.get_segments(), start=1):
            segment.id = idx
            for force in segment.forces:
                force.id = Force._next_id
                Force._used_ids.add(Force._next_id)
                Force._next_id += 1
            for torque in segment.torques:
                torque.id = Torque._next_id
                Torque._used_ids.add(Torque._next_id)
                Torque._next_id += 1

    @staticmethod
    def format_readable_answers(answer_dict: dict[str, float]) -> dict[str, float]:
        readable_answer = {}

        for key, value in answer_dict.items():
            if key.startswith('node_'):
                parts = key.split('_')
                node_id = parts[1]

                if '_vertical_y' in key or key.endswith('_y'):
                    readable_answer[f"Вертикальная реакция в узле {node_id}"] = value
                elif '_horizontal_x' in key or key.endswith('_x'):
                    readable_answer[f"Горизонтальная реакция в узле {node_id}"] = value
                elif '_torque' in key:
                    readable_answer[f"Момент в узле {node_id}"] = value

            elif key.startswith('hinge_') and ('_force_x' in key or '_force_y' in key):
                hinge_id = key.split('_')[1]
                direction = 'горизонтальная' if '_force_x' in key else 'вертикальная'
                readable_answer[f"{direction.capitalize()} сила в шарнире {hinge_id}"] = value

            else:
                # fallback — просто ключ
                readable_answer[key] = value

        return readable_answer


    def solve(self):
        if len(self.graph.nodes) == 0:
            raise NoBeamError("Нет балки!")
        
        if all(node.support is None for node in self.get_nodes()):
            raise NoSupportsError("Вы не добавили опор!")

        if not nx.is_connected(self.graph):
            raise DividedBeamError("Балка состоит из несвязанных сегментов!")

        self.reassign_ids()

        fx_dict, fy_dict, t_dict = {}, {}, {}

        def add_force_parts(name: str, force: Force, x: float, y: float):
            if force.get_type != Force.Type.VERTICAL:
                part = force.part_x
                fx_dict[f'{name}_x'] = '?' if force.unknown else part
                dy = y
                t_dict[f'{name}_x_torque'] = 0 if dy == 0 else f'{dy}*{name}_x' if force.unknown else part * dy

            if force.get_type != Force.Type.HORIZONTAL:
                part = force.part_y
                fy_dict[f'{name}_y'] = '?' if force.unknown else part
                dx = x
                t_dict[f'{name}_y_torque'] = 0 if dx == 0 else f'{dx}*{name}_y' if force.unknown else part * dx

        for node in self.get_nodes():
            nid = f'node_{node.id}'
            if node.support:
                add_force_parts(f'{nid}_vertical', node.support.vertical_force, node.x, node.y)
                add_force_parts(f'{nid}_horizontal', node.support.horizontal_force, node.x, node.y)
                t_dict[f'{nid}_torque'] = '?' if node.support.torque.unknown else node.support.torque.value

        for segment in self.get_segments():
            sid = f'segment_{segment.id}'
            for i, force in enumerate(segment.forces):
                x = segment.node1.x + force.node1_dist * (segment.node2.x - segment.node1.x) / segment.length
                y = segment.node1.y + force.node1_dist * (segment.node2.y - segment.node1.y) / segment.length
                add_force_parts(f'{sid}_force_{i}', force, x, y)
            for i, torque in enumerate(segment.torques):
                t_dict[f'{sid}_torque_{i}'] = '?' if torque.unknown else torque.value

        eqs = [
            sp.Eq(sp.simplify(' + '.join(fx_dict.keys())), 0),
            sp.Eq(sp.simplify(' + '.join(fy_dict.keys())), 0),
            sp.Eq(sp.simplify(' + '.join(t_dict.keys())), 0)
        ]

        secondary_eqs = []
        unknowns = []
        all_symbols = []

        for d in (fx_dict, fy_dict, t_dict):
            for key, val in d.items():
                if val == '?':
                    unknowns.append(key)
                else:
                    secondary_eqs.append(sp.Eq(sp.Symbol(key), sp.simplify(val)))
                all_symbols.append(key)

        if len(unknowns) > 3:
            raise TooManyUnknownsError("Невозможно найти больше трёх неизвестных!")

        solution = sp.solve(eqs + secondary_eqs, sp.symbols(all_symbols))

        if len(solution) < 1:
            raise UnsolvableError("Невозможно найти решение либо система подвижна!")

        raw_answer = {str(k): float(v) for k, v in solution.items() if str(k) in unknowns}

        return Beam.format_readable_answers(raw_answer)

    def __repr__(self):
        return f"Beam(segments={self.get_segments()})"
    
    def to_dict(self):
        return {
            'nodes': [
                {
                    'id': node.id,
                    'x': node.x,
                    'y': node.y,
                    'support': {
                        'id': node.support.id,
                        'angle': node.support.angle,
                        'horizontal_force': {
                            'id': node.support.horizontal_force.id,
                            'value': node.support.horizontal_force.value,
                            'angle': node.support.horizontal_force.angle,
                            'node1_dist': node.support.horizontal_force.node1_dist,
                            'length': node.support.horizontal_force.length,
                            'unknown': node.support.horizontal_force.unknown
                        },
                        'vertical_force': {
                            'id': node.support.vertical_force.id,
                            'value': node.support.vertical_force.value,
                            'angle': node.support.vertical_force.angle,
                            'node1_dist': node.support.vertical_force.node1_dist,
                            'length': node.support.vertical_force.length,
                            'unknown': node.support.vertical_force.unknown
                        },
                        'torque': {
                            'id': node.support.torque.id,
                            'value': node.support.torque.value,
                            'node1_dist': node.support.torque.node1_dist,
                            'unknown': node.support.torque.unknown
                        }
                    } if node.support else None
                }
                for node in self.get_nodes()
            ],
            'segments': [
                {
                    'id': segment.id,
                    'node1_id': segment.node1.id,
                    'node2_id': segment.node2.id,
                    'forces': [
                        {
                            'id': force.id,
                            'value': force.value,
                            'angle': force.angle,
                            'node1_dist': force.node1_dist,
                            'length': force.length,
                            'unknown': force.unknown
                        } for force in segment.forces
                    ],
                    'torques': [
                        {
                            'id': torque.id,
                            'value': torque.value,
                            'node1_dist': torque.node1_dist,
                            'unknown': torque.unknown
                        } for torque in segment.torques
                    ]
                }
                for segment in self.get_segments()
            ]
        }

    def save_to_file(self, filename: str = "beam.bm"):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4)

    @classmethod
    def load_from_file(cls, filename: str = "beam.bm"):
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        id_node_map = {}
        beam = cls()

        for node_data in data['nodes']:
            node = Node(node_data['x'], node_data['y'], custom_id=node_data['id'])
            if node_data['support']:
                support_data = node_data['support']
                support = Support(
                    support_data['angle'],
                    support_data['horizontal_force']['value'],
                    support_data['vertical_force']['value'],
                    support_data['torque']['value'],
                    support_data['horizontal_force']['unknown'],
                    support_data['vertical_force']['unknown'],
                    support_data['torque']['unknown'],
                    custom_id=support_data['id']
                )
                # Принудительно выставляем ID внутренним объектам:
                support.horizontal_force.id = support_data['horizontal_force']['id']
                support.vertical_force.id = support_data['vertical_force']['id']
                support.torque.id = support_data['torque']['id']
                node.add_support(support)
            id_node_map[node.id] = beam.add_node(node)

        for segment_data in data['segments']:
            node1 = id_node_map[segment_data['node1_id']]
            node2 = id_node_map[segment_data['node2_id']]
            segment = BeamSegment(node1, node2, custom_id=segment_data['id'])

            for force_data in segment_data['forces']:
                force = Force(
                    force_data['value'],
                    force_data['angle'],
                    force_data['node1_dist'],
                    force_data['length'],
                    force_data['unknown'],
                    custom_id=force_data['id']
                )
                segment.add_force(force)

            for torque_data in segment_data['torques']:
                torque = Torque(
                    torque_data['value'],
                    torque_data['node1_dist'],
                    torque_data['unknown'],
                    custom_id=torque_data['id']
                )
                segment.add_torque(torque)

            beam.add_segment(segment)

        return beam
    
    def pretty_print(self, indent=0):
        pad = ' ' * indent
        lines = [f"{pad}Beam#{self.id}:"]
        lines.append(f"{pad} Nodes:")
        for node in self.get_nodes():
            lines.append(node.pretty_print(indent + 2))
        lines.append(f"{pad} Segments:")
        for segment in self.get_segments():
            lines.append(segment.pretty_print(indent + 2))
        return '\n'.join(lines)
    
    def split_beam_by_hinges(self) -> list["Beam"]:
        visited = set()
        subbeams = []

        def dfs_collect_nodes(start):
            stack = [start]
            local_nodes = set()

            while stack:
                node = stack.pop()
                if node in visited:
                    continue
                visited.add(node)
                local_nodes.add(node)

                for neighbor in self.graph.neighbors(node):
                    if neighbor in visited:
                        continue
                    if neighbor.hinge is not None:
                        local_nodes.add(neighbor)
                        continue
                    stack.append(neighbor)

            return local_nodes

        for node in self.get_nodes():
            if node in visited or node.hinge is not None:
                continue

            group_nodes = dfs_collect_nodes(node)
            subgraph = self.graph.subgraph(group_nodes)

            subbeam = Beam()
            for u, v, data in subgraph.edges(data=True):
                subbeam.add_segment(data['object'])

            subbeams.append(subbeam)

        return subbeams

    def _collect_equilibrium_equations(self):
        import sympy as sp

        self.reassign_ids()

        eqs = []
        variables = []
        fx, fy, mz = 0, 0, 0

        for node in self.get_nodes():
            x, y = node.x, node.y
            if node.support:
                h = node.support.horizontal_force
                v = node.support.vertical_force
                t = node.support.torque

                if h.unknown:
                    sx = sp.Symbol(f'node_{node.id}_horizontal_x') if not isinstance(h.value, sp.Basic) else h.value
                    variables.append(sx)
                    fx += sx
                else:
                    fx += h.part_x

                if v.unknown:
                    sy = sp.Symbol(f'node_{node.id}_vertical_y') if not isinstance(v.value, sp.Basic) else v.value
                    variables.append(sy)
                    fy += sy
                else:
                    fy += v.part_y

                if t.unknown:
                    st = sp.Symbol(f'node_{node.id}_torque') if not isinstance(t.value, sp.Basic) else t.value
                    variables.append(st)
                    mz += st
                else:
                    mz += t.value

        for segment in self.get_segments():
            x1, y1 = segment.node1.x, segment.node1.y
            dx = segment.node2.x - x1
            dy = segment.node2.y - y1

            for force in segment.forces:
                fx += force.part_x
                fy += force.part_y

                r = force.node1_dist / segment.length
                px = x1 + r * dx
                py = y1 + r * dy
                mz += force.part_x * (py - 0) - force.part_y * (px - 0)

            for torque in segment.torques:
                mz += torque.value

        eqs.extend([fx, fy, mz])
        return eqs, variables
    
    def solve_composite(self) -> dict[str, float]:
        import sympy as sp

        parts = self.split_beam_by_hinges()
        if len(parts) == 1:
            return parts[0].solve()

        equations = []
        symbols = set()
        solutions = {}

        hinge_force_map = {}  # {hinge_id: [fx1, fx2], [fy1, fy2]}

        for part_index, part in enumerate(parts):
            for node in part.get_nodes():
                if node.hinge:
                    hid = node.hinge.id

                    # создаём уникальные имена для каждой части
                    x_sym = sp.Symbol(f"hinge_{hid}_part{part_index}_x")
                    y_sym = sp.Symbol(f"hinge_{hid}_part{part_index}_y")
                    symbols.update([x_sym, y_sym])

                    # корректно добавим новую опору с символами
                    node.add_support(Support(
                        angle=0,
                        force_x=x_sym,
                        force_y=y_sym,
                        torque=0,
                        unknown_fx=True,
                        unknown_fy=True,
                        unknown_t=False
                    ))

                    if hid not in hinge_force_map:
                        hinge_force_map[hid] = {"x": [], "y": []}
                    hinge_force_map[hid]["x"].append(x_sym)
                    hinge_force_map[hid]["y"].append(y_sym)

        # Добавим уравнения: сумма сил в шарнире = 0
        for hid, forces in hinge_force_map.items():
            if len(forces["x"]) == 2:
                equations.append(forces["x"][0] + forces["x"][1])
            if len(forces["y"]) == 2:
                equations.append(forces["y"][0] + forces["y"][1])

        # Собираем уравнения равновесия всех подбалок
        for part in parts:
            try:
                part_eqs, part_vars = part._collect_equilibrium_equations()
                equations.extend(part_eqs)
                symbols.update(part_vars)
            except Exception as e:
                raise UnsolvableError(f"Ошибка при разборе подбалки: {e}")

        # Решаем систему
        try:
            solved = sp.solve(equations, list(symbols), dict=True)
            if not solved:
                raise TooManyUnknownsError("Система не может быть решена.")
            solved = solved[0]
        except Exception as e:
            raise UnsolvableError(f"Не удалось решить систему уравнений: {e}")

        # Собираем финальные ответы
        full_result = {}
        for part in parts:
            partial = part.solve(subs=solved)
            full_result.update(self.format_readable_answers(partial))

        # Добавим значения шарнирных сил
        for k, v in solved.items():
            if isinstance(k, sp.Symbol):
                full_result[str(k)] = float(v)

        return full_result
