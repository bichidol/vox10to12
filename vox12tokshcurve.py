import argparse
from scipy.interpolate import interp1d

def convert_to_ticks(measure, beat, tick, beats_per_measure, ticks_per_beat):
    return ((measure - 1) * beats_per_measure * ticks_per_beat) + ((beat - 1) * ticks_per_beat) + tick

def interpolate_to_24th_notes(x_values, y_values, ticks_per_beat):
    x_min, x_max = min(x_values), max(x_values)
    x_new = range(x_min, x_max + 1, ticks_per_beat // 3)
    interpolation_func = interp1d(x_values, y_values, kind='cubic', fill_value="extrapolate")
    y_new = interpolation_func(x_new)
    return x_new, y_new

def convert_from_ticks(tick, beats_per_measure, ticks_per_beat):
    measure = tick // (beats_per_measure * ticks_per_beat) + 1
    beat = (tick % (beats_per_measure * ticks_per_beat)) // ticks_per_beat + 1
    tick_remainder = int(tick % ticks_per_beat)  
    return measure, beat, tick_remainder

def main(input_file, time_signature):
    numerator, denominator = map(int, time_signature.split('/'))
    beats_per_measure = numerator
    ticks_per_beat = int((4 / denominator) * 48)

    with open(input_file, 'r') as file:
        data_lines = file.readlines()

    x_values = []
    y_values = []
    extra_values = []
    for line in data_lines:
        parts = line.strip().split('\t')
        measure, beat, tick = map(int, parts[0].split(','))
        y = float(parts[1])
        x = convert_to_ticks(measure, beat, tick, beats_per_measure, ticks_per_beat)
        x_values.append(x)
        y_values.append(y)
        extra_values.append(parts[2:]) 

    x_24th, y_24th = interpolate_to_24th_notes(x_values, y_values, ticks_per_beat)

    output_data = []
    for i, (x, y) in enumerate(zip(x_24th, y_24th)):
        measure, beat, tick = convert_from_ticks(x, beats_per_measure, ticks_per_beat)
        extras = '\t'.join(extra_values[min(i, len(extra_values) - 1)]) 
        output_line = "{},{:02d},{:02d}\t{:.6f}\t{}".format(measure, beat, tick, y, extras)
        output_data.append(output_line)

    with open('kshcurve.txt', 'w') as out_file:
        out_file.write('\n'.join(output_data))
        print(f"output written to kshcurve.txt")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Interpolate 64th note laser points to 24th notes for ksh format.')
    parser.add_argument('input_file', help='The input file containing the laser points.')
    parser.add_argument('time_signature', help='Time signature in the format of "4/4".')
    args = parser.parse_args()
    main(args.input_file, args.time_signature)
