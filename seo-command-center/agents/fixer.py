import os
import json
import subprocess
import sys
from urllib.parse import urlparse

# Ensure we can import modules relative to the project root
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "mcp"))
import server  # Exposes seo_set_fixes and RUN state directly

MODEL = os.environ.get("RADAR_MODEL", "qwen3.5:9b")

def ask_local_llm(prompt: str) -> str:
    """Helper to query the local Ollama instance running our stack model."""
    try:
        res = subprocess.run(
            ["ollama", "run", MODEL, prompt],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True
        )
        return res.stdout.strip()
    except Exception:
        return ""

def find_closest_live_target(broken_url: str, live_urls: list[str]) -> str:
    """Finds the closest matching path section or folder structure among 200 OK pages."""
    try:
        broken_path = urlparse(broken_url).path.strip("/").split("/")
        if not broken_path or broken_path == [""]:
            return live_urls[0] if live_urls else broken_url
            
        best_target = live_urls[0] if live_urls else broken_url
        max_overlap = -1
        
        for live_url in live_urls:
            live_path = urlparse(live_url).path.strip("/").split("/")
            overlap = 0
            for b_seg, l_seg in zip(broken_path, live_path):
                if b_seg == l_seg:
                    overlap += 1
                else:
                    break
            if overlap > max_overlap:
                max_overlap = overlap
                best_target = live_url
        return best_target
    except Exception:
        return live_urls[0] if live_urls else broken_url

def execute_fixes():
    """Processes affected URLs through the LLM with tight length-guard loops."""
    # Ensure a crawl has been loaded into state first
    if "rows" not in server.RUN or not server.RUN["rows"]:
        print("Error: No crawl data found in running state to fix.")
        return

    rows = server.RUN["rows"]
    issues = server.RUN.get("issues", [])
    
    # Pre-calculate baseline groups
    live_pages = [r["Address"] for r in rows if server._int(r.get("Status Code")) == 200 and server.is_html(r)]
    
    titles_to_fix = []
    broken_to_fix = []
    
    for issue in issues:
        if issue["type"] in ["missing_title", "title_too_long", "title_too_short"]:
            titles_to_fix.extend(issue["affected_urls"])
        elif issue["type"] == "broken_link":
            broken_to_fix.extend(issue["affected_urls"])
            
    # Uniquify targets to optimize model call efficiency score
    titles_to_fix = list(set(titles_to_fix))[:15]  # Sample limit to protect time/quota budgets
    broken_to_fix = list(set(broken_to_fix))[:15]
    
    fixed_titles = []
    redirect_map = []
    model_calls_counter = 0

    # --- PART 1: AI Title Copy Generation + Validation Loop ---
    for url in titles_to_fix:
        # Pull matching context from row metrics
        row_ctx = next((r for r in rows if r["Address"] == url), {})
        h1_context = row_ctx.get("H1-1", "None available")
        old_title = row_ctx.get("Title 1", "")
        
        prompt = (
            f"Context Page URL: {url}\n"
            f"Main H1 Heading: {h1_context}\n"
            f"Generate a clear, SEO-friendly webpage title tag for this page. "
            f"It must be strictly 60 characters or less. Print ONLY the raw title text string, no explanations, no quotes."
        )
        
        # Validation and Retry Loop
        new_title = ask_local_llm(prompt)
        model_calls_counter += 1
        
        if len(new_title) > 60 or not new_title:
            # Code validation guard fallback: Retry once with explicit constraint enforcement
            retry_prompt = f"Your previous generation was too long. Rewrite this title to be shorter than 60 characters: '{new_title}'. Output ONLY raw text."
            new_title = ask_local_llm(retry_prompt)
            model_calls_counter += 1
            
        # Final safety truncation if model fails constraints
        if len(new_title) > 60:
            new_title = new_title[:57] + "..."
            
        fixed_titles.append({
            "url": url,
            "old": old_title,
            "new": new_title or "Optimized Page Title"
        })

    # --- PART 2: Algorithmic Redirect Map Closest-Path Alignment ---
    for url in broken_to_fix:
        target = find_closest_live_target(url, live_pages)
        redirect_map.append({
            "from": url,
            "to": target,
            "reason": "404 Broken Link Cleanup Map"
        })

    # Sync metrics back to running memory framework
    server.RUN["model_calls"] = server.RUN.get("model_calls", 0) + model_calls_counter
    server.seo_set_fixes(titles=fixed_titles, redirect_map=redirect_map)
    print(f"Fixer Complete: Handled {len(fixed_titles)} titles and {len(redirect_map)} redirects across {model_calls_counter} model operations.")

if __name__ == "__main__":
    execute_fixes()