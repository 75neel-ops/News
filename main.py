"""Terminal entry point:  python main.py   (Streamlit UI: streamlit run app.py)"""
import os
from datetime import datetime

import cli
import config
import newsletter
from gemini_client import GeminiNewsClient
from service import generate_sections


def main():
    api_key = config.get_api_key()
    prefs = cli.collect_preferences()
    client = GeminiNewsClient(api_key, config.MODEL)

    print(f"\nFetching with Gemini ({config.MODEL})...\n")
    sections = generate_sections(
        prefs, client,
        on_progress=lambda n, total, t, g, c: print(f"  ✓ [{n}/{total}] {t} / {g}: {c} item(s)"))

    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    md_path = os.path.join(config.OUTPUT_DIR, f"newsletter_{stamp}.md")
    html_path = os.path.join(config.OUTPUT_DIR, f"newsletter_{stamp}.html")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(newsletter.render_markdown(sections, prefs))
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(newsletter.render_html(sections, prefs))
    print(f"\nDone!\n  HTML: {html_path}\n  Markdown: {md_path}")


if __name__ == "__main__":
    main()
