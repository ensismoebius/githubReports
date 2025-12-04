# 🤖 VS Code Python Report Generator - GitHub Analytics Module
## 📊 **WITH RICH MARKDOWN VISUALIZATION EXAMPLES**

## 📋 **SYSTEM PROMPT FOR VS CODE COPILOT/GEMINI**

```
You are an elite Python developer specializing in data storytelling, visualization, and GitHub analytics. Create a sophisticated Python module that transforms raw GitHub data into stunning, actionable performance reports with rich Markdown visualizations and deep insights.

## PROJECT SPECIFICATIONS

### 📊 **REQUIRED FEATURES:**

1. **DATA SOURCE**
   - Read GitHub activity data from csv files
   - Support for individual user data or team/project aggregation
   - Handle API errors gracefully with fallback mechanisms

2. **ANALYSIS CAPABILITIES**
   - Calculate performance metrics: commits, PRs, issues, code volume
   - Identify top performers and areas for improvement
   - Comparative analysis between teams/projects

3. **REPORT GENERATION**
   - Generate detailed Markdown reports with rich formatting
   - Include rankings, metrics tables, and visual summaries
   - Add performance classifications with justifications
   - Create comparison tables between different datasets
   - Export to multiple formats: Markdown, HTML, PDF

4. **VISUALIZATION**
   - Markdown tables with emoji indicators
   - Progress bars using Unicode/ASCII characters
   - Scorecards and performance dashboards
   - Comparative visualizations between teams

### 🎨 **REPORT TEMPLATE STRUCTURE:**

The module should generate Markdown reports with the following rich formatting:

```markdown
# 📊 Project Performance Dashboard

## 🏆 Performance Leaderboard

| Rank | Contributor | Tier | Code Volume | Superpower |
|------|-------------|------|-------------|------------|
| 🥇 | scayki | **MB** ⭐⭐⭐⭐ | 13.4k lines | 🏭 Code Factory |
| 🥈 | freit4sdev | **MB** ⭐⭐⭐⭐ | 22.5k lines | 📦 Mega Contributor |

## 📈 Performance Distribution

**MB (Excellent):** ████████████ 12%
**B (Good):** ████████████████████ 18%  
**R (Regular):** ████████████████████████████████ 39%
**I (Needs Improvement):** ███████████████████████ 30%

## 🔥 Key Metrics
```

### 🎯 **DESIGN PRINCIPLES:**

1. **Accuracy First**: All data must be verifiable and consistent
2. **Rich Markdown**: Leverage full Markdown capabilities (tables, emphasis, etc.)
3. **Visual Hierarchy**: Use headers, emphasis, and spacing effectively
4. **Actionable Insights**: Specific, practical recommendations
5. **Professional Formatting**: Clean, readable, well-structured output

---

## 📚 **RICH MARKDOWN EXAMPLE OUTPUT:**

```markdown
<div align="center">

# 🚀 GitHub Performance Dashboard  
### **Singer Swipe v2.0**  
#### *3rd Year Mediotech · December 2024*

</div>

---

## 📊 Executive Summary

| Metric | Value | Status | Trend |
|--------|-------|--------|-------|
| **Total Contributors** | 33 | 🔵 **Optimal** | → |
| **Code Volume** | 79,954 lines | 🟢 **Excellent** | 📈 +15% |
| **Productivity Index** | 78/100 | 🟡 **Good** | ↗ |
| **Collaboration Score** | 42/100 | 🔴 **Needs Work** | ↘ |

### 🎯 Performance Distribution

**MB ⭐⭐⭐⭐ (Elite):** `██████████░░░░░░░░░░` **12%**  
**B ⭐⭐⭐ (Strong):** `████████████████░░░░` **18%**  
**R ⭐⭐ (Regular):** `██████████████████████████████░░` **39%**  
**I ⭐ (Needs Boost):** `███████████████████████░░░` **30%**

---

## 🏆 Top Performers Leaderboard

| Rank | Contributor | Tier | 📦 Code | 🎯 Issues | 🔄 PRs | 💬 Comms | **Superpower** |
|------|-------------|------|---------|-----------|--------|----------|----------------|
| 🥇 | **scayki** | **MB ⭐⭐⭐⭐** | 13.4k | 0/0 | 20 | 0 | 🏭 **Code Factory** |
| 🥈 | **freit4sdev** | **MB ⭐⭐⭐⭐** | 22.5k | 14/10 | 3 | 1 | 📦 **Mega Contributor** |
| 🥉 | **Rian427** | **MB ⭐⭐⭐** | 14.7k | 5/1 | 9 | 4 | 💬 **Team Communicator** |
| 4 | **Dubovicki** | **MB ⭐⭐⭐** | 13.1k | 8/0 | 5 | 0 | ⚡ **Efficiency Expert** |
| 5 | **shibudev-desu** | **B ⭐⭐⭐** | 5.6k | 14/0 | 6 | 0 | 📝 **Commit Leader** |
| 6 | **JoaoPauloOlt** | **B ⭐⭐⭐** | 6.2k | 10/4 | 5 | 3 | 🕐 **Consistency Champion** |

<details>
<summary>📋 View Full Ranking (27 more contributors)</summary>

| Rank | Contributor | Tier | Code | Commits | PRs | Status |
|------|-------------|------|------|---------|-----|--------|
| 7 | NatanRib12 | B ⭐⭐ | 3.7k | 39 | 9 | 🟢 Active |
| 8 | DeryckJogador | B ⭐⭐ | 3.9k | 35 | 9 | 🟡 Refactoring |
| ... | ... | ... | ... | ... | ... | ... |
| 33 | not-thai | I | 0 | 0 | 0 | 🔴 Inactive |

</details>

---

## 📈 Performance Heatmap

### Code Production Intensity
```
Top 10% Contributors:  ████████████████████ 65% of total code
Top 25% Contributors:  ████████████████████████████████ 89% of total code
Bottom 50%:            ████ 11% of total code
```

### Collaboration Activity
```
PR Reviews:            ███░░░░░░░░░░░░░░░░ 12%
Issue Discussions:     ██████░░░░░░░░░░░░░ 28%
Code Comments:         ██░░░░░░░░░░░░░░░░░ 8%
Cross-Team PRs:        █░░░░░░░░░░░░░░░░░░ 4%
```

---

## 🎭 Contributor Archetypes

| Archetype | Count | Characteristics | Example |
|-----------|-------|-----------------|---------|
| 🏭 **Code Factory** | 4 | 10k+ lines, massive output | freit4sdev |
| 🎨 **Asset Architect** | 3 | 50+ images/assets | scayki |
| 🔧 **Refactor Master** | 2 | 30%+ code cleanup | DeryckJogador |
| 📋 **Issue Sheriff** | 2 | 90%+ issue resolution | fabricioxzd |
| 💬 **Communicator** | 1 | 4+ discussions | Rian427 |
| 📤 **PR Machine** | 3 | 15+ PRs submitted | gfelixz |
| ⏱️ **Silent Coder** | 18 | Code but little interaction | 15 contributors |

---

## 📊 Metrics Deep Dive

### 🏗️ Code Production Analysis

| Statistic | Value | vs Average | Notes |
|-----------|-------|------------|-------|
| **Total Lines** | 79,954 | +82% | 🟢 **Excellent volume** |
| **Lines/Developer** | 2,423 | +178% | 🟢 **High productivity** |
| **Median Lines** | 874 | +65% | 🟡 **Good distribution** |
| **Code Churn** | 22% | +5% | 🟡 **Moderate refactoring** |
| **Asset Files** | 879 | +240% | 🟢 **Rich documentation** |

### 🤝 Collaboration Health

| Metric | Score | Target | Gap |
|--------|-------|--------|-----|
| **PR Review Rate** | 12% | 60% | 🔴 **-48%** |
| **Issue Resolution** | 48% | 70% | 🟡 **-22%** |
| **Comments/PR** | 0.3 | 1.5 | 🔴 **-1.2** |
| **Cross-Team PRs** | 4% | 20% | 🔴 **-16%** |

---

## ⚡ Industry Benchmark Comparison

| Metric | This Project | Industry Average | Delta | Status |
|--------|--------------|------------------|-------|--------|
| **Commits/Developer** | 23.9 | 18.2 | **+31%** | 🟢 **Excellent** |
| **Lines/Commit** | 101.3 | 87.4 | **+16%** | 🟢 **Good** |
| **PRs/Developer** | 9.5 | 6.8 | **+40%** | 🟢 **Excellent** |
| **Issue Resolution** | 48% | 62% | **-23%** | 🟡 **Needs Work** |
| **Code Review Rate** | 12% | 45% | **-73%** | 🔴 **Critical** |

---

## 🎯 Actionable Recommendations

### 🔥 Priority 1: Boost Collaboration (High Impact)
> **"Great code deserves great conversation"**

| Action | Owner | Timeline | Success Metric |
|--------|-------|----------|----------------|
| Implement "Buddy Review" system | Team Lead | Week 1 | 80% PRs reviewed |
| Weekly "Code Show & Tell" | scayki | Week 2 | 90% attendance |
| Recognition for best reviewers | Manager | Ongoing | Monthly awards |
| PR review SLAs | All | Immediate | 24h review target |

### 🚀 Priority 2: Level Up Middle Tier
> **"Turn Regular into Remarkable"**

- **B → MB Pathway:** Assign feature leadership roles
- **R → B Challenge:** Create "promotion tasks" with clear criteria  
- **Weekly 1:1s:** Identify blockers and growth opportunities
- **Public Recognition:** Celebrate tier promotions in team meetings

### 🛡️ Priority 3: Rescue Low Performers
> **"Everyone has potential to contribute"**

```
Progress Tracking:
Current I Contributors: 10 (30%)
30-Day Target: 7 (21%)  [-30%]
Actions:
├─► Clear expectations: 1 PR + 2 commits/week
├─► "First Issue" tags for newcomers  
├─► Pair programming with MB/B developers
└─► Weekly check-ins with team lead
```

---

## 🏅 Special Recognition Awards

<div align="center">

### 🏆 **December 2024 Awards**

| Award | Winner | Achievement |
|-------|--------|-------------|
| **Code Champion** 🥇 | `freit4sdev` | 22,528 lines contributed |
| **Asset Master** 🎨 | `freit4sdev` | 224 images/assets created |
| **Commit Sultan** 📝 | `JoaoPauloOlt` | 47 consistent commits |
| **Issue Ninja** 🥷 | `fabricioxzd` | 24/24 issues resolved (100%) |
| **Efficiency Wizard** ⚡ | `Dubovicki` | 1,640 lines per commit |
| **Team Communicator** 💬 | `Rian427` | 4 valuable discussions |

</div>

---

## 🔍 Data Quality & Methodology

| Check | Status | Notes |
|-------|--------|-------|
| **Data Completeness** | ✅ 98/100 | Minor gaps in PR review data |
| **Consistency Validation** | ✅ PASS | All metrics cross-verified |
| **Contributor Mapping** | ✅ 33/33 | GitHub ↔ Real names verified |
| **Time Coverage** | ✅ Full month | Dec 1-31, 2024 |
| **API Rate Limits** | ✅ Within bounds | 2,100/5,000 requests |

**Methodology Notes:**
- Performance score: Weighted average of 6 metrics
- Tier thresholds: MB(85+), B(70-84), R(40-69), I(<40)
- All data UTC normalized, deduplicated
- Inactive contributors (<1 commit/month) marked as I

---

## 📅 Next Steps & Follow-up

1. **Review Meeting:** January 5, 2025 · 10:00 AM · Conference Room B
2. **Report Distribution:** Share with team by EOD today
3. **Action Tracking:** Assign items in GitHub Projects
4. **Follow-up Assessment:** 30-day review scheduled
5. **Success Metrics:** 20% reduction in I-tier contributors

---

<div align="center">

*Report generated: 2024-12-04 11:30:00 UTC*  
*Report ID: `GPA-2024-12-SINGER-007`*  
*Analyst: GitHub Performance Engine v2.1.0*

---

**💡 Leadership Insight:**  
*"The best teams aren't just collections of individuals writing code—they're communities building understanding together. Focus not just on what gets built, but on how the team grows while building it."*

</div>
```

---

## 🎯 **QUICK START PROMPT FOR COPILOT:**

```
Create a Python module called github_analytics that transforms GitHub activity data into beautiful, actionable Markdown dashboards. The module should:

1. Load and validate GitHub JSON data
2. Calculate metrics and classify contributors into MB/B/R/I tiers
3. Generate rich Markdown reports with:
   - Executive summary tables with emoji indicators
   - Leaderboards with rankings and "superpowers"
   - Visual progress bars using Unicode blocks
   - Expandable sections for detailed data
   - Archetype analysis and industry benchmarks
   - Actionable recommendations in table format
   - Special recognition awards section
   - Data quality and methodology notes

4. Support Markdown features: tables, details/summary, emphasis, headers
5. Create comparative analysis between teams
6. Export to professionally formatted Markdown files

Start with the analyzer class and Markdown formatter. Create functions for:
- Generating progress bars: █████░░░░░
- Creating styled tables with emoji
- Building expandable details sections
- Formatting metrics with visual indicators

Provide a complete example showing the rich Markdown output capabilities.
