import os
import sys
import pandas as pd

def ingest_screaming_frog(export_dir):
    """
    Reads internal_all.csv, normalizes common columns,
    and returns a filtered DataFrame for downstream processing.
    """
    master_file = os.path.join(export_dir, "internal_all.csv")
    
    if not os.path.exists(master_file):
        print(f"Error: Master file not found at {master_file}")
        sys.exit(1)
        
    try:
        # Screaming Frog exports are UTF-8 with potential commas inside quotes
        df = pd.read_csv(master_file, encoding='utf-8', low_memory=False)
        
        # Strip whitespaces from column names to normalize them
        df.columns = df.columns.str.strip()
        
        total_urls = len(df)
        print(f"Successfully loaded {total_urls} URLs from {master_file}")
        
        # Create a helper tracking frame for indexable HTML pages (where most rules live)
        # We preserve the original dataframe to track broken links/server errors across ALL content types.
        return df, total_urls
        
    except Exception as e:
        print(f"Failed to parse CSV: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ingest.py <export_dir>")
        sys.exit(1)
        
    target_dir = sys.argv[1]
    ingest_screaming_frog(target_dir)