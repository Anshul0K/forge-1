import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from exporters.json_exporter import export_to_json # type: ignore
from exporters.html_exporter import export_to_html # type: ignore

def run_reporter_agent(audit_results, output_dir="outputs"):
    print("[Agent: Reporter] Compiling audit logs and drafting client deliverable dashboards...")
    os.makedirs(output_dir, exist_ok=True)
    
    # Wraps your existing exporter configurations
    export_to_json(audit_results, os.path.join(output_dir, "report.json"))
    export_to_html(audit_results, os.path.join(output_dir, "report.html"))
    print(f"[Agent: Reporter] Outputs successfully written to {output_dir}/")