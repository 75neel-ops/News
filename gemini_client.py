"""Fetch + summarize via Gemini with Google Search grounding.

How links stay trustworthy: Gemini is asked to write one line per item. The API
returns grounding metadata that maps each span of the answer to the real web pages
it came from. We take each item's link from that metadata (never from text the model
typed), resolve the redirect, and drop anything outside the selected sources.
"""
import re
import time
from datetime import date
from urllib.parse import urlparse

import requests
from google import genai
from google.genai import types

import config
import sources as src
from models import Item

LINE_RE = re.compile(r"^\s*(?:[-*•]\s+|\d+[.)]\s+)?\*\*(.+?)\*\*\s*[—–:\-]*\s*(.+)$")


class GeminiNewsClient:
    def __init__(self, api_key: str, model: str = config.MODEL):
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self._redirect_cache = {}

    # ---------- public ----------
    def fetch_items(self, topic, group_sources, prefs) -> list:
        prompt = self._build_prompt(topic, group_sources, prefs)
        response = self._generate(prompt)
        return self._parse(response, group_sources, prefs.items_per_group)

    # ---------- prompt ----------
    def _build_prompt(self, topic, group_sources, prefs) -> str:
        is_social = group_sources[0].group == src.SOCIAL
        kind = "posts, videos or discussions" if is_social else "news articles"
        site_list = "\n".join(f"- {s.name}: {', '.join(s.domains)}" for s in group_sources)
        return f"""You are a careful news curator. Today's date is {date.today():%d %B %Y}.

Find up to {prefs.items_per_group} distinct, noteworthy {kind} about "{topic}", {prefs.timeframe.phrase}.

Allowed sources ONLY:
{site_list}

Use Google Search (for example queries like `{topic} site:{group_sources[0].domains[0]}`).
Rules:
- Report only what you actually found in search results. Never invent items.
- Do not repeat the same story twice.
- Output ONE line per item, exactly in this format:
  **Headline** — crisp 1-2 sentence summary (max 45 words)
- Write headlines and summaries in {prefs.language}.
- No introduction, no closing remarks, no URLs, no other text.
- If nothing relevant is found, output exactly: NO_RESULTS"""

    # ---------- API call ----------
    def _generate(self, prompt: str):
        cfg = types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
            temperature=0.2,
        )
        last_err = None
        for attempt in range(config.MAX_RETRIES):
            try:
                return self.client.models.generate_content(
                    model=self.model, contents=prompt, config=cfg)
            except Exception as e:                       # network / quota / 5xx
                last_err = e
                time.sleep(2 ** attempt)
        print(f"  ! Gemini call failed: {last_err}")
        return None

    # ---------- parsing ----------
    def _parse(self, response, group_sources, limit) -> list:
        if response is None or not response.candidates:
            return []
        cand = response.candidates[0]
        text = response.text or ""
        meta = cand.grounding_metadata
        if not text or "NO_RESULTS" in text or meta is None:
            return []
        chunks = meta.grounding_chunks or []
        supports = meta.grounding_supports or []

        items, offset = [], 0
        for line in text.split("\n"):
            start, end = offset, offset + len(line.encode("utf-8"))   # API uses byte offsets
            offset = end + 1
            m = LINE_RE.match(line)
            if not m:
                continue
            url, source_name = self._link_for_span(start, end, supports, chunks, group_sources)
            if url:
                items.append(Item(m.group(1).strip(), m.group(2).strip(), url, source_name))
            if len(items) >= limit:
                break
        return items

    def _link_for_span(self, start, end, supports, chunks, group_sources):
        indices = []
        for s in supports:
            seg = s.segment
            if seg is None:
                continue
            if (seg.start_index or 0) < end and (seg.end_index or 0) > start:
                indices.extend(s.grounding_chunk_indices or [])
        for i in indices:
            if i >= len(chunks) or chunks[i].web is None:
                continue
            final_url, host = self._resolve(chunks[i].web.uri, chunks[i].web.title or "")
            source = src.find_by_host(host, group_sources)
            if source:
                return final_url, source.name
        return None, None

    def _resolve(self, uri: str, title: str):
        """Grounding links are redirects; follow them to the real article URL."""
        if uri in self._redirect_cache:
            return self._redirect_cache[uri]
        final = uri
        try:
            r = requests.get(uri, allow_redirects=True, timeout=10, stream=True,
                             headers={"User-Agent": "Mozilla/5.0"})
            final = r.url
            r.close()
        except Exception:
            pass
        host = urlparse(final).netloc.lower().removeprefix("www.")
        if "vertexaisearch" in host or "google" in host:   # redirect failed; chunk title is the domain
            host = title.lower().removeprefix("www.")
        self._redirect_cache[uri] = (final, host)
        return final, host
