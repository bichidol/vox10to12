import numpy as np
import re
import sys

def parse_ticks(tick_string, beats_per_measure):
    measure, beat, tick = map(int, re.findall(r'\d+', tick_string))
    total_ticks = (measure - 1) * beats_per_measure * 48 + (beat - 1) * 48 + tick
    return total_ticks

def interpolate(start_point, end_point, interpolation_type, beats_per_measure):
    start_tick, start_val = start_point
    end_tick, end_val = end_point
    interpolated_points = []
    total_ticks = end_tick - start_tick

    for tick in range(start_tick, end_tick + 1, 3):  #64th notes, spaced by 3 ticks
        ratio = (tick - start_tick) / total_ticks
        if interpolation_type == 'ease_in':
            value = start_val + (end_val - start_val) * np.sin(ratio * np.pi / 2)
        elif interpolation_type == 'ease_out':
            value = start_val + (end_val - start_val) * (1 - np.cos(ratio * np.pi / 2))
        elif interpolation_type == 'sharp':
            value = start_val + (end_val - start_val) * ratio
        interpolated_points.append((tick, value))

    return interpolated_points

def format_output(interpolated_points, beats_per_measure, extra_values):
    output_lines = []
    for tick, value in interpolated_points:
        measure = tick // (beats_per_measure * 48) + 1
        beat = (tick % (beats_per_measure * 48)) // 48 + 1
        sub_beat = tick % 48
        extra_values_str = '\t'.join(extra_values).strip()  
        output_lines.append(f"{measure:03},{beat:02},{sub_beat:02}\t{value:.6f}\t{extra_values_str}\n")
    return ''.join(output_lines)

def process_file(file_path, interpolation_type, time_signature):
    beats_per_measure = int(time_signature.split('/')[0])
    with open(file_path, 'r') as file:
        lines = file.readlines()

    points = []
    for line in lines:
        parts = line.split('\t')
        tick_string = parts[0]
        value = float(parts[1])
        total_ticks = parse_ticks(tick_string, beats_per_measure)
        points.append((total_ticks, value))

    interpolated_points = interpolate(points[0], points[-1], interpolation_type, beats_per_measure)

    output_lines = format_output(interpolated_points, beats_per_measure)
    with open(file_path, 'w') as file:
        file.writelines(output_lines)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <input_file> <interpolation_type> <time_signature>")
        sys.exit(1)

    input_file = sys.argv[1]
    interpolation_type = sys.argv[2].lower()
    time_signature = sys.argv[3]

    if interpolation_type not in ['ease_in', 'ease_out', 'sharp']:
        print("Error: Interpolation type must be 'ease_in', 'ease_out', or 'sharp'.")
        sys.exit(1)

    process_file(input_file, interpolation_type, time_signature)
