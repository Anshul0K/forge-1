import os
import sys

# Maintain package imports for runtime CLI execution
AGENTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(AGENTS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, "mcp"))

import server  # type: ignore

def _int(val):
    try:
        return int(val)
    except (ValueError, TypeError):
        return 0

def _float(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0

def is_html(row):
    return "text/html" in row.get("Content Type", "").lower()

def is_indexable(row):
    return row.get("Indexability", "").lower() == "indexable"

def run_audit_agent():
    print("[Agent: Auditor] Commencing deterministic rulebook analysis...")
    
    if "rows" not in server.RUN or not server.RUN["rows"]:
        print("Error: No crawl data found in server memory to audit.")
        return

    rows = server.RUN["rows"]
    
    # 1. Tracking Maps for Duplicates
    titles_map = {}
    metas_map = {}
    h1s_map = {}
    
    for row in rows:
        if row.get("Status Code") == "200" and is_indexable(row) and is_html(row):
            t = row.get("Title 1", "").strip()
            m = row.get("Meta Description 1", "").strip()
            if t: titles_map[t] = titles_map.get(t, []) + [row["Address"]]
            if m: metas_map[m] = metas_map.get(m, []) + [row["Address"]]
            
        if row.get("Status Code") == "200" and is_html(row):
            h1 = row.get("H1-1", "").strip()
            if h1: h1s_map[h1] = h1s_map.get(h1, []) + [row["Address"]]

    # 2. Build Redirect Graph to Catch Chains & Loops
    redirect_graph = {}
    for row in rows:
        addr = row.get("Address")
        status = _int(row.get("Status Code"))
        redir_url = row.get("Redirect URL")
        if 300 <= status < 400 and addr and redir_url:
            redirect_graph[addr] = redir_url

    # 3. Compile Unique Issues List
    issues_registry = {}

    def add_issue(issue_type, severity, url, explanation):
        if issue_type not in issues_registry:
            issues_registry[issue_type] = {
                "type": issue_type,
                "severity": severity,
                "affected_urls": [],
                "count": 0,
                "explanation": explanation
            }
        if url not in issues_registry[issue_type]["affected_urls"]:
            issues_registry[issue_type]["affected_urls"].append(url)
            issues_registry[issue_type]["count"] += 1

    # 4. Evaluate Every Row Against the Rulebook
    for row in rows:
        url = row.get("Address")
        status = _int(row.get("Status Code"))
        
        # Response Codes
        if 400 <= status < 500:
            add_issue("broken_link_client_error", "High", url, "Pages returned a 4xx client failure status code.")
        elif 500 <= status < 600:
            add_issue("server_error", "High", url, "Pages returned a 5xx server failure status code.")
        elif 300 <= status < 400:
            add_issue("redirect", "Medium", url, "Pages return active 3xx HTTP routing directives.")
            
            # Trace Redirect Chains & Loops
            path = []
            curr = url
            is_loop = False
            while curr in redirect_graph:
                if curr in path:
                    is_loop = True
                    break
                path.append(curr)
                curr = redirect_graph[curr]
            if is_loop or len(path) > 1:
                add_issue("redirect_chain_loop", "High", url, "Pages caught in multi-hop redirect chains or cyclic loops.")

        # Text/HTML and Indexability Guarded Content Checks
        if status == 200 and is_html(row):
            # H1 Checklist
            h1_1 = row.get("H1-1", "").strip()
            if not h1_1:
                add_issue("missing_h1", "Medium", url, "Pages are missing a primary H1 structured title heading.")
            
            # Check for multiple H1s or duplicate H1 contents across pages
            h1_count = _int(row.get("H1-1 Count"))
            if h1_count > 1 or (h1_1 and len(h1s_map.get(h1_1, [])) > 1):
                add_issue("multiple_duplicate_h1", "Low", url, "Pages contain multiple H1 tags or share identical headings across URLs.")

            # Slow Page Speed Check
            resp_time = _float(row.get("Response Time"))
            if resp_time > 1.0:
                add_issue("slow_page", "Low", url, "Pages took longer than 1.0 seconds to respond.")

            if is_indexable(row):
                # Title Checks
                title = row.get("Title 1", "").strip()
                t_len = _int(row.get("Title 1 Length"))
                t_pix = _int(row.get("Title 1 Pixel Width"))
                
                if not title:
                    add_issue("missing_title", "High", url, "Indexable HTML pages are missing a defined page title tag.")
                if title and len(titles_map.get(title, [])) > 1:
                    add_issue("duplicate_title", "High", url, "Multiple indexable URLs share duplicate page title definitions.")
                if t_pix > 561 or t_len > 60:
                    add_issue("title_too_long", "Medium", url, "Page title lengths exceed recommended maximum bounds (60 chars / 561px).")
                if 0 < t_len < 30:
                    add_issue("title_too_short", "Low", url, "Page title lengths fall below recommended minimum visibility limits (30 chars).")

                # Meta Description Checks
                meta = row.get("Meta Description 1", "").strip()
                m_len = _int(row.get("Meta Description 1 Length"))
                
                if not meta:
                    add_issue("missing_meta_description", "Medium", url, "Indexable HTML pages are missing meta description snippets.")
                if meta and len(metas_map.get(meta, [])) > 1:
                    add_issue("duplicate_meta_description", "Medium", url, "Multiple indexable URLs share duplicate meta description snippets.")
                if m_len > 155:
                    add_issue("meta_description_too_long", "Low", url, "Meta description configurations exceed maximum layout character bounds (155 chars).")

                # Thin Content Check
                words = _int(row.get("Word Count"))
                if words < 200:
                    add_issue("thin_content", "Low", url, "Indexable production pages contain thin content under 200 body words.")

                # Orphan Page Check
                inlinks = _int(row.get("Inlinks"))
                if inlinks == 0:
                    add_issue("orphan_page", "Medium", url, "Indexable pages are unlinked from internal pathways (0 active incoming links).")

        # Non-Indexable Linked Check
        if row.get("Indexability", "").lower() == "non-indexable":
            inlinks = _int(row.get("Inlinks"))
            if inlinks > 0:
                add_issue("non_indexable_but_linked", "Medium", url, "Pages marked non-indexable are still actively referenced by incoming links.")

    # 5. Populate Metrics into Running Server State Contract
    compiled_issues = list(issues_registry.values())
    high_cnt = sum(1 for i in compiled_issues if i["severity"] == "High" for _ in i["affected_urls"])
    med_cnt = sum(1 for i in compiled_issues if i["severity"] == "Medium" for _ in i["affected_urls"])
    low_cnt = sum(1 for i in compiled_issues if i["severity"] == "Low" for _ in i["affected_urls"])

    server.RUN["total_issues"] = high_cnt + med_cnt + low_cnt
    server.RUN["by_severity"] = {"High": high_cnt, "Medium": med_cnt, "Low": low_cnt}
    server.RUN["issues"] = compiled_issues

    print(f"[Agent: Auditor] Complete. Structural issues detected: {server.RUN['total_issues']}.")

if __name__ == "__main__":
    run_audit_agent()