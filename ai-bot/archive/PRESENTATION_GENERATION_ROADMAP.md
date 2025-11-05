# Presentation Generation Roadmap - v0.4.1 & v0.4.2

**Status:** 🎯 IMMEDIATE PRIORITY
**Version:** v0.4.1 → v0.4.2
**Timeline:** 8-10 days total
**Last Updated:** 2025-10-28

**v0.4.1 Status:**
- ✅ Implementation COMPLETE (2025-10-27, 2 hours)
- ✅ Bot Integration COMPLETE (save_html_presentation_tool created and registered)
- ✅ Custom API Endpoint Fix APPLIED (env parameter in ClaudeAgentOptions)
- ✅ System Prompts UPDATED (3 bots with HTML output workflow guidance)
- ✅ Integration Testing COMPLETE (12/12 tests passing, 2025-10-28)
- ✅ Phase 9: Local Docker testing COMPLETE (2025-10-28)
  - ✅ Docker build issues resolved (LibreOffice split installation)
  - ✅ Tool import fixes applied (Build #6)
  - ✅ End-to-end testing verified (file download working)
  - ✅ Custom API endpoint working (HusanAI)
- ✅ **v0.4.1 READY FOR PRODUCTION DEPLOYMENT**
- 🔜 Next: v0.4.2 implementation (presentation generation)

**Testing Status:**
- ✅ docker-compose.dev.yml configured
- ✅ File access working (/campfire-files mount)
- ✅ File registration/download/stats endpoints tested
- ✅ Custom API endpoints working (env parameter passed to subprocess)
- ✅ Integration test suite passing (test_bot_file_download_integration.py)
- ✅ Local Docker end-to-end testing passing (Phase 9)

---

## Executive Summary

Enable Campfire AI bots to create interactive web presentations and data visualizations:
- 🎯 Slide presentations (reveal.js)
- 📊 Infographic dashboards (Chart.js)
- 📱 Inline previews + downloadable full versions
- 🤖 3 bots: Financial Analyst, Operations Assistant, Personal Assistant

---

## User Story

```
User: @财务分析师 Create Q3 financial performance presentation

Bot posts to Campfire:
┌─────────────────────────────────┐
│ 📊 Q3 Financial Performance     │
│ Key Metrics (Preview):          │
│ • Revenue: $1.2M (+23% YoY)     │
│ • Profit Margin: 32%            │
│ [Revenue Chart - Preview]       │
│ [🎯 View Full Presentation]     │
│ 7 slides • Link expires 1 hour  │
└─────────────────────────────────┘

User clicks → Full reveal.js presentation opens with:
- Interactive Chart.js charts
- Arrow key navigation
- Professional design
```

---

## Architecture

```
User Request → Bot Processing → Data Query (Supabase/MCP)
                    ↓
         ┌──────────┴──────────┐
         ↓                     ↓
    Full Version          Inline Preview
    (reveal.js HTML)      (Static HTML)
         ↓                     ↓
    File Registry         Post to Campfire
    (UUID token)          [Preview + Button]
         ↓
    Download Link
```

---

## Version 0.4.1: File Download System ✅ COMPLETE

**Status:** ✅ COMPLETE (2025-10-27, 2 hours)

**Components Implemented:**
- FileRegistry class (153 lines) - UUID token management
- Three REST endpoints: /files/register, /files/download/{token}, /files/stats
- Automatic expiry (1 hour, configurable)
- Background cleanup (every 5 minutes)
- HTML templates: generate_download_button() and generate_inline_preview()
- Timezone-aware datetime (timezone.utc)

**Files Created:**
- `src/file_registry.py` (153 lines)
- `src/presentation_utils.py` (184 lines)
- `test_file_download.py` (227 lines, 100% coverage)

**Architecture:**
```
Bot generates file → FileRegistry.register_file()
                            ↓
                    Returns UUID token
                            ↓
                    GET /files/download/{token}
                            ↓
                    File served (1-hour expiry)
```

**See source code:**
- `/Users/heng/Development/campfire/ai-bot/src/file_registry.py`
- `/Users/heng/Development/campfire/ai-bot/src/presentation_utils.py`

---

## Version 0.4.2: Presentation Generation

**Status:** Design complete, implementation pending
**Effort:** 6-8 days
**Priority:** HIGH

### Phase 1: Chart Generation Library (Day 1, 3-4 hours)

**Create:** `src/presentation/chart_generator.py`

**Class:** `ChartGenerator`
- Method: `generate_chart(data, chart_type, interactive=True)`
- Returns: `{html, script, static_svg}`
- Chart types: bar, line, pie, area, scatter
- Interactive mode: Chart.js (for full version)
- Static mode: matplotlib SVG (for inline preview)

**Example:**
```python
chart_generator.generate_chart(
    data={'labels': ['Jan', 'Feb'], 'datasets': [...]},
    chart_type='bar',
    interactive=True
)
# Returns: {html: '<canvas>', script: 'new Chart(...)', static_svg: '<svg>'}
```

### Phase 2: Slide Presentations (Days 2-3, 7-9 hours)

**Create:** `src/presentation/slide_generator.py`

**Class:** `SlideGenerator`
- Method: `generate_presentation(title, slides, style='financial')`
- Uses: Jinja2 templates + reveal.js
- Styles: financial, operations, general
- Templates: `templates/slides/{base,financial,operations}.html`

**Slide Structure:**
```json
{
  "title": "Revenue Breakdown",
  "metrics": [{"value": "$1.2M", "label": "Revenue", "change": "+23%"}],
  "chart": {"labels": [...], "datasets": [...]},
  "chart_type": "bar",
  "insights": ["Strong growth in Q1"]
}
```

**Features:**
- reveal.js framework (arrow key navigation)
- Chart.js integration (interactive charts)
- Metric cards with gradients
- Insights boxes
- Professional styling

### Phase 3: Infographic Reports (Days 4-5, 7-9 hours)

**Create:** `src/presentation/infographic_generator.py`

**Class:** `InfographicGenerator`
- Method: `generate_report(title, sections, style='dashboard')`
- Uses: Jinja2 templates (scrollable layout)
- Styles: dashboard, report, analysis
- Templates: `templates/infographic/{dashboard,report}.html`

**Section Structure:**
```json
{
  "title": "Performance Overview",
  "metrics": [...],
  "chart": {...},
  "table": {"headers": [...], "rows": [...]},
  "insights": [...]
}
```

**Features:**
- Scrollable single-page layout
- Metric cards with color themes
- Data tables
- Chart.js charts
- Insights boxes

### Phase 4: Inline Preview Generator (Day 6, 2-3 hours)

**Create:** `src/presentation/inline_preview.py`

**Class:** `InlinePreviewGenerator`
- Method: `generate_preview(title, summary, metrics, chart_data, download_token)`
- Returns: Campfire-safe HTML (no JavaScript)
- Features:
  - Static SVG charts (matplotlib)
  - Metric cards preview
  - Styled download button
  - Expiry notice

**Key constraint:** No JavaScript allowed in Campfire HTML

### Phase 5: Bot Integration (Day 7, 3-5 hours)

**Create:** `src/tools/presentation_decorators.py`

**Tools:**
1. `generate_slide_presentation_tool(args)`
   - Generates reveal.js presentation
   - Registers file with UUID token
   - Returns inline preview + download link

2. `generate_infographic_report_tool(args)`
   - Generates scrollable dashboard
   - Registers file with UUID token
   - Returns inline preview + download link

**Bot Configuration Updates:**
- Add tools to `financial_analyst.json`, `operations_assistant.json`, `personal_assistant.json`
- Add system prompt guidance for presentation generation
- Include data structure examples

**System Prompt Addition:**
```
When user requests presentation:
1. Determine format: slides vs dashboard
2. Choose style: financial/operations/general
3. Query data using existing tools
4. Structure data into slides/sections
5. Call generate_slide_presentation or generate_infographic_report
6. Post result (inline preview + download button)
```

---

## Implementation Flow

```
Day 1: Chart generation library (ChartGenerator)
  └─ Test: Interactive + static charts

Days 2-3: Slide presentations (SlideGenerator + templates)
  └─ Test: Full reveal.js presentation

Days 4-5: Infographic reports (InfographicGenerator + templates)
  └─ Test: Scrollable dashboard

Day 6: Inline preview generator (InlinePreviewGenerator)
  └─ Test: Campfire-safe HTML output

Day 7: Bot integration (presentation_decorators.py)
  └─ Test: End-to-end with bots

Day 8: Testing & refinement
  └─ Test: All 3 bots, multiple scenarios
```

---

## Dependencies

**Python Packages (add to pyproject.toml):**
```toml
dependencies = [
    "fastapi-utils>=0.2.1",  # Background tasks
    "jinja2>=3.1.0",         # Template engine
    "matplotlib>=3.8.0",     # Static chart generation
]
```

**External CDN (in templates):**
- reveal.js 4.6.0 (MIT license)
- Chart.js 4.4.0 (MIT license)
- Inter font (Google Fonts)

---

## Timeline Summary

| Phase | Duration | Status |
|-------|----------|--------|
| v0.4.1 File Download | 2 hours | ✅ COMPLETE |
| Phase 1: Charts | 3-4 hours | 🔜 Pending |
| Phase 2: Slides | 7-9 hours | 🔜 Pending |
| Phase 3: Infographics | 7-9 hours | 🔜 Pending |
| Phase 4: Preview | 2-3 hours | 🔜 Pending |
| Phase 5: Integration | 3-5 hours | 🔜 Pending |
| Testing | 2-3 hours | 🔜 Pending |
| **Total** | **27-40 hours (~4-5 days)** | |

---

## Success Criteria

✅ User requests: "@财务分析师 Create Q3 presentation"
✅ Bot generates both versions (full HTML + inline preview)
✅ Download link works (opens in browser)
✅ Charts are interactive (hover tooltips, animations)
✅ Slide navigation works (arrow keys)
✅ Links expire correctly (1 hour)
✅ 3 bots enabled (Financial, Operations, Personal)

---

## Future Enhancements (v0.5.0+)

1. Persistent file storage (DigitalOcean Spaces)
2. PDF export (presentations to PDF)
3. Custom themes (user-selectable colors)
4. Animation templates (pre-built sequences)
5. Collaboration (share via unique URLs)
6. Analytics (track views, downloads)
7. More chart types (Gantt, heatmaps, treemaps)

---

**Status:** Ready for v0.4.2 Implementation
**Next Step:** Begin Phase 1 (Chart Generation Library)
**Deployment Target:** v0.4.2 in 5-7 days
