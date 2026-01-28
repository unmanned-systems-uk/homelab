#!/usr/bin/env python3
"""
Generate MCP tool documentation from homelab_server.py source code.

Usage:
    python3 scripts/generate-mcp-docs.py > ~/cc-share/tools/api-reference/MCP_TOOLS_AUTO.md

This script extracts all @mcp.tool() decorated functions and their docstrings
to generate up-to-date documentation automatically.
"""

import re
import ast
from pathlib import Path
from datetime import datetime

MCP_SERVER_PATH = Path(__file__).parent.parent / "mcp-servers/homelab-infra/homelab_server.py"


def extract_tools(source_code: str) -> list[dict]:
    """Extract tool definitions from source code."""
    tools = []

    # Parse the AST
    tree = ast.parse(source_code)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Check if function has @mcp.tool() decorator
            is_mcp_tool = False
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Call):
                    if isinstance(decorator.func, ast.Attribute):
                        if decorator.func.attr == "tool":
                            is_mcp_tool = True
                elif isinstance(decorator, ast.Attribute):
                    if decorator.attr == "tool":
                        is_mcp_tool = True

            if not is_mcp_tool:
                continue

            # Extract function info
            func_name = node.name
            docstring = ast.get_docstring(node) or "No description"

            # Extract parameters
            params = []
            defaults_offset = len(node.args.args) - len(node.args.defaults)

            for i, arg in enumerate(node.args.args):
                if arg.arg == "self":
                    continue

                param = {"name": arg.arg, "type": "any", "default": None}

                # Get type annotation
                if arg.annotation:
                    param["type"] = ast.unparse(arg.annotation)

                # Get default value
                default_idx = i - defaults_offset
                if default_idx >= 0 and default_idx < len(node.args.defaults):
                    default = node.args.defaults[default_idx]
                    try:
                        param["default"] = ast.literal_eval(ast.unparse(default))
                    except:
                        param["default"] = ast.unparse(default)

                params.append(param)

            # Get return type
            return_type = "dict"
            if node.returns:
                return_type = ast.unparse(node.returns)

            tools.append({
                "name": func_name,
                "docstring": docstring,
                "params": params,
                "return_type": return_type,
                "line": node.lineno
            })

    return tools


def categorize_tools(tools: list[dict]) -> dict[str, list[dict]]:
    """Categorize tools by prefix."""
    categories = {
        "Infrastructure": [],
        "SCPI Equipment": [],
        "Credentials & Summary": [],
        "CCPM Messaging": [],
        "CCPM Tasks": [],
        "CCPM Sprints": [],
        "Session Management": [],
        "Lessons Learned": [],
        "Piggyback Messaging": [],
        "Completion Signaling": []
    }

    for tool in tools:
        name = tool["name"]

        if name.startswith("homelab_list_scpi") or name.startswith("homelab_get_scpi"):
            categories["SCPI Equipment"].append(tool)
        elif name.startswith("homelab_get_credentials") or name.startswith("homelab_infrastructure"):
            categories["Credentials & Summary"].append(tool)
        elif name.startswith("homelab_"):
            categories["Infrastructure"].append(tool)
        elif name.startswith("ccpm_list_lessons") or name.startswith("ccpm_get_lesson") or \
             name.startswith("ccpm_create_lesson") or name.startswith("ccpm_get_my_lesson") or \
             name.startswith("ccpm_acknowledge_lesson") or name.startswith("ccpm_implement_lesson") or \
             name.startswith("ccpm_generate_lesson"):
            categories["Lessons Learned"].append(tool)
        elif name.startswith("ccpm_") and ("message" in name or name in ["ccpm_list_agents", "ccpm_send_message", "ccpm_broadcast_message", "ccpm_check_inbox", "ccpm_mark_message_read", "ccpm_mark_message_complete", "ccpm_acknowledge_and_complete"]):
            categories["CCPM Messaging"].append(tool)
        elif name.startswith("ccpm_") and "task" in name:
            categories["CCPM Tasks"].append(tool)
        elif name.startswith("ccpm_") and "sprint" in name:
            categories["CCPM Sprints"].append(tool)
        elif name.startswith("ccpm_") and "session" in name:
            categories["Session Management"].append(tool)
        elif name == "ccpm_signal_completion":
            categories["Completion Signaling"].append(tool)
        elif name.startswith("piggyback_"):
            categories["Piggyback Messaging"].append(tool)
        elif name.startswith("ccpm_"):
            # Default CCPM to messaging if not matched
            if "message" in name.lower() or "agent" in name.lower():
                categories["CCPM Messaging"].append(tool)
            else:
                categories["CCPM Tasks"].append(tool)

    return categories


def generate_markdown(tools: list[dict]) -> str:
    """Generate markdown documentation."""
    categories = categorize_tools(tools)

    lines = [
        "# HomeLab MCP Tools - Auto-Generated Reference",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Total Tools:** {len(tools)}",
        f"**Source:** `mcp-servers/homelab-infra/homelab_server.py`",
        "",
        "---",
        "",
        "## Tool Summary",
        "",
        "| Category | Count |",
        "|----------|-------|"
    ]

    for cat, cat_tools in categories.items():
        if cat_tools:
            lines.append(f"| {cat} | {len(cat_tools)} |")

    lines.extend(["", "---", ""])

    for cat, cat_tools in categories.items():
        if not cat_tools:
            continue

        lines.append(f"## {cat}")
        lines.append("")

        for tool in cat_tools:
            lines.append(f"### {tool['name']}")
            lines.append("")

            # First line of docstring as description
            desc_lines = tool['docstring'].split('\n')
            brief = desc_lines[0].strip()
            lines.append(f"{brief}")
            lines.append("")

            # Parameters
            if tool['params']:
                lines.append("**Parameters:**")
                lines.append("```")
                for p in tool['params']:
                    default_str = f" = {repr(p['default'])}" if p['default'] is not None else ""
                    lines.append(f"  {p['name']}: {p['type']}{default_str}")
                lines.append("```")
                lines.append("")

            # Returns
            lines.append(f"**Returns:** `{tool['return_type']}`")
            lines.append("")

            # Source line
            lines.append(f"*Source: line {tool['line']}*")
            lines.append("")
            lines.append("---")
            lines.append("")

    return '\n'.join(lines)


def main():
    if not MCP_SERVER_PATH.exists():
        print(f"Error: MCP server file not found at {MCP_SERVER_PATH}")
        return

    source_code = MCP_SERVER_PATH.read_text()
    tools = extract_tools(source_code)
    markdown = generate_markdown(tools)
    print(markdown)


if __name__ == "__main__":
    main()
