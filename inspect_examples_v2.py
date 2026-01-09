
import os
import pandas as pd
from backend.data_utils import read_docx, read_pdf

DATA_DIR = r"c:\Users\anshu\Desktop\infinity\data"

def inspect_folder(folder_name):
    base_path = os.path.join(DATA_DIR, folder_name)
    print(f"\n{'='*50}")
    print(f"EXPERIMENT: {folder_name}")
    print(f"{'='*50}")

    # --- INPUT INSPECTION ---
    input_path = os.path.join(base_path, "input")
    print("\n[ INPUT FILES ]")
    if os.path.exists(input_path):
        files = os.listdir(input_path)
        if not files:
            print("  (Empty directory)")
        for f in files:
            full_path = os.path.join(input_path, f)
            print(f"  FILE: {f}")
            try:
                content = ""
                if f.endswith(".docx"):
                    content = read_docx(full_path)
                elif f.endswith(".pdf"):
                    content = read_pdf(full_path)
                
                if content:
                    print(f"     Preview: {content[:200]}...")
            except Exception as e:
                print(f"     Error reading: {e}")
    else:
        print("  (Missing input directory)")

    # --- OUTPUT INSPECTION ---
    output_path = os.path.join(base_path, "output")
    print("\n[ OUTPUT FILES ]")
    if os.path.exists(output_path):
        files = os.listdir(output_path)
        if not files:
            print("  (Empty directory)")
        for f in files:
            full_path = os.path.join(output_path, f)
            print(f"  FILE: {f}")
            if f.endswith(".xlsx"):
                try:
                    xl = pd.ExcelFile(full_path)
                    print(f"     Sheets: {xl.sheet_names}")
                    for sheet in xl.sheet_names:
                        df = pd.read_excel(full_path, sheet_name=sheet)
                        print(f"     --- Sheet: {sheet} ---")
                        print(f"     Columns: {list(df.columns)}")
                        print(f"     Row Count: {len(df)}")
                        print(f"     First Row Sample: {df.iloc[0].values if not df.empty else 'Empty'}")
                except Exception as e:
                    print(f"     Error reading Excel: {e}")
    else:
        print("  (Missing output directory)")

def main():
    if not os.path.exists(DATA_DIR):
        print(f"Data directory not found: {DATA_DIR}")
        return

    for item in os.listdir(DATA_DIR):
        if item.startswith("Example-") and os.path.isdir(os.path.join(DATA_DIR, item)):
            inspect_folder(item)

if __name__ == "__main__":
    main()
