# kali_linux_setup.sh - Setup script khusus untuk Kali Linux
cat > /tmp/kali_linux_setup.sh << 'EOF'
#!/bin/bash
# kali_linux_setup.sh - Setup File Integrity Checker di Kali Linux
# Usage: sudo ./kali_linux_setup.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root: sudo $0${NC}"
    exit 1
fi

echo -e "${BLUE}Setting up File Integrity Checker for Kali Linux${NC}"
echo "=================================================="

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
apt update
apt install -y python3 python3-pip git curl wget

# Create directories
echo -e "${YELLOW}Creating directories...${NC}"
mkdir -p /opt/file-integrity-checker
mkdir -p /opt/file-integrity-checker/logs
mkdir -p /opt/file-integrity-checker/reports
mkdir -p /opt/file-integrity-checker/db

# Set permissions
chown -R root:root /opt/file-integrity-checker
chmod 755 /opt/file-integrity-checker
chmod 700 /opt/file-integrity-checker/db
chmod 755 /opt/file-integrity-checker/logs
chmod 755 /opt/file-integrity-checker/reports

# Copy files (assuming they're in current directory)
if [ -f "file_integrity_checker.py" ]; then
    cp file_integrity_checker.py /opt/file-integrity-checker/
    chmod +x /opt/file-integrity-checker/file_integrity_checker.py
    ln -sf /opt/file-integrity-checker/file_integrity_checker.py /usr/local/bin/integrity-checker
    echo -e "${GREEN}✓ Main script installed${NC}"
else
    echo -e "${RED}✗ file_integrity_checker.py not found in current directory${NC}"
fi

if [ -f "dashboard.html" ]; then
    cp dashboard.html /opt/file-integrity-checker/
    echo -e "${GREEN}✓ Dashboard installed${NC}"
fi

# Setup critical file monitoring
echo -e "${YELLOW}Setting up critical file monitoring...${NC}"

CRITICAL_FILES=(
    "/etc/passwd"
    "/etc/shadow"
    "/etc/group"
    "/etc/sudoers" 
    "/etc/ssh/sshd_config"
    "/etc/hosts"
    "/etc/hostname"
    "/etc/crontab"
    "/root/.bashrc"
    "/root/.bash_profile"
    "/boot/grub/grub.cfg"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        /usr/local/bin/integrity-checker --add "$file" --algorithm sha256
        echo -e "${GREEN}✓ Added $file to monitoring${NC}"
    else
        echo -e "${YELLOW}⚠ File not found: $file${NC}"
    fi
done

# Setup systemd service
echo -e "${YELLOW}Creating systemd service...${NC}"
cat > /etc/systemd/system/integrity-checker.service << 'EOL'
[Unit]
Description=File Integrity Checker Service
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/integrity-checker --report
User=root
Group=root
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOL

# Setup systemd timer
cat > /etc/systemd/system/integrity-checker.timer << 'EOL'
[Unit]
Description=Run File Integrity Checker every hour
Requires=integrity-checker.service

[Timer]
OnCalendar=hourly
Persistent=true

[Install]
WantedBy=timers.target
EOL

systemctl daemon-reload
systemctl enable integrity-checker.timer
systemctl start integrity-checker.timer

echo -e "${GREEN}✓ Systemd service and timer created${NC}"

# Setup log rotation
echo -e "${YELLOW}Setting up log rotation...${NC}"
cat > /etc/logrotate.d/integrity-checker << 'EOL'
/opt/file-integrity-checker/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    copytruncate
    create 640 root root
}
EOL

echo -e "${GREEN}✓ Log rotation configured${NC}"

# Create daily report cron job
echo -e "${YELLOW}Setting up daily reporting...${NC}"
cat > /etc/cron.daily/integrity-report << 'EOL'
#!/bin/bash
REPORT_DIR="/opt/file-integrity-checker/reports"
DATE=$(date +%Y%m%d)
/usr/local/bin/integrity-checker --report --export html --output "$REPORT_DIR/daily_report_$DATE.html"
# Cleanup reports older than 30 days
find "$REPORT_DIR" -name "daily_report_*.html" -mtime +30 -delete
EOL

chmod +x /etc/cron.daily/integrity-report
echo -e "${GREEN}✓ Daily reporting configured${NC}"

# Setup web dashboard service (optional)
read -p "Do you want to setup web dashboard service? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cat > /etc/systemd/system/integrity-dashboard.service << 'EOL'
[Unit]
Description=File Integrity Checker Web Dashboard
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 -m http.server 8080
WorkingDirectory=/opt/file-integrity-checker
User=www-data
Group=www-data
Restart=always

[Install]
WantedBy=multi-user.target
EOL
    
    systemctl daemon-reload
    systemctl enable integrity-dashboard.service
    systemctl start integrity-dashboard.service
    echo -e "${GREEN}✓ Web dashboard service started on port 8080${NC}"
fi

# Create useful aliases
echo -e "${YELLOW}Creating useful aliases...${NC}"
cat >> /root/.bashrc << 'EOL'

# File Integrity Checker Aliases
alias ic-check='integrity-checker --report'
alias ic-add='integrity-checker --add'
alias ic-scan='integrity-checker --scan'
alias ic-status='systemctl status integrity-checker.timer'
alias ic-logs='tail -f /opt/file-integrity-checker/logs/integrity_checker.log'
alias ic-web='cd /opt/file-integrity-checker && python3 -m http.server 8080'
EOL

# Final setup verification
echo -e "${YELLOW}Running setup verification...${NC}"
if command -v integrity-checker >/dev/null 2>&1; then
    echo -e "${GREEN}✓ integrity-checker command available${NC}"
else
    echo -e "${RED}✗ integrity-checker command not found${NC}"
fi

if systemctl is-enabled integrity-checker.timer >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Systemd timer enabled${NC}"
else
    echo -e "${RED}✗ Systemd timer not enabled${NC}"
fi

echo
echo -e "${BLUE}=================================================="
echo -e "File Integrity Checker Setup Complete!"
echo -e "==================================================${NC}"
echo
echo -e "${GREEN}Usage:${NC}"
echo "  integrity-checker --help                 # Show help"
echo "  integrity-checker --add /path/to/file    # Add file to monitoring"  
echo "  integrity-checker --check /path/to/file  # Check specific file"
echo "  integrity-checker --report               # Generate report"
echo "  ic-check                                 # Alias for quick check"
echo
echo -e "${GREEN}Web Dashboard:${NC}"
echo "  http://localhost:8080/dashboard.html     # Access web interface"
echo
echo -e "${GREEN}Logs:${NC}"
echo "  /opt/file-integrity-checker/logs/        # Log files"
echo "  ic-logs                                  # View real-time logs"
echo
echo -e "${GREEN}Reports:${NC}"
echo "  /opt/file-integrity-checker/reports/     # Generated reports"
echo
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Add more files to monitoring using: integrity-checker --add /path/to/file"
echo "2. Review daily reports in /opt/file-integrity-checker/reports/"
echo "3. Check systemd timer status: systemctl status integrity-checker.timer"
echo "4. Access web dashboard at http://localhost:8080/dashboard.html"
echo
echo -e "${GREEN}Setup completed successfully!${NC}"

EOF

chmod +x /tmp/system_monitor.py
chmod +x /tmp/kali_linux_setup.sh

echo "Scripts created:"
echo "1. automated_check.sh - Automated monitoring script"  
echo "2. system_monitor.py - Comprehensive system monitoring"
echo "3. kali_linux_setup.sh - Complete setup for Kali Linux"
echo ""
echo "Usage:"
echo "  sudo ./kali_linux_setup.sh              # Complete setup"
echo "  python3 system_monitor.py               # System monitoring"  
echo "  ./automated_check.sh                    # Run automated check"
