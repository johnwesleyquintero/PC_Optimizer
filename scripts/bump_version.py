#!/usr/bin/env python3

import re
import sys
import os
from pathlib import Path

def get_current_version():
    """Read current version from pyproject.toml"""
    try:
        with open('pyproject.toml', 'r') as f:
            content = f.read()
            match = re.search(r'version = "([^"]+)"', content)
            return match.group(1) if match else '0.1.0'
    except FileNotFoundError:
        return '0.1.0'

def bump_version(current_version, bump_type):
    """Bump version according to semver rules"""
    major, minor, patch = map(int, current_version.split('.'))
    
    if bump_type == 'major':
        return f"{major + 1}.0.0"
    elif bump_type == 'minor':
        return f"{major}.{minor + 1}.0"
    elif bump_type == 'patch':
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")

def update_pyproject_toml(new_version):
    """Update version in pyproject.toml"""
    try:
        with open('pyproject.toml', 'r') as f:
            content = f.read()
        
        content = re.sub(
            r'version = "[^"]+"',
            f'version = "{new_version}"',
            content
        )
        
        with open('pyproject.toml', 'w') as f:
            f.write(content)
    except FileNotFoundError:
        print("Error: pyproject.toml not found")
        sys.exit(1)

def create_git_tag(new_version):
    """Create and push git tag"""
    tag = f"v{new_version}"
    os.system(f'git tag {tag}')
    print(f"\nCreated new tag: {tag}")
    print("\nTo push the tag, run:")
    print(f"  git push origin {tag}")

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ['major', 'minor', 'patch']:
        print("Usage: python bump_version.py [major|minor|patch]")
        sys.exit(1)

    bump_type = sys.argv[1]
    current_version = get_current_version()
    new_version = bump_version(current_version, bump_type)
    
    print(f"Current version: {current_version}")
    print(f"New version: {new_version}")
    
    update_pyproject_toml(new_version)
    create_git_tag(new_version)
    
    print("\nVersion bump complete!")
    print("Remember to commit changes to pyproject.toml")

if __name__ == '__main__':
    main()