import os
import csv
import sys

def ingest_screaming_frog(export_dir):
    """
    Reads internal_all.csv and returns a list of dictionaries.
    Uses the standard csv module to avoid external dependencies.
    """
    master_file = os.path.join(export_dir, "internal_all.csv")

    if not os.path.exists(master_file):
        print(f"Error: Master file not found at {master_file}")
        sys.exit(1)

    try:
        with open(master_file, encoding='utf-8-sig', newline='') as f:
            # Use DictReader to get rows as dictionaries
            reader = csv.DictReader(f)
            rows = list(reader)

            # Normalize column names by stripping whitespace
            for row in rows:
                row = {k.strip(): v for k, v in row.items()}

            # Note: The above list comprehension doesn't mutate the rows in the list
            # We need to actually rebuild the list with stripped keys
            normalized_rows = [{k.strip(): v for k, v in row.items()} for row in rows]

            total_urls = len(normalized_rows)
            print(f"Successfully loaded {total_urls} URLs from {master_file}")

            return normalized_rows, total_urls

    except Exception as e:
        print(f"Failed to parse CSV: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ingest.py <export_dir>")
        sys.exit(1)

    target_dir = sys.argv[1]
    ingest_screaming_frog(target_dir)
