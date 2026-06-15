import os
import pandas as pd

def merge_all_years(start_year=2013, end_year=2025, output_filename="merged_all_years.csv"):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dfs = []
    
    print(f"Starting merge of yearly datasets from {start_year} to {end_year}...")
    
    for year in range(start_year, end_year + 1):
        filename = f"merged_years{year}.csv"
        # Look in the year's subfolder, e.g., '2017/merged_years2017.csv'
        rel_path = os.path.join(str(year), filename)
        
        # 1. Try finding relative to current working directory
        filepath = rel_path
        if not os.path.exists(filepath):
            # 2. Try finding relative to the script directory
            filepath = os.path.join(script_dir, rel_path)
            
        if not os.path.exists(filepath):
            # 3. Fallback: check if the file is directly in the workspace root
            filepath = filename
            if not os.path.exists(filepath):
                filepath = os.path.join(script_dir, filename)
                
        if os.path.exists(filepath):
            print(f"Found and reading: {filepath}")
            try:
                df = pd.read_csv(filepath)
                # Ensure a 'year' column exists to distinguish records
                if 'year' not in df.columns:
                    df['year'] = year
                dfs.append(df)
            except Exception as e:
                print(f"❌ Error reading {filepath}: {e}")

    if dfs:
        merged = pd.concat(dfs, ignore_index=True)
        output_filepath = os.path.join(script_dir, output_filename)
        merged.to_csv(output_filepath, index=False)
        print(f"\nSuccessfully merged {len(dfs)} files into {output_filepath}")
        print("Merged dataset shape:", merged.shape)
        if 'year' in merged.columns:
            print("Entries per year:\n", merged['year'].value_counts().sort_index())
    else:
        print("❌ No matching yearly CSV files were found to merge.")

if __name__ == "__main__":
    merge_all_years()