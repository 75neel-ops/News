"""Plain data containers shared by all modules."""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Source:
    name: str
    domains: tuple      # domains that count as this source
    group: str          # e.g. "Bengali newspapers"

    def matches_host(self, host: str) -> bool:
        host = host.lower()
        return any(host == d or host.endswith("." + d) for d in self.domains)


@dataclass
class Item:
    title: str
    summary: str
    url: str
    source: str


@dataclass
class Timeframe:
    label: str     # shown in the newsletter header
    phrase: str    # injected into the Gemini prompt


@dataclass
class Preferences:
    sources: list
    topics: list
    timeframe: Timeframe
    items_per_group: int = 3
    language: str = "English"        # language of headlines/summaries


@dataclass
class TopicSection:
    topic: str
    by_group: dict = field(default_factory=dict)   # group name -> list[Item]
