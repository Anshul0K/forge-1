# PROMPTS.md — AI prompt history log

A running record of the iterative engineering prompts used to guide Claude Code and local testing models during this sprint. 

---

## 1. Ingestion Engine Setup
**Prompt used to initialize data loading in `agents/ingest.py`:**
> "Read the standard CSV output from our Screaming Frog export file using Python's native csv library. Strip whitespace from header strings and isolate the main root domain name from the 'Address' field."

---

## 2. Setting Up the Auditor Compliance Logic
**Prompt used to build the core rulebook checks in `agents/auditor.py`:**
> "Look at the compliance guidelines inside auditors.md. Help me write clean Python loops to scan rows for 4xx/5xx status codes, missing H1 tags, response times over 1.0s, and thin content under 200 words."

**Iterative prompt to handle advanced validation guards:**
> "Modify the auditor code so that duplicate checking for page titles and meta descriptions is strictly guarded. It should only register duplicate flags among pages that are indexable and have a text/html Content Type."

**Iterative prompt to build the redirect graph engine:**
> "Create a dictionary-based graph path tracker for all 3xx redirect status rows. Use a traversal loop to walk the redirection steps node-by-node so we can capture deep multi-hop redirect chains and cyclic infinite loops."

---

## 3. Integrating the Local LLM Fixer
**Prompt used to engineer the Ollama local model connector in `agents/fixer.py`:**
> "I am setting up an automation task that uses a local model (qwen3.5:9b) through an Ollama subprocess call. Help me write the subprocess connection code to feed bad page headers into the model to generate optimized titles and meta descriptions."

**Iterative prompt to create strict system constraints:**
> "Draft a tight system prompt instruction for the local LLM. It must return strictly raw text strings—no markdown styling, no quotation marks, and zero conversational pleasantries like 'Sure, here is your title'."

**Iterative prompt to build the length safety validation loop:**
> "Wrap my local model subprocess call inside a validation loop. Add a strict 2-second timeout to prevent the terminal execution thread from hanging. If the model generates an optimized title exceeding 60 characters, catch it in code, send one condensed retry prompt, and apply an explicit substring slice fallback if it fails a second time."

**Iterative prompt to handle broken link routing:**
> "For broken links (4xx errors), let's use directory segment string overlap checking to automatically map the dead URL to the closest matching live page on the site for our redirect mapping output."

---

## 4. Multi-Format Output Generation
**Prompt used to engineer the document builder in `agents/reporter.py`:**
> "Take our finalized issue registry data and compile it into a fully structured, indented outputs/report.json file that perfectly honors our required schema contract."

**Iterative prompt to extract independent fix sheets:**
> "Inside reporter.py, extract the optimized content variables out of memory and write two separate, standalone spreadsheet assets inside the outputs/ folder: a titles_metas_fixes.csv and a redirect_map.csv."

**Iterative prompt to design the client presentation layer:**
> "Help me generate a clean, standalone outputs/report.html dashboard file. Include basic, color-coded inline alert boxes (High, Medium, Low severity badges) so a regular client can open the report in a browser and read the technical audit results instantly."

---

## 5. Debugging Workspace Import and Port Errors
**Prompt used to resolve workspace execution crashes:**
> "When running run.py from the root folder terminal, the pipeline crashes due to a relative import error beyond top-level packages. If I remove the dots, my editor flags broken paths. Show me how to programmatically insert the workspace root directory into sys.path at the top of the entry files to fix terminal execution while keeping the linter happy."

**Prompt used to diagnose execution environment failures:**
> "Check this agent error trace coming from my local script engine. Find out why the execution pipeline is crashing on the terminal runner and suggest a localized fix."

---

## 6. Configuring the Central Orchestrator in `run.py`
**Prompt used to engineer sequential execution flow:**
> "I need to configure run.py to act purely as a multi-agent orchestrator rather than doing the processing directly. Show me how to set up sequentially executing triggers that run the sub-agents in order: ingest, audit, fix, and report. Ensure that shared execution metrics are correctly retained across the server lifecycle state."

**Iterative prompt to manage environmental port configuration overrides:**
> "Add environmental variable safety guards into run.py so that it dynamically binds to the network port designated by the grader environment (like SEO_PORT=7799). Include fallback error catches so running the terminal command won't crash on standard port conflict errors."

---

## 7. Migrating Logic and Downsizing `seo/detector.py`
**Prompt used to decouple rulebook logic out of static scripts:**
> "To maximize our agentic architecture score, I need to migrate our core evaluation algorithms out of standalone script spaces. Show me how to extract the main analytical loop out of seo/detector.py and house it completely within agents/auditor.py so that the work is logged under the proper agent identity."

**Iterative prompt to transition the file into a pure utility module:**
> "Now that the heavy auditing tasks are handled by auditor.py, clean out seo/detector.py so it functions solely as a light utility library. Keep basic string and mathematical filters (like the pixel calculation functions) intact so other scripts like fixer.py can still cleanly import them as helper components without breaking code dependencies."