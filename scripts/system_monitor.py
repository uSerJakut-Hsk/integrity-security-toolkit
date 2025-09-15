# system_monitor.py - Python script untuk monitoring sistem comprehensive
cat > /tmp/system_monitor.py << 'EOF'
#!/usr/bin/env python3
"""
System Monitor untuk File Integrity Checker
Monitoring komprehensif untuk sistem Linux/Kali Linux
"""

import os
import sys
import subprocess
import json
from pathlib import Path
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

class SystemMonitor:
    def __init__(self):
        self.checker_path = "/opt/file-integrity-checker/file_integrity_checker.py"
        self.critical_files = [
            "/etc/passwd",
            "/etc/shadow", 
            "/etc/sudoers",
            "/etc/ssh/sshd_config",
            "/etc/hosts",
            "/etc/crontab",
            "/boot/grub/grub.cfg"
        ]
        self.critical_dirs = [
            "/etc/ssh/",
            "/etc/pam.d/",
            "/etc/security/",
            "/root/.ssh/"
        ]
        
    def setup_monitoring(self):
        """Setup monitoring untuk file dan direktori critical"""
        print("Setting up system monitoring...")
        
        # Add critical files
        for file_path in self.critical_files:
            if os.path.exists(file_path):
                cmd = [sys.executable, self.checker_path, "--add", file_path, "--algorithm", "sha256"]
                try:
                    subprocess.run(cmd, check=True, capture_output=True)
                    print(f"✓ Added {file_path} to monitoring")
                except subprocess.CalledProcessError as e:
                    print(f"✗ Failed to add {file_path}: {e}")
            else:
                print(f"⚠ File not found: {file_path}")
        
        # Add critical directories
        for dir_path in self.critical_dirs:
            if os.path.exists(dir_path):
                cmd = [sys.executable, self.checker_path, "--scan", dir_path, "--recursive"]
                try:
                    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                    print(f"✓ Scanned {dir_path}")
                except subprocess.CalledProcessError as e:
                    print(f"✗ Failed to scan {dir_path}: {e}")
            else:
                print(f"⚠ Directory not found: {dir_path}")
    
    def run_security_scan(self):
        """Run comprehensive security scan"""
        print("\n" + "="*50)
        print("RUNNING SECURITY INTEGRITY SCAN")
        print("="*50)
        
        # Generate report
        cmd = [sys.executable, self.checker_path, "--report"]
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("Report generated successfully")
            
            # Parse output for summary
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Total files monitored:' in line or \
                   'Unchanged:' in line or \
                   'Modified:' in line or \
                   'Missing:' in line:
                    print(line)
                    
        except subprocess.CalledProcessError as e:
            print(f"Failed to generate report: {e}")
            return False
        
        return True
    
    def check_rootkit_indicators(self):
        """Check for common rootkit indicators"""
        print("\n" + "="*50)
        print("CHECKING ROOTKIT INDICATORS")
        print("="*50)
        
        indicators = [
            "/tmp/.ICE-unix",
            "/tmp/.X11-unix", 
            "/dev/shm/",
            "/var/tmp/",
            "/usr/bin/last",
            "/usr/bin/netstat",
            "/usr/bin/ps"
        ]
        
        suspicious_found = False
        
        for indicator in indicators:
            if os.path.exists(indicator):
                # Check if file has been modified recently
                cmd = [sys.executable, self.checker_path, "--check", indicator]
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if "modified" in result.stdout.lower():
                        print(f"⚠ SUSPICIOUS: {indicator} has been modified")
                        suspicious_found = True
                    else:
                        print(f"✓ OK: {indicator}")
                except:
                    print(f"? Unable to check: {indicator}")
        
        if not suspicious_found:
            print("✓ No obvious rootkit indicators found")
        
        return not suspicious_found

def main():
    if os.geteuid() != 0:
        print("This script should be run as root for comprehensive monitoring")
        print("Run with: sudo python3 system_monitor.py")
        sys.exit(1)
    
    monitor = SystemMonitor()
    
    # Setup monitoring
    monitor.setup_monitoring()
    
    # Run security scan
    scan_success = monitor.run_security_scan()
    
    # Check rootkit indicators
    rootkit_clean = monitor.check_rootkit_indicators()
    
    # Summary
    print("\n" + "="*50)
    print("SECURITY MONITORING SUMMARY")
    print("="*50)
    
    if scan_success and rootkit_clean:
        print("✓ System appears secure")
        sys.exit(0)
    else:
        print("⚠ Security issues detected - investigate immediately")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF