#!/usr/bin/env python3
"""
run.py — headless runner for the SEO Command Center.
"""
from __future__ import annotations
import argparse
import os
import sys
import time

# 1. Force Python to see local folders dynamically at runtime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "mcp"))

# 2. Standard absolute imports (type ignore keeps Pylance perfectly quiet)
import server # type: ignore
from agents import fixer # type: ignore

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("export_dir")
    ap.add_argument("--no-dashboard", action="store_true")
    args = ap.parse_args()

    if not args.no_dashboard:
        server.start_dashboard()
        print(f"[seo] dashboard: http://localhost:{server.PORT}", flush=True)
        time.sleep(1)

    t0 = time.time()
    
    # 1. Ingest
    server.seo_load(args.export_dir)
    
    # 2. Detect
    server.seo_detect()
    
    # 3. Fix
    print("[seo] Orchestrating local LLM Fixer Agent layer...", flush=True)
    fixer.execute_fixes()

    # 4. Recommendations
    issues = sorted(server.RUN["issues"], key=lambda x: {"High":0,"Medium":1,"Low":2}.get(x["severity"],3))
    recs = []
    for i in issues[:5]:
        recs.append(f"Fix the {i['count']} {i['severity']}-severity '{i['type']}' issue(s) first.")
    if not recs:
        recs.append("No issues detected on this crawl.")
    server.seo_recommend(recs)
    
    server.RUN["duration_sec"] = round(time.time() - t0, 1)
    
    # 5. Deliver
    server.seo_report()
    server.seo_export()

    s = server.RUN["summary"]
    print("\n=== SEO AUDIT RESULT ===")
    print(f"Site         : {server.RUN['site']}  ({server.RUN['urls']} URLs)")
    print(f"Total issues : {s['total_issues']}  (High {s['by_severity'].get('High',0)} / "
          f"Medium {s['by_severity'].get('Medium',0)} / Low {s['by_severity'].get('Low',0)})")
    print(f"Model Calls  : {server.RUN.get('model_calls', 0)}")
    print("Wrote outputs/report.json and outputs/report.html")

if __name__ == "__main__":
    main()