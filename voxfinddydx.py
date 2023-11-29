import numpy as np

def mbt_to_numerical_updated(mbt, beats_per_measure, ticks_per_beat):
    measures, beats, ticks = map(int, mbt.split(","))
    return ((measures - 1) * beats_per_measure * ticks_per_beat) + ((beats - 1) * ticks_per_beat) + ticks

def parse_data(file_path, beats_per_measure, ticks_per_beat):
    parsed_data = []
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split("\t")
            mbt, float_val = parts[0], float(parts[1]) 
            numerical_mbt = mbt_to_numerical_updated(mbt, beats_per_measure, ticks_per_beat)
            parsed_data.append((numerical_mbt, float_val))
    return parsed_data


def normalize_mbt(numerical_mbt, min_mbt, max_mbt):
    return (numerical_mbt - min_mbt) / (max_mbt - min_mbt)

def replace_mbt_with_normalized(data, min_mbt, max_mbt):
    return [(normalize_mbt(mbt, min_mbt, max_mbt), float_val) for mbt, float_val in data]

def find_cubic_polynomials_and_derivatives(control_points, interpolated_points):
    x_values = [point[0] for point in interpolated_points]
    y_values = [point[1] for point in interpolated_points]

    for i in range(len(control_points) - 1):
        start_x = control_points[i][0]
        end_x = control_points[i+1][0]
        segment_x = [x for x in x_values if start_x <= x <= end_x]
        segment_y = [y for x, y in zip(x_values, y_values) if start_x <= x <= end_x]

        coefficients = np.polyfit(segment_x, segment_y, 3)
        poly = np.poly1d(coefficients)
        print(f"Segment {i+1} Polynomial: {poly}")

        poly_deriv = poly.deriv()

        dydx_start = poly_deriv(start_x)
        dydx_end = poly_deriv(end_x)
        print(f"Segment {i+1} dy/dx at {start_x}: {dydx_start:.10f}")
        print(f"Segment {i+1} dy/dx at {end_x}: {dydx_end:.10f}")

def main():
    beats_per_measure = 4
    ticks_per_beat = 48

    control_points = parse_data('control_points.txt', beats_per_measure, ticks_per_beat)
    interpolated_points = parse_data('interpolated_points.txt', beats_per_measure, ticks_per_beat)

    all_numerical_mbts = [mbt for mbt, _ in control_points + interpolated_points]
    min_mbt, max_mbt = min(all_numerical_mbts), max(all_numerical_mbts)

    normalized_control_points = replace_mbt_with_normalized(control_points, min_mbt, max_mbt)
    normalized_interpolated_points = replace_mbt_with_normalized(interpolated_points, min_mbt, max_mbt)

    find_cubic_polynomials_and_derivatives(normalized_control_points, normalized_interpolated_points)

if __name__ == "__main__":
    main()
