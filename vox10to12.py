import sys

def convert_value(field_value):
    if 0 < field_value < 63:
        field_value = 129 - field_value
    scaled_value = (field_value * 32) / 127
    numerator = round(scaled_value)
    closest_fraction = numerator / 32
    if 0 < field_value < 63:
        closest_fraction = 1 - closest_fraction
    return closest_fraction

def process_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    in_format_version = False
    in_track1 = False
    in_track8 = False
    format_version = None

    processed_lines = []

    for line in lines:
        if line.strip() == '#FORMAT VERSION':
            in_format_version = True
        elif line.strip() == '#TRACK1':
            in_track1 = True
        elif line.strip() == '#TRACK8':
            in_track8 = True
        elif line.strip() == '#END':
            in_format_version = False
            in_track1 = False
            in_track8 = False

        if in_format_version:
            if line.strip().isdigit():
                format_version = int(line.strip())
                if format_version == 10:
                    line = '12\n'
        elif in_track1 or in_track8:
            parts = line.split('\t')
            if len(parts) > 1 and parts[1].replace('.', '', 1).isdigit():
                field_value = int(parts[1])
                if format_version == 10:
                    parts[1] = f"{convert_value(field_value):.6f}"
                else:
                    pass

                parts.insert(-1, '0')
                parts[-1] = parts[-1].strip()
                parts.append('0\n')
                line = '\t'.join(parts)

        processed_lines.append(line)

    new_file_path = file_path.replace('.vox', '_processed.vox')
    with open(new_file_path, 'w') as file:
        file.writelines(processed_lines)

    return new_file_path

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    processed_file_path = process_file(file_path)
    print(f"Processed file saved as: {processed_file_path}")