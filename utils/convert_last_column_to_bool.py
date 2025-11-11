import csv

file_path = "iris_face_tracking.csv"

rows = []
with open(file_path, "r", newline="", encoding="utf-8") as infile:
    reader = csv.reader(infile)
    header = next(reader)
    rows.append(header)

    for row in reader:
        if not row:
            continue

        last_val = row[-1].strip()
        if last_val == "1":
            row[-1] = "True"
        elif last_val == "0":
            row[-1] = "False"
        rows.append(row)

# Write the modified rows back to the same file
with open(file_path, "w", newline="", encoding="utf-8") as outfile:
    writer = csv.writer(outfile)
    writer.writerows(rows)

print(f"Converted 1→True and 0→False in '{file_path}'")
