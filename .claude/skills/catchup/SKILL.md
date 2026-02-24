---
name: catchup
description: Read session-state.md to catch up on previous session work. Use after clearing context, starting new session, or when you need to understand what was done previously.
---

# Catch Up on Session State

This skill reads the session state file to restore context about previous work.

---

## Usage

When invoked with `/catchup`, this skill will:

1. **Read session-state.md**: Load the session state file from `.claude/session-state.md`
2. **Summarize session**: Provide clear summary of:
   - Current goal/objective
   - What has been completed
   - What remains to be done
   - Modified files
   - Important notes and decisions
3. **Restore context**: Help Claude understand where the work left off

---

## When to Use

Use `/catchup` when:
- Starting a new conversation after `/clear`
- Returning to work after a break
- Context was lost due to summarization
- Need to remind Claude about the current task
- Another person is taking over the work

---

## Session State File

**Location**: `.claude/session-state.md`

**Structure**:
- **Ostatnia aktualizacja**: Timestamp of last update
- **Status**: Current status (w toku/zakończona/wstrzymana/planowanie)
- **Aktualny cel**: Main objective of current session
- **Co zrobione**: List of completed tasks
- **Co zostało**: List of remaining tasks
- **Pliki**: List of modified/created files
- **Uwagi**: Additional notes, problems, decisions

---

## Workflow

**Typical workflow**:

1. **Before clearing context**: Update session state
   ```
   User: /state-start
   Claude: [Updates session-state.md with current progress]
   ```

2. **Clear context**:
   ```
   User: /clear
   [Context cleared]
   ```

3. **Restore context**:
   ```
   User: /catchup
   Claude: [Reads session-state.md and summarizes]
   ```

---

## Action

**When this skill is invoked**:

1. Read `.claude/session-state.md`
2. Parse the content
3. Provide concise summary in this format:

```
Session Catch-Up

Last updated: [timestamp]
Status: [status]

Goal: [aktualny cel]

Done:
- [task 1]
- [task 2]

Remaining:
- [task 1]
- [task 2]

Files:
- [file 1]
- [file 2]

Notes:
[important notes]
```

4. Ask user if they want to continue where left off or start something new
