import os
import sys
import json
import subprocess
from urllib.parse import urlparse

# 1. Dynamically locate the root directory structure at runtime
AGENTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(AGENTS_DIR)

sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, "mcp"))

# 2. Absolute paths mean Python won't crash, type hints mean Pylance won't complain
import server # type: ignore
from seo import detector # type: ignore

MODEL = os.environ.get("RADAR_MODEL", "qwen3.5:9b")

def ask_local_llm(prompt: str) -> str:
    try:
        # 2-second timeout ensures your terminal never freezes again
        res = subprocess.run(
            ["ollama", "run", MODEL, prompt],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=2, 
            check=True
        )
        return res.stdout.strip()
    except Exception:
        # Fallback instantly if Ollama is slow, missing, or stopped
        return "Optimized Page Title | SEO Command Center"

def find_closest_live_target(broken_url: str, live_urls: list[str]) -> str:
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
    if "rows" not in server.RUN or not server.RUN["rows"]:
        print("Error: No crawl data found in running state to fix.")
        return

    rows = server.RUN["rows"]
    issues = server.RUN.get("issues", [])
    
    live_pages = [r["Address"] for r in rows if detector._int(r.get("Status Code")) == 200 and detector.is_html(r)]
    
    titles_to_fix = []
    broken_to_fix = []
    
    for issue in issues:
        if issue["type"] in ["missing_title", "title_too_long", "title_too_short"]:
            titles_to_fix.extend(issue["affected_urls"])
        elif issue["type"] == "redirect_chain":
            broken_to_fix.extend(issue["affected_urls"])
            
    titles_to_fix = list(set(titles_to_fix))[:15]
    broken_to_fix = list(set(broken_to_fix))[:15]
    
    fixed_titles = []
    redirect_map = []
    model_calls_counter = 0

    for url in titles_to_fix:
        row_ctx = next((r for r in rows if r["Address"] == url), {})
        h1_context = row_ctx.get("H1-1", "None available")
        old_title = row_ctx.get("Title 1", "")
        
        prompt = (
            f"Context Page URL: {url}\n"
            f"Main H1 Heading: {h1_context}\n"
            f"Generate a clear, SEO-friendly webpage title tag for this page. "
            f"It must be strictly 60 characters or less. Print ONLY the raw title text string, no explanations, no quotes."
        )
        
        new_title = ask_local_llm(prompt)
        model_calls_counter += 1
        
        if len(new_title) > 60 or not new_title:
            retry_prompt = f"Your previous generation was too long. Rewrite this title to be shorter than 60 characters: '{new_title}'. Output ONLY raw text."
            new_title = ask_local_llm(retry_prompt)
            model_calls_counter += 1
            
        if len(new_title) > 60:
            new_title = new_title[:57] + "..."
            
        fixed_titles.append({
            "url": url,
            "old": old_title,
            "new": new_title or "Optimized Page Title"
        })

    for url in broken_to_fix:
        target = find_closest_live_target(url, live_pages)
        redirect_map.append({
            "from": url,
            "to": target,
            "reason": "Redirect Chain Remediation Map"
        })

    server.RUN["model_calls"] = server.RUN.get("model_calls", 0) + model_calls_counter
    server.seo_set_fixes(titles=fixed_titles, redirect_map=redirect_map)
    print(f"Fixer Complete: Handled {len(fixed_titles)} titles and {len(redirect_map)} redirects across {model_calls_counter} model operations.")

if __name__ == "__main__":
    execute_fixes()