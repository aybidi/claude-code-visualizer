"""Process Claude Code session data into visualization-ready dict."""

import json
import os
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


def parse_jsonl(filepath):
    """Read a JSONL file, yielding parsed records."""
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def parse_timestamp(ts):
    """Parse a timestamp from various formats into a datetime."""
    if not ts:
        return None
    try:
        if isinstance(ts, str):
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        elif isinstance(ts, (int, float)):
            return datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    except (ValueError, OSError, OverflowError):
        return None
    return None


def _process_all_data(claude_dir):
    """Process all Claude Code session data from the given directory."""
    projects_dir = claude_dir / "projects"
    messages = []

    if not projects_dir.exists():
        return messages

    for project_dir in sorted(projects_dir.iterdir()):
        if not project_dir.is_dir():
            continue
        for jsonl_file in project_dir.glob("*.jsonl"):
            for record in parse_jsonl(jsonl_file):
                record["_project_dir"] = project_dir.name
                record["_session_file"] = jsonl_file.stem
                messages.append(record)

    # Derive project names from cwd fields in user messages
    project_name_map = {}
    for msg in messages:
        if msg.get("type") == "user" and "cwd" in msg:
            pdir = msg.get("_project_dir", "")
            if pdir and pdir not in project_name_map:
                project_name_map[pdir] = os.path.basename(msg["cwd"])

    # Assign human-readable project names
    for msg in messages:
        pdir = msg.get("_project_dir", "")
        if pdir in project_name_map:
            msg["_project_name"] = project_name_map[pdir]
        else:
            parts = pdir.split("-")
            skip = {"", "Users", "Documents", "Projects", "Desktop", "Code",
                    "repos", "src", "home", "var", "tmp"}
            meaningful = []
            skip_next_as_username = False
            for i, p in enumerate(parts):
                if p == "Users":
                    skip_next_as_username = True
                    continue
                if skip_next_as_username:
                    skip_next_as_username = False
                    continue
                if p not in skip:
                    meaningful.append(p)
            msg["_project_name"] = "-".join(meaningful) if meaningful else pdir

    return messages


def _load_insights(claude_dir):
    """Load and aggregate data from /insights facets and session-meta."""
    usage_dir = claude_dir / "usage-data"
    facets_dir = usage_dir / "facets"
    meta_dir = usage_dir / "session-meta"

    facets = []
    if facets_dir.exists():
        for fp in facets_dir.glob("*.json"):
            try:
                with open(fp) as f:
                    facets.append(json.load(f))
            except (json.JSONDecodeError, OSError):
                continue

    goal_counts = Counter()
    outcomes = Counter()
    helpfulness = Counter()
    satisfaction = Counter()
    friction = Counter()
    success_factors = Counter()
    session_types = Counter()
    summaries = []

    for fac in facets:
        for g, c in fac.get("goal_categories", {}).items():
            goal_counts[g] += c
        outcomes[fac.get("outcome", "unknown")] += 1
        helpfulness[fac.get("claude_helpfulness", "unknown")] += 1
        for s, c in fac.get("user_satisfaction_counts", {}).items():
            satisfaction[s] += c
        for fr, c in fac.get("friction_counts", {}).items():
            friction[fr] += c
        sf = fac.get("primary_success", "")
        if sf and sf != "none":
            success_factors[sf] += 1
        session_types[fac.get("session_type", "unknown")] += 1
        summaries.append({
            "outcome": fac.get("outcome", "unknown"),
            "summary": fac.get("brief_summary", ""),
            "helpfulness": fac.get("claude_helpfulness", "unknown"),
            "sessionId": fac.get("session_id", ""),
        })

    metas = []
    if meta_dir.exists():
        for fp in meta_dir.glob("*.json"):
            try:
                with open(fp) as f:
                    metas.append(json.load(f))
            except (json.JSONDecodeError, OSError):
                continue

    total_lines_added = sum(m.get("lines_added", 0) for m in metas)
    total_lines_removed = sum(m.get("lines_removed", 0) for m in metas)
    total_files_modified = sum(m.get("files_modified", 0) for m in metas)

    languages = Counter()
    for m in metas:
        for lang, c in m.get("languages", {}).items():
            languages[lang] += c

    return {
        "goals": [{"name": n, "count": c} for n, c in goal_counts.most_common(12)],
        "outcomes": [{"name": n, "count": c} for n, c in outcomes.most_common()],
        "helpfulness": [{"name": n, "count": c} for n, c in helpfulness.most_common()],
        "satisfaction": [{"name": n, "count": c} for n, c in satisfaction.most_common()],
        "friction": [{"name": n, "count": c} for n, c in friction.most_common()],
        "successFactors": [{"name": n, "count": c} for n, c in success_factors.most_common()],
        "sessionTypes": [{"name": n, "count": c} for n, c in session_types.most_common()],
        "summaries": summaries,
        "linesAdded": total_lines_added,
        "linesRemoved": total_lines_removed,
        "filesModified": total_files_modified,
        "languages": [{"name": n, "count": c} for n, c in languages.most_common()],
        "totalFacets": len(facets),
    }


def _compute_stats(messages, claude_dir):
    """Compute all statistics for the visualization."""
    user_msgs = [m for m in messages
                 if m.get("type") == "user" and not m.get("isMeta")]
    assistant_msgs = [m for m in messages if m.get("type") == "assistant"]
    all_typed = user_msgs + assistant_msgs

    # Overview
    total_input = total_output = total_cache_read = total_cache_write = 0
    for msg in assistant_msgs:
        u = msg.get("message", {}).get("usage", {})
        total_input += u.get("input_tokens", 0)
        total_output += u.get("output_tokens", 0)
        total_cache_read += u.get("cache_read_input_tokens", 0)
        total_cache_write += u.get("cache_creation_input_tokens", 0)

    timestamps = sorted(filter(None, (parse_timestamp(m.get("timestamp"))
                                       for m in all_typed)))
    first_date = timestamps[0] if timestamps else None
    last_date = timestamps[-1] if timestamps else None

    session_ids = {m["sessionId"] for m in all_typed if "sessionId" in m}

    overview = {
        "totalSessions": len(session_ids),
        "totalMessages": len(all_typed),
        "totalUserMessages": len(user_msgs),
        "totalAssistantMessages": len(assistant_msgs),
        "totalInputTokens": total_input,
        "totalOutputTokens": total_output,
        "totalCacheRead": total_cache_read,
        "totalCacheWrite": total_cache_write,
        "totalTokens": total_input + total_output + total_cache_read + total_cache_write,
        "firstDate": first_date.isoformat() if first_date else None,
        "lastDate": last_date.isoformat() if last_date else None,
        "daySpan": (last_date - first_date).days if first_date and last_date else 0,
    }

    # Daily Timeline
    daily = defaultdict(lambda: {
        "messages": 0, "userMessages": 0, "assistantMessages": 0,
        "inputTokens": 0, "outputTokens": 0, "sessions": set()
    })

    for msg in all_typed:
        dt = parse_timestamp(msg.get("timestamp"))
        if not dt:
            continue
        day = dt.strftime("%Y-%m-%d")
        daily[day]["messages"] += 1
        if msg.get("type") == "user":
            daily[day]["userMessages"] += 1
        else:
            daily[day]["assistantMessages"] += 1
            u = msg.get("message", {}).get("usage", {})
            daily[day]["inputTokens"] += u.get("input_tokens", 0)
            daily[day]["outputTokens"] += u.get("output_tokens", 0)
        sid = msg.get("sessionId")
        if sid:
            daily[day]["sessions"].add(sid)

    timeline = []
    for day in sorted(daily):
        d = daily[day]
        timeline.append({
            "date": day,
            "messages": d["messages"],
            "userMessages": d["userMessages"],
            "assistantMessages": d["assistantMessages"],
            "inputTokens": d["inputTokens"],
            "outputTokens": d["outputTokens"],
            "sessions": len(d["sessions"]),
        })

    # Projects
    proj = defaultdict(lambda: {
        "messages": 0, "userMessages": 0, "sessions": set(),
        "inputTokens": 0, "outputTokens": 0, "tools": Counter()
    })

    for msg in all_typed:
        pname = msg.get("_project_name", "Unknown")
        proj[pname]["messages"] += 1
        if msg.get("type") == "user":
            proj[pname]["userMessages"] += 1
        sid = msg.get("sessionId")
        if sid:
            proj[pname]["sessions"].add(sid)
        if msg.get("type") == "assistant":
            u = msg.get("message", {}).get("usage", {})
            proj[pname]["inputTokens"] += u.get("input_tokens", 0)
            proj[pname]["outputTokens"] += u.get("output_tokens", 0)
            for block in (msg.get("message", {}).get("content") or []):
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    proj[pname]["tools"][block.get("name", "?")] += 1

    projects = sorted(
        [{"name": n, "messages": s["messages"], "userMessages": s["userMessages"],
          "sessions": len(s["sessions"]),
          "inputTokens": s["inputTokens"], "outputTokens": s["outputTokens"],
          "topTools": s["tools"].most_common(5)}
         for n, s in proj.items()],
        key=lambda x: x["messages"], reverse=True
    )

    # Tool Usage
    tool_counter = Counter()
    tool_by_project = defaultdict(Counter)

    for msg in assistant_msgs:
        pname = msg.get("_project_name", "Unknown")
        for block in (msg.get("message", {}).get("content") or []):
            if isinstance(block, dict) and block.get("type") == "tool_use":
                name = block.get("name", "?")
                tool_counter[name] += 1
                tool_by_project[name][pname] += 1

    tools = [{"name": n, "count": c,
              "topProjects": tool_by_project[n].most_common(3)}
             for n, c in tool_counter.most_common()]

    # Models
    model_counter = Counter()
    model_timeline = defaultdict(Counter)

    for msg in assistant_msgs:
        model = msg.get("message", {}).get("model", "unknown")
        model_counter[model] += 1
        dt = parse_timestamp(msg.get("timestamp"))
        if dt:
            week = dt.strftime("%Y-W%W")
            model_timeline[week][model] += 1

    models = [{"name": n, "count": c} for n, c in model_counter.most_common()]

    models_over_time = []
    for week in sorted(model_timeline):
        entry = {"week": week}
        for m in model_counter:
            entry[m] = model_timeline[week].get(m, 0)
        models_over_time.append(entry)

    # Hourly / Weekly / Heatmap
    hourly = defaultdict(int)
    dow = defaultdict(int)
    heatmap = defaultdict(int)

    for msg in all_typed:
        dt = parse_timestamp(msg.get("timestamp"))
        if not dt:
            continue
        hourly[dt.hour] += 1
        dow[dt.weekday()] += 1
        heatmap[f"{dt.weekday()}-{dt.hour}"] += 1

    hourly_data = [{"hour": h, "count": hourly[h]} for h in range(24)]
    weekly_data = [{"day": d, "count": dow[d]} for d in range(7)]
    heatmap_data = [{"day": d, "hour": h, "count": heatmap.get(f"{d}-{h}", 0)}
                    for d in range(7) for h in range(24)]

    # Session Stats
    session_times = defaultdict(list)
    for msg in all_typed:
        sid = msg.get("sessionId")
        dt = parse_timestamp(msg.get("timestamp"))
        if sid and dt:
            session_times[sid].append(dt)

    durations = []
    msg_counts = []
    for sid, times in session_times.items():
        times.sort()
        if len(times) >= 2:
            dur = (times[-1] - times[0]).total_seconds() / 60
            durations.append(round(dur, 1))
        msg_counts.append(len(times))

    bins = [0, 5, 15, 30, 60, 120, 360, float("inf")]
    labels = ["<5m", "5-15m", "15-30m", "30m-1h", "1-2h", "2-6h", "6h+"]
    hist = [0] * len(labels)
    for d in durations:
        for i in range(len(bins) - 1):
            if bins[i] <= d < bins[i + 1]:
                hist[i] += 1
                break

    session_stats = {
        "durations": [{"label": l, "count": c} for l, c in zip(labels, hist)],
        "avgDuration": round(sum(durations) / len(durations), 1) if durations else 0,
        "maxDuration": round(max(durations), 1) if durations else 0,
        "avgMessages": round(sum(msg_counts) / len(msg_counts), 1) if msg_counts else 0,
        "maxMessages": max(msg_counts) if msg_counts else 0,
    }

    # Insights
    insights = _load_insights(claude_dir)

    return {
        "overview": overview,
        "timeline": timeline,
        "projects": projects,
        "tools": tools,
        "models": models,
        "modelsOverTime": models_over_time,
        "hourly": hourly_data,
        "weekly": weekly_data,
        "heatmap": heatmap_data,
        "sessionStats": session_stats,
        "insights": insights,
    }


def generate_data(claude_dir=None):
    """Generate visualization data from Claude Code session history.

    Args:
        claude_dir: Path to .claude directory. Defaults to ~/.claude.

    Returns:
        dict with all visualization data.
    """
    if claude_dir is None:
        claude_dir = Path.home() / ".claude"
    else:
        claude_dir = Path(claude_dir)

    messages = _process_all_data(claude_dir)
    return _compute_stats(messages, claude_dir)
