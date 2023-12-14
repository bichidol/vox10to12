import argparse
from scipy.interpolate import interp1d

def convert_to_ticks(measure, beat, tick, beats_per_measure, ticks_per_beat):
    return ((measure - 1) * beats_per_measure * ticks_per_beat) + ((beat - 1) * ticks_per_beat) + tick

def interpolate_to_24th_notes(x_values, y_values):
    x_min, x_max = min(x_values), max(x_values)
    step_size = 8  

    if (x_max - x_min) % step_size != 0:
        step_size = 12  

    x_new = range(x_min, x_max + 1, step_size)
    interpolation_func = interp1d(x_values, y_values, kind='cubic', fill_value="extrapolate")
    y_new = interpolation_func(x_new)
    y_new = [0 if abs(y) < 1e-6 else y for y in y_new]
    return x_new, y_new

def convert_from_ticks(tick, beats_per_measure, ticks_per_beat):
    measure = tick // (beats_per_measure * ticks_per_beat) + 1
    beat = (tick % (beats_per_measure * ticks_per_beat)) // ticks_per_beat + 1
    tick_remainder = int(tick % ticks_per_beat)  
    return measure, beat, tick_remainder

def interpolate_data(x_values, y_values, extra_values):
    segments = []
    start_index = 0
    for i in range(1, len(x_values)):
        if x_values[i] == x_values[i - 1]:
            segments.append((x_values[start_index:i], y_values[start_index:i], extra_values[start_index:i]))
            start_index = i
    segments.append((x_values[start_index:], y_values[start_index:], extra_values[start_index:]))
    
    interpolated_data = []
    for seg_idx, (x_segment, y_segment, extras_segment) in enumerate(segments):
        x_new, y_new = interpolate_to_24th_notes(x_segment, y_segment)
        for x_idx, (x, y) in enumerate(zip(x_new, y_new)):
            if seg_idx == 0 and x_idx == 0: 
                extras = extra_values[0]
            else:
                original_index = next((idx for idx, original_x in enumerate(x_segment) if original_x >= x), 0)
                extras = extras_segment[min(original_index, len(extras_segment) - 1)]
            interpolated_data.append((x, y, extras))
    
    return interpolated_data

def main(input_file, time_signature):
    numerator, denominator = map(int, time_signature.split('/'))
    beats_per_measure = numerator
    ticks_per_beat = int((4 / denominator) * 48)

    with open(input_file, 'r') as file:
        data_lines = file.readlines()

    x_values, y_values, extra_values = [], [], []
    for line in data_lines:
        parts = line.strip().split('\t')
        measure, beat, tick = map(int, parts[0].split(','))
        y = float(parts[1])
        x = convert_to_ticks(measure, beat, tick, beats_per_measure, ticks_per_beat)
        x_values.append(x)
        y_values.append(y)
        extra_values.append(parts[2:]) 

    interpolated_data = interpolate_data(x_values, y_values, extra_values)

    output_data = []
    for x, y, extras in interpolated_data:
        measure, beat, tick = convert_from_ticks(x, beats_per_measure, ticks_per_beat)
        output_line = "{:03d},{:02d},{:02d}\t{:.6f}\t{}".format(measure, beat, tick, y, '\t'.join(extras))
        output_data.append(output_line)

    with open('kshcurve.txt', 'w') as out_file:
        out_file.write('\n'.join(output_data))
        print("output written to kshcurve.txt")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Interpolate 64th note laser points to 24th notes for ksh format.')
    parser.add_argument('input_file', help='The input file containing the laser points.')
    parser.add_argument('time_signature', help='Time signature in the format of "4/4".')
    args = parser.parse_args()
    main(args.input_file, args.time_signature)