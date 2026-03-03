"""
File Name: combine_csv_files.py
Description: This script combines multiple CSV files from a specified folder into a single CSV file.
"""
import pandas as pd
import glob
import os

folder_path = "C:\\Uni Tests, Assignments, Labs\\Capstone Project\\Manual Collection Dataset"

csv_files = glob.glob(os.path.join(folder_path, "*.csv"))

combined_df = pd.concat([pd.read_csv(file)
                        for file in csv_files], ignore_index=True)

output_path = os.path.join(folder_path, "combined.csv")
combined_df.to_csv(output_path, index=False)

print("All CSV files combined successfully!")
