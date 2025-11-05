---
name: presentation-generation
description: "Create interactive HTML presentations with professional design, data visualization, and download support. Use this skill when users request presentations, slides, or visual reports."
version: 1.0.0
license: MIT
---

# HTML Presentation Generation Skill

## Overview

This skill provides workflows for creating professional, interactive HTML presentations that users can download and view in their browsers. Presentations support data visualization, responsive design, and cross-browser compatibility.

## When to Use This Skill

Load this skill when users request:
- "创建演示文稿" / "Create a presentation"
- "生成幻灯片" / "Generate slides"
- "HTML presentation"
- "Interactive slides"
- "Data visualization report"

## Supported Features

- 📊 **Data Visualization** - Charts, graphs, infographics
- 🎨 **Professional Design** - reveal.js style, responsive layouts
- 🔄 **Interactive Elements** - Hover effects, animations, navigation
- 📱 **Cross-Platform** - Works on desktop, tablet, mobile
- ⬇️ **Download Support** - UUID token-based file downloads

## 🚨 CRITICAL WORKFLOW - Must Follow Exactly

### Step 1: Create HTML Content

Design professional HTML presentation content:

**Requirements:**
- Use reveal.js framework OR custom slide格式
- Include complete CSS styles
- Add JavaScript for interactivity (optional)
- Ensure responsive design
- Support Chinese text rendering

**Example Structure:**
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Presentation Title</title>
  <style>
    /* Professional styles */
    body { font-family: 'Inter', 'PingFang SC', sans-serif; }
    .slide { min-height: 100vh; padding: 40px; }
    h1 { color: #2c5aa0; font-size: 3em; }
    /* ... more styles */
  </style>
</head>
<body>
  <div class="slide" id="slide1">
    <h1>Presentation Title</h1>
    <p>Introduction content...</p>
  </div>
  <div class="slide" id="slide2">
    <h2>Main Points</h2>
    <ul>
      <li>Point 1</li>
      <li>Point 2</li>
    </ul>
  </div>
  <!-- More slides -->
</body>
</html>
```

### Step 2: Call save_html_presentation Tool

Save the HTML content using the tool:

**Tool Signature:**
```
save_html_presentation(
  html_content: str,    # Complete HTML document
  filename: str,        # e.g., "quarterly_report.html"
  title: str           # Human-readable title
)
```

**Example:**
```python
save_html_presentation(
  html_content=complete_html,
  filename="q3_financial_presentation.html",
  title="Q3 Financial Performance Presentation"
)
```

### Step 3: Output Tool's HTML Exactly (⚠️ CRITICAL)

**THE MOST IMPORTANT STEP - MUST NOT DEVIATE**

The `save_html_presentation` tool returns a **styled download button** as HTML code. You **MUST**:

✅ **DO:**
- Include the tool's HTML output **exactly as returned**
- Do NOT modify, summarize, or paraphrase
- Do NOT create your own download link
- Copy-paste the entire `<div>` and `<a>` tags with all styles

❌ **DO NOT:**
- Write your own download button HTML
- Summarize the file information in text
- Create manual download links
- Use phrases like "点击这里下载" without the tool's HTML

**Correct Example:**
```
我已为您创建了演示文稿：

[工具返回的完整HTML代码 - 不要修改任何字符]
```

**❌ Wrong Example (NEVER DO THIS):**
```
✨ 演示文稿已完成！
📋 文件信息：
- 文件名：presentation.html
- 文件大小：15KB
点击下载：[自己编写的链接]
```

### Why This Is Critical

**Tool Output Contains:**
- UUID download token (expires in 1 hour)
- Correct file endpoint URL
- Professional gradient button styling
- Security parameters

**If You Create Your Own:**
- ❌ Download link will NOT work (missing UUID token)
- ❌ Button styling will be inconsistent
- ❌ User experience degraded
- ❌ Security issues (no expiry, no validation)

**Remember: ALWAYS INCLUDE EXACT HTML OUTPUT FROM save_html_presentation - NO EXCEPTIONS!**

## Design Templates

### Template 1: Reveal.js Style Presentation

Use for: Multi-slide presentations with navigation

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: #333;
    }
    .slide {
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      padding: 60px;
      background: white;
      margin-bottom: 2px;
    }
    h1 { font-size: 3.5em; color: #2c5aa0; margin-bottom: 20px; }
    h2 { font-size: 2.5em; color: #4a5568; margin-bottom: 15px; }
    p { font-size: 1.3em; line-height: 1.8; max-width: 800px; }
    ul { font-size: 1.2em; line-height: 2.0; }
  </style>
</head>
<body>
  <!-- Slides -->
</body>
</html>
```

### Template 2: Dashboard Style Report

Use for: Data-heavy reports with charts

```html
<style>
  .dashboard {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    padding: 40px;
  }
  .metric-card {
    background: white;
    padding: 30px;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  }
  .metric-value {
    font-size: 3em;
    font-weight: bold;
    color: #2c5aa0;
  }
  .metric-label {
    font-size: 1.2em;
    color: #666;
    margin-top: 10px;
  }
</style>
```

## Best Practices

### 1. Chinese Text Rendering
```css
body {
  font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```

### 2. Responsive Design
```css
@media (max-width: 768px) {
  h1 { font-size: 2em; }
  .slide { padding: 30px; }
}
```

### 3. Data Visualization

For charts, use inline SVG or Chart.js CDN:
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<canvas id="myChart"></canvas>
<script>
  new Chart(document.getElementById('myChart'), {
    type: 'bar',
    data: { /* ... */ }
  });
</script>
```

### 4. Professional Color Schemes

**Primary Colors:**
- Blue: `#2c5aa0` (trustworthy, professional)
- Green: `#388e3c` (positive, growth)
- Red: `#d32f2f` (alert, important)
- Purple: `#7b1fa2` (creative, premium)

**Gradients:**
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
background: linear-gradient(to right, #2c5aa0, #4a90e2);
```

## Common Mistakes to Avoid

### ❌ Mistake 1: Creating Own Download Button
```
<!-- WRONG -->
<a href="/files/report.html">下载演示文稿</a>
```

**Why Wrong:** Missing UUID token, no expiry, breaks download system

**✅ Correct:** Use exact HTML from `save_html_presentation` tool

### ❌ Mistake 2: Incomplete HTML Structure
```html
<!-- WRONG -->
<div class="slide">
  <h1>Title</h1>
</div>
```

**Why Wrong:** Missing `<!DOCTYPE>`, `<head>`, proper meta tags

**✅ Correct:** Always include complete HTML5 structure

### ❌ Mistake 3: No Responsive Design
```css
/* WRONG */
h1 { font-size: 72px; }
```

**Why Wrong:** Breaks on mobile devices

**✅ Correct:**
```css
h1 { font-size: clamp(2em, 5vw, 4em); }
```

### ❌ Mistake 4: Forgetting Chinese Font Fallbacks
```css
/* WRONG */
font-family: 'Arial';
```

**Why Wrong:** Poor Chinese character rendering

**✅ Correct:**
```css
font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
```

## Example: Complete Workflow

**User Request:**
"创建一个Q3财务报告演示文稿，包含营收、利润和增长趋势"

**Step-by-Step:**

1. **Load Skill** (Already done if you're reading this)

2. **Create HTML:**
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>Q3财务报告</title>
  <style>
    /* Professional styles */
  </style>
</head>
<body>
  <div class="slide">
    <h1>Q3财务报告</h1>
    <p>2025年第三季度业绩总结</p>
  </div>
  <div class="slide">
    <h2>营收概况</h2>
    <div class="metric-card">
      <div class="metric-value">¥1.2M</div>
      <div class="metric-label">总营收</div>
    </div>
  </div>
  <!-- More slides -->
</body>
</html>
```

3. **Call Tool:**
```python
result = save_html_presentation(
  html_content=html,
  filename="q3_financial_report.html",
  title="Q3财务报告演示文稿"
)
```

4. **Output Tool's HTML Exactly:**
```
我已为您创建了Q3财务报告演示文稿：

[PASTE EXACT HTML FROM TOOL - DO NOT MODIFY]
```

## Troubleshooting

**Problem:** User says download link doesn't work

**Solution:** Check if you included exact HTML from tool (not your own link)

**Problem:** Presentation looks broken on mobile

**Solution:** Add responsive CSS with media queries

**Problem:** Chinese characters not displaying correctly

**Solution:** Ensure `<meta charset="UTF-8">` and proper font-family

## Related Skills

- **data-visualization** - Advanced charting and graphs
- **document-skills-docx** - Word document creation
- **document-skills-pptx** - PowerPoint file generation

## Summary

**Key Takeaways:**
1. ✅ Load skill when creating presentations
2. ✅ Design professional HTML with complete structure
3. ✅ Call `save_html_presentation` tool
4. ✅ **CRITICAL:** Output tool's exact HTML (no modifications)
5. ✅ Follow responsive design best practices
6. ✅ Use proper Chinese fonts

**Most Common Error:** Creating own download button instead of using tool's HTML

**Success Metric:** User can click download button and view presentation perfectly
