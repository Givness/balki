from structures import *
import sympy as sp

eqs = [
    sp.Eq(sp.simplify('node_1_horizontal_x + hinge_1_force_x'), 0),
    sp.Eq(sp.simplify('node_1_vertical_y + segment_2_force_6_y + segment_2_force_5_y + hinge_1_force_y'), 0),
    sp.Eq(sp.simplify('node_1_vertical_y_torque + segment_1_torque_3 + hinge_1_force_y_torque + hinge_1_force_x_torque'), 0),
    sp.Eq(sp.simplify('hinge_1_force_x_opp + segment_3_force_7_x + node_4_horizontal_x'), 0),
    sp.Eq(sp.simplify('hinge_1_force_y_opp + node_4_vertical_y'), 0),
    sp.Eq(sp.simplify('hinge_1_force_x_opp_torque + hinge_1_force_y_opp_torque + segment_3_force_7_x_torque + node_4_vertical_y_torque'), 0),
]

secondary_eqs = [
    sp.Eq(sp.simplify('segment_2_force_5_y'), -15000),
    sp.Eq(sp.simplify('segment_2_force_6_y'), -4000),
    sp.Eq(sp.simplify('segment_3_force_7_x'), -10000),
    sp.Eq(sp.simplify('segment_1_torque_3'), -20000),

    sp.Eq(sp.simplify('node_1_horizontal_x_torque'), 0),
    sp.Eq(sp.simplify('node_4_horizontal_x_torque'), 0),
    sp.Eq(sp.simplify('hinge_1_force_x_torque'), sp.simplify('-2*hinge_1_force_x')),
    sp.Eq(sp.simplify('node_1_vertical_y_torque'), sp.simplify('-node_1_vertical_y')),
    sp.Eq(sp.simplify('node_4_vertical_y_torque'), sp.simplify('2*node_4_vertical_y')),
    sp.Eq(sp.simplify('hinge_1_force_y_torque'), sp.simplify('hinge_1_force_y')),
    sp.Eq(sp.simplify('segment_2_force_5_y_torque'), 0),
    sp.Eq(sp.simplify('segment_3_force_7_x_torque'), sp.simplify('-segment_3_force_7_x')),
    sp.Eq(sp.simplify('segment_2_force_6_y_torque'), 0),

    sp.Eq(sp.simplify('hinge_1_force_x_opp'), sp.simplify('-hinge_1_force_x')),
    sp.Eq(sp.simplify('hinge_1_force_y_opp'), sp.simplify('-hinge_1_force_y')),
    sp.Eq(sp.simplify('hinge_1_force_x_opp_torque'), sp.simplify('-2*hinge_1_force_x_opp')),
    sp.Eq(sp.simplify('hinge_1_force_y_opp_torque'), sp.simplify('hinge_1_force_y_opp')),
]

symbols =[
    'node_1_horizontal_x',
    'node_4_horizontal_x',
    'hinge_1_force_x',
    'node_1_vertical_y',
    'node_4_vertical_y',
    'hinge_1_force_y',
    'segment_2_force_5_y',
    'segment_3_force_7_x',
    'segment_2_force_6_y',
    'segment_1_torque_3',
    
    'node_1_horizontal_x_torque',
    'node_4_horizontal_x_torque',
    'hinge_1_force_x_torque',
    'node_1_vertical_y_torque',
    'node_4_vertical_y_torque',
    'hinge_1_force_y_torque',
    'segment_2_force_5_y_torque',
    'segment_3_force_7_x_torque',
    'segment_2_force_6_y_torque',

    'hinge_1_force_x_opp',
    'hinge_1_force_y_opp',
    'hinge_1_force_x_opp_torque',
    'hinge_1_force_y_opp_torque',
]

unknown = [
    'node_1_horizontal_x',
    'node_4_horizontal_x',
    'hinge_1_force_x',
    'node_1_vertical_y',
    'node_4_vertical_y',
    'hinge_1_force_y'
]


solution = sp.solve(eqs + secondary_eqs, sp.sympify(symbols))

filtered_decimal_solution = {
    str(k): float(v.evalf()) for k, v in solution.items() if str(k) in unknown
}

print(filtered_decimal_solution)