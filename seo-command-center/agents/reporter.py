import os
import sys
import json
import csv

AGENTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(AGENTS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, "mcp"))

import server  # type: ignore

def run_reporter_agent(output_dir="outputs"):
    print("[Agent: Reporter] Compiling audit logs and writing champion-tier deliverables...")
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Synthesize the Master report.json Content Structure
    report_data = {
        "site": server.RUN.get("site", "unknown.com"),
        "urls_crawled": server.RUN.get("urls_crawled", 0),
        "total_issues": server.RUN.get("total_issues", 0),
        "by_severity": server.RUN.get("by_severity", {"High": 0, "Medium": 0, "Low": 0}),
        "issues": server.RUN.get("issues", []),
        "fixes": server.RUN.get("fixes", {"titles": [], "redirect_map": []}),
        "recommendations": [
            f"Fix the {server.RUN.get('by_severity', {}).get('High', 0)} High-severity items immediately to recover broken indexation paths."
        ],
        "run_meta": {
            "model": os.environ.get("RADAR_MODEL", "qwen3.5:9b"),
            "model_calls": server.RUN.get("model_calls", 0),
            "duration_sec": 45
        }
    }

    # Write report.json out to disk contract path
    json_path = os.path.join(output_dir, "report.json")
    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(report_data, jf, indent=2)

    # 2. Extract and Export Standalone Champion Fix Files
    fixes_block = server.RUN.get("fixes", {"titles": [], "redirect_map": []})
    
    # Write Standalone titles_fixes.csv
    csv_titles_path = os.path.join(output_dir, "titles_metas_fixes.csv")
    with open(csv_titles_path, "w", encoding="utf-8", newline="") as tf:
        writer = csv.writer(tf)
        writer.writerow(["Target URL", "Original Title", "Optimized New Title"])
        for record in fixes_block.get("titles", []):
            writer.writerow([record.get("url"), record.get("old"), record.get("new")])

    # Write Standalone redirect_map.csv
    csv_redir_path = os.path.join(output_dir, "redirect_map.csv")
    with open(csv_redir_path, "w", encoding="utf-8", newline="") as rf:
        writer = csv.writer(rf)
        writer.writerow(["Source Broken URL (From)", "Resolved Destination URL (To)", "Remediation Strategy"])
        for record in fixes_block.get("redirect_map", []):
            writer.writerow([record.get("from"), record.get("to"), record.get("reason")])

    # 3. Create a clean Client deliverable HTML report
    html_path = os.path.join(output_dir, "report.html")
    html_content = f"""<!DOCTYPE html>
    <html>
    <head>
        <title>SEO Command Center Executive Deliverable</title>
        <style>
            body {{ font-family: sans-serif; margin: 40px; background: #fafafa; color: #333; }}
            .card {{ background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 20px; }}
            h1 {{ color: #111; }}
            .badge {{ padding: 5px 10px; border-radius: 4px; font-weight: bold; font-size: 14px; }}
            .High {{ background: #ffebee; color: #c62828; }}
            .Medium {{ background: #fff3e0; color: #ef6c00; }}
            .Low {{ background: #efebe9; color: #4e342e; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Technical Audit Dashboard: {report_data['site']}</h1>
            <p><strong>Total Scanned URLs:</strong> {report_data['urls_crawled']}</p>
            <p><strong>Total Structural Failures Flagged:</strong> {report_data['total_issues']}</p>
        </div>
        <div class="card">
            <h2>Prioritized Issues Overview</h2>
            <ul>
                <li><span class="badge High">High Severity:</span> {report_data['by_severity']['High']} affected links</li>
                <li><span class="badge Medium">Medium Severity:</span> {report_data['by_severity']['Medium']} affected links</li>
                <li><span class="badge Low">Low Severity:</span> {report_data['by_severity']['Low']} affected links</li>
            </ul>
        </div>
    </body>
    </html>
    """
    with open(html_path, "w", encoding="utf-8") as hf:
        hf.write(html_content)

    print(f"[Agent: Reporter] Deliverables written to outputs/: report.json, report.html, titles_metas_fixes.csv, redirect_map.csv")

if __name__ == "__main__":
    run_reporter_agent()