#!/usr/bin/env python3
"""
Claude Code PreToolUse Security Hook
Skanuje content przed zapisem pliku lub wykonaniem Basha.
Exit 0 = OK, Exit 2 = blokada z feedbackiem do Claude
"""

import sys
import json
import re
import os

# Wzorce sekretów (pattern, label, block)
SECRET_PATTERNS = [
    (r'sk-[a-zA-Z0-9]{40,}', 'OpenAI API key (sk-...)', True),
    (r'sk-proj-[a-zA-Z0-9_-]{40,}', 'OpenAI Project API key', True),
    (r'AIza[0-9A-Za-z_-]{35}', 'Google API key', True),
    (r'(postgresql|mysql|mongodb|redis)://[^:@\s"\']+:[^@\s"\']+@\S+', 'Connection string z haslem', True),
    (r'Bearer\s+[A-Za-z0-9._\-]{30,}', 'Bearer token', True),
    (r'"password"\s*:\s*"[^"]{4,}"', 'Hardcoded password w JSON', True),
    (r'password\s*=\s*["\'][^"\']{4,}["\']', 'Hardcoded password', True),
    (r'(?i)(api_key|apikey|api_secret|client_secret)\s*[:=]\s*["\']?[a-zA-Z0-9_\-]{20,}', 'Generic API key/secret', True),
    (r'ghp_[a-zA-Z0-9]{36}', 'GitHub Personal Access Token', True),
    (r'gho_[a-zA-Z0-9]{36}', 'GitHub OAuth token', True),
    (r'AKIA[0-9A-Z]{16}', 'AWS Access Key ID', True),
]

# Rozszerzenia plików z danymi klientów
DATA_FILE_EXTENSIONS = {'.xlsx', '.xls', '.csv', '.mdb', '.accdb'}

# Ścieżki dokumentacyjne — skanuj ale nie blokuj (przykłady sekretów są zamierzone)
DOC_PATHS = ['/.claude/', '/system/reference/', '/system/instructions/', 'CLAUDE.md', 'README.md', 'snippets.md']

# Komendy git które mogą commitować wrażliwe pliki
RISKY_GIT_PATTERNS = [
    (r'git add\s+.*\.(xlsx|xls|csv|env|key|pem)', 'dodawanie pliku z danymi/sekretami do git'),
    (r'git add -A|git add \.', 'git add -A / git add . (moze dodac wrazliwe pliki)'),
]


def scan_content(content: str, file_path: str = "") -> list[tuple[str, bool]]:
    """Zwraca listę (opis, czy_blokować) dla znalezionych sekretów."""
    findings = []

    for pattern, label, should_block in SECRET_PATTERNS:
        if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
            findings.append((label, should_block))

    return findings


def check_file_path(file_path: str) -> list[tuple[str, bool]]:
    """Sprawdza czy sam path pliku jest podejrzany."""
    findings = []
    ext = os.path.splitext(file_path)[1].lower()

    if ext in DATA_FILE_EXTENSIONS:
        findings.append((f'plik z danymi ({ext})', True))

    suspicious_names = ['credential', 'secret', 'password', 'private', 'token']
    basename = os.path.basename(file_path).lower()
    for name in suspicious_names:
        if name in basename:
            findings.append((f'podejrzana nazwa pliku: {os.path.basename(file_path)}', False))
            break

    return findings


def check_bash_command(command: str) -> list[tuple[str, bool]]:
    """Sprawdza komendy bash pod katem ryzykownych operacji git."""
    findings = []

    for pattern, label in RISKY_GIT_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            findings.append((label, False))  # warn only, don't block

    return findings


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, Exception):
        sys.exit(0)

    tool_name = data.get('tool_name', '')
    tool_input = data.get('tool_input', {})

    all_findings = []
    context = ""

    if tool_name == 'Write':
        content = tool_input.get('content', '')
        file_path = tool_input.get('file_path', '')
        context = f"Write -> {os.path.basename(file_path)}"
        is_doc = any(d in file_path for d in DOC_PATHS)

        all_findings += check_file_path(file_path)
        raw = scan_content(content, file_path)
        # W plikach dokumentacyjnych — warn only, nie blokuj
        if is_doc:
            all_findings += [(label, False) for label, _ in raw]
        else:
            all_findings += raw

    elif tool_name == 'Edit':
        new_string = tool_input.get('new_string', '')
        file_path = tool_input.get('file_path', '')
        context = f"Edit -> {os.path.basename(file_path)}"
        is_doc = any(d in file_path for d in DOC_PATHS)

        raw = scan_content(new_string, file_path)
        if is_doc:
            all_findings += [(label, False) for label, _ in raw]
        else:
            all_findings += raw

    elif tool_name == 'Bash':
        command = tool_input.get('command', '')
        context = f"Bash -> {command[:80]}"

        all_findings += check_bash_command(command)

    else:
        sys.exit(0)

    if not all_findings:
        sys.exit(0)

    should_block = any(block for _, block in all_findings)

    # Output goes back to Claude as context (exit 2)
    severity = "BLOKADA" if should_block else "OSTRZEZENIE"
    print(f"[SECURITY {severity}] Wykryto potencjalnie wrazliwe dane ({context}):")
    for label, block in all_findings:
        prefix = "BLOKUJE" if block else "OSTRZEGA"
        print(f"  [{prefix}] {label}")

    if should_block:
        print()
        print("Sprawdz czy to zamierzone. Nie zapisuj sekretow w plikach.")
        print("Jezeli to false positive, poinformuj uzytkownika i zapytaj o potwierdzenie.")
        sys.exit(2)
    else:
        # Warning only - let it through but Claude sees the message
        print()
        print("To ostrzezenie (nie blokada). Upewnij sie ze to zamierzone.")
        sys.exit(0)


if __name__ == '__main__':
    main()
