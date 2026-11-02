# Personalized Newsletter Generator

    pip install -r requirements.txt
    export GEMINI_API_KEY="your-paid-key"
    python main.py

Optional: `GEMINI_MODEL` (default gemini-2.5-flash), `NEWSLETTER_OUT` (default ./output).

| File | Role |
|---|---|
| models.py | Dataclasses (Source, Item, Preferences...) |
| sources.py | Newspaper / social media registry (edit to add more) |
| cli.py | Interactive choices: sources, topics, timeframe, language |
| gemini_client.py | Gemini + Google Search grounding, link extraction |
| newsletter.py | Markdown + HTML rendering |
| config.py | API key, model, retries |
| main.py | Orchestration (parallel fetch, write files) |

## Streamlit UI

    pip install -r requirements.txt
    streamlit run app.py

Optional: put the key in `.streamlit/secrets.toml` as `GEMINI_API_KEY = "..."` so you don't retype it.
`app.py` and `main.py` are two front ends over the same `service.py`; `cli.py` is only used by the terminal version.
