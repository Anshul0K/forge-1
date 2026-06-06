# PROMPTS.md — AI prompt history log

A short running record of the highest-leverage prompts you used during this sprint. 
Documenting your prompt engineering choices is graded (challenge brief section 08).

---

## 1. Expanding the Rulebook Detector Module
**Prompt used to build `seo/detector.py` functions:**
> "Hey, look at this basic detector template for SEO. I need to implement the rest of the rulebook cleanly. Give me clean Python standard library code to check for missing/duplicate meta descriptions, H1 structural errors, thin content under 200 words, response times over 1.0s, and a graph-based loop checker to catch multi-hop redirect chains from the address headers. No pandas, just use native types."

## 2. Setting Up the AI Fixer Validation Loop
**Prompt used to engineer the validation loop in `agents/fixer.py`:**
> "Write a prompt for a local Ollama model to generate page titles from URL paths and H1 context. The output must be strictly 60 characters or less, raw string text only. Also, show me how to wrap the python subprocess call in a validation loop so if the model returns something too long, it catches it, runs a shorter retry prompt, and applies a fallback if it fails again."

## 3. Resolving the Python Relative Import Crash
**Prompt used to fix the `ImportError` runtime bug:**
> "My python script run.py crashes with 'ImportError: attempted relative import beyond top-level package' when running from the terminal, but if I remove the dots, VS Code's Pylance highlights everything in yellow because it can't track sys.path changes. How do I fix both the execution crash and keep the IDE linter perfectly clean without using relative dots?"