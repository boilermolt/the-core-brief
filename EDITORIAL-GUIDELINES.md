# The Core Brief - Editorial Guidelines

## Mission

Systematic, technical coverage of the global nuclear industry with a focus on radiation safety, reactor technology, policy, and the stories that don't make mainstream headlines.

---

## Core Principles

### 1. **Open Sources Only**
- All sources must be publicly available
- Regulatory filings (NRC, IAEA, national regulators)
- Industry publications (ANS, World Nuclear News, NEI)
- Research journals (arXiv, peer-reviewed publications)
- Community discussions (Reddit, public forums)
- News outlets and trade press
- **NO proprietary information**
- **NO inside information from workplace or personal contacts**
- **NO confidential or restricted data**

### 2. **No Insider Claims**
- Do not position the newsletter as "insider perspective"
- Do not imply access to non-public information
- Do not claim special access or privileged knowledge
- Technical expertise is acceptable; inside information is not

### 3. **Technical But Accessible**
- Write for technically literate readers
- Provide context for non-specialists
- Explain acronyms and industry jargon
- Assume readers are smart but may not be domain experts

### 4. **No Promotional Content**
- No industry PR disguised as news
- No vendor promotion
- No advocacy for specific companies or technologies (analysis is fine)
- Disclose any potential conflicts of interest

### 5. **No Fearmongering**
- Incidents should be covered factually, not sensationally
- Provide technical context for radiation/dose numbers
- Distinguish between hazards and actual risks
- Avoid "nuclear disaster" framing unless genuinely warranted

---

## Content Types

### Weekly Digest (5-10 min read)
- **3-5 top stories** with substantive analysis (200-400 words each)
- **"In Brief" section** with 3-5 quick hits (50-100 words each)
- **"What to Watch" section** highlighting developing stories, comment periods, expected milestones

### Monthly Deep Dive (15-20+ min read)
- Long-form investigative piece on one topic
- Must have 3+ related stories in the database to justify
- Topics selected based on:
  - Trending topics analysis (last 30 days)
  - Deep dive candidate scoring (story count + relevance)
  - Timeliness and reader interest

---

## Sourcing Rules

### Attribution
- Every story must link to primary source
- Use format: `**Source:** [Publication Name](URL)`
- Credit aggregators when stories come from Reddit/forums

### Source Priority
1. **Primary sources** (regulatory docs, research papers, official statements)
2. **Industry trade press** (ANS Nuclear Newswire, NEI, World Nuclear News)
3. **General news outlets** (Reuters, Bloomberg, AP)
4. **Community discussions** (Reddit, forums) - use for identifying stories, not as sole source

### Verification
- Cross-check claims against primary sources when possible
- If only one source available, note that explicitly
- Distinguish between "reported" and "confirmed" information

---

## Database Workflow

### Story Lifecycle

1. **Discovered** (default status when imported from aggregator)
   - Story appears in aggregator cache
   - Imported to database via `import_aggregator_to_db.py`
   - Topics auto-extracted via keyword matching
   - Relevance score calculated

2. **Monitoring** (optional, for developing stories)
   - Story has potential but needs more developments
   - Follow-up entry created with expected date
   - Checked periodically for updates

3. **Covered** (published in an edition)
   - Story appears in weekly digest or deep dive
   - Edition date and section recorded
   - Coverage status updated

4. **Archived** (resolved, no longer relevant)
   - Story no longer newsworthy
   - Removed from active consideration

### Weekly Workflow

1. **Saturday/Sunday:** Run aggregator
   ```bash
   python src/aggregator.py
   ```

2. **Import to database**
   ```bash
   python src/import_aggregator_to_db.py
   ```

3. **Review trending topics**
   ```bash
   python src/story_db.py trending
   python src/story_db.py uncovered
   ```

4. **Draft edition** (Monday)
   - Select 3-5 top stories from uncovered queue
   - Select 3-5 quick hits for "In Brief"
   - Identify 2-3 developments for "What to Watch"
   - Use `web_fetch` to pull full story details for top stories

5. **Mark stories as covered**
   - Update database with edition date and section
   - Create script for each edition (see `mark_pilot_covered.py`)

6. **Export to Obsidian**
   ```bash
   python scripts/export_to_obsidian.py
   ```

### Monthly Deep Dive Planning

1. **Query deep dive candidates** (last week of month)
   ```bash
   python src/story_db.py candidates
   ```

2. **Review topics with 3+ stories**
   - Check recency (last story date)
   - Verify topic is still relevant/timely
   - Confirm enough material for long-form piece

3. **Research & draft** (throughout month)
   - Pull all related stories from database
   - Identify additional sources not yet in database
   - Draft long-form analysis (2000-3000 words)

---

## Voice & Tone

### Do:
- Be direct and factual
- Use technical terminology correctly
- Provide context for regulatory/technical developments
- Acknowledge uncertainty when it exists
- Compare to similar precedents when relevant

### Don't:
- Use promotional language ("game-changing", "revolutionary")
- Engage in hype or speculation without clear framing
- Make definitive predictions about regulatory outcomes
- Oversimplify complex technical issues for dramatic effect
- Use fear-based or sensational framing

---

## Topics to Cover

### Priority Areas
- **Radiation Safety:** Incidents, protocols, equipment, dose reduction, ALARA programs
- **Regulatory Developments:** NRC/CNSC/IAEA actions, rule changes, enforcement, inspection findings
- **Advanced Reactors:** SMRs, Gen IV designs, licensing milestones, technology demonstrations
- **Licensing:** Construction permits, operating licenses, extensions, amendments
- **Workforce & Operations:** Training, safety culture, staffing, outages
- **Technology:** Fuel cycles, waste management, instrumentation, digital I&C
- **Policy:** Energy policy, climate/decarbonization, financing, public perception
- **International:** Global projects, regulatory harmonization, IAEA activities

### De-Prioritize
- Political horse-race coverage (unless directly affects regulatory/technical outcomes)
- Opinion pieces or think-tank advocacy (unless it's high-quality technical analysis)
- Marketing/PR announcements without substantive technical content
- Social media drama or personality conflicts

---

## Quality Standards

### Before Publishing
- [ ] All sources are open and publicly available
- [ ] No insider/proprietary claims made
- [ ] Technical accuracy verified (cross-check key facts)
- [ ] Links tested and functional
- [ ] Acronyms explained on first use
- [ ] Stories marked as covered in database
- [ ] Exported to Obsidian with proper frontmatter

### Edition Checklist
- [ ] 3-5 top stories with analysis
- [ ] "In Brief" section (3-5 items)
- [ ] "What to Watch" section (2-3 items)
- [ ] About section with proper disclaimer
- [ ] Sources list at bottom
- [ ] Next edition date noted

---

## Revision History

- **2026-03-02:** Initial guidelines established (Pilot #1 feedback)
