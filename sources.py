"""Registry of selectable sources. Add or remove entries freely."""
from models import Source

BENGALI = "Bengali newspapers"
ENGLISH = "English newspapers"
SOCIAL = "Social media"
GROUP_ORDER = [BENGALI, ENGLISH, SOCIAL]

SOURCES = [
    # --- Bengali newspapers (India + Bangladesh) ---
    Source("Anandabazar Patrika", ("anandabazar.com",), BENGALI),
    Source("Bartaman", ("bartamanpatrika.com",), BENGALI),
    Source("Sangbad Pratidin", ("sangbadpratidin.in",), BENGALI),
    Source("Ei Samay", ("eisamay.com",), BENGALI),
    Source("Prothom Alo", ("prothomalo.com",), BENGALI),
    Source("Ittefaq", ("ittefaq.com.bd",), BENGALI),
    Source("Kaler Kantho", ("kalerkantho.com",), BENGALI),
    Source("Jugantor", ("jugantor.com",), BENGALI),
    # --- English newspapers ---
    Source("The Hindu", ("thehindu.com",), ENGLISH),
    Source("Times of India", ("timesofindia.indiatimes.com", "indiatimes.com"), ENGLISH),
    Source("Hindustan Times", ("hindustantimes.com",), ENGLISH),
    Source("The Telegraph India", ("telegraphindia.com",), ENGLISH),
    Source("The Indian Express", ("indianexpress.com",), ENGLISH),
    Source("NDTV", ("ndtv.com",), ENGLISH),
    Source("The Statesman", ("thestatesman.com",), ENGLISH),
    Source("The Daily Star (BD)", ("thedailystar.net",), ENGLISH),
    Source("Dhaka Tribune", ("dhakatribune.com",), ENGLISH),
    # --- Social media (public, search-indexed content only) ---
    Source("Reddit", ("reddit.com",), SOCIAL),
    Source("X (Twitter)", ("x.com", "twitter.com"), SOCIAL),
    Source("YouTube", ("youtube.com", "youtu.be"), SOCIAL),
    Source("Facebook", ("facebook.com",), SOCIAL),
    Source("Instagram", ("instagram.com",), SOCIAL),
    Source("LinkedIn", ("linkedin.com",), SOCIAL),
    Source("Hacker News", ("news.ycombinator.com",), SOCIAL),
]


def by_group(group: str):
    return [s for s in SOURCES if s.group == group]


def find_by_host(host: str, candidates):
    for s in candidates:
        if s.matches_host(host):
            return s
    return None
