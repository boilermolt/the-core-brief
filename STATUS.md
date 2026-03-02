# The Core Brief - Project Status

**Last updated:** 2026-03-02

---

## 🎯 Current Status: **Pilot Phase Complete**

✅ All infrastructure built  
✅ Pilot #1 drafted and revised  
✅ Editorial guidelines established  
✅ Ready for weekly operations  

---

## ✅ Completed

### Infrastructure
- [x] Source aggregator (RSS feeds + NRC events scraper + Reddit monitoring)
- [x] SQLite database (story tracking, topic extraction, deep dive planning)
- [x] Obsidian integration (auto-export with frontmatter + wikilinks)
- [x] Web dashboard (Flask app for story review)
- [x] Editorial guidelines documentation

### Content
- [x] Pilot #1 drafted (2026-03-02)
  - 5 top stories with expanded analysis
  - "In Brief" section (4 quick hits)
  - "What to Watch" section
  - ~16KB, 10-12 min read
- [x] Database coverage tracking (9/84 stories marked as covered)
- [x] Bio/disclaimer revised (no "insider" language, open-source only)

### Documentation
- [x] `PLAN.md` - Project overview
- [x] `DATABASE.md` - Database schema and CLI usage
- [x] `EDITORIAL-GUIDELINES.md` - Sourcing rules, workflow, voice/tone
- [x] `README.md` - Public-facing project description
- [x] `STATUS.md` - This file

---

## 📊 By The Numbers

- **84 stories** in database (aggregated from last 7 days)
- **11 topics** auto-extracted
- **9 stories** covered in Pilot #1
- **8 RSS feeds** monitored
- **2 Reddit communities** monitored (r/nuclear, r/NuclearPower)
- **1 NRC events scraper** operational

### Trending Topics (Last 30 Days)
1. NRC Oversight (11 stories)
2. IAEA (8 stories)
3. Radiation Safety (7 stories)
4. Licensing (4 stories)
5. Advanced Reactors (4 stories)

### Deep Dive Candidates (3+ stories)
- NRC Oversight (11 stories)
- IAEA (8 stories)
- Radiation Safety (7 stories)

---

## 🔄 Weekly Workflow

1. **Saturday/Sunday:** Run aggregator
   ```bash
   cd ~/clawd/projects/the-core-brief
   source venv/bin/activate
   python src/aggregator.py
   ```

2. **Import to database**
   ```bash
   python src/import_aggregator_to_db.py
   ```

3. **Review trends & uncovered stories**
   ```bash
   python src/story_db.py trending
   python src/story_db.py uncovered
   ```

4. **Draft edition (Monday)**
   - Select 3-5 top stories from uncovered queue
   - Use `web_fetch` to get full story details
   - Write analysis (200-400 words per top story)
   - Add 3-5 quick hits for "In Brief"
   - Add 2-3 items for "What to Watch"
   - Save to `drafts/YYYY-MM-DD.md`

5. **Mark stories as covered**
   ```bash
   python src/mark_pilot_covered.py  # (adapt for each edition)
   ```

6. **Export to Obsidian**
   ```bash
   python scripts/export_to_obsidian.py
   ```

7. **Publish to Substack** (when ready)

---

## 📅 Next Steps

### Immediate (This Week)
- [ ] Run weekly aggregation cycle (Sat/Sun, March 8-9)
- [ ] Draft Pilot #2 (week of March 9)
- [ ] Review and iterate format based on Pilot #1 feedback

### Short Term (Next 2-3 Weeks)
- [ ] Complete Pilot #3
- [ ] Set up Substack account
- [ ] Finalize newsletter name/branding
- [ ] Plan first monthly deep dive topic
- [ ] Decide on publication cadence (Monday AM? Friday PM?)

### Medium Term (Next Month)
- [ ] Launch publicly on Substack
- [ ] Publish first monthly deep dive
- [ ] Build initial subscriber base
- [ ] Establish social media presence (if desired)
- [ ] Consider adding more sources (Google News API, additional regulatory feeds)

---

## 🎨 Design Decisions

### Format
- **Weekly digest:** 5-10 min read (3-5 stories + brief + watch)
- **Monthly deep dive:** 15-20+ min read (2000-3000 words)

### Platform
- **Substack** (better discovery, easy to start, own email list)

### Monetization
- **Free to start**, paid tier can come later

### Voice
- Technical but accessible
- Direct, factual, no hype
- Context for non-specialists
- No fearmongering, no PR

---

## 📝 Editorial Principles

1. **Open sources only** - No proprietary or insider information
2. **No insider claims** - Don't position as "insider perspective"
3. **Technical but accessible** - Smart readers, may not be domain experts
4. **No promotional content** - No vendor PR or advocacy
5. **No fearmongering** - Factual incident coverage with technical context

See `EDITORIAL-GUIDELINES.md` for full details.

---

## 🔗 Links

- **GitHub:** https://github.com/boilermolt/the-core-brief
- **Obsidian vault:** `/media/boilerrat/Bobby/ObsidianVaults/Claw/Claw/AI/Boilermolt/The Core Brief/`
- **Local project:** `~/clawd/projects/the-core-brief/`

---

## 📞 Contact

- **Feedback:** [Open an issue on GitHub](https://github.com/boilermolt/the-core-brief/issues)
