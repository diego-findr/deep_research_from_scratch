#!/usr/bin/env python
"""
Quick verification script to check all project files are non-empty.
"""

import os
from pathlib import Path

def check_files(directory, extensions=None):
    """Check files in directory."""
    if extensions is None:
        extensions = {'.py', '.json', '.md', '.txt', '.toml'}
    
    issues = []
    checked = 0
    
    for root, dirs, files in os.walk(directory):
        # Skip hidden and cache directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'venv', '.venv', 'output']]
        
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                filepath = Path(root) / file
                checked += 1
                
                try:
                    size = filepath.stat().st_size
                    if size == 0:
                        issues.append(f"EMPTY: {filepath}")
                    elif size < 10:  # Suspiciously small
                        issues.append(f"SMALL ({size} bytes): {filepath}")
                except Exception as e:
                    issues.append(f"ERROR reading {filepath}: {e}")
    
    return checked, issues


if __name__ == "__main__":
    print("="*70)
    print("PROJECT FILE VERIFICATION")
    print("="*70)
    
    # Check source files
    print("\n📁 Checking src/ directory...")
    checked_src, issues_src = check_files('src')
    print(f"   ✓ Checked {checked_src} files")
    
    # Check tests
    print("\n🧪 Checking tests/ directory...")
    checked_tests, issues_tests = check_files('tests')
    print(f"   ✓ Checked {checked_tests} files")
    
    # Check documentation
    print("\n📚 Checking documentation files...")
    checked_docs, issues_docs = check_files('.', {'.md', '.txt', '.toml'})
    print(f"   ✓ Checked {checked_docs} files")
    
    # Report issues
    all_issues = issues_src + issues_tests + issues_docs
    
    print("\n" + "="*70)
    if all_issues:
        print(f"⚠️  FOUND {len(all_issues)} ISSUES:")
        print("="*70)
        for issue in all_issues:
            print(f"  {issue}")
    else:
        print("✅ ALL FILES VERIFIED - NO ISSUES FOUND!")
        print("="*70)
        print(f"\nTotal files checked: {checked_src + checked_tests + checked_docs}")
        print("\nProject structure is complete and ready to use!")
    
    print("\n" + "="*70)

