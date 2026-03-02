#!/usr/bin/env python3
"""
Mark Pilot #1 stories as covered in the database.
"""

from story_db import StoryDB

# URLs of stories covered in Pilot #1
PILOT_1_STORIES = {
    "https://www.ans.org/news/2026-02-26/article-7801/nrc-staff-proposes-rop-security-inspection-overhauls/": "top-stories",
    "http://www.iaea.org/newscenter/pressreleases/iaea-coordinated-research-finds-variation-in-radiation-doses-from-cardiac-imaging-highlights-areas-to-enhance-patient-safety": "top-stories",
    "https://reddit.com/r/NuclearPower/comments/1rgww63/diablo_canyon_has_cleared_one_of_the_last_hurdles/": "top-stories",
    "https://www.ans.org/news/2026-02-27/article-7804/tests-back-shielding-plan-for-kairos-power/": "top-stories",
    "https://www.ans.org/news/2026-02-26/article-7800/nrc-ends-work-on-three-proposed-rules-for-securing-spent-fuel/": "top-stories",
    "https://www.ans.org/news/2026-02-23/article-7780/triso-pebble-lifecycle-studied-in-new-ornl-kairos-power-partnership/": "in-brief",
    "https://www.ans.org/news/2026-02-23/article-7774/inl-teams-with-nvidia-in-prometheus-project-to-accelerate-nuclear-deployment/": "in-brief",
    "http://www.iaea.org/newscenter/news/georgia-signs-an-extension-of-its-country-programme-framework-cpf-for-2020-2028": "in-brief",
    "https://reddit.com/r/nuclear/comments/1rgd9vz/the_trump_administrations_favorite_nuclear/": "in-brief"
}

EDITION_DATE = "2026-03-02"

def main():
    db = StoryDB()
    
    marked_count = 0
    not_found = []
    
    for url, section in PILOT_1_STORIES.items():
        # Find story by URL
        with db.db_path.open() as conn:
            import sqlite3
            conn = sqlite3.connect(db.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM stories WHERE url = ?", (url,))
            result = cursor.fetchone()
            
            if result:
                story_id = result[0]
                db.mark_covered(story_id, EDITION_DATE, section)
                marked_count += 1
                print(f"✓ Marked story {story_id} as covered ({section})")
            else:
                not_found.append(url)
                print(f"✗ Story not found: {url}")
    
    print(f"\n✓ Marked {marked_count} stories as covered in edition {EDITION_DATE}")
    
    if not_found:
        print(f"\n⚠ {len(not_found)} stories not found in database:")
        for url in not_found:
            print(f"  - {url}")

if __name__ == "__main__":
    main()
