"""UI-independent orchestration, shared by the terminal (main.py) and Streamlit (app.py)."""
from concurrent.futures import ThreadPoolExecutor, as_completed

import config
import sources as src
from models import TopicSection


def generate_sections(prefs, client, on_progress=None):
    """Fetch all topic x source-group combinations in parallel.

    on_progress(done, total, topic, group, item_count) is called from the calling
    thread (never a worker thread), so it is safe to update Streamlit widgets in it.
    """
    groups = [g for g in src.GROUP_ORDER if any(s.group == g for s in prefs.sources)]
    sections = {t: TopicSection(t, {g: [] for g in groups}) for t in prefs.topics}
    jobs = [(t, g, [s for s in prefs.sources if s.group == g])
            for t in prefs.topics for g in groups]

    with ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as pool:
        futures = {pool.submit(client.fetch_items, t, srcs, prefs): (t, g)
                   for t, g, srcs in jobs}
        for n, fut in enumerate(as_completed(futures), 1):
            topic, group = futures[fut]
            try:
                items = fut.result()
            except Exception:
                items = []
            sections[topic].by_group[group] = items
            if on_progress:
                on_progress(n, len(jobs), topic, group, len(items))
    return [sections[t] for t in prefs.topics]
