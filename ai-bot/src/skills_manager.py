"""
SkillsManager - Skills discovery and loading for Campfire AI Bot

This module manages Skills (domain expertise) following Anthropic's Skills pattern:
- Skills = Progressive disclosure of specialized knowledge
- SKILL.md format with YAML frontmatter
- Skills loaded on-demand to reduce token usage
- Integration with existing Skills MCP server

Skills Architecture (from research):
- Level 1: Metadata (150 tokens) - skill_id, description, version
- Level 2: SKILL.md (full documentation) - workflows, examples, best practices
- Level 3: Resources (templates, examples) - supplementary materials

Directory structure:
    .claude/skills/          # Current Skills MCP location
    ├── document-skills-docx/
    │   └── SKILL.md
    └── campfire-financial-analysis/
        └── SKILL.md

    prompts/skills/          # New Skills location (gradual migration)
    ├── document-skills-docx/
    │   ├── SKILL.md
    │   └── resources/
    └── presentation-generation/
        ├── SKILL.md
        └── resources/

Usage:
    manager = SkillsManager(
        skills_dirs=[".claude/skills", "prompts/skills"]
    )

    # Discover available Skills
    skills = manager.discover_skills()

    # Load Skill content
    skill = manager.load_skill("document-skills-docx")

    # Get Skill metadata
    metadata = manager.get_skill_metadata("document-skills-docx")
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
import re

logger = logging.getLogger(__name__)


@dataclass
class SkillMetadata:
    """
    Skill metadata extracted from YAML frontmatter.

    Follows Anthropic Skills format:
    ---
    name: docx
    description: "Document creation and editing..."
    version: 1.0.0
    license: MIT
    ---
    """
    skill_id: str           # Directory name (e.g., "document-skills-docx")
    name: str               # Short name (e.g., "docx")
    description: str        # What the skill does
    version: Optional[str] = None
    license: Optional[str] = None
    path: Optional[Path] = None  # Full path to SKILL.md


@dataclass
class Skill:
    """
    Complete Skill with metadata and content.
    """
    metadata: SkillMetadata
    content: str            # Full SKILL.md content (without frontmatter)
    raw_content: str        # Raw SKILL.md (with frontmatter)


class SkillsManager:
    """
    Manages Skills discovery and loading across multiple directories.

    This bridges our existing Skills MCP (.claude/skills/) with
    the new file-based prompt system (prompts/skills/).
    """

    def __init__(self, skills_dirs: List[str] = None):
        """
        Initialize SkillsManager.

        Args:
            skills_dirs: List of directories to search for Skills
                        Default: [".claude/skills", "prompts/skills"]
        """
        if skills_dirs is None:
            skills_dirs = [".claude/skills", "prompts/skills"]

        self.skills_dirs = [Path(d) for d in skills_dirs]

        # Cache for discovered Skills
        self._skills_cache: Dict[str, Skill] = {}

        logger.info(f"[SkillsManager] Initialized with dirs: {skills_dirs}")

    def discover_skills(self) -> List[SkillMetadata]:
        """
        Discover all available Skills across all directories.

        Searches for directories containing SKILL.md files.

        Returns:
            List of SkillMetadata objects

        Example:
            skills = manager.discover_skills()
            for skill in skills:
                print(f"{skill.skill_id}: {skill.description}")
        """
        discovered_skills = []

        for skills_dir in self.skills_dirs:
            if not skills_dir.exists():
                logger.warning(f"[SkillsManager] ⚠️  Skills directory not found: {skills_dir}")
                continue

            # Find all SKILL.md files
            skill_files = list(skills_dir.glob("*/SKILL.md"))

            for skill_file in skill_files:
                skill_id = skill_file.parent.name
                metadata = self._parse_skill_metadata(skill_file, skill_id)

                if metadata:
                    discovered_skills.append(metadata)

        logger.info(f"[SkillsManager] 🔍 Discovered {len(discovered_skills)} Skills")
        return discovered_skills

    def load_skill(self, skill_id: str) -> Optional[Skill]:
        """
        Load full Skill content by skill_id.

        Searches all configured directories for the Skill.
        Results are cached for performance.

        Args:
            skill_id: Skill identifier (directory name)

        Returns:
            Skill object with metadata and content, or None if not found

        Example:
            skill = manager.load_skill("document-skills-docx")
            if skill:
                print(skill.content)  # Full SKILL.md content
        """
        # Check cache first
        if skill_id in self._skills_cache:
            logger.info(f"[SkillsManager] ✅ Loaded from cache: {skill_id}")
            return self._skills_cache[skill_id]

        # Search in all directories
        for skills_dir in self.skills_dirs:
            skill_file = skills_dir / skill_id / "SKILL.md"

            if skill_file.exists():
                skill = self._load_skill_from_file(skill_file, skill_id)

                if skill:
                    # Cache the result
                    self._skills_cache[skill_id] = skill
                    logger.info(f"[SkillsManager] ✅ Loaded Skill: {skill_id} from {skills_dir}")
                    return skill

        logger.warning(f"[SkillsManager] ⚠️  Skill not found: {skill_id}")
        return None

    def get_skill_metadata(self, skill_id: str) -> Optional[SkillMetadata]:
        """
        Get Skill metadata without loading full content.

        Faster than load_skill() for just checking Skill info.

        Args:
            skill_id: Skill identifier

        Returns:
            SkillMetadata object or None if not found
        """
        for skills_dir in self.skills_dirs:
            skill_file = skills_dir / skill_id / "SKILL.md"

            if skill_file.exists():
                return self._parse_skill_metadata(skill_file, skill_id)

        return None

    def list_skill_ids(self) -> List[str]:
        """
        List all available Skill IDs.

        Returns:
            List of skill_id strings

        Example:
            skill_ids = manager.list_skill_ids()
            # Returns: ["document-skills-docx", "presentation-generation", ...]
        """
        skills = self.discover_skills()
        return [s.skill_id for s in skills]

    def has_skill(self, skill_id: str) -> bool:
        """
        Check if a Skill exists.

        Args:
            skill_id: Skill identifier

        Returns:
            True if Skill exists in any configured directory
        """
        for skills_dir in self.skills_dirs:
            skill_file = skills_dir / skill_id / "SKILL.md"
            if skill_file.exists():
                return True

        return False

    def _parse_skill_metadata(self, skill_file: Path, skill_id: str) -> Optional[SkillMetadata]:
        """
        Parse YAML frontmatter from SKILL.md file.

        Expected format:
        ---
        name: docx
        description: "Document creation..."
        version: 1.0.0
        license: MIT
        ---

        Args:
            skill_file: Path to SKILL.md file
            skill_id: Skill identifier (directory name)

        Returns:
            SkillMetadata object or None if parsing fails
        """
        try:
            content = skill_file.read_text(encoding='utf-8')

            # Extract YAML frontmatter
            frontmatter = self._extract_frontmatter(content)

            if frontmatter:
                # Parse YAML manually (simple key: value pairs)
                metadata_dict = self._parse_simple_yaml(frontmatter)

                return SkillMetadata(
                    skill_id=skill_id,
                    name=metadata_dict.get('name', skill_id),
                    description=metadata_dict.get('description', ''),
                    version=metadata_dict.get('version'),
                    license=metadata_dict.get('license'),
                    path=skill_file
                )

        except Exception as e:
            logger.error(f"[SkillsManager] ❌ Error parsing metadata for {skill_id}: {e}")

        return None

    def _load_skill_from_file(self, skill_file: Path, skill_id: str) -> Optional[Skill]:
        """
        Load full Skill from SKILL.md file.

        Args:
            skill_file: Path to SKILL.md file
            skill_id: Skill identifier

        Returns:
            Skill object or None if loading fails
        """
        try:
            raw_content = skill_file.read_text(encoding='utf-8')

            # Parse metadata
            metadata = self._parse_skill_metadata(skill_file, skill_id)

            if not metadata:
                return None

            # Remove frontmatter from content
            content = self._remove_frontmatter(raw_content)

            return Skill(
                metadata=metadata,
                content=content,
                raw_content=raw_content
            )

        except Exception as e:
            logger.error(f"[SkillsManager] ❌ Error loading Skill {skill_id}: {e}")
            return None

    def _extract_frontmatter(self, content: str) -> Optional[str]:
        """
        Extract YAML frontmatter from markdown content.

        Looks for:
        ---
        key: value
        ---

        Args:
            content: Raw markdown content

        Returns:
            Frontmatter content (without ---) or None
        """
        # Match YAML frontmatter pattern
        pattern = r'^---\s*\n(.*?)\n---\s*\n'
        match = re.match(pattern, content, re.DOTALL)

        if match:
            return match.group(1)

        return None

    def _remove_frontmatter(self, content: str) -> str:
        """
        Remove YAML frontmatter from content.

        Args:
            content: Raw markdown content with frontmatter

        Returns:
            Content without frontmatter
        """
        pattern = r'^---\s*\n.*?\n---\s*\n'
        return re.sub(pattern, '', content, count=1, flags=re.DOTALL)

    def _parse_simple_yaml(self, yaml_str: str) -> Dict[str, str]:
        """
        Simple YAML parser for key: value pairs.

        Handles:
        - key: value
        - key: "quoted value"
        - key: 'single quoted'

        Does NOT handle:
        - Nested structures
        - Lists
        - Multi-line values

        Args:
            yaml_str: YAML content

        Returns:
            Dictionary of key-value pairs
        """
        result = {}

        for line in yaml_str.split('\n'):
            line = line.strip()

            if not line or line.startswith('#'):
                continue

            # Match key: value or key: "value"
            match = re.match(r'^(\w+):\s*(.+)$', line)

            if match:
                key = match.group(1)
                value = match.group(2).strip()

                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]

                result[key] = value

        return result


# Convenience function for quick Skill loading
def load_skill(skill_id: str, skills_dirs: List[str] = None) -> Optional[str]:
    """
    Convenience function to load Skill content in one line.

    Args:
        skill_id: Skill identifier
        skills_dirs: Optional list of Skills directories

    Returns:
        Skill content (without frontmatter) or None if not found

    Example:
        content = load_skill("document-skills-docx")
    """
    manager = SkillsManager(skills_dirs)
    skill = manager.load_skill(skill_id)

    if skill:
        return skill.content

    return None
