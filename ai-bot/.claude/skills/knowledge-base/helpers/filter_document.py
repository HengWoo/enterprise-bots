"""
Knowledge Base Document Filtering Helpers

These functions enable efficient knowledge base processing by filtering
documents in the execution environment BEFORE passing content to the model.

Based on Anthropic's "Code Execution with MCP" best practices:
- Process large documents locally (not in model context)
- Extract only relevant sections
- Achieve 85-95% token savings

Usage:
    from helpers.filter_document import search_and_extract, extract_section

    # High-level search (recommended)
    results = search_and_extract(query="MCP integration", category="claude-code")

    # Low-level extraction
    section = extract_section(path="claude-code/llm.txt", keywords=["MCP", "integration"])
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Any


def extract_section(
    document_path: str,
    keywords: List[str],
    context_lines: int = 10,
    max_sections: int = 5
) -> str:
    """
    Extract only relevant sections from large knowledge base documents.

    This function runs in the execution environment - the full document
    never enters the model context! Only matching sections are returned.

    Args:
        document_path: Path to document (relative to KB root or absolute)
        keywords: List of keywords to search for
        context_lines: Lines of context before/after each match (default: 10)
        max_sections: Maximum number of sections to return (default: 5)

    Returns:
        Concatenated relevant sections separated by "---"

    Example:
        # Extract MCP-related sections from 4.7K line document
        section = extract_section(
            document_path="claude-code/llm.txt",
            keywords=["MCP", "Model Context Protocol"],
            context_lines=10
        )
        # Returns ~200 lines instead of 4700 (95% token savings!)
    """
    # Resolve path
    if os.path.isabs(document_path):
        doc_path = Path(document_path)
    else:
        # Try relative to knowledge base root
        kb_root = Path(__file__).parent.parent.parent.parent.parent / "knowledge-base"
        doc_path = kb_root / document_path

        # If not found, try relative to current directory
        if not doc_path.exists():
            doc_path = Path(document_path)

    if not doc_path.exists():
        return f"Error: Document not found at {document_path}"

    try:
        with open(doc_path, 'r', encoding='utf-8') as f:
            full_content = f.read()
    except Exception as e:
        return f"Error reading document: {str(e)}"

    lines = full_content.split('\n')
    relevant_sections = []
    matched_line_numbers = set()

    # Find all matching lines
    for i, line in enumerate(lines):
        # Case-insensitive keyword matching
        if any(keyword.lower() in line.lower() for keyword in keywords):
            matched_line_numbers.add(i)

    if not matched_line_numbers:
        return f"No matches found for keywords: {', '.join(keywords)}"

    # Extract sections with context
    sections_extracted = []
    for line_num in sorted(matched_line_numbers)[:max_sections * 2]:  # Buffer for merging
        start = max(0, line_num - context_lines)
        end = min(len(lines), line_num + context_lines + 1)

        # Check if this section overlaps with previous
        if sections_extracted:
            last_section = sections_extracted[-1]
            if start <= last_section['end']:
                # Merge with previous section
                last_section['end'] = max(last_section['end'], end)
                continue

        sections_extracted.append({
            'start': start,
            'end': end,
            'match_line': line_num
        })

        if len(sections_extracted) >= max_sections:
            break

    # Build result
    result_parts = []
    for i, section in enumerate(sections_extracted):
        section_lines = lines[section['start']:section['end']]
        section_text = '\n'.join(section_lines)

        # Add section header
        header = f"[Section {i+1} - Match at line {section['match_line']+1}]"
        result_parts.append(f"{header}\n{section_text}")

    # Add metadata footer
    footer = f"\n\n[Extracted {len(sections_extracted)} sections from {len(lines)} total lines]"
    footer += f"\n[Keywords: {', '.join(keywords)}]"
    footer += f"\n[Source: {document_path}]"

    return '\n\n---\n\n'.join(result_parts) + footer


def extract_by_headings(
    document_path: str,
    heading_keywords: List[str],
    include_subheadings: bool = True
) -> str:
    """
    Extract sections by markdown heading keywords.

    More structured than keyword search - extracts complete sections
    delimited by markdown headings (# ## ###).

    Args:
        document_path: Path to markdown document
        heading_keywords: Keywords to search in headings
        include_subheadings: Include subsections (default: True)

    Returns:
        Concatenated matching sections

    Example:
        # Extract all MCP-related sections from documentation
        sections = extract_by_headings(
            document_path="claude-code/llm.txt",
            heading_keywords=["MCP", "Integration"],
            include_subheadings=True
        )
    """
    # Resolve path (same logic as extract_section)
    if os.path.isabs(document_path):
        doc_path = Path(document_path)
    else:
        kb_root = Path(__file__).parent.parent.parent.parent.parent / "knowledge-base"
        doc_path = kb_root / document_path
        if not doc_path.exists():
            doc_path = Path(document_path)

    if not doc_path.exists():
        return f"Error: Document not found at {document_path}"

    try:
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return f"Error reading document: {str(e)}"

    lines = content.split('\n')
    sections = []
    current_section = None
    current_heading_level = 0

    for i, line in enumerate(lines):
        # Check if line is a heading
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)

        if heading_match:
            heading_level = len(heading_match.group(1))
            heading_text = heading_match.group(2)

            # Check if heading matches keywords
            matches = any(keyword.lower() in heading_text.lower() for keyword in heading_keywords)

            if matches:
                # Start new section
                if current_section:
                    sections.append(current_section)
                current_section = {
                    'heading': line,
                    'level': heading_level,
                    'lines': [line],
                    'start_line': i
                }
                current_heading_level = heading_level
            elif current_section:
                # Check if we should continue current section
                if include_subheadings and heading_level > current_heading_level:
                    # Subheading - include
                    current_section['lines'].append(line)
                elif heading_level <= current_heading_level:
                    # Same or higher level - end current section
                    sections.append(current_section)
                    current_section = None
                    current_heading_level = 0
                else:
                    current_section['lines'].append(line)
        elif current_section:
            # Regular line - add to current section if active
            current_section['lines'].append(line)

    # Add last section
    if current_section:
        sections.append(current_section)

    if not sections:
        return f"No sections found matching headings: {', '.join(heading_keywords)}"

    # Build result
    result_parts = []
    for i, section in enumerate(sections):
        section_text = '\n'.join(section['lines'])
        header = f"[Section {i+1}: {section['heading']} - Line {section['start_line']+1}]"
        result_parts.append(f"{header}\n{section_text}")

    footer = f"\n\n[Extracted {len(sections)} sections]"
    footer += f"\n[Heading keywords: {', '.join(heading_keywords)}]"
    footer += f"\n[Source: {document_path}]"

    return '\n\n---\n\n'.join(result_parts) + footer


def search_and_extract(
    query: str,
    category: Optional[str] = None,
    context_lines: int = 10,
    max_results: int = 3
) -> List[Dict[str, Any]]:
    """
    High-level search that processes results in execution environment.

    This is the recommended entry point for knowledge base queries.
    Combines MCP search with local filtering for maximum efficiency.

    Workflow:
        1. Use MCP to search knowledge base (returns metadata only)
        2. For each result, extract relevant sections locally
        3. Return filtered extracts (not full documents!)

    Args:
        query: Search query string
        category: Optional category filter
        context_lines: Context lines around matches (default: 10)
        max_results: Maximum results to process (default: 3)

    Returns:
        List of dicts with keys: path, title, relevant_excerpt, metadata

    Example:
        results = search_and_extract(
            query="MCP configuration settings",
            category="claude-code"
        )

        for result in results:
            print(f"Source: {result['path']}")
            print(result['relevant_excerpt'])  # Only ~200 lines, not 4700!
    """
    # Import here to avoid circular dependency
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../..'))

    try:
        from src.tools.campfire_tools import CampfireTools

        # Get knowledge base path from environment or use default
        kb_path = os.getenv('KNOWLEDGE_BASE_PATH', './ai-knowledge/company_kb')
        tools = CampfireTools(
            db_path="dummy",  # Not needed for KB operations
            knowledge_base_dir=kb_path
        )

        # Step 1: Search (returns metadata only)
        search_results = tools.search_knowledge_base(
            query=query,
            category=category,
            max_results=max_results
        )

        if not search_results:
            return [{
                "success": False,
                "message": f"No results found for query: {query}",
                "query": query,
                "category": category
            }]

        # Step 2: Extract relevant sections from each result
        extracts = []
        keywords = query.split()  # Simple tokenization

        for result in search_results[:max_results]:
            # Extract only relevant sections (not full document!)
            relevant_excerpt = extract_section(
                document_path=result['path'],
                keywords=keywords,
                context_lines=context_lines,
                max_sections=5
            )

            extracts.append({
                "path": result['path'],
                "title": result.get('title', 'Untitled'),
                "relevance_score": result.get('relevance_score', 0),
                "relevant_excerpt": relevant_excerpt,  # Filtered content!
                "metadata": {
                    "original_query": query,
                    "extraction_method": "keyword_matching",
                    "context_lines": context_lines
                }
            })

        return extracts

    except Exception as e:
        return [{
            "success": False,
            "error": str(e),
            "message": "Error during search and extraction"
        }]


def get_document_outline(document_path: str) -> str:
    """
    Generate document outline showing structure (headings only).

    Useful for understanding document organization before extracting sections.
    Returns only heading structure - minimal token cost.

    Args:
        document_path: Path to markdown document

    Returns:
        Formatted outline with heading hierarchy

    Example:
        outline = get_document_outline("claude-code/llm.txt")
        print(outline)
        # Output:
        # # Claude Code Documentation
        #   ## What is Claude Code?
        #   ## Installation
        #     ### NPM Installation
        #     ### Homebrew Installation
        #   ## Common Workflows
        #   ...
    """
    # Resolve path
    if os.path.isabs(document_path):
        doc_path = Path(document_path)
    else:
        kb_root = Path(__file__).parent.parent.parent.parent.parent / "knowledge-base"
        doc_path = kb_root / document_path
        if not doc_path.exists():
            doc_path = Path(document_path)

    if not doc_path.exists():
        return f"Error: Document not found at {document_path}"

    try:
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return f"Error reading document: {str(e)}"

    lines = content.split('\n')
    outline_lines = []

    for line in lines:
        # Match markdown headings
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if heading_match:
            level = len(heading_match.group(1))
            text = heading_match.group(2)
            indent = '  ' * (level - 1)
            outline_lines.append(f"{indent}{'#' * level} {text}")

    if not outline_lines:
        return f"No headings found in {document_path}"

    header = f"Document Outline: {document_path}\n"
    header += f"Total headings: {len(outline_lines)}\n"
    header += "=" * 60 + "\n\n"

    return header + '\n'.join(outline_lines)


# Example usage (for testing)
if __name__ == "__main__":
    print("Knowledge Base Filtering Helpers")
    print("=" * 60)
    print()
    print("Example 1: Extract sections by keywords")
    print("-" * 60)
    result = extract_section(
        document_path="claude-code/llm.txt",
        keywords=["MCP", "integration"],
        context_lines=5
    )
    print(result[:500] + "..." if len(result) > 500 else result)
    print()

    print("Example 2: Get document outline")
    print("-" * 60)
    outline = get_document_outline("claude-code/llm.txt")
    print(outline[:500] + "..." if len(outline) > 500 else outline)
    print()

    print("Example 3: Search and extract (high-level)")
    print("-" * 60)
    results = search_and_extract(query="MCP configuration", category="claude-code")
    for result in results:
        print(f"Path: {result.get('path', 'N/A')}")
        print(f"Excerpt length: {len(result.get('relevant_excerpt', ''))} chars")
        print()
