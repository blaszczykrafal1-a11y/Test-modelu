#!/bin/bash
# Security pre-commit hook
# Instalacja: cp system/scripts/pre-commit.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
# Kompatybilny z macOS bash 3.2+

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

FOUND_BLOCKS=0

STAGED_FILES=$(git diff --cached --name-only)

if [ -z "$STAGED_FILES" ]; then
  exit 0
fi

check_file() {
  local file="$1"
  local blocked=0

  if [ ! -f "$file" ]; then return 0; fi

  case "$file" in
    *.xlsx|*.xls|*.csv|*.mdb|*.accdb|*.XLSX|*.XLS|*.CSV)
      echo -e "${RED}[BLOKADA]${NC} Plik z danymi klientow: $file"
      return 1
      ;;
  esac

  local basename_file
  basename_file=$(basename "$file")
  case "$basename_file" in
    .env|.env.*|*.env)
      echo -e "${RED}[BLOKADA]${NC} Plik env: $file"
      return 1
      ;;
  esac

  case "$basename_file" in
    *credential*|*secret*|*password*|*private*|*token*)
      echo -e "${YELLOW}[OSTRZEZENIE]${NC} Podejrzana nazwa pliku: $file"
      ;;
  esac

  if ! file "$file" 2>/dev/null | grep -qE "text|ASCII|UTF"; then
    return 0
  fi

  local lnum

  if grep -qE 'sk-[a-zA-Z0-9]{40,}' "$file" 2>/dev/null; then
    lnum=$(grep -nE 'sk-[a-zA-Z0-9]{40,}' "$file" | head -1 | cut -d: -f1)
    echo -e "${RED}[BLOKADA]${NC} OpenAI API key w: $file (linia $lnum)"
    blocked=1
  fi

  if grep -qE 'sk-proj-[a-zA-Z0-9_-]{40,}' "$file" 2>/dev/null; then
    lnum=$(grep -nE 'sk-proj-[a-zA-Z0-9_-]{40,}' "$file" | head -1 | cut -d: -f1)
    echo -e "${RED}[BLOKADA]${NC} OpenAI Project key w: $file (linia $lnum)"
    blocked=1
  fi

  if grep -qE 'AIza[0-9A-Za-z_-]{35}' "$file" 2>/dev/null; then
    lnum=$(grep -nE 'AIza[0-9A-Za-z_-]{35}' "$file" | head -1 | cut -d: -f1)
    echo -e "${RED}[BLOKADA]${NC} Google API key w: $file (linia $lnum)"
    blocked=1
  fi

  if grep -qE 'ghp_[a-zA-Z0-9]{36}' "$file" 2>/dev/null; then
    lnum=$(grep -nE 'ghp_[a-zA-Z0-9]{36}' "$file" | head -1 | cut -d: -f1)
    echo -e "${RED}[BLOKADA]${NC} GitHub PAT w: $file (linia $lnum)"
    blocked=1
  fi

  if grep -qE 'AKIA[0-9A-Z]{16}' "$file" 2>/dev/null; then
    lnum=$(grep -nE 'AKIA[0-9A-Z]{16}' "$file" | head -1 | cut -d: -f1)
    echo -e "${RED}[BLOKADA]${NC} AWS Access Key w: $file (linia $lnum)"
    blocked=1
  fi

  if grep -qE '(postgresql|mysql|mongodb|redis)://[^:@[:space:]]+:[^@[:space:]]+@' "$file" 2>/dev/null; then
    lnum=$(grep -nE '(postgresql|mysql|mongodb|redis)://[^:@[:space:]]+:[^@[:space:]]+@' "$file" | head -1 | cut -d: -f1)
    echo -e "${RED}[BLOKADA]${NC} DB connection string z haslem w: $file (linia $lnum)"
    blocked=1
  fi

  if grep -qE '"password"[[:space:]]*:[[:space:]]*"[^"]{4,}"' "$file" 2>/dev/null; then
    lnum=$(grep -nE '"password"[[:space:]]*:[[:space:]]*"[^"]{4,}"' "$file" | head -1 | cut -d: -f1)
    echo -e "${RED}[BLOKADA]${NC} Hardcoded password w: $file (linia $lnum)"
    blocked=1
  fi

  if grep -qiE '(api_key|apikey|api_secret)[[:space:]]*[:=][[:space:]]*[A-Za-z0-9_-]{20,}' "$file" 2>/dev/null; then
    echo -e "${YELLOW}[OSTRZEZENIE]${NC} Potencjalny API key w: $file"
  fi

  return $blocked
}

for file in $STAGED_FILES; do
  if ! check_file "$file"; then
    FOUND_BLOCKS=1
  fi
done

echo ""

if [ $FOUND_BLOCKS -eq 1 ]; then
  echo -e "${RED}Commit ZABLOKOWANY ze wzgledow bezpieczenstwa.${NC}"
  echo "Usun wrazliwe dane i sprobuj ponownie."
  echo ""
  echo "Aby pominac (tylko jesli wiesz co robisz):"
  echo "  git commit --no-verify"
  exit 1
fi

echo -e "${GREEN}Skan bezpieczenstwa: OK${NC}"
exit 0
