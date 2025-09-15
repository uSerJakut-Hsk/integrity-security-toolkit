#!/usr/bin/env python3
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description='File Integrity Checker Test')
    parser.add_argument('--add', help='Add file to monitoring')
    parser.add_argument('--check', help='Check specific file')
    parser.add_argument('--report', action='store_true', help='Generate report')
    
    args = parser.parse_args()
    
    print("Test script working!")
    print(f"Args: {args}")
    
    if args.add:
        print(f"Would add: {args.add}")
    elif args.check:
        print(f"Would check: {args.check}")
    elif args.report:
        print("Would generate report")

if __name__ == "__main__":
    main()
