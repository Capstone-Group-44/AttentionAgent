import csv

file_path = "iris_face_tracking.csv"

# Read the file and replace the last column with "True"
rows = []
with open(file_path, "r", newline="", encoding="utf-8") as infile:
    reader = csv.reader(infile)
    header = next(reader)
    rows.append(header)

    for row in reader:
        if not row:
            continue
        row[-1] = "True"
        rows.append(row)

# Write the modified rows back to the same file
with open(file_path, "w", newline="", encoding="utf-8") as outfile:
    writer = csv.writer(outfile)
    writer.writerows(rows)

print(f"All values in the last column of '{file_path}' set to 'True'")
