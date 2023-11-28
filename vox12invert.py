import re
import sys

def parse_ticks(tick_string, beats_per_measure):
    measure, beat, tick = map(int, re.findall(r'\d+', tick_string))
    total_ticks = (measure - 1) * beats_per_measure * 48 + (beat - 1) * 48 + tick
    return total_ticks, measure, beat, tick

def format_ticks(total_ticks, beats_per_measure):
    measure = total_ticks // (beats_per_measure * 48) + 1
    remaining_ticks = total_ticks % (beats_per_measure * 48)
    beat = remaining_ticks // 48 + 1
    tick = remaining_ticks % 48
    return f"{measure:03},{beat:02},{tick:02}"

def process_file(file_path, time_signature, measure_offset=0, beat_offset=0):
    beats_per_measure = int(time_signature.split('/')[0])
    output_lines = []

    with open(file_path, 'r') as file:
        for line in file:
            parts = line.split('\t')
            tick_string, value = parts[0], float(parts[1])
            extra_values = parts[2:]

            # Reverse the float value
            reversed_value = 1.0 - value

            # Parse the tick string and apply offsets
            total_ticks, _, _, _ = parse_ticks(tick_string, beats_per_measure)
            total_ticks += measure_offset * beats_per_measure * 48 + beat_offset * 48
            new_tick_string = format_ticks(total_ticks, beats_per_measure)

            # Construct the new line
            new_line = f"{new_tick_string}\t{reversed_value:.6f}\t" + '\t'.join(extra_values)
            output_lines.append(new_line)

    return output_lines

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python script.py <input_file> <time_signature> <measure_offset> <beat_offset>")
        sys.exit(1)

    input_file = sys.argv[1]
    time_signature = sys.argv[2]
    measure_offset = int(sys.argv[3])
    beat_offset = int(sys.argv[4])

    processed_lines = process_file(input_file, time_signature, measure_offset, beat_offset)
    with open(input_file, 'w') as file:
        file.writelines(processed_lines)
