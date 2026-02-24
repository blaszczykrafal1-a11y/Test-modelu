#!/bin/bash

# Read JSON input
input=$(cat)

# Extract model name
model=$(echo "$input" | jq -r '.model.display_name')

# Extract context window data
total_input=$(echo "$input" | jq -r '.context_window.total_input_tokens // 0')
total_output=$(echo "$input" | jq -r '.context_window.total_output_tokens // 0')
context_window_size=$(echo "$input" | jq -r '.context_window.context_window_size // 0')

# Calculate total tokens used
total_used=$((total_input + total_output))

# Calculate remaining percentage correctly
remaining_percent=0
context_color=$'\033[2m'  # Default: dim
if [ "$context_window_size" -gt 0 ]; then
    remaining_percent=$(awk "BEGIN {printf \"%.0f\", (($context_window_size - $total_used) / $context_window_size) * 100}")

    # Set color based on remaining percentage
    if [ "$remaining_percent" -ge 70 ]; then
        context_color=$'\033[2m'  # Default: dim
    elif [ "$remaining_percent" -ge 60 ]; then
        context_color=$'\033[2;33m'  # Dim yellow
    else
        context_color=$'\033[2;31m'  # Dim red
    fi
fi

# Build status line with color
printf $'\033[2m[%s] %sContext: %s%% remaining | Tokens: %s/%s\033[0m' \
    "$model" \
    "$context_color" \
    "$remaining_percent" \
    "$total_used" \
    "$context_window_size"

# Add warning if context is below 70%
if [ "$remaining_percent" -lt 70 ]; then
    printf $'\n\033[2;33m⚠️  Zbliżasz się do końca kontekstu, aby uniknąć halucynacji użyj komend:\033[0m'
    printf $'\n   \033[1;37m/state-start\033[0m\033[37m zapisz stan\033[0m \033[33m→\033[0m \033[1;37m/clear\033[0m\033[37m wyczyść historię\033[0m \033[33m→\033[0m \033[1;37m/exit\033[0m\033[37m zamknij chat\033[0m \033[33m→\033[0m \033[1;37mclaude\033[0m\033[37m uruchom chat\033[0m \033[33m→\033[0m \033[1;37m/catchup\033[0m\033[37m przywróć kontekst\033[0m'
fi
