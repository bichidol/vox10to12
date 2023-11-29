import numpy as np
import re
import sys
from scipy.interpolate import CubicSpline, CubicHermiteSpline

def parse_ticks(tick_string, beats_per_measure):
    measure, beat, tick = map(int, re.findall(r'\d+', tick_string))
    total_ticks = (measure - 1) * beats_per_measure * 48 + (beat - 1) * 48 + tick
    return total_ticks

def parse_line(line):
    parts = line.split('\t')
    tick_string = parts[0]
    value = float(parts[1])
    extra_values = parts[2:]
    return tick_string, value, extra_values

def bezier_point(t, p0, p1, p2):
    return (1 - t)**2 * p0 + 2 * (1 - t) * t * p1 + t**2 * p2

def ease_in_cubic(t):
    return t**3

def ease_out_cubic(t):
    return 1 - (1 - t)**3

def ease_in_quint(t):
    return t**5

def ease_out_quint(t):
    return 1 - (1 - t)**5

def ease_in_circ(t):
    return 1 - np.sqrt(1 - t**2)

def ease_out_circ(t):
    return np.sqrt(1 - (t - 1)**2)

def ease_in_quad(t):
    return t**2

def ease_out_quad(t):
    return 1 - (1 - t)**2

def ease_in_quart(t):
    return t**4

def ease_out_quart(t):
    return 1 - (1 - t)**4

def ease_in_expo(t):
    return 2**(10 * (t - 1)) if t > 0 else 0

def ease_out_expo(t):
    return 1 - 2**(-10 * t)

def ease_in_elastic(t):
    c4 = (2 * np.pi) / 3
    return np.power(2, 10 * t - 10) * np.sin((t * 10 - 10.75) * c4) if t > 0 else 0

def ease_out_elastic(t):
    c4 = (2 * np.pi) / 3
    return 1 - np.power(2, -10 * t) * np.sin((t * 10 - 0.75) * c4)

def ease_in_back(t):
    c1 = 1.70158
    c3 = c1 + 1
    return c3 * t * t * t - c1 * t * t

def ease_out_back(t):
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * np.power(t - 1, 3) + c1 * np.power(t - 1, 2)

def ease_in_bounce(t):
    return 1 - ease_out_bounce(1 - t)

def ease_out_bounce(t):
    n1 = 7.5625
    d1 = 2.75
    if t < 1 / d1:
        return n1 * t * t
    elif t < 2 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75
    elif t < 2.5 / d1:
        t -= 2.25 / d1
        return n1 * t * t + 0.9375
    else:
        t -= 2.625 / d1
        return n1 * t * t + 0.984375
    
def interpolate(points, interpolation_type):
    print(points)
    interpolated_points = []

    if interpolation_type == 'cubic_spline':
        if len(points) < 3:
            print("Error: Cubic spline requires at least 3 points.")
            sys.exit(1)

        x = np.array([point[0] for point in points])
        y = np.array([point[1] for point in points])

        cs = CubicSpline(x, y, bc_type='natural')

        for tick in range(int(x[0]), int(x[-1]) + 1, 3):
            value = cs(tick)
            interpolated_points.append((tick, value))

    elif interpolation_type == 'cubic_hermite':
        if len(points) < 3 or any(point[2] is None for point in points):
            print("Error: Cubic Hermite spline requires at least 3 points with dydx values.")
            sys.exit(1)

        min_tick = min(point[0] for point in points)
        max_tick = max(point[0] for point in points)
        max_num_points = (max_tick - min_tick) // 3 + 1
        normalized_ticks = [(point[0] - min_tick) / (max_tick - min_tick) for point in points]

        x = np.array(normalized_ticks)
        y = np.array([point[1] for point in points])
        dydx = np.array([point[2] for point in points])

        chs = CubicHermiteSpline(x, y, dydx)

        normalized_x_dense = np.linspace(0, 1, max_num_points)

        evenly_spaced_ticks = [min_tick + i * 3 for i in range(max_num_points)]

        max_num_points = len(evenly_spaced_ticks)
        normalized_x_dense = np.linspace(0, 1, max_num_points)

        for i, norm_x_val in enumerate(normalized_x_dense):
            original_tick = evenly_spaced_ticks[i]
            value = chs(norm_x_val)
            interpolated_points.append((original_tick, value))

    else:
        start_tick, start_val, dydx = points[0]
        end_tick, end_val, dydx = points[-1]
        total_ticks = end_tick - start_tick
        
        for tick in range(start_tick, end_tick + 1, 3):
            ratio = (tick - start_tick) / total_ticks
            value = None
            if interpolation_type == 'ease_out_sin':
                value = start_val + (end_val - start_val) * np.sin(ratio * np.pi / 2)
            elif interpolation_type == 'ease_in_sin':
                value = start_val + (end_val - start_val) * (1 - np.cos(ratio * np.pi / 2))
            elif interpolation_type == 'sharp':
                value = start_val + (end_val - start_val) * ratio
            elif interpolation_type == 'ease_in_bezier':
                control_point = start_val
                value = bezier_point(ratio, start_val, control_point, end_val)
            elif interpolation_type == 'ease_in_bezier':
                control_point = end_val
                value = bezier_point(ratio, start_val, control_point, end_val)
            elif interpolation_type == 'ease_in_cubic':
                value = start_val + (end_val - start_val) * ease_in_cubic(ratio)
            elif interpolation_type == 'ease_out_cubic':
                value = start_val + (end_val - start_val) * ease_out_cubic(ratio)
            elif interpolation_type == 'ease_in_quint':
                value = start_val + (end_val - start_val) * ease_in_quint(ratio)
            elif interpolation_type == 'ease_out_quint':
                value = start_val + (end_val - start_val) * ease_out_quint(ratio)
            elif interpolation_type == 'ease_in_circ':
                value = start_val + (end_val - start_val) * ease_in_circ(ratio)
            elif interpolation_type == 'ease_out_circ':
                value = start_val + (end_val - start_val) * ease_out_circ(ratio)
            elif interpolation_type == 'ease_in_quad':
                value = start_val + (end_val - start_val) * ease_in_quad(ratio)
            elif interpolation_type == 'ease_out_quad':
                value = start_val + (end_val - start_val) * ease_out_quad(ratio)
            elif interpolation_type == 'ease_in_quart':
                value = start_val + (end_val - start_val) * ease_in_quart(ratio)
            elif interpolation_type == 'ease_out_quart':
                value = start_val + (end_val - start_val) * ease_out_quart(ratio)
            elif interpolation_type == 'ease_in_expo':
                value = start_val + (end_val - start_val) * ease_in_expo(ratio)
            elif interpolation_type == 'ease_out_expo':
                value = start_val + (end_val - start_val) * ease_out_expo(ratio)
            elif interpolation_type == 'ease_in_elastic':
                value = start_val + (end_val - start_val) * ease_in_elastic(ratio)
            elif interpolation_type == 'ease_out_elastic':
                value = start_val + (end_val - start_val) * ease_out_elastic(ratio)
            elif interpolation_type == 'ease_in_back':
                value = start_val + (end_val - start_val) * ease_in_back(ratio)
            elif interpolation_type == 'ease_out_back':
                value = start_val + (end_val - start_val) * ease_out_back(ratio)
            elif interpolation_type == 'ease_in_bounce':
                value = start_val + (end_val - start_val) * ease_in_bounce(ratio)
            elif interpolation_type == 'ease_out_bounce':
                value = start_val + (end_val - start_val) * ease_out_bounce(ratio)
            interpolated_points.append((tick, value))

    return interpolated_points

def format_output(interpolated_points, beats_per_measure, first_line_extra_values, second_line_extra_values):
    output_lines = []
    last_line_extra_values = second_line_extra_values[:] 
    
    for index, (tick, value) in enumerate(interpolated_points):
        measure = tick // (beats_per_measure * 48) + 1
        beat = (tick % (beats_per_measure * 48)) // 48 + 1
        sub_beat = tick % 48

        if index == 0:  
            extra_values_str = '\t'.join(first_line_extra_values).strip()
        elif index == len(interpolated_points) - 1: 
            extra_values_str = '\t'.join(last_line_extra_values).strip()
        else: 
            adjusted_extra_values = ['0'] + first_line_extra_values[1:]
            extra_values_str = '\t'.join(adjusted_extra_values).strip()

        output_lines.append(f"{measure:03},{beat:02},{sub_beat:02}\t{value:.6f}\t{extra_values_str}\n")
    return ''.join(output_lines)


def process_file(file_path, interpolation_type, time_signature):
    beats_per_measure = int(time_signature.split('/')[0])
    with open(file_path, 'r') as file:
        lines = file.readlines()

    points = []
    extra_values_list = []
    for line in lines:
        tick_string, value, extra_values = parse_line(line)
        print(extra_values)
        total_ticks = parse_ticks(tick_string, beats_per_measure)

        dydx = float(extra_values[7]) if len(extra_values) > 7 else None
        points.append((total_ticks, value, dydx))

        extra_values_list.append(extra_values[:6])

    if len(points) < 2:
        print("Error: Not enough lines for processing.")
        sys.exit(1)

    interpolated_points = interpolate(points, interpolation_type)

    output_lines = []
    ticks_per_measure = beats_per_measure * 48

    for index, (tick, value) in enumerate(interpolated_points):
        measure = tick // ticks_per_measure + 1
        beat = (tick % ticks_per_measure) // 48 + 1
        sub_beat = tick % 48

        if index == 0:
            extra_values_str = '\t'.join(extra_values_list[0]).strip()
        elif index == len(interpolated_points) - 1:
            extra_values_str = '\t'.join(extra_values_list[-1]).strip()
        else:
            adjusted_extra_values = ['0'] + extra_values_list[0][1:]
            extra_values_str = '\t'.join(adjusted_extra_values).strip()

        output_lines.append(f"{measure:03},{beat:02},{sub_beat:02}\t{value:.6f}\t{extra_values_str}\n")

    with open(file_path, 'w') as file:
        file.writelines(output_lines)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <input_file> <interpolation_type> <time_signature>")
        sys.exit(1)

    input_file = sys.argv[1]
    interpolation_type = sys.argv[2].lower()
    time_signature = sys.argv[3]

    if interpolation_type not in [
        'ease_in_sin', 'ease_out_sin', 'sharp',
        'ease_in_cubic', 'ease_out_cubic', 'ease_in_quint', 'ease_out_quint',
        'ease_in_circ', 'ease_out_circ', 'ease_in_quad', 'ease_out_quad',
        'ease_in_quart', 'ease_out_quart', 'ease_in_expo', 'ease_out_expo',
        'ease_in_elastic', 'ease_out_elastic', 'ease_in_back', 'ease_out_back',
        'ease_in_bounce', 'ease_out_bounce', 'cubic_spline', 'cubic_hermite'
    ]:
        print("Error: Interpolation type not recognized.")
        sys.exit(1)

    process_file(input_file, interpolation_type, time_signature)