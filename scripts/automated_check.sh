#!/bin/bash
# automated_check.sh - Script otomatis untuk monitoring integritas file
# Usage: ./automated_check.sh
# Cron: 0 */6 * * * /path/to/automated_check.sh

set -e

# Configuration
CHECKER_PATH="/opt/file-integrity-checker/file_integrity_checker.py"
REPORT_DIR="/opt/reports"
LOG_FILE="/var/log/integrity_monitor.log"
EMAIL_ALERT="admin@company.com"
SLACK_WEBHOOK="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Check if checker exists
if [ ! -f "$CHECKER_PATH" ]; then
    log "ERROR: File integrity checker not found at $CHECKER_PATH"
    exit 1
fi

# Create report directory if it doesn't exist
mkdir -p "$REPORT_DIR"

log "Starting automated integrity check..."

# Generate report
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="$REPORT_DIR/integrity_report_$TIMESTAMP.json"
HTML_REPORT="$REPORT_DIR/integrity_report_$TIMESTAMP.html"

# Run integrity check and generate reports
python3 "$CHECKER_PATH" --report --export json --output "$REPORT_FILE"
python3 "$CHECKER_PATH" --report --export html --output "$HTML_REPORT"

# Check for modifications
if [ -f "$REPORT_FILE" ]; then
    MODIFIED_COUNT=$(grep -o '"modified": [0-9]*' "$REPORT_FILE" | cut -d':' -f2 | tr -d ' ')
    MISSING_COUNT=$(grep -o '"missing": [0-9]*' "$REPORT_FILE" | cut -d':' -f2 | tr -d ' ')
    
    if [ "$MODIFIED_COUNT" -gt 0 ] || [ "$MISSING_COUNT" -gt 0 ]; then
        echo -e "${RED}WARNING: Integrity violations detected!${NC}"
        echo -e "${RED}Modified files: $MODIFIED_COUNT${NC}"
        echo -e "${RED}Missing files: $MISSING_COUNT${NC}"
        
        log "ALERT: $MODIFIED_COUNT modified files, $MISSING_COUNT missing files"
        
        # Send email alert
        if command -v mail >/dev/null 2>&1; then
            {
                echo "File Integrity Alert - $(date)"
                echo "Modified files: $MODIFIED_COUNT"
                echo "Missing files: $MISSING_COUNT"
                echo ""
                echo "Report: $HTML_REPORT"
                echo ""
                echo "Please investigate immediately."
            } | mail -s "SECURITY ALERT: File Integrity Violation" "$EMAIL_ALERT"
            log "Email alert sent to $EMAIL_ALERT"
        fi
        
        # Send Slack notification
        if [ -n "$SLACK_WEBHOOK" ]; then
            curl -X POST -H 'Content-type: application/json' \
                --data "{\"text\":\"🚨 *File Integrity Alert*\nModified: $MODIFIED_COUNT files\nMissing: $MISSING_COUNT files\nTime: $(date)\nReport: $HTML_REPORT\"}" \
                "$SLACK_WEBHOOK" >/dev/null 2>&1
            log "Slack notification sent"
        fi
        
    else
        echo -e "${GREEN}All monitored files are intact${NC}"
        log "All files integrity verified - no violations detected"
    fi
else
    echo -e "${RED}ERROR: Report file not generated${NC}"
    log "ERROR: Failed to generate integrity report"
    exit 1
fi

# Cleanup old reports (keep last 30 days)
find "$REPORT_DIR" -name "integrity_report_*.json" -mtime +30 -delete
find "$REPORT_DIR" -name "integrity_report_*.html" -mtime +30 -delete

log "Automated integrity check completed"

echo -e "${GREEN}Report generated: $HTML_REPORT${NC}"
