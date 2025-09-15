# File Integrity Checker 🛡️

**File Integrity Checker** adalah tool security monitoring yang powerful untuk memantau integritas file menggunakan cryptographic hash (MD5, SHA1, SHA256, SHA512). Tool ini sangat cocok digunakan untuk security monitoring di Kali Linux dan sistem Linux lainnya.

## ✨ Fitur Utama

- **Multi-Algorithm Hash Support**: MD5, SHA1, SHA256, SHA512
- **Real-time Monitoring**: Deteksi perubahan file secara real-time
- **Web Dashboard**: Interface web modern dengan Tailwind CSS
- **Comprehensive Reporting**: Export laporan dalam format JSON dan HTML
- **Directory Scanning**: Scan direktori secara recursive
- **Logging System**: Activity logging untuk audit trail
- **Database Persistence**: Simpan hash database dalam JSON format
- **Command Line Interface**: CLI yang user-friendly

## 🚀 Mengapa Tool Ini Bagus untuk Security?

### 1. **Deteksi Intrusion**
- Mendeteksi perubahan unauthorized pada file sistem critical
- Monitoring file konfigurasi penting (/etc/passwd, /etc/shadow, dll)
- Alert ketika ada modifikasi file yang mencurigakan

### 2. **Compliance & Audit**
- Memenuhi requirement security compliance
- Audit trail lengkap untuk investigasi forensik
- Reporting untuk dokumentasi security

### 3. **System Administration**
- Monitoring integritas backup files
- Verifikasi file setelah update sistem
- Deteksi corruption atau tampering

## 📋 Prerequisites

- **Python 3.7+**
- **Kali Linux** (atau distro Linux lainnya)
- **Git** untuk clone repository
- **Web browser** untuk dashboard

## 🔧 Installation

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/file-integrity-checker.git
cd file-integrity-checker
```

### 2. Install Dependencies
```bash
# Install Python dependencies
pip3 install -r requirements.txt

# Atau install secara manual
pip3 install pathlib hashlib
```

### 3. Make Executable
```bash
chmod +x file_integrity_checker.py
```

### 4. Optional: Install System-wide
```bash
sudo cp file_integrity_checker.py /usr/local/bin/integrity-checker
sudo chmod +x /usr/local/bin/integrity-checker
```

## 📖 Cara Penggunaan

### Command Line Interface

#### 1. Menambah File untuk Monitoring
```bash
# Tambah single file
python3 file_integrity_checker.py --add /etc/passwd

# Dengan algoritma tertentu
python3 file_integrity_checker.py --add /etc/shadow --algorithm sha512
```

#### 2. Check File Integrity
```bash
# Check file specific
python3 file_integrity_checker.py --check /etc/passwd

# Hasil output:
# File: /etc/passwd
# Status: unchanged
# Message: File integrity verified
```

#### 3. Scan Directory
```bash
# Scan directory
python3 file_integrity_checker.py --scan /etc/

# Scan recursive
python3 file_integrity_checker.py --scan /home/user/ --recursive
```

#### 4. Generate Reports
```bash
# Generate JSON report
python3 file_integrity_checker.py --report

# Export ke HTML
python3 file_integrity_checker.py --report --export html

# Export dengan custom filename
python3 file_integrity_checker.py --report --export json --output my_report.json
```

### Web Dashboard

1. **Start Web Server**
```bash
# Serve HTML dashboard
python3 -m http.server 8000
```

2. **Access Dashboard**
```
http://localhost:8000/dashboard.html
```

### Contoh Use Cases untuk Kali Linux

#### 1. **Monitor System Files**
```bash
# Monitor file sistem critical
python3 file_integrity_checker.py --add /etc/passwd --algorithm sha256
python3 file_integrity_checker.py --add /etc/shadow --algorithm sha256
python3 file_integrity_checker.py --add /etc/sudoers --algorithm sha256
python3 file_integrity_checker.py --add /etc/ssh/sshd_config --algorithm sha256
```

#### 2. **Monitor Web Applications**
```bash
# Monitor web application files
python3 file_integrity_checker.py --scan /var/www/html/ --recursive
```

#### 3. **Monitor Log Files**
```bash
# Monitor important log files
python3 file_integrity_checker.py --add /var/log/auth.log --algorithm md5
python3 file_integrity_checker.py --add /var/log/syslog --algorithm md5
```

#### 4. **Automated Monitoring Script**
```bash
#!/bin/bash
# automated_check.sh

echo "Starting automated integrity check..."

# Run integrity check
python3 file_integrity_checker.py --report --export html --output daily_report.html

# Check for modifications
MODIFIED=$(python3 file_integrity_checker.py --report | grep "Modified: [1-9]")

if [ ! -z "$MODIFIED" ]; then
    echo "WARNING: Files have been modified!"
    # Send notification atau email
    echo "Modified files detected at $(date)" | mail -s "Integrity Check Alert" admin@company.com
fi

echo "Integrity check completed."
```

## 📊 Web Dashboard Features

### Dashboard Overview
- **Total Files**: Jumlah file yang dimonitor
- **Intact Files**: File yang tidak berubah
- **Modified Files**: File yang telah dimodifikasi
- **Missing Files**: File yang hilang

### Interactive Features
- **Real-time Updates**: Auto-refresh setiap 30 detik
- **File Filtering**: Filter berdasarkan status
- **Search Function**: Cari file berdasarkan nama
- **Detailed View**: Lihat hash details dan informasi file
- **Export Reports**: Export dalam format JSON

### Security Alerts
- **Visual Indicators**: Alert merah untuk file yang modified
- **Activity Log**: Log semua aktivitas monitoring
- **Status Icons**: Icon berbeda untuk setiap status file

## 🗂️ Struktur Project

```
file-integrity-checker/
├── file_integrity_checker.py    # Main Python module
├── dashboard.html               # Web dashboard
├── requirements.txt            # Python dependencies
├── setup.py                   # Package setup
├── README.md                  # Documentation
├── examples/                  # Example scripts
│   ├── automated_check.sh     # Automated checking script
│   └── system_monitor.py      # System monitoring example
├── logs/                      # Log files
│   └── integrity_checker.log  # Application logs
└── reports/                   # Generated reports
    ├── integrity_report.json  # JSON reports
    └── integrity_report.html  # HTML reports
```

## 🔐 Security Best Practices

### 1. **File Permissions**
```bash
# Set proper permissions
chmod 600 integrity_db.json      # Database file
chmod 700 logs/                  # Log directory
chmod 644 reports/*.html         # Report files
```

### 2. **Secure Storage**
```bash
# Store database di direktori secure
mkdir -p /opt/integrity-checker/db
mv integrity_db.json /opt/integrity-checker/db/
chown root:root /opt/integrity-checker/db/integrity_db.json
chmod 600 /opt/integrity-checker/db/integrity_db.json
```

### 3. **Cron Jobs untuk Automated Monitoring**
```bash
# Edit crontab
crontab -e

# Add lines:
# Check setiap jam
0 * * * * /usr/local/bin/integrity-checker --report > /dev/null 2>&1

# Daily report
0 6 * * * /usr/local/bin/integrity-checker --report --export html --output /opt/reports/daily_$(date +\%Y\%m\%d).html
```

## 🛠️ Advanced Configuration

### 1. **Custom Hash Algorithms**
```python
# Dalam script, Anda bisa extend dengan algoritma lain
SUPPORTED_ALGORITHMS = ['md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512']
```

### 2. **Database Encryption**
```python
# Tambahkan enkripsi untuk database
import cryptography.fernet

def encrypt_database(data, key):
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())
    return encrypted_data
```

### 3. **Network Monitoring**
```bash
# Monitor file via network
python3 file_integrity_checker.py --add /path/to/shared/file --algorithm sha256
```

## 🐛 Troubleshooting

### Common Issues

1. **Permission Denied**
```bash
# Jalankan dengan sudo jika diperlukan
sudo python3 file_integrity_checker.py --add /etc/shadow
```

2. **Database Corruption**
```bash
# Backup dan reset database
cp integrity_db.json integrity_db.json.backup
rm integrity_db.json
# Re-add files
```

3. **Large Files Performance**
```bash
# Untuk file besar, gunakan algoritma yang lebih cepat
python3 file_integrity_checker.py --add /path/to/largefile --algorithm md5
```

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📄 License

MIT License - lihat file LICENSE untuk details.

## 📞 Support

- **Issues**: Report bugs di GitHub Issues
- **Documentation**: Cek wiki untuk dokumentasi lengkap
- **Community**: Join diskusi di GitHub Discussions

## 🎯 Roadmap

- [ ] Database encryption
- [ ] Email notifications
- [ ] Slack/Discord integration  
- [ ] REST API
- [ ] Docker container
- [ ] Windows support
- [ ] Real-time file watching
- [ ] Machine learning anomaly detection

---

**⚠️ Disclaimer**: Tool ini untuk tujuan security monitoring dan educational. Pastikan Anda memiliki permission yang tepat sebelum monitoring file sistem.