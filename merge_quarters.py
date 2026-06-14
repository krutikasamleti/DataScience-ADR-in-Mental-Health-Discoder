import os
import glob
import re
import csv

def merge_quarters_by_year(directory="."):
    # Find all CSV files matching the pattern 20XXqX.csv (case-insensitive)
    csv_files = glob.glob(os.path.join(directory, "*q[1-4].csv"))
    
    # Group files by year
    years_data = {}
    for f in csv_files:
        filename = os.path.basename(f)
        match = re.match(r'^(\d{4})q[1-4]\.csv$', filename, re.IGNORECASE)
        if match:
            year = match.group(1)
            if year not in years_data:
                years_data[year] = []
            years_data[year].append(f)
            
    if not years_data:
        print("No quarterly CSV files (e.g. 2017q1.csv) found to merge.")
        return

    # Process each year
    for year, files in sorted(years_data.items()):
        # Sort files so q1, q2, q3, q4 are merged in order
        files.sort()
        
        output_file = os.path.join(directory, f"{year}.csv")
        print(f"Merging {len(files)} quarters for {year} into {output_file}...")
        
        first_file = True
        total_rows = 0
        
        with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            writer = None
            
            for file_path in files:
                print(f"  Reading {os.path.basename(file_path)}...")
                with open(file_path, 'r', encoding='utf-8') as infile:
                    reader = csv.reader(infile)
                    
                    try:
                        header = next(reader)
                    except StopIteration:
                        # Empty file
                        continue
                        
                    if first_file:
                        writer = csv.writer(outfile)
                        # Write the header only from the first file
                        writer.writerow(header)
                        first_file = False
                        
                    for row in reader:
                        writer.writerow(row)
                        total_rows += 1
                        
        print(f"Completed merging {year}. Total data rows: {total_rows}\n")

if __name__ == "__main__":
    # Resolve directory to the folder containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    merge_quarters_by_year(script_dir)
