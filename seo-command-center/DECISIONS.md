# DECISIONS.md — decision & learnings log

A short running note of the real choices you made: what you tried, what failed and why, what
you changed. This is your engineering judgement on the record — it is what separates a builder
from a button-presser, and it is graded (challenge brief section 08).

Append a 1–2 line entry whenever you make a real decision or hit/fix a wall. Add a timestamp.

Format:
`[HH:MM] <decision or problem> → <what you did and why>`

---

## My log
- `[11:15]` Dropped pandas requirement from setup → plain csv module handles 456 rows instantly anyway. No need for heavy external dependencies.

- `[12:30]` Custom redirect logic failed on multi-hop jumps → rewrote detector.py using a small graph-based trace matrix to follow headers manually. Now catches true loops and stacked chains.

- `[13:10]` Terminal froze completely during execution → python subprocess was stuck waiting forever on Ollama because qwen3.5:9b wasn't downloaded locally.

- `[13:15]` Added strict 2s timeout guard to subprocess run → if local model hangs or is missing, it drops back to safe string optimization instantly instead of locking the console.

- `[13:45]` Relative imports like `..mcp` crashing script execution → python hates running top-level files directly with dots. Added sys.path.insert overrides and type ignores to keep Pylance quiet while maintaining clean CLI boots on port 7799.