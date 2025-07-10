#!/usr/bin/env python3

import re
import sys
from typing import Dict, List
from datetime import datetime

import requests


def read_netxms_changelog(input_lines: List[str]) -> Dict[str, List[str]]:
    changelog: Dict[str, List[str]] = {}
    version = "UNKNOWN"
    padding = ""
    for line in input_lines:
        if line == "":
            continue
        if line.strip() == "*":
            continue
        m = re.match(r"^\# ([0-9.]+(-SNAPSHOT)?)", line)
        if m:
            padding = ""
            version = m.group(1)
            if version not in changelog:
                v: List[str] = []
                changelog[version] = v
        if line.startswith("## Fixed issues"):
            changelog[version].append("  * Fixed issues:")
            padding = "  "
        if line[0] == "-":
            changelog[version].append("  * " + padding + line[2:].strip())
    return changelog


def update_rpm_spec_changelog(spec_file: str, version: str, changes: List[str]):
    now = datetime.now()
    date_str = now.strftime("%a %b %d %Y")
    
    new_entry = f"* {date_str} Alex Kirhenshtein <alk@netxms.org> - {version}-1\n"
    for change in changes:
        new_entry += f"{change}\n"
    new_entry += "\n"
    
    with open(spec_file, 'r') as f:
        content = f.read()
    
    changelog_pattern = r'(%changelog\n)'
    if re.search(changelog_pattern, content):
        updated_content = re.sub(
            changelog_pattern,
            r'\1' + new_entry,
            content,
            count=1
        )
        
        with open(spec_file, 'w') as f:
            f.write(updated_content)
    else:
        raise ValueError("No %changelog section found in spec file")

def update_rpm_spec_version(spec_file: str, version: str):
    with open(spec_file, 'r') as f:
        content = f.read()
    
    version_pattern = r'(Version:\s+)([^\n]+)'
    updated_content = re.sub(
        version_pattern,
        rf'\g<1>{version}',
        content
    )
    
    with open(spec_file, 'w') as f:
        f.write(updated_content)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: update_changelog.py <version>")
        sys.exit(1)
        
    version = sys.argv[1]
    spec_file = 'SPECS/netxms.spec'
    
    text = requests.get('https://raw.githubusercontent.com/netxms/changelog/master/ChangeLog.md').text.splitlines()
    new_changes = read_netxms_changelog(text)[version]
    
    update_rpm_spec_version(spec_file, version)
    
    update_rpm_spec_changelog(spec_file, version, new_changes)
    
    print(f"Updated {spec_file} with version {version}")
