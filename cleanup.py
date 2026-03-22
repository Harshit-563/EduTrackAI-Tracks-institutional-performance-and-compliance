#!/usr/bin/env python
"""
Cleanup script for EduTrack workspace
Removes temporary files, cache directories, and outdated documentation
"""
import os
import shutil
from pathlib import Path

# Project root
project_root = Path('c:/edutech')
os.chdir(project_root)

# Files to remove
unwanted_files = [
    'tempCodeRunnerFile.py',
    'fire_cert.pdf',
    'test_fire_cert.jpg',
    'COMPLETION_SUMMARY.md',
    'EXECUTION_COMPLETE.md',
    'FILE_STRUCTURE_AND_CHANGES.md',
    'FRONTEND_COLOR_PALETTE_COMPLETE.md',
    'FRONTEND_COMPLETE.md',
    'FRONTEND_SETUP_COMPLETE.md',
    'IMPLEMENTATION_VERIFICATION_CHECKLIST.md',
    'LAUNCH_GUIDE.md',
    'PROJECT_COMPLETION.md',
    'README_DOCUMENTATION_INDEX.md',
    'risk_model.pkl',
    'scaler.pkl',
    'cleanup.ps1'  # Also remove the PowerShell script
]

print("🧹 Starting workspace cleanup...\n")

# Remove files
removed_count = 0
for file in unwanted_files:
    file_path = project_root / file
    try:
        if file_path.exists():
            file_path.unlink()
            print(f"✓ Removed: {file}")
            removed_count += 1
    except Exception as e:
        print(f"✗ Error removing {file}: {e}")

# Remove __pycache__ directories
pycache_count = 0
for root, dirs, files in os.walk(project_root):
    if '__pycache__' in dirs:
        cache_path = Path(root) / '__pycache__'
        try:
            shutil.rmtree(cache_path)
            print(f"✓ Removed: {cache_path.relative_to(project_root)}")
            pycache_count += 1
        except Exception as e:
            print(f"✗ Error removing {cache_path}: {e}")

# Remove .pyc files
pyc_count = 0
for root, dirs, files in os.walk(project_root):
    for file in files:
        if file.endswith('.pyc'):
            pyc_path = Path(root) / file
            try:
                pyc_path.unlink()
                pyc_count += 1
            except Exception as e:
                print(f"✗ Error removing {pyc_path}: {e}")

if pyc_count > 0:
    print(f"✓ Removed {pyc_count} .pyc files")

print(f"\n{'='*50}")
print(f"✅ Cleanup complete!")
print(f"{'='*50}")
print(f"Files removed: {removed_count}")
print(f"Cache directories removed: {pycache_count}")
print(f"\n📁 Workspace is now clean and ready for development!")
