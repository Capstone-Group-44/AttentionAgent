import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv(
    "C:\\Uni Tests, Assignments, Labs\\Capstone Project\\Manual Collection Dataset\\master_dataset.csv")

label_column = "label"

counts = df[label_column].value_counts()

print("Class distribution:")
print(counts)

plt.figure()
counts.plot(kind='bar')

plt.xlabel("Class")
plt.ylabel("Count")
plt.title("Focused vs Not Focused Distribution")

for i, v in enumerate(counts):
    plt.text(i, v, str(v), ha='center', va='bottom')

plt.tight_layout()
plt.show()
