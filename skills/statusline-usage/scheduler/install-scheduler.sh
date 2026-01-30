#!/bin/bash
# ABOUTME: Cross-platform scheduler installer for the usage scraper.
# ABOUTME: Detects OS and installs LaunchAgent (macOS), cron (Linux), or shows Windows instructions.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CACHE_DIR="${CLAUDE_USAGE_CACHE_DIR:-$HOME/.claude-statusline-usage}"
SCRAPER_PATH="$CACHE_DIR/scrape-usage.py"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

get_python_path() { which python3; }

install_macos() {
    info "Installing macOS LaunchAgent..."

    PLIST_DIR="$HOME/Library/LaunchAgents"
    PLIST_NAME="com.claude.usage-scraper.plist"
    PLIST_PATH="$PLIST_DIR/$PLIST_NAME"
    TEMPLATE="$SCRIPT_DIR/macos/$PLIST_NAME"

    mkdir -p "$PLIST_DIR"

    PYTHON_PATH=$(get_python_path)
    PATH_VAR="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin"

    sed -e "s|__PYTHON_PATH__|$PYTHON_PATH|g" \
        -e "s|__SCRAPER_PATH__|$SCRAPER_PATH|g" \
        -e "s|__CACHE_DIR__|$CACHE_DIR|g" \
        -e "s|__PATH__|$PATH_VAR|g" \
        -e "s|__HOME__|$HOME|g" \
        "$TEMPLATE" > "$PLIST_PATH"

    launchctl unload "$PLIST_PATH" 2>/dev/null || true
    launchctl load "$PLIST_PATH"

    info "LaunchAgent installed. Runs every 15 minutes."
    echo ""
    echo "To uninstall:"
    echo "  launchctl unload $PLIST_PATH"
    echo "  rm $PLIST_PATH"
}

install_linux() {
    info "Installing Linux cron job..."

    PYTHON_PATH=$(get_python_path)
    CRON_LINE="*/15 * * * * $PYTHON_PATH $SCRAPER_PATH --quiet >> $CACHE_DIR/cron.log 2>&1"

    if crontab -l 2>/dev/null | grep -q "scrape-usage.py"; then
        warn "Cron job already exists. Updating..."
        crontab -l 2>/dev/null | grep -v "scrape-usage.py" | crontab -
    fi

    (crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -

    info "Cron job installed. Runs every 15 minutes."
    echo ""
    echo "To uninstall:"
    echo "  crontab -e  # remove the claude usage scraper line"
}

install_windows() {
    warn "Windows detected. Run PowerShell script instead:"
    echo "  scheduler\\windows\\install-task.ps1"
    echo ""
    echo "NOTE: PTY automation is not supported on Windows."
}

# Detect OS and install
if ! command -v python3 &> /dev/null; then
    error "Python 3 is required."
fi

echo "Claude Usage Scraper - Scheduler Installation"
echo "═══════════════════════════════════════════════"
echo ""

case "$OSTYPE" in
    darwin*)  install_macos ;;
    linux*)   install_linux ;;
    msys*|cygwin*|win32*) install_windows ;;
    *)        error "Unsupported OS: $OSTYPE" ;;
esac

echo ""
info "Done!"
