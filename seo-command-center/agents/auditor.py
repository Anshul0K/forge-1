import os
import sys
# Align with your path setup
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from seo.detector import execute_analysis # type: ignore

def run_audit_agent(urls_data):
    print("[Agent: Auditor] Commencing deterministic rulebook analysis...")
    # Wraps your existing working detector logic
    return execute_analysis(urls_data)