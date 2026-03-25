"""CLI entry point for claude-code-visualizer."""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        prog="claude-viz",
        description="Generate a self-contained HTML visualization of your Claude Code usage",
    )
    parser.add_argument(
        "-o", "--output",
        default="claude-code-viz.html",
        help="Output HTML file path (default: claude-code-viz.html)",
    )
    parser.add_argument(
        "--claude-dir",
        default=None,
        help="Path to .claude directory (default: ~/.claude)",
    )
    parser.add_argument(
        "--open", action="store_true",
        help="Open the generated HTML in the default browser",
    )
    args = parser.parse_args()

    from claude_code_visualizer.data import generate_data
    from claude_code_visualizer.renderer import render_html

    print("Processing Claude Code session data...")
    data = generate_data(claude_dir=args.claude_dir)

    overview = data.get("overview", {})
    print(f"  {overview.get('totalSessions', 0)} sessions, "
          f"{overview.get('totalMessages', 0)} messages, "
          f"{len(data.get('projects', []))} projects")

    if overview.get("totalMessages", 0) == 0:
        print("\nNo Claude Code data found. Make sure you have session history in ~/.claude/")
        sys.exit(1)

    html = render_html(data)

    output_path = Path(args.output).resolve()
    output_path.write_text(html, encoding="utf-8")
    size_kb = output_path.stat().st_size / 1024
    print(f"\nGenerated: {output_path} ({size_kb:.0f} KB)")
    print("Open in your browser — no server needed.")

    if args.open:
        import webbrowser
        webbrowser.open(f"file://{output_path}")
