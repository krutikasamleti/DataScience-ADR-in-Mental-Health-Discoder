# ## 🔄 Flow of the Script

# ### **Step 1: Setup**
# - Import libraries (`csv`, `os`).
# - Define file paths for input files (DEMO, REAC, DRUG, INDI, OUTC).
# - Define output file path.
# - Define **mental health keywords list**.

# ---

# ### **Step 2: Identify Teen Patients (DEMO file)**
# - Open **DEMO25Q1.txt**.
# - Read each patient’s demographic info.
# - If **age is between 10–18 years** → add their `primaryid` to `target_pids`.
# - Store their demographic details in `demo_data`.

# ---

# ### **Step 3: Filter for Mental Health Patients**
# - Create empty set `mh_pids`.

# **(a) Check REAC file — Reactions**
# - Open **REAC25Q1.txt**.
# - For each patient in `target_pids`:
#   - Collect their reaction terms (`pt`).
#   - If reaction contains a **mental health keyword** → add patient to `mh_pids`.

# **(b) Check INDI file — Indications**
# - Open **INDI25Q1.txt**.
# - For each patient in `target_pids`:
#   - Collect their indication terms (`indi_pt`).
#   - If indication contains a **mental health keyword** → add patient to `mh_pids`.

# 👉 **This is where the mental health keywords list is used.**  
# It acts like a filter to decide which patients are considered “mental health cases.”

# ---

# ### **Step 4: Collect Outcomes (OUTC file)**
# - Open **OUTC25Q1.txt**.
# - For each patient in `mh_pids`:
#   - Collect their outcomes (`outc_cod`).
#   - Store in `outc_data`.

# ---

# ### **Step 5: Collect Drug Information (DRUG file)**
# - Open **DRUG25Q1.txt**.
# - For each patient in `mh_pids`:
#   - Collect drug details (name, dose, route, frequency, etc.).
#   - Link with:
#     - **DEMO data** (age, sex, country).
#     - **REAC data** (reactions).
#     - **INDI data** (indications).
#     - **OUTC data** (outcomes).
#   - Build a **compiled row** with all this info.

# ---

# ### **Step 6: Write Final Dataset**
# - Open output file (`mental_health_extracted_data.tsv`).
# - Write headers (column names).
# - Write all compiled rows (one per patient-drug record).
# - Print success message.

# ---

# ## ⚡ In One Sentence
# The script:  
# **Finds teenagers → checks if they have mental health terms in reactions/indications → collects their outcomes → collects their drug info → saves everything into one clean TSV file.**

# ---

# Would you like me to **draw a layered diagram** showing how DEMO → REAC/INDI → OUTC → DRUG → OUTPUT connect together? That would make the flow visually clear.
import csv
import os
import sys
import glob

# Load MedDRA PT terms
def load_meddra_pts(csv_file):
    pt_set = set()

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            pt = row["PT"].strip().lower()
            if pt:
                pt_set.add(pt)

    return pt_set

# Path to your PT CSV
MEDDRA_PT_FILE = "Meddra_PT_Unique_Keywords_PT.csv"

# Load all PT terms
mental_health_pts = load_meddra_pts(MEDDRA_PT_FILE)

# Keywords for identifying mental health illnesses

def is_mental_health_term(term):
    if not term:
        return False

    return term.strip().lower() in mental_health_pts

def extract_data(data_dir, output_dir):
    demo_files = glob.glob(os.path.join(data_dir, "DEMO*.txt"))
    if not demo_files:
        print(f"No DEMO file found in {data_dir}. Skipping.")
        return
    
    demo_file = demo_files[0]
    suffix = os.path.basename(demo_file)[4:-4] # e.g. "25Q1" from "DEMO25Q1.txt"
    
    reac_file = os.path.join(data_dir, f"REAC{suffix}.txt")
    drug_file = os.path.join(data_dir, f"DRUG{suffix}.txt")
    indi_file = os.path.join(data_dir, f"INDI{suffix}.txt")
    outc_file = os.path.join(data_dir, f"OUTC{suffix}.txt")
    
    # Check if all files exist
    for f in [demo_file, reac_file, drug_file, indi_file, outc_file]:
        if not os.path.exists(f):
            print(f"Error: Missing expected file {f}")
            return
            
    output_file = os.path.join(output_dir, f"ram_mental_health_extracted_data_1{suffix}.csv")

    print(f"--- Processing {data_dir} ---")
    print("1. Identifying target patients from DEMO (Age 10-18)...")
    target_pids = set()
    demo_data = {}
    
    with open(demo_file, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f, delimiter='$')
        header = next(reader)
        
        # 'sex' column is called 'gndr_cod' in older FAERS files (pre-2014)
        sex_col = 'sex' if 'sex' in header else ('gndr_cod' if 'gndr_cod' in header else None)
        if sex_col is None:
            print("Warning: No sex/gndr_cod column found in DEMO file. Sex will be blank.")

        col_idx = {
            'primaryid': header.index('primaryid'),
            'caseid': header.index('caseid'),
            'age': header.index('age'),
            'age_cod': header.index('age_cod'),
            'age_grp': header.index('age_grp') if 'age_grp' in header else -1,
            'sex': header.index(sex_col) if sex_col else -1,
            'wt': header.index('wt') if 'wt' in header else -1,
            'reporter_country': header.index('reporter_country') if 'reporter_country' in header else -1,
            'occr_country': header.index('occr_country') if 'occr_country' in header else -1
        }
        
        for row in reader:
            if len(row) > col_idx['age']:
                age_str = row[col_idx['age']].strip()
                age_cod = row[col_idx['age_cod']].strip().upper()
                
                if age_str and age_cod == "YR":
                    try:
                        age = float(age_str)
                        if 10 <= age <= 18:
                            pid = row[col_idx['primaryid']]
                            target_pids.add(pid)
                            demo_data[pid] = {
                                'caseid': row[col_idx['caseid']] if col_idx['caseid'] != -1 else '',
                                'age': age_str,
                                'age_grp': row[col_idx['age_grp']] if col_idx['age_grp'] != -1 and len(row) > col_idx['age_grp'] else '',
                                'sex': row[col_idx['sex']] if col_idx['sex'] != -1 and len(row) > col_idx['sex'] else '',
                                'wt': row[col_idx['wt']] if col_idx['wt'] != -1 and len(row) > col_idx['wt'] else '',
                                'reporter_country': row[col_idx['reporter_country']] if col_idx['reporter_country'] != -1 and len(row) > col_idx['reporter_country'] else '',
                                'occr_country': row[col_idx['occr_country']] if col_idx['occr_country'] != -1 and len(row) > col_idx['occr_country'] else ''
                            }
                    except ValueError:
                        pass
                        
    print(f"   Found {len(target_pids)} patients matching the age criteria.")
    
    print("2. Filtering target patients for Mental Health indications/reactions...")
    mh_pids = set()
    
    # Check REAC
    reactions_data = {}
    with open(reac_file, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f, delimiter='$')
        header = next(reader)
        pid_idx = header.index("primaryid")
        pt_idx = header.index("pt")
        drug_rec_act_idx = header.index("drug_rec_act") if "drug_rec_act" in header else -1
        
        for row in reader:
            if len(row) > pt_idx:
                pid, pt = row[pid_idx], row[pt_idx]
                if pid in target_pids:
                    drug_rec_act = row[drug_rec_act_idx] if drug_rec_act_idx != -1 and len(row) > drug_rec_act_idx else ""
                    if pid not in reactions_data:
                        reactions_data[pid] = []
                    reactions_data[pid].append(f"{pt} (Rec Act: {drug_rec_act})")
                    
                    if is_mental_health_term(pt):
                        mh_pids.add(pid)

    # Check INDI
    indications_data = {}
    with open(indi_file, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f, delimiter='$')
        header = next(reader)
        pid_idx = header.index("primaryid")
        indi_drug_seq_idx = header.index("indi_drug_seq")
        indi_pt_idx = header.index("indi_pt") if "indi_pt" in header else -1
        
        for row in reader:
            if len(row) > indi_drug_seq_idx:
                pid, indi_drug_seq = row[pid_idx], row[indi_drug_seq_idx]
                if pid in target_pids:
                    indi_pt = row[indi_pt_idx] if indi_pt_idx != -1 and len(row) > indi_pt_idx else ""
                    key = (pid, indi_drug_seq)
                    if key not in indications_data:
                        indications_data[key] = []
                    indications_data[key].append(indi_pt)
                    
                    if is_mental_health_term(indi_pt):
                        mh_pids.add(pid)

    print(f"   Found {len(mh_pids)} mental health patients aged 10-18.")

    print("3. Extracting OUTC data for matching patients...")
    outc_data = {}
    with open(outc_file, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f, delimiter='$')
        header = next(reader)
        pid_idx = header.index("primaryid")
        outc_cod_idx = header.index("outc_cod")
        
        for row in reader:
            if len(row) > outc_cod_idx:
                pid = row[pid_idx]
                if pid in mh_pids:
                    outc_cod = row[outc_cod_idx]
                    if pid not in outc_data:
                        outc_data[pid] = []
                    outc_data[pid].append(outc_cod)

    print("4. Extracting DRUG data and compiling final dataset...")
    compiled_rows = []
    with open(drug_file, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f, delimiter='$')
        header = next(reader)
        
        col_idx = {
            'primaryid': header.index('primaryid'),
            'drug_seq': header.index('drug_seq'),
            'drugname': header.index('drugname'),
            'role_cod': header.index('role_cod'),
            'dose_amt': header.index('dose_amt') if 'dose_amt' in header else -1,
            'dose_unit': header.index('dose_unit') if 'dose_unit' in header else -1,
            'dose_freq': header.index('dose_freq') if 'dose_freq' in header else -1,
            'route': header.index('route') if 'route' in header else -1,
            'cum_dose_chr': header.index('cum_dose_chr') if 'cum_dose_chr' in header else -1
        }
        
        for row in reader:
            if len(row) > col_idx['drugname']:
                pid = row[col_idx['primaryid']]
                if pid in mh_pids:
                    drug_seq = row[col_idx['drug_seq']]
                    
                    # Gather DRUG fields
                    drugname = row[col_idx['drugname']]
                    role_cod = row[col_idx['role_cod']]
                    dose_amt = row[col_idx['dose_amt']] if col_idx['dose_amt'] != -1 and len(row) > col_idx['dose_amt'] else ""
                    dose_unit = row[col_idx['dose_unit']] if col_idx['dose_unit'] != -1 and len(row) > col_idx['dose_unit'] else ""
                    dose_freq = row[col_idx['dose_freq']] if col_idx['dose_freq'] != -1 and len(row) > col_idx['dose_freq'] else ""
                    route = row[col_idx['route']] if col_idx['route'] != -1 and len(row) > col_idx['route'] else ""
                    cum_dose_chr = row[col_idx['cum_dose_chr']] if col_idx['cum_dose_chr'] != -1 and len(row) > col_idx['cum_dose_chr'] else ""
                    
                    # Gather DEMO fields
                    demo = demo_data[pid]
                    
                    # Gather REAC fields
                    reacs = " | ".join(set(reactions_data.get(pid, [])))
                    
                    # Gather INDI fields (link via primaryid + drug_seq)
                    indis = " | ".join(set(indications_data.get((pid, drug_seq), [])))
                    
                    # Gather OUTC fields
                    outcs = " | ".join(set(outc_data.get(pid, [])))
                    
                    compiled_rows.append([
                        pid, demo['caseid'], demo['age'], demo['age_grp'], demo['sex'], demo['wt'], demo['reporter_country'], demo['occr_country'],
                        drugname, role_cod, dose_amt, dose_unit, dose_freq, route, cum_dose_chr, drug_seq,
                        indis, # indication for this specific drug
                        reacs, # reactions for this patient
                        outcs  # outcomes for this patient
                    ])

    print(f"   Writing {len(compiled_rows)} compiled rows to {output_file}...")
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter=',')
        
        # Write headers
        writer.writerow([
            "primaryid", "caseid", "age", "age_grp", "sex", "wt", "reporter_country", "occr_country",
            "drugname", "role_cod", "dose_amt", "dose_unit", "dose_freq", "route", "cum_dose_chr", "drug_seq",
            "indi_pt (for drug_seq)",
            "pt & drug_rec_act",
            "outc_cod"
        ])
        
        # Write data
        for row in compiled_rows:
            writer.writerow(row)

    print("Extraction successfully completed!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        data_dirs = sys.argv[1:]
    else:
        # Auto-detect folders like 2025Q1/ASCII or faers_ascii_2013q1/ascii
        data_dirs = glob.glob(os.path.join(".", "*", "ASCII")) + glob.glob(os.path.join(".", "*", "ascii"))
        if not data_dirs:
            print("No ASCII/ascii folders found in the current directory. Please provide a folder path as an argument.")
            sys.exit(1)
            
    output_dir = os.path.abspath(".")
    for d in data_dirs:
        extract_data(d, output_dir)
