#!/usr/bin/env python3
"""
Version bump script for AI Email Routing Framework.
Increments version in VERSION, CHANGELOG.md, and architecture_diagram.html.
"""

import re
import sys
from datetime import datetime
from pathlib import Path

# Files to update
VERSION_FILE = Path("VERSION")
CHANGELOG_FILE = Path("CHANGELOG.md")
DIAGRAM_FILE = Path("architecture_diagram.html")


def get_current_version():
    """Read current version from VERSION file."""
    return VERSION_FILE.read_text().strip()


def bump_version(current: str) -> str:
    """Increment the release number."""
    year, release = current.split(".")
    current_year = str(datetime.now().year)

    # If new year, reset to X.1
    if year != current_year:
        return f"{current_year}.1"

    # Otherwise increment release
    return f"{year}.{int(release) + 1}"


def update_version_file(new_version: str):
    """Update VERSION file."""
    VERSION_FILE.write_text(f"{new_version}\n")
    print(f"  ✓ VERSION: {new_version}")


def update_diagram(old_version: str, new_version: str):
    """Update version in architecture diagram HTML."""
    if not DIAGRAM_FILE.exists():
        print(f"  ⚠ {DIAGRAM_FILE} not found, skipping")
        return

    content = DIAGRAM_FILE.read_text()
    updated = content.replace(f"v{old_version}", f"v{new_version}")
    DIAGRAM_FILE.write_text(updated)
    print(f"  ✓ {DIAGRAM_FILE}: v{new_version}")


def update_changelog(new_version: str, notes: list):
    """Add new entry to CHANGELOG.md."""
    if not CHANGELOG_FILE.exists():
        print(f"  ⚠ {CHANGELOG_FILE} not found, skipping")
        return

    content = CHANGELOG_FILE.read_text()
    today = datetime.now().strftime("%Y-%m-%d")

    # Build new entry
    notes_text = "\n".join(f"- {note}" for note in notes) if notes else "- Updates and improvements"

    new_entry = f"""## [{new_version}] - {today}

### Changed
{notes_text}

---

"""

    # Insert after the header section (after first ---)
    parts = content.split("---", 2)
    if len(parts) >= 3:
        updated = f"{parts[0]}---{parts[1]}---\n\n{new_entry}{parts[2]}"
    else:
        updated = content + f"\n{new_entry}"

    CHANGELOG_FILE.write_text(updated)
    print(f"  ✓ {CHANGELOG_FILE}: Added entry for {new_version}")


def main():
    print("\n📦 AI Email Routing Framework - Version Bump\n")

    # Get current version
    current = get_current_version()
    new = bump_version(current)

    print(f"Current version: {current}")
    print(f"New version:     {new}\n")

    # Confirm
    confirm = input("Proceed? (y/n): ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        sys.exit(0)

    # Get changelog notes
    print("\nEnter changelog notes (one per line, empty line to finish):")
    notes = []
    while True:
        note = input("  - ").strip()
        if not note:
            break
        notes.append(note)

    print("\nUpdating files...")

    # Update all files
    update_version_file(new)
    update_diagram(current, new)
    update_changelog(new, notes)

    print(f"\n✅ Bumped to v{new}\n")


if __name__ == "__main__":
    main()
