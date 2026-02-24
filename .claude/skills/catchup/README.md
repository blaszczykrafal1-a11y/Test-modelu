# Catch Up Skill

Reads session-state.md to restore context about previous work.

## Usage

```
/catchup
```

## What It Does

1. Reads `.claude/session-state.md`
2. Summarizes current session state:
   - Current goal
   - Completed tasks
   - Remaining tasks
   - Modified files
   - Important notes
3. Helps Claude understand where work left off

## When to Use

- After using `/clear`
- Starting new session after a break
- Context was lost due to summarization
- Need to remind Claude about current task
- Another person taking over work

## Workflow

```bash
# Before clearing context
/state-start  # Update session state

# Clear context
/clear

# Restore context in new session
/catchup
```

## Output Format

```
📋 Session Catch-Up

Ostatnia aktualizacja: [timestamp]
Status: [status]

🎯 Cel: [goal]

✅ Zrobione:
- [completed tasks]

⏳ Zostało:
- [remaining tasks]

📁 Pliki:
- [modified files]

📝 Uwagi:
[notes]
```
