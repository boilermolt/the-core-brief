#!/usr/bin/env python3
"""
Export The Core Brief editions to Obsidian vault with graph-friendly frontmatter.

Creates one note per edition with:
- Frontmatter tags for stories, sources, keywords
- Wikilinks to key topics for graph visualization
- Backlinks between related editions
"""

from pathlib import Path
import re
from datetime import datetime
import yaml

OBSIDIAN_VAULT = Path("/media/boilerrat/Bobby/ObsidianVaults/Claw/Claw")
OBSIDIAN_CORE_BRIEF_DIR = OBSIDIAN_VAULT / "AI" / "Boilermolt" / "The Core Brief"
DRAFTS_DIR = Path(__file__).parent.parent / "drafts"


def extract_metadata(content: str) -> dict:
    """Extract metadata from markdown content."""
    meta = {
        'tags': set(),
        'sources': set(),
        'keywords': set(),
        'topics': set(),
        'stories': []
    }
    
    # Extract story titles (## headers after "Top Stories")
    in_top_stories = False
    for line in content.split('\n'):
        if '## This Week\'s Top Stories' in line or '## Top Stories' in line:
            in_top_stories = True
            continue
        if in_top_stories and line.startswith('### '):
            title = line.replace('###', '').strip()
            # Remove trailing numbers (e.g., "1. Story Title" -> "Story Title")
            title = re.sub(r'^\d+\.\s*', '', title)
            meta['stories'].append(title)
        if in_top_stories and line.startswith('## '):
            in_top_stories = False
    
    # Extract sources from links
    source_pattern = r'\*\*Source:\*\*\s*\[(.*?)\]'
    meta['sources'] = set(re.findall(source_pattern, content))
    
    # Extract keywords from code blocks
    keyword_pattern = r'`([^`]+)`'
    meta['keywords'] = set(re.findall(keyword_pattern, content))
    
    # Extract topics (common nuclear industry terms)
    topics = [
        'NRC', 'IAEA', 'radiation safety', 'inspection', 'licensing',
        'advanced reactors', 'spent fuel', 'TRISO', 'SMR', 'security',
        'shielding', 'dose', 'ALARA', 'reactor oversight'
    ]
    for topic in topics:
        if topic.lower() in content.lower():
            meta['topics'].add(topic)
    
    # Base tags
    meta['tags'].add('nuclear-industry')
    meta['tags'].add('core-brief')
    meta['tags'].add('newsletter')
    
    return meta


def create_wikilinks(content: str, meta: dict) -> str:
    """Replace first occurrence of key topics with wikilinks."""
    replacements = {
        'Reactor Oversight Process': '[[Reactor Oversight Process|ROP]]',
        'Force-on-Force': '[[Force-on-Force Exercises]]',
        'TRISO': '[[TRISO Fuel]]',
        'fluoride salt-cooled high-temperature reactor': '[[Fluoride Salt-Cooled High-Temperature Reactor|FHR]]',
        'dry cask storage': '[[Dry Cask Storage]]',
        'ALARA': '[[ALARA]]',
        'coronary artery disease': '[[Coronary Artery Disease|CAD]]',
        'spent fuel': '[[Spent Nuclear Fuel]]',
    }
    
    modified = content
    for term, link in replacements.items():
        # Only replace first occurrence to avoid cluttering
        modified = modified.replace(term, link, 1)
    
    return modified


def generate_frontmatter(edition_date: str, meta: dict) -> str:
    """Generate YAML frontmatter for Obsidian."""
    frontmatter = {
        'date': edition_date,
        'type': 'newsletter-edition',
        'publication': 'The Core Brief',
        'edition': 'pilot',
        'tags': sorted(list(meta['tags'])),
        'sources': sorted(list(meta['sources'])),
        'topics': sorted(list(meta['topics'])),
        'stories': meta['stories']
    }
    
    return '---\n' + yaml.dump(frontmatter, sort_keys=False, allow_unicode=True) + '---\n\n'


def export_edition(draft_path: Path):
    """Export a single edition to Obsidian."""
    content = draft_path.read_text()
    
    # Extract date from filename (assumes YYYY-MM-DD-*.md)
    date_match = re.match(r'(\d{4}-\d{2}-\d{2})', draft_path.stem)
    if not date_match:
        print(f"Could not extract date from {draft_path.name}")
        return
    
    edition_date = date_match.group(1)
    
    # Extract metadata
    meta = extract_metadata(content)
    
    # Add wikilinks
    content_with_links = create_wikilinks(content, meta)
    
    # Generate frontmatter
    frontmatter = generate_frontmatter(edition_date, meta)
    
    # Combine
    final_content = frontmatter + content_with_links
    
    # Write to Obsidian
    output_dir = OBSIDIAN_CORE_BRIEF_DIR / "Editions"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{edition_date}.md"
    
    output_path.write_text(final_content)
    print(f"✓ Exported {edition_date} to {output_path}")
    
    return output_path


def update_index():
    """Update the main index file with links to all editions."""
    editions_dir = OBSIDIAN_CORE_BRIEF_DIR / "Editions"
    if not editions_dir.exists():
        return
    
    editions = sorted(editions_dir.glob("*.md"), reverse=True)
    
    index_content = "# The Core Brief - Edition Index\n\n"
    index_content += "*Auto-generated index of all newsletter editions.*\n\n"
    index_content += "## Recent Editions\n\n"
    
    for edition_path in editions:
        date = edition_path.stem
        index_content += f"- [[{date}]] - {date}\n"
    
    index_path = OBSIDIAN_CORE_BRIEF_DIR / "Edition Index.md"
    index_path.write_text(index_content)
    print(f"✓ Updated index at {index_path}")


def main():
    """Export all draft editions to Obsidian."""
    if not OBSIDIAN_VAULT.exists():
        print(f"Error: Obsidian vault not found at {OBSIDIAN_VAULT}")
        return 1
    
    OBSIDIAN_CORE_BRIEF_DIR.mkdir(parents=True, exist_ok=True)
    
    drafts = sorted(DRAFTS_DIR.glob("*.md"))
    
    if not drafts:
        print("No drafts found to export.")
        return 0
    
    print(f"Found {len(drafts)} draft(s) to export...\n")
    
    for draft in drafts:
        export_edition(draft)
    
    print()
    update_index()
    
    print(f"\n✓ Export complete. Check Obsidian vault at:")
    print(f"  {OBSIDIAN_CORE_BRIEF_DIR}")


if __name__ == "__main__":
    exit(main())
