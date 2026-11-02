"""Interactive prompts that produce a Preferences object."""
from datetime import date

import sources as src
from models import Preferences, Timeframe


def _ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    return input(f"{prompt}{suffix}: ").strip() or default


def _pick_sources():
    print("\n=== Sources ===")
    numbered = []
    for group in src.GROUP_ORDER:
        print(f"\n{group}:")
        for s in src.by_group(group):
            numbered.append(s)
            print(f"  {len(numbered):>2}. {s.name}")
    print("\nEnter numbers (e.g. 1,4,10-12), or: a = all, b = all Bengali, "
          "e = all English, s = all social media (combine: b,e)")
    while True:
        raw = _ask("Your choice", "a").lower().replace(" ", "")
        chosen, ok = [], True
        for tok in filter(None, raw.split(",")):
            if tok == "a":
                chosen += numbered
            elif tok == "b":
                chosen += src.by_group(src.BENGALI)
            elif tok == "e":
                chosen += src.by_group(src.ENGLISH)
            elif tok == "s":
                chosen += src.by_group(src.SOCIAL)
            elif "-" in tok and all(p.isdigit() for p in tok.split("-", 1)):
                lo, hi = map(int, tok.split("-", 1))
                chosen += [numbered[i - 1] for i in range(lo, hi + 1) if 1 <= i <= len(numbered)]
            elif tok.isdigit() and 1 <= int(tok) <= len(numbered):
                chosen.append(numbered[int(tok) - 1])
            else:
                print(f"  Couldn't understand '{tok}'.")
                ok = False
        if ok and chosen:
            return list(dict.fromkeys(chosen))   # de-duplicate, keep order


PRESET_TOPICS = ["Politics", "Sports", "Science", "Technology", "Business & Economy",
                 "Entertainment", "Health", "Education", "Environment", "World affairs"]


def _pick_topics():
    print("\n=== Topics ===")
    for i, t in enumerate(PRESET_TOPICS, 1):
        print(f"  {i:>2}. {t}")
    print("Pick numbers and/or type custom topics, comma-separated "
          "(e.g. 1,3,Kolkata Metro,Durga Puja).")
    while True:
        raw = _ask("Your topics")
        topics = []
        for tok in (t.strip() for t in raw.split(",")):
            if not tok:
                continue
            if tok.isdigit() and 1 <= int(tok) <= len(PRESET_TOPICS):
                topics.append(PRESET_TOPICS[int(tok) - 1])
            else:
                topics.append(tok)
        if topics:
            return list(dict.fromkeys(topics))
        print("  Please enter at least one topic.")


def _pick_timeframe() -> Timeframe:
    print("\n=== Timeframe ===")
    print("  1. Latest (last 48 hours)\n  2. Past week\n  3. Past month\n"
          "  4. A specific year\n  5. Custom (e.g. 'March 2023' or 'during the 2022 World Cup')")
    choice = _ask("Your choice", "1")
    if choice == "2":
        return Timeframe("Past week", "published within the last 7 days")
    if choice == "3":
        return Timeframe("Past month", "published within the last 30 days")
    if choice == "4":
        while True:
            y = _ask("Year (e.g. 2023)")
            if y.isdigit() and 1990 <= int(y) <= date.today().year:
                return Timeframe(f"Year {y}", f"published during the calendar year {y}")
            print("  Enter a valid 4-digit year.")
    if choice == "5":
        text = _ask("Describe the period")
        return Timeframe(text, f"relevant to this period: {text}")
    return Timeframe("Latest", "published within the last 48 hours (the most recent available)")


def collect_preferences() -> Preferences:
    sources = _pick_sources()
    topics = _pick_topics()
    timeframe = _pick_timeframe()
    print("\n=== Output ===")
    lang = "Bengali" if _ask("Summary language: (E)nglish or (B)engali", "E").lower().startswith("b") else "English"
    n = _ask("Max items per topic, per source group", "3")
    n = int(n) if n.isdigit() and int(n) > 0 else 3
    return Preferences(sources, topics, timeframe, n, lang)
