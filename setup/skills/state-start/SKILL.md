---
name: state-start
description: Update session-state.md with current session progress. Use before clearing context, taking a break, or when significant work has been completed.
---

# Update Session State

This skill updates the session state file with current progress.

---

## Usage

When invoked with `/state-start`, this skill will:

1. **Analyze current session**: Review conversation history to understand:
   - What task is being worked on
   - What has been completed
   - What remains to be done
   - Which files were modified
   - Important decisions and notes

2. **Update session-state.md**: Write comprehensive summary to `.claude/session-state.md`

3. **Confirm update**: Show summary of what was saved

---

## When to Use

Use `/state-start` when:
- **Before `/clear`**: Save progress before clearing context
- **After major milestone**: Document completion of significant work
- **Before taking a break**: Save state for later continuation
- **Context running low**: Prepare for context summarization
- **Switching tasks**: Document current state before switching
- **End of work session**: Save progress before ending session

---

## Session State Structure

The skill will update all sections of `session-state.md`:

### Ostatnia aktualizacja
Current timestamp in format: `YYYY-MM-DD HH:MM:SS`

### Status
One of:
- **w toku** - Work in progress
- **zakończona** - Completed
- **wstrzymana** - Paused/blocked
- **planowanie** - Planning phase

### Aktualny cel
Main objective of current session (1-2 sentences)

### Co zrobione
Bullet list of completed tasks

### Co zostało
Bullet list of remaining tasks

### Pliki
List of modified/created files with brief description

### Uwagi
Important notes: decisions, blockers, context

---

## Action

**When this skill is invoked**:

1. **Review conversation**: Analyze recent messages to understand current goal, actions taken, results achieved, files modified, problems encountered, decisions made

2. **Assess status**: Determine whether project is w toku / zakończona / wstrzymana / planowanie

3. **Update file**: Write to `.claude/session-state.md`

4. **Show confirmation**:
   ```
   Session State Updated

   Status: [status]
   Goal: [brief goal]
   Tasks completed: [count]
   Tasks remaining: [count]
   Files modified: [count]

   Saved to: .claude/session-state.md
   Use /clear to clear context window.
   Use /catchup to restore this context later.
   ```

---

## Best Practices

1. **Update regularly**: Don't wait until context is full - update proactively
2. **Be specific**: Include concrete details, not vague summaries
3. **Note blockers**: Document what's blocking progress
4. **Track decisions**: Record why certain approaches were chosen
5. **List all files**: Include all modified files, even small changes
