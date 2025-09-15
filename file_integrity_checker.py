#!/usr/bin/env python3
"""
File Integrity Checker
A security tool to monitor file integrity using cryptographic hashes
Author: Security Team
Version: 1.0
"""

import hashlib
import os
import json
import datetime
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

class FileIntegrityChecker:
    def __init__(self, database_file: str = "integrity_db.json"):
        """
        Initialize the File Integrity Checker
        
        Args:
            database_file: Path to the database file storing hash information
        """
        self.database_file = database_file
        self.database = self._load_database()
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('integrity_checker.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _load_database(self) -> Dict:
        """Load hash database from file"""
        if os.path.exists(self.database_file):
            try:
                with open(self.database_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading database: {e}")
                return {}
        return {}
    
    def _save_database(self):
        """Save hash database to file"""
        try:
            with open(self.database_file, 'w') as f:
                json.dump(self.database, f, indent=2, default=str)
        except IOError as e:
            self.logger.error(f"Error saving database: {e}")
    
    def calculate_hash(self, file_path: str, algorithm: str = 'sha256') -> Optional[str]:
        """
        Calculate hash of a file
        
        Args:
            file_path: Path to the file
            algorithm: Hash algorithm (md5, sha1, sha256, sha512)
            
        Returns:
            Hash string or None if error
        """
        try:
            hash_obj = hashlib.new(algorithm.lower())
            
            with open(file_path, 'rb') as f:
                # Read file in chunks to handle large files
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            
            return hash_obj.hexdigest()
        
        except (IOError, ValueError) as e:
            self.logger.error(f"Error calculating hash for {file_path}: {e}")
            return None
    
    def add_file(self, file_path: str, algorithm: str = 'sha256') -> bool:
        """
        Add file to integrity monitoring
        
        Args:
            file_path: Path to the file
            algorithm: Hash algorithm to use
            
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(file_path):
            self.logger.error(f"File not found: {file_path}")
            return False
        
        file_hash = self.calculate_hash(file_path, algorithm)
        if not file_hash:
            return False
        
        file_stat = os.stat(file_path)
        
        self.database[file_path] = {
            'hash': file_hash,
            'algorithm': algorithm,
            'size': file_stat.st_size,
            'mtime': file_stat.st_mtime,
            'added_time': datetime.datetime.now().isoformat(),
            'last_check': datetime.datetime.now().isoformat()
        }
        
        self._save_database()
        self.logger.info(f"Added file to monitoring: {file_path}")
        return True
    
    def check_file(self, file_path: str) -> Dict:
        """
        Check if file has been modified
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with check results
        """
        if file_path not in self.database:
            return {
                'status': 'not_monitored',
                'message': 'File is not being monitored'
            }
        
        if not os.path.exists(file_path):
            return {
                'status': 'missing',
                'message': 'File is missing',
                'original_hash': self.database[file_path]['hash']
            }
        
        stored_info = self.database[file_path]
        current_hash = self.calculate_hash(file_path, stored_info['algorithm'])
        
        if not current_hash:
            return {
                'status': 'error',
                'message': 'Could not calculate current hash'
            }
        
        file_stat = os.stat(file_path)
        
        # Update last check time
        self.database[file_path]['last_check'] = datetime.datetime.now().isoformat()
        self._save_database()
        
        if current_hash == stored_info['hash']:
            return {
                'status': 'unchanged',
                'message': 'File integrity verified',
                'hash': current_hash,
                'algorithm': stored_info['algorithm']
            }
        else:
            self.logger.warning(f"INTEGRITY VIOLATION: {file_path}")
            return {
                'status': 'modified',
                'message': 'File has been modified',
                'original_hash': stored_info['hash'],
                'current_hash': current_hash,
                'algorithm': stored_info['algorithm'],
                'size_change': file_stat.st_size - stored_info['size'],
                'mtime_change': file_stat.st_mtime - stored_info['mtime']
            }
    
    def scan_directory(self, directory: str, recursive: bool = False, 
                      file_pattern: str = "*") -> List[Tuple[str, Dict]]:
        """
        Scan directory and check all monitored files
        
        Args:
            directory: Directory to scan
            recursive: Scan subdirectories
            file_pattern: File pattern to match
            
        Returns:
            List of (file_path, check_result) tuples
        """
        results = []
        
        if recursive:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file_path in self.database:
                        result = self.check_file(file_path)
                        results.append((file_path, result))
        else:
            for file_path in Path(directory).glob(file_pattern):
                if str(file_path) in self.database:
                    result = self.check_file(str(file_path))
                    results.append((str(file_path), result))
        
        return results
    
    def generate_report(self) -> Dict:
        """Generate comprehensive integrity report"""
        report = {
            'timestamp': datetime.datetime.now().isoformat(),
            'total_files': len(self.database),
            'files': {},
            'summary': {
                'unchanged': 0,
                'modified': 0,
                'missing': 0,
                'errors': 0
            }
        }
        
        for file_path in self.database:
            result = self.check_file(file_path)
            report['files'][file_path] = result
            
            if result['status'] in report['summary']:
                report['summary'][result['status']] += 1
        
        return report
    
    def export_report(self, format: str = 'json', output_file: str = None):
        """Export report to file"""
        report = self.generate_report()
        
        if not output_file:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"integrity_report_{timestamp}.{format}"
        
        if format.lower() == 'json':
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
        elif format.lower() == 'html':
            self._export_html_report(report, output_file)
        
        self.logger.info(f"Report exported to: {output_file}")
        return output_file
    
    def _export_html_report(self, report: Dict, output_file: str):
        """Export report as HTML"""
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>File Integrity Report</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gray-100">
            <div class="container mx-auto px-4 py-8">
                <h1 class="text-3xl font-bold text-center mb-8">File Integrity Report</h1>
                
                <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                    <div class="bg-white rounded-lg shadow p-6 text-center">
                        <div class="text-2xl font-bold text-blue-600">{report['total_files']}</div>
                        <div class="text-gray-600">Total Files</div>
                    </div>
                    <div class="bg-white rounded-lg shadow p-6 text-center">
                        <div class="text-2xl font-bold text-green-600">{report['summary']['unchanged']}</div>
                        <div class="text-gray-600">Unchanged</div>
                    </div>
                    <div class="bg-white rounded-lg shadow p-6 text-center">
                        <div class="text-2xl font-bold text-red-600">{report['summary']['modified']}</div>
                        <div class="text-gray-600">Modified</div>
                    </div>
                    <div class="bg-white rounded-lg shadow p-6 text-center">
                        <div class="text-2xl font-bold text-yellow-600">{report['summary']['missing']}</div>
                        <div class="text-gray-600">Missing</div>
                    </div>
                </div>
                
                <div class="bg-white rounded-lg shadow overflow-hidden">
                    <table class="min-w-full">
                        <thead class="bg-gray-50">
                            <tr>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">File Path</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Message</th>
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200">
        """
        
        for file_path, result in report['files'].items():
            status_color = {
                'unchanged': 'text-green-600',
                'modified': 'text-red-600',
                'missing': 'text-yellow-600',
                'error': 'text-red-600'
            }.get(result['status'], 'text-gray-600')
            
            html_content += f"""
                            <tr>
                                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{file_path}</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm {status_color}">{result['status'].upper()}</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{result['message']}</td>
                            </tr>
            """
        
        html_content += """
                        </tbody>
                    </table>
                </div>
                
                <div class="mt-8 text-center text-gray-500 text-sm">
                    Generated on """ + report['timestamp'] + """
                </div>
            </div>
        </body>
        </html>
        """
        
        with open(output_file, 'w') as f:
            f.write(html_content)

def main():
    parser = argparse.ArgumentParser(description='File Integrity Checker')
    parser.add_argument('--add', '-a', help='Add file to monitoring')
    parser.add_argument('--check', '-c', help='Check specific file')
    parser.add_argument('--scan', '-s', help='Scan directory')
    parser.add_argument('--report', '-r', action='store_true', help='Generate report')
    parser.add_argument('--algorithm', default='sha256', 
                       choices=['md5', 'sha1', 'sha256', 'sha512'],
                       help='Hash algorithm to use')
    parser.add_argument('--recursive', action='store_true', help='Scan recursively')
    parser.add_argument('--export', choices=['json', 'html'], help='Export report format')
    parser.add_argument('--output', '-o', help='Output file name')
    
    args = parser.parse_args()
    
    checker = FileIntegrityChecker()
    
    if args.add:
        success = checker.add_file(args.add, args.algorithm)
        if success:
            print(f"Successfully added {args.add} to monitoring")
        else:
            print(f"Failed to add {args.add}")
    
    elif args.check:
        result = checker.check_file(args.check)
        print(f"File: {args.check}")
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")
        
        if result['status'] == 'modified':
            print(f"Original hash: {result['original_hash']}")
            print(f"Current hash: {result['current_hash']}")
    
    elif args.scan:
        results = checker.scan_directory(args.scan, args.recursive)
        print(f"Scanned {len(results)} files:")
        
        for file_path, result in results:
            status_symbol = {
                'unchanged': '✓',
                'modified': '✗',
                'missing': '?',
                'error': '!'
            }.get(result['status'], '?')
            
            print(f"{status_symbol} {file_path} - {result['status']}")
    
    elif args.report:
        report = checker.generate_report()
        print(f"Integrity Report Generated at {report['timestamp']}")
        print(f"Total files monitored: {report['total_files']}")
        print(f"Unchanged: {report['summary']['unchanged']}")
        print(f"Modified: {report['summary']['modified']}")
        print(f"Missing: {report['summary']['missing']}")
        print(f"Errors: {report['summary']['errors']}")
        
        if args.export:
            output_file = checker.export_report(args.export, args.output)
            print(f"Report exported to: {output_file}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()