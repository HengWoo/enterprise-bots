## Phase 1: Critical Gaps (Weeks 1-2)

### Overview
**Goal:** Implement verification system, code generation, and programmatic testing
**Duration:** 10-13 days
**Effort:** 24-34 hours (pilot + full migration)
**Target Version:** v0.5.0

### Component 1.1: Verification System

**Problem Statement:**
Agents may return incorrect calculations, malformed outputs, or invalid data without detection. No systematic validation of results before returning to users.

**Solution:**
Three-layer verification architecture following Anthropic recommendations:

#### Layer 1: Rules-Based Validation
**Implementation:** `src/verification/validators.py`

```python
# Input validation
@validate_inputs(required=["revenue", "cost"], types={"revenue": float, "cost": float})
async def calculate_profit_tool(args):
    # Tool implementation

# Business logic validation
def verify_profit_margin(margin: float) -> dict:
    """Verify profit margin is in valid range."""
    if not 0 <= margin <= 1:
        return {"valid": False, "error": "Margin must be 0-100%"}
    if margin < 0.05:
        return {"valid": True, "warning": "Low margin (<5%)"}
    return {"valid": True}
```

**Validation Rules:**
- **Financial:** Balance sheet equations, percentage ranges, positive numbers
- **Data Quality:** Missing fields, duplicate keys, orphaned records
- **Format:** HTML structure, JSON schema, date formats
- **Business Logic:** Date ranges, quantity limits, status transitions

#### Layer 2: Visual Feedback
**Implementation:** `src/verification/visual_verifiers.py`

```python
async def verify_html_presentation(html_content: str) -> dict:
    """Verify HTML presentation quality."""
    # Check structure (head, body, proper nesting)
    # Validate CSS (inline styles, responsive)
    # Check content (headings, paragraphs, charts exist)
    # Optionally: Generate screenshot for manual review
    return {"passed": True, "issues": []}
```

**Visual Checks:**
- HTML presentations: Structure, styling, content hierarchy
- Generated documents: Format, layout, readability
- Charts/graphs: Data accuracy, labeling, legends

#### Layer 3: LLM-as-Judge (Phase 2)
**Implementation:** `src/verification/llm_judge.py`

```python
async def judge_analytical_quality(analysis: str, context: dict) -> dict:
    """Use secondary model to evaluate analysis quality."""
    # Call Haiku model with specific criteria
    # Check for: Completeness, logical consistency, actionable recommendations
    # Return quality score and improvement suggestions
```

**Use Cases:**
- Operations Assistant STAR analyses
- Financial Analyst insights
- Menu Engineer recommendations

**Files Created:**
```
src/verification/
├── __init__.py                 # Module exports
├── validators.py               # Input validation (Layer 1)
├── calculators.py              # Safe math operations (Layer 1)
├── verifiers.py                # Result verification (Layer 1)
├── formatters.py               # Output formatting with validation
├── visual_verifiers.py         # Visual feedback (Layer 2)
└── llm_judge.py                # LLM-as-judge (Layer 3, Phase 2)
```

**Testing:**
```
tests/verification/
├── test_validators.py          # 15+ test cases
├── test_calculators.py         # 20+ test cases
├── test_verifiers.py           # 10+ test cases
└── test_visual_verifiers.py    # 5+ test cases
```

**Success Metrics:**
- ✅ Catches ≥3 production errors per week
- ✅ Zero false positives in 1 week of testing
- ✅ <50ms verification overhead per request
- ✅ 100% test coverage for verification module

---

### Component 1.2: Code Generation System

**Problem Statement:**
No systematic code generation for complex operations. Agents rely on natural language instructions which can be imprecise. Missing linting feedback loops for quality assurance.

**Solution:**
Template-based code generation with automated linting and safe execution.

#### Code Generation Architecture

**Templates:** `src/codegen/templates.py`

```python
class CodeTemplate:
    PYTHON_DATA_ANALYSIS = '''
"""
Generated data analysis script.
Purpose: {purpose}
Generated: {timestamp}
"""

import pandas as pd
from typing import Dict, List

def analyze_data(data: List[Dict]) -> Dict:
    """Analyze the provided dataset."""
    df = pd.DataFrame(data)

    {analysis_code}

    return {{
        "count": len(df),
        "summary": df.describe().to_dict(),
        "insights": insights
    }}

if __name__ == "__main__":
    # Test with sample data
    sample = {sample_data}
    result = analyze_data(sample)
    print(result)
'''

    SQL_QUERY = '''
-- Generated SQL query
-- Purpose: {purpose}
-- Generated: {timestamp}

{query_code}

-- Safety checks:
-- - Read-only (SELECT only)
-- - LIMIT clause present
-- - No DELETE/UPDATE/DROP
'''
```

**Generator:** `src/codegen/generators.py`

```python
class CodeGenerator:
    def generate_python_script(
        self,
        purpose: str,
        analysis_type: str,
        data_schema: Dict
    ) -> Dict[str, str]:
        """Generate Python analysis script."""
        template = CodeTemplate.PYTHON_DATA_ANALYSIS
        code = template.format(
            purpose=purpose,
            timestamp=datetime.now(),
            analysis_code=self._get_analysis_logic(analysis_type),
            sample_data=self._generate_sample_data(data_schema)
        )

        # Validate generated code
        validation = self.validate_code(code, "python")
        if not validation["valid"]:
            # Attempt auto-fix
            code = self._fix_linting_errors(code, validation["errors"])

        return {
            "code": code,
            "language": "python",
            "validated": True,
            "path": f"/tmp/generated/{uuid4().hex}.py"
        }
```

**Linting Integration:** `src/codegen/validators.py`

```python
def lint_python_code(code: str) -> Dict:
    """Lint Python code with ruff + mypy."""
    # Write to temp file
    temp_file = Path(f"/tmp/lint_{uuid4().hex}.py")
    temp_file.write_text(code)

    # Run ruff
    ruff_result = subprocess.run(
        ["ruff", "check", "--output-format=json", str(temp_file)],
        capture_output=True,
        text=True
    )

    # Run mypy
    mypy_result = subprocess.run(
        ["mypy", "--output=json", str(temp_file)],
        capture_output=True,
        text=True
    )

    # Parse results
    errors = parse_linting_output(ruff_result, mypy_result)

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": extract_warnings(ruff_result)
    }
```

**Safe Execution:** `src/codegen/executor.py`

```python
async def execute_generated_code(
    code: str,
    language: str,
    input_data: Any,
    timeout: int = 30
) -> Dict:
    """Execute generated code in Docker sandbox."""
    # Save code to /tmp/generated/
    code_file = save_code(code, language)

    # Execute via Bash tool (Docker sandbox)
    if language == "python":
        cmd = f"python {code_file}"
    elif language == "sql":
        cmd = f"sqlite3 :memory: < {code_file}"

    # Run with timeout
    result = await bash_tool({
        "command": cmd,
        "timeout": timeout,
        "cwd": "/tmp/generated"
    })

    return {
        "output": result["stdout"],
        "errors": result["stderr"],
        "exit_code": result["exit_code"]
    }
```

**New Skill:** `prompts/skills/code-generation/SKILL.md`

```markdown
---
name: code-generation
description: "Generate and execute code safely for data analysis and transformations"
version: 1.0.0
author: Campfire AI Team
---

# Code Generation Workflows

## When to Generate Code

Generate code instead of using tools when:
- ✅ Complex data transformations (>3 steps)
- ✅ Precise calculations requiring type safety
- ✅ Reusable logic needed across requests
- ✅ Performance-critical operations

Do NOT generate code when:
- ❌ Simple operations (use existing tools)
- ❌ One-time calculations
- ❌ Unsafe operations (file system modifications)

## Workflow: Generate Python Data Analysis

1. **Identify Requirements**
   - What analysis is needed?
   - What data schema?
   - What outputs expected?

2. **Generate Code**
   - Call code generator with purpose and schema
   - Review generated template

3. **Validate Code**
   - Run ruff linting (catch syntax errors)
   - Run mypy type checking (catch type errors)
   - Review validation results

4. **Execute Safely**
   - Run in Docker sandbox via Bash tool
   - Monitor execution with timeout
   - Capture output and errors

5. **Return Results**
   - Present analysis results to user
   - Offer generated code file for download
   - Save to /tmp/generated/ for review

## Example: Data Analysis

```python
# User request: "Analyze sales data and find trends"

# 1. Generate code
code = await code_generator.generate_python_script(
    purpose="Analyze sales trends",
    analysis_type="trend_analysis",
    data_schema={"date": "datetime", "revenue": "float", "orders": "int"}
)

# 2. Lint code
validation = lint_python_code(code["code"])
if not validation["valid"]:
    # Show errors to user
    # Attempt auto-fix

# 3. Execute
result = await execute_generated_code(
    code=code["code"],
    language="python",
    input_data=sales_data
)

# 4. Return results
return {
    "analysis": result["output"],
    "code_file": code["path"]
}
```

## Safety Rules

1. **ALWAYS lint before execution**
2. **NEVER execute user-provided code directly**
3. **Use templates for known-good patterns**
4. **Sandbox all execution via Bash tool**
5. **Set execution timeouts (default: 30s)**
6. **Store generated code for audit trail**

## Supported Languages

- ✅ Python (pandas, numpy for data analysis)
- ✅ SQL (read-only queries)
- ⏳ JavaScript (planned for v0.5.1)
- ⏳ R (planned for advanced analytics)
```

**Files Created:**
```
src/codegen/
├── __init__.py
├── templates.py                # Code templates
├── generators.py               # Code generation logic
├── validators.py               # Linting integration
└── executor.py                 # Safe execution

prompts/skills/code-generation/
├── SKILL.md                    # Workflows
└── templates/
    ├── python_data_analysis.py.jinja
    ├── python_file_processing.py.jinja
    └── sql_query.sql.jinja
```

**Success Metrics:**
- ✅ Used successfully in ≥5 user requests per week
- ✅ Generated code passes linting 95%+ of time
- ✅ Zero code execution errors in production
- ✅ <200ms code generation time
- ✅ 80%+ test coverage for codegen module

---

### Component 1.3: Programmatic Testing Infrastructure

**Problem Statement:**
No automated testing of agent behaviors. Manual testing only. No regression detection. CI/CD only checks Docker build + health endpoint.

**Solution:**
Comprehensive pytest suite testing agent behaviors, workflows, and tool interactions.

#### Agent Behavior Tests

**Test Structure:** `tests/agent_behaviors/test_personal_assistant.py`

```python
import pytest
from src.campfire_agent import CampfireAgent
from tests.utils.agent_test_helper import AgentTestHelper

class TestPersonalAssistantBehaviors:
    """Test personal_assistant bot behaviors and workflows."""

    @pytest.fixture
    async def agent(self):
        """Create test agent instance."""
        return await AgentTestHelper.create_test_agent("personal_assistant")

    # Task Management Workflows

    @pytest.mark.asyncio
    async def test_create_task_workflow(self, agent):
        """Test creating a task with reminder."""
        response = await agent.process(
            user_message="Remind me to review reports tomorrow at 2pm",
            room_id=999,
            user_id=1
        )

        # Verify task created
        assert "task created" in response.lower() or "reminder set" in response.lower()
        # Verify confirmation
        assert "tomorrow" in response.lower() or "2pm" in response.lower()

    @pytest.mark.asyncio
    async def test_list_tasks_workflow(self, agent):
        """Test listing user's tasks."""
        # Create tasks first
        await agent.process("Add task: Finish Q3 report", room_id=999, user_id=1)
        await agent.process("Add task: Review budget", room_id=999, user_id=1)

        # List tasks
        response = await agent.process("What are my tasks?", room_id=999, user_id=1)

        # Verify both tasks appear
        assert "finish q3 report" in response.lower()
        assert "review budget" in response.lower()

    # Document Processing Workflows

    @pytest.mark.asyncio
    async def test_pdf_processing(self, agent):
        """Test PDF file analysis."""
        response = await agent.process(
            user_message="Summarize this PDF: tests/fixtures/sample_report.pdf",
            room_id=999,
            user_id=1
        )

        # Verify PDF content extracted
        assert len(response) > 100  # Meaningful summary
        # Verify no errors
        assert "⚠️" not in response
        assert "error" not in response.lower()

    @pytest.mark.asyncio
    async def test_html_presentation_generation(self, agent):
        """Test HTML presentation creation."""
        response = await agent.process(
            user_message="Create a presentation about Q3 revenue trends",
            room_id=999,
            user_id=1
        )

        # Verify download link generated
        assert "download" in response.lower() or "presentation" in response.lower()
        # Verify file registry token present
        assert "http://" in response or "https://" in response

    # Code Generation Workflows

    @pytest.mark.asyncio
    async def test_code_generation_workflow(self, agent):
        """Test code generation for data analysis."""
        response = await agent.process(
            user_message="Generate Python code to analyze this CSV and find trends",
            room_id=999,
            user_id=1
        )

        # Verify code generated
        assert "def " in response or "import" in response
        # Verify linting passed
        assert "ruff" in response.lower() or "validated" in response.lower()

    # Verification Workflows

    @pytest.mark.asyncio
    async def test_input_validation_catches_errors(self, agent):
        """Test that verification catches invalid inputs."""
        response = await agent.process(
            user_message="Set reminder for yesterday",  # Invalid: past date
            room_id=999,
            user_id=1
        )

        # Verify error caught
        assert "⚠️" in response or "error" in response.lower() or "cannot" in response.lower()

    # Performance Benchmarks

    @pytest.mark.asyncio
    async def test_response_time_simple_query(self, agent):
        """Test response time for simple queries."""
        import time

        start = time.time()
        response = await agent.process(
            user_message="Hello, how are you?",
            room_id=999,
            user_id=1
        )
        elapsed = time.time() - start

        # Verify acceptable response time
        assert elapsed < 10, f"Response took {elapsed}s (target: <10s)"

    @pytest.mark.asyncio
    async def test_response_time_complex_workflow(self, agent):
        """Test response time for complex workflows."""
        import time

        start = time.time()
        response = await agent.process(
            user_message="Analyze this Excel file and create a presentation",
            room_id=999,
            user_id=1
        )
        elapsed = time.time() - start

        # Verify acceptable response time
        assert elapsed < 30, f"Response took {elapsed}s (target: <30s)"
```

**Test Fixtures:** `tests/agent_behaviors/fixtures/`

```
fixtures/
├── sample_requests.json        # 50+ representative queries
├── expected_behaviors.json     # Expected response patterns
├── sample_report.pdf           # Test PDF document
├── sample_data.xlsx            # Test Excel file
├── sample_image.png            # Test image file
└── test_database.db            # Pre-populated test DB
```

**Test Utilities:** `tests/utils/agent_test_helper.py`

```python
class AgentTestHelper:
    """Helper utilities for testing agent behaviors."""

    @staticmethod
    async def create_test_agent(bot_id: str) -> CampfireAgent:
        """Create agent instance configured for testing."""
        # Load bot config
        bot_manager = BotManager(bots_dirs=["./bots", "prompts/configs"])
        bot_config = bot_manager.get_bot(bot_id)

        # Create test tools instance
        tools = CampfireTools(
            db_path="tests/fixtures/test.db",
            context_dir="/tmp/test_contexts"
        )

        # Create agent
        agent = CampfireAgent(
            bot_config=bot_config,
            campfire_tools=tools,
            bot_manager=bot_manager
        )

        return agent

    @staticmethod
    def assert_contains_metrics(response: str, metrics: List[str]):
        """Assert response contains expected metrics."""
        response_lower = response.lower()
        for metric in metrics:
            assert metric.lower() in response_lower, f"Missing metric: {metric}"

    @staticmethod
    def assert_no_errors(response: str):
        """Assert response contains no error indicators."""
        assert "⚠️" not in response
        assert "error" not in response.lower()
        assert "failed" not in response.lower()
```

**CI/CD Integration:** `.github/workflows/build-and-test.yml`

```yaml
name: Build and Test

on:
  push:
    branches: [main, develop, feature/*]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Build Docker image
        run: docker build -t campfire-ai-bot:test .

      - name: Run linting
        run: |
          docker run --rm campfire-ai-bot:test \
            bash -c "ruff check src/ && mypy src/"

      - name: Run tests
        run: |
          docker run --rm \
            -v $(pwd)/tests:/app/tests \
            campfire-ai-bot:test \
            pytest tests/ -v --cov=src --cov-report=term --cov-report=html

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./htmlcov/coverage.xml

      - name: Run health check
        run: |
          docker run -d -p 8000:8000 campfire-ai-bot:test
          sleep 10
          curl -f http://localhost:8000/health || exit 1
```

**Files Created:**
```
tests/agent_behaviors/
├── __init__.py
├── test_personal_assistant.py      # 20+ test scenarios
├── test_financial_analyst.py       # Phase 1.2 (after pilot)
├── test_operations_assistant.py    # Phase 1.2 (after pilot)
└── fixtures/
    ├── sample_requests.json
    ├── expected_behaviors.json
    └── test_files/

tests/utils/
├── __init__.py
├── agent_test_helper.py
└── verification_helper.py
```

**Success Metrics:**
- ✅ 20+ test scenarios for personal_assistant
- ✅ All tests passing in CI/CD
- ✅ 80%+ code coverage for agent logic
- ✅ CI/CD pipeline completes in <5 minutes
- ✅ Test suite detects ≥1 regression per month

---

### Phase 1 Timeline & Milestones

#### Week 1: Pilot Implementation (personal_assistant)

**Day 1-2: Verification System (8 hours)**
- Create src/verification/ module
- Implement validators, calculators, verifiers
- Write 45+ test cases
- Achieve 100% test coverage

**Day 3-4: Code Generation (8 hours)**
- Create src/codegen/ module
- Implement templates, generators, linting
- Create code-generation SKILL
- Test safe execution

**Day 5-7: Testing Infrastructure (8 hours)**
- Create agent behavior tests (20+ scenarios)
- Integrate with CI/CD pipeline
- Run full test suite
- Document results

**Milestone:** Pilot implementation complete, ready for validation

#### Week 2: Validation & Migration Planning

**Day 8-11: Pilot Validation (4 days)**
- Deploy to test environment
- Monitor for 1 week
- Validate against 5 gates
- Document lessons learned

**Day 12-14: Migration Preparation (3 days)**
- Review validation results
- Create migration checklists
- Prepare documentation
- Plan rollout schedule

**Milestone:** Validation gates passed, ready for full migration

#### Weeks 3-4: Full Migration (7 Bots)

**Week 3: Critical Bots (3 bots, 22 hours)**
- financial_analyst (3-4 hours)
- operations_assistant (3-4 hours)
- technical_assistant (2-3 hours)

**Week 4: Remaining Bots (4 bots, 14 hours)**
- menu_engineer (2-3 hours)
- briefing_assistant (2 hours)
- cc_tutor (2 hours)
- default (1-2 hours)

**Milestone:** Phase 1 complete, all 8 bots upgraded

---

### Phase 1 Deliverables

**Code Modules (9 new modules):**
1. `src/verification/` - Validation and verification
2. `src/codegen/` - Code generation and linting
3. `tests/verification/` - Verification tests
4. `tests/agent_behaviors/` - Behavior tests
5. `tests/utils/` - Test utilities
6. `prompts/skills/code-generation/` - Code generation workflows
7. Updated CI/CD workflows
8. Updated bot configurations
9. Documentation (guides, roadmaps, checklists)

**Documentation (7 new docs):**
1. This roadmap (ANTHROPIC_BEST_PRACTICES_ROADMAP.md)
2. Verification guide
3. Code generation guide
4. Testing guide
5. Migration checklist
6. Validation gates document
7. Rollback procedures

**Test Coverage:**
- Verification module: 100%
- Codegen module: 80%+
- Agent behaviors: 20+ scenarios per bot
- Overall: 80%+ coverage target

---

