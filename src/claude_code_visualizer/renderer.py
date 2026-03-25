"""Assemble a self-contained HTML file with data and D3 inlined."""

import json
from pathlib import Path

ASSETS_DIR = Path(__file__).parent / "assets"


def render_html(data):
    """Produce a self-contained HTML string with data and D3 inlined.

    Args:
        data: dict from generate_data()

    Returns:
        str: Complete HTML document ready to open in a browser.
    """
    template = (ASSETS_DIR / "template.html").read_text(encoding="utf-8")
    d3_code = (ASSETS_DIR / "d3.v7.min.js").read_text(encoding="utf-8")

    # Inline D3
    template = template.replace(
        "<!-- D3_INLINE_SCRIPT -->",
        "<script>" + d3_code + "</script>"
    )

    # Inline data — sanitize </script> sequences in JSON to prevent breaking the HTML
    data_json = json.dumps(data, separators=(",", ":"), default=str)
    data_json = data_json.replace("</script>", "<\\/script>")

    template = template.replace(
        "const __CLAUDE_VIZ_DATA__ = null; // DATA_MARKER",
        "const __CLAUDE_VIZ_DATA__ = " + data_json + ";"
    )

    return template
