#!/usr/bin/env bash
# Fetch calendar agenda for today and tomorrow, filtering out noisy recurring reminders
set -euo pipefail
gws calendar +agenda --days 2 | \
    grep -Ev "(daily health|daily reminder)" || true
