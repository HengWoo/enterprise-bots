"""
Custom Skills MCP Server for Progressive Disclosure

This MCP server enables on-demand loading of skill content, achieving progressive
disclosure within the Agent SDK architecture. Skills are loaded only when needed,
reducing token usage by ~63% compared to manual skill content in system prompts.

Tools provided:
- list_skills: List all available skills
- load_skill: Load a skill's SKILL.md content
- load_skill_file: Load additional skill files (e.g., docx-js.md, ooxml.md)
"""

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("skills-mcp")

# Create MCP server
server = Server("campfire-skills")

# Skills directory (configured via environment variable)
SKILLS_DIR = os.getenv("SKILLS_DIR", "/app/.claude/skills")

logger.info(f"Skills MCP Server starting with SKILLS_DIR={SKILLS_DIR}")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available skill-related tools"""
    return [
        types.Tool(
            name="list_skills",
            description="List all available skills and their descriptions. Use this to discover what skills are available.",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ),
        types.Tool(
            name="load_skill",
            description="Load a skill's expertise and workflows on-demand. ONLY call this when you need specific expertise (e.g., user asks about Word documents → load docx skill). Do NOT preload all skills.",
            inputSchema={
                "type": "object",
                "properties": {
                    "skill_name": {
                        "type": "string",
                        "description": "Name of skill to load. Options: 'docx' (Word documents), 'xlsx' (Excel spreadsheets), 'pptx' (PowerPoint presentations)"
                    }
                },
                "required": ["skill_name"]
            }
        ),
        types.Tool(
            name="load_skill_file",
            description="Load additional detailed files from a skill (third level of detail). Only use AFTER loading the main skill if you need more specific information from referenced documentation files.",
            inputSchema={
                "type": "object",
                "properties": {
                    "skill_name": {
                        "type": "string",
                        "description": "Skill name (e.g., 'docx', 'xlsx', 'pptx')"
                    },
                    "file_name": {
                        "type": "string",
                        "description": "File to load (e.g., 'docx-js.md', 'ooxml.md')"
                    }
                },
                "required": ["skill_name", "file_name"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Execute tool calls"""

    try:
        if name == "list_skills":
            return await list_available_skills()

        elif name == "load_skill":
            skill_name = arguments["skill_name"]
            return await load_skill_content(skill_name)

        elif name == "load_skill_file":
            skill_name = arguments["skill_name"]
            file_name = arguments["file_name"]
            return await load_additional_file(skill_name, file_name)

        else:
            logger.error(f"Unknown tool: {name}")
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}", exc_info=True)
        return [types.TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]


async def list_available_skills() -> list[types.TextContent]:
    """List all skills in .claude/skills/ directory"""

    logger.info(f"Listing skills from: {SKILLS_DIR}")

    if not os.path.exists(SKILLS_DIR):
        logger.error(f"Skills directory not found: {SKILLS_DIR}")
        return [types.TextContent(
            type="text",
            text=f"Error: Skills directory not found: {SKILLS_DIR}"
        )]

    skills = []

    try:
        for dir_name in os.listdir(SKILLS_DIR):
            skill_path = os.path.join(SKILLS_DIR, dir_name)
            skill_md = os.path.join(skill_path, "SKILL.md")

            if os.path.isdir(skill_path) and os.path.exists(skill_md):
                # Parse YAML frontmatter for metadata
                with open(skill_md, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract metadata from frontmatter
                name = dir_name
                description = "Document processing skill"

                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        frontmatter = parts[1]

                        # Simple parsing (extract name and description)
                        for line in frontmatter.split('\n'):
                            line = line.strip()
                            if line.startswith('name:'):
                                name = line.split(':', 1)[1].strip()
                            elif line.startswith('description:'):
                                description = line.split(':', 1)[1].strip()

                skills.append(f"- **{name}**: {description}")

        if not skills:
            result = "No skills found in .claude/skills/ directory"
            logger.warning(result)
        else:
            result = "Available Skills:\n\n" + "\n".join(skills)
            logger.info(f"Found {len(skills)} skills")

        return [types.TextContent(type="text", text=result)]

    except Exception as e:
        logger.error(f"Error listing skills: {e}", exc_info=True)
        return [types.TextContent(
            type="text",
            text=f"Error listing skills: {str(e)}"
        )]


async def load_skill_content(skill_name: str) -> list[types.TextContent]:
    """Load main SKILL.md content"""

    # Support both formats: "docx" and "document-skills-docx"
    original_skill_name = skill_name
    if not skill_name.startswith("document-skills-"):
        skill_name = f"document-skills-{skill_name}"

    logger.info(f"Loading skill: {original_skill_name} (full name: {skill_name})")

    skill_path = os.path.join(SKILLS_DIR, skill_name)
    skill_md = os.path.join(skill_path, "SKILL.md")

    if not os.path.exists(skill_md):
        logger.error(f"Skill not found: {skill_name} at {skill_md}")
        return [types.TextContent(
            type="text",
            text=f"Error: Skill '{original_skill_name}' not found in {SKILLS_DIR}\n\nAvailable skills: docx, xlsx, pptx"
        )]

    try:
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()

        # Return skill content with header and footer
        result = f"""# {original_skill_name.upper()} Skill Loaded

{content}

---
**Note:** This skill may reference additional files. Use `load_skill_file(skill_name="{original_skill_name}", file_name="...")` if you need more specific details from referenced documentation.
"""

        logger.info(f"Successfully loaded skill: {skill_name} ({len(content)} bytes)")

        return [types.TextContent(type="text", text=result)]

    except Exception as e:
        logger.error(f"Error loading skill {skill_name}: {e}", exc_info=True)
        return [types.TextContent(
            type="text",
            text=f"Error loading skill '{original_skill_name}': {str(e)}"
        )]


async def load_additional_file(skill_name: str, file_name: str) -> list[types.TextContent]:
    """Load additional skill files (docx-js.md, ooxml.md, etc.)"""

    # Support both formats
    original_skill_name = skill_name
    if not skill_name.startswith("document-skills-"):
        skill_name = f"document-skills-{skill_name}"

    logger.info(f"Loading skill file: {original_skill_name}/{file_name}")

    skill_path = os.path.join(SKILLS_DIR, skill_name)
    file_path = os.path.join(skill_path, file_name)

    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_name} in {skill_name} at {file_path}")
        return [types.TextContent(
            type="text",
            text=f"Error: File '{file_name}' not found in {original_skill_name} skill"
        )]

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        result = f"""# {file_name} (from {original_skill_name} skill)

{content}
"""

        logger.info(f"Successfully loaded file: {file_name} ({len(content)} bytes)")

        return [types.TextContent(type="text", text=result)]

    except Exception as e:
        logger.error(f"Error loading file {file_name}: {e}", exc_info=True)
        return [types.TextContent(
            type="text",
            text=f"Error loading file '{file_name}' from {original_skill_name}: {str(e)}"
        )]


async def main():
    """Run the MCP server"""
    logger.info("Starting Skills MCP server...")

    async with stdio_server() as (read_stream, write_stream):
        logger.info("Skills MCP server ready")
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
