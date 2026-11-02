"""Render sections into Markdown and HTML."""
from datetime import datetime
from html import escape


def _count(sections):
    return sum(len(v) for s in sections for v in s.by_group.values())


def render_markdown(sections, prefs) -> str:
    out = [f"# Your Personalized Newsletter",
           f"*{datetime.now():%A, %d %B %Y}  |  Timeframe: {prefs.timeframe.label}  |  "
           f"{_count(sections)} items*", ""]
    for sec in sections:
        out += [f"## {sec.topic}", ""]
        for group, items in sec.by_group.items():
            out.append(f"### {group}")
            if not items:
                out.append("_Nothing found for this topic in the selected sources._")
            for it in items:
                out.append(f"- **{it.title}** ({it.source})  \n  {it.summary}  \n  [Read more]({it.url})")
            out.append("")
    return "\n".join(out)


def render_html(sections, prefs) -> str:
    parts = []
    for sec in sections:
        parts.append(f"<h2>{escape(sec.topic)}</h2>")
        for group, items in sec.by_group.items():
            parts.append(f"<h3>{escape(group)}</h3>")
            if not items:
                parts.append("<p class='empty'>Nothing found for this topic in the selected sources.</p>")
            for it in items:
                parts.append(
                    f"<div class='card'><div class='src'>{escape(it.source)}</div>"
                    f"<h4>{escape(it.title)}</h4><p>{escape(it.summary)}</p>"
                    f"<a href='{escape(it.url, quote=True)}' target='_blank' rel='noopener'>Read full story →</a></div>")
    body = "\n".join(parts)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Your Personalized Newsletter</title>
<style>
 body{{font-family:'Noto Sans Bengali','Segoe UI',Roboto,Arial,sans-serif;max-width:760px;margin:2rem auto;padding:0 1rem;color:#1d1d1f;background:#fafafa}}
 h1{{margin-bottom:.2rem}} .meta{{color:#666;margin-bottom:2rem}}
 h2{{border-bottom:2px solid #222;padding-bottom:.3rem;margin-top:2.5rem}}
 h3{{color:#8a4b00;text-transform:uppercase;font-size:.85rem;letter-spacing:.06em}}
 .card{{background:#fff;border:1px solid #e3e3e3;border-radius:10px;padding:1rem 1.2rem;margin:.8rem 0}}
 .card h4{{margin:.2rem 0 .4rem}} .src{{font-size:.75rem;color:#888}}
 .card a{{color:#0b57d0;text-decoration:none;font-weight:600}} .empty{{color:#888;font-style:italic}}
 @media (prefers-color-scheme:dark){{body{{background:#111;color:#eee}}.card{{background:#1b1b1b;border-color:#333}}.meta,.src{{color:#aaa}}.card a{{color:#8ab4f8}}h2{{border-color:#eee}}}}
</style></head><body>
<h1>Your Personalized Newsletter</h1>
<div class="meta">{datetime.now():%A, %d %B %Y} &middot; Timeframe: {escape(prefs.timeframe.label)} &middot; {_count(sections)} items</div>
{body}
</body></html>"""
